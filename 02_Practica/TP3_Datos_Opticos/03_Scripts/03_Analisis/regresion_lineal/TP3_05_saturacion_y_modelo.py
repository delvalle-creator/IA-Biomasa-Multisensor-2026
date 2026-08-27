#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP3_05_saturacion_y_modelo.py   ---> QUINTO y ultimo script del TP3.

QUE HACE
--------
Cruza los indices opticos con la referencia GEDI del TP2, ajusta un modelo
simple de altura del dosel y MIDE DONDE SATURA cada indice. Este ultimo punto
es la conclusion del practico.

POR QUE ESTE SCRIPT ES EL MAS IMPORTANTE DEL TP3
------------------------------------------------
Hasta aqui el practico calculo indices. Pero un indice no es biomasa: hay que
demostrar que se relaciona con la estructura real del bosque, y sobre todo hay
que averiguar HASTA DONDE sirve. Eso se hace enfrentandolo a una medida
independiente: las huellas GEDI que el TP2 dejo filtradas.

COMO SE CRUZAN DOS COSAS TAN DISTINTAS
--------------------------------------
GEDI son puntos: huellas de 25 m con una altura medida. Los indices son un
raster continuo de 10 m. Para cruzarlos, por cada huella GEDI se toma el valor
del indice en una ventana de 3x3 pixeles (30x30 m) centrada en ella, y se
promedia. Esa ventana se aproxima al tamano de la huella.

Ojo con una cosa: se usan los indices PRE-INCENDIO, porque GEDI es de sep. 2024
a mar. 2025, es decir, del bosque en pie. Cruzar GEDI con la imagen post-incendio
no tendria ningun sentido: se estaria comparando la altura de arboles que ya no
existen.

QUE ES LA SATURACION Y COMO SE MIDE AQUI
----------------------------------------
Un indice optico mira el DOSEL. Mientras el dosel esta abierto, si crece la
vegetacion el indice sube. Pero cuando el dosel se cierra del todo, lo que haya
DEBAJO deja de verse: el arbol puede seguir engrosando su tronco y acumulando
biomasa, y el indice ya no cambia. El indice SATURA.

Para medirlo, el script agrupa las huellas por altura y calcula el indice mediano
en cada grupo. Si el indice sigue subiendo con la altura, no satura. Si se
aplana a partir de cierta altura, ahi satura. El resultado es un numero concreto
que el estudiante puede citar en su informe.

Esa saturacion es la razon de ser del TP4: el radar de banda L penetra el dosel
y llega a los troncos, de modo que sigue respondiendo cuando el optico ya no.

