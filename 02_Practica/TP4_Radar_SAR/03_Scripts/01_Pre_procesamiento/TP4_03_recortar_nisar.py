#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_03_recortar_nisar.py   ---> TERCER script del TP4.
Recorta los productos NISAR GCOV a la grilla comun de 15 x 15 km
(EPSG:32719, 10 m, 1500 x 1500 pixeles), igual que el resto de los sensores.

POR QUE ESTE SCRIPT Y NO SNAP
-----------------------------
SNAP todavia no trae un lector de NISAR. Pero para GCOV eso NO es un problema,
porque GCOV ya viene resuelto:

  - Ya esta GEOCODIFICADO: no hay que hacer Terrain Correction.
  - Ya tiene aplicada la CORRECCION RADIOMETRICA DE TERRENO (RTC): los valores
    son gamma0, no beta0 ni sigma0. El Terrain Flattening que en Sentinel-1
    hacemos nosotros, en GCOV ya viene hecho por la NASA.
  - Y en esta zona viene en EPSG:32719, la misma proyeccion de nuestra grilla.

GCOV no es un producto crudo: es un raster de gamma0 listo, guardado dentro de
un HDF5. Lo unico que falta es sacarlo del HDF5 con la georreferencia puesta,
porque el driver HDF5 de GDAL lee los numeros pero NO las coordenadas: NISAR
las guarda en arreglos aparte (xCoordinates / yCoordinates), no en un
geotransform. Eso es lo que hace este script, con h5py y GDAL.

DOS COMPROBACIONES QUE ESTE SCRIPT HACE Y QUE SON IMPRESCINDIBLES
-----------------------------------------------------------------
1. DATO VALIDO, no huella. Que la grilla del producto CONTENGA al AOI no
   significa que tenga dato ahi: la grilla es un rectangulo que envuelve una
   franja inclinada, y las esquinas quedan vacias. Los seis granulos del track
   075 contienen el AOI de estepa pero solo un 15% de sus pixeles tiene dato
   real: el AOI cae en el borde de la franja. Por eso aqui se cuenta el
   porcentaje de pixeles VALIDOS dentro del AOI y se descarta lo que no llegue
   al umbral. Sin esta comprobacion se generan subsets casi vacios.

2. ALINEACION. Se verifica que los bordes de los pixeles del producto caigan
   sobre los de la grilla comun. Si caen (es el caso de los granulos utiles,
   que vienen a 10 m), el recorte es una simple lectura de ventana y NO se
   remuestrea nada: el dato llega intacto. Si no caen, se remuestrea por vecino
   mas cercano y se avisa.

Bandas de salida: Gamma0_HH, Gamma0_HV (gamma0 lineal, como los subsets S1),
mas 'mask' (mascara de calidad del producto) y 'numberOfLooks'.

OJO: NISAR sobre esta zona adquiere en DUAL-POL HH/HV. No hay terminos cruzados
(HHHV, HHVV...), asi que GCOV NO sirve para polarimetria completa: para eso hay
que usar el ALOS-1 quad-pol.

