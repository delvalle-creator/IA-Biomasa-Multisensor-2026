#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_06_speckle.py   ---> SEXTO script del TP4.

QUE HACE
--------
Mide cuanto ruido de speckle tiene cada producto y aplica un filtro. Es el paso
que hay que dar ANTES de cualquier analisis cuantitativo con radar.

QUE ES EL SPECKLE Y POR QUE NO ES RUIDO COMUN
---------------------------------------------
Una imagen de radar granulada no esta mal tomada. El speckle es una consecuencia
inevitable de iluminar con una onda COHERENTE: dentro de un pixel de 10 m hay
miles de dispersores (hojas, ramas, piedras) y cada uno devuelve una onda con su
fase. Esas ondas se suman entre si, y la suma puede reforzarse o cancelarse segun
las fases coincidan o no. El resultado es que dos pixeles del MISMO bosque, con
la MISMA biomasa, pueden diferir varios decibeles solo por como cayeron las fases.

Esto lo distingue del ruido de un sensor optico: no se reduce mejorando el
instrumento, porque no es un defecto del instrumento. Es fisica de la onda.

Consecuencia practica: un pixel suelto de radar NO es una medida confiable. Hay
que promediar. Promediar suma intensidades y las fases se descorrelacionan entre
pixeles vecinos, de modo que el promedio converge al valor verdadero.

CUANTO IMPORTA: EL EXPERIMENTO DE ESTE SCRIPT
---------------------------------------------
El script mide el R2 del ajuste gamma0 -> altura del dosel (GEDI) con ventanas de
distinto tamano. El resultado obtenido con los datos de este proyecto:

   fuente                 3x3     5x5     9x9   15x15   21x21   31x31
   S1 VH   (banda C)    0,011   0,018   0,023   0,026   0,028   0,025
   NISAR HV (banda L)   0,152   0,200   0,229   0,245   0,237   0,221
   PALSAR-2 HV (band L) 0,104   0,122   0,143   0,153   0,159   0,159

Lease asi. Con la ventana de 3x3, que es la que corresponde al tamano de la
huella GEDI, la banda L explica un 15% de la altura. Promediando a 15x15 (150 m)
sube a 24,5%: el promediado recupero casi diez puntos que el speckle se estaba
comiendo. A partir de ahi vuelve a bajar, porque la ventana empieza a promediar
bosque que ya no esta en la huella.

Ese maximo es un compromiso, y conviene entenderlo: ventana chica = mucho
speckle; ventana grande = se mezcla con lo que hay alrededor. El optimo aqui esta
alrededor de los 150 m.

Fijese tambien en la fila de la banda C: por mas que se filtre, no pasa de 0,03.
El speckle no era el problema de la banda C. Su problema es otro, y lo va a ver
en el script siguiente.

EL FILTRO QUE SE APLICA
-----------------------
Se usa el filtro de Lee refinado, que es el estandar de la disciplina. A
diferencia de un promedio liso, el filtro de Lee promedia MENOS donde detecta un
borde, de modo que suaviza el interior de las manchas homogeneas sin desdibujar
los limites entre ellas. Lee et al. (2009) lo describen en detalle.

IMPORTANTE: SE FILTRA EN LINEAL, NO EN DECIBELES
------------------------------------------------
Los decibeles son una escala logaritmica. El promedio de los logaritmos NO es el
logaritmo del promedio: filtrar en dB introduce un sesgo negativo sistematico,
que ademas crece con la varianza del speckle. El script filtra en gamma0 lineal y
recien despues pasa a dB, que es como debe hacerse.

