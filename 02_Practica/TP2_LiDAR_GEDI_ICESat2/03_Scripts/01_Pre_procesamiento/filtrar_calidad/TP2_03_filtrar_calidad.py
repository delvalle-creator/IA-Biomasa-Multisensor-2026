#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_03_filtrar_calidad.py   ---> TERCER script del TP2 (el primero de analisis propio).

QUE HACE
--------
Separa los disparos (footprints) GEDI que sirven de los que no, y guarda AMBOS
grupos: los aceptados y los descartados CON EL MOTIVO del descarte. Esto ultimo
lo exige la consigna del practico, y no es un capricho: si mas adelante un
modelo de biomasa da mal, lo primero que hay que poder auditar es que datos
entraron y cuales no.

POR QUE HAY QUE FILTRAR GEDI
----------------------------
GEDI no es una imagen: es un laser que dispara huellas de unos 25 m de diametro
desde la Estacion Espacial. Muchos disparos son inutilizables y el archivo NO
los marca como faltantes: vienen con numeros que parecen validos. Las causas mas
comunes son nubes (el laser no atraviesa una nube), poca energia de retorno,
o un angulo de puntería degradado.

LOS TRES FILTROS QUE SE APLICAN, Y POR QUE
------------------------------------------
1. l2a_quality_flag_rel3 == 1
   Es el veredicto del propio algoritmo de la NASA sobre si la forma de onda
   pudo interpretarse. Si vale 0, el dato no es confiable. Es el filtro basico
   y NO es opcional.

2. degrade_flag == 0
   Indica que el estado del instrumento y de la orbita eran normales. Un valor
   distinto de 0 significa que hubo un problema de puntería o de geolocalizacion:
   el disparo puede estar ubicado a decenas de metros de donde dice estar.

3. sensitivity > 0.90 (ver la nota del umbral, mas abajo)
   Es la fraccion de energia que el sensor habria podido detectar si viniera del
   suelo. Con sensibilidad baja, el laser no llego hasta el piso: entonces la
   altura del dosel se mide contra un "suelo" que en realidad esta a media copa,
   y la altura sale subestimada. El umbral 0.95 es el que recomienda la NASA para
   bosques cerrados. Es EXIGENTE a proposito: preferimos menos disparos y buenos.

OJO CON LA VERSION V003
-----------------------
La version V003 de GEDI RENOMBRO las variables: el flag de calidad, que antes se
llamaba 'quality_flag', ahora es 'l2a_quality_flag_rel3'. Un script escrito para
la version anterior no encuentra la columna y devuelve todo vacio SIN DAR NINGUN
ERROR. Es exactamente el error que ocurrio en este proyecto.

