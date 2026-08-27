#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_06_metricas_estructura.py   ---> SEXTO script del TP2.

QUE HACE
--------
Une, para cada disparo valido, las metricas de altura del L2A con las de
estructura del L2B, y compara el bosque con el ecotono de estepa.

QUE SIGNIFICA CADA METRICA (esto es lo importante del practico)
---------------------------------------------------------------
Del producto L2A, las metricas 'rh' (relative height) describen la forma
vertical de la vegetacion. rh95 es la altura por debajo de la cual vuelve el
95 % de la energia: en la practica, la ALTURA DEL DOSEL. Se prefiere rh95 o rh98
antes que rh100 porque el 100 % es sensible al ruido: una sola hoja alta, o un
pajaro, corren el maximo varios metros.

  rh25, rh50, rh75  ->  como se reparte la vegetacion en altura
  rh95, rh98        ->  altura del dosel

Del producto L2B:

  cover       fraccion del suelo cubierta por vegetacion vista desde arriba (0 a 1)
  pai         indice de area foliar de la planta: metros cuadrados de superficie
              vegetal (hojas y ramas) por metro cuadrado de suelo. A mas denso,
              mayor pai
  fhd_normal  diversidad de alturas del follaje. Alto = muchos estratos (un
              bosque maduro con sotobosque, arboles medios y emergentes);
              bajo = un solo estrato (un pastizal o una plantacion pareja)

POR QUE ESTO ANTECEDE A LA BIOMASA
----------------------------------
La biomasa no se mide desde el espacio: se INFIERE. Y se infiere de estas
metricas, sobre todo de la altura y de la densidad. Un arbol alto y denso tiene
mas madera que uno bajo y ralo. Por eso, antes de estimar biomasa (TP2_07), hay
que entender que miden estas variables y comprobar que se comportan como
esperamos: el bosque debe dar alturas y pai claramente mayores que la estepa. Si
eso no ocurre, hay un error en algun paso anterior.

