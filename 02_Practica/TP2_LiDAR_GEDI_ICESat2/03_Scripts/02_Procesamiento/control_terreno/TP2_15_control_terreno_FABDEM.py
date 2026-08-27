# -*- coding: utf-8 -*-
"""
TP2_15_control_terreno_FABDEM.py  ---> audita el terreno de ATL08 (y de GEDI)
                                       contra un suelo desnudo independiente.

POR QUE HACIA FALTA
-------------------
El cotejo del paso 13 mostro que ATL08 da el dosel mas alto que GEDI: 2,70
veces en el bosque y 3,28 en la estepa. Antes de discutir el dosel hay que
auditar el piso: h_canopy es una diferencia contra el terreno que el propio
ATL08 detecto, y si ese terreno esta mal, la altura del dosel hereda el error
completo. Lo mismo vale para GEDI: elev_lowestmode es el suelo que GEDI creyo
ver. Ninguna de las dos misiones puede auditarse a si misma.

FABDEM (Univ. de Bristol) es un modelo de elevacion GLOBAL de 30 m construido
sobre el Copernicus GLO-30 al que se le removieron bosques y edificios con
aprendizaje automatico: un "suelo desnudo" independiente de ambas misiones.
No es verdad de campo -- es otro modelo, como el CCI del anexo del TP2 -- pero
es un arbitro externo, y eso alcanza para DETECTAR terrenos mal medidos.

FABDEM AUDITA: NUNCA SE RESTA A LA ALTURA. Un segmento que falla el control se
descarta con criterio declarado; no se "corrige" con FABDEM, porque seria
mezclar la fisica de dos instrumentos distintos en una misma cifra.

EL DATUM VERTICAL, O POR QUE APARECEN LOS GEOIDES
-------------------------------------------------
Las alturas satelitales (h_te_best_fit de ATL08, elev_lowestmode de GEDI) son
ELIPSOIDALES: metros sobre el elipsoide WGS84. FABDEM es ORTOMETRICO: metros
sobre el geoide EGM2008, como las cotas de un mapa. Comparar sin convertir
seria un error de ~20 m aca (la ondulacion N del geoide en el AOI). Se lleva
todo al elipsoide:

    delta = h_satelital - (FABDEM + N)          con N del geoide EGM2008

Se calcula ademas N del GEOIDE-Ar16 (la realizacion del sistema vertical
argentino SRVN16, IGN). En este AOI ambos geoides difieren en menos de medio
metro: la conclusion no depende de cual se use, y ESO tambien queda declarado.

EL CRITERIO, DECLARADO
----------------------
    |delta| <= 5 m  ->  el segmento PASA; su terreno es compatible con FABDEM
    |delta| >  5 m  ->  DESCARTADO del re-cotejo del paso 16

5 m combina el error nominal de FABDEM en bosque (~2,5 m RMSE, Hawker et al.
2022) con la incertidumbre del propio h_te en 100 m de ladera. El log informa
la sensibilidad con 3 y con 10 m: el veredicto del paso 16 no cambia.

GEDI pasa por el MISMO control pero no se filtra: es la referencia del curso y
el resultado del control (mediana +0,2 m en bosque, +0,5 m en estepa) es parte
del veredicto, no un paso previo.

ENTRADA   00_COMUN/03_Topografia/FABDEM/fabdem_<RECINTO>_wgs84.tif
          00_COMUN/03_Topografia/GEOIDES/geoide_egm2008_AOI.tif  (+ Ar16)
          04_Tablas_de_trabajo/06_ICESat2/ATL08_<RECINTO>_<nivel>_utm.csv
          04_Tablas_de_trabajo/0{1,2}_*/GEDI_<RECINTO>_validos_con_estructura.csv

SALIDA    04_Tablas_de_trabajo/06_ICESat2/ATL08_<RECINTO>_<nivel>_terreno_utm.csv
          05_Resultados/04_Tablas/TP2_control_terreno_ATL08_<RECINTO>_<nivel>.csv
          05_Resultados/04_Tablas/TP2_control_terreno_GEDI_<RECINTO>.csv
          05_Resultados/06_Control_calidad/ICESat2_ATL08/TP2_15_control_terreno.log

Los archivos de entrada NO se tocan. Todo sale con nombre nuevo.

USO (entorno conda 'aoi'):   python TP2_15_control_terreno_FABDEM.py
"""
import csv
import math
import os
import statistics as est
import sys

import numpy as np
import rasterio

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
COMUN = os.path.abspath(os.path.join(TP2, "..", "00_COMUN"))
TOPO = os.path.join(COMUN, "03_Topografia")
ATL08 = os.path.join(TP2, "04_Tablas_de_trabajo", "06_ICESat2")
TABLAS = os.path.join(TP2, "05_Resultados", "04_Tablas")
CONTROL = os.path.join(TP2, "05_Resultados", "06_Control_calidad", "ICESat2_ATL08")

