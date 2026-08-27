# -*- coding: utf-8 -*-
"""
TP5_02_modelos.py   ---> SEGUNDO script del TP5.

QUE HACE
--------
Ajusta los CUATRO modelos del practico -optico, SAR, optico+SAR y
optico+SAR+LiDAR- sobre exactamente las mismas huellas y con exactamente la misma
particion.

EL OBJETIVO DE LOS MODELOS ES LA ALTURA DEL DOSEL (rh95), NO LA BIOMASA.
Y esa decision, que parece un retroceso respecto del titulo del curso, es lo
contrario: es lo que permite que la biomasa se estime de manera defendible.

POR QUE. La biomasa del GEDI L4A NO es una medicion independiente: la NASA la
MODELO a partir de las metricas de altura del propio L2A. Ajustar un modelo que
prediga `agbd` usando `rh95` entre las variables es reconstruir el modelo de la
NASA con otro nombre, y el R2 alto que sale de ahi no demuestra que la fusion de
sensores funcione. Este script lo deja medido, mas abajo, para que se vea el
tamano del problema en vez de discutirlo en abstracto.

La biomasa entra al final de la cadena, en TP5_04, convirtiendo la altura
predicha con la relacion altura-biomasa del L4A y arrastrando las TRES fuentes de
error: la del modelo de altura, la de esa conversion, y la del propio L4A.

QUE PREGUNTA CONTESTA, Y CUAL NO
--------------------------------
NO contesta "cual sensor es mejor". Esa pregunta ya se hizo en el TP4 y la
respuesta fue que optico y radar dan R2 parecidos. Contesta la unica que queda en
pie: CUANTO APORTA CADA FAMILIA DE VARIABLES CUANDO YA ESTAN LAS OTRAS. Eso es el
delta de R2 al agregarla, y es lo que este script reporta.

DOS ALGORITMOS, Y POR QUE
-------------------------
El LINEAL MULTIPLE es la referencia: transparente, reproducible con una planilla,
y su delta de R2 se lee sin ambiguedad. El BOSQUE ALEATORIO (Random Forest) se
corre al lado con la misma particion, no para ganarle, sino para medir cuanto de
la mejora es no linealidad real y cuanto es sobreajuste. Por eso se informan
SIEMPRE las dos cifras, entrenamiento y validacion: si la de entrenamiento es
mucho mejor que la de validacion, el modelo memorizo.

CASO COMPLETO
-------------
Una huella entra en la comparacion solo si tiene TODAS las variables de TODOS los
modelos y ademas el objetivo. Si cada modelo usara las huellas que le convienen,
la comparacion no seria justa. El script informa cuantas huellas quedan.

ENTRADA   04_Tablas_de_trabajo/TP5_dataset_<AOI>.csv  (del TP5_01)
SALIDA    05_Resultados/04_Tablas/TP5_modelos_<objetivo>.csv
USO       python TP5_02_modelos.py
"""
import csv
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
TP5 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SUBSETS = os.path.join(TP5, "04_Tablas_de_trabajo")
TABLAS = os.path.join(TP5, "05_Resultados", "04_Tablas")

OPTICO = ["NDVI", "EVI", "NDMI", "NBR"]
SAR = ["g0_C_VH", "g0_C_VV", "g0_L_SAOCOM_HH", "g0_L_SAOCOM_HV",
       "g0_L_NISAR_HH", "g0_L_NISAR_HV", "g0_L_PALSAR2_HH", "g0_L_PALSAR2_HV"]
