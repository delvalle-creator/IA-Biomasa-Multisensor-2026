#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_07_biomasa_referencia.py   ---> SEPTIMO script del TP2.

QUE HACE
--------
Obtiene la biomasa de referencia por disparo a partir del producto oficial
GEDI L4A, la une a los footprints validos y produce la tabla que usaran como
referencia el TP3, el TP4 y el TP5.

POR QUE L4A Y NO UNA FORMULA PROPIA
-----------------------------------
Es tentador inventar una ecuacion del tipo "biomasa = a * altura^b" con
coeficientes sacados de un paper cualquiera. NO se hace, y conviene entender por
que: los coeficientes alometricos son ESPECIFICOS de un tipo de bosque. Una
ecuacion ajustada en la Amazonia, o en un pinar del hemisferio norte, aplicada a
un bosque de Nothofagus patagonico, produce numeros que parecen razonables y son
falsos. El error no se nota: simplemente todo el TP5 queda mal calibrado.

GEDI L4A (Aboveground Biomass Density) resuelve eso: la NASA ajusto modelos por
GRUPO DE VEGETACION (aqui, bosque templado de hoja caduca del hemisferio sur) con
parcelas de campo reales, y ademas publica el INTERVALO DE PREDICCION de cada
disparo. Es decir, no solo dice cuanta biomasa hay, sino cuanto se puede confiar.

QUE ENTREGA L4A
   agbd            biomasa aerea, en megagramos por hectarea (Mg/ha)
   agbd_se         error estandar de esa estimacion, en Mg/ha
   l4_quality_flag calidad especifica del producto de biomasa
   predict_stratum el grupo de vegetacion con el que se modelo

SI NO SE PUEDE DESCARGAR EL L4A
-------------------------------
El script avisa y NO inventa nada. En ese caso el TP5 debera calibrarse contra
la ALTURA DEL DOSEL (rh95) en vez de contra biomasa, y decirlo explicitamente:
es una limitacion honesta, no un defecto.

