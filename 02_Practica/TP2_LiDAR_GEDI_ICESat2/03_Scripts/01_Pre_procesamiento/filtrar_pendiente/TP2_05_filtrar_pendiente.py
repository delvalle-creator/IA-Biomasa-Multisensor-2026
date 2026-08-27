#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_05_filtrar_pendiente.py   ---> QUINTO script del TP2.

QUE HACE
--------
De los disparos que aprobaron el filtro de calidad (TP2_03), descarta los que
caen en pendiente fuerte. Como siempre, guarda los descartados con su motivo.

POR QUE LA PENDIENTE ARRUINA LA ALTURA DEL DOSEL
------------------------------------------------
GEDI ilumina un circulo de unos 25 m y mide el tiempo que tarda en volver la
energia. En terreno llano, lo primero que vuelve es la copa y lo ultimo el
suelo: la diferencia es la altura del arbol.

En una ladera, el suelo del extremo de arriba de la huella esta varios metros
mas alto que el del extremo de abajo. Con 25 m de huella y 30 grados de
pendiente, esa diferencia es de unos 14 metros. El retorno del suelo se estira
en el tiempo y se mezcla con el de la vegetacion. El algoritmo interpreta como
"copa" lo que en realidad es suelo inclinado, y la altura sale SOBRESTIMADA, a
veces por varios metros.

El umbral que se aplica aqui es de 20 grados, un valor conservador y de uso
habitual en la literatura de GEDI en terreno montanoso. En un bosque andino esto
importa mucho: buena parte del AOI de bosque esta en ladera.

COMO SE HACE
------------
Para cada disparo se lee la pendiente del pixel del DEM en el que cae (su
coordenada UTM ya viene en el CSV). No se interpola: se toma el valor del pixel,
porque la pendiente es una propiedad del terreno en ese punto.