GEDI_POR_RECINTO = {
    "BOSQUE_NW_02": os.path.join(TP2, "04_Tablas_de_trabajo", "01_Bosque",
                                 "GEDI_BOSQUE_NW_02_validos_con_estructura.csv"),
    "ESTEPA_NW_02": os.path.join(TP2, "04_Tablas_de_trabajo", "02_Estepa",
                                 "GEDI_ESTEPA_NW_02_validos_con_estructura.csv"),
}

UMBRAL = 5.0          # metros; el criterio declarado de arriba
SENSIBILIDAD = (3.0, 5.0, 10.0)
NIVELES = ("operacional", "conservador")


# ------------------------------------------------------------------ AUXILIARES
def a_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def leer(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def escribir(ruta, filas, campos):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)


class Raster(object):
    """Un GeoTIFF en memoria con muestreo bilineal en lon/lat.

    La interpolacion bilineal pondera las 4 celdas vecinas: es la manera
    estandar de leer un raster continuo (elevacion, geoide) en un punto que
    no cae justo en el centro de un pixel. Si alguna vecina es nodata, el
    punto se declara sin muestra en lugar de inventar un valor.
    """

    def __init__(self, ruta):
        with rasterio.open(ruta) as d:
            self.arr = d.read(1).astype(float)
            self.t = d.transform
            self.nodata = d.nodata if d.nodata is not None else -9999.0

    def muestra(self, lon, lat):
        col = (lon - self.t.c) / self.t.a - 0.5
        fil = (lat - self.t.f) / self.t.e - 0.5
        c0, f0 = int(math.floor(col)), int(math.floor(fil))
        if c0 < 0 or f0 < 0 or c0 + 1 >= self.arr.shape[1] or f0 + 1 >= self.arr.shape[0]:
            return None
        v = self.arr[f0:f0 + 2, c0:c0 + 2]
        if np.isnan(v).any() or (v == self.nodata).any():
            return None
        wc, wf = col - c0, fil - f0
        return float(v[0, 0] * (1 - wc) * (1 - wf) + v[0, 1] * wc * (1 - wf)
                     + v[1, 0] * (1 - wc) * wf + v[1, 1] * wc * wf)


def resumen(valores):
    if not valores:
        return None
    s = sorted(valores)
    med = est.median(s)
    return {"n": len(s), "mediana": med,
            "mad": est.median([abs(v - med) for v in s]),
            "p5": s[max(0, int(0.05 * len(s)) - 1)],
            "p95": s[min(len(s) - 1, int(0.95 * len(s)))]}


def porcentaje_sobre(valores, umbral):
    if not valores:
        return 0.0
    return 100.0 * sum(1 for v in valores if abs(v) > umbral) / len(valores)


