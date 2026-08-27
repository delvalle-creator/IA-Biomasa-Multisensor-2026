# -*- coding: utf-8 -*-
"""Utilidades compartidas por los generadores de figuras del TP3."""
import glob, os
import numpy as np, rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from _a_pptx import a_pptx

AQUI = os.path.dirname(os.path.abspath(__file__))
FIGURAS = os.path.abspath(os.path.join(AQUI, ".."))
PROY = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
S2 = os.path.join(PROY, "TP3_Datos_Opticos", "02_Subsets_SNAP_QGIS", "Sentinel_2")
# LAS HUELLAS SON LAS *VALIDAS* DEL TP2, NO LAS "ACEPTADAS". Corregido el
# 29/07/2026. "Aceptadas" (1.025 en el bosque) son las que pasaron el filtro de
# calidad del L2A; "validas" (690) son las que ademas pasaron el filtro de
# PENDIENTE de 20 grados y tienen estructura del L2B. Son las que el TP2 declara
# como su producto y las que consumen el TP3, el TP4 y el TP5.
#
# No es un detalle de contabilidad: en una ladera el pulso de GEDI abarca 25 m de
# desnivel y el rh95 sale inflado, de modo que las huellas de pendiente meten
# ruido justo en la variable que estas figuras miden. Comprobado: con las validas
# el R2 del gamma0 de banda L contra la altura SUBE (SAOCOM 0,127 -> 0,180;
# PALSAR-2 0,167 -> 0,190) y las conclusiones no cambian.
GEDI = os.path.join(PROY, "TP2_LiDAR_GEDI_ICESat2", "04_Tablas_de_trabajo")
SUB = {"BOSQUE_NW_02": "01_Bosque", "ESTEPA_NW_02": "02_Estepa"}


def csv_gedi(aoi):
    return os.path.join(GEDI, SUB[aoi], "GEDI_%s_validos_con_estructura.csv" % aoi)
MAL = [0, 1, 3, 8, 9, 10, 11]
PRE, POST = "*20251125*.tif", "*20260305*.tif"
BANDAS = [("B2", 492, "Azul"), ("B3", 560, "Verde"), ("B4", 665, "Rojo"),
          ("B5", 704, ""), ("B6", 740, ""), ("B7", 783, ""), ("B8", 833, "NIR"),
          ("B8A", 865, ""), ("B11", 1610, "SWIR1"), ("B12", 2190, "SWIR2")]
VERDE, ROJO, AZUL, NARANJA = "#2d6a4f", "#a50f15", "#1d3557", "#d97706"
plt.rcParams.update({"font.family": "serif", "font.size": 12,
                     "axes.spines.top": False, "axes.spines.right": False,
                     # svg.fonttype="none" deja los textos como TEXTO dentro del
                     # SVG en vez de convertirlos en trazados. Sin esto el SVG se
                     # abre en Inkscape pero cada letra es un dibujo y NO se le
                     # puede cambiar el cuerpo ni el tipo de letra. Puesto el
                     # 29/07/2026, a pedido del docente, para poder ajustar los
                     # tamanos de letra al armar la guia general.
                     "svg.fonttype": "none"})

def escena(aoi, pat):
    return sorted(glob.glob(os.path.join(S2, "*", aoi, pat)))[0]

def guardar(fig, nombre, dpi=110):
    """Guarda PNG (para Word) y SVG (editable en Inkscape/Illustrator).

    110 ppp sobre una figura de 16 cm de ancho da ~1.700 px: mas que suficiente
    para imprimir. Con 150 ppp los mapas pesaban 7 MB y algunos conversores a PDF
    los descartaban sin avisar."""
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(FIGURAS, nombre + "." + ext), dpi=dpi,
                    bbox_inches="tight")
    a_pptx(fig, nombre, os.path.join(FIGURAS, "editables_pptx"))
    p = os.path.join(FIGURAS, nombre + ".png")
    print("  -> %s.png (%.1f MB) y %s.svg" % (nombre, os.path.getsize(p) / 1e6, nombre))
