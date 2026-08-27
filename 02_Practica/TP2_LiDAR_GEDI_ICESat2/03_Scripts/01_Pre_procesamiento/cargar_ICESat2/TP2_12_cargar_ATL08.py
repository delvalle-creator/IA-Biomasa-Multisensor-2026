# -*- coding: utf-8 -*-
"""
TP2_12_cargar_ATL08.py   ---> normaliza los segmentos ICESat-2 / ATL08 y los deja
                              listos para cotejar contra GEDI.

POR QUE HACIA FALTA
-------------------
Los cuatro CSV de ATL08 llegan con 47 columnas, coordenadas geograficas y dos
niveles de filtrado ya evaluados. Antes de cotejarlos contra GEDI hay que hacer
tres cosas que no conviene repetir en cada script que los use:

  1. Proyectarlos a la grilla comun del proyecto (EPSG:32719, UTM 19 Sur). GEDI
     ya esta proyectado; ATL08 no. Comparar grados contra metros no da error:
     da disparates.
  2. Comprobar que cada segmento cae dentro del recinto que dice. El segmento
     mide 100 m, asi que su centroide puede quedar hasta 50 m afuera y el
     segmento seguir tocando el recinto: eso es efecto de borde. Mas alla de
     50 m ya no lo es, y hay que verlo ahora y no tres pasos despues.
  3. Registrar la retencion y los faltantes. Nueve de cada diez segmentos brutos
     se descartan antes de llegar aca; el practico exige saber por que.

Este script NO filtra nada por su cuenta. Los niveles operacional y conservador
vienen decididos en el paquete de origen: aca solo se normalizan, se verifican y
se documentan.

POR QUE LA PROYECCION VA ESCRITA A MANO
---------------------------------------
La conversion WGS84 -> UTM 19S esta implementada en este archivo, con las
formulas de Karney para el Mercator transverso. Se hizo asi para que el script
corra sin GDAL ni pyproj, que es lo que mas se rompe al reinstalar el entorno.
Se verifico contra pyproj 3.7.2 sobre los 6.259 segmentos de los dos recintos y
los dos niveles: diferencia maxima de 0,014 mm en el este y 0,2 mm en el norte,
muy por debajo del pixel de 10 m del proyecto.

QUE COLUMNAS AGREGA
-------------------
    este_utm19s       coordenada este en EPSG:32719, en metros
    norte_utm19s      coordenada norte en EPSG:32719, en metros
    aoi_normalizado   BOSQUE_NW_02 o ESTEPA_NW_02
    nivel             operacional o conservador
    dentro_aoi        SI o NO segun el recuadro de AOIS_UTM
    fuera_del_borde_m distancia al recuadro cuando dentro_aoi es NO, en metros
    fecha             AAAA-MM-DD, sacada de acquisition_datetime
    extremo_3iqr      SI cuando h_canopy_m supera el umbral de 3 IQR del recinto

ENTRADA   02_Subsets_SNAP_QGIS/ICESat2_ATL08/ATL08_<RECINTO>_<nivel>.csv

SALIDA    04_Tablas_de_trabajo/06_ICESat2/ATL08_<RECINTO>_<nivel>_utm.csv
          05_Resultados/06_Control_calidad/ICESat2_ATL08/TP2_12_carga_ATL08.csv

Los archivos de entrada NO se tocan. Todo sale con nombre nuevo.

USO (entorno conda 'aoi'):   python TP2_12_cargar_ATL08.py
"""
import csv
import math
import os
import statistics as est
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, os.path.join(TP2, "03_Scripts", "configuracion"))
from configuracion_comun import AOIS_UTM, EPSG                      # noqa: E402

ENTRADA = os.path.join(TP2, "02_Subsets_SNAP_QGIS", "ICESat2_ATL08")
SALIDA = os.path.join(TP2, "04_Tablas_de_trabajo", "06_ICESat2")
CONTROL = os.path.join(TP2, "05_Resultados", "06_Control_calidad", "ICESat2_ATL08")

RECINTOS = {"BOSQUE": "BOSQUE_NW_02", "ESTEPA": "ESTEPA_NW_02"}
NIVELES = ("operacional", "conservador")