ENTRADA   04_Tablas_de_trabajo/01_Bosque | 02_Estepa/*.csv  (salida del TP2_05)
          02_Subsets_SNAP_QGIS/GEDI_L2B/*.csv
SALIDA    04_Tablas_de_trabajo/01_Bosque | 02_Estepa/*_con_estructura.csv
          05_Resultados/04_Tablas/altura_dosel_<AOI>.csv
          05_Resultados/06_Control_calidad/comparacion_bosque_estepa.csv

USO (entorno conda 'aoi'):   python TP2_06_metricas_estructura.py
"""
import csv
import glob
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
INSUMOS = os.path.join(TP2, "02_Subsets_SNAP_QGIS")
SUBSETS = os.path.join(TP2, "04_Tablas_de_trabajo")
RESULTADOS = os.path.join(TP2, "05_Resultados")

METRICAS_L2B = ["pai", "fhd_normal", "cover"]


def mediana(v):
    v = sorted(v)
    n = len(v)
    if n == 0:
        return float("nan")
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def percentil(v, p):
    v = sorted(v)
    if not v:
        return float("nan")
    k = int(round((len(v) - 1) * p / 100.0))
    return v[k]


def cargar_l2b(aoi):
    """Indexa el L2B por shot_number, para poder unirlo con el L2A.

    Se indexa TODO, tambien lo que el L2B marca como malo: la decision de
    aceptar o descartar se toma al unir, para que cada descarte quede
    registrado con su motivo. Antes el filtrado ocurria aca y el disparo
    356601100400192753 de la estepa (l2b_quality_flag_rel3 = 0) desaparecia
    sin dejar rastro: 3.083 filas donde la aritmetica daba 3.084.
    """
    hit = glob.glob(os.path.join(INSUMOS, "GEDI_L2B", "*%s*.csv" % aoi))
    if not hit:
        return {}
    idx = {}
    with open(hit[0], newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            idx[fila["shot_number"]] = fila
    return idx


def calidad_l2b_ok(fila_l2b):
    """El criterio del propio L2B: rel3 en 1 (o ausente, que vale como 1)."""
    return fila_l2b.get("l2b_quality_flag_rel3", "1") in ("1", "1.0")


def procesar(ruta_csv):
    base = os.path.basename(ruta_csv)
    aoi = "BOSQUE_NW_02" if "BOSQUE" in base else "ESTEPA_NW_02"
    etiqueta = "Bosque" if "BOSQUE" in base else "Estepa"

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        return None

    l2b = cargar_l2b(aoi)
    unidas, descartadas = [], []
    for fila in filas:
        fila = dict(fila)
        m = l2b.get(fila["shot_number"])
        if m is None:
            fila["motivo"] = "sin par en el L2B"
            fila["detalle"] = "el disparo no aparece en el recorte L2B"
            descartadas.append(fila)
            continue                      # sin estructura no sirve para biomasa
        if not calidad_l2b_ok(m):
            fila["motivo"] = "calidad L2B insuficiente"
            fila["detalle"] = "l2b_quality_flag_rel3 = %s" % m.get("l2b_quality_flag_rel3", "")
            descartadas.append(fila)
            continue
        for k in METRICAS_L2B:
            fila[k] = m.get(k, "")
        unidas.append(fila)

    # la regla del proyecto: los descartes se registran, nunca se pierden
    sal_desc = os.path.join(RESULTADOS, "04_Tablas",
                            "GEDI_%s_descartados_estructura.csv" % aoi)
    os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)
    if descartadas:
        with open(sal_desc, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(descartadas[0]))
            w.writeheader(); w.writerows(descartadas)

    if not unidas:
        print("   ningun disparo pudo unirse con el L2B")
        return None

    sal = ruta_csv.replace("_validos.csv", "_validos_con_estructura.csv")
    with open(sal, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(unidas[0]))
        w.writeheader(); w.writerows(unidas)

    # --- tabla de altura de dosel ---
    os.makedirs(os.path.join(RESULTADOS, "04_Tablas"), exist_ok=True)
    with open(os.path.join(RESULTADOS, "04_Tablas",
                           "altura_dosel_%s.csv" % aoi),
              "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["shot_number", "este_utm19s", "norte_utm19s",
                    "altura_dosel_rh95_m", "rh98_m", "cover", "pai",
                    "fhd_normal", "pendiente_grados"])
        for d in unidas:
            w.writerow([d["shot_number"], d["este_utm19s"], d["norte_utm19s"],
                        d["rh95"], d["rh98"], d.get("cover", ""),
                        d.get("pai", ""), d.get("fhd_normal", ""),
                        d.get("pendiente_grados", "")])

    def col(nombre):
        out = []
        for d in unidas:
            try:
                out.append(float(d[nombre]))
            except (KeyError, ValueError, TypeError):
                pass
        return out

    print("   disparos con estructura : %5d  (descartados al unir con L2B: %d)"
          % (len(unidas), len(descartadas)))
    if descartadas:
        print("   descartes registrados en: %s" % sal_desc)
    est = {"sitio": etiqueta, "aoi": aoi, "n": len(unidas)}
    print("   %-16s %8s %8s %8s" % ("metrica", "mediana", "p90", "maximo"))
    for nombre, etiq in [("rh95", "altura dosel (m)"), ("rh98", "rh98 (m)"),
                         ("cover", "cobertura (0-1)"), ("pai", "pai"),
                         ("fhd_normal", "fhd (estratos)")]:
        v = col(nombre)
        if not v:
            continue
        print("   %-16s %8.2f %8.2f %8.2f"
              % (etiq, mediana(v), percentil(v, 90), max(v)))
        est[nombre + "_mediana"] = mediana(v)
        est[nombre + "_p90"] = percentil(v, 90)
    return est


print(__doc__)
resumen = []
archivos = sorted(glob.glob(os.path.join(SUBSETS, "0[12]_*",
                                         "*_validos.csv")))
if not archivos:
    sys.exit("No hay footprints validos.\nEjecute antes:  python TP2_05_filtrar_pendiente.py")

for ruta in archivos:
    print("=" * 72)
    print(os.path.basename(ruta))
    print("=" * 72)
    r = procesar(ruta)
    if r:
        resumen.append(r)
    print()

# ------------------- comparacion bosque vs estepa -------------------
if len(resumen) == 2:
    b = next((r for r in resumen if r["sitio"] == "Bosque"), None)
    e = next((r for r in resumen if r["sitio"] == "Estepa"), None)
    if b and e:
        print("=" * 72)
        print("COMPARACION BOSQUE vs ESTEPA  (medianas)")
        print("=" * 72)
        print("   %-22s %10s %10s %10s" % ("metrica", "bosque", "estepa", "razon"))
        for k, etiq in [("rh95_mediana", "altura dosel (m)"),
                        ("cover_mediana", "cobertura"),
                        ("pai_mediana", "pai"),
                        ("fhd_normal_mediana", "fhd (estratos)")]:
            if k in b and k in e and e[k]:
                razon = b[k] / e[k] if e[k] else float("nan")
                print("   %-22s %10.2f %10.2f %9.1fx" % (etiq, b[k], e[k], razon))
        os.makedirs(os.path.join(RESULTADOS, "06_Control_calidad"), exist_ok=True)
        with open(os.path.join(RESULTADOS, "06_Control_calidad",
                               "comparacion_bosque_estepa.csv"),
                  "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["metrica", "bosque_mediana", "estepa_mediana", "razon"])
            for k, etiq in [("rh95_mediana", "altura_dosel_rh95_m"),
                            ("cover_mediana", "cover"),
                            ("pai_mediana", "pai"),
                            ("fhd_normal_mediana", "fhd_normal")]:
                if k in b and k in e:
                    r = b[k] / e[k] if e[k] else ""
                    w.writerow([etiq, "%.3f" % b[k], "%.3f" % e[k],
                                "%.2f" % r if r != "" else ""])
        print()
        print("Si el bosque NO da alturas y pai claramente mayores que la estepa,")
        print("hay un error en algun paso anterior: revise el filtrado.")

print()
print("SIGUIENTE PASO:  python TP2_07_biomasa_referencia.py")
