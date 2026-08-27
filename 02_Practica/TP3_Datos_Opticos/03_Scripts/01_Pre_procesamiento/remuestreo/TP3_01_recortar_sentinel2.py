#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_recortar_s2.py
Recorta las escenas Sentinel-2 L2A a la grilla comun de 15 x 15 km
(EPSG:32719, 10 m, 1500 x 1500 px) usando SNAP (gpt), de modo que el resultado
CONSERVE LOS METADATOS del producto.

SALIDA, en ../04_Tablas_de_trabajo/<AOI>/S2_L2A/:
  *_subset15km.dim + .data   PRODUCTO PRINCIPAL (BEAM-DIMAP, formato nativo de
                             SNAP). Mantiene metadatos, angulos solares y de
                             vista, y las mascaras: puede procesarse en SNAP
                             (p. ej. con el Biophysical Processor: LAI, FAPAR).
  *_subset15km.tif           copia GeoTIFF, solo para visualizar en QGIS.
                             NO usar como entrada de SNAP: pierde los metadatos.

Nota sobre formatos: dentro del .SAFE, la ESA distribuye cada banda en
JPEG-2000 (.jp2). Si SNAP no las lee, revise que la instalacion este completa.

REQUISITOS: SNAP instalado ('gpt' en el PATH, o editar GPT mas abajo) y el
entorno conda 'aoi' (para la copia GeoTIFF).
USO:  python 03_recortar_s2.py              (todas las epocas)
      python 03_recortar_s2.py pre_incendio  (solo una epoca)
"""
import glob
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

try:
    from osgeo import gdal
except ImportError:
    sys.exit("Falta GDAL. Ejecutar: conda activate aoi")


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

from aoi_config import (AOIS_UTM, DESCARGAS, PROCESADOS, GRAFOS, PIXEL,
                        EPOCAS)
import nombres

gdal.UseExceptions()
GPT = "gpt"                 # o la ruta completa a gpt.exe
MEM_GPT = ["-c", "4G", "-q", "4"]
GRAFO = os.path.join(GRAFOS, "graph_s2_l2a_subset.xml")


def hay_gpt():
    try:
        subprocess.run([GPT, "-h"], capture_output=True, timeout=180)
        return True
    except Exception:
        return False


def bandas_del_dim(dim):
    raiz = ET.parse(dim).getroot()
    carpeta = dim[:-4] + ".data"
    salida = []
    for b in raiz.findall(".//Spectral_Band_Info"):
        nombre = b.find("BAND_NAME").text
        img = os.path.join(carpeta, nombre + ".img")
        if os.path.exists(img):
            salida.append((nombre, img))
    return salida


def copia_geotiff(dim, tif, solo=None):
    """GeoTIFF para QGIS. 'solo' permite quedarse con algunas bandas."""
    bandas = bandas_del_dim(dim)
    if solo:
        bandas = [b for b in bandas if b[0] in solo]
        bandas.sort(key=lambda b: solo.index(b[0]))
    if not bandas:
        print("   aviso: no se pudo generar la copia GeoTIFF")
        return
    vrt = gdal.BuildVRT("", [img for _, img in bandas], separate=True)
    gdal.Translate(tif + ".tmp", vrt, format="GTiff",
                   creationOptions=["COMPRESS=DEFLATE", "TILED=YES"])
    os.replace(tif + ".tmp", tif)
    ds = gdal.Open(tif, gdal.GA_Update)
    for i, (nombre, _) in enumerate(bandas, 1):
        ds.GetRasterBand(i).SetDescription(nombre)
    ds = None


# Bandas que se vuelcan a la copia GeoTIFF (para QGIS). Las diez opticas mas la
# clasificacion de escena, que en SNAP se llama quality_scene_classification y
# equivale a la mascara SCL del producto original (3 = sombra de nube,
# 8 y 9 = nube, 10 = cirrus, 4 = vegetacion, 5 = suelo desnudo).
B_GEOTIFF = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12",
             "quality_scene_classification"]


def procesar(zip_s2, aoi, epoca):
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    original = os.path.basename(zip_s2)[:-4]
    # nombre CORTO para la salida: Windows limita la ruta a 260 caracteres y el
    # nombre original, sumado a la carpeta .data, agota ese limite.
    corto, fecha = nombres.corto_sentinel2(original)
    outdir = os.path.join(PROCESADOS, "Sentinel_2", epoca, aoi)
    os.makedirs(outdir, exist_ok=True)
    base = os.path.join(outdir, corto)
    dim, tif = base + ".dim", base + ".tif"
    if os.path.exists(dim):
        print("   ya existe, se omite")
        return True

    t0 = time.time()
    print("   SNAP gpt: remuestreo a 10 m y reproyeccion a la grilla comun...",
          flush=True)
    cmd = ([GPT, GRAFO] + MEM_GPT
           + ["-Pentrada=" + zip_s2,
              "-Psalida=" + dim,
              "-Peasting=%f" % xmin,      # esquina superior izquierda de la grilla
              "-Pnorthing=%f" % ymax])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dim):
        print("   ERROR en gpt:")
        print("   " + (r.stderr or r.stdout or "")[-700:].replace("\n", "\n   "))
        return False

    print("   copia GeoTIFF para QGIS (10 bandas + SCL)...", flush=True)
    copia_geotiff(dim, tif, solo=B_GEOTIFF)
    nombres.registrar(PROCESADOS, [corto, aoi, "S2_L2A", fecha, original,
                                os.path.basename(zip_s2)])
    print("   OK (%.1f min) -> %s.dim" % ((time.time() - t0) / 60, corto),
          flush=True)
    return True


print(__doc__)
if not hay_gpt():
    sys.exit("No se encontro '%s'. Instalar SNAP o editar la variable GPT." % GPT)

hechos, fallidos = 0, 0
FILTRO_EPOCA = sys.argv[1] if len(sys.argv) > 1 else ""
for epoca in EPOCAS:
    if FILTRO_EPOCA and FILTRO_EPOCA not in epoca:
        continue
    for aoi in AOIS_UTM:
        zips = sorted(glob.glob(os.path.join(DESCARGAS, epoca, aoi,
                                             "S2_L2A", "*.zip")))
        if not zips:
            continue
        print("\n=== %s | %s: %d escenas ===" % (epoca, aoi, len(zips)), flush=True)
        for z in zips:
            print(" ", os.path.basename(z), flush=True)
            if procesar(z, aoi, epoca):
                hechos += 1
            else:
                fallidos += 1

print("\nListo. %d escenas procesadas, %d con error." % (hechos, fallidos))
print("PRINCIPAL: 04_Tablas_de_trabajo/<AOI>/S2_L2A/*.dim (BEAM-DIMAP, con metadatos y "
      "mascaras: usar este en SNAP)")
print("Copia GIS: el .tif del mismo nombre, solo para visualizar en QGIS.")