ENTRADA   02_Subsets_SNAP_QGIS/<sensor>/<epoca>/<AOI>/*/*.tif   (gamma0 LINEAL)
SALIDA    05_Resultados/04_Tablas/enl_por_producto.csv   (calidad de cada producto)
          05_Resultados/04_Tablas/r2_vs_ventana.csv      (el experimento de arriba)
          05_Resultados/02_Rasters/filtrados/<sensor>_<fecha>_<AOI>_lee.tif

USO (entorno conda 'aoi'):   python TP4_06_speckle.py
"""
import csv
import glob
import os
import sys

try:
    import numpy as np
    from osgeo import gdal, osr
except ImportError:
    sys.exit("Falta numpy o GDAL. Active el entorno conda 'aoi'.")

AQUI = os.path.dirname(os.path.abspath(__file__))
TP4 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROYECTO = os.path.dirname(TP4)
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
INSUMOS = os.path.join(TP4, "02_Subsets_SNAP_QGIS")
RESULTADOS = os.path.join(TP4, "05_Resultados")
GEDI = os.path.join(PROYECTO, "TP2_LiDAR_GEDI_ICESat2", "05_Resultados", "04_Tablas")
VENTANAS = (1, 2, 4, 7, 10, 15)          # radios: 3x3, 5x5, 9x9, 15x15, 21x21, 31x31
LEE_RADIO = 3                            # ventana 7x7 para el filtro de Lee


def productos(aoi):
    """Devuelve [(etiqueta, banda_pol, ruta, n_banda), ...] de este AOI."""
    P = []
    for f in sorted(glob.glob(os.path.join(INSUMOS, "Sentinel_1", "*", aoi, "S1_GRD", "*.tif"))):
        fecha = os.path.basename(f).split("_")[3]
        P += [("S1_GRD_%s" % fecha, "C_VH", f, 1), ("S1_GRD_%s" % fecha, "C_VV", f, 2)]
    for f in sorted(glob.glob(os.path.join(INSUMOS, "SAOCOM", "*", aoi, "*", "*.tif"))):
        fecha = os.path.basename(f).split("_")[2]
        P += [("SAOCOM_%s" % fecha, "L_HH", f, 1), ("SAOCOM_%s" % fecha, "L_HV", f, 2)]
    for f in sorted(glob.glob(os.path.join(INSUMOS, "NISAR", "*", aoi, "*", "*.tif"))):
        if "_mask" in f:
            continue
        fecha = os.path.basename(f).replace(".tif", "").split("_")[-1]
        P += [("NISAR_%s" % fecha, "L_HH", f, 1), ("NISAR_%s" % fecha, "L_HV", f, 2)]
    for f in sorted(glob.glob(os.path.join(INSUMOS, "ALOS_PALSAR_2", "*", aoi, "*", "*.tif"))):
        anio = os.path.basename(f).replace(".tif", "").split("_")[-1]
        P += [("PALSAR2_%s" % anio, "L_HH", f, 1), ("PALSAR2_%s" % anio, "L_HV", f, 2)]
    return P


def enl(a):
    """Numero equivalente de looks: (media/desvio)^2 sobre gamma0 LINEAL.

    Mide cuanto speckle queda. Cuanto MAS alto, menos ruido. Un producto de un
    solo look da ENL ~ 1. El GRD de Sentinel-1, que ya viene multi-look, ronda 4
    o 5. Es la forma estandar de comparar la calidad radiometrica de productos de
    origen distinto."""
    v = a[np.isfinite(a) & (a > 0)]
    if v.size < 100:
        return float("nan")
    m, s = float(v.mean()), float(v.std())
    return (m / s) ** 2 if s else float("nan")


def lee_refinado(a, radio=LEE_RADIO):
    """Filtro de Lee. Promedia menos donde la varianza local es alta (bordes)."""
    from scipy.ndimage import uniform_filter
    a = np.where(np.isfinite(a) & (a > 0), a, np.nan)
    k = 2 * radio + 1
    relleno = np.where(np.isnan(a), np.nanmean(a), a)
    media = uniform_filter(relleno, k)
    media2 = uniform_filter(relleno ** 2, k)
    var = np.maximum(media2 - media ** 2, 0)
    cu2 = 1.0 / enl(a) if enl(a) == enl(a) else 0.25      # varianza del speckle
    ci2 = np.divide(var, media ** 2, out=np.zeros_like(var), where=media > 0)
    w = np.clip(1 - cu2 / np.maximum(ci2, 1e-9), 0, 1)    # 0 = liso, 1 = borde
    return np.where(np.isnan(a), np.nan, media + w * (relleno - media))


def cargar_gedi(aoi):
    p = os.path.join(GEDI, "GEDI_L2A_%s_aceptados.csv" % aoi)
    if not os.path.exists(p):
        return []
    out = []
    for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
        try:
            out.append((float(r["este_utm19s"]), float(r["norte_utm19s"]), float(r["rh95"])))
        except (KeyError, ValueError):
            continue
    return out


def r2_contra_gedi(ruta, banda, huellas, radio):
    ds = gdal.Open(ruta)
    gt = ds.GetGeoTransform()
    a = ds.GetRasterBand(banda).ReadAsArray().astype("float64")
    # Se queda en gamma0 LINEAL. El paso a dB va DESPUES de promediar la
    # ventana: el promedio de los logaritmos no es el logaritmo del promedio,
    # y ese sesgo negativo CRECE con la heterogeneidad de la ventana, que es
    # justo lo que este script esta midiendo. Promediar en dB comprimiria la
    # senal buscada, y el sesgo (~0,5 dB) es del orden del efecto medido.
    a = np.where(np.isfinite(a) & (a > 0), a, np.nan)
    ny, nx = a.shape
    X, Y = [], []
    for e, n, h in huellas:
        c = int((e - gt[0]) / gt[1]); f = int((n - gt[3]) / gt[5])
        if not (radio <= c < nx - radio and radio <= f < ny - radio):
            continue
        w = a[f - radio:f + radio + 1, c - radio:c + radio + 1]
        w = w[np.isfinite(w)]
        if w.size:
            X.append(h); Y.append(float(10 * np.log10(w.mean())))
    if len(X) < 30:
        return float("nan"), 0
    X, Y = np.array(X), np.array(Y)
    p, q = np.polyfit(Y, X, 1); pred = p * Y + q
    return 1 - ((X - pred) ** 2).sum() / ((X - X.mean()) ** 2).sum(), len(X)


def escribir(ruta, capas, aoi):
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    ny, nx = capas[0][1].shape
    ds = gdal.GetDriverByName("GTiff").Create(ruta, nx, ny, len(capas), gdal.GDT_Float32,
                                              options=["COMPRESS=DEFLATE", "TILED=YES"])
    ds.SetGeoTransform((xmin, PIXEL, 0, ymax, 0, -PIXEL))
    sr = osr.SpatialReference(); sr.ImportFromEPSG(EPSG); ds.SetProjection(sr.ExportToWkt())
    for i, (nom, arr) in enumerate(capas, 1):
        b = ds.GetRasterBand(i); b.WriteArray(arr.astype("float32")); b.SetDescription(nom)
        b.SetNoDataValue(float("nan"))
    ds.FlushCache(); ds = None


print(__doc__)
os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)
os.makedirs(os.path.join(RESULTADOS, "02_Rasters", "filtrados"), exist_ok=True)

# ---------------------------------------------- 1. cuanto speckle tiene cada producto
print("=" * 78)
print("PASO 1. Cuanto speckle tiene cada producto (ENL: mas alto = mejor)")
print("=" * 78)
filas = []
for aoi in AOIS_UTM:
    for etq, pol, f, b in productos(aoi):
        # OJO: no encadenar gdal.Open(f).GetRasterBand(b). En GDAL 3 el
        # Dataset temporal se libera en cuanto termina la expresion y la banda
        # queda colgando: ReadAsArray falla con "TypeError: in method
        # 'Band_XSize_get'". Hay que guardar el Dataset en una variable.
        # Corregido el 11/09/2026.
        ds = gdal.Open(f)
        a = ds.GetRasterBand(b).ReadAsArray().astype("float64")
        ds = None
        e = enl(a)
        filas.append([aoi, etq, pol, "%.2f" % e])
        print("   %-14s %-18s %-5s ENL = %5.2f" % (aoi[:6], etq, pol, e))
with open(os.path.join(RESULTADOS, "04_Tablas", "enl_por_producto.csv"), "w",
          newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["aoi", "producto", "banda_pol", "ENL"]); w.writerows(filas)

# ---------------------------------------------- 2. el experimento de la ventana
print()
print("=" * 78)
print("PASO 2. Cuanto R2 recupera el promediado (solo el bosque: la estepa no tiene dosel)")
print("=" * 78)
huellas = cargar_gedi("BOSQUE_NW_02")
if not huellas:
    print("   faltan las huellas GEDI. Ejecute antes el TP2.")
else:
    print("   huellas GEDI validas: %d" % len(huellas))
    print()
    print("   %-24s %s" % ("fuente", "".join("%9s" % ("%dx%d" % (2 * v + 1, 2 * v + 1))
                                             for v in VENTANAS)))
    exp = []
    ELEGIDOS = [("S1_GRD", "C_VH"), ("NISAR", "L_HV"), ("PALSAR2", "L_HV"), ("SAOCOM", "L_HV")]
    for etq, pol, f, b in productos("BOSQUE_NW_02"):
        if not any(etq.startswith(s) and pol == p for s, p in ELEGIDOS):
            continue
        linea = "   %-24s" % ("%s %s" % (etq, pol))
        fila = [etq, pol]
        for v in VENTANAS:
            r2, n = r2_contra_gedi(f, b, huellas, v)
            linea += "%9.3f" % r2; fila.append("%.3f" % r2)
        print(linea); exp.append(fila)
    with open(os.path.join(RESULTADOS, "04_Tablas", "r2_vs_ventana.csv"), "w",
              newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["producto", "banda_pol"] + ["r2_%dx%d" % (2 * v + 1, 2 * v + 1) for v in VENTANAS])
        w.writerows(exp)
    print()
    print("   LO QUE HAY QUE VER: en banda L el R2 SUBE al agrandar la ventana, hasta")
    print("   los 150 m, y despues baja. En banda C no sube: no es el speckle lo que")
    print("   le falta a la banda C.")

# ---------------------------------------------- 3. filtrar
print()
print("=" * 78)
print("PASO 3. Aplicar el filtro de Lee (en gamma0 LINEAL, no en dB)")
print("=" * 78)
try:
    from scipy.ndimage import uniform_filter          # noqa: F401
except ImportError:
    sys.exit("Falta scipy:  conda install -c conda-forge scipy")
n_ok = 0
for aoi in AOIS_UTM:
    vistos = set()
    for etq, pol, f, b in productos(aoi):
        if (etq, f) in vistos:
            continue
        vistos.add((etq, f))
        ds = gdal.Open(f)
        capas = []
        for i in (1, 2):
            a = ds.GetRasterBand(i).ReadAsArray().astype("float64")
            capas.append((ds.GetRasterBand(i).GetDescription() or "banda%d" % i,
                          lee_refinado(a)))
        sal = os.path.join(RESULTADOS, "02_Rasters", "filtrados", "%s_%s_lee.tif" % (etq, aoi))
        escribir(sal, capas, aoi)
        n_ok += 1
        e0 = enl(ds.GetRasterBand(1).ReadAsArray().astype("float64"))
        e1 = enl(capas[0][1])
        print("   %-14s %-18s ENL %5.2f -> %5.2f" % (aoi[:6], etq, e0, e1))
print()
print("Listo. %d productos filtrados -> 05_Resultados/02_Rasters/filtrados/" % n_ok)
print("El ENL sube tras filtrar: eso es exactamente lo que el filtro debe hacer.")
print()
print("SIGUIENTE PASO:  python TP4_07_contraste_C_vs_L.py")
