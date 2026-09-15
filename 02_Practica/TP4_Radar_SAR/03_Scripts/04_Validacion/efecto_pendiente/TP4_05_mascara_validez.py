#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_05_mascara_validez.py   ---> QUINTO script del TP4.
Construye la MASCARA COMUN DE VALIDEZ GEOMETRICA para el analisis multisensor.

Por que hace falta. Sentinel-1 observa estos sitios en pasada ASCENDENTE y
SAOCOM en pasada DESCENDENTE: los dos radares miran desde lados opuestos. El
Terrain Flattening ya normalizo el area iluminada, de modo que la radiometria es
comparable; pero la geometria no lo es en todos los pixeles. En terreno con
relieve hay zonas de layover (la ladera que mira al sensor se "vuelca" sobre el
rango) y de sombra de radar (la ladera opuesta no recibe pulso), y esas zonas
NO son las mismas para una mirada y para la otra. Un pixel en sombra para
SAOCOM puede estar perfectamente iluminado para Sentinel-1, y comparar ambos
alli carece de sentido.

Criterio. Se usa el angulo de incidencia LOCAL, que cada producto trae como
banda. Un pixel se considera geometricamente valido para un sensor cuando:

    UMBRAL_MIN < angulo local < UMBRAL_MAX   y   gamma0 > 0

Angulos muy pequenos indican laderas que encaran al sensor (riesgo de layover y
de saturacion); angulos muy grandes, laderas de espaldas (sombra, senal cercana
al ruido). La mascara final es la INTERSECCION de los pixeles validos para
TODOS los sensores y TODAS las fechas: el analisis multisensor debe restringirse
a ella.

SALIDA (una por recinto, en 02_Subsets_SNAP_QGIS/mascaras/):
    mascara_validez_<AOI>.tif   1 = valido para todos los sensores, 0 = descartar
                                (bandas adicionales: validez por sensor)

USO:  python TP4_05_mascara_validez.py [epoca]    (por defecto 02_pre)
"""
import glob
import os
import sys

import numpy as np

try:
    from osgeo import gdal
except ImportError:
    sys.exit("Falta GDAL. Ejecutar: conda activate aoi")


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

from aoi_config import AOIS_UTM, EPSG, PIXEL, PROCESADOS, EPOCAS, dir_procesado

gdal.UseExceptions()

UMBRAL_MIN = 15.0     # grados: por debajo, riesgo de layover
UMBRAL_MAX = 70.0     # grados: por encima, sombra o senal muy debil
SENSORES = ["S1_GRD", "S1_SLC", "SAOCOM_L1A"]


def leer(img):
    ds = gdal.Open(img)
    a = ds.GetRasterBand(1).ReadAsArray().astype("float32")
    ds = None
    return a


def valido_producto(dim):
    """Mascara booleana de validez geometrica de un producto."""
    data = dim[:-4] + ".data"
    ang = os.path.join(data, "localIncidenceAngle.img")
    if not os.path.exists(ang):
        return None
    a = leer(ang)
    ok = (a > UMBRAL_MIN) & (a < UMBRAL_MAX) & np.isfinite(a)
    # ademas, gamma0 debe existir y ser positivo en todas las polarizaciones
    for g in glob.glob(os.path.join(data, "Gamma0_*.img")):
        v = leer(g)
        ok &= np.isfinite(v) & (v > 0)
    return ok


print(__doc__)
EPOCA = sys.argv[1] if len(sys.argv) > 1 else "02_pre"
EPOCA = next((e for e in EPOCAS if EPOCA in e), EPOCA)
print("\nEpoca: %s\n" % EPOCA)
for aoi in AOIS_UTM:
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    print("\n=== %s ===" % aoi)
    por_sensor, comun = {}, None
    for sensor in SENSORES:
        d = dir_procesado(sensor, EPOCA, aoi)
        dims = sorted(glob.glob(os.path.join(d, "*.dim"))) if d else []
        if not dims:
            continue
        acumulado = None
        for d in dims:
            v = valido_producto(d)
            if v is None:
                continue
            acumulado = v if acumulado is None else (acumulado & v)
        if acumulado is None:
            continue
        por_sensor[sensor] = acumulado
        comun = acumulado if comun is None else (comun & acumulado)
        print("   %-11s valido en %5.1f %% del AOI  (%d fechas)"
              % (sensor, 100 * acumulado.mean(), len(dims)))
    if comun is None:
        print("   sin productos SAR")
        continue
    print("   %-11s valido en %5.1f %% del AOI" % ("COMUN", 100 * comun.mean()))
    perdido = 100 * (1 - comun.mean())
    print("   -> se descarta el %.1f %% de los pixeles por geometria "
          "desfavorable en al menos un sensor" % perdido)

    # ---- escritura del GeoTIFF: banda 1 = comun, luego una por sensor ----
    # Una mascara por AOI, en la carpeta que ya existe para eso.
    salida = os.path.join(PROCESADOS, "mascaras", "mascara_validez_%s.tif" % aoi)
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    nombres_b = ["valido_comun"] + ["valido_" + s for s in por_sensor]
    capas = [comun] + [por_sensor[s] for s in por_sensor]
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(salida, 1500, 1500, len(capas), gdal.GDT_Byte,
                    ["COMPRESS=DEFLATE", "TILED=YES"])
    ds.SetGeoTransform((xmin, PIXEL, 0, ymax, 0, -PIXEL))
    from osgeo import osr
    srs = osr.SpatialReference(); srs.ImportFromEPSG(EPSG)
    ds.SetProjection(srs.ExportToWkt())
    for i, (nom, capa) in enumerate(zip(nombres_b, capas), 1):
        b = ds.GetRasterBand(i)
        b.WriteArray(capa.astype("uint8"))
        b.SetDescription(nom)
    ds = None
    print("   mascara escrita: %s" % os.path.basename(salida))

print("\nListo. Restrinja el analisis multisensor a los pixeles con "
      "valido_comun = 1.")
