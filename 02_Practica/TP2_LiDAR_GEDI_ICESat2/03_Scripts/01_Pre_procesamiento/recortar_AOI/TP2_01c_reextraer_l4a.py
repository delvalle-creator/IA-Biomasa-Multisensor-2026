#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_01c_reextraer_l4a.py   ---> vuelve a leer los .h5 del L4A que YA ESTAN.

QUE HACE Y QUE NO HACE
----------------------
NO se conecta a internet. NO pide credenciales de Earthdata. NO descarga nada.
Lee los granulos GEDI L4A que ya estan guardados en

    00_COMUN/08_Originales_crudos/02_pre/GEDI_L4A/<AOI>/*.h5

y vuelve a escribir el CSV de disparos con la lista COMPLETA de campos, la que
esta en funciones/gedi_l4a.py. Tarda unos minutos y no consume ancho de banda.

CUANDO SE CORRE
---------------
Cada vez que se agregue o se saque un campo de la lista de gedi_l4a.py. La
descarga -TP2_01b- solo hace falta si cambia el PERIODO, el RECINTO o la version
del producto. Mientras los .h5 sigan en disco, este script alcanza.

POR QUE ESTO IMPORTA
--------------------
Los granulos pesan 2,7 GB y bajarlos lleva horas. Son el dato crudo del que sale
todo lo demas: se guardan y no se borran nunca. Si alguna vez faltan, hay que
volver a bajarlos con TP2_01b, y recien entonces.

SALIDA    TP2_LiDAR_GEDI_ICESat2/02_Subsets_SNAP_QGIS/GEDI_L4A/GEDI04_A_<AOI>_shots15km.csv
          (se sobrescribe; el anterior se guarda con el sufijo .previo)

USO (entorno conda 'aoi'):   python TP2_01c_reextraer_l4a.py
"""
import os
import shutil
import sys

# --- para que Python encuentre funciones/ y configuracion/ del practico ---
_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d):
    if os.path.isdir(os.path.join(_d, "funciones")):
        sys.path.insert(0, os.path.join(_d, "funciones"))
        sys.path.insert(0, os.path.join(_d, "configuracion"))
        break
    _d = os.path.dirname(_d)

from aoi_config import AOIS_WGS84, DESCARGAS                        # noqa: E402
from gedi_l4a import extraer_h5                                     # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
DESTINO_CSV = os.path.join(TP2, "02_Subsets_SNAP_QGIS", "GEDI_L4A")
EPOCA = "02_pre"

print(__doc__)

falta = False
for aoi in AOIS_WGS84:
    carpeta = os.path.join(DESCARGAS, EPOCA, "GEDI_L4A", aoi)
    n = len([x for x in os.listdir(carpeta) if x.endswith(".h5")]) \
        if os.path.isdir(carpeta) else 0
    print("   %-14s %2d granulos en %s" % (aoi, n, carpeta))
    if n == 0:
        falta = True

if falta:
    sys.exit("\nFaltan granulos. Hay que bajarlos primero:\n"
             "   python TP2_01b_descargar_gedi_l4a.py")

print()
total = 0
for aoi in AOIS_WGS84:
    print("=== %s ===" % aoi)
    previo = os.path.join(DESTINO_CSV, "GEDI04_A_%s_shots15km.csv" % aoi)
    if os.path.isfile(previo):
        shutil.copy2(previo, previo + ".previo")
        print("   copia del CSV anterior -> %s.previo" % os.path.basename(previo))
    total += extraer_h5(os.path.join(DESCARGAS, EPOCA, "GEDI_L4A", aoi),
                        aoi, DESTINO_CSV)
    print()

print("=" * 72)
print("%d disparos extraidos en total." % total)
print()
print("SIGUIENTE PASO, en este orden:")
print("   python TP2_10_auditoria_L4A.py")
print("      (ahora si puede decir cuantas huellas se caen por predictor_limit,")
print("       por response_limit y por algorithm_run, y cuantas por hoja caida)")
print("   python TP2_07_biomasa_referencia.py")
print("   python TP2_09_cobertura_BAP.py")