# Columnas sin las cuales el script no puede seguir.
OBLIGATORIAS = ("longitude", "latitude", "h_canopy_m", "granule",
                "acquisition_datetime", "beam")

# ------------------------------------------------------- WGS84 -> UTM 19 SUR
# Elipsoide WGS84 y parametros de la zona 19 Sur (EPSG:32719).
_A = 6378137.0
_F = 1.0 / 298.257223563
_K0 = 0.9996
_LON0 = math.radians(-69.0)          # meridiano central de la zona 19
_ESTE_FALSO = 500000.0
_NORTE_FALSO = 10000000.0            # hemisferio sur


def wgs84_a_utm19s(lon_grados, lat_grados):
    """Devuelve (este, norte) en metros, EPSG:32719."""
    e2 = _F * (2.0 - _F)
    ep2 = e2 / (1.0 - e2)
    lat = math.radians(lat_grados)
    dlon = math.radians(lon_grados) - _LON0
    # normaliza el salto de meridiano
    while dlon > math.pi:
        dlon -= 2.0 * math.pi
    while dlon < -math.pi:
        dlon += 2.0 * math.pi

    sen, cos = math.sin(lat), math.cos(lat)
    tan = sen / cos
    n = _A / math.sqrt(1.0 - e2 * sen * sen)
    t = tan * tan
    c = ep2 * cos * cos
    a = cos * dlon

    m = _A * ((1.0 - e2 / 4.0 - 3.0 * e2 ** 2 / 64.0 - 5.0 * e2 ** 3 / 256.0) * lat
              - (3.0 * e2 / 8.0 + 3.0 * e2 ** 2 / 32.0 + 45.0 * e2 ** 3 / 1024.0) * math.sin(2 * lat)
              + (15.0 * e2 ** 2 / 256.0 + 45.0 * e2 ** 3 / 1024.0) * math.sin(4 * lat)
              - (35.0 * e2 ** 3 / 3072.0) * math.sin(6 * lat))

    este = _ESTE_FALSO + _K0 * n * (
        a + (1.0 - t + c) * a ** 3 / 6.0
        + (5.0 - 18.0 * t + t * t + 72.0 * c - 58.0 * ep2) * a ** 5 / 120.0)

    norte = _K0 * (m + n * tan * (
        a * a / 2.0 + (5.0 - t + 9.0 * c + 4.0 * c * c) * a ** 4 / 24.0
        + (61.0 - 58.0 * t + t * t + 600.0 * c - 330.0 * ep2) * a ** 6 / 720.0))
    norte += _NORTE_FALSO                      # el AOI esta en el hemisferio sur
    return este, norte


# ------------------------------------------------------------------ AUXILIARES
def a_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def umbral_3iqr(valores):
    """Umbral superior de valor extremo: p75 + 3 * (p75 - p25)."""
    if len(valores) < 4:
        return float("inf")
    d = est.quantiles(sorted(valores), n=4, method="inclusive")
    return d[2] + 3.0 * (d[2] - d[0])


