# -*- coding: utf-8 -*-
"""Figura: como mide GEDI. Es un esquema conceptual, no datos.

Izquierda: la huella de unos 25 m sobre el dosel. Derecha: la forma de onda que
vuelve, con el primer retorno en la copa, el ultimo en el suelo, y los percentiles
de altura relativa (rh) que se derivan de ella.
Uso:  python gen_fig02_como_mide_gedi.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
from _comun_fig import *

fig, ax = plt.subplots(1, 2, figsize=(15, 6.4),
                       gridspec_kw={"width_ratios": [1, 1.15]})

# ---------------------------------------------------------------- izquierda
a = ax[0]
a.set_xlim(0, 10); a.set_ylim(-0.6, 10); a.axis("off")
a.add_patch(Rectangle((0.2, 0.0), 9.6, 1.5, facecolor=ARENA, alpha=0.75, lw=0))
a.text(9.6, 0.75, "suelo", ha="right", va="center", fontsize=12, color=MARRON)
for cx in (2.8, 5.0, 7.2):
    a.add_patch(Rectangle((cx - 0.16, 1.4), 0.32, 2.1, facecolor=MARRON, lw=0))
    a.add_patch(Ellipse((cx, 5.0), 3.1, 3.0, facecolor=VERDE, alpha=0.45, lw=0))
    a.add_patch(Ellipse((cx, 5.6), 2.2, 2.0, facecolor=VERDE, alpha=0.75, lw=0))
a.text(9.6, 5.6, "copa", ha="right", va="center", fontsize=12, color=VERDE)
a.annotate("", xy=(5.0, 7.4), xytext=(5.0, 9.6),
           arrowprops=dict(arrowstyle="-|>", color=ROJO, lw=2.6))
a.text(5.35, 8.6, "pulso láser", fontsize=12.5, color=ROJO, va="center")
a.annotate("", xy=(7.6, 0.55), xytext=(2.4, 0.55),
           arrowprops=dict(arrowstyle="<|-|>", color=ROJO, lw=2.2))
a.text(5.0, -0.25, "huella ≈ 25 m", ha="center", fontsize=12.5, color=ROJO)
a.set_title("Lo que GEDI ilumina", fontweight="bold", fontsize=14)

# ----------------------------------------------------------------- derecha
b = ax[1]
z = np.linspace(0, 10, 900)
onda = (2.1 * np.exp(-((z - 6.0) ** 2) / 1.9) +      # dosel
        3.2 * np.exp(-((z - 0.7) ** 2) / 0.10))      # suelo
b.plot(onda, z, color=AZUL, lw=2.6)
b.fill_betweenx(z, 0, onda, color=AZUL, alpha=0.10)
b.set_xlim(-0.05, onda.max() * 1.35); b.set_ylim(0, 10)
b.set_xlabel("energía que vuelve"); b.set_ylabel("altura sobre el suelo (m)")
b.set_title("La forma de onda que registra", fontweight="bold", fontsize=14)
b.axhline(0.70, color=MARRON, ls="--", lw=2)
b.text(onda.max() * 1.33, 0.70, "último retorno = suelo", ha="right", va="bottom",
       fontsize=11.5, color=MARRON)
b.axhline(6.90, color=VERDE, ls="--", lw=2)
b.text(onda.max() * 1.33, 6.90, "primer retorno = copa", ha="right", va="bottom",
       fontsize=11.5, color=VERDE)
for h, et in ((2.3, "rh25"), (3.9, "rh50"), (5.4, "rh75")):
    b.axhline(h, color="#b0b0b0", ls=":", lw=1.2)
    b.text(onda.max() * 1.33, h, et, ha="right", va="bottom", fontsize=10.5,
           color="#888888")
b.annotate("", xy=(0.34, 6.90), xytext=(0.34, 0.70),
           arrowprops=dict(arrowstyle="<|-|>", color=ROJO, lw=2.2))
# el rotulo va en el hueco de la izquierda, NO encima de la curva
b.text(0.46, 3.8, "altura del dosel\n(rh95)", fontsize=12.5, color=ROJO,
       fontweight="bold", va="center")

fig.suptitle("Qué mide GEDI, y por qué de una sola forma de onda salen muchas alturas\n"
             "esquema conceptual: los valores son ilustrativos, no datos del proyecto",
             fontweight="bold", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.91])
guardar(fig, "fig02_como_mide_gedi")
