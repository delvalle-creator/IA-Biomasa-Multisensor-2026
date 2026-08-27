# -*- coding: utf-8 -*-
"""Figura: la secuencia de los SEIS scripts del TP3.

La version dibujada a mano tenia cinco cajas donde el texto y la Tabla 3.2 hablan
de seis: faltaba TP3_06_exportar_para_gis.py, que es el que deja los resultados
listos para QGIS. Uso:  python gen_tp3_flujo.py
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from _comun_fig import *

GRIS = "#9aa5b1"          # el modulo comun del TP3 no lo define; el del TP4 si

PASOS = [
    ("1", "TP3_01_recortar_sentinel2", "Recorta Sentinel-2\na la grilla común", GRIS),
    ("2", "TP3_02_landsat9", "Lo mismo con\nLandsat 9", GRIS),
    ("3", "TP3_03_indices", "NDVI, EVI,\nNDMI y NBR", AZUL),
    ("4", "TP3_04_dnbr_incendio", "dNBR y las siete\nclases de severidad", ROJO),
    ("5", "TP3_05_saturacion_y_modelo", "Índices contra la\naltura de GEDI", AZUL),
    ("6", "TP3_06_exportar_para_gis", "Estilos .qml y\nvectores para QGIS", VERDE),
]
FILAS, COLS = 2, 3
# Recorrido en boustrofedon, igual que el flujo del TP2: la flecha de cambio de
# renglon es un tramo corto y vertical y no cruza por encima de las cajas.
fig, ax = plt.subplots(figsize=(15, 6.2))
ax.set_xlim(0.3, COLS * 10 - 0.3); ax.set_ylim(1.4, FILAS * 10 - 1.4)
ax.axis("off"); ax.invert_yaxis()
pos = []
for i in range(len(PASOS)):
    f, c = divmod(i, COLS)
    if f % 2:
        c = COLS - 1 - c
    pos.append((c * 10 + 5, f * 10 + 5))
for i, (num, nombre, que, color) in enumerate(PASOS):
    x, y = pos[i]
    ax.add_patch(FancyBboxPatch((x - 4.3, y - 3.0), 8.6, 6.0,
                                boxstyle="round,pad=0.15,rounding_size=0.5",
                                facecolor=color, alpha=0.16, edgecolor=color, lw=2.0))
    ax.text(x, y - 1.9, "paso %s" % num, ha="center", va="center",
            fontsize=11, fontweight="bold", color=color)
    ax.text(x, y - 0.4, nombre, ha="center", va="center", fontsize=11, family="monospace")
    ax.text(x, y + 1.6, que, ha="center", va="center", fontsize=11, color="#333333")
    if i < len(PASOS) - 1:
        x2, y2 = pos[i + 1]
        if y2 == y:
            d = 1 if x2 > x else -1
            ax.annotate("", xy=(x2 - d * 4.5, y), xytext=(x + d * 4.5, y),
                        arrowprops=dict(arrowstyle="-|>", color="#666666", lw=2.2))
        else:
            ax.annotate("", xy=(x, y2 - 3.2), xytext=(x, y + 3.2),
                        arrowprops=dict(arrowstyle="-|>", color="#666666", lw=2.2))
fig.suptitle("Los seis scripts del TP3, en orden de ejecución\n"
             "los pasos 1 y 2 ya fueron ejecutados: prepararon las imágenes en la grilla común",
             fontweight="bold", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.93])
guardar(fig, "tp3_flujo")