ENTRADA   05_Resultados/02_Rasters/indices/02_pre/<AOI>/*.tif  (del TP3_03)
          ../TP2_LiDAR_GEDI_ICESat2/04_Tablas_de_trabajo/01_Bosque | 02_Estepa/*_validos*.csv
SALIDA    05_Resultados/04_Tablas/cruce_gedi_indices.csv
          05_Resultados/04_Tablas/saturacion.csv
          05_Resultados/04_Tablas/modelo_altura.txt

USO (entorno conda 'aoi'):   python TP3_05_saturacion_y_modelo.py
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
TP3 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROYECTO = os.path.dirname(TP3)
TP2 = os.path.join(PROYECTO, "TP2_LiDAR_GEDI_ICESat2")
sys.path.insert(0, os.path.join(PROYECTO, "00_COMUN"))

gdal.UseExceptions()
RESULTADOS = os.path.join(TP3, "05_Resultados")
VENTANA = 1          # 1 = 3x3 pixeles (30x30 m), parecido a la huella GEDI
INDICES = ["NDVI", "EVI", "NDMI", "NBR"]


class Cubo:
    """Lee los cuatro indices y permite consultarlos en una coordenada."""

    def __init__(self, ruta):
        ds = gdal.Open(ruta)
        self.gt = ds.GetGeoTransform()
        self.arr = {}
        for i in range(1, ds.RasterCount + 1):
            b = ds.GetRasterBand(i)
            self.arr[b.GetDescription()] = b.ReadAsArray().astype("float32")
        self.ny, self.nx = list(self.arr.values())[0].shape

    def en(self, este, norte, nombre):
        col = int((este - self.gt[0]) / self.gt[1])
        fil = int((norte - self.gt[3]) / self.gt[5])
        c0, c1 = max(0, col - VENTANA), min(self.nx, col + VENTANA + 1)
        f0, f1 = max(0, fil - VENTANA), min(self.ny, fil + VENTANA + 1)
        if c0 >= c1 or f0 >= f1:
            return float("nan")
        v = self.arr[nombre][f0:f1, c0:c1]
        v = v[np.isfinite(v)]
        return float(v.mean()) if v.size else float("nan")


# Carpetas reales que produce el TP2_05 (una por sitio). El nombre lo fija ese
# script; no se arma a mano.
SUBSET_DE_SITIO = {"Bosque": "01_Bosque", "Estepa": "02_Estepa"}


def cargar_gedi(sitio):
    p = os.path.join(TP2, "04_Tablas_de_trabajo", SUBSET_DE_SITIO[sitio], "*_validos*.csv")
    hits = sorted(glob.glob(p))
    if not hits:
        print("   AVISO: no hay huellas validas en %s." % os.path.dirname(p))
        print("   Ejecute antes, en el TP2:  TP2_05_filtrar_pendiente.py"
              " y TP2_06_metricas_estructura.py")
        return []
    # se prefiere el que ya tiene estructura (salida del TP2_06)
    ruta = next((h for h in hits if "con_estructura" in h), hits[0])
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ajustar(x, y):
    """Regresion lineal simple por minimos cuadrados. Devuelve (a, b, r2, n)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if x.size < 10:
        return None
    a, b = np.polyfit(x, y, 1)          # y = a*x + b
    pred = a * x + b
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")
    rmse = float(np.sqrt(((y - pred) ** 2).mean()))
    return a, b, r2, rmse, int(x.size)


print(__doc__)
filas = []
for sitio, aoi in (("Bosque", "BOSQUE_NW_02"), ("Estepa", "ESTEPA_NW_02")):
    print("=" * 72)
    print(sitio)
    print("=" * 72)
    # "02_pre*" con comodin: la carpeta real se llama 02_pre_incendio_2025_26,
    # que es la que escribe TP3_03_indices.py. Corregido el 29/07/2026.
    tifs = sorted(glob.glob(os.path.join(RESULTADOS, "02_Rasters", "indices",
                                         "02_pre*", aoi, "*.tif")))
    if not tifs:
        print("   faltan los indices. Ejecute antes:  python TP3_03_indices.py")
        continue
    cubo = Cubo(tifs[-1])              # la escena pre-incendio mas cercana al fuego
    print("   indices: %s" % os.path.basename(tifs[-1]))
    gedi = cargar_gedi(sitio)
    if not gedi:
        print("   faltan los footprints GEDI. Ejecute antes el TP2 completo.")
        continue
    print("   huellas GEDI: %d" % len(gedi))
    n = 0
    for g in gedi:
        try:
            e, no = float(g["este_utm19s"]), float(g["norte_utm19s"])
            h = float(g["rh95"])
        except (KeyError, ValueError):
            continue
        fila = {"sitio": sitio, "shot": g.get("shot_number", ""),
                "este": e, "norte": no, "rh95": h,
                "cover": g.get("cover", ""), "pai": g.get("pai", "")}
        ok = True
        for k in INDICES:
            v = cubo.en(e, no, k)
            fila[k] = v
            if not np.isfinite(v):
                ok = False
        if ok:
            filas.append(fila); n += 1
    print("   cruzadas con indice valido: %d" % n)
    print()

if not filas:
    sys.exit("No se pudo cruzar nada. Revise que el TP2 y el TP3_03 hayan corrido.")

os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)
with open(os.path.join(RESULTADOS, "04_Tablas", "cruce_gedi_indices.csv"),
          "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)

# ------------------------- modelo: indice -> altura -------------------------
print("=" * 72)
print("MODELO SIMPLE: el indice explica la altura del dosel?")
print("=" * 72)
print("   %-6s %10s %10s %10s %8s" % ("indice", "pendiente", "R2", "RMSE (m)", "n"))
lineas = []
for k in INDICES:
    r = ajustar([f[k] for f in filas], [f["rh95"] for f in filas])
    if r:
        a, b, r2, rmse, nn = r
        print("   %-6s %10.2f %10.3f %10.2f %8d" % (k, a, r2, rmse, nn))
        lineas.append("%s: altura = %.2f * %s + %.2f | R2 = %.3f | RMSE = %.2f m | n = %d"
                      % (k, a, k, b, r2, rmse, nn))
with open(os.path.join(RESULTADOS, "04_Tablas", "modelo_altura.txt"), "w",
          encoding="utf-8") as f:
    f.write("Modelos lineales indice -> altura del dosel (rh95), datos pre-incendio\n")
    f.write("=" * 70 + "\n")
    for l in lineas:
        f.write(l + "\n")

# ------------------------- saturacion -------------------------
print()
print("=" * 72)
print("SATURACION: hasta que altura responde cada indice?")
print("=" * 72)
bosque = [f for f in filas if f["sitio"] == "Bosque"]
cortes = [0, 3, 6, 9, 12, 15, 18, 21, 25, 30, 40]
sat = []
print("   %-12s %6s %8s %8s %8s %8s" % ("altura (m)", "n", "NDVI", "EVI", "NDMI", "NBR"))
for i in range(len(cortes) - 1):
    lo, hi = cortes[i], cortes[i + 1]
    g = [f for f in bosque if lo <= f["rh95"] < hi]
    if len(g) < 5:
        continue
    fila = {"rango_altura_m": "%d-%d" % (lo, hi), "n": len(g)}
    out = "   %-12s %6d" % ("%d-%d" % (lo, hi), len(g))
    for k in INDICES:
        m = float(np.median([f[k] for f in g]))
        fila[k] = round(m, 3)
        out += " %8.3f" % m
    print(out)
    sat.append(fila)
if sat:
    with open(os.path.join(RESULTADOS, "04_Tablas", "saturacion.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sat[0])); w.writeheader(); w.writerows(sat)

    print()
    print("COMO SE LEE ESTA TABLA:")
    print("   Baje por la columna del NDVI. Mientras los arboles son bajos, el")
    print("   NDVI sube. A partir de cierta altura DEJA DE SUBIR aunque los")
    print("   arboles sigan creciendo: ahi satura. Compare con el EVI, que")
    print("   deberia aguantar un poco mas.")
    print()
    print("   Ese techo es la limitacion del optico, y es la razon por la que")
    print("   el TP4 usa radar de banda L: penetra el dosel y llega a los troncos.")

print()
print("FIN DEL TP3.")
print("   05_Resultados/04_Tablas/cruce_gedi_indices.csv   cada huella con sus indices")
print("   05_Resultados/04_Tablas/modelo_altura.txt        los modelos ajustados")
print("   05_Resultados/04_Tablas/saturacion.csv           donde satura cada indice")
