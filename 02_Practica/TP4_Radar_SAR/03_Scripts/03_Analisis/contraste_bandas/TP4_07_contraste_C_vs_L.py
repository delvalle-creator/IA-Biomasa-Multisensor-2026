#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_07_contraste_C_vs_L.py   ---> SEPTIMO script del TP4.

QUE HACE
--------
Mide el CONTRASTE entre el bosque y la estepa en cada sensor y cada polarizacion,
y con eso responde la pregunta central del practico: por que la banda L y no la C.

LA PREGUNTA
-----------
Los dos sitios son casi vecinos, tienen el mismo clima y el mismo relieve. La
diferencia es la biomasa: uno tiene un bosque de veinte metros y el otro un
pastizal. Si un sensor sirve para medir biomasa, TIENE que ver esa diferencia.
Cuanto mas grande sea la separacion entre los dos sitios, mas sensible es el
sensor a lo que nos interesa. Este script mide esa separacion, en decibeles.

LA FISICA, EN DOS PARRAFOS
--------------------------
El radar ilumina con microondas de una longitud de onda determinada, y la regla
practica es que una onda "ve" los objetos de tamano comparable a su longitud de
onda y ATRAVIESA los mas chicos.

La banda C mide unos 5,6 cm. Es del tamano de una hoja. Rebota en la superficie
del dosel y no baja mas: mide el techo, igual que el optico del TP3. La banda L
mide unos 24 cm. Le pasa de largo a las hojas y rebota en las RAMAS GRUESAS y los
TRONCOS, que es donde esta la mayor parte de la biomasa de un arbol. Por eso la
banda L ve biomasa y la banda C ve follaje.

LA POLARIZACION CRUZADA
-----------------------
El radar emite con una polarizacion y recibe con otra. HH y VV son "co-polares":
emite y recibe igual. HV y VH son "cruzadas": emite en una y recibe en la otra.

Una superficie lisa devuelve la onda sin cambiarle la polarizacion. Para que la
onda vuelva con la polarizacion CAMBIADA tiene que haber rebotado varias veces en
un volumen desordenado de dispersores orientados al azar: exactamente lo que es la
copa de un arbol con sus ramas. Por eso la polarizacion cruzada es la que mejor
responde al volumen de ramas, es decir, a la biomasa.

Ojo con una consecuencia incomoda: HV siempre da una senal MAS DEBIL en valor
absoluto (numeros mas negativos en dB) que HH o VV. Eso no la hace peor. Lo que
importa no es cuanta senal vuelve sino cuanto SEPARA las dos clases.

LO QUE VA A ENCONTRAR (medido con los datos de este proyecto)
--------------------------------------------------------------
   sensor                banda  pol   contraste bosque - estepa
   Sentinel-1 (10/01)      C     VV        3,5 dB
   Sentinel-1 (10/01)      C     VH        4,2 dB
   NISAR (08/01)           L     HH        8,1 dB
   NISAR (08/01)           L     HV        9,9 dB
   PALSAR-2 (2025)         L     HV       11,7 dB

La banda L separa los dos sitios con casi el triple de contraste que la banda C,
y el maximo esta en la polarizacion cruzada. Las dos cosas que predice la fisica.

EL CONTROL CRUZADO QUE VALE ORO
-------------------------------
NISAR y PALSAR-2 son misiones distintas, de agencias distintas, con
procesamientos distintos. Sobre el mismo bosque, en HV, dan -13,2 dB y -12,5 dB.
Coinciden dentro de un decibel sin haberse puesto de acuerdo. Eso es una
verificacion de calibracion independiente, y es la mejor prueba de que los
numeros no son un artefacto del procesamiento.

Cuando dos sensores independientes coinciden, se les puede creer a los dos.
Cuando discrepan, hay que ir a ver por que (en el TP3 fue asi como se descubrio
la bruma).

