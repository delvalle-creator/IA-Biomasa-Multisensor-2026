# -*- coding: utf-8 -*-
"""Figura: el embudo del filtrado, con los datos reales del proyecto.

CUATRO escalones, no tres: los tres filtros de calidad (forma de onda,
degradacion, sensibilidad) MAS el filtro de pendiente, que antes no se aplicaba
y por eso no figuraba en la version dibujada a mano.
Uso:  python gen_fig04_embudo_filtrado.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
from _comun_fig import *

CAL, PEN = calidad(), pendiente()
ETIQ = ["Disparos dentro\ndel AOI",
        "Pasan calidad\n(forma de onda)",
        "Pasan degradación\n(puntería u órbita)",
        "Pasan sensibilidad\n(el láser llegó al suelo)",
        "Pasan pendiente\n(≤ %s°) = VÁLIDOS"]
COLOR = [GRIS, ARENA, "#f4a261", "#e07a5f", VERDE]

fig, ax = plt.subplots(1, 2, figsize=(15.5, 7.4))
for k, (aoi, sitio) in enumerate(SITIOS):
    c, p = CAL[aoi], PEN[aoi]
    bajas = [n for _, n in c["motivos"]] + [p["descartados"]]
    quedan, x = [c["total"]], c["total"]
    for b in bajas:
        x -= b; quedan.append(x)
    a = ax[k]
    a.set_xlim(0, 10); a.set_ylim(-0.6, len(quedan) - 0.4); a.invert_yaxis(); a.axis("off")
    umbral = coma(p["umbral"], 0)
    for i, n in enumerate(quedan):
        an = 5.6 * n / float(c["total"])
        a.add_patch(Rectangle((5 - an / 2.0, i - 0.30), an, 0.60,
                              facecolor=COLOR[i], edgecolor=AZUL, lw=1.2, zorder=2))
        a.text(5, i, "{:,}".format(n).replace(",", "."), ha="center", va="center",
               fontsize=13, fontweight="bold", zorder=3,
               color="white" if i == len(quedan) - 1 else "black")
        et = ETIQ[i] % umbral if "%s" in ETIQ[i] else ETIQ[i]
        a.text(1.7, i, et, ha="right", va="center", fontsize=11)
        a.text(8.4, i, "%s %%" % coma(100.0 * n / c["total"], 1), ha="left",
               va="center", fontsize=11, color="#555555")
        if i < len(bajas):
            a.annotate("", xy=(5, i + 0.44), xytext=(5, i + 0.32),
                       arrowprops=dict(arrowstyle="-|>", color=ROJO, lw=2))
            a.text(5.25, i + 0.42, "−%s" % "{:,}".format(bajas[i]).replace(",", "."),
                   ha="left", va="center", fontsize=11, color=ROJO)
    a.set_title("%s: %s de %s sobreviven (%s %%)"
                % (sitio, "{:,}".format(quedan[-1]).replace(",", "."),
                   "{:,}".format(c["total"]).replace(",", "."),
                   coma(100.0 * quedan[-1] / c["total"], 1)),
                fontweight="bold", fontsize=14, pad=16)
fig.suptitle("El embudo del filtrado de GEDI, con los datos reales del proyecto\n"
             "cuatro filtros: forma de onda, degradación, sensibilidad y pendiente",
             fontweight="bold", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.93])
guardar(fig, "fig04_embudo_filtrado")
for aoi, sitio in SITIOS:
    c, p = calidad()[aoi], pendiente()[aoi]
    print("   %-7s %5d -> calidad %5d -> pendiente %5d  (%.1f %% del total)"
          % (sitio, c["total"], c["aceptados"], p["validos"],
             100.0 * p["validos"] / c["total"]))
