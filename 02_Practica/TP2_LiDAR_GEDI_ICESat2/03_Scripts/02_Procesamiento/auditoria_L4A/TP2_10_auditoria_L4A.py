# -*- coding: utf-8 -*-
"""
TP2_10_auditoria_L4A.py   ---> por que el L4A descarta lo que descarta.

LA PREGUNTA
-----------
De las 690 huellas que el TP2 declara validas en BOSQUE_NW_02, solo 271 llegan
con biomasa. Se pierde el 60,7 %. En ESTEPA_NW_02 se pierde el 63,4 %. Antes de
seguir construyendo encima de ese 39 % que sobrevive hay que saber si lo que se
cae es una muestra al azar del recinto o si se cae siempre lo mismo.

No es al azar. Se cae, sobre todo, la lenga.

QUE MIDE ESTE SCRIPT
--------------------
1. DONDE SE PIERDE CADA HUELLA. El L4A trae su propia bandera de calidad,
   l4_quality_flag. Este script descompone el rechazo en las causas que se
   pueden verificar con lo que hay descargado:
       - l2_quality_flag = 0   (el propio L2A ya la daba por mala)
       - sensitivity < 0,95    (umbral medido, no supuesto: la sensibilidad mas
                                baja entre todas las huellas ACEPTADAS es 0,9500)
       - ninguna de las dos    (queda sin explicacion)
   Ese ultimo grupo es el interesante: son huellas que pasan los dos controles
   conocidos y aun asi el L4A rechaza. Solo pueden explicarse con las banderas
   que la primera descarga no trajo -algorithm_run_flag, predictor_limit_flag,
   response_limit_flag-, que son las que agrega la version corregida del
   TP2_01b. En el bosque son 224 huellas, el 53,5 % de todo el rechazo, y 93 de
   ellas son lenga.

2. QUE MODELO LE APLICO LA NASA A CADA HUELLA. El L4A no tiene un solo modelo:
   elige uno segun el estrato (predict_stratum), que sale de un mapa global de
   tipos funcionales de vegetacion. Este script cruza ese estrato contra la
   cobertura del SNMBN 2017, que es un relevamiento local.
   Lo que aparece no es un detalle: dentro de una misma cobertura, y a igual
   altura y cobertura de dosel, el AGBD cambia por un factor de entre 8 y 300
   segun el estrato que le toco. En el nire, las huellas con MAS dosel medido
   reciben MENOS biomasa que las de menos dosel, porque las primeras cayeron en
   el modelo de latifoliada caducifolia y las segundas en el de conifera.

ENTRADA   TP2_LiDAR_GEDI_ICESat2/02_Subsets_SNAP_QGIS/GEDI_L4A/GEDI04_A_<AOI>_shots15km.csv
          TP5_Sinergia_Multisensor/04_Tablas_de_trabajo/TP5_dataset_<AOI>_cobertura.csv
SALIDA    TP2_LiDAR_GEDI_ICESat2/05_Resultados/06_Control_calidad/
              TP2_rechazo_L4A_por_cobertura.csv
              TP2_estrato_L4A_vs_cobertura.csv

USO (entorno conda 'aoi'):   python TP2_10_auditoria_L4A.py
"""
import csv
import os
import statistics as est

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROY = os.path.abspath(os.path.join(TP2, ".."))
L4A = os.path.join(TP2, "02_Subsets_SNAP_QGIS", "GEDI_L4A")
TP5 = os.path.join(PROY, "TP5_Sinergia_Multisensor", "04_Tablas_de_trabajo")
SALIDA = os.path.join(TP2, "05_Resultados", "06_Control_calidad")

UMBRAL_SENS = 0.95      # medido sobre los datos, no tomado de la documentacion
AOIS = ["BOSQUE_NW_02", "ESTEPA_NW_02"]

# Banderas que la primera extraccion no habia bajado. Si el CSV todavia es el
# viejo, estas columnas no existen y el script lo dice en vez de romperse: la
# tabla sale igual, con la columna correspondiente vacia.
BANDERAS = [("algorithm_run_flag", "0"),      # el algoritmo no llego a correr
            ("predictor_limit_flag", "0"),    # alguna metrica fuera del rango del modelo
            ("response_limit_flag", "0"),     # la biomasa predicha fuera del rango del modelo
            ("surface_flag", "1")]            # el retorno no viene de la superficie
LEAF_OFF = "leaf_off_flag"                    # 1 = disparo tomado sin hojas