ENTRADA   05_Resultados/04_Tablas/*_aceptados.csv   (salida del TP2_03)
          00_COMUN/03_Topografia/pendiente/pendiente_<AOI>.tif  (salida del TP2_04)
SALIDA    04_Tablas_de_trabajo/01_Bosque | 02_Estepa/*.csv   <- LOS DEFINITIVOS
          05_Resultados/04_Tablas/*_pendiente.csv
          05_Resultados/06_Control_calidad/filtrado_pendiente.csv

USO (entorno conda 'aoi'):   python TP2_05_filtrar_pendiente.py
"""
import csv
import glob
import math
import os
import sys

try:
    import numpy as np
    from osgeo import gdal
except ImportError:
    sys.exit("Falta numpy o GDAL. Active el entorno conda 'aoi'.")

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROYECTO = os.path.dirname(TP2)
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

from configuracion_comun import TOPOGRAFIA

gdal.UseExceptions()

RESULTADOS = os.path.join(TP2, "05_Resultados")
SUBSETS = os.path.join(TP2, "04_Tablas_de_trabajo")

PENDIENTE_MAXIMA = 20.0        # grados


class Raster:
    """Lee el valor de un raster en una coordenada UTM, sin interpolar."""

    # Media huella de GEDI: 12,5 m. Con pixel de 10 m, una ventana de 3x3 (30 m)
    # es la que mejor se aproxima al circulo de 25 m que ilumina el laser.
    RADIO = 1

    def __init__(self, ruta):
        self.ds = gdal.Open(ruta)
        self.gt = self.ds.GetGeoTransform()
        self.banda = self.ds.GetRasterBand(1)
        self.arr = self.banda.ReadAsArray().astype("float64")
        self.ny, self.nx = self.arr.shape
        # El relleno de gdaldem es -9999. Si no se lo saca, una pendiente de
        # -9999 grados pasa el filtro "p > 20" como si fuera terreno llano, y
        # ademas contamina la mediana que se informa como control de calidad.
        nod = self.banda.GetNoDataValue()
        malo = ~np.isfinite(self.arr) | (self.arr < -1000.0)
        if nod is not None:
            malo |= (self.arr == nod)
        self.arr[malo] = np.nan

    def valor(self, este, norte):
        """Pendiente REPRESENTATIVA de la huella, no la del pixel del centro.

        Lo que estira la forma de onda no es la inclinacion en un punto sino el
        DESNIVEL dentro del circulo de 25 m: en una ladera de 30 grados son unos
        14 m entre el borde de arriba y el de abajo, comparables a la altura del
        arbol que se quiere medir. Tomar el pixel del centro puede caer en un
        rellano dentro de una ladera quebrada y dejar pasar la huella. Se toma el
        MAXIMO de la ventana, que es el criterio conservador.

        math.floor y no int(): int() trunca hacia cero, de modo que un punto
        apenas al oeste o al norte del raster daria columna 0 y se leeria el
        borde en vez de rechazarse.
        """
        col = int(math.floor((este - self.gt[0]) / self.gt[1]))
        fil = int(math.floor((norte - self.gt[3]) / self.gt[5]))
        if not (0 <= col < self.nx and 0 <= fil < self.ny):
            return None
        r = self.RADIO
        v = self.arr[max(0, fil - r):fil + r + 1, max(0, col - r):col + r + 1]
        v = v[np.isfinite(v)]
        return float(v.max()) if v.size else None


def procesar(ruta_csv):
    base = os.path.basename(ruta_csv)
    aoi = "BOSQUE_NW_02" if "BOSQUE" in base else "ESTEPA_NW_02"
    etiqueta = "Bosque" if "BOSQUE" in base else "Estepa"

    rpend = os.path.join(TOPOGRAFIA, "pendiente", "pendiente_%s.tif" % aoi)
    if not os.path.exists(rpend):
        print("   FALTA la pendiente: %s" % rpend)
        print("   Ejecute antes:  python TP2_04_dem_y_pendiente.py")
        return None
    pend = Raster(rpend)

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        print("   sin disparos que procesar")
        return None

    validos, descartados = [], []
    for fila in filas:
        e = float(fila["este_utm19s"])
        n = float(fila["norte_utm19s"])
        p = pend.valor(e, n)
        fila = dict(fila)
        fila["pendiente_grados"] = "%.2f" % p if p is not None else ""
        if p is None:
            fila["motivo"] = "fuera del DEM"
            fila["detalle"] = "sin pendiente disponible"
            descartados.append(fila)
        elif p > PENDIENTE_MAXIMA:
            fila["motivo"] = "pendiente fuerte: la altura del dosel se sobrestima"
            fila["detalle"] = "pendiente=%.1f > %.0f grados" % (p, PENDIENTE_MAXIMA)
            descartados.append(fila)
        else:
            validos.append(fila)

    d_ok = os.path.join(SUBSETS, "01_Bosque" if etiqueta == "Bosque" else "02_Estepa")
    os.makedirs(d_ok, exist_ok=True)
    os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)

    sal_ok = os.path.join(d_ok, "GEDI_%s_validos.csv" % aoi)
    sal_no = os.path.join(RESULTADOS, "04_Tablas",
                          "GEDI_%s_descartados_pendiente.csv" % aoi)
    if validos:
        with open(sal_ok, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(validos[0]))
            w.writeheader(); w.writerows(validos)
    if descartados:
        with open(sal_no, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(descartados[0]))
            w.writeheader(); w.writerows(descartados)

    n = len(filas)
    ps = [float(f["pendiente_grados"]) for f in validos + descartados
          if f["pendiente_grados"]]
    ps.sort()
    print("   entraron (aprobaron calidad): %5d" % n)
    print("   VALIDOS (pendiente <= %.0f)   : %5d  (%.1f%%)"
          % (PENDIENTE_MAXIMA, len(validos), 100.0*len(validos)/n))
    print("   descartados por pendiente     : %5d  (%.1f%%)"
          % (len(descartados), 100.0*len(descartados)/n))
    if ps:
        print("   pendiente del AOI: mediana %.1f grados, maxima %.1f grados"
              % (ps[len(ps)//2], ps[-1]))
    return {"aoi": aoi, "entraron": n, "validos": len(validos),
            "descartados": len(descartados),
            "pend_mediana": ps[len(ps)//2] if ps else 0}


print(__doc__)
resumen = []
patron = os.path.join(RESULTADOS, "04_Tablas", "*_aceptados.csv")
archivos = sorted(glob.glob(patron))
if not archivos:
    sys.exit("No hay footprints aceptados.\nEjecute antes:  python TP2_03_filtrar_calidad.py")

for ruta in archivos:
    print("=" * 72)
    print(os.path.basename(ruta))
    print("=" * 72)
    r = procesar(ruta)
    if r:
        resumen.append(r)
    print()

if resumen:
    os.makedirs(os.path.join(RESULTADOS, "06_Control_calidad"), exist_ok=True)
    sal = os.path.join(RESULTADOS, "06_Control_calidad", "filtrado_pendiente.csv")
    with open(sal, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["aoi", "entraron_tras_calidad", "validos_finales",
                    "descartados_pendiente", "porcentaje_valido",
                    "pendiente_mediana_grados", "umbral_grados"])
        for r in resumen:
            w.writerow([r["aoi"], r["entraron"], r["validos"], r["descartados"],
                        "%.1f" % (100.0*r["validos"]/r["entraron"]),
                        "%.1f" % r["pend_mediana"], PENDIENTE_MAXIMA])
    print("Tabla -> 05_Resultados/06_Control_calidad/filtrado_pendiente.csv")

print()
print("Los footprints DEFINITIVOS quedaron en 04_Tablas_de_trabajo/01_Bosque | 02_Estepa/")
print("Son los que se usaran como referencia en el TP3, el TP4 y el TP5.")
print()
print("SIGUIENTE PASO:  python TP2_06_metricas_estructura.py")
