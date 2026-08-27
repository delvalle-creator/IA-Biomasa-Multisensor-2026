#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP1_01_verificar_cobertura.py   ---> PRIMER script del TP1.

QUE HACE
--------
Consulta los catalogos y, para cada producto hallado, compara DOS cosas:

   (a) lo que el catalogo DICE     -> la huella del producto
   (b) lo que el producto TIENE    -> los pixeles con dato dentro del AOI

Y muestra la diferencia. Ese contraste es la leccion central del practico.

POR QUE ESTE SCRIPT VA PRIMERO
------------------------------
Es tentador empezar descargando. No se hace. Primero se audita, porque una
descarga mal elegida cuesta horas y decenas de gigabytes, y el error no avisa:
el archivo baja bien, abre bien, se recorta bien... y esta vacio.

EL CONCEPTO: LA HUELLA NO ES EL DATO
------------------------------------
Un catalogo guarda, por cada escena, un poligono con su huella. Ese poligono
describe POR DONDE PASO EL SATELITE, no donde hay informacion utilizable:

  - Una franja de radar es un rectangulo inclinado inscripto en una grilla
    rectangular. Las esquinas de esa grilla estan VACIAS.
  - Una escena optica puede estar tapada de nubes.
  - Un producto puede haber sido reprocesado y renombrado.

Consultar por un rectangulo devuelve todo lo que lo TOCA, no lo que lo CUBRE.

CASO REAL DE ESTE PROYECTO
--------------------------
De 9 granulos NISAR hallados sobre los AOI, la huella del catalogo decia que 6
cubrian la estepa entre el 69% y el 76%. Al contar los pixeles con dato dentro
del AOI, la cobertura real era del 15%: el AOI caia en el borde de la franja.
Esos 6 granulos (12 GB) fueron descartados. Solo 3 servian.

QUE HACE ESTE SCRIPT, EN CONCRETO
---------------------------------
1. Consulta el catalogo abierto de Planetary Computer (sin credenciales) para
   Sentinel-2 y Landsat 9 sobre los dos AOI.
2. Para cada escena hallada calcula, SIN DESCARGARLA ENTERA, el porcentaje de
   pixeles con dato valido dentro del AOI. Lee solo la ventana del AOI de una
   banda, aprovechando que los productos estan en formato COG.
3. En el caso optico, ademas, recalcula la NUBOSIDAD REAL dentro del AOI con la
   banda de calidad, y la compara con la que informa el catalogo.
4. Escribe una tabla con las dos cifras, la declarada y la verificada.

SALIDA   05_Resultados/04_Tablas/verificacion_cobertura.csv

