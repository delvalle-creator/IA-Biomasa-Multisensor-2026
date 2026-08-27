# -*- coding: utf-8 -*-
"""
comprobar_entorno.py   ---> se corre ANTES que cualquier otro script.

POR QUE EXISTE
--------------
El 31/07/2026 la cadena completa se corto en el paso 3 de 10 porque al entorno
'aoi' le faltaba rasterio. Los dos primeros pasos ya habian reescrito sus
salidas, asi que el proyecto quedo a medio actualizar. Un fallo asi no se puede
descubrir a mitad de camino: hay que descubrirlo antes de tocar nada.

Este script no lee ni escribe datos. Solo intenta importar cada paquete que la
cadena necesita y, si falta alguno, imprime la linea exacta que hay que ejecutar
para instalarlo y devuelve un codigo de error para que el .bat se detenga.

USO (entorno conda 'aoi'):   python comprobar_entorno.py
"""
import sys

# (modulo que se importa, paquete de conda-forge, para que se usa)
NECESARIOS = [
    ("numpy",        "numpy",         "calculo numerico; casi todos los scripts"),
    ("rasterio",     "rasterio",      "lectura de GeoTIFF; TP4_11 y TP5_01 a TP5_05"),
    ("sklearn",      "scikit-learn",  "regresion y metricas; TP5_02 y TP5_06"),
    ("scipy",        "scipy",         "filtro de moteado por ventana movil; TP4_06"),
    ("pandas",       "pandas",        "tablas de la validacion estricta; TP5_06"),
    ("shapely",      "shapely",       "cruce de huellas con la cobertura; TP2_09"),
    ("shapefile",    "pyshp",         "lectura de los shapefiles BAP; TP2_09"),
    ("osgeo",        "gdal",          "exportacion a GeoPackage; TP2_08"),
    ("pyproj",       "pyproj",        "reproyeccion a EPSG:32719"),
    ("h5py",         "h5py",          "lectura de los granulos GEDI .h5"),
    ("requests",     "requests",      "descargas por HTTP; TP1_01, TP1_03, TP1_04, TP1_07, TP1_08"),
    ("earthaccess",  "earthaccess",   "acceso a NASA Earthdata; TP1_05, TP1_06, TP2_01"),
    ("pystac_client","pystac-client", "consulta del catalogo STAC de BIOMASS; TP1_08"),
]

print("Python %s" % sys.version.split()[0])
print("Interprete: %s" % sys.executable)
print()

faltan = []
for modulo, paquete, para_que in NECESARIOS:
    try:
        __import__(modulo)
        estado = "ok"
    except ImportError:
        estado = "FALTA"
        faltan.append(paquete)
    print("   %-6s %-14s %s" % (estado, modulo, para_que))

print()
if faltan:
    print("=" * 70)
    print("FALTAN %d PAQUETE(S). No se ejecuto ningun paso de la cadena." % len(faltan))
    print("=" * 70)
    print()
    print("Copie y pegue esta linea en el Miniforge Prompt:")
    print()
    print("   conda install -c conda-forge %s" % " ".join(faltan))
    print()
    print("Cuando termine, vuelva a hacer doble clic en EJECUTAR_cadena_escenarioB.bat")
    sys.exit(1)

print("El entorno esta completo. Se puede correr la cadena.")
sys.exit(0)
