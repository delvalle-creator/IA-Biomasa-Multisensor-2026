#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP3_04_dnbr_incendio.py   ---> CUARTO script del TP3.
Cartografia del incendio con el indice dNBR y estadisticas de superficie
quemada por sitio y por clase de severidad.

QUE ES EL NBR Y POR QUE FUNCIONA
--------------------------------
El NBR (Normalized Burn Ratio, indice normalizado de area quemada) combina dos
bandas que reaccionan de forma OPUESTA al fuego:

  NBR = (NIR - SWIR2) / (NIR + SWIR2)

  - NIR  (infrarrojo cercano, B8): la vegetacion viva y sana lo refleja mucho,
    porque la estructura interna de las hojas lo dispersa. Al quemarse, cae.
  - SWIR2 (infrarrojo de onda corta, B12): responde al contenido de agua. La
    vegetacion viva lo absorbe (es decir, refleja poco); el suelo desnudo, la
    ceniza y el carbon, que estan secos, lo reflejan mucho. Al quemarse, sube.

Como una banda baja y la otra sube, el NBR se desploma tras el fuego, y esa es
la razon por la que separa el area quemada mejor que cualquier banda sola o que
el NDVI.

El dNBR es la DIFERENCIA entre el antes y el despues:

  dNBR = NBR_pre - NBR_post

Valores altos y positivos = mucha perdida de vegetacion (quema severa). Valores
cercanos a cero = sin cambio. Se usan los umbrales de severidad de Key y Benson
(USGS), que son el estandar internacional.

POR QUE SE COMPARAN ESTAS FECHAS
--------------------------------
  pre  = 25/11/2025 (la ultima imagen LIMPIA antes del incendio)
  post = 05/03/2026 (la primera imagen limpia despues)

ATENCION: LA FECHA PRE NO ES LA MAS CERCANA AL INCENDIO, Y ESO ES DELIBERADO.
La escena del 09/01/2026 esta mas cerca del fuego, pero esta CONTAMINADA CON
BRUMA: su banda azul vale 0,158 cuando lo normal en este sitio es 0,024, casi
siete veces mas. La mascara de nubes del producto (SCL) no la detecto: marco
apenas un 7% de cirros. El script TP1_02_detectar_bruma.py del practico 1 la
identifica.

Se comprobo el efecto de usar una u otra escena:

   escena pre        NBR pre    area quemada
   09/01/2026 (bruma)  0,528    16.502 ha (79,4%)
   25/11/2025 (limpia) 0,513    18.009 ha (80,2%)

La diferencia es menor a un punto porcentual, y la razon es instructiva: el NBR
usa el infrarrojo cercano y el de onda corta, que son las bandas MENOS afectadas
por la bruma (los aerosoles dispersan sobre todo las longitudes de onda cortas).
Por eso el NBR aguanta la bruma mientras el NDVI de esa misma escena se derrumba
de 0,80 a 0,34. Aun asi, habiendo una escena limpia disponible, se usa la limpia.

Se usa Sentinel-2 por su resolucion de 10 m.

ENMASCARADO DE NUBES: se usa la banda de clasificacion de escena (SCL) de
Sentinel-2, descartando nubes, sombras de nube, nieve y pixeles saturados. Un
pixel solo se considera valido si esta limpio en AMBAS fechas.