USO (entorno conda 'aoi'):   python TP4_03_recortar_nisar.py
"""
import glob
import os
import struct
import sys

try:
    import h5py
    import numpy as np
    from osgeo import gdal, osr
except ImportError:
    sys.exit("Falta h5py, numpy o GDAL. Activar el entorno conda 'aoi'.")


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

RUTA = "science/LSAR/GCOV/grids/frequencyA"
BANDAS = [("HHHH", "Gamma0_HH"), ("HVHV", "Gamma0_HV"),
          ("numberOfLooks", "numberOfLooks"), ("mask", "mask")]
EPOCA = "02_pre"
MIN_VALIDO = 0.90          # fraccion minima de pixeles con dato dentro del AOI
NPIX = 1500


def h5_completo(ruta):
    """El superbloque HDF5 declara donde termina el archivo."""
    try:
        d = open(ruta, "rb").read(64)
        if d[:8] != b"\x89HDF\r\n\x1a\n":
            return False
        ver = d[8]
        eof = struct.unpack("<Q", d[40:48] if ver in (0, 1) else d[28:36])[0]
        return os.path.getsize(ruta) >= eof > 0
    except Exception:
        return False


def fecha_de(nombre):
    for t in nombre.split("_"):
        if len(t) == 15 and t[8:9] == "T" and t[:8].isdigit():
            return t[:8]
    return "00000000"


def track_de(nombre):
    p = nombre.split("_")
    return p[5] + p[6] if len(p) > 6 else "?"


def escribir(ruta, capas, x0, y0, paso):
    """GeoTIFF georreferenciado. 'capas' = lista de (nombre, array)."""
    ny, nx = capas[0][1].shape
    tipos = {np.dtype("float32"): gdal.GDT_Float32,
             np.dtype("uint8"): gdal.GDT_Byte,
             np.dtype("uint16"): gdal.GDT_UInt16}
    ds = gdal.GetDriverByName("GTiff").Create(
        ruta, nx, ny, len(capas), tipos.get(capas[0][1].dtype, gdal.GDT_Float32),
        options=["COMPRESS=DEFLATE", "TILED=YES"])
    ds.SetGeoTransform((x0, paso, 0, y0, 0, -paso))
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(EPSG)
    ds.SetProjection(sr.ExportToWkt())
    for i, (nom, a) in enumerate(capas, 1):
        b = ds.GetRasterBand(i)
        b.WriteArray(a)
        b.SetDescription(nom)
        if a.dtype == np.float32:
            b.SetNoDataValue(0.0)
    ds.FlushCache()
    ds = None


def procesar(h5path, aoi):
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    base = os.path.basename(h5path)
    fecha = fecha_de(base)
    corto = "NISAR_GCOV_%s" % fecha

    with h5py.File(h5path, "r") as h:
        g = h[RUTA]
        epsg_prod = int(g["projection"].attrs["epsg_code"])
        if epsg_prod != EPSG:
            print("     OMITIDO: el producto esta en EPSG:%d" % epsg_prod)
            return False
        x, y = g["xCoordinates"][:], g["yCoordinates"][:]
        paso = abs(float(x[1] - x[0]))
        # x, y son CENTROS de pixel: el borde esta a medio pixel de distancia
        bx, by = x[0] - paso / 2.0, y[0] + paso / 2.0

        i0f, j0f = (xmin - bx) / paso, (by - ymax) / paso
        i0, i1 = int(round(i0f)), int(round((xmax - bx) / paso))
        j0, j1 = int(round(j0f)), int(round((by - ymin) / paso))
        if i0 < 0 or j0 < 0 or i1 > len(x) or j1 > len(y):
            print("     OMITIDO: el AOI cae fuera de la grilla del producto")
            return False

        alineado = abs(i0f - i0) < 1e-6 and abs(j0f - j0) < 1e-6 \
            and abs(paso - PIXEL) < 1e-6

        # --- comprobacion de DATO VALIDO (no de huella) --------------------
        hh = g["HHHH"][j0:j1, i0:i1].astype(np.float32)
        valido = np.isfinite(hh) & (hh > 0)
        frac = float(valido.mean())
        if frac < MIN_VALIDO:
            print("     DESCARTADO: solo %.1f%% de pixeles con dato dentro del "
                  "AOI (el AOI cae en el borde de la franja)" % (100 * frac))
            return False

        capas = [("Gamma0_HH", hh)]
        for clave, nom in BANDAS[1:]:
            if clave not in g:
                continue
            a = g[clave][j0:j1, i0:i1]
            capas.append((nom, a if a.dtype == np.uint8 else a.astype(np.float32)))

    outdir = dir_procesado("NISAR_GCOV", EPOCA, aoi)
    os.makedirs(outdir, exist_ok=True)
    final = os.path.join(outdir, corto + ".tif")
    if os.path.exists(final):
        print("     ya existe, se omite")
        return True

    flotantes = [c for c in capas if c[1].dtype == np.float32]
    enteras = [c for c in capas if c[1].dtype == np.uint8]

    if alineado:
        # Paso 10 m y bordes coincidentes: recorte exacto, SIN remuestrear.
        escribir(final, flotantes, xmin, ymax, paso)
        if enteras:
            escribir(final.replace(".tif", "_mask.tif"), enteras, xmin, ymax, paso)
        nota = "recorte exacto, sin remuestreo"
    else:
        # Grilla distinta: se escribe en resolucion nativa y se remuestrea por
        # VECINO MAS CERCANO (no se interpola gamma0 ni la mascara).
        nativo = final.replace(".tif", "_nativo%dm.tif" % int(paso))
        escribir(nativo, flotantes, xmin, ymax, paso)
        gdal.Warp(final, nativo, format="GTiff", dstSRS="EPSG:%d" % EPSG,
                  outputBounds=(xmin, ymin, xmax, ymax),
                  xRes=PIXEL, yRes=PIXEL, resampleAlg="near",
                  creationOptions=["COMPRESS=DEFLATE", "TILED=YES"])
        nota = "remuestreado de %d m a %d m (vecino mas cercano)" % (paso, PIXEL)

    d = gdal.Open(final)
    nombres.registrar(PROCESADOS, [corto, aoi, "NISAR_GCOV", fecha,
                                   base.replace(".h5", ""), base])
    print("     OK  %dx%d px  %.1f%% con dato  (%s)"
          % (d.RasterXSize, d.RasterYSize, 100 * frac, nota))
    return True


print(__doc__)
carpeta = os.path.join(DESCARGAS, EPOCA, "NISAR", "GCOV")
archivos = sorted(glob.glob(os.path.join(carpeta, "*.h5")))
if not archivos:
    sys.exit("No hay .h5 en %s\nEjecutar antes:  python 12_descargar_nisar_directo.py"
             % carpeta)

hechos, descartados, rotos = 0, 0, 0
for aoi in AOIS_UTM:
    print("\n" + "=" * 72)
    print("%s" % aoi)
    print("=" * 72)
    for f in archivos:
        b = os.path.basename(f)
        print("  %s  track %s" % (fecha_de(b), track_de(b)))
        if not h5_completo(f):
            print("     ARCHIVO TRUNCADO: volver a descargarlo (script 12)")
            rotos += 1
            continue
        if procesar(f, aoi):
            hechos += 1
        else:
            descartados += 1

print("\n" + "=" * 72)
print("%d subsets generados | %d descartados | %d archivos truncados"
      % (hechos, descartados, rotos))
print("Salida: 04_Tablas_de_trabajo/%s/<AOI>/NISAR_GCOV/*.tif" % EPOCA)
print("Se abren en QGIS y en SNAP (File > Open Product).")
