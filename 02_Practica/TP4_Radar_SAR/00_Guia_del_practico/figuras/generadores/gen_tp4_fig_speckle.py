# -*- coding: utf-8 -*-
"""Figura: cuanto R2 se come el speckle, y hasta donde lo recupera el promediado.
   Datos reales del proyecto. Uso: python gen_tp4_fig_speckle.py"""
import numpy as np
import matplotlib.pyplot as plt
from _comun_fig import *

VENT = [1, 2, 4, 7, 10, 15]
hs = huellas()
fig, ax = plt.subplots(1, 2, figsize=(15, 6.5))
fig.suptitle("El speckle y el promediado, medidos con los datos del proyecto\n"
             "%d huellas GEDI del bosque × γ⁰ de cada sensor" % len(hs),
             fontweight="bold", fontsize=15)

# --- izquierda: R2 contra tamano de ventana
for nom, banda, pat, b, col, ls in FUENTES:
    a, T = leer_db(pat, "BOSQUE_NW_02", b)
    if a is None: continue
    ys = []
    for v in VENT:
        X, Y = extraer(a, T, hs, v)
        ys.append(r2(X, Y))
    ax[0].plot([(2 * v + 1) * 10 for v in VENT], ys, "o"+ls, color=col, lw=2.5, ms=7,
               label="%s (banda %s)" % (nom, banda))
ax[0].set_xlabel("lado de la ventana de promediado (m)")
ax[0].set_ylabel("R² del ajuste γ⁰ → altura del dosel")
ax[0].set_title("Promediar recupera señal... en banda L", fontweight="bold")
# LA LEYENDA NUNCA TAPA LA FIGURA: va debajo del eje. Regla del 29/07/2026.
ax[0].legend(fontsize=10.5, loc="upper center", bbox_to_anchor=(0.5, -0.16),
             ncol=2, frameon=False)
ax[0].axvline(150, ls=":", color=AZUL, lw=1.5)
ax[0].annotate("óptimo ≈ 150 m", xy=(150, 0.245), xytext=(168, 0.225),
               fontsize=11, color=AZUL)
ax[0].text(0.97, 0.42, "la banda C no sube:\nno es speckle lo que le falta",
           transform=ax[0].transAxes, ha="right", fontsize=11, color=GRIS,
           bbox=dict(boxstyle="round,pad=0.35", fc="#f4f4f4", ec=GRIS))

# --- derecha: por que. dispersion de un pixel suelto vs promediado
a, T = leer_db("NISAR/*/%s/*/NISAR_GCOV_20260108.tif", "BOSQUE_NW_02", 2)
X1, Y1 = extraer(a, T, hs, 1)
X2, Y2 = extraer(a, T, hs, 7)
ax[1].scatter(X1, Y1, s=13, alpha=0.30, color=GRIS, edgecolors="none",
              label="ventana 30 m (R² = %s)" % ("%.2f" % r2(X1, Y1)).replace(".", ","))
ax[1].scatter(X2, Y2, s=13, alpha=0.55, color=ROJO, edgecolors="none",
              label="ventana 150 m (R² = %s)" % ("%.2f" % r2(X2, Y2)).replace(".", ","))
# recta de ajuste, dibujada solo en el rango de alturas realmente observado
p, q = np.polyfit(Y2, X2, 1)
yy = np.linspace(Y2.min(), Y2.max(), 50)
xx = p * yy + q
m = (xx >= X2.min()) & (xx <= X2.max())
ax[1].plot(xx[m], yy[m], color=AZUL, lw=2.5)
ax[1].set_xlabel("altura del dosel medida por GEDI, rh95 (m)")
ax[1].set_ylabel("γ⁰ HV (dB)")
ax[1].set_title("NISAR HV: la misma nube de puntos, dos ventanas", fontweight="bold")
ax[1].legend(fontsize=11, loc="upper center", bbox_to_anchor=(0.5, -0.16),
             ncol=2, frameon=False)
ax[1].text(0.03, 0.97, "La nube gris es más ancha porque el speckle\n"
                       "hace que dos píxeles del mismo bosque\n"
                       "difieran varios dB. Al promediar 15×15, la\n"
                       "nube se aprieta y aparece la pendiente.",
           transform=ax[1].transAxes, va="top", fontsize=10.5, color=AZUL,
           bbox=dict(boxstyle="round,pad=0.4", fc="#eef2f7", ec=AZUL, alpha=0.95))
fig.tight_layout(rect=[0, 0, 1, 0.9])
guardar(fig, "tp4_fig_speckle")
