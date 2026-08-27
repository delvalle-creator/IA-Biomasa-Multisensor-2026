#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_04_dem_y_pendiente.py   ---> CUARTO script del TP2.

QUE HACE
--------
Descarga el modelo digital de elevacion Copernicus GLO-30 y calcula, a partir de
el, la pendiente, la orientacion (aspecto) y el sombreado. Los guarda en la
carpeta COMUN del proyecto, porque son datos auxiliares que usan varios
practicos: el TP2 los necesita para filtrar disparos GEDI en pendiente fuerte, y
el TP4 los necesita para analizar el efecto del relieve sobre el radar.

Se ejecuta una sola vez. Si los archivos ya existen, no vuelve a hacer nada.

POR QUE HACE FALTA UN DEM EN UN PRACTICO DE LiDAR
-------------------------------------------------
GEDI mide la altura del dosel como la diferencia entre la primera energia que
vuelve (la copa) y la ultima (el suelo). En terreno inclinado eso se distorsiona:
dentro de una misma huella de 25 m, el suelo de un extremo esta mas alto que el
del otro. El retorno del suelo se "ensancha" y se confunde con el de la
vegetacion baja, de modo que la altura del dosel sale SOBRESTIMADA. Cuanto mayor
la pendiente, peor. Por eso, en el script siguiente, se descartan los disparos
que caen en pendientes fuertes.

DE DONDE SALE EL DEM
--------------------
Del catalogo abierto de Microsoft Planetary Computer (coleccion 'cop-dem-glo-30'),
que no pide credenciales. Es el mismo DEM que SNAP usa internamente para el
Terrain Flattening del TP4, de modo que todo el proyecto queda coherente: una
sola fuente de topografia.

El DEM se recorta a la grilla comun (EPSG:32719, 10 m). Ojo: su resolucion real
es de 30 m; llevarlo a 10 m solo sirve para que la grilla coincida con la de los
demas sensores, no agrega detalle.

SALIDA   00_COMUN/03_Topografia/DEM/dem_<AOI>.tif  y  dem_<AOI>_30m.tif
         00_COMUN/03_Topografia/pendiente/pendiente_<AOI>.tif     (grados)
         00_COMUN/03_Topografia/orientacion/orientacion_<AOI>.tif (grados)
         00_COMUN/03_Topografia/sombreado/sombreado_<AOI>.tif

