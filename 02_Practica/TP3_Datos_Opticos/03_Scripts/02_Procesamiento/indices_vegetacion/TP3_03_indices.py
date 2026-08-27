#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP3_03_indices.py   ---> TERCER script del TP3.

QUE HACE
--------
Calcula, para cada escena Sentinel-2 y para cada epoca, cuatro indices
espectrales. Los guarda en la grilla comun, listos para el modelo.

QUE ES UN INDICE ESPECTRAL Y POR QUE SE USA
-------------------------------------------
Una banda sola dice poco: su valor depende de la iluminacion, de la pendiente y
de la atmosfera. Un INDICE combina dos o mas bandas en un COCIENTE, y al dividir
se cancela buena parte de esos efectos. Por eso los indices son mas estables que
las bandas y son la base de casi todo el analisis optico.

LOS CUATRO INDICES Y QUE MIDE CADA UNO
--------------------------------------
  NDVI = (NIR - ROJO) / (NIR + ROJO)
     Es el mas conocido. La vegetacion viva ABSORBE el rojo (la clorofila lo usa
     para fotosintetizar) y REFLEJA muchisimo el infrarrojo cercano (la
     estructura interna de la hoja lo dispersa). Cuanto mas verde y densa la
     vegetacion, mas alto. Va de -1 a 1; el bosque sano ronda 0,8.

  EVI  = 2,5 * (NIR - ROJO) / (NIR + 6*ROJO - 7,5*AZUL + 1)
     Es un NDVI mejorado. Corrige el efecto del suelo de fondo y del aerosol
     (por eso usa el azul), y sobre todo SATURA MAS TARDE que el NDVI. En bosques
     densos, donde el NDVI ya no distingue nada, el EVI todavia responde.

  NDMI = (NIR - SWIR1) / (NIR + SWIR1)
     Indice de humedad. El infrarrojo de onda corta es absorbido por el AGUA de
     las hojas. Un dosel hidratado da NDMI alto; uno seco o estresado, bajo.
     Es util para separar bosque sano de bosque estresado, y para detectar el
     efecto del fuego.

  NBR  = (NIR - SWIR2) / (NIR + SWIR2)
     Indice de area quemada. Se explica en el script siguiente (TP3_04), donde
     se usa para cartografiar el incendio. Se calcula aqui para tenerlo junto a
     los demas.

LA LIMITACION QUE HAY QUE ENTENDER: LA SATURACION
-------------------------------------------------
Los indices opticos miden el DOSEL, no el tronco. Cuando el dosel se cierra por
completo, agregar mas biomasa debajo NO cambia lo que ve el satelite: el indice
se queda quieto. A eso se le llama SATURACION, y ocurre en el NDVI a partir de
unas 100-150 Mg/ha, que es poco para un bosque maduro.

Esa es la limitacion central del TP3, y la razon de ser del TP4: el radar de
banda L SI penetra el dosel y llega a los troncos. El script TP3_05 mide donde
satura cada indice con los datos de este proyecto.

