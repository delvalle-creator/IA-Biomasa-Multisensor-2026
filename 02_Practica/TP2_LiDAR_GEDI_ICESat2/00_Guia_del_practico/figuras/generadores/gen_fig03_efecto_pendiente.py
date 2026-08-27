# -*- coding: utf-8 -*-
"""Figura: por que la pendiente distorsiona la altura del dosel.

Esquema conceptual con UN numero real: el desnivel que cabe dentro de la huella
de 25 m en una ladera del angulo indicado, que es 25 * tan(angulo). En 30 grados
son 14,4 m, mas que el arbol tipico de este bosque (mediana 5,07 m). Por eso el
TP2 descarta las huellas con pendiente mayor que el umbral.
Uso:  python gen_fig03_efecto_pendiente.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
from _comun_fig import *

HUELLA = 25.0
CASOS = [(0.0, "Terreno llano"), (30.0, "Ladera de 30°")]
PEN = pendiente()
UMBRAL = PEN["BOSQUE_NW_02"]["umbral"]

fig, ax = plt.subplots(1, 2, figsize=(15, 6.6))
for k, (grados, titulo) in enumerate(CASOS):
    a = ax[k]
    desnivel = HUELLA * np.tan(np.radians(grados))
    x = np.array([-6.0, HUELLA + 6.0])
    suelo = (x - x[0]) * np.tan(np.radians(grados))
    a.plot(x, suelo, color=MARRON, lw=3, zorder=2)
    a.fill_between(x, suelo - 40, suelo, color=ARENA, alpha=0.55, zorder=1)
    for cx in (3.0, 12.5, 22.0):
        base = (cx - x[0]) * np.tan(np.radians(grados))
        a.add_patch(Rectangle((cx - 0.5, base), 1.0, 3.0, facecolor=MARRON, lw=0, zorder=3))
        a.add_patch(Ellipse((cx, base + 5.0), 8.0, 5.4, facecolor=VERDE, alpha=0.55,
                            lw=0, zorder=3))
    y0 = (0 - x[0]) * np.tan(np.radians(grados))
    y1 = (HUELLA - x[0]) * np.tan(np.radians(grados))
    a.plot([0, 0], [y0 - 3, y0 + 26], color=ROJO, ls=":", lw=1.6, zorder=4)
    a.plot([HUELLA, HUELLA], [y1 - 3, y1 + 26], color=ROJO, ls=":", lw=1.6, zorder=4)
    a.annotate("", xy=(HUELLA, y0 - 2.4), xytext=(0, y0 - 2.4),
               arrowprops=dict(arrowstyle="<|-|>", color=ROJO, lw=2.2))
    a.text(HUELLA / 2.0, y0 - 4.6, "huella ≈ 25 m", ha="center", fontsize=12.5, color=ROJO)
    if grados > 0:
        a.annotate("", xy=(HUELLA + 3.2, y1), xytext=(HUELLA + 3.2, y0),
                   arrowprops=dict(arrowstyle="<|-|>", color=AZUL, lw=2.4))
        a.text(HUELLA + 4.2, (y0 + y1) / 2.0,
               "%s m de desnivel\nDENTRO de la misma huella" % coma(desnivel, 1),
               fontsize=12.5, color=AZUL, va="center", fontweight="bold")
        a.text(HUELLA / 2.0 + 3.0, y1 + 6.0,
               "el suelo del borde alto llega ANTES\nque la copa del borde bajo:\n"
               "el rh95 sale inflado",
               ha="center", fontsize=12, color=ROJO)
    else:
        a.text(HUELLA / 2.0, y0 + 21.0,
               "todo el suelo de la huella está\na la misma altura:\n"
               "el rh95 mide el árbol",
               ha="center", fontsize=12, color=VERDE)
    a.set_xlim(-7, HUELLA + 17); a.set_ylim(-8, 31)
    a.set_aspect("equal"); a.axis("off")
    a.set_title(titulo, fontweight="bold", fontsize=14)

fig.suptitle("Por qué la pendiente distorsiona la altura del dosel, y por qué se filtra\n"
             "en el TP2 se descarta toda huella con pendiente mayor que %s°"
             % coma(UMBRAL, 0),
             fontweight="bold", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.91])
guardar(fig, "fig03_efecto_pendiente")
print("   desnivel dentro de la huella: %.1f m a 30°, contra una mediana de dosel de 5,07 m"
      % (HUELLA * np.tan(np.radians(30))))
