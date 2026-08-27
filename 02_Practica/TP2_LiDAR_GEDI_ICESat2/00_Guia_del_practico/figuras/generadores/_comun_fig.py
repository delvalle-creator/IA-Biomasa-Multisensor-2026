# -*- coding: utf-8 -*-
"""Utilidades compartidas por los generadores de figuras del TP2.

Escrito el 29/07/2026: el TP2 era el unico practico cuyas figuras no tenian
generador, de modo que no habia forma de rehacerlas cuando cambiaban los datos.
Las seis figuras del TP2 se dibujaban a mano y quedaron congeladas con el
filtrado viejo (sensibilidad 0,95 y sin filtro de pendiente).

REGLAS QUE CUMPLEN TODOS LOS GENERADORES
  - La leyenda NUNCA tapa el dibujo: va en una franja debajo del eje.
  - Los numeros NO se escriben a mano: se leen de los CSV de 05_Resultados.
  - Cada figura deja PNG (para el .docx), SVG con el texto editable, y un
    .pptx donde cada rotulo es un cuadro de texto de PowerPoint.
"""
import csv, glob, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from _a_pptx import a_pptx

AQUI = os.path.dirname(os.path.abspath(__file__))
FIGURAS = os.path.abspath(os.path.join(AQUI, ".."))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
TABLAS = os.path.join(TP2, "05_Resultados", "04_Tablas")
CONTROL = os.path.join(TP2, "05_Resultados", "06_Control_calidad")
SUBSETS = os.path.join(TP2, "04_Tablas_de_trabajo")
GRAFICOS = os.path.join(TP2, "05_Resultados", "05_Graficos")

VERDE, ROJO, AZUL, NARANJA = "#2d6a4f", "#a50f15", "#1d3557", "#d97706"
ARENA, GRIS, MARRON = "#e9c46a", "#9aa5b1", "#8d5524"
AOIS = {"BOSQUE_NW_02": (-71.5978, -42.6953, -71.4095, -42.5562),
        "ESTEPA_NW_02": (-71.2138, -42.8468, -71.0258, -42.7084)}
SITIOS = [("BOSQUE_NW_02", "Bosque"), ("ESTEPA_NW_02", "Estepa")]

plt.rcParams.update({"font.family": "serif", "font.size": 12,
                     "axes.spines.top": False, "axes.spines.right": False,
                     # texto editable dentro del SVG (si no, cada letra es un trazado)
                     "svg.fonttype": "none"})


def leer(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def col(filas, campo, tipo=float):
    out = []
    for r in filas:
        v = (r.get(campo) or "").strip()
        if not v:
            continue
        try:
            out.append(tipo(v))
        except ValueError:
            pass
    return np.array(out)


def calidad():
    """{aoi: {'total':, 'aceptados':, 'motivos':[(nombre, cantidad), ...]}}"""
    d = {}
    for r in leer(os.path.join(CONTROL, "filtrado_calidad.csv")):
        a = d.setdefault(r["aoi"], {"total": int(r["disparos_totales"]),
                                    "aceptados": int(r["aceptados"]), "motivos": []})
        a["motivos"].append((r["motivo"], int(r["cantidad"])))
    return d


def pendiente():
    d = {}
    for r in leer(os.path.join(CONTROL, "filtrado_pendiente.csv")):
        d[r["aoi"]] = {"entraron": int(r["entraron_tras_calidad"]),
                       "validos": int(r["validos_finales"]),
                       "descartados": int(r["descartados_pendiente"]),
                       "mediana": float(r["pendiente_mediana_grados"]),
                       "umbral": float(r["umbral_grados"])}
    return d


def validos(aoi):
    sub = "01_Bosque" if aoi.startswith("BOSQUE") else "02_Estepa"
    return leer(os.path.join(SUBSETS, sub, "GEDI_%s_validos_con_estructura.csv" % aoi))


def biomasa(aoi):
    return leer(os.path.join(TABLAS, "biomasa_%s.csv" % aoi))


def coma(x, dec=2):
    return ("%.*f" % (dec, x)).replace(".", ",")


def guardar(fig, nombre, dpi=110):
    """PNG para el .docx, SVG editable y .pptx con cada rotulo como texto."""
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(FIGURAS, nombre + "." + ext), dpi=dpi,
                    bbox_inches="tight")
    a_pptx(fig, nombre, os.path.join(FIGURAS, "editables_pptx"))
    p = os.path.join(FIGURAS, nombre + ".png")
    print("  -> %s.png (%.1f MB), .svg y .pptx" % (nombre, os.path.getsize(p) / 1e6))
