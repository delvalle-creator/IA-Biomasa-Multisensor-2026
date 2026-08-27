# -*- coding: utf-8 -*-
"""
gedi_l4a.py   ---> que campos se sacan del L4A, y como se sacan.

POR QUE ESTE MODULO EXISTE APARTE
---------------------------------
La lista de campos y la rutina que los extrae las necesitan DOS scripts:

    TP2_01b_descargar_gedi_l4a.py   busca, descarga y extrae
    TP2_01c_reextraer_l4a.py        vuelve a extraer de los .h5 que ya estan

Si cada uno llevara su propia copia de la lista, tarde o temprano una de las dos
quedaria vieja y el CSV saldria con columnas distintas segun quien lo genero.
Aca hay una sola lista, y las dos la leen.

POR QUE LA LISTA TIENE 20 CAMPOS Y NO 7 (31/07/2026)
----------------------------------------------------
La primera extraccion bajo siete campos y con eso no se podia explicar por que el
L4A descarta huellas. Medido sobre los granulos que ya estaban en disco:

    BOSQUE_NW_02   de 690 huellas validas del L2A, el L4A rechaza 419.
                   195 se explican por sensitivity < 0,95 (umbral medido: la
                   sensibilidad mas baja entre las ACEPTADAS es 0,9501).
                   224 pasan el control del L2A Y el de sensibilidad y aun asi
                   quedan rechazadas. 93 de esas 224 son lenga, o sea el 57 %
                   de toda la lenga del recinto.

Ese 53,5 % del rechazo solo puede venir de las banderas que no se habian bajado:
algorithm_run_flag, predictor_limit_flag y response_limit_flag. Se agregan
tambien el intervalo de prediccion completo, el algoritmo elegido y el bloque
land_cover_data, que trae leaf_off_flag: lenga y nire son CADUCIFOLIAS, y un
disparo tomado sin hojas no mide el mismo dosel que uno tomado con hojas.

Cada entrada es (ruta dentro del grupo BEAM, nombre de la columna del CSV). Si
una version del producto no trae alguno de estos campos, la columna sale vacia y
el script no se cae.
"""
import csv
import glob
import os

import h5py
from pyproj import Transformer

from aoi_config import AOIS_WGS84, EPSG

CAMPOS = [
    ("agbd",                             "agbd"),
    ("agbd_se",                          "agbd_se"),
    ("agbd_pi_lower",                    "agbd_pi_lower"),
    ("agbd_pi_upper",                    "agbd_pi_upper"),
    ("l4_quality_flag",                  "l4_quality_flag"),
    ("l2_quality_flag",                  "l2_quality_flag"),
    ("algorithm_run_flag",               "algorithm_run_flag"),
    ("predictor_limit_flag",             "predictor_limit_flag"),
    ("response_limit_flag",              "response_limit_flag"),
    ("surface_flag",                     "surface_flag"),
    ("selected_algorithm",               "selected_algorithm"),
    ("degrade_flag",                     "degrade_flag"),
    ("sensitivity",                      "sensitivity"),
    ("solar_elevation",                  "solar_elevation"),
    ("predict_stratum",                  "predict_stratum"),
    ("land_cover_data/pft_class",        "pft_class"),
    ("land_cover_data/region_class",     "region_class"),
    ("land_cover_data/leaf_off_flag",    "leaf_off_flag"),
    ("land_cover_data/landsat_treecover","landsat_treecover"),
    ("land_cover_data/urban_proportion", "urban_proportion"),
]

COLUMNAS = (["archivo", "beam", "shot_number", "lat", "lon",
             "este_utm19s", "norte_utm19s"] + [c for _, c in CAMPOS])

_T = Transformer.from_crs(4326, EPSG, always_xy=True)


def extraer_h5(carpeta_h5, aoi, destino_csv):
    """Vuelca a CSV los disparos del L4A que caen dentro del recinto del AOI.

    No toca la red: solo lee los .h5 que ya estan en 'carpeta_h5'.
    Devuelve la cantidad de disparos escritos.
    """
    lonmin, latmin, lonmax, latmax = AOIS_WGS84[aoi]
    h5s = sorted(glob.glob(os.path.join(carpeta_h5, "*.h5")))
    if not h5s:
        print("   no hay .h5 que extraer en %s" % carpeta_h5)
        return 0

    os.makedirs(destino_csv, exist_ok=True)
    sal = os.path.join(destino_csv, "GEDI04_A_%s_shots15km.csv" % aoi)
    n_total, n_aporta = 0, 0

    with open(sal, "w", newline="", encoding="utf-8") as fcsv:
        w = csv.DictWriter(fcsv, fieldnames=COLUMNAS)
        w.writeheader()
        for archivo in h5s:
            nombre = os.path.basename(archivo)
            try:
                f = h5py.File(archivo, "r")
            except Exception as e:
                print("   no se pudo abrir %s (%s)" % (nombre, e))
                continue
            n_antes = n_total
            with f:
                for beam in [k for k in f.keys() if k.startswith("BEAM")]:
                    g = f[beam]
                    if "lat_lowestmode" not in g:
                        continue
                    lat = g["lat_lowestmode"][:]
                    lon = g["lon_lowestmode"][:]
                    dentro = ((lat >= latmin) & (lat <= latmax) &
                              (lon >= lonmin) & (lon <= lonmax))
                    idx = dentro.nonzero()[0]
                    if idx.size == 0:
                        continue
                    shot = g["shot_number"][:]
                    # OJO: la variable del lazo se llama 'campo', NO 'ruta'.
                    # Si se llamara 'ruta' pisaria el nombre del .h5 que se esta
                    # leyendo, que es justo la clase de error que no se ve hasta
                    # que alguien agrega una linea mas abajo.
                    datos = {}
                    for campo, col in CAMPOS:
                        datos[col] = g[campo][:] if campo in g else None
                    este, norte = _T.transform(lon[idx], lat[idx])
                    for k, i in enumerate(idx):
                        fila = {"archivo": nombre, "beam": beam,
                                "shot_number": str(shot[i]),
                                "lat": "%.6f" % lat[i], "lon": "%.6f" % lon[i],
                                "este_utm19s": "%.2f" % este[k],
                                "norte_utm19s": "%.2f" % norte[k]}
                        for _, col in CAMPOS:
                            v = datos[col]
                            if v is None:
                                fila[col] = ""
                            else:
                                x = v[i]
                                fila[col] = (x.decode() if isinstance(x, bytes)
                                             else str(x))
                        w.writerow(fila)
                        n_total += 1
            if n_total > n_antes:
                n_aporta += 1

    faltantes = [c for _, c in CAMPOS]
    print("   %d granulos leidos, %d aportaron disparos dentro del recinto"
          % (len(h5s), n_aporta))
    print("   %d disparos  ->  %s" % (n_total, os.path.basename(sal)))
    print("   columnas escritas: %d  (%s)" % (len(COLUMNAS), ", ".join(faltantes)))
    return n_total