# DOS TRAMPAS DE CIRCULARIDAD QUE HAY QUE ESQUIVAR, Y NO SON OBVIAS
#
# 1. Si el objetivo es rh95, meter rh95 entre las variables da R2 = 1,000. Es
#    absurdo dicho asi, pero es exactamente lo que pasa si uno arma la lista de
#    variables una sola vez y la usa para los dos objetivos. Por eso, cuando el
#    objetivo es la altura, la familia LiDAR se queda solo con la ESTRUCTURA del
#    L2B (pai, cover, fhd) y se sacan las metricas de altura.
#
# 2. Mas sutil, y mas peligrosa: la biomasa del GEDI L4A NO es una medicion
#    independiente. La NASA la MODELO a partir de las metricas de altura del
#    L2A. Predecir agbd usando rh95 es, en buena medida, reconstruir el modelo
#    de la NASA, y el R2 alto que sale de ahi NO demuestra que la fusion de
#    sensores funcione. Por eso se corre ademas el modelo "solo LiDAR": si su
#    R2 ya es alto por si solo, la mejora del modelo completo hay que
#    atribuirsela a la circularidad y no al aporte del optico ni del radar.
LIDAR_ALTURA = ["pai", "cover", "fhd_normal"]
LIDAR_BIOMASA = ["rh95", "rh50", "pai", "cover", "fhd_normal"]


def familias(objetivo):
    lid = LIDAR_ALTURA if objetivo == "rh95" else LIDAR_BIOMASA
    return [("optico", OPTICO),
            ("SAR", SAR),
            ("optico+SAR", OPTICO + SAR),
            ("optico+SAR+LiDAR", OPTICO + SAR + lid)], lid
# El primero es el objetivo de verdad. El segundo se corre SOLO como diagnostico
# de la circularidad, y su salida lleva el aviso encima.
OBJETIVOS = [("altura", "rh95", "m"), ("biomasa", "agbd_Mg_ha", "Mg/ha")]
# error estandar mediano del propio L4A, medido en el TP2: es el PISO contra el
# que hay que comparar el RMSE de biomasa, no contra cero
PISO_L4A = {"bosque": 11.1, "estepa": 3.0}

try:
    from sklearn.ensemble import RandomForestRegressor
    HAY_RF = True
except ImportError:
    HAY_RF = False


def cargar():
    # OJO CON EL NOMBRE DEL ARCHIVO (corregido el 31/07/2026)
    # ------------------------------------------------------------------
    # Antes esto decia   f.startswith("TP5_dataset_") and f.endswith(".csv")
    # y funcionaba mientras en 04_Tablas_de_trabajo solo estuvieran los dos datasets.
    # Cuando el TP2_09 empezo a escribir TP5_dataset_<AOI>_cobertura.csv en la
    # misma carpeta, ese prefijo paso a capturar TAMBIEN las copias con las
    # columnas de cobertura, y cada huella entro DOS VECES. El sintoma es
    # silencioso: el R2 y los coeficientes no cambian -duplicar todas las filas
    # no mueve un ajuste por minimos cuadrados- pero los n informados salen al
    # doble y cualquier error estandar sale dividido por raiz de 2.
    #
    # Ahora se nombran los dos archivos de forma exacta, y ademas se comprueba
    # que ninguna huella aparezca repetida. Si aparece, el script se detiene.
    filas = []
    for aoi in ("BOSQUE_NW_02", "ESTEPA_NW_02"):
        ruta = os.path.join(SUBSETS, "TP5_dataset_%s.csv" % aoi)
        if not os.path.isfile(ruta):
            continue
        with open(ruta, newline="", encoding="utf-8") as h:
            filas.extend(list(csv.DictReader(h)))
    if not filas:
        sys.exit("No hay dataset. Ejecute antes:  python TP5_01_dataset.py")

    vistas, repetidas = set(), 0
    for r in filas:
        sn = r.get("shot_number", "")
        if sn in vistas:
            repetidas += 1
        vistas.add(sn)
    if repetidas:
        sys.exit("ERROR: %d huellas repetidas en el dataset. No se puede seguir."
                 % repetidas)
    return filas