ENTRADA   02_Subsets_SNAP_QGIS/Sentinel_2/<epoca>/<AOI>/*.tif
SALIDA    05_Resultados/02_Rasters/indices/<epoca>/<AOI>/indices_<fecha>.tif
          (4 bandas: NDVI, EVI, NDMI, NBR, en Float32)

USO (entorno conda 'aoi'):   python TP3_03_indices.py
"""
import glob
import os
import sys

try:
    import numpy as np
    from osgeo import gdal, osr
except ImportError:
    sys.exit("Falta numpy o GDAL. Active el entorno conda 'aoi'.")

AQUI = os.path.dirname(os.path.abspath(__file__))
TP3 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROYECTO = os.path.dirname(TP3)
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

from configuracion_comun import AOIS_UTM, EPSG, PIXEL

gdal.UseExceptions()

INSUMOS = os.path.join(TP3, "02_Subsets_SNAP_QGIS", "Sentinel_2")
RESULTADOS = os.path.join(TP3, "05_Resultados")

# numero de banda en el GeoTIFF de Sentinel-2 (ver el diccionario de datos)
B2_AZUL, B4_ROJO, B8_NIR, B11_SWIR1, B12_SWIR2, SCL = 1, 3, 7, 9, 10, 11
SCL_MALAS = (0, 1, 3, 8, 9, 10, 11)      # nube, sombra, nieve, saturado, sin dato


def indices(ds):
    """Devuelve los cuatro indices y la mascara de pixeles utiles."""
    def b(n):
        return ds.GetRasterBand(n).ReadAsArray().astype("float32")
    azul, rojo, nir = b(B2_AZUL), b(B4_ROJO), b(B8_NIR)
    swir1, swir2 = b(B11_SWIR1), b(B12_SWIR2)
    scl = ds.GetRasterBand(SCL).ReadAsArray().astype("int16")

    limpio = ~np.isin(scl, SCL_MALAS)
    con_dato = (nir > 0) & (rojo > 0)
    val = limpio & con_dato

    def cociente(a, b_):
        den = a + b_
        return np.where(val & (den != 0), (a - b_) / np.where(den == 0, 1, den), np.nan)

    ndvi = cociente(nir, rojo)
    ndmi = cociente(nir, swir1)
    nbr = cociente(nir, swir2)
    # EVI: los coeficientes son los estandar de la mision MODIS, de uso general
    den = nir + 6.0 * rojo - 7.5 * azul + 1.0
    evi = np.where(val & (den != 0), 2.5 * (nir - rojo) / np.where(den == 0, 1, den), np.nan)
    evi = np.clip(evi, -1, 1)            # el EVI puede dispararse con pixeles raros
    return {"NDVI": ndvi.astype("float32"), "EVI": evi.astype("float32"),
            "NDMI": ndmi.astype("float32"), "NBR": nbr.astype("float32")}, val


def escribir(ruta, capas, aoi):
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    ny, nx = capas[0][1].shape
    ds = gdal.GetDriverByName("GTiff").Create(
        ruta, nx, ny, len(capas), gdal.GDT_Float32,
        options=["COMPRESS=DEFLATE", "TILED=YES"])
    ds.SetGeoTransform((xmin, PIXEL, 0, ymax, 0, -PIXEL))
    sr = osr.SpatialReference(); sr.ImportFromEPSG(EPSG)
    ds.SetProjection(sr.ExportToWkt())
    for i, (nom, arr) in enumerate(capas, 1):
        b_ = ds.GetRasterBand(i); b_.WriteArray(arr); b_.SetDescription(nom)
        b_.SetNoDataValue(float("nan"))
    ds.FlushCache(); ds = None


def mediana(a):
    v = a[np.isfinite(a)]
    return float(np.median(v)) if v.size else float("nan")


print(__doc__)
n_ok = 0
for epoca in sorted(os.listdir(INSUMOS)):
    for aoi in AOIS_UTM:
        patron = os.path.join(INSUMOS, epoca, aoi, "*.tif")
        for f in sorted(glob.glob(patron)):
            base = os.path.basename(f)
            fecha = next((t for t in base.split("_") if len(t) == 8 and t.isdigit()), "?")
            print("=" * 72)
            print("%s | %s | %s" % (epoca[:2], aoi[:6], fecha))
            ds = gdal.Open(f)
            if ds.RasterCount < SCL:
                print("   no tiene banda SCL, se omite")
                continue
            ix, val = indices(ds)
            outdir = os.path.join(RESULTADOS, "02_Rasters", "indices", epoca, aoi)
            os.makedirs(outdir, exist_ok=True)
            sal = os.path.join(outdir, "indices_%s.tif" % fecha)
            escribir(sal, list(ix.items()), aoi)
            n_ok += 1
            print("   pixeles utiles: %5.1f%%" % (100.0 * val.mean()))
            for k in ("NDVI", "EVI", "NDMI", "NBR"):
                print("   %-5s mediana %6.3f" % (k, mediana(ix[k])))

print()
print("Listo. %d escenas procesadas." % n_ok)
print("Salida: 05_Resultados/02_Rasters/indices/<epoca>/<AOI>/indices_<fecha>.tif")
print()
print("QUE OBSERVAR:")
print("  - En el bosque, el NDVI pre-incendio ronda 0,8 y el post cae a ~0,3.")
print("  - En la estepa, el NDVI se mantiene bajo (~0,2) en todas las epocas.")
print("  - El NDMI cae con el fuego: el dosel pierde agua.")
print()
print("SIGUIENTE PASO:  python TP3_04_dnbr_incendio.py")