def numero(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def mediana(filas, columna):
    v = [numero(f[columna]) for f in filas]
    v = [x for x in v if x is not None]
    return round(est.median(v), 3) if v else ""


def main():
    os.makedirs(SALIDA, exist_ok=True)
    rechazo, estratos = [], []

    for aoi in AOIS:
        l4 = {r["shot_number"]: r for r in csv.DictReader(
            open(os.path.join(L4A, "GEDI04_A_%s_shots15km.csv" % aoi),
                 encoding="utf-8"))}
        filas = list(csv.DictReader(
            open(os.path.join(TP5, "TP5_dataset_%s_cobertura.csv" % aoi),
                 encoding="utf-8")))

        columnas = set(next(iter(l4.values())).keys()) if l4 else set()
        disponibles = {c: (c in columnas)
                       for c in [b for b, _ in BANDERAS] + [LEAF_OFF]}
        if not all(disponibles.values()):
            print("   AVISO: el CSV del L4A todavia no trae %s."
                  % ", ".join(sorted(c for c, hay in disponibles.items() if not hay)))
            print("          Correr antes:  python TP2_01c_reextraer_l4a.py")

        faltan = [f for f in filas if f["shot_number"] not in l4]
        if faltan:
            print("   ATENCION: %d huellas validas no aparecen en el L4A" % len(faltan))

        aceptadas = [f for f in filas if f["shot_number"] in l4
                     and l4[f["shot_number"]]["l4_quality_flag"] == "1"]
        if aceptadas:
            minima = min(numero(l4[f["shot_number"]]["sensitivity"]) or 1
                         for f in aceptadas)
            print("%s: sensibilidad minima entre las aceptadas = %.4f "
                  "(el umbral que se usa aca es %.2f)" % (aoi, minima, UMBRAL_SENS))

        # ---- 1. de que se muere cada huella, por cobertura ------------------
        clases = {}
        for f in filas:
            clases.setdefault(f["COB_N3"], []).append(f)
        for k in sorted(clases, key=lambda x: -len(clases[x])):
            g = clases[k]
            n_ok = n_l2 = n_sens = n_resto = 0
            resto = []
            for f in g:
                r = l4.get(f["shot_number"])
                if r is None:
                    continue
                if r["l4_quality_flag"] == "1":
                    n_ok += 1
                elif r["l2_quality_flag"] != "1":
                    n_l2 += 1
                elif (numero(r["sensitivity"]) or 0) < UMBRAL_SENS:
                    n_sens += 1
                else:
                    n_resto += 1
                    resto.append(f)
            fila = {
                "AOI": aoi, "COBERTURA_N3": k, "N_HUELLAS": len(g),
                "CON_AGBD": n_ok,
                "RETENCION_PCT": round(100.0 * n_ok / len(g), 1) if g else "",
                "RECH_l2_quality": n_l2,
                "RECH_sensitivity": n_sens,
                "RECH_SIN_EXPLICAR": n_resto,
                "PCT_SIN_EXPLICAR_DE_LA_CLASE":
                    round(100.0 * n_resto / len(g), 1) if g else "",
                "RH95_MED_ACEPTADAS": mediana(
                    [f for f in g if l4.get(f["shot_number"], {}).get("l4_quality_flag") == "1"], "rh95"),
                "RH95_MED_SIN_EXPLICAR": mediana(resto, "rh95"),
            }
            # Que dicen las banderas nuevas sobre el grupo sin explicar
            for campo, bueno in BANDERAS:
                fila["SIN_EXPL_" + campo] = (
                    sum(1 for f in resto if l4[f["shot_number"]].get(campo, "") not in ("", bueno))
                    if disponibles.get(campo) else "")
            fila["SIN_EXPL_hoja_caida"] = (
                sum(1 for f in resto if l4[f["shot_number"]].get(LEAF_OFF, "") == "1")
                if disponibles.get(LEAF_OFF) else "")
            fila["ACEPTADAS_hoja_caida"] = (
                sum(1 for f in g if l4.get(f["shot_number"], {}).get("l4_quality_flag") == "1"
                    and l4[f["shot_number"]].get(LEAF_OFF, "") == "1")
                if disponibles.get(LEAF_OFF) else "")
            rechazo.append(fila)

        # ---- 2. que modelo le aplico la NASA -------------------------------
        con = [f for f in filas
               if f["shot_number"] in l4 and numero(f["agbd_Mg_ha"]) is not None]
        cruce = {}
        for f in con:
            cruce.setdefault(f["COB_N3"], {}).setdefault(
                l4[f["shot_number"]]["predict_stratum"], []).append(f)
        for k in sorted(cruce, key=lambda x: -sum(len(v) for v in cruce[x].values())):
            for s, g in sorted(cruce[k].items(), key=lambda x: -len(x[1])):
                estratos.append({
                    "AOI": aoi, "COBERTURA_N3": k, "PREDICT_STRATUM": s,
                    "N": len(g),
                    "RH95_MEDIANA": mediana(g, "rh95"),
                    "RH50_MEDIANA": mediana(g, "rh50"),
                    "COVER_MEDIANA": mediana(g, "cover"),
                    "PAI_MEDIANA": mediana(g, "pai"),
                    "AGBD_MEDIANA": mediana(g, "agbd_Mg_ha"),
                    "AGBD_MEDIA": round(est.fmean(
                        [numero(f["agbd_Mg_ha"]) for f in g]), 2),
                })

    for nombre, datos in [("TP2_rechazo_L4A_por_cobertura.csv", rechazo),
                          ("TP2_estrato_L4A_vs_cobertura.csv", estratos)]:
        ruta = os.path.join(SALIDA, nombre)
        with open(ruta, "w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=list(datos[0].keys()))
            w.writeheader()
            w.writerows(datos)
        print("tabla  %s  (%d filas)" % (nombre, len(datos)))


if __name__ == "__main__":
    main()