USO (entorno conda 'aoi'):   python TP1_01_verificar_cobertura.py
"""
import csv
import os
import sys

try:
    import numpy as np
    import requests
    from osgeo import gdal
except ImportError:
    sys.exit("Falta requests, numpy o GDAL. Active el entorno conda 'aoi'.")

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

from configuracion_comun import AOIS_UTM, AOIS_WGS84, EPSG, ruta_practico

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
gdal.SetConfigOption("CPL_VSIL_CURL_USE_HEAD", "NO")

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token"

# Que se consulta. Se eligen dos fechas de ejemplo, una por epoca.
CONSULTAS = [
    {"coleccion": "sentinel-2-l2a", "cuenta": "sentinel2l2a01", "contenedor": "sentinel2-l2",
     "banda": "B08", "calidad": "SCL", "periodo": "2026-01-01/2026-01-20",
     "etiqueta": "Sentinel-2 L2A (pre-incendio)"},
    {"coleccion": "landsat-c2-l2", "cuenta": "landsateuwest", "contenedor": "landsat-c2",
     "banda": "nir08", "calidad": "qa_pixel", "periodo": "2026-01-01/2026-01-20",
     "etiqueta": "Landsat 9 C2 L2 (pre-incendio)"},
]
# clases de la banda SCL de Sentinel-2 que NO son dato util
SCL_MALAS = (0, 1, 3, 8, 9, 10, 11)


def token(cuenta, contenedor):
    return requests.get("%s/%s/%s" % (SAS, cuenta, contenedor), timeout=60).json()["token"]


def buscar(coleccion, periodo, aoi):
    cuerpo = {"collections": [coleccion], "bbox": list(AOIS_WGS84[aoi]),
              "datetime": periodo, "limit": 5}
    r = requests.post(STAC, json=cuerpo, timeout=90)
    r.raise_for_status()
    return r.json().get("features", [])


def leer_ventana(href, tok, aoi):
    """Lee SOLO la ventana del AOI de un COG remoto. No descarga la escena."""
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    src = "/vsicurl/%s?%s" % (href, tok)
    ds = gdal.Warp("", src, format="MEM", dstSRS="EPSG:%d" % EPSG,
                   outputBounds=(xmin, ymin, xmax, ymax),
                   xRes=20, yRes=20, resampleAlg="near")   # 20 m: alcanza para contar
    return ds.GetRasterBand(1).ReadAsArray()


print(__doc__)
filas = []
for c in CONSULTAS:
    tok = token(c["cuenta"], c["contenedor"])
    for aoi in AOIS_UTM:
        print("=" * 72)
        print("%s  |  %s" % (c["etiqueta"], aoi))
        print("=" * 72)
        items = buscar(c["coleccion"], c["periodo"], aoi)
        if not items:
            print("   sin escenas en el periodo")
            continue
        for it in items[:2]:
            p = it["properties"]
            fecha = p["datetime"][:10]
            nubes_cat = p.get("eo:cloud_cover", -1)

            # --- (a) lo que DICE el catalogo: la huella cubre el AOI?
            from shapely.geometry import shape, box
            huella = shape(it["geometry"])
            caja = box(*AOIS_WGS84[aoi])
            cob_huella = 100.0 * huella.intersection(caja).area / caja.area

            # --- (b) lo que TIENE el dato: pixeles validos dentro del AOI
            try:
                a = leer_ventana(it["assets"][c["banda"]]["href"], tok, aoi)
            except Exception as e:
                print("   no se pudo leer la banda: %s" % str(e)[:60])
                continue
            con_dato = 100.0 * float((a > 0).mean())

            # --- nubosidad REAL dentro del AOI
            nubes_aoi = float("nan")
            try:
                q = leer_ventana(it["assets"][c["calidad"]]["href"], tok, aoi)
                if c["coleccion"].startswith("sentinel"):
                    nub = np.isin(q, SCL_MALAS)
                    val = ~nub & (q > 0)
                    nubes_aoi = 100.0 * nub.mean()
                else:
                    nub = ((q >> 3) & 1) | ((q >> 4) & 1)
                    v = q > 1
                    nubes_aoi = 100.0 * nub[v].mean() if v.any() else 100.0
            except Exception:
                pass

            print("   %s" % fecha)
            print("      (a) el catalogo DICE : huella cubre %5.1f%% del AOI | nubes escena %4.0f%%"
                  % (cob_huella, nubes_cat))
            print("      (b) el dato TIENE    : %5.1f%% de pixeles con valor  | nubes en AOI %4.1f%%"
                  % (con_dato, nubes_aoi))
            dif = abs(nubes_cat - nubes_aoi) if nubes_cat >= 0 and nubes_aoi == nubes_aoi else 0
            if dif > 10:
                print("      >>> la nubosidad del catalogo se aparta %.0f puntos de la real en el AOI"
                      % dif)
            filas.append([c["etiqueta"], aoi, fecha, "%.1f" % cob_huella,
                          "%.1f" % con_dato, "%.0f" % nubes_cat, "%.1f" % nubes_aoi])
        print()

sal_dir = ruta_practico("TP1", "05_Resultados", "04_Tablas")
os.makedirs(sal_dir, exist_ok=True)
sal = os.path.join(sal_dir, "verificacion_cobertura.csv")
with open(sal, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["producto", "aoi", "fecha", "cobertura_huella_catalogo_pct",
                "pixeles_con_dato_en_AOI_pct", "nubes_escena_catalogo_pct",
                "nubes_reales_en_AOI_pct"])
    w.writerows(filas)
print("Tabla -> 05_Resultados/04_Tablas/verificacion_cobertura.csv")
print()
print("LO QUE HAY QUE OBSERVAR:")
print("  1. La cobertura de la huella y el porcentaje de pixeles con dato NO")
print("     tienen por que coincidir. Cuando difieren, manda el segundo.")
print("  2. La nubosidad del catalogo es de la escena entera (110 x 110 km).")
print("     La del AOI (15 x 15 km) puede ser muy distinta, para bien o para mal.")
print()
print("SIGUIENTE PASO:  python TP1_03_descargar_sentinel.py")
print("(recien ahora, con la verificacion hecha, se descarga)")