USO (entorno conda 'aoi'):   python TP2_04_dem_y_pendiente.py
"""
import os
import sys

try:
    import requests
    from osgeo import gdal
except ImportError:
    sys.exit("Falta requests o GDAL. Active el entorno conda 'aoi'.")

AQUI = os.path.dirname(os.path.abspath(__file__))
PROYECTO = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
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

from configuracion_comun import AOIS_UTM, AOIS_WGS84, EPSG, PIXEL, TOPOGRAFIA

gdal.UseExceptions()
gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
gdal.SetConfigOption("CPL_VSIL_CURL_USE_HEAD", "NO")

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
# El endpoint por CUENTA/CONTENEDOR (.../token/dem/copernicus-dem) devuelve 404
# desde julio de 2026: la coleccion se mudo a la cuenta 'elevationeuwest'. El
# endpoint POR COLECCION es el estable, y es este.
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token/cop-dem-glo-30"

# Respaldo sin credenciales ni token: el espejo publico del Copernicus GLO-30 en
# AWS Open Data. Es EL MISMO dato. Se usa si Planetary Computer vuelve a cambiar,
# para que un servicio ajeno no deje al practico sin topografia.
AWS = ("https://copernicus-dem-30m.s3.amazonaws.com/"
       "Copernicus_DSM_COG_10_%s_00_%s_00_DEM/"
       "Copernicus_DSM_COG_10_%s_00_%s_00_DEM.tif")


def tiles_aws(aoi):
    """URL de los tiles de 1x1 grado que cubren el AOI, en el espejo de AWS.

    Los tiles se nombran por su esquina SUROESTE, de ahi el floor().
    """
    import math
    lonmin, latmin, lonmax, latmax = AOIS_WGS84[aoi]
    urls = []
    for la in range(int(math.floor(latmin)), int(math.floor(latmax)) + 1):
        for lo in range(int(math.floor(lonmin)), int(math.floor(lonmax)) + 1):
            ns = ("N%02d" % la) if la >= 0 else ("S%02d" % abs(la))
            ew = ("E%03d" % lo) if lo >= 0 else ("W%03d" % abs(lo))
            urls.append(AWS % (ns, ew, ns, ew))
    return urls


def obtener_token():
    """Token de lectura de Planetary Computer. None si no se puede."""
    try:
        d = requests.get(SAS, timeout=60).json()
        return d["token"]
    except Exception as e:
        print("Aviso: Planetary Computer no entrego token (%s)." % e)
        print("Se usara el espejo publico de AWS, que no lo necesita.\n")
        return None


def buscar_dem(aoi):
    """Devuelve las URL de los tiles del DEM que cubren el AOI."""
    cuerpo = {"collections": ["cop-dem-glo-30"],
              "bbox": list(AOIS_WGS84[aoi]), "limit": 10}
    try:
        r = requests.post(STAC, json=cuerpo, timeout=90)
        r.raise_for_status()
        items = r.json().get("features", [])
        return [it["assets"]["data"]["href"] for it in items]
    except Exception as e:
        print("   el catalogo STAC no respondio (%s); se usa el espejo de AWS" % e)
        return []


def generar(aoi, token):
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    d_dem = os.path.join(TOPOGRAFIA, "DEM")
    os.makedirs(d_dem, exist_ok=True)
    dem = os.path.join(d_dem, "dem_%s.tif" % aoi)

    if not os.path.exists(dem):
        # EL ESPEJO DE AWS VA PRIMERO, y no es una preferencia estetica.
        #
        # Planetary Computer entrega un token valido, y su catalogo encuentra el
        # tile correcto, pero al leer el blob GDAL recibe HTTP 403. En vez de
        # pelear con un servicio ajeno para conseguir un dato que ademas es
        # PUBLICO, se toma del espejo abierto de AWS: es el mismo Copernicus
        # GLO-30, no pide token de ninguna clase, y se verifico que GDAL lo lee
        # por red en esta misma instalacion.
        #
        # Planetary Computer queda de respaldo, por si algun dia AWS falla.
        urls = tiles_aws(aoi)
        token = None
        if urls:
            print("   espejo publico de AWS: %d tile(s), sin token" % len(urls))
        else:
            urls = buscar_dem(aoi)
            token = obtener_token()
            if urls:
                print("   Planetary Computer: %d tile(s)" % len(urls))
        if not urls:
            print("   no se hallaron tiles de DEM para este AOI")
            return
        print("   %d tile(s) de DEM; recortando a la grilla comun..." % len(urls))
        if token:
            fuentes = ["/vsicurl/%s?%s" % (u, token) for u in urls]
        else:
            fuentes = ["/vsicurl/%s" % u for u in urls]
        # Si hacen falta varios tiles, gdal.Warp los une (mosaico) y recorta.
        gdal.Warp(dem, fuentes, format="GTiff", dstSRS="EPSG:%d" % EPSG,
                  outputBounds=(xmin, ymin, xmax, ymax),
                  xRes=PIXEL, yRes=PIXEL, resampleAlg="bilinear",
                  creationOptions=["COMPRESS=DEFLATE", "TILED=YES"])
        print("   DEM -> %s" % os.path.basename(dem))

    # DEM en su resolucion NATIVA, que es sobre el que se derivan pendiente y
    # orientacion. Se conserva: es el insumo del calculo, no un intermedio.
    dem30 = os.path.join(d_dem, "dem_%s_30m.tif" % aoi)
    if not os.path.exists(dem30):
        gdal.Warp(dem30, fuentes, format="GTiff", dstSRS="EPSG:%d" % EPSG,
                  outputBounds=(xmin, ymin, xmax, ymax),
                  xRes=30, yRes=30, resampleAlg="bilinear",
                  creationOptions=["COMPRESS=DEFLATE", "TILED=YES"])
        print("   DEM nativo 30 m -> %s" % os.path.basename(dem30))
    else:
        print("   el DEM ya existe, se omite")

    # --- derivados: pendiente, orientacion y sombreado ---
    # Se calculan con gdal.DEMProcessing, que aplica el algoritmo de Horn.
    derivados = [
        ("pendiente", "slope", {"slopeFormat": "degree"},
         "inclinacion del terreno, en grados"),
        ("orientacion", "aspect", {},
         "hacia donde mira la ladera, en grados desde el norte"),
        ("sombreado", "hillshade", {"azimuth": 315, "altitude": 45},
         "sombreado para visualizacion"),
    ]
    for carpeta, alg, opciones, que_es in derivados:
        dsal = os.path.join(TOPOGRAFIA, carpeta)
        os.makedirs(dsal, exist_ok=True)
        sal = os.path.join(dsal, "%s_%s.tif" % (carpeta, aoi))
        if os.path.exists(sal):
            print("   %s ya existe" % carpeta)
            continue
        # SE DERIVA SOBRE EL DEM NATIVO DE 30 m Y RECIEN DESPUES SE REMUESTREA.
        #
        # El GLO-30 tiene 30 m de resolucion real. Si primero se lo lleva a 10 m
        # por interpolacion bilineal y despues se aplica Horn sobre una ventana
        # 3x3 —que abarca 20 m—, lo que se mide es la pendiente de una superficie
        # creada por la interpolacion, no la del terreno: sale sistematicamente
        # SUAVIZADA y SUBESTIMADA, sobre todo en filos y quiebres de ladera. Con
        # un umbral de descarte de 20 grados, eso significa descartar MENOS
        # huellas de las que corresponde, y justamente en ladera fuerte, que es
        # donde la huella de 25 m se estira sobre el desnivel y la altura del
        # dosel sale inflada.
        #
        # La pendiente es una derivada: se deriva primero y se remuestrea
        # despues, nunca al reves.
        #
        # computeEdges=True evita que el borde del raster quede en -9999, que en
        # el filtro pasaria como si fuera terreno llano.
        tmp = sal + ".30m.tif"
        gdal.DEMProcessing(tmp, dem30, alg, computeEdges=True,
                           creationOptions=["COMPRESS=DEFLATE", "TILED=YES"],
                           **opciones)
        # el sombreado es solo para mirar: puede ir directo a 10 m
        remuestreo = "near" if alg == "aspect" else "bilinear"
        gdal.Warp(sal, tmp, format="GTiff", dstSRS="EPSG:%d" % EPSG,
                  outputBounds=(xmin, ymin, xmax, ymax),
                  xRes=PIXEL, yRes=PIXEL, resampleAlg=remuestreo,
                  creationOptions=["COMPRESS=DEFLATE", "TILED=YES"])
        os.remove(tmp)
        print("   %-12s -> %s  (%s; derivado a 30 m, remuestreado a %d m)"
              % (carpeta, os.path.basename(sal), que_es, PIXEL))


print(__doc__)
token = obtener_token()
print("Fuente del DEM: %s\n" % ("Planetary Computer" if token
                                  else "espejo publico de AWS"))

for aoi in AOIS_UTM:
    print("=" * 72)
    print(aoi)
    print("=" * 72)
    generar(aoi, token)
    print()

# --- resumen de lo generado ---
import glob
print("Topografia disponible en 00_COMUN/03_Topografia/:")
for c in ("DEM", "pendiente", "orientacion", "sombreado"):
    n = len(glob.glob(os.path.join(TOPOGRAFIA, c, "*.tif")))
    print("   %-12s %d archivo(s)" % (c, n))
print()
print("Estos productos los usan TAMBIEN el TP4 (efecto del relieve sobre el")
print("radar) y el TP5 (variables auxiliares del modelo).")
print()
print("SIGUIENTE PASO:  python TP2_05_filtrar_pendiente.py")
