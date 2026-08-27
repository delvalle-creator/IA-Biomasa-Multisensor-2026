# -*- coding: utf-8 -*-
"""
TP2_13_cotejar_GEDI_ICESat2.py  ---> compara la altura de dosel que mide GEDI con
                                     la que mide ICESat-2 sobre el mismo terreno.

POR QUE HACIA FALTA
-------------------
Este proyecto usa GEDI como referencia para calibrar los tres practicos que
siguen, y no tiene parcelas de campo con que verificarlo. La limitacion esta
declarada en el 00_LEEME del practico y no se resuelve con este script: GEDI
sigue siendo una estimacion satelital que nadie midio desde el suelo.

Lo que si se puede hacer es preguntarle lo mismo a un segundo instrumento. GEDI
es laser de onda completa sobre huellas de 25 m; ICESat-2 / ATL08 es conteo de
fotones sobre segmentos de 100 m. Son dos maneras distintas de medir la misma
altura. Donde las dos misiones pasan por el mismo lugar, la diferencia entre lo
que dicen es una cota inferior del error de la referencia. No es la verdad de
campo: es lo unico honesto que hay hasta que existan parcelas.

COMO SE COMPARA, Y POR QUE NO DE A UNA
--------------------------------------
Una huella GEDI de 25 m y un segmento ATL08 de 100 m casi nunca coinciden, y sus
orbitas son distintas: las trazas se cruzan en pocos lugares. Emparejar por
vecino mas cercano produciria pares que no describen el mismo terreno.

Se compara entonces sobre una grilla de celdas cuadradas, alineada al recuadro
del recinto. En cada celda con suficientes observaciones de ambas misiones se
toma la MEDIANA de cada una y se compara. La mediana resiste los extremos, que en
ATL08 llegan a 132 m sobre 24 fotones de copa.

    diferencia = mediana ATL08 - mediana GEDI      (metros, positivo = ATL08 mas alto)

QUE SE COMPARA CONTRA QUE
-------------------------
    GEDI    rh98            altura relativa al percentil 98 sobre el suelo
    ATL08   h_canopy_m      altura relativa al percentil 98 sobre el terreno

Son la misma definicion. NO se usa rh95 contra h_canopy: se veria una diferencia
que es de definicion y no del terreno.

LAS DOS VENTANAS TEMPORALES
---------------------------
GEDI aporta aca de sep. 2024 a mar. 2025. ATL08 acumula de nov. 2018 a abr. 2026,
y ademas cubre la hibernacion de GEDI entre marzo de 2023 y abril de 2024. El
script produce las dos comparaciones:

    todo        ATL08 completo. Mas muestra, menos comparable en el tiempo.
    ventana     ATL08 recortado a las fechas de GEDI. Comparable, y mucho menor.

Se informan las dos y se dice cuanta muestra queda en cada una. Elegir una sola y
callar la otra seria elegir el resultado.

ENTRADA   04_Tablas_de_trabajo/06_ICESat2/ATL08_<RECINTO>_<nivel>_utm.csv   (paso 12)
          04_Tablas_de_trabajo/0{1,2}_*/GEDI_<RECINTO>_validos_con_estructura.csv

SALIDA    05_Resultados/04_Tablas/TP2_cotejo_GEDI_ICESat2_celdas.csv
          05_Resultados/04_Tablas/TP2_cotejo_GEDI_ICESat2_resumen.csv
          05_Resultados/06_Control_calidad/ICESat2_ATL08/TP2_13_cotejo.log

Los archivos de entrada NO se tocan. Todo sale con nombre nuevo.

USO (entorno conda 'aoi'):   python TP2_13_cotejar_GEDI_ICESat2.py [nivel]

    Sin argumento coteja el nivel operacional, que es el del practico. Con
    "conservador" coteja ese nivel y agrega el sufijo _conservador a las tres
    salidas, para no pisar las operacionales que usa el paso 14.
"""
import csv
import math
import os
import statistics as est
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, os.path.join(TP2, "03_Scripts", "configuracion"))
from configuracion_comun import AOIS_UTM                            # noqa: E402

ATL08 = os.path.join(TP2, "04_Tablas_de_trabajo", "06_ICESat2")
TABLAS = os.path.join(TP2, "05_Resultados", "04_Tablas")
CONTROL = os.path.join(TP2, "05_Resultados", "06_Control_calidad", "ICESat2_ATL08")