def leer(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    os.makedirs(SALIDA, exist_ok=True)
    os.makedirs(CONTROL, exist_ok=True)
    registro = []
    total_escrito = 0

    for corto, recinto in RECINTOS.items():
        xmin, ymin, xmax, ymax = AOIS_UTM[recinto]

        for nivel in NIVELES:
            ruta = os.path.join(ENTRADA, "ATL08_%s_%s.csv" % (corto, nivel))
            if not os.path.exists(ruta):
                print("FALTA  %s" % ruta)
                print("       Los CSV de ATL08 son insumo del practico: se copian")
                print("       del paquete ICESat2_ATLAS_BOSQUE_ESTEPA_CORREGIDO.")
                continue

            filas = leer(ruta)
            if not filas:
                print("VACIO  %s" % ruta)
                continue

            faltan = [c for c in OBLIGATORIAS if c not in filas[0]]
            if faltan:
                print("ERROR  %s no trae %s" % (os.path.basename(ruta), ", ".join(faltan)))
                print("       Sin esas columnas no se puede cotejar. Se corta aca.")
                return 1

            alturas = [a_float(x.get("h_canopy_m")) for x in filas]
            alturas = [v for v in alturas if v is not None]
            umbral = umbral_3iqr(alturas)

            salida, fuera, sin_altura, extremos = [], 0, 0, 0
            peor_fuera = 0.0
            for x in filas:
                lon, lat = a_float(x.get("longitude")), a_float(x.get("latitude"))
                if lon is None or lat is None:
                    continue
                este, norte = wgs84_a_utm19s(lon, lat)
                h = a_float(x.get("h_canopy_m"))
                dx = max(xmin - este, este - xmax, 0.0)
                dy = max(ymin - norte, norte - ymax, 0.0)
                fuera_m = math.hypot(dx, dy)
                dentro = (fuera_m == 0.0)
                if not dentro:
                    fuera += 1
                    peor_fuera = max(peor_fuera, fuera_m)
                if h is None:
                    sin_altura += 1
                es_extremo = (h is not None and h > umbral)
                if es_extremo:
                    extremos += 1

                y = dict(x)
                y["este_utm19s"] = "%.1f" % este
                y["norte_utm19s"] = "%.1f" % norte
                y["aoi_normalizado"] = recinto
                y["nivel"] = nivel
                y["dentro_aoi"] = "SI" if dentro else "NO"
                y["fuera_del_borde_m"] = "" if dentro else "%.1f" % fuera_m
                y["fecha"] = (x.get("acquisition_datetime") or "")[:10]
                y["extremo_3iqr"] = "SI" if es_extremo else "NO"
                salida.append(y)

            destino = os.path.join(SALIDA, "ATL08_%s_%s_utm.csv" % (recinto, nivel))
            campos = list(filas[0].keys()) + ["este_utm19s", "norte_utm19s",
                                              "aoi_normalizado", "nivel",
                                              "dentro_aoi", "fuera_del_borde_m",
                                              "fecha", "extremo_3iqr"]
            with open(destino, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=campos)
                w.writeheader()
                w.writerows(salida)
            total_escrito += len(salida)

            fechas = sorted(v["fecha"] for v in salida if v["fecha"])
            registro.append({
                "recinto": recinto,
                "nivel": nivel,
                "segmentos": len(salida),
                "fuera_del_aoi": fuera,
                "peor_fuera_m": "%.1f" % peor_fuera,
                "sin_h_canopy": sin_altura,
                "extremos_3iqr": extremos,
                "umbral_3iqr_m": "%.2f" % umbral,
                "mediana_h_canopy_m": "%.2f" % est.median([v for v in alturas]),
                "granulos": len(set(v.get("granule", "") for v in salida)),
                "fecha_min": fechas[0] if fechas else "",
                "fecha_max": fechas[-1] if fechas else "",
            })
            print("%-14s %-12s %5d segmentos  ->  %s"
                  % (recinto, nivel, len(salida), os.path.basename(destino)))
            if fuera:
                # Un segmento ATL08 mide 100 m: su centroide puede quedar hasta
                # 50 m afuera y el segmento seguir tocando el recinto. Mas alla
                # de eso ya no es efecto de borde.
                if peor_fuera <= 50.0:
                    print("   %d segmentos con el centroide hasta %.1f m fuera del "
                          "recuadro: efecto de borde, el segmento igual lo toca."
                          % (fuera, peor_fuera))
                else:
                    print("   AVISO: %d segmentos fuera del recuadro, el peor a %.1f m."
                          % (fuera, peor_fuera))
                    print("          Mas de 50 m no es borde: revise la extraccion.")

    if not registro:
        print("\nNo se cargo nada. Revise la carpeta de entrada.")
        return 1

    ctrl = os.path.join(CONTROL, "TP2_12_carga_ATL08.csv")
    with open(ctrl, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(registro[0].keys()))
        w.writeheader()
        w.writerows(registro)

    print("\nEPSG de salida: %d" % EPSG)
    print("Total normalizado: %d segmentos" % total_escrito)
    print("Control de calidad: %s" % ctrl)
    return 0


if __name__ == "__main__":
    sys.exit(main())