def completas(filas, objetivo):
    """Caso completo: todas las variables de todos los modelos, y el objetivo."""
    todas = OPTICO + SAR + LIDAR_BIOMASA + [objetivo]
    out = []
    for r in filas:
        if not r.get("particion"):
            continue
        try:
            v = {k: float(r[k]) for k in todas}
        except (KeyError, ValueError):
            continue
        v["particion"] = r["particion"]; v["sitio"] = r["sitio"]
        out.append(v)
    return out


def metricas(y, pred):
    ss = ((y - y.mean()) ** 2).sum()
    r2 = 1 - ((y - pred) ** 2).sum() / ss if ss > 0 else float("nan")
    return r2, float(np.sqrt(((y - pred) ** 2).mean()))


def lineal(Xe, ye, Xv):
    A = np.column_stack([Xe, np.ones(len(Xe))])
    beta, _, _, _ = np.linalg.lstsq(A, ye, rcond=None)
    return (np.column_stack([Xe, np.ones(len(Xe))]) @ beta,
            np.column_stack([Xv, np.ones(len(Xv))]) @ beta)


def bosque(Xe, ye, Xv, semilla=42):
    m = RandomForestRegressor(n_estimators=400, min_samples_leaf=5,
                              random_state=semilla, n_jobs=-1)
    m.fit(Xe, ye)
    return m.predict(Xe), m.predict(Xv)


def corrida(D, objetivo, unidad, etiqueta, filtro=None, entrena=None, valida=None):
    """Devuelve las filas de resultado de una comparacion de los cuatro modelos."""
    if entrena is None:
        entrena = [d for d in D if d["particion"] == "entrenamiento" and (filtro is None or filtro(d))]
        valida = [d for d in D if d["particion"] == "validacion" and (filtro is None or filtro(d))]
    if len(entrena) < 30 or len(valida) < 10:
        print("   %-22s muestra insuficiente (entrena %d, valida %d): se omite"
              % (etiqueta, len(entrena), len(valida)))
        return []
    ye = np.array([d[objetivo] for d in entrena])
    yv = np.array([d[objetivo] for d in valida])
    print()
    print("   %s   (entrena %d, valida %d)" % (etiqueta, len(entrena), len(valida)))
    print("      %-18s %-24s %-24s" % ("modelo", "lineal (entren / valid)", "bosque aleatorio"))
    modelos, lid = familias(objetivo)
    salida, previo_lin, previo_rf = [], None, None
    for nombre, cols in modelos + [("solo LiDAR (control)", lid)]:
        Xe = np.array([[d[c] for c in cols] for d in entrena])
        Xv = np.array([[d[c] for c in cols] for d in valida])
        pe, pv = lineal(Xe, ye, Xv)
        r2e, _ = metricas(ye, pe); r2v, rmv = metricas(yv, pv)
        if HAY_RF:
            qe, qv = bosque(Xe, ye, Xv)
            s2e, _ = metricas(ye, qe); s2v, smv = metricas(yv, qv)
            txt_rf = "%.3f / %.3f  RMSE %.2f" % (s2e, s2v, smv)
        else:
            s2e = s2v = smv = float("nan"); txt_rf = "(sin scikit-learn)"
        control = nombre.startswith("solo LiDAR")
        d_lin = "" if previo_lin is None or control else "  (%+.3f)" % (r2v - previo_lin)
        print("      %-18s %.3f / %.3f  RMSE %5.2f%-8s %s"
              % (nombre, r2e, r2v, rmv, d_lin, txt_rf))
        salida.append({"comparacion": etiqueta, "objetivo": objetivo, "unidad": unidad,
                       "modelo": nombre, "n_entrena": len(entrena), "n_valida": len(valida),
                       "R2_entrena_lineal": "%.4f" % r2e, "R2_valida_lineal": "%.4f" % r2v,
                       "RMSE_valida_lineal": "%.3f" % rmv,
                       "R2_entrena_RF": "" if not HAY_RF else "%.4f" % s2e,
                       "R2_valida_RF": "" if not HAY_RF else "%.4f" % s2v,
                       "RMSE_valida_RF": "" if not HAY_RF else "%.3f" % smv})
        if not control:
            previo_lin, previo_rf = r2v, s2v
    return salida


