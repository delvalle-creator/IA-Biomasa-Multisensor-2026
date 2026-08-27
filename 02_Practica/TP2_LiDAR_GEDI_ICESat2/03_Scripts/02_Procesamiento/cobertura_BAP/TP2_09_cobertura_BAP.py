# -*- coding: utf-8 -*-
"""
TP2_09_cobertura_BAP.py   ---> cruza cada huella GEDI con la cobertura vegetal.

POR QUE HACIA FALTA
-------------------
Hasta ahora los resultados se informaban por recinto: "el bosque" y "la estepa".
Pero el recinto BOSQUE_NW_02 no es bosque. Segun el relevamiento del SNMBN 2017
(capa BAP de Chubut) esta compuesto asi:

    nire bajo          34,8 %      lenga             33,0 %
    nire               11,6 %      cipres             4,9 %
    estepa              3,7 %      lenga baja         3,2 %
    y once clases mas por debajo del 3 %

Promediar biomasa sobre esa mezcla no describe a ninguna de las partes. El nire
bajo es una leñosa de porte arbustivo con casi nada de biomasa aerea; la lenga es
bosque alto. La media del conjunto queda en tierra de nadie y, ademas, depende de
cuantas huellas GEDI cayeron en cada clase, que es un accidente de las orbitas y
no una propiedad del terreno.

Este script le pega a cada huella la clase de cobertura que le corresponde, y a
partir de ahi los practicos que siguen pueden informar por clase, que es lo unico
que se puede comparar contra la bibliografia y contra un inventario de campo.

COMO SE ASIGNA LA CLASE
-----------------------
La huella de GEDI no es un punto: es un circulo de 25 m de diametro. Asi que no
se pregunta "en que poligono cae el centro" sino "que fraccion del circulo ocupa
cada clase". Se toma la clase mayoritaria y se guarda ademas su fraccion, que es
la que permite descartar despues las huellas que caen a caballo de dos coberturas.

COLUMNAS QUE AGREGA
-------------------
    COB_N3            clase mayoritaria dentro de la huella (LEYENDA_N3 del BAP)
    COB_GRUPO         agrupamiento del BAP (lenga, nire, cipres, estepa, ...)
    COB_FRAC          fraccion del circulo ocupada por esa clase, de 0 a 1
    COB_NCLASES       cuantas clases distintas toca la huella
    COB_BORDE         SI cuando COB_FRAC < 0,90; la huella es de transicion
    COB_FRAC_BOSQUE   fraccion del circulo con clases que el BAP marca BOSQUE=SI

ENTRADA   00_COMUN/02_Coberturas/BAP_SNMBN_2017/BAP_<AOI>_recorte.shp
          TP2_LiDAR_GEDI_ICESat2/04_Tablas_de_trabajo/0*/GEDI_<AOI>_validos_con_estructura.csv
          TP5_Sinergia_Multisensor/04_Tablas_de_trabajo/TP5_dataset_<AOI>.csv

SALIDA    ..._validos_con_cobertura.csv   y   TP5_dataset_<AOI>_cobertura.csv
          TP5_.../05_Resultados/04_Tablas/TP5_AGBD_por_cobertura.csv
          TP5_.../05_Resultados/04_Tablas/TP5_AGBD_estratificado.csv

Los archivos de entrada NO se tocan. Todo sale con nombre nuevo.

USO (entorno conda 'aoi'):   python TP2_09_cobertura_BAP.py
"""
import csv
import math
import os
import statistics as est
import sys

from shapely.geometry import Point
from shapely.strtree import STRtree

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import lector_bap                                                   # noqa: E402

TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROY = os.path.abspath(os.path.join(TP2, ".."))
BAP = os.path.join(PROY, "00_COMUN", "02_Coberturas", "BAP_SNMBN_2017")
TP5 = os.path.join(PROY, "TP5_Sinergia_Multisensor")
TABLAS = os.path.join(TP5, "05_Resultados", "04_Tablas")

RADIO = 12.5        # radio de la huella GEDI: 25 m de diametro
PURA = 0.90         # por debajo de esta fraccion la huella se declara de borde

