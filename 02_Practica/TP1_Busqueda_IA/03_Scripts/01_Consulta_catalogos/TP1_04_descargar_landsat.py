#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP1_04_descargar_landsat.py   ---> CUARTO script del TP1.

Descarga Landsat 9 (OLI-2, Collection 2 Level 2, reflectancia de superficie)
recortado a cada AOI, desde Microsoft Planetary Computer. Es la contraparte
optica de TP1_03_descargar_sentinel.py: alli Sentinel-2, aqui Landsat 9.

No hace falta cuenta ni contrasena: Planetary Computer entrega un token SAS
temporal y gratuito. Es la MISMA via que ya usa TP1_01_verificar_cobertura.py.

Que baja, por AOI y por epoca:
  - la o las escenas Landsat-9 con menos nube dentro de la ventana de fechas;
  - seis bandas de reflectancia (blue, green, red, nir08, swir16, swir22) y la
    banda de calidad qa_pixel, apiladas en un unico GeoTIFF multibanda;
  - a 30 m (resolucion nativa de Landsat), recortado al AOI en EPSG:32719.
    El remuestreo a 10 m se hace despues, en TP3_02_landsat9.py.

USO (entorno conda 'aoi'):
  python TP1_04_descargar_landsat.py                 (pre y post incendio 2025-26)
  python TP1_04_descargar_landsat.py --linea-base    (linea de base 2023-24)
  python TP1_04_descargar_landsat.py --todas         (todas las epocas opticas)

Cada archivo se guarda en:
  08_Originales_crudos/<epoca>/LANDSAT9/<AOI>/LC09_<AOI>_<fecha>.tif
Si se corta, volver a ejecutar: los archivos ya completos no se repiten.

SIGUIENTE PASO:  python TP1_05_descargar_gedi.py
"""
import os
import sys
import time

try:
    import requests
    from osgeo import gdal
except ImportError:
    sys.exit("Falta requests o GDAL. Active el entorno conda 'aoi'.")

AQUI = os.path.dirname(os.path.abspath(__file__))
PROYECTO = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, os.path.join(PROYECTO, "00_COMUN"))

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

from configuracion_comun import (          # noqa: E402
    AOIS_UTM, AOIS_WGS84, EPSG, DESCARGAS_ORIGINALES,
)

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
gdal.SetConfigOption("CPL_VSIL_CURL_USE_HEAD", "NO")

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token"
COLECCION = "landsat-c2-l2"
CUENTA = "landsateuwest"
CONTENEDOR = "landsat-c2"

# Bandas a apilar, EN ESTE ORDEN (reflectancia de superficie + calidad).
BANDAS = ["blue", "green", "red", "nir08", "swir16", "swir22", "qa_pixel"]
RES = 30                         # resolucion nativa de Landsat 9 (m)

# Ventanas de busqueda por epoca (alineadas con las fechas de Sentinel-2).
EPOCAS_OPTICAS = {
    "01_base":  "2023-10-01/2024-04-01",
    "02_pre": "2025-11-01/2026-01-10",
    "03_post":   "2026-02-27/2026-04-05",
}
MAX_POR_EPOCA = 2                # cuantas escenas (las de menos nube) por AOI


def token():
    return requests.get("%s/%s/%s" % (SAS, CUENTA, CONTENEDOR),
                        timeout=60).json()["token"]


def buscar(periodo, aoi):
    cuerpo = {
        "collections": [COLECCION],
        "bbox": list(AOIS_WGS84[aoi]),
        "datetime": periodo,
        "query": {"platform": {"eq": "landsat-9"}},
        "limit": 20,
    }
    r = requests.post(STAC, json=cuerpo, timeout=90)
    r.raise_for_status()
    feats = r.json().get("features", [])
    # de menos a mas nube
    feats.sort(key=lambda x: x["properties"].get("eo:cloud_cover", 100))
    return feats


def descargar_escena(item, aoi, tok, destino):
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    arrays, geo, proj = [], None, None
    for banda in BANDAS:
        if banda not in item["assets"]:
            print("      falta la banda %s, se omite la escena" % banda)
            return False
        href = item["assets"][banda]["href"]
        src = "/vsicurl/%s?%s" % (href, tok)
        remuestreo = "near" if banda == "qa_pixel" else "bilinear"
        ds = gdal.Warp("", src, format="MEM", dstSRS="EPSG:%d" % EPSG,
                       outputBounds=(xmin, ymin, xmax, ymax),
                       xRes=RES, yRes=RES, resampleAlg=remuestreo)
        arrays.append((banda, ds.GetRasterBand(1).ReadAsArray()))
        if geo is None:
            geo, proj = ds.GetGeoTransform(), ds.GetProjection()
    # escribir GeoTIFF multibanda
    alto, ancho = arrays[0][1].shape
    drv = gdal.GetDriverByName("GTiff")
    out = drv.Create(destino, ancho, alto, len(arrays),
                     gdal.GDT_UInt16, ["COMPRESS=DEFLATE", "TILED=YES"])
    out.SetGeoTransform(geo)
    out.SetProjection(proj)
    for i, (banda, arr) in enumerate(arrays, start=1):
        b = out.GetRasterBand(i)
        b.WriteArray(arr)
        b.SetDescription(banda)
    out.FlushCache()
    out = None
    return True


def main():
    if "--todas" in sys.argv:
        epocas = EPOCAS_OPTICAS
    elif "--linea-base" in sys.argv:
        epocas = {"01_base": EPOCAS_OPTICAS["01_base"]}
    else:
        epocas = {k: v for k, v in EPOCAS_OPTICAS.items()
                  if k.startswith(("02_", "03_"))}

    print(__doc__)
    tok = token()
    print("Token de Planetary Computer obtenido.\n")
    total = bajadas = 0
    for epoca, periodo in epocas.items():
        for aoi in AOIS_UTM:
            print("=" * 72)
            print("%s  |  %s  |  %s" % (epoca, aoi, periodo))
            print("=" * 72)
            try:
                items = buscar(periodo, aoi)
            except Exception as e:
                print("   error consultando el catalogo: %s" % str(e)[:70])
                continue
            if not items:
                print("   sin escenas Landsat-9 en el periodo")
                continue
            carpeta = os.path.join(DESCARGAS_ORIGINALES, epoca, "LANDSAT9", aoi)
            os.makedirs(carpeta, exist_ok=True)
            for it in items[:MAX_POR_EPOCA]:
                fecha = it["properties"]["datetime"][:10]
                nubes = it["properties"].get("eo:cloud_cover", -1)
                destino = os.path.join(carpeta, "LC09_%s_%s.tif" % (aoi, fecha))
                total += 1
                if os.path.exists(destino) and os.path.getsize(destino) > 0:
                    print("   %s  ya estaba (nube %2.0f%%)" % (fecha, nubes))
                    continue
                print("   %s  descargando (nube %2.0f%%) ..." % (fecha, nubes))
                t0 = time.time()
                try:
                    ok = descargar_escena(it, aoi, tok, destino)
                except Exception as e:
                    print("      fallo: %s" % str(e)[:70])
                    if os.path.exists(destino):
                        os.remove(destino)
                    continue
                if ok:
                    bajadas += 1
                    print("      guardado en %.0f s -> %s"
                          % (time.time() - t0, os.path.basename(destino)))

    print("\n" + "=" * 72)
    print("Listo. %d escenas nuevas descargadas (%d revisadas)." % (bajadas, total))
    print("SIGUIENTE PASO:  python TP1_05_descargar_gedi.py")


if __name__ == "__main__":
    main()
