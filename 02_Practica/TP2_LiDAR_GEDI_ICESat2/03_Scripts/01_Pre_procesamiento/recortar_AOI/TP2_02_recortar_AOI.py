#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05_recortar_gedi.py
Extrae de los .h5 GEDI los disparos (footprints de ~25 m) que caen dentro de
cada AOI de 15 x 15 km y los guarda como CSV (WGS84 + UTM 19S).

  L2A: elev_lowestmode, rh25/50/75/95/98, quality_flag, sensitivity
  L2B: pai, fhd_normal, cover, l2b_quality_flag_rel3

USO (entorno conda 'aoi'):
  python 05_recortar_gedi.py                          (todo)
  python 05_recortar_gedi.py BOSQUE_NW_02 GEDI02_B    (un solo bloque)
"""
import csv
import glob
import os
import sys

try:
    import h5py
except ImportError:
    sys.exit("Falta h5py. Ejecutar: conda install -c conda-forge h5py pyproj")
try:
    from pyproj import Transformer
except ImportError:
    sys.exit("Falta pyproj. Ejecutar: conda install -c conda-forge h5py pyproj")


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

from aoi_config import AOIS_WGS84, EPSG, DESCARGAS, PROCESADOS

# GEDI (2024-2025) es anterior al incendio
EPOCA_GEDI = "02_pre"

T = Transformer.from_crs(4326, EPSG, always_xy=True)

# En GEDI V003 las coordenadas estan en la raiz del beam (L2A y L2B).
VARS = {
    "GEDI02_A": {
        "campos": ["elev_lowestmode", "l2a_quality_flag_rel3",
                   "degrade_flag", "sensitivity"],
        "rh": [25, 50, 75, 95, 98],
    },
    "GEDI02_B": {
        "campos": ["pai", "fhd_normal", "cover", "l2b_quality_flag_rel3"],
        "rh": [],
    },
}


def procesar(h5path, aoi, prod, escritor, encabezado_hecho):
    lonmin, latmin, lonmax, latmax = AOIS_WGS84[aoi]
    v = VARS[prod]
    n_total = 0
    nombre_h5 = os.path.basename(h5path)
    with h5py.File(h5path, "r") as f:
        for beam in [k for k in f.keys() if k.startswith("BEAM")]:
            g = f[beam]
            try:
                lat = g["lat_lowestmode"][:]
                lon = g["lon_lowestmode"][:]
            except KeyError:
                continue
            mask = ((lon >= lonmin) & (lon <= lonmax)
                    & (lat >= latmin) & (lat <= latmax))
            idx = mask.nonzero()[0]
            if idx.size == 0:
                continue

            shot = g["shot_number"][idx]
            cols = {}
            for c in v["campos"]:
                try:
                    cols[c] = g[c][idx]
                except KeyError:
                    cols[c] = [""] * idx.size
            if v["rh"]:
                rh_sub = g["rh"][idx, :]
                for p in v["rh"]:
                    cols["rh%d" % p] = rh_sub[:, p]

            if not encabezado_hecho[0]:
                escritor.writerow(["archivo", "beam", "shot_number", "lat",
                                   "lon", "este_utm19s", "norte_utm19s"]
                                  + list(cols))
                encabezado_hecho[0] = True

            for i, k in enumerate(idx):
                x, y = T.transform(lon[k], lat[k])
                escritor.writerow(
                    [nombre_h5, beam, shot[i], "%.6f" % lat[k],
                     "%.6f" % lon[k], "%.1f" % x, "%.1f" % y]
                    + [cols[c][i] for c in cols])
            n_total += idx.size
    return n_total


print(__doc__)
F_AOI = sys.argv[1] if len(sys.argv) > 1 else ""
F_PROD = sys.argv[2] if len(sys.argv) > 2 else ""

for aoi in AOIS_WGS84:
    if F_AOI and aoi != F_AOI:
        continue
    for prod in VARS:
        if F_PROD and prod != F_PROD:
            continue
        archivos = sorted(glob.glob(os.path.join(
            DESCARGAS, EPOCA_GEDI, "GEDI", aoi, prod, "*.h5")))
        if not archivos:
            print("=== %s | %s: SIN ARCHIVOS .h5 ===" % (aoi, prod))
            continue
        # Una sola ubicacion por producto, que es de donde leen TP2_03, TP2_06
        # y TP2_07. Antes esto escribia en "footprints_originales" y ademas
        # existia una copia identica en GEDI_L2A/ y GEDI_L2B/: dos lugares para
        # el mismo archivo, que es justo lo que la regla 2 prohibe.
        carpeta_prod = {"GEDI02_A": "GEDI_L2A", "GEDI02_B": "GEDI_L2B"}[prod]
        outdir = os.path.join(PROCESADOS, carpeta_prod)
        os.makedirs(outdir, exist_ok=True)
        salida = os.path.join(outdir, "%s_V003_%s_shots15km.csv" % (prod, aoi))
        print("=== %s | %s: %d granulos ===" % (aoi, prod, len(archivos)),
              flush=True)

        total = 0
        temporal = salida + ".tmp"
        with open(temporal, "w", newline="", encoding="utf-8") as fo:
            w = csv.writer(fo)
            hecho = [False]
            for a in archivos:
                n = procesar(a, aoi, prod, w, hecho)
                print("   %s: %d disparos" % (os.path.basename(a), n),
                      flush=True)
                total += n
        os.replace(temporal, salida)
        print("   TOTAL: %d disparos\n" % total, flush=True)

print("Listo. CSV en ./04_Tablas_de_trabajo/<AOI>/GEDI/ (QGIS: capa de puntos, columnas "
      "este_utm19s / norte_utm19s, EPSG:32719)")