AOIS = [("BOSQUE_NW_02", os.path.join(TP2, "04_Tablas_de_trabajo", "01_Bosque")),
        ("ESTEPA_NW_02", os.path.join(TP2, "04_Tablas_de_trabajo", "02_Estepa"))]

NUEVAS = ["COB_N3", "COB_GRUPO", "COB_FRAC", "COB_NCLASES", "COB_BORDE",
          "COB_FRAC_BOSQUE"]


def numero(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def cruzar(geometrias, atributos, arbol, filas):
    """Le agrega a cada fila las seis columnas de cobertura."""
    for f in filas:
        circulo = Point(float(f["este_utm19s"]),
                        float(f["norte_utm19s"])).buffer(RADIO, quad_segs=16)
        por_n3, por_grupo, area_bosque = {}, {}, 0.0
        for i in arbol.query(circulo):
            trozo = geometrias[i].intersection(circulo)
            if trozo.is_empty or trozo.area <= 0:
                continue
            a = trozo.area
            at = atributos[i]
            por_n3[at["LEYENDA_N3"]] = por_n3.get(at["LEYENDA_N3"], 0.0) + a
            por_grupo[at["GRUPO"]] = por_grupo.get(at["GRUPO"], 0.0) + a
            if at["BOSQUE"] == "SI":
                area_bosque += a
        total = sum(por_n3.values())
        if total <= 0:                       # no deberia pasar: el BAP cubre el 100 %
            f.update(COB_N3="", COB_GRUPO="", COB_FRAC=0.0, COB_NCLASES=0,
                     COB_BORDE="SD", COB_FRAC_BOSQUE=0.0)
            continue
        n3 = max(por_n3, key=por_n3.get)
        fraccion = por_n3[n3] / total
        f.update(COB_N3=n3,
                 COB_GRUPO=max(por_grupo, key=por_grupo.get),
                 COB_FRAC=round(fraccion, 4),
                 COB_NCLASES=len(por_n3),
                 COB_BORDE=("NO" if fraccion >= PURA else "SI"),
                 COB_FRAC_BOSQUE=round(area_bosque / total, 4))
    return filas


def escribir(ruta, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print("      escrito  %s  (%d filas)" % (os.path.basename(ruta), len(filas)))


def main():
    por_clase, por_aoi = [], []

    for aoi, carpeta in AOIS:
        print("=" * 78)
        print(aoi)
        shp = os.path.join(BAP, "BAP_%s_recorte" % aoi)
        geometrias, atributos = lector_bap.leer(shp)
        print("   poligonos BAP %d   superficie reconstruida %.6f km2"
              % (len(geometrias), sum(g.area for g in geometrias) / 1e6))
        arbol = STRtree(geometrias)

        # --- huellas del TP2 ------------------------------------------------
        origen = os.path.join(carpeta, "GEDI_%s_validos_con_estructura.csv" % aoi)
        filas = list(csv.DictReader(open(origen, encoding="utf-8")))
        filas = cruzar(geometrias, atributos, arbol, filas)
        escribir(os.path.join(carpeta, "GEDI_%s_validos_con_cobertura.csv" % aoi),
                 filas)

        # --- tabla apilada del TP5 ------------------------------------------
        origen5 = os.path.join(TP5, "04_Tablas_de_trabajo", "TP5_dataset_%s.csv" % aoi)
        filas5 = list(csv.DictReader(open(origen5, encoding="utf-8")))
        filas5 = cruzar(geometrias, atributos, arbol, filas5)
        escribir(os.path.join(TP5, "04_Tablas_de_trabajo",
                              "TP5_dataset_%s_cobertura.csv" % aoi), filas5)

        # --- superficie de cada clase, del propio resumen del BAP ------------
        resumen = {r["LEYENDA_N3"]: r for r in csv.DictReader(
            open(os.path.join(BAP, "BAP_%s_resumen_N3.csv" % aoi),
                 encoding="utf-8-sig"))}

        con_agbd = [f for f in filas5 if numero(f["agbd_Mg_ha"]) is not None]

        # --- AGBD por clase de cobertura ------------------------------------
        clases = sorted({f["COB_N3"] for f in filas5})
        superficie_muestreada = sum(float(resumen[k]["AREA_HA"]) for k in clases
                                    if k in resumen and
                                    any(f["COB_N3"] == k for f in con_agbd))
        media_estratificada, varianza = 0.0, 0.0
        for k in clases:
            g = [f for f in filas5 if f["COB_N3"] == k]
            ga = [numero(f["agbd_Mg_ha"]) for f in g]
            ga = [x for x in ga if x is not None]
            rh = [numero(f["rh95"]) for f in g if numero(f["rh95"]) is not None]
            cv = [numero(f["cover"]) for f in g if numero(f["cover"]) is not None]
            r = resumen.get(k, {})
            fila = {
                "AOI": aoi, "COBERTURA_N3": k,
                "GRUPO": r.get("GRUPO", ""), "BOSQUE_BAP": r.get("BOSQUE", ""),
                "SUP_HA": r.get("AREA_HA", ""), "PCT_AOI": r.get("PCT_AOI", ""),
                "N_HUELLAS": len(g), "N_CON_AGBD": len(ga),
                "RETENCION_L4A_PCT": round(100.0 * len(ga) / len(g), 1) if g else "",
                "RH95_MEDIANA": round(est.median(rh), 2) if rh else "",
                "COVER_MEDIANA": round(est.median(cv), 3) if cv else "",
                "AGBD_MEDIA": round(est.fmean(ga), 2) if ga else "",
                "AGBD_MEDIANA": round(est.median(ga), 2) if ga else "",
                "AGBD_EE": round(est.stdev(ga) / len(ga) ** 0.5, 2) if len(ga) > 1 else "",
                "STOCK_Mg": round(est.fmean(ga) * float(r["AREA_HA"])) if (ga and r) else "",
            }
            por_clase.append(fila)
            if ga and r and superficie_muestreada > 0:
                peso = float(r["AREA_HA"]) / superficie_muestreada
                media_estratificada += peso * est.fmean(ga)
                if len(ga) > 1:
                    varianza += (peso ** 2) * est.variance(ga) / len(ga)

        simple = [numero(f["agbd_Mg_ha"]) for f in con_agbd]
        ee_estrat = math.sqrt(varianza)
        por_aoi.append({
            "AOI": aoi,
            "N_HUELLAS": len(filas5),
            "N_CON_AGBD": len(con_agbd),
            "RETENCION_L4A_PCT": round(100.0 * len(con_agbd) / len(filas5), 1),
            "AGBD_MEDIA_SIMPLE": round(est.fmean(simple), 2),
            "EE_SIMPLE": round(est.stdev(simple) / len(simple) ** 0.5, 2),
            "AGBD_MEDIA_ESTRATIFICADA": round(media_estratificada, 2),
            "EE_ESTRATIFICADA": round(ee_estrat, 2),
            "SUP_MUESTREADA_HA": round(superficie_muestreada, 1),
            "PCT_AOI_MUESTREADO": round(100.0 * superficie_muestreada / 22500.0, 1),
            "STOCK_Mg": round(media_estratificada * superficie_muestreada),
            "STOCK_EE_Mg": round(ee_estrat * superficie_muestreada),
            "HUELLAS_DE_BORDE": sum(1 for f in filas5 if f["COB_BORDE"] == "SI"),
        })
        print("   media simple %.2f  ->  media estratificada %.2f +/- %.2f Mg/ha"
              % (est.fmean(simple), media_estratificada, ee_estrat))

    for nombre, datos in [("TP5_AGBD_por_cobertura.csv", por_clase),
                          ("TP5_AGBD_estratificado.csv", por_aoi)]:
        ruta = os.path.join(TABLAS, nombre)
        with open(ruta, "w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=list(datos[0].keys()))
            w.writeheader()
            w.writerows(datos)
        print("tabla  %s  (%d filas)" % (nombre, len(datos)))


if __name__ == "__main__":
    main()
