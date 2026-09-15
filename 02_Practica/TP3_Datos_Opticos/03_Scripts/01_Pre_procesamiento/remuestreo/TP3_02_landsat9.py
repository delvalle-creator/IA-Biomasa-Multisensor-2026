#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP3_02_landsat9.py
Descarga Landsat 9 (OLI-2) Coleccion 2 Nivel-2 -reflectancia de superficie ya
corregida atmosfericamente, 30 m- y lo recorta a los dos AOI, en DOS versiones:

  - NATIVA 30 m  (500 x 500 px): el dato fiel, sin remuestreo mas alla del
                 recorte. Es como se ve realmente Landsat 9.
  - COMUN 10 m   (1500 x 1500 px, EPSG:32719): la misma grilla que Sentinel-2,
                 Sentinel-1 y NISAR, para poder superponer pixel a pixel. Las
                 bandas de reflectancia se remuestrean por interpolacion
                 BILINEAL (para que no se vean escalonadas); la banda de
                 calidad QA_PIXEL, que es categorica, por VECINO MAS CERCANO.

IMPORTANTE sobre la resolucion: remuestrear a 10 m NO agrega detalle. La
resolucion real de Landsat 9 sigue siendo de 30 m; la grilla de 10 m solo sirve
para el apilado con los demas sensores. Por eso se conserva tambien la version
nativa de 30 m.

ACCESO: Microsoft Planetary Computer, catalogo abierto, SIN credenciales. Cada
banda es un GeoTIFF en la nube (COG); el script pide una firma temporal (token
SAS) y lee unicamente la ventana del AOI, de modo que descarga muy pocos MB por
banda en lugar de la escena entera.

Se elige, en cada epoca, la escena Landsat 9 de MENOR nubosidad sobre el AOI.
Landsat 9 se lanzo en septiembre de 2021, de modo que NO cubre la epoca
historica 2007-2010.

