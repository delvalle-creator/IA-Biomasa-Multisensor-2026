#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP1_10_reconstruir_diccionario.py   (utilidad)

Reconstruye desde cero los diccionarios de nombres, recorriendo los productos
ORIGINALES de 00_COMUN/08_Originales_crudos y comprobando cuales tienen ya
su recorte generado.

Sirve para reparar el CSV si quedo incompleto (por ejemplo, si se interrumpio un
script o se movieron carpetas mientras corria), y para verificar que cada
producto de salida tiene su equivalente de entrada.

Los diccionarios se escriben DESDE CERO (modo "w"). Por eso el script se niega a
escribir un diccionario vacio: si no encuentra ningun producto es que las rutas
estan mal, y borrar el CSV bueno seria peor que no hacer nada.

USO:  python TP1_10_reconstruir_diccionario.py
"""
import csv
import glob
import os
import re
import sys


# La carpeta funciones/ es hermana de esta, no esta en el sys.path por defecto.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "funciones"))


# --- para que Python encuentre funciones/ y configuracion/ del practico ---
# Se sube por el arbol hasta dar con la carpeta 'funciones', de modo que el
# script corra desde cualquier directorio de trabajo y a cualquier profundidad.
_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d):
    if os.path.isdir(os.path.join(_d, "funciones")):
        sys.path.insert(0, os.path.join(_d, "funciones"))
        sys.path.insert(0, os.path.join(_d, "configuracion"))
        break
    _d = os.path.dirname(_d)

from aoi_config import (AOIS_UTM, DESCARGAS, EPOCAS,
                        dir_procesado, dir_crudo, ruta_practico)
import nombres


def fecha_saocom(xemt):
    txt = open(xemt, encoding="utf-8", errors="ignore").read()
    m = re.search(r"<startTime>(\d{4})-(\d{2})-(\d{2})", txt)
    return "".join(m.groups()) if m else "00000000"


def existe_producto(carpeta, corto):
    """True si el producto procesado esta, como .dim de SNAP o como GeoTIFF.
    Sentinel-2 queda recortado como .tif, no como .dim."""
    return bool(carpeta) and any(os.path.exists(os.path.join(carpeta, corto + ext))
                                 for ext in (".dim", ".tif"))


def escribir(destino, filas, etiqueta):
    ruta = os.path.join(destino, nombres.CSV_DICCIONARIO)
    if not filas:
        print("  %s: 0 entradas -> NO se escribe (se conserva el CSV actual)."
              % etiqueta)
        return 0
    os.makedirs(destino, exist_ok=True)
    filas.sort(key=lambda r: (r[1], r[2], r[3]))
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(nombres.ENCABEZADO)
        w.writerows(filas)
    print("  %s: %d entradas" % (etiqueta, len(filas)))
    return len(filas)


proc, crudo = [], []
faltan = []

# Las descargas cuelgan de <epoca>/, y los productos procesados de
# <practico>/02_Subsets_SNAP_QGIS/<grupo>/<epoca>/<AOI>/. Sin recorrer las epocas no se
# encuentra nada: es el bug que vaciaba los diccionarios.
for epoca in EPOCAS:
    for aoi in AOIS_UTM:
        # -------- Sentinel-2 --------
        for z in sorted(glob.glob(os.path.join(DESCARGAS, epoca, aoi,
                                               "S2_L2A", "*.zip"))):
            original = os.path.basename(z)[:-4]
            corto, fecha = nombres.corto_sentinel2(original)
            d = dir_procesado("S2_L2A", epoca, aoi)
            if existe_producto(d, corto):
                proc.append([corto, aoi, "S2_L2A", fecha, original,
                             os.path.basename(z)])
            else:
                faltan.append("%s | %s | S2_L2A | %s" % (epoca, aoi, corto))

        # -------- Sentinel-1 --------
        for sensor in ("S1_GRD", "S1_SLC"):
            for z in sorted(glob.glob(os.path.join(DESCARGAS, epoca, aoi,
                                                   sensor, "*.zip"))):
                original = os.path.basename(z)[:-4]
                corto, fecha = nombres.corto_sentinel1(original)
                d = dir_procesado(sensor, epoca, aoi)
                if existe_producto(d, corto):
                    proc.append([corto, aoi, sensor, fecha, original,
                                 os.path.basename(z)])
                else:
                    faltan.append("%s | %s | %s | %s" % (epoca, aoi, sensor, corto))
                if sensor == "S1_SLC":
                    c = dir_crudo(sensor, epoca, aoi)
                    if os.path.exists(os.path.join(c, corto + "_crudo.dim")):
                        crudo.append([corto + "_crudo", aoi, "S1_SLC_crudo",
                                      fecha, original, os.path.basename(z)])

    # -------- SAOCOM (vive en <epoca>/SAOCOM/, y sirve a los dos AOI) --------
    for x in sorted(glob.glob(os.path.join(DESCARGAS, epoca, "SAOCOM",
                                           "*", "*.xemt"))):
        original = os.path.basename(os.path.dirname(x))
        corto, fecha = nombres.corto_saocom(original, fecha_saocom(x))
        for aoi in AOIS_UTM:
            d = dir_procesado("SAOCOM_L1A", epoca, aoi)
            if existe_producto(d, corto):
                proc.append([corto, aoi, "SAOCOM_L1A", fecha, original,
                             os.path.basename(x)])
            else:
                faltan.append("%s | %s | SAOCOM_L1A | %s" % (epoca, aoi, corto))
            c = dir_crudo("SAOCOM_L1A", epoca, aoi)
            if os.path.exists(os.path.join(c, corto + "_crudo.dim")):
                crudo.append([corto + "_crudo", aoi, "SAOCOM_L1A_crudo", fecha,
                              original, os.path.basename(x)])

print(__doc__)

# Los dos diccionarios viven en TP4: el de gamma0 en 02_Subsets_SNAP_QGIS, y el de los
# recortes con fase en 02_Subsets_SNAP_QGIS/00_Recortes_crudos_fase.
DEST_PROC = ruta_practico("TP4", "02_Subsets_SNAP_QGIS")
DEST_CRUDO = os.path.join(DEST_PROC, "00_Recortes_crudos_fase")

if not proc and not crudo:
    sys.exit("No se encontro NINGUN producto procesado. Antes de escribir nada:\n"
             "revise que las rutas de UBICACION en aoi_config.py sigan siendo las\n"
             "reales. No se toco ningun CSV.")

print("Diccionarios reconstruidos:")
n1 = escribir(DEST_PROC, proc, "gamma0 / reflectancia")
n2 = escribir(DEST_CRUDO, crudo, "recortes crudos con fase")

# GEDI: no lleva nombre corto (los CSV ya son legibles), pero se informa
gedi = len(glob.glob(os.path.join(ruta_practico("TP2", "02_Subsets_SNAP_QGIS"),
                                  "*", "*.csv")))
print("\nResumen:")
print("  procesados (gamma0, grilla comun): %d" % n1)
print("  recortes crudos (con fase):        %d" % n2)
print("  CSV de GEDI:                       %d" % gedi)
if faltan:
    print("\nProductos descargados SIN recorte procesado (revisar):")
    for f in faltan:
        print("   -", f)
else:
    print("\nTodos los productos descargados tienen su recorte procesado.")
