#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_04_palsar2_mosaico.py   ---> CUARTO script del TP4.
Recorta a la grilla comun el MOSAICO ANUAL global PALSAR-2 de JAXA (banda L,
25 m, HH+HV), ya orto-rectificado y con correccion radiometrica de terreno
(gamma cero, producto CEOS-ARD). Es una referencia adicional de banda L,
dual-pol, independiente de SAOCOM y de NISAR.

DISPONIBILIDAD (verificada en el sitio de JAXA, abril 2026): el mosaico anual
existe para 2015-2025. NO existe 2026 todavia (se publica con ~1 ano de
retraso), asi que este mosaico NO puede mostrar el incendio; sirve como
referencia del bosque en pie. Anos utiles aqui: 2023 (linea de base) y, si se
desea, 2025 (referencia anual pre-incendio).

POR QUE LA DESCARGA ES MANUAL
-----------------------------
JAXA distribuye el mosaico desde un sitio con registro gratuito y un mapa donde
se hace clic en el tile; no ofrece una API para automatizar. Es una descarga
unica y pequena (un tile de 1x1 grado cubre los DOS AOI). Pasos:

  1. Registrese (gratis, solo pide un email):
     https://www.eorc.jaxa.jp/ALOS/en/dataset/fnf_e.htm
     COMPROBADO EL 02/08/2026: la direccion anterior,
     .../ALOS/en/palsar_fnf/registration.htm, ya no existe; JAXA mudo el sitio
     y esa pagina solo devuelve un aviso de cambio de direccion. La de arriba es
     la vigente.
  2. Entre al sitio de descarga:
     https://www.eorc.jaxa.jp/ALOS/en/index_e.htm
  3. En el mapa, acerque a la Patagonia (lat -42.7, lon -71.3) y haga clic en el
     tile que va de latitud -43 a -42 y de longitud -72 a -71 (se llama
     'S42W072'). Elija el ano 2023 (y/o 2025). Descargue el tile.
  4. Descomprima el .zip/.tar.gz y copie la CARPETA del tile dentro de:
         04_descargas/01_base/PALSAR2_MOSAIC/2023/
     (para 2025:  04_descargas/02_pre/PALSAR2_MOSAIC/2025/)

Este script busca ahi los GeoTIFF de HH y HV, los convierte a gamma cero y los
recorta a la grilla comun de 10 m (vecino mas cercano: es radar, sus valores no
se interpolan). No necesita credenciales: solo lee archivos locales.

CONVERSION: el mosaico guarda numeros digitales (DN) de 16 bits. Se convierte a
gamma cero con la formula oficial de JAXA:
      gamma0 (dB)     = 10 * log10(DN^2) - 83.0
      gamma0 (lineal) = DN^2 * 10^(-8.3)
Se guarda gamma0 LINEAL (como los subsets de Sentinel-1 y NISAR) para poder
compararlos directamente.

USO (entorno conda 'aoi'):
   python TP4_04_palsar2_mosaico.py            procesa el ano 2023 (linea de base)
   python TP4_04_palsar2_mosaico.py 2025       procesa el ano 2025 (pre-incendio)
