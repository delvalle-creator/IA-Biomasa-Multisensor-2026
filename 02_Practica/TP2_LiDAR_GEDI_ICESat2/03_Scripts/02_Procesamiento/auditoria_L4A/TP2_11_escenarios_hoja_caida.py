# -*- coding: utf-8 -*-
"""
TP2_11_escenarios_hoja_caida.py   ---> cuanto cambia el AGBD segun que se decida.

LA DECISION QUE HAY QUE TOMAR
-----------------------------
El L4A descarta TODO disparo tomado con el dosel sin hojas: de los 6.287 del
bosque, ni uno solo con leaf_off_flag = 1 fue aceptado. En un bosque de
caducifolias eso se lleva 224 huellas, la mitad del rechazo, y 93 de ellas son
lenga. La pregunta es si se las deja afuera y se declara, o si se las usa.

Este script no decide: pone los tres escenarios uno al lado del otro.

    A   solo hoja presente. Es lo que veniamos informando.
    B   se suman las de hoja caida CON EL AGBD QUE LA PROPIA NASA CALCULO.
        No agrega ningun modelo nuevo: la NASA corrio el modelo igual
        (algorithm_run_flag = 1 en las 224) y lo unico que hizo fue no
        certificarlo.
    C   como B, pero ademas se exige coherencia botanica: en las clases de
        Nothofagus -lenga y nire, que son latifoliadas caducifolias- se aceptan
        solo las huellas a las que la NASA les aplico el modelo DBT_SA, y se
        descartan las que cayeron en ENT_SA (conifera perennifolia) o GSW_SA
        (pastizal-matorral).

LO QUE HAY QUE SABER ANTES DE LEER EL RESULTADO
-----------------------------------------------
1. LAS 224 HUELLAS DE HOJA CAIDA SON TODAS DBT_SA. Sin excepcion. Y las
   aceptadas son una mezcla. Por eso, si se comparan los dos grupos en bruto,
   parece que la hoja caida "baja" el AGBD; lo que baja es el cambio de modelo,
   no la hoja. A IGUAL ESTRATO la hoja caida no deprime nada:

       lenga DBT_SA     hoja presente 91,33   hoja caida 88,82
       nire  DBT_SA     hoja presente  2,66   hoja caida  3,95
       nire bajo DBT_SA hoja presente  0,06   hoja caida  0,65

   Es la razon por la que el escenario B es defendible.

2. EL ESCENARIO C NO SIRVE EN LA ESTEPA. Alla NINGUNA huella de lenga o de nire
   recibio DBT_SA: la NASA les puso GSW_SA a todas. Asi que en ESTEPA_NW_02 el
   escenario C no corrige el estrato, directamente borra la clase, y por eso
   tambien le baja la superficie muestreada. En la estepa solo valen A y B, que
   ademas dan lo mismo porque alli leaf_off_flag es 0 en las 3.083 huellas.

3. LA ELECCION ENTRE DBT_SA Y ENT_SA NO SE PUEDE RESOLVER CON ESTOS DATOS. El
   nire es Nothofagus antarctica, latifoliada caducifolia, asi que DBT_SA es lo
   botanicamente correcto; pero ninguno de los dos modelos se puede validar sin
   las parcelas de campo. Por eso C se informa como prueba de sensibilidad y no
   como resultado.

ENTRADA   TP2_LiDAR_GEDI_ICESat2/02_Subsets_SNAP_QGIS/GEDI_L4A/GEDI04_A_<AOI>_shots15km.csv
          TP5_Sinergia_Multisensor/04_Tablas_de_trabajo/TP5_dataset_<AOI>_cobertura.csv
          00_COMUN/02_Coberturas/BAP_SNMBN_2017/BAP_<AOI>_resumen_N3.csv
SALIDA    TP5_.../05_Resultados/04_Tablas/TP5_escenarios_hoja_caida.csv
          TP5_.../05_Resultados/04_Tablas/TP5_escenarios_por_clase.csv

USO (entorno conda 'aoi'):   python TP2_11_escenarios_hoja_caida.py
"""
import csv
import math
import os
import statistics as est

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROY = os.path.abspath(os.path.join(TP2, ".."))
L4A = os.path.join(TP2, "02_Subsets_SNAP_QGIS", "GEDI_L4A")
BAP = os.path.join(PROY, "00_COMUN", "02_Coberturas", "BAP_SNMBN_2017")
TP5 = os.path.join(PROY, "TP5_Sinergia_Multisensor")
TABLAS = os.path.join(TP5, "05_Resultados", "04_Tablas")

UMBRAL_SENS = 0.95
AOIS = ["BOSQUE_NW_02", "ESTEPA_NW_02"]

# Clases del BAP que son Nothofagus: latifoliadas caducifolias.
NOTHOFAGUS = {"Lenga", "Lenga Baja", "Lenga Achaparrada", "Lenga Juvenil Briznal",
              "Lenga Marginal", "Lenga-Ñire", "Lenga-Ñire Bajo",
              "Ñire", "Ñire Bajo", "Ñire-Lenga", "Ñire Bajo-Lenga"}