ENTRADA   02_Subsets_SNAP_QGIS/GEDI_L2A/*.csv  y  02_Subsets_SNAP_QGIS/GEDI_L2B/*.csv
SALIDA    05_Resultados/04_Tablas/*.csv
          05_Resultados/04_Tablas/*.csv   (con la columna 'motivo')
          05_Resultados/06_Control_calidad/filtrado_calidad.csv

USO (entorno conda 'aoi'):   python TP2_03_filtrar_calidad.py
"""
import csv
import glob
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
INSUMOS = os.path.join(TP2, "02_Subsets_SNAP_QGIS")
RESULTADOS = os.path.join(TP2, "05_Resultados")

# --------------------------------------------------------- umbrales del filtro
# Se puede cambiar al ejecutar:  python TP2_03_filtrar_calidad.py --sensibilidad 0.95
#
# POR QUE 0.90 Y NO 0.95. El 0.95 es la recomendacion para DOSEL CERRADO Y DENSO;
# la general para GEDI L2A es 0.90. Ni este bosque andino bajo (mediana en torno a
# los 7 m) ni el ecotono de estepa son dosel cerrado, de modo que 0.95 se estaba
# aplicando fuera de su dominio de validez.
#
# Y no es un filtro neutral: medido sobre estos datos, el 0.95 elimina
# preferentemente las huellas BAJAS. En el bosque, la mediana de rh95 de las que
# retiene es 8,23 m y la de las que descarta 4,49 m, con lo que sube la mediana
# del conjunto de 6,59 a 8,23 m: un 25 % de sesgo hacia arriba en la variable que
# despues se quiere modelar. En la estepa descarta el 70 % de los disparos validos.
# Como el mismo umbral se aplica a los dos sitios, cuya comparacion es el corazon
# del diseno, parte del contraste bosque-estepa seria un artefacto del filtro.
#
# Ademas trunca el extremo bajo de la distribucion de alturas, que es justamente
# el tramo que necesitan los analisis de saturacion del TP3 y del TP4.
UMBRAL_SENSIBILIDAD = 0.90
if "--sensibilidad" in sys.argv:
    UMBRAL_SENSIBILIDAD = float(sys.argv[sys.argv.index("--sensibilidad") + 1])
EXIGIR_QUALITY = 1              # l2a_quality_flag_rel3 debe valer 1
EXIGIR_DEGRADE = 0              # degrade_flag debe valer 0


def a_float(x, por_defecto=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return por_defecto


def motivo_descarte(fila):
    """Devuelve (categoria, detalle) del descarte, o (None, None) si es valido.

    La CATEGORIA sirve para contar cuantos se perdieron por cada causa.
    El DETALLE guarda el valor exacto, para poder auditar disparo por disparo.
    El orden importa: se informa el PRIMER motivo, que es el mas grave.
    """
    q = a_float(fila.get("l2a_quality_flag_rel3"))
    d = a_float(fila.get("degrade_flag"))
    s = a_float(fila.get("sensitivity"))
    if q != EXIGIR_QUALITY:
        return ("calidad: forma de onda no interpretable",
                "l2a_quality_flag_rel3=%g" % q)
    if d != EXIGIR_DEGRADE:
        return ("degradado: punteria u orbita anomalas",
                "degrade_flag=%g" % d)
    if not (s > UMBRAL_SENSIBILIDAD):
        return ("sensibilidad baja: el laser no llego al suelo",
                "sensitivity=%.3f <= %.2f" % (s, UMBRAL_SENSIBILIDAD))
    return (None, None)


def procesar(ruta_l2a):
    base = os.path.basename(ruta_l2a)
    aoi = "BOSQUE_NW_02" if "BOSQUE" in base else "ESTEPA_NW_02"

    with open(ruta_l2a, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        print("   archivo vacio, se omite")
        return None

    # comprobacion explicita: si la columna clave no esta, el script AVISA.
    # (en V002 se llamaba 'quality_flag'; en V003, 'l2a_quality_flag_rel3')
    if "l2a_quality_flag_rel3" not in filas[0]:
        print("   ERROR: no existe la columna 'l2a_quality_flag_rel3'.")
        print("   Columnas presentes:", list(filas[0])[:12])
        print("   Probablemente el CSV se genero con un script para GEDI V002.")
        return None

    aceptados, descartados = [], []
    for fila in filas:
        cat, det = motivo_descarte(fila)
        if cat is None:
            aceptados.append(fila)
        else:
            fila = dict(fila)
            fila["motivo"] = cat
            fila["detalle"] = det
            descartados.append(fila)

    os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)
    os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)

    sal_ok = os.path.join(RESULTADOS, "04_Tablas",
                          "GEDI_L2A_%s_aceptados.csv" % aoi)
    sal_no = os.path.join(RESULTADOS, "04_Tablas",
                          "GEDI_L2A_%s_descartados.csv" % aoi)
    if aceptados:
        with open(sal_ok, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(aceptados[0]))
            w.writeheader(); w.writerows(aceptados)
    if descartados:
        with open(sal_no, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(descartados[0]))
            w.writeheader(); w.writerows(descartados)

    # --- desglose de motivos, para entender QUE se perdio y por que ---
    motivos = {}
    for d in descartados:
        motivos[d["motivo"]] = motivos.get(d["motivo"], 0) + 1

    n = len(filas)
    print("   total de disparos      : %6d" % n)
    print("   ACEPTADOS              : %6d  (%.1f%%)" % (len(aceptados), 100.0*len(aceptados)/n))
    print("   descartados            : %6d  (%.1f%%)" % (len(descartados), 100.0*len(descartados)/n))
    for k, v in sorted(motivos.items(), key=lambda x: -x[1]):
        print("      %-46s %5d  (%.1f%%)" % (k, v, 100.0*v/n))
    return {"aoi": aoi, "total": n, "aceptados": len(aceptados),
            "descartados": len(descartados), "motivos": motivos}


print(__doc__)
resumen = []
for ruta in sorted(glob.glob(os.path.join(INSUMOS, "GEDI_L2A", "*.csv"))):
    print("=" * 72)
    print(os.path.basename(ruta))
    print("=" * 72)
    r = procesar(ruta)
    if r:
        resumen.append(r)
    print()

# --- tabla de calidad ---
if resumen:
    os.makedirs(os.path.join(RESULTADOS, "06_Control_calidad"), exist_ok=True)
    sal = os.path.join(RESULTADOS, "06_Control_calidad", "filtrado_calidad.csv")
    with open(sal, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["aoi", "disparos_totales", "aceptados", "descartados",
                    "porcentaje_aceptado", "motivo", "cantidad"])
        for r in resumen:
            pct = "%.1f" % (100.0 * r["aceptados"] / r["total"])
            if r["motivos"]:
                for k, v in sorted(r["motivos"].items(), key=lambda x: -x[1]):
                    w.writerow([r["aoi"], r["total"], r["aceptados"],
                                r["descartados"], pct, k, v])
            else:
                w.writerow([r["aoi"], r["total"], r["aceptados"],
                            r["descartados"], pct, "-", 0])
    print("Tabla de calidad -> 05_Resultados/06_Control_calidad/filtrado_calidad.csv")

print()
print("SIGUIENTE PASO:  python TP2_05_filtrar_pendiente.py")
print("(los disparos aceptados aqui todavia deben filtrarse por pendiente)")
