#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_01_descargar_gedi.py
Descarga GEDI L2A y L2B version V003 (sep-2024 a mar-2025) sobre los dos AOI,
como referencia estructural HISTORICA (no contemporanea a las escenas 2025/26).

USO:
  1. pip install earthaccess
  2. python TP2_01_descargar_gedi.py
  3. Ingresar usuario y contrasena de NASA Earthdata (urs.earthdata.nasa.gov)
     cuando lo pida.

DONDE QUEDAN LOS DATOS
  00_COMUN/08_Originales_crudos/02_pre/GEDI/<AOI>/<producto>/

  NO quedan dentro del practico: los productos originales son comunes a los
  cinco practicos y viven una sola vez en 00_COMUN. El nivel de EPOCA es
  obligatorio: TP1_09_inventario.py y los scripts del TP2 buscan los .h5 en
  <epoca>/GEDI/<AOI>/, y sin ese nivel no los encuentran.

Cada granulo pesa 0.5-3 GB; son ~19 granulos por producto (L2A y L2B).
"""
import os
import sys

try:
    import earthaccess
except ImportError:
    sys.exit("Falta el paquete 'earthaccess'. Ejecutar:  pip install earthaccess")


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

from aoi_config import AOIS_WGS84 as AOIS, DESCARGAS
PERIODO = ("2024-09-01", "2025-03-31")
# La EPOCA es parte de la ruta de destino: sin ella los .h5 caen sueltos en
# 08_Originales_crudos/GEDI/ y el inventario del TP1 y los scripts del TP2
# no los encuentran.
EPOCA = "02_pre"
PRODUCTOS = [("GEDI02_A", "003"), ("GEDI02_B", "003")]

# 'interactive' OBLIGA a pedir usuario y contrasena aunque ya esten guardadas.
# Sin strategy, earthaccess busca primero en las variables de entorno, luego en
# el archivo ~/.netrc (donde persist=True las guardo la primera vez) y solo
# pregunta si no encuentra nada. Asi el script se puede dejar corriendo solo.
auth = earthaccess.login(persist=True)
if not auth.authenticated:
    sys.exit("No se pudo autenticar en Earthdata.")

for aoi, bbox in AOIS.items():
    for short_name, version in PRODUCTOS:
        print(f"\n=== {aoi} | {short_name} v{version} ===")
        granulos = earthaccess.search_data(
            short_name=short_name, version=version,
            bounding_box=bbox, temporal=PERIODO)
        print(f"  {len(granulos)} granulos encontrados")
        carpeta = os.path.join(DESCARGAS, EPOCA, "GEDI", aoi, short_name)
        os.makedirs(carpeta, exist_ok=True)
        # limpiar restos de descargas interrumpidas
        import glob
        for p in glob.glob(os.path.join(carpeta, "partial_*")):
            os.remove(p)
        # threads=2: mas lento pero mucho mas estable con LP DAAC
        for intento in range(3):
            try:
                earthaccess.download(granulos, carpeta, threads=2)
                break
            except Exception as e:
                print(f"  interrupcion ({e}); reintento {intento+1}/3...")

print("\nListo. Los .h5 quedaron en:")
print("   " + os.path.join(DESCARGAS, EPOCA, "GEDI"))
print("Ejecutar despues TP2_02_recortar_AOI.py para extraer los disparos")
print("(shots) que caen dentro de cada AOI.")
