#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_04_diagnostico_dem.py   ---> auxiliar. Averigua por que falla la descarga
del modelo de elevacion, y si hay una fuente alternativa que si funcione.

No escribe ningun producto. Solo prueba y muestra.

USO:  python TP2_04_diagnostico_dem.py > salida_diag_dem.txt 2>&1
"""
import json
import sys

try:
    import requests
except ImportError:
    sys.exit("Falta requests.")

def prueba(nombre, fn):
    print("-" * 68)
    print(nombre)
    print("-" * 68)
    try:
        fn()
    except Exception as e:
        print("   ERROR: %s: %s" % (type(e).__name__, e))
    print()


def pc_sas():
    u = "https://planetarycomputer.microsoft.com/api/sas/v1/token/dem/copernicus-dem"
    r = requests.get(u, timeout=60)
    print("   HTTP %s" % r.status_code)
    print("   respuesta (primeros 400 caracteres):")
    print("   " + r.text[:400].replace("\n", "\n   "))


def pc_sas_coleccion():
    # forma alternativa: por identificador de coleccion, no por cuenta/contenedor
    u = "https://planetarycomputer.microsoft.com/api/sas/v1/token/cop-dem-glo-30"
    r = requests.get(u, timeout=60)
    print("   HTTP %s" % r.status_code)
    print("   " + r.text[:300].replace("\n", "\n   "))


def pc_stac():
    u = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
    cuerpo = {"collections": ["cop-dem-glo-30"],
              "bbox": [-71.60, -42.70, -71.40, -42.55], "limit": 5}
    r = requests.post(u, json=cuerpo, timeout=60)
    print("   HTTP %s" % r.status_code)
    try:
        d = r.json()
        its = d.get("features", [])
        print("   %d tile(s) encontrados" % len(its))
        for it in its[:3]:
            print("      id:", it.get("id"))
            for k, v in list(it.get("assets", {}).items())[:3]:
                print("        asset %-8s %s" % (k, str(v.get("href"))[:110]))
    except Exception as e:
        print("   no es JSON:", r.text[:200], e)


def aws_publico():
    # Espejo publico del Copernicus DEM 30 m. No pide credenciales ni token.
    base = ("https://copernicus-dem-30m.s3.amazonaws.com/"
            "Copernicus_DSM_COG_10_%s_00_%s_00_DEM/"
            "Copernicus_DSM_COG_10_%s_00_%s_00_DEM.tif")
    for lat, lon in (("S43", "W072"), ("S43", "W071")):
        u = base % (lat, lon, lat, lon)
        try:
            h = requests.head(u, timeout=60)
            print("   %s %s -> HTTP %s   tamano %s" %
                  (lat, lon, h.status_code, h.headers.get("Content-Length", "?")))
        except Exception as e:
            print("   %s %s -> ERROR %s" % (lat, lon, e))


def gdal_vsicurl():
    from osgeo import gdal
    gdal.UseExceptions()
    u = ("/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/"
         "Copernicus_DSM_COG_10_S43_00_W072_00_DEM/"
         "Copernicus_DSM_COG_10_S43_00_W072_00_DEM.tif")
    ds = gdal.Open(u)
    print("   GDAL abrio el tile por red: %d x %d pixeles" % (ds.RasterXSize, ds.RasterYSize))
    gt = ds.GetGeoTransform()
    print("   esquina: %.4f, %.4f   paso: %.6f grados" % (gt[0], gt[3], gt[1]))
    print("   -> /vsicurl FUNCIONA: se puede usar esta fuente sin token")


print(__doc__)
prueba("1. Planetary Computer, endpoint SAS que usa el script hoy", pc_sas)
prueba("2. Planetary Computer, endpoint SAS por coleccion", pc_sas_coleccion)
prueba("3. Planetary Computer, catalogo STAC (busqueda de tiles)", pc_stac)
prueba("4. Espejo publico de AWS, sin credenciales", aws_publico)
prueba("5. GDAL leyendo por red (/vsicurl) del espejo de AWS", gdal_vsicurl)
print("=" * 68)
print("Pasarle este archivo al asistente.")