print(__doc__)
if not HAY_RF:
    print("AVISO: no esta scikit-learn en este entorno. Se corre solo el modelo")
    print("lineal. Para agregar el bosque aleatorio:  conda install scikit-learn")
    print()
os.makedirs(TABLAS, exist_ok=True)
filas = cargar()
for objetivo, campo, unidad in OBJETIVOS:
    D = completas(filas, campo)
    print("=" * 72)
    print("OBJETIVO: %s  (%s, en %s)" % (objetivo.upper(), campo, unidad))
    print("=" * 72)
    print("   huellas con TODAS las variables y el objetivo: %d de %d" % (len(D), len(filas)))
    for s in ("bosque", "estepa"):
        n = sum(1 for d in D if d["sitio"] == s)
        print("      %-7s %4d" % (s, n))
    if objetivo == "biomasa":
        print()
        print("   >>> ESTE BLOQUE ES UN DIAGNOSTICO, NO EL MODELO DEL PRACTICO. <<<")
        print("   Se corre para MEDIR la circularidad, no para usar sus resultados.")
        print("   ATENCION: la biomasa del L4A la modelo la NASA A PARTIR DE LAS METRICAS")
        print("   DE ALTURA DEL L2A. Predecirla con rh95 es reconstruir ese modelo, no")
        print("   demostrar sinergia. Mire la fila 'solo LiDAR (control)': lo que ese")
        print("   modelo ya explica por si solo NO es merito de la fusion.")
        print()
        print("   PISO del propio L4A (error estandar mediano por disparo):")
        print("      bosque %.1f Mg/ha    estepa %.1f Mg/ha" % (PISO_L4A["bosque"], PISO_L4A["estepa"]))
        print("      Un RMSE parecido a esos valores NO es un mal modelo: es el techo del dato.")

    res = []
    res += corrida(D, campo, unidad, "los dos sitios juntos")
    for s in ("bosque", "estepa"):
        res += corrida(D, campo, unidad, "solo %s" % s, filtro=lambda d, s=s: d["sitio"] == s)
    # --- test espacial duro: entrenar en un sitio y probar en el OTRO
    for a, b in (("bosque", "estepa"), ("estepa", "bosque")):
        res += corrida(D, campo, unidad, "entrena %s -> valida %s" % (a, b),
                       entrena=[d for d in D if d["sitio"] == a],
                       valida=[d for d in D if d["sitio"] == b])
    if res:
        sal = os.path.join(TABLAS, "TP5_modelos_%s.csv" % objetivo)
        with open(sal, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(res[0])); w.writeheader(); w.writerows(res)
        print()
        print("   -> %s" % sal)
    print()

print("SIGUIENTE PASO:  python TP5_03_validacion.py")
print()
print("RECORDATORIO: el modelo del practico es el de ALTURA. El bloque de biomasa")
print("de mas arriba esta para mostrar por que NO se usa como objetivo directo.")
print()
print("COMO SE LEE ESTA SALIDA, y es lo que hay que escribir en el informe:")
print("  - El numero entre parentesis es el DELTA de R2 al agregar esa familia de")
print("    variables a la anterior. Ahi esta la respuesta del practico.")
print("  - Si el R2 de entrenamiento es mucho mayor que el de validacion, el modelo")
print("    memorizo. Declararlo vale mas que esconderlo.")
print("  - La fila 'solo LiDAR (control)' NO entra en la cadena de deltas. Esta")
print("    para que se vea cuanto del resultado es circularidad del propio L4A.")
print("  - Las dos ultimas comparaciones son el test duro: entrenar en un sitio y")
print("    predecir en el otro. Es normal que den mal. Eso mide transferibilidad,")
print("    que es lo que hace falta para dibujar un mapa fuera del area de ajuste.")
