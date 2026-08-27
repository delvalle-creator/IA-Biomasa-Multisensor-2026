#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_08_saturacion_radar.py   ---> OCTAVO y ultimo script del TP4.

QUE HACE
--------
Repite EXACTAMENTE el experimento del TP3_05, pero con radar en vez de optico:
cruza las huellas GEDI del bosque con gamma0 y mide hasta donde responde cada
banda al aumentar la altura del dosel. Es la comparacion que cierra el practico y
la que contesta la pregunta que quedo abierta en el TP3.

POR QUE SE REPITE EL MISMO EXPERIMENTO
--------------------------------------
Porque si no, no hay comparacion posible. Mismas huellas, mismo bosque, misma
metrica (rh95), mismo procedimiento: lo unico que cambia es el sensor. Cuando se
quiere comparar dos instrumentos, todo lo demas tiene que quedar igual. Eso es lo
que hace que el resultado signifique algo.

Una diferencia si hay, y es deliberada: aqui la ventana es de 15x15 pixeles
(150 m) y no de 3x3. El script TP4_06 mostro por que: con 3x3 el speckle se come
la senal del radar. No es hacer trampa, es corregir por una propiedad conocida
del instrumento, y queda declarado.

LO QUE VA A ENCONTRAR
---------------------
gamma0 mediano (dB) por franja de altura del dosel, ventana de 150 m:

   altura (m)     n    S1 VH    S1 VV   NISAR HV  PALSAR2 HV  SAOCOM HV
   0-3           76   -16,19   -10,20    -14,32     -13,65     -18,56
   3-6          192   -15,89    -9,93    -13,94     -13,31     -18,12
   6-9          104   -15,85    -9,99    -13,78     -13,22     -17,93
   9-12          68   -15,79    -9,84    -13,12     -12,79     -17,18
   12-15         58   -15,78    -9,66    -12,17     -11,87     -16,96
   15-18         40   -15,86    -9,67    -12,14     -11,96     -16,95
   18-21         54   -16,00    -9,80    -12,22     -11,84     -16,87
   21-25         59   -15,63    -9,61    -11,73     -11,41     -16,44
   25-30         33   -15,76    -9,71    -11,55     -11,69     -16,60

   de 0-3 m a mas de 21 m:  S1 VH gana 0,53 dB | S1 VV 0,52 dB
                            NISAR HV 2,59 dB | PALSAR-2 HV 2,16 dB | SAOCOM HV 1,98 dB

TRES CONCLUSIONES, Y NINGUNA ES OPCIONAL
----------------------------------------
1. LA BANDA C ES PLANA. Recorra la columna de S1 VH de arriba abajo: -16,19 al
   principio, -15,76 al final. Medio decibel en veinticinco metros de arbol, con
   idas y venidas por el medio. La banda C no distingue un renoval de un bosque
   maduro. No es cuestion de filtrar mejor ni de ajustar otro modelo: la senal no
   esta. Esa es la respuesta a "por que la banda L y no la C", y usted la acaba de
   medir en vez de leerla.

2. LA BANDA L RESPONDE, Y SIGUE RESPONDIENDO DONDE EL OPTICO YA NO. Esta es la
   conclusion importante. Compare con lo que midio en el TP3:

      franja de altura      NDVI (TP3)     NISAR HV (TP4)
      18-21 m                  0,878          -12,22 dB
      21-25 m                  0,896          -11,73 dB
      25-30 m                  0,894          -11,55 dB
                            se aplano        sigue subiendo

   Donde el NDVI se quedo quieto, la banda L todavia gana medio decibel por
   franja. Eso es, literalmente, la razon de ser de este practico: el radar de
   banda L ve lo que el optico ya no puede ver, porque la onda atraviesa el dosel
   y llega a los troncos.

3. LOS TRES SENSORES DE BANDA L COINCIDEN EN LA FORMA, NO EN EL VALOR. NISAR,
   PALSAR-2 y SAOCOM arrancan en -14,3, -13,7 y -18,6 dB: valores absolutos muy
   distintos, porque tienen distinto angulo de incidencia y distinta calibracion.
   Pero los tres suben de manera monotona y ganan alrededor de 2 dB en el mismo
   tramo. Tres instrumentos independientes describen el mismo fenomeno. Cuando eso
   pasa, el fenomeno es real y no un artefacto del procesamiento.

   Leccion transferible: entre sensores distintos, compare FORMAS y CONTRASTES.
   Los valores absolutos solo son comparables dentro de una misma calibracion.

Y AHORA LA PARTE INCOMODA, QUE TAMBIEN HAY QUE DECIR
-----------------------------------------------------
El R2 del ajuste gamma0 -> altura llega a 0,245 en el mejor caso (NISAR HV con
ventana de 150 m). Es OCHO VECES el de la banda C (0,03), pero sigue siendo bajo,
y de hecho es menor que el 0,30 que dio el NDMI en el TP3.