"""
import glob
import os
import sys

try:
    import numpy as np
    from osgeo import gdal, osr
except ImportError:
    sys.exit("Falta numpy o GDAL. Activar el entorno conda 'aoi'.")


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

from aoi_config import AOIS_UTM, DESCARGAS, PROCESADOS, EPSG, PIXEL, dir_procesado
import nombres

gdal.UseExceptions()

# ano y epoca a la que pertenece
ANO = sys.argv[1] if len(sys.argv) > 1 else "2023"
EPOCA = {"2023": "01_base",
         "2024": "01_base",
         "2025": "02_pre"}.get(ANO, "01_base")

CARPETA = os.path.join(DESCARGAS, EPOCA, "PALSAR2_MOSAIC", ANO)


def buscar(patrones):
    """Primer archivo que case alguno de los patrones (busqueda recursiva)."""
    for pat in patrones:
        hits = glob.glob(os.path.join(CARPETA, "**", pat), recursive=True)
        if hits:
            return hits[0]
    return None


def a_gamma0_lineal(ruta_dn):
    """Lee un tile de DN (uint16) y devuelve (gamma0 lineal float32, dataset)."""
    ds = gdal.Open(ruta_dn)
    dn = ds.GetRasterBand(1).ReadAsArray().astype("float64")
    val = dn > 0
    g0 = np.where(val, (dn ** 2) * (10.0 ** (-8.3)), 0.0).astype("float32")
    return g0, ds


def guardar_temporal_geo(arr, ref_ds, ruta):
    """Guarda un array en la geometria (lat/lon) del tile original, para warpear."""
    drv = gdal.GetDriverByName("GTiff")
    out = drv.Create(ruta, ref_ds.RasterXSize, ref_ds.RasterYSize, 1, gdal.GDT_Float32)
    out.SetGeoTransform(ref_ds.GetGeoTransform())
    out.SetProjection(ref_ds.GetProjection())
    out.GetRasterBand(1).WriteArray(arr)
    out.GetRasterBand(1).SetNoDataValue(0.0)
    out.FlushCache()
    return ruta


def recortar(aoi, capas_geo, angulo_geo):
    """Warpea cada capa a la grilla comun 10 m (vecino mas cercano) y escribe
    un unico GeoTIFF multibanda."""
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    outdir = dir_procesado("PALSAR2_MOSAIC", EPOCA, aoi)
    os.makedirs(outdir, exist_ok=True)
    corto = "PALSAR2_%s" % ANO
    final = os.path.join(outdir, corto + ".tif")
    if os.path.exists(final):
        print("     %s ya existe, se omite" % aoi)
        return

    bandas = list(capas_geo)
    if angulo_geo:
        bandas.append(("localIncidenceAngle", angulo_geo, "near"))

    warpeadas = []
    for nombre, ruta_geo, alg in bandas:
        w = gdal.Warp("", ruta_geo, format="MEM", dstSRS="EPSG:%d" % EPSG,
                      outputBounds=(xmin, ymin, xmax, ymax),
                      xRes=PIXEL, yRes=PIXEL, resampleAlg=alg,
                      srcNodata=0, dstNodata=0)
        warpeadas.append((nombre, w.GetRasterBand(1).ReadAsArray()))

    nx, ny = warpeadas[0][1].shape[1], warpeadas[0][1].shape[0]
    ds = gdal.GetDriverByName("GTiff").Create(
        final, nx, ny, len(warpeadas), gdal.GDT_Float32,
        options=["COMPRESS=DEFLATE", "TILED=YES"])
    ds.SetGeoTransform((xmin, PIXEL, 0, ymax, 0, -PIXEL))
    sr = osr.SpatialReference(); sr.ImportFromEPSG(EPSG)
    ds.SetProjection(sr.ExportToWkt())
    for i, (nombre, arr) in enumerate(warpeadas, 1):
        b = ds.GetRasterBand(i); b.WriteArray(arr); b.SetDescription(nombre)
        b.SetNoDataValue(0.0)
    ds.FlushCache(); ds = None

    hh = warpeadas[0][1]
    val = hh > 0
    print("     %s  %dx%d  valido=%.1f%%  g0HH mediana=%.2f dB"
          % (aoi, nx, ny, 100 * val.mean(),
             10 * np.log10(np.median(hh[val])) if val.any() else float("nan")))
    nombres.registrar(PROCESADOS, [corto, aoi, "PALSAR2_MOSAIC", ANO,
                                   "JAXA_global_mosaic_%s" % ANO, "tile S42W072"])


print(__doc__)
if not os.path.isdir(CARPETA):
    sys.exit("No existe la carpeta:\n   %s\n"
             "Descargue el tile S42W072 del ano %s (ver instrucciones arriba) y "
             "copielo alli." % (CARPETA, ANO))

hh = buscar(["*_HH_*.tif", "*_sl_HH*.tif", "*HH*.tif"])
hv = buscar(["*_HV_*.tif", "*_sl_HV*.tif", "*HV*.tif"])
ang = buscar(["*linci*.tif", "*_linci_*.tif"])
if not hh or not hv:
    sys.exit("No se encontraron los GeoTIFF de HH y HV dentro de:\n   %s\n"
             "Verifique que descomprimio el tile alli." % CARPETA)

print("Tile encontrado:")
print("   HH :", os.path.basename(hh))
print("   HV :", os.path.basename(hv))
print("   ang:", os.path.basename(ang) if ang else "(sin banda de angulo)")

# convertir DN -> gamma0 lineal y dejar en geometria original para warpear
tmp = os.path.join(CARPETA, "_tmp_geo")
os.makedirs(tmp, exist_ok=True)
g0hh, ref = a_gamma0_lineal(hh)
guardar_temporal_geo(g0hh, ref, os.path.join(tmp, "hh.tif"))
g0hv, _ = a_gamma0_lineal(hv)
guardar_temporal_geo(g0hv, ref, os.path.join(tmp, "hv.tif"))
capas = [("Gamma0_HH", os.path.join(tmp, "hh.tif"), "near"),
         ("Gamma0_HV", os.path.join(tmp, "hv.tif"), "near")]

print("\nRecortando a la grilla comun (EPSG:%d, %d m):" % (EPSG, PIXEL))
for aoi in AOIS_UTM:
    recortar(aoi, capas, ang)

# limpiar temporales
for f in glob.glob(os.path.join(tmp, "*.tif")):
    os.remove(f)
os.rmdir(tmp)

print("\nListo. Salida en 04_Tablas_de_trabajo/%s/<AOI>/PALSAR2_MOSAIC/PALSAR2_%s.tif"
      % (EPOCA, ANO))
print("Bandas Gamma0_HH y Gamma0_HV en gamma cero LINEAL (como Sentinel-1 y "
      "NISAR). Para dB: 10*log10(valor). Se abre en QGIS y en SNAP.")