USO (entorno conda 'aoi'):   python TP3_02_landsat9.py
"""
import json
import os
import sys

try:
    import requests
    from osgeo import gdal, osr
except ImportError:
    sys.exit("Falta requests o GDAL. Activar el entorno conda 'aoi'.")


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

from aoi_config import AOIS_UTM, AOIS_WGS84, PROCESADOS, EPSG, PIXEL

gdal.UseExceptions()
# Lectura remota de COG por /vsicurl/: no intentar listar el "directorio"
# (la URL lleva el token como query y romperia la deteccion por extension).
gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
gdal.SetConfigOption("CPL_VSIL_CURL_USE_HEAD", "NO")
gdal.SetConfigOption("GDAL_HTTP_MAX_RETRY", "3")
gdal.SetConfigOption("GDAL_HTTP_RETRY_DELAY", "2")

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token/landsateuwest/landsat-c2"

# Bandas de reflectancia de superficie que interesan (equivalentes a las de
# Sentinel-2 que ya se usan) y la banda de calidad.
REFLECT = [("coastal", "SR_B1_coastal"), ("blue", "SR_B2_blue"),
           ("green", "SR_B3_green"), ("red", "SR_B4_red"),
           ("nir08", "SR_B5_nir"), ("swir16", "SR_B6_swir16"),
           ("swir22", "SR_B7_swir22")]
QA = ("qa_pixel", "QA_PIXEL")
ESCALA, OFFSET = 0.0000275, -0.2      # DN -> reflectancia de superficie

# Ventana de busqueda por epoca (se elige la de menor nubosidad dentro de ella).
EPOCAS = {
    "01_base": ("2023-10-01", "2024-03-31"),
    "02_pre": ("2025-11-01", "2026-01-10"),   # el fuego empieza el 10/01
    "03_post": ("2026-02-27", "2026-04-20"),   # se apaga el 27/02
}
MAX_NUBES = 60        # % maximo de nubosidad de escena aceptable

# Carpeta REAL de cada epoca en 02_Subsets_SNAP_QGIS/Landsat_8_9. Antes se usaba
# la clave corta (01_base, 02_pre, 03_post) como nombre de carpeta: el script no
# reconocia las escenas ya descargadas y las volvia a bajar en carpetas nuevas,
# duplicadas. Corregido el 11/09/2026.
CARPETA = {"01_base": "01_linea_base_2023_24",
           "02_pre": "02_pre_incendio_2025_26",
           "03_post": "03_post_incendio_2026"}


def escena_existente(epoca, aoi):
    """Devuelve el nombre de la escena Landsat 9 ya recortada, o None."""
    d = os.path.join(PROCESADOS, "Landsat_8_9", CARPETA.get(epoca, epoca), aoi)
    if not os.path.isdir(d):
        return None
    for f in sorted(os.listdir(d)):
        if f.startswith("LC09_") and f.endswith(".tif") and "_QA" not in f \
                and "nativo" not in f:
            return f
    return None


def bbox_union():
    lon = [v[0] for v in AOIS_WGS84.values()] + [v[2] for v in AOIS_WGS84.values()]
    lat = [v[1] for v in AOIS_WGS84.values()] + [v[3] for v in AOIS_WGS84.values()]
    return [min(lon), min(lat), max(lon), max(lat)]


def buscar_mejor_escena(desde, hasta):
    """Devuelve el item Landsat 9 de menor nubosidad que cubre los dos AOI."""
    cuerpo = {
        "collections": ["landsat-c2-l2"],
        "bbox": bbox_union(),
        "datetime": "%sT00:00:00Z/%sT23:59:59Z" % (desde, hasta),
        "query": {"platform": {"eq": "landsat-9"},
                  "eo:cloud_cover": {"lt": MAX_NUBES}},
        "sortby": [{"field": "eo:cloud_cover", "direction": "asc"}],
        "limit": 20,
    }
    r = requests.post(STAC, json=cuerpo, timeout=90)
    r.raise_for_status()
    items = r.json().get("features", [])
    if not items:
        return None
    # el que menos nubes tiene y cuya huella contiene la caja de union
    from shapely.geometry import shape, box
    caja = box(*bbox_union())
    for it in items:
        geom = shape(it["geometry"])
        if geom.contains(caja) or geom.intersection(caja).area / caja.area > 0.99:
            return it
    return items[0]        # si ninguno la contiene del todo, el de menos nubes


def firmar(href, token):
    return "/vsicurl/%s?%s" % (href, token)


def recortar_banda(src_firmado, xmin, ymin, xmax, ymax, res, alg):
    """Recorta y remuestrea una banda al AOI. Devuelve un dataset en memoria."""
    return gdal.Warp("", src_firmado, format="MEM",
                     dstSRS="EPSG:%d" % EPSG,
                     outputBounds=(xmin, ymin, xmax, ymax),
                     xRes=res, yRes=res, targetAlignedPixels=False,
                     resampleAlg=alg, srcNodata=0, dstNodata=0)


def a_reflectancia(ds):
    """Convierte DN a reflectancia de superficie (Float32, 0..1)."""
    import numpy as np
    a = ds.GetRasterBand(1).ReadAsArray().astype("float32")
    val = a > 0
    out = np.where(val, a * ESCALA + OFFSET, 0.0).astype("float32")
    np.clip(out, 0.0, 1.0, out=out)
    out[~val] = 0.0
    return out


def escribir(ruta, capas, x0, y0, res, tipo):
    nx, ny = capas[0][1].shape[1], capas[0][1].shape[0]
    ds = gdal.GetDriverByName("GTiff").Create(
        ruta, nx, ny, len(capas), tipo,
        options=["COMPRESS=DEFLATE", "TILED=YES"])
    ds.SetGeoTransform((x0, res, 0, y0, 0, -res))
    sr = osr.SpatialReference(); sr.ImportFromEPSG(EPSG)
    ds.SetProjection(sr.ExportToWkt())
    for i, (nom, arr) in enumerate(capas, 1):
        b = ds.GetRasterBand(i); b.WriteArray(arr); b.SetDescription(nom)
        if tipo == gdal.GDT_Float32:
            b.SetNoDataValue(0.0)
    ds.FlushCache(); ds = None


def procesar_aoi(item, token, aoi, epoca):
    import numpy as np
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    fecha = item["properties"]["datetime"][:10].replace("-", "")
    nubes = item["properties"].get("eo:cloud_cover", -1)
    corto = "LC09_%s" % fecha
    outdir = os.path.join(PROCESADOS, "Landsat_8_9", CARPETA.get(epoca, epoca), aoi)
    os.makedirs(outdir, exist_ok=True)
    nat = os.path.join(outdir, corto + "_nativo30m.tif")
    com = os.path.join(outdir, corto + ".tif")
    if os.path.exists(com):
        print("     %s ya existe, se omite" % aoi)
        return True

    # --- reflectancia: nativa 30 m (nearest, fiel) y comun 10 m (bilineal) ---
    cap_nat, cap_com = [], []
    for asset, nombre in REFLECT:
        href = item["assets"][asset]["href"]
        src = firmar(href, token)
        dn30 = recortar_banda(src, xmin, ymin, xmax, ymax, 30, "near")
        dn10 = recortar_banda(src, xmin, ymin, xmax, ymax, PIXEL, "bilinear")
        cap_nat.append((nombre, a_reflectancia(dn30)))
        cap_com.append((nombre, a_reflectancia(dn10)))
    escribir(nat, cap_nat, xmin, ymax, 30, gdal.GDT_Float32)
    escribir(com, cap_com, xmin, ymax, PIXEL, gdal.GDT_Float32)

    # --- QA_PIXEL: categorica, SIEMPRE vecino mas cercano --------------------
    hrefqa = item["assets"][QA[0]]["href"]
    qa30 = recortar_banda(firmar(hrefqa, token), xmin, ymin, xmax, ymax, 30, "near")
    qa10 = recortar_banda(firmar(hrefqa, token), xmin, ymin, xmax, ymax, PIXEL, "near")
    escribir(nat.replace(".tif", "_QA.tif"),
             [(QA[1], qa30.GetRasterBand(1).ReadAsArray())], xmin, ymax, 30, gdal.GDT_UInt16)
    escribir(com.replace(".tif", "_QA.tif"),
             [(QA[1], qa10.GetRasterBand(1).ReadAsArray())], xmin, ymax, PIXEL, gdal.GDT_UInt16)

    # nubosidad REAL dentro del AOI (bits 3 nube y 4 sombra de QA_PIXEL)
    qa = qa10.GetRasterBand(1).ReadAsArray()
    nube = ((qa >> 3) & 1) | ((qa >> 4) & 1)
    valido = qa > 1
    pct = 100.0 * nube[valido].mean() if valido.any() else 100.0
    print("     %s  %s  nubes escena=%.0f%%  nubes dentro del AOI=%.1f%%"
          % (aoi, fecha, nubes, pct))
    return True


print(__doc__)
token = None      # se pide recien cuando hay algo que descargar

for epoca, (desde, hasta) in EPOCAS.items():
    print("=" * 72)
    print("%s   (busqueda %s a %s)" % (epoca, desde, hasta))
    # Si los dos recintos ya tienen su escena, no se busca ni se descarga nada:
    # asi el alumno no pisa ni duplica los recortes que vienen con el curso.
    ya = {aoi: escena_existente(epoca, aoi) for aoi in AOIS_UTM}
    if all(ya.values()):
        for aoi, f in ya.items():
            print("     %s: ya esta %s, se omite" % (aoi, f))
        continue
    if token is None:
        token = requests.get(SAS, timeout=60).json()["token"]
        print("Token de acceso obtenido (Planetary Computer, sin credenciales).\n")
    item = buscar_mejor_escena(desde, hasta)
    if not item:
        print("   sin escenas Landsat 9 con nubosidad < %d%% en esta ventana" % MAX_NUBES)
        continue
    for aoi in AOIS_UTM:
        if ya[aoi]:
            # ese recinto ya tiene su escena: no se le agrega otra
            print("     %s: ya esta %s, se omite" % (aoi, ya[aoi]))
            continue
        procesar_aoi(item, token, aoi, epoca)
print("\nListo. Salida en 02_Subsets_SNAP_QGIS/Landsat_8_9/<epoca>/<AOI>/")
print("  LC09_<fecha>.tif            reflectancia, grilla comun 10 m (bilineal)")
print("  LC09_<fecha>_nativo30m.tif  reflectancia, resolucion nativa 30 m")
print("  ..._QA.tif                  banda de calidad QA_PIXEL (vecino mas cercano)")
print("Bandas de reflectancia en Float32 (0 a 1). Se abren en QGIS y en SNAP.")
