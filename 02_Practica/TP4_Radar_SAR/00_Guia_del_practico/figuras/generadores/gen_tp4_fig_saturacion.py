# -*- coding: utf-8 -*-
"""Figura central del TP4: la banda L responde donde la C es plana, y sigue
   respondiendo donde el NDVI del TP3 ya saturo. Todo medido con los datos del
   proyecto. Uso: python gen_tp4_fig_saturacion.py"""
import numpy as np
import matplotlib.pyplot as plt
from _comun_fig import *

RADIO = 7                       # ventana 15x15 = 150 m (ver TP4_06)
CORTES = [0, 3, 6, 9, 12, 15, 18, 21, 25, 30]
CENTROS = [(CORTES[i] + CORTES[i+1]) / 2 for i in range(len(CORTES) - 1)]
# medianas del NDVI por franja, medidas en el TP3 (script TP3_05)
# Medianas de NDVI por franja, calculadas por gen_tp3_fig_saturacion.py sobre
# las 690 huellas validas del bosque. Copiadas a mano A PROPOSITO: esta figura
# es del TP4 y no debe depender de que esten los insumos opticos del TP3. Si se
# vuelve a correr aquel generador, hay que actualizar esta linea.
# Ultima actualizacion: 29/07/2026.
NDVI_TP3 = [0.712, 0.769, 0.797, 0.832, 0.855, 0.886, 0.879, 0.897, 0.893]

hs = huellas()
fig, ax = plt.subplots(1, 2, figsize=(15.5, 7.6))
fig.suptitle("Por qué la banda L y no la C — medido con %d huellas GEDI del bosque" % len(hs),
             fontweight="bold", fontsize=16)

# ---------------- izquierda: gamma0 por franja de altura, cada sensor
for nom, banda, pat, b, col, ls in FUENTES:
    a, T = leer_db(pat, "BOSQUE_NW_02", b)
    if a is None: continue
    X, Y = extraer(a, T, hs, RADIO)
    med = []
    for i in range(len(CORTES) - 1):
        g = Y[(X >= CORTES[i]) & (X < CORTES[i + 1])]
        med.append(np.median(g) if g.size >= 5 else np.nan)
    gan = np.nanmedian(Y[X >= 21]) - np.nanmedian(Y[X < 3])
    ax[0].plot(CENTROS, med, "o"+ls, color=col, lw=2.5, ms=7,
               label="%s · banda %s  (gana %s dB)" % (nom, banda, ("%.1f" % gan).replace(".", ",")))
ax[0].set_xlabel("altura del dosel medida por GEDI, rh95 (m)")
ax[0].set_ylabel("γ⁰ mediano por franja (dB)")
ax[0].set_title("Cada sensor contra la altura real", fontweight="bold")
ax[0].set_ylim(-20.5, -8.8)
# LA LEYENDA NUNCA TAPA LA FIGURA: va debajo del eje. Regla del 29/07/2026.
ax[0].legend(fontsize=10, loc="upper center", bbox_to_anchor=(0.5, -0.16),
             ncol=2, frameon=False)
ax[0].annotate("la banda C es PLANA:\nmedio dB en 25 m de árbol", xy=(17.5, -15.85),
               xytext=(19.5, -14.4), fontsize=11.5, color="#555555",
               arrowprops=dict(arrowstyle="->", color=GRIS))

# ---------------- derecha: NDVI del TP3 contra banda L del TP4
a, T = leer_db("NISAR/*/%s/*/NISAR_GCOV_20260108.tif", "BOSQUE_NW_02", 2)
X, Y = extraer(a, T, hs, RADIO)
med_L = []
for i in range(len(CORTES) - 1):
    g = Y[(X >= CORTES[i]) & (X < CORTES[i + 1])]
    med_L.append(np.median(g) if g.size >= 5 else np.nan)
ax[1].plot(CENTROS, NDVI_TP3, "o-", color=VERDE, lw=2.5, ms=8, label="NDVI (TP3, óptico)")
ax[1].set_ylabel("NDVI (mediana por franja)", color=VERDE)
ax[1].tick_params(axis="y", labelcolor=VERDE); ax[1].set_ylim(0.68, 0.93)
ax2 = ax[1].twinx()
ax2.plot(CENTROS, med_L, "s-", color=ROJO, lw=2.5, ms=8, label="γ⁰ HV NISAR (TP4, banda L)")
ax2.set_ylabel("γ⁰ HV (dB)", color=ROJO); ax2.tick_params(axis="y", labelcolor=ROJO)
ax2.set_ylim(-14.9, -11.2); ax2.spines["top"].set_visible(False)
ax[1].axvspan(21, 30, color="#fde68a", alpha=0.45)
ax[1].set_xlabel("altura del dosel medida por GEDI, rh95 (m)")
ax[1].set_title("El resultado del curso, en una figura", fontweight="bold")
ax[1].annotate("el NDVI se aplana:\n%s → %s"
               % (("%.3f" % NDVI_TP3[-2]).replace(".", ","),
                  ("%.3f" % NDVI_TP3[-1]).replace(".", ",")),
               xy=(24.5, 0.8955), xytext=(1.8, 0.907),
               fontsize=11.5, color=VERDE, arrowprops=dict(arrowstyle="->", color=VERDE))
# Rotulo MEDIDO, sin verbo interpretativo. Con las 690 huellas validas la banda
# L gana ~2 dB hasta los 15 m y despues tambien se aplana: decir "SIGUE
# subiendo" en la ultima franja seria falso. Ver seccion 50 del CONTEXTO_IA.
ax2.annotate("banda L, medianas por franja:\n%s dB"
             % " → ".join(("%.2f" % x).replace("-", "−").replace(".", ",")
                          for x in med_L[-3:]),
             xy=(27.3, -11.6),
             xytext=(10.5, -14.3), fontsize=11.5, color=ROJO,
             arrowprops=dict(arrowstyle="->", color=ROJO))
ax[1].text(25.5, 0.856, "aquí el óptico\nya no ve", ha="center", fontsize=11.5,
           color="#92400e", fontweight="bold")
h1, l1 = ax[1].get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax[1].legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.16),
             ncol=2, frameon=False, fontsize=10.5)
fig.tight_layout(rect=[0, 0, 1, 0.92])
guardar(fig, "tp4_fig_saturacion")
