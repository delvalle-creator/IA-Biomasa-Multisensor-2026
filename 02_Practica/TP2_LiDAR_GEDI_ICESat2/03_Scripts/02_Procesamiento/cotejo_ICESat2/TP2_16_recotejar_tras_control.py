# -*- coding: utf-8 -*-
"""
TP2_16_recotejar_tras_control.py  ---> repite la pregunta del paso 13 despues
                                       del control de terreno del paso 15.

POR QUE HACIA FALTA
-------------------
El paso 13 midio el desacuerdo GEDI-ATL08 con TODOS los segmentos: 2,70x en el
bosque, 3,28x en la estepa. El paso 15 mostro que una parte de los segmentos
tiene el terreno mal detectado (|delta| > 5 m contra FABDEM). Este paso repite
EXACTAMENTE el mismo cotejo -- misma grilla de 500 m, misma mediana por celda,
mismas dos ventanas temporales -- pero solo con los segmentos que PASAN el
control. La diferencia entre ambos resultados es la parte del desacuerdo que
era del terreno; lo que queda es la parte que no lo es.

LO QUE DA, Y COMO SE LEE
------------------------
En el bosque la razon baja (los segmentos con suelo malo inflaban h_canopy):
el desacuerdo era en buena parte corregible, y quedo corregido POR DESCARTE,
nunca restando FABDEM a ninguna altura. En la estepa la razon casi no se
mueve: el desacuerdo ahi no es del terreno sino de la clasificacion de
fotones de copa en vegetacion baja y rala -- el limite metodologico que ya
anticipaba el log del paso 13.

ENTRADA   04_Tablas_de_trabajo/06_ICESat2/ATL08_<RECINTO>_<nivel>_terreno_utm.csv  (paso 15)
          04_Tablas_de_trabajo/0{1,2}_*/GEDI_<RECINTO>_validos_con_estructura.csv

SALIDA    05_Resultados/04_Tablas/TP2_cotejo_GEDI_ICESat2_celdas_terreno[_conservador].csv
          05_Resultados/04_Tablas/TP2_cotejo_GEDI_ICESat2_resumen_terreno[_conservador].csv
          05_Resultados/06_Control_calidad/ICESat2_ATL08/TP2_16_recotejo[_conservador].log

Los archivos de entrada NO se tocan. Todo sale con nombre nuevo: las salidas
del paso 13 quedan intactas para poder poner ANTES y DESPUES lado a lado.

USO (entorno conda 'aoi'):   python TP2_16_recotejar_tras_control.py [nivel]

    Sin argumento re-coteja el nivel operacional; con "conservador", ese.
    Las constantes del cotejo (celda de 500 m, minimos por celda) son las del
    paso 13; si alguna vez cambian alla, deben cambiar aca.
"""
import csv
import datetime as dt
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

CELDA = 500.0        # identicas al paso 13: el cotejo debe ser el MISMO
MIN_GEDI = 3
MIN_ATL = 3
NIVEL = "operacional"
if len(sys.argv) > 1:
    NIVEL = sys.argv[1].strip().lower()
if NIVEL not in ("operacional", "conservador"):
    sys.exit("Nivel desconocido: %r. Use operacional o conservador." % NIVEL)
SUFIJO = "_terreno" if NIVEL == "operacional" else "_terreno_conservador"