# ----------------------------------------------------------------------- CUERPO
def main():
    os.makedirs(TABLAS, exist_ok=True)
    os.makedirs(CONTROL, exist_ok=True)
    lineas = []

    def decir(s=""):
        lineas.append(s)
        print(s)

    decir("CONTROL DE TERRENO CONTRA FABDEM (suelo desnudo, 30 m)")
    decir("delta = h_satelital(elipsoidal WGS84) - (FABDEM + N_EGM2008)")
    decir("criterio declarado: |delta| <= %.0f m pasa; se informa 3 y 10 m" % UMBRAL)
    decir("")

    geo_egm = Raster(os.path.join(TOPO, "GEOIDES", "geoide_egm2008_AOI.tif"))
    geo_ar16 = Raster(os.path.join(TOPO, "GEOIDES", "geoide_ar16_AOI.tif"))

    for recinto in ("BOSQUE_NW_02", "ESTEPA_NW_02"):
        fabdem = Raster(os.path.join(TOPO, "FABDEM", "fabdem_%s_wgs84.tif" % recinto))

        # --- los dos geoides difieren en centimetros: se declara y se sigue ---
        difs = []
        for x in leer(GEDI_POR_RECINTO[recinto])[::25]:
            lon, lat = a_float(x.get("lon")), a_float(x.get("lat"))
            if lon is None:
                continue
            a, b = geo_egm.muestra(lon, lat), geo_ar16.muestra(lon, lat)
            if a is not None and b is not None:
                difs.append(a - b)
        if difs:
            decir("%s: N_EGM2008 - N_Ar16 = %+.2f m (mediana); la eleccion del"
                  % (recinto, est.median(difs)))
            decir("   geoide no cambia el control (umbral de %.0f m)." % UMBRAL)

        # ------------------------------------------------------ ATL08, por nivel
        for nivel in NIVELES:
            nombre = "ATL08_%s_%s_utm.csv" % (recinto, nivel)
            filas = leer(os.path.join(ATL08, nombre))
            campos = list(filas[0].keys()) + ["fabdem_m", "n_egm2008_m",
                                              "n_geoide_ar16_m",
                                              "delta_terreno_m", "control_terreno"]
            todas, pasan, deltas = [], [], []
            sin_muestra = 0
            for x in filas:
                lon = a_float(x.get("longitude"))
                lat = a_float(x.get("latitude"))
                hte = a_float(x.get("h_te_best_fit_m"))
                fv = geo = ar = delta = None
                if None not in (lon, lat, hte):
                    fv = fabdem.muestra(lon, lat)
                    geo = geo_egm.muestra(lon, lat)
                    ar = geo_ar16.muestra(lon, lat)
                    if fv is not None and geo is not None:
                        delta = hte - (fv + geo)
                x = dict(x)
                x["fabdem_m"] = "%.2f" % fv if fv is not None else ""
                x["n_egm2008_m"] = "%.3f" % geo if geo is not None else ""
                x["n_geoide_ar16_m"] = "%.3f" % ar if ar is not None else ""
                x["delta_terreno_m"] = "%.2f" % delta if delta is not None else ""
                if delta is None:
                    x["control_terreno"] = "SIN_MUESTRA"
                    sin_muestra += 1
                elif abs(delta) <= UMBRAL:
                    x["control_terreno"] = "PASA"
                    pasan.append(x)
                    deltas.append(delta)
                else:
                    x["control_terreno"] = "DESCARTADO"
                    deltas.append(delta)
                todas.append(x)

            escribir(os.path.join(TABLAS, "TP2_control_terreno_ATL08_%s_%s.csv"
                                  % (recinto, nivel)), todas, campos)
            escribir(os.path.join(ATL08, "ATL08_%s_%s_terreno_utm.csv"
                                  % (recinto, nivel)), pasan, campos)

            r = resumen(deltas)
            decir("")
            decir("ATL08 %s %s" % (recinto, nivel))
            decir("   %d segmentos, %d sin muestra FABDEM" % (len(todas), sin_muestra))
            decir("   delta: mediana %+.2f m, MAD %.2f, p5 %+.2f, p95 %+.2f"
                  % (r["mediana"], r["mad"], r["p5"], r["p95"]))
            decir("   sensibilidad: " + "  ".join(
                "|d|>%.0fm: %.1f%%" % (u, porcentaje_sobre(deltas, u))
                for u in SENSIBILIDAD))
            decir("   PASAN %d de %d (%.1f%%)  ->  %s"
                  % (len(pasan), len(todas), 100.0 * len(pasan) / len(todas),
                     "ATL08_%s_%s_terreno_utm.csv" % (recinto, nivel)))

        # ------------------------------------------------- GEDI: control, no filtro
        filas = leer(GEDI_POR_RECINTO[recinto])
        campos = ["shot_number", "lat", "lon", "elev_lowestmode", "fabdem_m",
                  "n_egm2008_m", "delta_terreno_m", "control_terreno"]
        salida, deltas = [], []
        for x in filas:
            lon, lat = a_float(x.get("lon")), a_float(x.get("lat"))
            el = a_float(x.get("elev_lowestmode"))
            fv = geo = delta = None
            if None not in (lon, lat, el):
                fv = fabdem.muestra(lon, lat)
                geo = geo_egm.muestra(lon, lat)
                if fv is not None and geo is not None:
                    delta = el - (fv + geo)
            fila = {"shot_number": x.get("shot_number", ""),
                    "lat": x.get("lat", ""), "lon": x.get("lon", ""),
                    "elev_lowestmode": x.get("elev_lowestmode", ""),
                    "fabdem_m": "%.2f" % fv if fv is not None else "",
                    "n_egm2008_m": "%.3f" % geo if geo is not None else "",
                    "delta_terreno_m": "%.2f" % delta if delta is not None else "",
                    "control_terreno": ("PASA" if delta is not None
                                        and abs(delta) <= UMBRAL else
                                        "FUERA_DE_UMBRAL" if delta is not None
                                        else "SIN_MUESTRA")}
            if delta is not None:
                deltas.append(delta)
            salida.append(fila)
        escribir(os.path.join(TABLAS, "TP2_control_terreno_GEDI_%s.csv" % recinto),
                 salida, campos)
        r = resumen(deltas)
        decir("")
        decir("GEDI %s (control informativo: la referencia NO se filtra)" % recinto)
        decir("   %d huellas con muestra" % r["n"])
        decir("   delta: mediana %+.2f m, MAD %.2f, p5 %+.2f, p95 %+.2f"
              % (r["mediana"], r["mad"], r["p5"], r["p95"]))
        decir("   sensibilidad: " + "  ".join(
            "|d|>%.0fm: %.1f%%" % (u, porcentaje_sobre(deltas, u))
            for u in SENSIBILIDAD))
        decir("")

    decir("COMO SE LEE ESTO")
    decir("   FABDEM no es verdad de campo: es otro modelo. Por eso audita y")
    decir("   filtra, pero jamas corrige: ninguna altura se toca. El paso 16")
    decir("   repite el cotejo del paso 13 solo con los segmentos que PASAN.")
    decir("   Si la mediana del delta esta cerca de cero, el datum vertical")
    decir("   quedo bien llevado: un error de geoide se veria como un salto")
    decir("   de ~20 m, no de centimetros.")

    with open(os.path.join(CONTROL, "TP2_15_control_terreno.log"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