GEDI_POR_RECINTO = {
    "BOSQUE_NW_02": os.path.join(TP2, "04_Tablas_de_trabajo", "01_Bosque",
                                 "GEDI_BOSQUE_NW_02_validos_con_estructura.csv"),
    "ESTEPA_NW_02": os.path.join(TP2, "04_Tablas_de_trabajo", "02_Estepa",
                                 "GEDI_ESTEPA_NW_02_validos_con_estructura.csv"),
}

CELDA = 500.0        # lado de la celda de comparacion, en metros
MIN_GEDI = 3         # huellas GEDI minimas para que la celda cuente
MIN_ATL = 3          # segmentos ATL08 minimos para que la celda cuente
NIVEL = "operacional"    # por omision; puede pasarse por linea de ordenes
if len(sys.argv) > 1:
    NIVEL = sys.argv[1].strip().lower()
if NIVEL not in ("operacional", "conservador"):
    sys.exit("Nivel desconocido: %r. Use operacional o conservador." % NIVEL)
SUFIJO = "" if NIVEL == "operacional" else "_" + NIVEL


# ------------------------------------------------------------------ AUXILIARES
def a_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def leer(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fecha_gedi(nombre_h5):
    """GEDI02_A_AAAADDDHHMMSS_... -> AAAA-MM-DD. Devuelve '' si no se reconoce."""
    import datetime as dt
    partes = nombre_h5.split("_")
    for p in partes:
        if len(p) == 13 and p.isdigit():
            anio, dia = int(p[:4]), int(p[4:7])
            try:
                d = dt.date(anio, 1, 1) + dt.timedelta(days=dia - 1)
                return d.isoformat()
            except ValueError:
                return ""
    return ""


def celda_de(este, norte, xmin, ymin):
    return (int((este - xmin) // CELDA), int((norte - ymin) // CELDA))


def spearman(pares):
    """Rho de Spearman sin scipy. Devuelve None con menos de 4 pares."""
    n = len(pares)
    if n < 4:
        return None

    def rangos(vals):
        orden = sorted(range(n), key=lambda i: vals[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vals[orden[j + 1]] == vals[orden[i]]:
                j += 1
            medio = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[orden[k]] = medio
            i = j + 1
        return r

    rx = rangos([p[0] for p in pares])
    ry = rangos([p[1] for p in pares])
    mx, my = est.mean(rx), est.mean(ry)
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    den = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n))
                    * sum((ry[i] - my) ** 2 for i in range(n)))
    return None if den == 0 else num / den


def resumen(valores):
    if not valores:
        return {}
    s = sorted(valores)
    if len(s) >= 4:
        q = est.quantiles(s, n=4, method="inclusive")
        p25, p75 = q[0], q[2]
    else:
        p25 = p75 = est.median(s)
    return {"n": len(s), "mediana": est.median(s), "p25": p25, "p75": p75,
            "min": s[0], "max": s[-1],
            "mad": est.median([abs(v - est.median(s)) for v in s])}


# ----------------------------------------------------------------------- CUERPO
def cargar_gedi(recinto):
    ruta = GEDI_POR_RECINTO[recinto]
    if not os.path.exists(ruta):
        return None
    puntos = []
    for x in leer(ruta):
        e, n, h = (a_float(x.get("este_utm19s")), a_float(x.get("norte_utm19s")),
                   a_float(x.get("rh98")))
        if None in (e, n, h):
            continue
        puntos.append((e, n, h, fecha_gedi(x.get("archivo", ""))))
    return puntos


def cargar_atl08(recinto, nivel):
    ruta = os.path.join(ATL08, "ATL08_%s_%s_utm.csv" % (recinto, nivel))
    if not os.path.exists(ruta):
        return None
    puntos = []
    for x in leer(ruta):
        e, n, h = (a_float(x.get("este_utm19s")), a_float(x.get("norte_utm19s")),
                   a_float(x.get("h_canopy_m")))
        if None in (e, n, h):
            continue
        # Los extremos ya vienen marcados por el paso 12; se dejan pasar porque
        # la mediana de la celda los absorbe, pero se cuentan.
        puntos.append((e, n, h, x.get("fecha", ""), x.get("extremo_3iqr", "")))
    return puntos


def agrupar(puntos, xmin, ymin):
    celdas = {}
    for p in puntos:
        celdas.setdefault(celda_de(p[0], p[1], xmin, ymin), []).append(p[2])
    return celdas


def cotejar(recinto, gedi, atl, etiqueta, filas_celdas):
    xmin, ymin, _, _ = AOIS_UTM[recinto]
    cg = agrupar(gedi, xmin, ymin)
    ca = agrupar(atl, xmin, ymin)
    comunes = sorted(set(cg) & set(ca))

    diferencias, pares = [], []
    niv_g, niv_a = [], []
    for c in comunes:
        vg, va = cg[c], ca[c]
        if len(vg) < MIN_GEDI or len(va) < MIN_ATL:
            continue
        mg, ma = est.median(vg), est.median(va)
        diferencias.append(ma - mg)
        pares.append((mg, ma))
        niv_g.append(mg)
        niv_a.append(ma)
        filas_celdas.append({
            "recinto": recinto,
            "ventana": etiqueta,
            "celda_col": c[0],
            "celda_fil": c[1],
            "este_centro": "%.1f" % (xmin + (c[0] + 0.5) * CELDA),
            "norte_centro": "%.1f" % (ymin + (c[1] + 0.5) * CELDA),
            "n_gedi": len(vg),
            "n_atl08": len(va),
            "mediana_gedi_rh98_m": "%.2f" % mg,
            "mediana_atl08_hcanopy_m": "%.2f" % ma,
            "diferencia_m": "%.2f" % (ma - mg),
        })

    r = resumen(diferencias)
    rho = spearman(pares)
    # El nivel de cada mision importa tanto como la diferencia: +4 m sobre 6 m no
    # es lo mismo que +4 m sobre 25 m. Sin esto la cifra se lee al reves.
    n_g = est.median(niv_g) if niv_g else None
    n_a = est.median(niv_a) if niv_a else None
    return {
        "recinto": recinto,
        "ventana": etiqueta,
        "celdas_con_ambos": len(comunes),
        "celdas_comparables": r.get("n", 0),
        "huellas_gedi": len(gedi),
        "segmentos_atl08": len(atl),
        "mediana_gedi_rh98_m": ("%.2f" % n_g) if n_g is not None else "",
        "mediana_atl08_hcanopy_m": ("%.2f" % n_a) if n_a is not None else "",
        "razon_atl08_sobre_gedi": ("%.2f" % (n_a / n_g)) if n_g else "",
        "mediana_diferencia_m": ("%.2f" % r["mediana"]) if r else "",
        "p25_diferencia_m": ("%.2f" % r["p25"]) if r else "",
        "p75_diferencia_m": ("%.2f" % r["p75"]) if r else "",
        "mad_diferencia_m": ("%.2f" % r["mad"]) if r else "",
        "min_diferencia_m": ("%.2f" % r["min"]) if r else "",
        "max_diferencia_m": ("%.2f" % r["max"]) if r else "",
        "spearman_rho": ("%.3f" % rho) if rho is not None else "",
    }


def main():
    os.makedirs(TABLAS, exist_ok=True)
    os.makedirs(CONTROL, exist_ok=True)
    filas_celdas, resumenes, avisos = [], [], []

    for recinto in ("BOSQUE_NW_02", "ESTEPA_NW_02"):
        gedi = cargar_gedi(recinto)
        atl = cargar_atl08(recinto, NIVEL)
        if gedi is None:
            avisos.append("FALTA la tabla GEDI de %s. Corra antes el paso 6." % recinto)
            continue
        if atl is None:
            avisos.append("FALTA la tabla ATL08 de %s. Corra antes el paso 12." % recinto)
            continue

        fg = sorted(p[3] for p in gedi if p[3])
        if not fg:
            avisos.append("No se pudo fechar ninguna huella GEDI de %s: la ventana "
                          "temporal no se aplica." % recinto)
            desde, hasta = "", ""
        else:
            desde, hasta = fg[0], fg[-1]

        resumenes.append(cotejar(recinto, gedi, atl, "todo", filas_celdas))

        if desde:
            atl_v = [p for p in atl if p[3] and desde <= p[3] <= hasta]
            if len(atl_v) < MIN_ATL:
                avisos.append("En la ventana de GEDI (%s a %s) quedan %d segmentos "
                              "ATL08 en %s: no alcanza para cotejar."
                              % (desde, hasta, len(atl_v), recinto))
            resumenes.append(cotejar(recinto, gedi, atl_v,
                                     "ventana_gedi_%s_a_%s" % (desde, hasta),
                                     filas_celdas))

        extremos = sum(1 for p in atl if p[4] == "SI")
        if extremos:
            avisos.append("%s: %d segmentos ATL08 marcados como extremos 3 IQR "
                          "entraron al cotejo; la mediana por celda los absorbe."
                          % (recinto, extremos))

    if not resumenes:
        print("No se pudo cotejar nada.")
        for a in avisos:
            print("  " + a)
        return 1

    f_celdas = os.path.join(TABLAS, "TP2_cotejo_GEDI_ICESat2_celdas%s.csv" % SUFIJO)
    with open(f_celdas, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas_celdas[0].keys()))
        w.writeheader()
        w.writerows(filas_celdas)

    f_res = os.path.join(TABLAS, "TP2_cotejo_GEDI_ICESat2_resumen%s.csv" % SUFIJO)
    with open(f_res, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(resumenes[0].keys()))
        w.writeheader()
        w.writerows(resumenes)

    lineas = []
    lineas.append("COTEJO GEDI (rh98) CONTRA ICESat-2 ATL08 (h_canopy)")
    lineas.append("celda de %d m, minimo %d huellas GEDI y %d segmentos ATL08 por celda"
                  % (int(CELDA), MIN_GEDI, MIN_ATL))
    lineas.append("nivel ATL08: %s" % NIVEL)
    lineas.append("")
    for r in resumenes:
        lineas.append("%s | %s" % (r["recinto"], r["ventana"]))
        lineas.append("   celdas con ambas misiones: %d, comparables: %d"
                      % (r["celdas_con_ambos"], r["celdas_comparables"]))
        lineas.append("   huellas GEDI %d, segmentos ATL08 %d"
                      % (r["huellas_gedi"], r["segmentos_atl08"]))
        if r["mediana_diferencia_m"] != "":
            lineas.append("   nivel por celda: GEDI %s m, ATL08 %s m  (razon %s x)"
                          % (r["mediana_gedi_rh98_m"], r["mediana_atl08_hcanopy_m"],
                             r["razon_atl08_sobre_gedi"]))
            lineas.append("   diferencia mediana pareada (ATL08 - GEDI): %s m  [p25 %s, p75 %s]"
                          % (r["mediana_diferencia_m"], r["p25_diferencia_m"],
                             r["p75_diferencia_m"]))
            lineas.append("   Spearman entre medianas de celda: %s" % (r["spearman_rho"] or "sin datos"))
        else:
            lineas.append("   sin celdas comparables")
        lineas.append("")
    if avisos:
        lineas.append("AVISOS")
        for a in avisos:
            lineas.append("   " + a)
        lineas.append("")
    lineas.append("COMO SE LEE ESTO")
    lineas.append("   Lea la diferencia junto al nivel, nunca sola. Una diferencia de 4 m")
    lineas.append("   sobre un dosel de 6 m no es lo mismo que sobre uno de 25 m: la razon")
    lineas.append("   dice cuanto pesa en proporcion, y es la cifra que hay que informar.")
    lineas.append("")
    lineas.append("   La diferencia mediana NO es el error de GEDI: es la discrepancia")
    lineas.append("   entre dos estimaciones satelitales, ninguna verificada en el suelo.")
    lineas.append("   Sirve como cota inferior de la incertidumbre de la referencia, y")
    lineas.append("   como aviso: donde las dos misiones no coinciden, cualquier modelo")
    lineas.append("   calibrado contra una sola hereda esa discrepancia sin declararla.")
    lineas.append("")
    lineas.append("   Si la discrepancia resulta mayor en la estepa que en el bosque,")
    lineas.append("   antes de explicarla por el terreno conviene mirar los errores")
    lineas.append("   conocidos de ATL08 (06_Bibliografia/04_Enlaces): la clasificacion")
    lineas.append("   de fotones de copa y de terreno es mas dificil donde la vegetacion")
    lineas.append("   es baja y rala, que es justamente la estepa.")

    texto = "\n".join(lineas)
    with open(os.path.join(CONTROL, "TP2_13_cotejo%s.log" % SUFIJO), "w", encoding="utf-8") as f:
        f.write(texto + "\n")
    print(texto)
    print("Celdas:  %s" % f_celdas)
    print("Resumen: %s" % f_res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
