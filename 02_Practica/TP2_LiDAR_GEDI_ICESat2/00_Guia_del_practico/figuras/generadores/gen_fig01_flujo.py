# -*- coding: utf-8 -*-
"""Figura 2.1 de la guia del TP2: la secuencia de pasos, en pagina apaisada.

Los pasos son los del archivo TP2_LiDAR_GEDI_ICESat2/03_Scripts/00_ORDEN_DE_EJECUCION.md:
DIECISIETE pasos numerados, del 1 al 17, mas el paso 1b, que va intercalado
entre el 1 y el 2 porque el paso 7 necesita lo que produce. Dieciocho cajas en
total, en tres filas: en la tercera, en celeste, la rama ICESat-2 (pasos 12 a
16, con el control de terreno FABDEM de los pasos 15 y 16), y en amarillo el
paso 17, el mapa de biomasa GEDI contra el CCI.

La figura va en pagina apaisada: a 24,6 cm de ancho las cajas admiten cuerpo
legible. En vertical, a 15,5 cm, la letra quedaba ilegible.

Uso:  python gen_fig01_flujo.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.abspath(os.path.join(AQUI, ".."))

SERIF = "Liberation Serif"
plt.rcParams["font.family"] = SERIF
plt.rcParams["svg.fonttype"] = "none"
GRIS, NARANJA, AZUL, VERDE, LILA = "#DEE2E6", "#FFD6A5", "#CAF0F8", "#B7E4C7", "#DCC9E8"
CELESTE = "#BDE0FE"          # la rama ICESat-2
AMARILLO = "#FDF3B4"         # el mapa contra el CCI
BORDE = "#1D3557"

PASOS = [("1",  "TP2_01", "Descargar\nGEDI (.h5)",   GRIS),
         ("1b", "TP2_01b", "Descargar\nel L4A",      GRIS),
         ("2",  "TP2_02", "Recortar\nal AOI",        GRIS),
         ("3",  "TP2_03", "Filtrar\ncalidad",        NARANJA),
         ("4",  "TP2_04", "DEM y\npendiente",        AZUL),
         ("5",  "TP2_05", "Filtrar\npendiente",      NARANJA),
         ("6",  "TP2_06", "Métricas de\nestructura", VERDE),
         ("7",  "TP2_07", "Biomasa de\nreferencia",  VERDE),
         ("8",  "TP2_08", "Exportar\npara QGIS",     VERDE),
         ("9",  "TP2_09", "Clase de\ncobertura",     LILA),
         ("10", "TP2_10", "Auditar\nel L4A",         LILA),
         ("11", "TP2_11", "Escenarios\nhoja caída",  LILA),
         ("12", "TP2_12", "Cargar y\nproyectar ATL08",   CELESTE),
         ("13", "TP2_13", "Cotejar\nGEDI–ICESat-2",      CELESTE),
         ("14", "TP2_14", "Exportar cotejo\npara QGIS",  CELESTE),
         ("15", "TP2_15", "Control de terreno\n(FABDEM)",   CELESTE),
         ("16", "TP2_16", "Re-cotejo tras\nel control",     CELESTE),
         ("17", "TP2_17", "Mapa AGB\nGEDI–CCI",             AMARILLO)]
FASES = [(0, 2,  "Ya ejecutados",                     "#6C757D"),
         (3, 5,  "Filtrado: el corazón del práctico", "#E8590C"),
         (6, 8,  "Productos para TP3-TP5",            "#2D6A4F"),
         (9, 11, "Auditoría por clase de cobertura",  "#6F42C1"),
         (12, 16, "Rama ICESat-2: la segunda referencia, con su control de terreno", "#1D6FB8"),
         (17, 17, "El mapa", "#8B7A00")]

COLS = 6
fig, ax = plt.subplots(figsize=(21.4, 14.2), dpi=100)
ax.set_xlim(0, 100); ax.set_ylim(142, 0); ax.axis("off")
fig.subplots_adjust(0, 0, 1, 1)

M, SEP = 2.6, 1.5
ancho = (100 - 2*M - SEP*(COLS-1)) / COLS
ALTO = 27.0
Y = [17.0, 62.0, 107.0]

def caja(i):
    f, c = divmod(i, COLS)
    return M + c*(ancho+SEP), Y[f]

for i, (num, cod, que, color) in enumerate(PASOS):
    x, y = caja(i)
    ax.add_patch(FancyBboxPatch((x, y), ancho, ALTO,
        boxstyle="round,pad=0,rounding_size=0.5", facecolor=color,
        edgecolor=BORDE, lw=2.0))
    ax.text(x+ancho/2, y+ALTO*0.24, "paso %s" % num, ha="center", va="center",
            fontsize=17, color="#555555", family=SERIF)
    ax.text(x+ancho/2, y+ALTO*0.50, cod, ha="center", va="center",
            fontsize=25, fontweight="bold", color="#111111", family=SERIF)
    ax.text(x+ancho/2, y+ALTO*0.79, que, ha="center", va="center",
            fontsize=20, color="#111111", family=SERIF, linespacing=1.35)
    if i < len(PASOS)-1 and caja(i+1)[1] == y:
        ax.annotate("", xy=(caja(i+1)[0]-0.15, y+ALTO/2), xytext=(x+ancho+0.15, y+ALTO/2),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.55",
                                    color=BORDE, lw=2.0))

x0, y0 = caja(0)
ax.add_patch(Rectangle((x0-0.8, y0-1.0), 3*ancho+2*SEP+1.6, ALTO+2.0,
                       fill=False, edgecolor="#6C757D", lw=1.4, linestyle=(0,(1,2))))

for a, b, rot, col in FASES:
    xa, ya = caja(a); xb, _ = caja(b)
    ax.text((xa+xb+ancho)/2, ya-5.2, rot, ha="center", va="center",
            fontsize=21, fontstyle="italic", color=col, family=SERIF)

ax.text(50, 136.0,
        "Diecisiete pasos numerados, del 1 al 17, más el 1b, que se intercala porque el paso 7 necesita lo que produce.",
        ha="center", va="center", fontsize=19, color="#333333", family=SERIF)
ax.text(50, 140.0,
        "Cada paso consume lo que dejó el anterior; la rama ICESat-2 (12 a 16) corre aparte: el 13 y el 16 leen, además, la salida del paso 6.",
        ha="center", va="center", fontsize=19, color="#333333", family=SERIF)

fig.savefig(os.path.join(SALIDA, "fig01_flujo.png"), dpi=100, facecolor="white")
fig.savefig(os.path.join(SALIDA, "fig01_flujo.svg"), facecolor="white")
print("generada en %s" % SALIDA)