ESCENARIOS = ["A. solo hoja presente",
              "B. + hoja caida, AGBD de la NASA",
              "C. B + Nothofagus solo DBT_SA"]


def numero(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def estratificar(por_clase, resumen):
    """Media ponderada por la superficie de cada cobertura, y su error estandar."""
    sup = sum(float(resumen[k]["AREA_HA"])
              for k in por_clase if k in resumen and por_clase[k])
    if sup <= 0:
        return 0.0, 0.0, 0.0
    media, varianza = 0.0, 0.0
    for k, g in por_clase.items():
        if k not in resumen or not g:
            continue
        peso = float(resumen[k]["AREA_HA"]) / sup
        media += peso * est.fmean(g)
        if len(g) > 1:
            varianza += peso * peso * est.variance(g) / len(g)
    return media, math.sqrt(varianza), sup


def main():
    os.makedirs(TABLAS, exist_ok=True)
    resumen_global, por_clase_global = [], []

    for aoi in AOIS:
        l4 = {r["shot_number"]: r for r in csv.DictReader(
            open(os.path.join(L4A, "GEDI04_A_%s_shots15km.csv" % aoi),
                 encoding="utf-8"))}
        filas = list(csv.DictReader(
            open(os.path.join(TP5, "04_Tablas_de_trabajo", "TP5_dataset_%s_cobertura.csv" % aoi),
                 encoding="utf-8")))
        resumen = {r["LEYENDA_N3"]: r for r in csv.DictReader(
            open(os.path.join(BAP, "BAP_%s_resumen_N3.csv" % aoi),
                 encoding="utf-8-sig"))}

        if "leaf_off_flag" not in next(iter(l4.values())):
            raise SystemExit("El CSV del L4A no trae leaf_off_flag.\n"
                             "Correr antes:  python TP2_01c_reextraer_l4a.py")

        def aceptada(f):
            return l4[f["shot_number"]]["l4_quality_flag"] == "1"

        def hoja_caida_util(f):
            r = l4[f["shot_number"]]
            return (r["leaf_off_flag"] == "1"
                    and (numero(r["sensitivity"]) or 0) >= UMBRAL_SENS)

        def estrato(f):
            return l4[f["shot_number"]]["predict_stratum"]

        seleccion = {
            ESCENARIOS[0]: [f for f in filas if aceptada(f)],
            ESCENARIOS[1]: [f for f in filas if aceptada(f) or hoja_caida_util(f)],
        }
        seleccion[ESCENARIOS[2]] = [
            f for f in seleccion[ESCENARIOS[1]]
            if not (f["COB_N3"] in NOTHOFAGUS and estrato(f) != "DBT_SA")]

        for nombre in ESCENARIOS:
            por_clase = {}
            for f in seleccion[nombre]:
                v = numero(l4[f["shot_number"]]["agbd"])
                if v is not None:
                    por_clase.setdefault(f["COB_N3"], []).append(v)
            media, ee, sup = estratificar(por_clase, resumen)
            resumen_global.append({
                "AOI": aoi, "ESCENARIO": nombre,
                "N_HUELLAS": sum(len(v) for v in por_clase.values()),
                "AGBD_Mg_ha": round(media, 2), "EE_Mg_ha": round(ee, 2),
                "SUP_MUESTREADA_HA": round(sup, 1),
                "STOCK_Mg": round(media * sup),
            })
            for k, g in sorted(por_clase.items(), key=lambda x: -len(x[1])):
                por_clase_global.append({
                    "AOI": aoi, "ESCENARIO": nombre, "COBERTURA_N3": k,
                    "N": len(g),
                    "AGBD_MEDIA": round(est.fmean(g), 2),
                    "AGBD_MEDIANA": round(est.median(g), 2),
                    "PCT_AOI": resumen.get(k, {}).get("PCT_AOI", ""),
                })

    for nombre, datos in [("TP5_escenarios_hoja_caida.csv", resumen_global),
                          ("TP5_escenarios_por_clase.csv", por_clase_global)]:
        ruta = os.path.join(TABLAS, nombre)
        with open(ruta, "w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=list(datos[0].keys()))
            w.writeheader()
            w.writerows(datos)
        print("tabla  %s  (%d filas)" % (nombre, len(datos)))

    print()
    print("%-14s %-34s %6s %11s %8s %14s"
          % ("AOI", "ESCENARIO", "n", "AGBD Mg/ha", "+/- EE", "stock (Mg)"))
    for r in resumen_global:
        print("%-14s %-34s %6d %11.2f %8.2f %14d"
              % (r["AOI"], r["ESCENARIO"], r["N_HUELLAS"], r["AGBD_Mg_ha"],
                 r["EE_Mg_ha"], r["STOCK_Mg"]))


if __name__ == "__main__":
    main()