ENTRADA   02_Subsets_SNAP_QGIS/Sentinel_2/<epoca>/<AOI>/*.tif
SALIDA    05_Resultados/02_Rasters/incendio/<AOI>/dNBR_<AOI>.tif       (dNBR, NBR_pre, NBR_post)
          05_Resultados/02_Rasters/incendio/<AOI>/severidad_<AOI>.tif  (clases, ver tabla)
          05_Resultados/04_Tablas/estadisticas_incendio.csv

USO (entorno conda 'aoi'):   python TP3_04_dnbr_incendio.py
"""
import csv
import glob
import os
import sys

try:
    import numpy as np
    from osgeo import gdal, osr
except ImportError:
    sys.exit("Falta numpy o GDAL. Activar el entorno conda 'aoi'.")

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

INSUMOS = os.path.join(TP3, "02_Subsets_SNAP_QGIS", "Sentinel_2")
RESULTADOS = os.path.join(TP3, "05_Resultados")

gdal.UseExceptions()

# fechas elegidas (la ultima limpia antes y la primera limpia despues)
# El comodin del final NO es decorativo. Las carpetas de 02_Subsets_SNAP_QGIS se llaman
# 02_pre_incendio_2025_26 y 03_post_incendio_2026, no 02_pre y 03_post. Sin el
# asterisco el glob no encuentra nada y el script contesta "faltan escenas pre o
# post, se omite" sin dar ningun error. Corregido el 29/07/2026.
# POR QUE LA DEL 25/11 Y NO LA DEL 09/01/2026 (verificado el 31/07/2026)
# En 02_pre_incendio_2025_26 hay una segunda escena, del 9 de enero de 2026, que
# a primera vista es mejor: tambien es pre-incendio -el fuego fue entre el 10/01
# y el 27/02- y esta a ocho semanas de la post, las dos en verano. NO SIRVE: su
# correccion atmosferica fallo. El visible quedo inflado entre cuatro y seis
# veces (azul 0,1528 contra 0,0235; rojo 0,1210 contra 0,0290) mientras el NIR y
# los SWIR quedaron iguales, que es la firma de dispersion no removida. El NDVI
# sobre bosque cerrado da 0,38 y el SCL etiqueta el 78 % del recinto como suelo
# desnudo. Detalle completo en el LEEME de esa carpeta.
# La del 25/11/2025 tiene 0,00 % de pixeles inutilizables y es Sentinel-2B, el
# mismo sensor que la post.
PRE_PAT = "02_pre*/%s/*20251125*.tif"
POST_PAT = "03_post*/%s/*20260305*.tif"

B8, B12, SCL = 7, 10, 11        # numero de banda en el GeoTIFF de S2

# SCL: clases que NO sirven (nube, sombra, nieve, saturado, sin dato)
SCL_MALAS = {0, 1, 3, 8, 9, 10, 11}

# Umbrales de severidad de Key y Benson (USGS), el estandar internacional.
# Son SIETE clases y los limites son CONTIGUOS: el extremo superior de cada una
# es el extremo inferior de la siguiente. Si se dejara un hueco (terminar en
# 0,099 y empezar la siguiente en 0,100), los pixeles caidos en ese hueco no
# recibirian ninguna clase y quedarian marcados como "sin dato".
SEVERIDAD = [
    (1, "Regeneracion alta",      -np.inf, -0.250),
    (2, "Regeneracion baja",      -0.250, -0.100),
    (3, "Sin cambio",             -0.100,  0.100),
    (4, "Severidad baja",          0.100,  0.270),
    (5, "Severidad moderada-baja", 0.270,  0.440),
    (6, "Severidad moderada-alta", 0.440,  0.660),
    (7, "Severidad alta",          0.660,  np.inf),
]
QUEMADO_DESDE = 4      # de la clase 4 (severidad baja) en adelante: quemado


def leer(patron, aoi):
    hits = sorted(glob.glob(os.path.join(INSUMOS, patron % aoi)))
    if not hits:
        return None, None
    d = gdal.Open(hits[0])
    return d, os.path.basename(hits[0])


def nbr_y_mascara(ds):
    """Devuelve (NBR, mascara_valida) de un producto Sentinel-2."""
    nir = ds.GetRasterBand(B8).ReadAsArray().astype("float32")
    swir = ds.GetRasterBand(B12).ReadAsArray().astype("float32")
    scl = ds.GetRasterBand(SCL).ReadAsArray().astype("int16")
    limpio = ~np.isin(scl, list(SCL_MALAS))
    con_dato = (nir > 0) & (swir > 0)
    val = limpio & con_dato
    den = nir + swir
    nbr = np.where(val & (den != 0), (nir - swir) / np.where(den == 0, 1, den), np.nan)
    return nbr.astype("float32"), val


def escribir(ruta, capas, aoi, tipo=gdal.GDT_Float32, nodata=None):
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    ny, nx = capas[0][1].shape
    ds = gdal.GetDriverByName("GTiff").Create(
        ruta, nx, ny, len(capas), tipo,
        options=["COMPRESS=DEFLATE", "TILED=YES"])
    ds.SetGeoTransform((xmin, PIXEL, 0, ymax, 0, -PIXEL))
    sr = osr.SpatialReference(); sr.ImportFromEPSG(EPSG)
    ds.SetProjection(sr.ExportToWkt())
    for i, (nom, arr) in enumerate(capas, 1):
        b = ds.GetRasterBand(i); b.WriteArray(arr); b.SetDescription(nom)
        if nodata is not None:
            b.SetNoDataValue(nodata)
    ds.FlushCache(); ds = None


print(__doc__)
filas = []
for aoi in AOIS_UTM:
    print("=" * 72)
    print(aoi)
    print("=" * 72)
    dpre, npre = leer(PRE_PAT, aoi)
    dpost, npost = leer(POST_PAT, aoi)
    if dpre is None or dpost is None:
        print("   faltan escenas pre o post, se omite")
        continue
    print("   pre :", npre)
    print("   post:", npost)

    nbr_pre, val_pre = nbr_y_mascara(dpre)
    nbr_post, val_post = nbr_y_mascara(dpost)
    # un pixel solo vale si esta limpio en AMBAS fechas
    val = val_pre & val_post
    dnbr = np.where(val, nbr_pre - nbr_post, np.nan).astype("float32")
    print("   pixeles validos en ambas fechas: %.1f%%" % (100 * val.mean()))

    # --- clasificacion de severidad ---
    sev = np.zeros(dnbr.shape, dtype="uint8")     # 0 = sin dato
    for cod, nom, lo, hi in SEVERIDAD:
        m = val & (dnbr >= lo) & (dnbr < hi)
        sev[m] = cod

    outdir = os.path.join(RESULTADOS, "02_Rasters", "incendio", aoi)
    os.makedirs(outdir, exist_ok=True)
    escribir(os.path.join(outdir, "dNBR_%s.tif" % aoi),
             [("dNBR", dnbr), ("NBR_pre", nbr_pre), ("NBR_post", nbr_post)],
             aoi, nodata=float("nan"))
    escribir(os.path.join(outdir, "severidad_%s.tif" % aoi),
             [("severidad", sev)], aoi, tipo=gdal.GDT_Byte, nodata=0)

    # --- estadisticas ---
    total_val = int(val.sum())
    print()
    print("   %-26s %10s %8s %12s" % ("Clase", "pixeles", "%", "hectareas"))
    for cod, nom, lo, hi in SEVERIDAD:
        n = int((sev == cod).sum())
        if n == 0:
            continue
        ha = n / 100.0                      # pixel 10x10 m = 100 m2
        pct = 100.0 * n / total_val if total_val else 0
        print("   %-26s %10d %7.2f%% %12.1f" % (nom, n, pct, ha))
        filas.append([aoi, nom, "%.3f a %.3f" % (lo, hi) if np.isfinite(lo) and np.isfinite(hi)
                      else ("< %.3f" % hi if not np.isfinite(lo) else "> %.3f" % lo),
                      n, "%.2f" % pct, "%.1f" % ha])
    # Control: ningun pixel valido puede quedar sin clase. Si aparece alguno,
    # hay un hueco en los umbrales y hay que corregirlo, no ignorarlo.
    sin_clase = int((val & (sev == 0)).sum())
    if sin_clase:
        print("   ATENCION: %d pixeles validos quedaron SIN CLASE "
              "(hay un hueco en los umbrales)" % sin_clase)

    quemado = int(np.isin(sev, [c for c, _, _, _ in SEVERIDAD if c >= QUEMADO_DESDE]).sum())
    ha_q = quemado / 100.0
    # DOS denominadores, porque no significan lo mismo:
    #   pct_val = sobre los pixeles utiles (limpios en ambas fechas)
    #   pct_aoi = sobre el recinto completo de 15 x 15 km = 22.500 ha
    pct_q = 100.0 * quemado / total_val if total_val else 0
    pct_aoi = 100.0 * quemado / sev.size if sev.size else 0
    print("   " + "-" * 60)
    print("   %-26s %10d %7.2f%% %12.1f" % ("QUEMADO (severidad >= baja)", quemado, pct_q, ha_q))
    print("   %-26s %10s %7.2f%% %12.1f" % ("   ...sobre el recinto", "", pct_aoi,
                                            sev.size / 100.0))
    filas.append([aoi, "TOTAL QUEMADO", "dNBR >= 0.100", quemado,
                  "%.2f" % pct_q, "%.1f" % ha_q])
    filas.append([aoi, "TOTAL QUEMADO (% del recinto)", "dNBR >= 0.100", quemado,
                  "%.2f" % pct_aoi, "%.1f" % ha_q])
    if quemado:
        print("   dNBR mediano en el area quemada: %.3f"
              % float(np.nanmedian(dnbr[sev >= QUEMADO_DESDE])))
    print()

# --- CSV ---
os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)
csvp = os.path.join(RESULTADOS, "04_Tablas", "estadisticas_incendio.csv")
with open(csvp, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["aoi", "clase_severidad", "rango_dNBR", "pixeles", "porcentaje", "hectareas"])
    w.writerows(filas)

print("Listo.")
print("  Rasters: 05_Resultados/02_Rasters/incendio/<AOI>/")
print("  Tabla  : 05_Resultados/04_Tablas/estadisticas_incendio.csv")
print("Los .tif se abren en QGIS. Para ver el dNBR, aplique una paleta divergente")
print("y clasifique con los umbrales de Key y Benson.")