ENTRADA   04_Tablas_de_trabajo/01_Bosque | 02_Estepa/*_con_estructura.csv (del TP2_06)
          02_Subsets_SNAP_QGIS/GEDI_L4A/*.csv   (si existe; ver instrucciones abajo)
SALIDA    05_Resultados/04_Tablas/biomasa_<AOI>.csv
          04_Tablas_de_trabajo/04_Entrenamiento/ y 05_Validacion/  (particion por BLOQUES
          ESPACIALES de 3 x 3 km ESTRATIFICADOS POR ALTURA: ver particionar())

USO (entorno conda 'aoi'):   python TP2_07_biomasa_referencia.py
"""
import csv
import glob
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
INSUMOS = os.path.join(TP2, "02_Subsets_SNAP_QGIS")
SUBSETS = os.path.join(TP2, "04_Tablas_de_trabajo")
RESULTADOS = os.path.join(TP2, "05_Resultados")

# La particion NO usa azar: es deterministica (ver particionar()). Por eso ya
# no hay semilla ni fraccion objetivo; se reparte uno de cada cuatro bloques.
LADO_BLOQUE = 3000    # metros. 15 km / 3 km = bloques de 5 x 5 por AOI


# --------------------------------------------------------------------------
# QUE HUELLAS DEL L4A SE ACEPTAN  (decision del 31/07/2026)
# --------------------------------------------------------------------------
# La NASA marca l4_quality_flag = 1 solo si, entre otras cosas, el disparo se
# tomo con el dosel CON HOJAS. Sobre un bosque de caducifolias eso es carisimo:
# de las 690 huellas validas del bosque, 224 -la mitad del rechazo, y 93 de
# ellas de lenga- se descartaban solo por leaf_off_flag = 1.
#
# Se comprobo que la hoja caida NO deprime el AGBD. Comparando a IGUAL estrato
# de la NASA, que es la unica comparacion legitima:
#
#     lenga     DBT_SA    hoja presente 91,33   hoja caida 88,82
#     nire      DBT_SA    hoja presente  2,66   hoja caida  3,95
#     nire bajo DBT_SA    hoja presente  0,06   hoja caida  0,65
#
# Y la NASA les corrio el modelo igual: algorithm_run_flag = 1 en las 224. Lo
# unico que hizo fue no certificarlas.
#
# Asi que se aceptan, con dos condiciones: que pasen el mismo umbral de
# sensibilidad que las certificadas (0,95, medido sobre los datos: la
# sensibilidad mas baja entre todas las aceptadas por la NASA es 0,9501) y que
# queden MARCADAS en la columna agbd_origen, para que cualquiera pueda rehacer
# el calculo sin ellas.
#
# Efecto medido: la muestra del bosque pasa de 271 a 495 huellas, la lenga de 33
# a 126, el AGBD estratificado se mueve de 45,56 a 44,32 Mg/ha -un 2,7 %- y el
# error estandar BAJA de 3,33 a 2,20. Se gana precision sin mover el resultado.
UMBRAL_SENS = 0.95


def cargar_l4a(aoi):
    """Indexa el L4A por shot_number. Devuelve {} si no esta descargado.

    Cada fila queda con un campo extra, 'agbd_origen':
        certificada   l4_quality_flag = 1, la NASA la avala
        hoja_caida    rechazada solo por leaf_off_flag, recuperada aca
    """
    hits = glob.glob(os.path.join(INSUMOS, "GEDI_L4A", "*%s*.csv" % aoi))
    if not hits:
        return {}
    idx = {}
    with open(hits[0], newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            if fila.get("l4_quality_flag", "1") in ("1", "1.0"):
                fila["agbd_origen"] = "certificada"
            elif fila.get("leaf_off_flag", "") == "1":
                try:
                    if float(fila.get("sensitivity", "0")) < UMBRAL_SENS:
                        continue
                except ValueError:
                    continue
                if fila.get("algorithm_run_flag", "1") != "1":
                    continue
                fila["agbd_origen"] = "hoja_caida"
            else:
                continue
            idx[fila["shot_number"]] = fila
    return idx


def mediana(v):
    """Mediana verdadera: con un numero par de valores promedia los dos del
    medio. Devolver v[len(v)//2] a secas da el central superior, no la mediana."""
    v = sorted(v)
    n = len(v)
    if not n:
        return float("nan")
    if n % 2:
        return v[n // 2]
    return (v[n // 2 - 1] + v[n // 2]) / 2.0


def procesar(ruta):
    base = os.path.basename(ruta)
    aoi = "BOSQUE_NW_02" if "BOSQUE" in base else "ESTEPA_NW_02"
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        return None

    l4a = cargar_l4a(aoi)
    hay_l4a = bool(l4a)

    salida, con_bio = [], 0
    for fila in filas:
        d = dict(fila)
        m = l4a.get(d["shot_number"]) if hay_l4a else None
        if m:
            d["agbd_Mg_ha"] = m.get("agbd", "")
            d["agbd_se_Mg_ha"] = m.get("agbd_se", "")
            d["predict_stratum"] = m.get("predict_stratum", "")
            d["agbd_origen"] = m.get("agbd_origen", "")
            d["leaf_off_flag"] = m.get("leaf_off_flag", "")
            con_bio += 1
        else:
            d["agbd_Mg_ha"] = ""
            d["agbd_se_Mg_ha"] = ""
            d["predict_stratum"] = ""
            d["agbd_origen"] = ""
            d["leaf_off_flag"] = ""
        salida.append(d)

    os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)
    sal = os.path.join(RESULTADOS, "04_Tablas", "biomasa_%s.csv" % aoi)
    with open(sal, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(salida[0]))
        w.writeheader(); w.writerows(salida)

    print("   disparos validos        : %5d" % len(salida))
    if hay_l4a:
        bios = [float(d["agbd_Mg_ha"]) for d in salida if d["agbd_Mg_ha"]]
        ses = [float(d["agbd_se_Mg_ha"]) for d in salida if d["agbd_se_Mg_ha"]]
        cert = sum(1 for d in salida if d.get("agbd_origen") == "certificada")
        rec = sum(1 for d in salida if d.get("agbd_origen") == "hoja_caida")
        print("   con biomasa L4A         : %5d" % con_bio)
        print("      certificadas por NASA: %5d" % cert)
        print("      con hoja caida       : %5d  (recuperadas; ver agbd_origen)" % rec)
        if bios:
            print("   biomasa mediana         : %6.1f Mg/ha" % mediana(bios))
            print("   biomasa maxima          : %6.1f Mg/ha" % max(bios))
            if ses:
                print("   error estandar mediano  : %6.1f Mg/ha (%.0f%% de la mediana)"
                      % (mediana(ses), 100.0*mediana(ses)/mediana(bios)))
    else:
        print("   SIN L4A: no hay biomasa. Se usara rh95 como referencia.")
        alturas = [float(d["rh95"]) for d in salida if d.get("rh95")]
        if alturas:
            print("   altura de dosel mediana : %6.2f m" % mediana(alturas))
    return {"aoi": aoi, "filas": salida, "hay_l4a": hay_l4a}


def bloque_de(fila):
    """Celda de la grilla de bloques a la que cae la huella. None si no tiene
    coordenadas proyectadas."""
    try:
        e = float(fila["este_utm19s"])
        n = float(fila["norte_utm19s"])
    except (KeyError, ValueError, TypeError):
        return None
    return (int(e // LADO_BLOQUE), int(n // LADO_BLOQUE))


def particionar(todo):
    """Divide en entrenamiento y validacion POR BLOQUES ESPACIALES.

    POR QUE NO AL AZAR. Las huellas de GEDI no son independientes entre si: se
    reparten a lo largo de las orbitas, de modo que dos huellas contiguas
    distan 60 m y ven practicamente el mismo bosque. Si la particion se hace al
    azar, esas dos vecinas caen una en entrenamiento y otra en validacion, y el
    modelo es evaluado sobre informacion que ya vio. El R2 sale optimista y no
    dice nada sobre la capacidad de predecir en otro lado.

    Repartiendo BLOQUES ENTEROS de 3 x 3 km, la validacion cae sobre terreno
    que el modelo no vio. Es lo que exige el criterio de evaluacion del TP5:
    distinguir mejora real de sobreajuste.
    """
    for grupo in ("04_Entrenamiento", "05_Validacion"):
        os.makedirs(os.path.join(SUBSETS, grupo), exist_ok=True)

    for r in todo:
        filas = list(r["filas"])
        porbloque = {}
        sin_coord = []
        for f in filas:
            b = bloque_de(f)
            if b is None:
                sin_coord.append(f)
            else:
                porbloque.setdefault(b, []).append(f)

        if not porbloque:
            print("   %-14s SIN COORDENADAS: no se puede particionar por bloques"
                  % r["aoi"])
            continue

        # ESTRATIFICADO POR ALTURA. Corregido el 29/07/2026.
        #
        # Antes se barajaban los bloques al azar y se llenaba entrenamiento
        # hasta la fraccion objetivo. El bloque sigue siendo la unidad, asi que
        # no habia filtracion espacial, pero SI un desbalance grave: en el
        # bosque los 22 bloques tienen medianas de rh95 que van de 2,84 a
        # 18,94 m, y el sorteo mandaba los altos a validacion. Medido:
        #
        #     al azar        entrenamiento mediana  4,26 m | validacion 13,54 m
        #     estratificado  entrenamiento mediana  5,35 m | validacion  4,15 m
        #
        # Un modelo entrenado con arbustos y validado con arboles no mide lo
        # que se cree que mide, y el R2 que sale de ahi no es interpretable.
        #
        # La correccion ordena los bloques por su mediana de altura y manda uno
        # de cada cuatro a validacion. Los bloques siguen enteros -no hay
        # filtracion- y las dos particiones cubren todo el rango de alturas.
        bloques = sorted(porbloque, key=lambda b: mediana(
            [float(f["rh95"]) for f in porbloque[b]
             if (f.get("rh95") or "").strip()]))
        entrena, valida = [], []
        for i, b in enumerate(bloques):
            if i % 4 == 3:
                valida.extend(porbloque[b])
            else:
                entrena.extend(porbloque[b])
        # las huellas sin coordenada no se usan para validar: van a entrenamiento
        entrena.extend(sin_coord)

        for grupo, parte in (("04_Entrenamiento", entrena),
                             ("05_Validacion", valida)):
            if not parte:
                continue
            sal = os.path.join(SUBSETS, grupo, "GEDI_%s_%s.csv"
                               % (r["aoi"], grupo.lower()))
            with open(sal, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(parte[0]))
                w.writeheader(); w.writerows(parte)

        nb_e = sum(1 for b in bloques if porbloque[b] and porbloque[b][0] in entrena)
        print("   %-14s entrenamiento %4d / validacion %4d  "
              "(%d bloques de %d m, %d a entrenamiento)"
              % (r["aoi"], len(entrena), len(valida), len(bloques),
                 LADO_BLOQUE, nb_e))
        if sin_coord:
            print("   %-14s %d huellas sin coordenada proyectada -> entrenamiento"
                  % ("", len(sin_coord)))


print(__doc__)
archivos = sorted(glob.glob(os.path.join(SUBSETS, "0[12]_*",
                                         "*_con_estructura.csv")))
if not archivos:
    sys.exit("No hay footprints con estructura.\n"
             "Ejecute antes:  python TP2_06_metricas_estructura.py")

if not glob.glob(os.path.join(INSUMOS, "GEDI_L4A", "*.csv")):
    print("!" * 72)
    print("AVISO: no hay producto GEDI L4A.")
    print("Si lo descarga, CREE la carpeta 02_Subsets_SNAP_QGIS/GEDI_L4A/ y ponga ahi el .csv.")
    print("Sin el, este script NO estima biomasa (y no la inventa).")
    print("Para obtenerlo: coleccion 'GEDI_L4A_AGB_Density_V2_1_2056' en NASA")
    print("Earthdata, misma zona y periodo (sep. 2024 a mar. 2025). Se extrae")
    print("igual que el L2A, con el script TP2_02_recortar_AOI.py adaptado.")
    print("Mientras tanto se usara rh95 (altura del dosel) como referencia.")
    print("!" * 72)
    print()

todo = []
for ruta in archivos:
    print("=" * 72)
    print(os.path.basename(ruta))
    print("=" * 72)
    r = procesar(ruta)
    if r:
        todo.append(r)
    print()

if todo:
    print("=" * 72)
    print("PARTICION POR BLOQUES ESPACIALES ESTRATIFICADOS POR ALTURA")
    print("=" * 72)
    particionar(todo)

print()
print("SIGUIENTE PASO:  python TP2_08_exportar_para_gis.py")
print("(exporta las huellas a QGIS para que usted VERIFIQUE todo esto en un mapa)")
print()
print("Productos del TP2 que consumen los practicos siguientes:")
print("Los productos que usaran el TP3, el TP4 y el TP5 son:")
print("   04_Tablas_de_trabajo/04_Entrenamiento/ y 05_Validacion/")
print("   05_Resultados/04_Tablas/")
print()
print("Recuerde declarar en el informe que GEDI es de sep. 2024 a mar. 2025 y")
print("NO es contemporaneo de la linea de base 2023-24 (el instrumento estuvo")
print("hibernado entre marzo de 2023 y abril de 2024).")