ENTRADA   02_Subsets_SNAP_QGIS/<sensor>/<epoca>/<AOI>/*/*.tif   (gamma0 LINEAL)
          02_Subsets_SNAP_QGIS/mascaras/mascara_validez.tif
SALIDA    05_Resultados/04_Tablas/contraste_bandas.csv

USO (entorno conda 'aoi'):   python TP4_07_contraste_C_vs_L.py
"""
import csv
import glob
import os
import sys

try:
    import numpy as np
    from osgeo import gdal
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

from configuracion_comun import AOIS_UTM          # noqa: E402

gdal.UseExceptions()
INSUMOS = os.path.join(TP4, "02_Subsets_SNAP_QGIS")
RESULTADOS = os.path.join(TP4, "05_Resultados")

# Se comparan fechas CASI SIMULTANEAS, para que la diferencia sea del sensor y no
# del momento. Todas son pre-incendio: el bosque en pie.
COMPARABLES = [
    ("Sentinel-1 GRD", "C", ("VH", "VV"), "Sentinel_1/*/%s/S1_GRD/*20260110*.tif"),
    ("SAOCOM L1A", "L", ("HH", "HV"), "SAOCOM/*/%s/*/*20260110*.tif"),
    ("NISAR GCOV", "L", ("HH", "HV"), "NISAR/*/%s/*/NISAR_GCOV_20260108.tif"),
    ("PALSAR-2 mosaico", "L", ("HH", "HV"), "ALOS_PALSAR_2/*/%s/*/PALSAR2_2025.tif"),
]


def db(a):
    """gamma0 lineal -> dB. Se pasa a dB DESPUES de promediar, nunca antes."""
    return np.where(a > 0, 10 * np.log10(a, where=a > 0), np.nan)


def mediana_db(patron, aoi, banda):
    hits = sorted(glob.glob(os.path.join(INSUMOS, patron % aoi)))
    hits = [h for h in hits if "_mask" not in h]
    if not hits:
        return float("nan"), 0
    ds = gdal.Open(hits[0])
    a = ds.GetRasterBand(banda).ReadAsArray().astype("float64")
    v = a[np.isfinite(a) & (a > 0)]
    if v.size < 1000:
        return float("nan"), 0
    # mediana en LINEAL y recien despues a dB
    return float(10 * np.log10(np.median(v))), int(v.size)


print(__doc__)
os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)
filas = []
print("=" * 84)
print("%-20s %-6s %-5s %10s %10s %12s" % ("sensor", "banda", "pol", "bosque", "estepa", "contraste"))
print("=" * 84)
for nombre, banda, pols, patron in COMPARABLES:
    for i, pol in enumerate(pols, 1):
        b, nb = mediana_db(patron, "BOSQUE_NW_02", i)
        e, ne = mediana_db(patron, "ESTEPA_NW_02", i)
        if b != b or e != e:
            print("%-20s %-6s %-5s   falta el producto" % (nombre, banda, pol))
            continue
        c = b - e
        marca = "  <--" if c > 9 else ""
        print("%-20s %-6s %-5s %9.2f %9.2f %11.2f dB%s" % (nombre, banda, pol, b, e, c, marca))
        filas.append([nombre, banda, pol, "%.2f" % b, "%.2f" % e, "%.2f" % c])

with open(os.path.join(RESULTADOS, "04_Tablas", "contraste_bandas.csv"), "w",
          newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sensor", "banda", "polarizacion", "bosque_gamma0_dB",
                "estepa_gamma0_dB", "contraste_dB"])
    w.writerows(filas)

print()
print("=" * 84)
print("CONTROL CRUZADO: dos misiones independientes sobre el mismo bosque")
print("=" * 84)
for nombre, patron in (("NISAR GCOV (08/01/2026)", "NISAR/*/%s/*/NISAR_GCOV_20260108.tif"),
                       ("PALSAR-2 mosaico (2025)", "ALOS_PALSAR_2/*/%s/*/PALSAR2_2025.tif")):
    b, _ = mediana_db(patron, "BOSQUE_NW_02", 2)
    print("   %-26s bosque HV = %6.2f dB" % (nombre, b))
print("   Si difieren en menos de 1 dB, las dos calibraciones se confirman entre si.")
print()
print("Tabla -> 05_Resultados/04_Tablas/contraste_bandas.csv")
print()
print("LO QUE HAY QUE OBSERVAR")
print("  1. La banda L separa el bosque de la estepa mucho mejor que la banda C.")
print("  2. Dentro de cada banda, la polarizacion CRUZADA (HV) separa mas que la")
print("     co-polar (HH, VV), aunque su senal absoluta sea mas debil.")
print("  3. Los valores absolutos de SAOCOM no coinciden con los de NISAR: distinto")
print("     angulo de incidencia y distinta calibracion. Compare FORMAS y CONTRASTES")
print("     entre sensores, no valores absolutos.")
print()
print("SIGUIENTE PASO:  python TP4_08_saturacion_radar.py")