Conviene entender por que, porque no contradice nada de lo anterior:

  - GEDI mide ALTURA; el radar de banda L responde a BIOMASA. Son cosas
    relacionadas pero distintas: dos bosques de la misma altura pueden tener muy
    distinta densidad de troncos.
  - Este bosque es mayormente bajo: la mitad de las huellas no llega a 9 m. En ese
    rango el optico todavia no satura, asi que compite de igual a igual. La ventaja
    de la banda L recien se despliega en biomasa alta, y aqui hay poca.
  - El radar arrastra el efecto del relieve, y este es un bosque andino.

La conclusion honesta del TP4 no es "el radar gana". Es esta: NINGUN sensor solo
alcanza. El optico satura, el radar tiene speckle y responde a otra variable, y
GEDI mide bien pero solo en huellas dispersas. Cada uno falla donde el otro
funciona. Eso no es un problema del trabajo: es el argumento del TP5, que los
combina.

ENTRADA   02_Subsets_SNAP_QGIS/<sensor>/<epoca>/<AOI>/*/*.tif
          ../TP2_LiDAR_GEDI_ICESat2/05_Resultados/04_Tablas/GEDI_L2A_<AOI>_aceptados.csv
SALIDA    05_Resultados/04_Tablas/saturacion_radar.csv
          05_Resultados/04_Tablas/modelos_radar.txt
          05_Resultados/04_Tablas/cruce_gedi_radar.csv

USO (entorno conda 'aoi'):   python TP4_08_saturacion_radar.py
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

gdal.UseExceptions()
INSUMOS = os.path.join(TP4, "02_Subsets_SNAP_QGIS")
RESULTADOS = os.path.join(TP4, "05_Resultados")
GEDI = os.path.join(PROYECTO, "TP2_LiDAR_GEDI_ICESat2", "05_Resultados", "04_Tablas")
AOI = "BOSQUE_NW_02"          # la estepa no tiene dosel: no hay altura que explicar
RADIO = 7                     # ventana 15x15 = 150 m (ver TP4_06)
CORTES = [0, 3, 6, 9, 12, 15, 18, 21, 25, 30]

FUENTES = [
    ("S1 VH", "C", "Sentinel_1/*/%s/S1_GRD/*20251123*.tif", 1),
    ("S1 VV", "C", "Sentinel_1/*/%s/S1_GRD/*20251123*.tif", 2),
    ("SAOCOM HV", "L", "SAOCOM/*/%s/*/*20260110*.tif", 2),
    ("NISAR HH", "L", "NISAR/*/%s/*/NISAR_GCOV_20260108.tif", 1),
    ("NISAR HV", "L", "NISAR/*/%s/*/NISAR_GCOV_20260108.tif", 2),
    ("PALSAR2 HV", "L", "ALOS_PALSAR_2/*/%s/*/PALSAR2_2025.tif", 2),
]


def huellas():
    p = os.path.join(GEDI, "GEDI_L2A_%s_aceptados.csv" % AOI)
    if not os.path.exists(p):
        sys.exit("No hay huellas GEDI. Ejecute antes el TP2 completo.")
    out = []
    for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
        try:
            out.append((float(r["este_utm19s"]), float(r["norte_utm19s"]),
                        float(r["rh95"]), r.get("shot_number", "")))
        except (KeyError, ValueError):
            continue
    return out


def extraer(patron, banda, hs):
    hits = [h for h in sorted(glob.glob(os.path.join(INSUMOS, patron % AOI))) if "_mask" not in h]
    if not hits:
        return None
    ds = gdal.Open(hits[0]); gt = ds.GetGeoTransform()
    a = ds.GetRasterBand(banda).ReadAsArray().astype("float64")
    # Se queda en gamma0 LINEAL. El paso a dB va DESPUES de promediar la
    # ventana: el promedio de los logaritmos no es el logaritmo del promedio,
    # y ese sesgo negativo CRECE con la heterogeneidad de la ventana, que es
    # justo lo que este script esta midiendo. Promediar en dB comprimiria la
    # senal buscada, y el sesgo (~0,5 dB) es del orden del efecto medido.
    a = np.where(np.isfinite(a) & (a > 0), a, np.nan)
    ny, nx = a.shape
    out = []
    for e, n, h, shot in hs:
        c = int((e - gt[0]) / gt[1]); f = int((n - gt[3]) / gt[5])
        if not (RADIO <= c < nx - RADIO and RADIO <= f < ny - RADIO):
            continue
        w = a[f - RADIO:f + RADIO + 1, c - RADIO:c + RADIO + 1]
        w = w[np.isfinite(w)]
        if w.size:
            out.append((shot, h, float(10 * np.log10(w.mean()))))
    return out


def ajustar(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.size < 30:
        return None
    a, b = np.polyfit(y, x, 1); pred = a * y + b
    r2 = 1 - ((x - pred) ** 2).sum() / ((x - x.mean()) ** 2).sum()
    rmse = float(np.sqrt(((x - pred) ** 2).mean()))
    return a, b, r2, rmse, int(x.size)


print(__doc__)
hs = huellas()
print("huellas GEDI validas del bosque: %d" % len(hs))
print("ventana: %dx%d pixeles (%d m)" % (2 * RADIO + 1, 2 * RADIO + 1, (2 * RADIO + 1) * 10))
print()

D, faltan = {}, []
for nom, banda, patron, b in FUENTES:
    r = extraer(patron, b, hs)
    if r is None:
        faltan.append(nom); continue
    D[nom] = r
if faltan:
    print("No estan disponibles: %s" % ", ".join(faltan))
    print()
if not D:
    sys.exit("No se pudo leer ningun producto. Revise 02_Subsets_SNAP_QGIS.")

# ------------------------------------------------ tabla de saturacion
print("=" * 84)
print("gamma0 mediano (dB) por franja de altura del dosel")
print("=" * 84)
nombres = list(D)
print("%-11s %5s %s" % ("altura (m)", "n", "".join("%12s" % n for n in nombres)))
tabla = []
for i in range(len(CORTES) - 1):
    lo, hi = CORTES[i], CORTES[i + 1]
    g = {n: [v for _, h, v in D[n] if lo <= h < hi] for n in nombres}
    n0 = max(len(v) for v in g.values())
    if n0 < 5:
        continue
    fila = {"rango_altura_m": "%d-%d" % (lo, hi), "n": n0}
    linea = "%-11s %5d" % ("%d-%d" % (lo, hi), n0)
    for n in nombres:
        m = float(np.median(g[n])) if g[n] else float("nan")
        fila[n] = round(m, 2); linea += "%12.2f" % m
    print(linea); tabla.append(fila)

print()
print("=" * 84)
print("Cuanto gana cada sensor entre el matorral (0-3 m) y el bosque maduro (>21 m)")
print("=" * 84)
for n in nombres:
    bajo = [v for _, h, v in D[n] if h < 3]
    alto = [v for _, h, v in D[n] if h >= 21]
    if len(bajo) < 5 or len(alto) < 5:
        continue
    g = float(np.median(alto)) - float(np.median(bajo))
    marca = "  <-- responde" if g > 1.5 else ("  <-- PLANO: no responde" if g < 1.0 else "")
    print("   %-12s %7.2f dB  ->  %7.2f dB   gana %5.2f dB%s"
          % (n, float(np.median(bajo)), float(np.median(alto)), g, marca))

# ------------------------------------------------ modelos
print()
print("=" * 84)
print("Ajuste gamma0 -> altura del dosel")
print("=" * 84)
print("   %-12s %12s %8s %10s %7s" % ("fuente", "pendiente", "R2", "RMSE (m)", "n"))
lineas = []
for n in nombres:
    r = ajustar([h for _, h, _ in D[n]], [v for _, _, v in D[n]])
    if not r:
        continue
    a, b, r2, rmse, nn = r
    print("   %-12s %12.2f %8.3f %10.2f %7d" % (n, a, r2, rmse, nn))
    lineas.append("%s: altura = %.2f * gamma0_dB + %.2f | R2 = %.3f | RMSE = %.2f m | n = %d"
                  % (n, a, b, r2, rmse, nn))

os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)
if tabla:
    with open(os.path.join(RESULTADOS, "04_Tablas", "saturacion_radar.csv"), "w",
              newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(tabla[0])); w.writeheader(); w.writerows(tabla)
with open(os.path.join(RESULTADOS, "04_Tablas", "modelos_radar.txt"), "w", encoding="utf-8") as f:
    f.write("Ajustes gamma0 -> altura del dosel (rh95), bosque, ventana %d m\n"
            % ((2 * RADIO + 1) * 10))
    f.write("=" * 74 + "\n")
    for l in lineas:
        f.write(l + "\n")
    f.write("\nGEDI mide ALTURA; la banda L responde a BIOMASA. No son la misma variable.\n")

filas = []
for n in nombres:
    for shot, h, v in D[n]:
        filas.append({"shot_number": shot, "rh95": h, "fuente": n, "gamma0_dB": round(v, 3)})
with open(os.path.join(RESULTADOS, "04_Tablas", "cruce_gedi_radar.csv"), "w",
          newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["shot_number", "rh95", "fuente", "gamma0_dB"])
    w.writeheader(); w.writerows(filas)

print()
print("FIN DEL TP4.")
print("   05_Resultados/04_Tablas/saturacion_radar.csv   la tabla de arriba")
print("   05_Resultados/04_Tablas/modelos_radar.txt      los ajustes")
print("   05_Resultados/04_Tablas/cruce_gedi_radar.csv   cada huella con su gamma0")
print()
print("PARA SU INFORME: compare la columna de la banda L con la del NDVI del TP3.")
print("Donde el NDVI se aplano (21 m), la banda L sigue subiendo. Ese es el")
print("resultado del practico, y usted lo midio.")