# ------------------------------------------------ AUXILIARES (como en el paso 13)
def a_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def leer(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fecha_gedi(nombre_h5):
    partes = nombre_h5.split("_")
    for p in partes:
        if len(p) == 13 and p.isdigit():
            anio, dia = int(p[:4]), int(p[4:7])
            try:
                return (dt.date(anio, 1, 1) + dt.timedelta(days=dia - 1)).isoformat()
            except ValueError:
                return ""
    return ""


def celda_de(este, norte, xmin, ymin):
    return (int((este - xmin) // CELDA), int((norte - ymin) // CELDA))


def spearman(pares):
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


def cargar_atl08_controlado(recinto, nivel):
    ruta = os.path.join(ATL08, "ATL08_%s_%s_terreno_utm.csv" % (recinto, nivel))
    if not os.path.exists(ruta):
        return None
    puntos = []
    for x in leer(ruta):
        e, n, h = (a_float(x.get("este_utm19s")), a_float(x.get("norte_utm19s")),
                   a_float(x.get("h_canopy_m")))
        if None in (e, n, h):
            continue
        puntos.append((e, n, h, x.get("fecha", "")))
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

    diferencias, pares, niv_g, niv_a = [], [], [], []
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
            "recinto": recinto, "ventana": etiqueta,
            "celda_col": c[0], "celda_fil": c[1],
            "este_centro": "%.1f" % (xmin + (c[0] + 0.5) * CELDA),
            "norte_centro": "%.1f" % (ymin + (c[1] + 0.5) * CELDA),
            "n_gedi": len(vg), "n_atl08": len(va),
            "mediana_gedi_rh98_m": "%.2f" % mg,
            "mediana_atl08_hcanopy_m": "%.2f" % ma,
            "diferencia_m": "%.2f" % (ma - mg),
        })

    r = resumen(diferencias)
    rho = spearman(pares)
    n_g = est.median(niv_g) if niv_g else None
    n_a = est.median(niv_a) if niv_a else None
    return {
        "recinto": recinto, "ventana": etiqueta,
        "celdas_con_ambos": len(comunes),
        "celdas_comparables": r.get("n", 0),
        "huellas_gedi": len(gedi), "segmentos_atl08": len(atl),
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
        atl = cargar_atl08_controlado(recinto, NIVEL)
        if gedi is None:
            avisos.append("FALTA la tabla GEDI de %s. Corra antes el paso 6." % recinto)
            continue
        if atl is None:
            avisos.append("FALTA ATL08_%s_%s_terreno_utm.csv. Corra antes el paso 15."
                          % (recinto, NIVEL))
            continue

        fg = sorted(p[3] for p in gedi if p[3])
        desde, hasta = (fg[0], fg[-1]) if fg else ("", "")

        resumenes.append(cotejar(recinto, gedi, atl, "todo", filas_celdas))
        if desde:
            atl_v = [p for p in atl if p[3] and desde <= p[3] <= hasta]
            resumenes.append(cotejar(recinto, gedi, atl_v,
                                     "ventana_gedi_%s_a_%s" % (desde, hasta),
                                     filas_celdas))

    if not resumenes:
        print("No se pudo re-cotejar nada.")
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
    lineas.append("RE-COTEJO GEDI (rh98) CONTRA ATL08 (h_canopy) TRAS EL CONTROL DE TERRENO")
    lineas.append("mismos parametros que el paso 13: celda %d m, minimos %d y %d"
                  % (int(CELDA), MIN_GEDI, MIN_ATL))
    lineas.append("nivel ATL08: %s, solo segmentos control_terreno = PASA" % NIVEL)
    lineas.append("")
    for r in resumenes:
        lineas.append("%s | %s" % (r["recinto"], r["ventana"]))
        lineas.append("   celdas con ambas misiones: %d, comparables: %d"
                      % (r["celdas_con_ambos"], r["celdas_comparables"]))
        lineas.append("   huellas GEDI %d, segmentos ATL08 (controlados) %d"
                      % (r["huellas_gedi"], r["segmentos_atl08"]))
        if r["mediana_diferencia_m"] != "":
            lineas.append("   nivel por celda: GEDI %s m, ATL08 %s m  (razon %s x)"
                          % (r["mediana_gedi_rh98_m"], r["mediana_atl08_hcanopy_m"],
                             r["razon_atl08_sobre_gedi"]))
            lineas.append("   diferencia mediana pareada (ATL08 - GEDI): %s m  [p25 %s, p75 %s]"
                          % (r["mediana_diferencia_m"], r["p25_diferencia_m"],
                             r["p75_diferencia_m"]))
            lineas.append("   Spearman entre medianas de celda: %s"
                          % (r["spearman_rho"] or "sin datos"))
        else:
            lineas.append("   sin celdas comparables")
        lineas.append("")
    if avisos:
        lineas.append("AVISOS")
        for a in avisos:
            lineas.append("   " + a)
        lineas.append("")
    lineas.append("COMO SE LEE ESTO")
    lineas.append("   Compare cada cifra con la del paso 13 (mismo nombre de archivo sin")
    lineas.append("   el sufijo _terreno). Lo que bajo era terreno mal detectado; lo que")
    lineas.append("   no bajo es la parte del desacuerdo que el terreno no explica. En")
    lineas.append("   este AOI: el bosque baja de 2,70x hacia ~1,9x, la estepa casi no")
    lineas.append("   se mueve. La estepa no tiene arreglo por filtrado: es el limite de")
    lineas.append("   clasificar fotones de copa donde el dosel mide menos que el ruido")
    lineas.append("   del terreno. Declararlo tambien es un resultado.")

    texto = "\n".join(lineas)
    with open(os.path.join(CONTROL, "TP2_16_recotejo%s.log"
                           % ("" if NIVEL == "operacional" else "_conservador")),
              "w", encoding="utf-8") as f:
        f.write(texto + "\n")
    print(texto)
    print("Celdas:  %s" % f_celdas)
    print("Resumen: %s" % f_res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
