#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP1_09_inventario.py
Recorre TODO el proyecto y produce el inventario del conjunto de datos, por
epoca, antes de pasar al preprocesamiento.

Salida (en TP1_Busqueda_IA/02_Subsets_SNAP_QGIS/03_Tablas/):
  inventario.csv    tabla plana, un renglon por producto

USO:  python TP1_09_inventario.py
"""
import sys
import csv
import glob
import os
import re


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

from aoi_config import (AOIS_UTM, DESCARGAS, EPOCAS, BASE,
                        dir_procesado, dir_crudo, dir_gedi)

FECHAS_ALOS = {
    "ALPSRP079284470": "20070721", "ALPSRP079284480": "20070721",
    "ALPSRP085994470": "20070905", "ALPSRP085994480": "20070905",
    "ALPSRP099414470": "20071206", "ALPSRP099414480": "20071206",
    "ALPSRP172576320": "20090421", "ALPSRP172576330": "20090421",
    "ALPSRP179286320": "20090606", "ALPSRP179286330": "20090606",
}


def fecha_de(nombre):
    for g, fe in FECHAS_ALOS.items():
        if g in nombre:
            return fe
    m = re.search(r"(20\d{2})(\d{2})(\d{2})T", nombre)
    if m:
        return "".join(m.groups())
    m = re.search(r"_(20\d{6})_", nombre) or re.search(r"(20\d{6})", nombre)
    return m.group(1) if m else ""


def gb(ruta):
    if os.path.isdir(ruta):
        return sum(os.path.getsize(os.path.join(d, f))
                   for d, _, fs in os.walk(ruta) for f in fs) / 1e9
    return os.path.getsize(ruta) / 1e9 if os.path.exists(ruta) else 0.0


def hay(carpeta, fecha, sufijo="*.dim"):
    """Busca un producto de esa fecha en la carpeta real. Tolera que no exista."""
    if not carpeta or not fecha:
        return False
    # Sentinel-2 queda recortado como GeoTIFF (.tif), no como producto .dim de
    # SNAP: por defecto se acepta cualquiera de los dos.
    sufijos = ("*.dim", "*.tif") if sufijo == "*.dim" else (sufijo,)
    return any(glob.glob(os.path.join(carpeta, "*%s%s" % (fecha, s)))
               for s in sufijos)


filas = []
for epoca in EPOCAS:
    # ---- Sentinel-1 y Sentinel-2 ----
    for aoi in AOIS_UTM:
        for sensor in ("S2_L2A", "S1_GRD", "S1_SLC"):
            for z in sorted(glob.glob(os.path.join(DESCARGAS, epoca, aoi,
                                                   sensor, "*.zip"))):
                nombre = os.path.basename(z)[:-4]
                fe = fecha_de(nombre)
                proc = hay(dir_procesado(sensor, epoca, aoi), fe)
                crudo = hay(dir_crudo(sensor, epoca, aoi), fe, "*_crudo.dim")
                filas.append([epoca, aoi, sensor, fe, nombre,
                              "%.2f" % gb(z),
                              "si" if proc else "no",
                              "si" if crudo else "-" if sensor != "S1_SLC" else "no"])
        # ---- ALOS ----
        for z in sorted(glob.glob(os.path.join(DESCARGAS, epoca, aoi,
                                               "ALOS_PALSAR_QP", "*", "*.zip"))):
            nombre = os.path.basename(z)
            fe = fecha_de(nombre)
            filas.append([epoca, aoi, "ALOS_QP", fe, nombre, "%.2f" % gb(z),
                          "no", "-"])
    # ---- SAOCOM (cubre los dos AOI) ----
    # Un producto SAOCOM es una CARPETA con un .xemt adentro. Se exige el .xemt
    # para no contar como producto los LEEME.md ni cualquier otro archivo suelto
    # que haya en la carpeta de la epoca.
    for x in sorted(glob.glob(os.path.join(DESCARGAS, epoca, "SAOCOM",
                                           "*", "*.xemt"))):
        d = os.path.dirname(x)
        txt = open(x, encoding="utf-8", errors="ignore").read()
        m = re.search(r"<startTime>(\d{4})-(\d{2})-(\d{2})", txt)
        fe = "".join(m.groups()) if m else ""
        pid = os.path.basename(d)
        for aoi in AOIS_UTM:
            proc = hay(dir_procesado("SAOCOM_L1A", epoca, aoi), fe)
            crudo = hay(dir_crudo("SAOCOM_L1A", epoca, aoi), fe, "*_crudo.dim")
            filas.append([epoca, aoi, "SAOCOM_L1A", fe, pid, "%.2f" % gb(d),
                          "si" if proc else "no", "si" if crudo else "no"])
    # ---- GEDI ----
    for aoi in AOIS_UTM:
        h5 = glob.glob(os.path.join(DESCARGAS, epoca, "GEDI", aoi, "*", "*.h5"))
        if h5:
            # los CSV de GEDI llevan el AOI en el NOMBRE, no en la carpeta
            csvs = glob.glob(os.path.join(dir_gedi(), "*", "*%s*.csv" % aoi))
            filas.append([epoca, aoi, "GEDI", "2024-2025",
                          "%d granulos (L2A + L2B)" % len(h5),
                          "%.2f" % sum(gb(f) for f in h5),
                          "si" if csvs else "no", "-"])
    # ---- NISAR ----
    for prod in sorted(glob.glob(os.path.join(DESCARGAS, epoca, "NISAR", "*"))):
        h5 = glob.glob(os.path.join(prod, "*.h5"))
        if h5:
            filas.append([epoca, "AMBOS", "NISAR_" + os.path.basename(prod),
                          "2025-2026", "%d granulos" % len(h5),
                          "%.2f" % sum(gb(f) for f in h5), "no", "-"])

ENCAB = ["epoca", "aoi", "sensor", "fecha", "producto", "GB",
         "procesado", "recorte_crudo"]
# El inventario es el insumo del TP1, y ahi lo busca su LEEME. No va a
# 05_Resultados: no es un resultado del analisis, es el punto de partida.
TABLAS = os.path.join(BASE, "02_Subsets_SNAP_QGIS", "03_Tablas")
os.makedirs(TABLAS, exist_ok=True)
ruta_csv = os.path.join(TABLAS, "inventario.csv")
with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(ENCAB)
    w.writerows(filas)

print(__doc__)
print("=== INVENTARIO POR EPOCA ===")
for epoca in EPOCAS:
    fs = [f for f in filas if f[0] == epoca]
    if not fs:
        print("\n  %s: (sin datos aun)" % epoca)
        continue
    gbs = sum(float(f[5]) for f in fs)
    proc = sum(1 for f in fs if f[6] == "si")
    print("\n  %s  (%d productos, %.1f GB, %d procesados)"
          % (epoca, len(fs), gbs, proc))
    print("     %s" % EPOCAS[epoca]["que_es"])
    sensores = {}
    for f in fs:
        sensores.setdefault(f[2], []).append(f[3])
    for s, fechas in sorted(sensores.items()):
        u = sorted(set(fechas))
        print("       %-14s %d producto(s)  fechas: %s"
              % (s, len(fechas), ", ".join(u[:5]) + (" ..." if len(u) > 5 else "")))

print("\nCSV: %s" % ruta_csv)
