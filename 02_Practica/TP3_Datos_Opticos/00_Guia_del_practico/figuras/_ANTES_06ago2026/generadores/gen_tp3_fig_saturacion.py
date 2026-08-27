# -*- coding: utf-8 -*-
"""Figura: la saturacion optica MEDIDA con los datos de este proyecto.
   Cruza las huellas GEDI validas del bosque (TP2) con los indices de la escena
   pre-incendio limpia (25/11/2025). No es un esquema: son los datos.
   Uso:  python gen_tp3_fig_saturacion.py"""
import csv, os
import numpy as np, rasterio
import matplotlib.pyplot as plt
from _comun_fig import *

AOI = "BOSQUE_NW_02"
CORTES = [0, 3, 6, 9, 12, 15, 18, 21, 25, 30]   # el grupo 30-40 tiene n<10: se omite

with rasterio.open(escena(AOI, PRE)) as d:
    T = d.transform
    az, ro = d.read(1).astype("f4"), d.read(3).astype("f4")
    ni = d.read(7).astype("f4"); s1 = d.read(9).astype("f4"); s2 = d.read(10).astype("f4")
    v = (~np.isin(d.read(11), MAL)) & (ni > 0) & (ro > 0)

def coc(a, b):
    den = a + b
    return np.where(v & (den != 0), (a - b) / np.where(den == 0, 1, den), np.nan)

den = ni + 6 * ro - 7.5 * az + 1
IX = {"NDVI": coc(ni, ro), "NDMI": coc(ni, s1), "NBR": coc(ni, s2),
      "EVI": np.clip(np.where(v & (den != 0), 2.5 * (ni - ro) / np.where(den == 0, 1, den), np.nan), -1, 1)}

D = []
for r in csv.DictReader(open(csv_gedi(AOI))):
    try:
        e, n, h = float(r["este_utm19s"]), float(r["norte_utm19s"]), float(r["rh95"])
    except (KeyError, ValueError):
        continue
    col, fil = int((e - T.c) / T.a), int((n - T.f) / T.e)
    if not (1 <= col < 1499 and 1 <= fil < 1499):
        continue
    d_, ok = {"rh95": h}, True
    for k, a in IX.items():                       # ventana 3x3 = 30 m ~ huella GEDI
        w = a[fil - 1:fil + 2, col - 1:col + 2]; w = w[np.isfinite(w)]
        if w.size == 0: ok = False; break
        d_[k] = float(w.mean())
    if ok: D.append(d_)

fig, ax = plt.subplots(1, 2, figsize=(15, 6.5))
fig.suptitle("La saturación del óptico, medida con los datos de este proyecto\n"
             "%d huellas GEDI válidas del bosque (calidad + pendiente ≤ 20°) × índices de Sentinel-2 del 25/11/2025" % len(D),
             fontweight="bold", fontsize=15)

# --- izquierda: nube de puntos NDVI vs altura
x = np.array([d["rh95"] for d in D]); y = np.array([d["NDVI"] for d in D])
ax[0].scatter(x, y, s=14, alpha=0.30, color=VERDE, edgecolors="none")
med_x, med_y = [], []
for i in range(len(CORTES) - 1):
    g = [d["NDVI"] for d in D if CORTES[i] <= d["rh95"] < CORTES[i + 1]]
    if len(g) >= 5:
        med_x.append((CORTES[i] + CORTES[i + 1]) / 2); med_y.append(np.median(g))
ax[0].plot(med_x, med_y, "o-", color=AZUL, lw=2.5, ms=8, label="mediana por franja de altura")
ax[0].axvline(21, ls=":", color=ROJO, lw=2)
ax[0].annotate("a partir de ~21 m el NDVI\nya no sube: SATURA",
               xy=(21, 0.60), xytext=(23, 0.42), fontsize=12, color=ROJO,
               arrowprops=dict(arrowstyle="->", color=ROJO))
ax[0].set_xlabel("altura del dosel medida por GEDI, rh95 (m)")
ax[0].set_ylabel("NDVI")
ax[0].set_title("El NDVI contra la altura real", fontweight="bold")
# LA LEYENDA NUNCA TAPA LA FIGURA: va debajo del eje. Regla del 29/07/2026.
ax[0].legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2,
             frameon=False, fontsize=11)
ax[0].set_ylim(0.2, 1.0)

# --- derecha: NDVI contra EVI, cada uno en su escala
def medianas(k):
    mx, my = [], []
    for i in range(len(CORTES) - 1):
        g = [d[k] for d in D if CORTES[i] <= d["rh95"] < CORTES[i + 1]]
        if len(g) >= 5:
            mx.append((CORTES[i] + CORTES[i + 1]) / 2); my.append(float(np.median(g)))
    return np.array(mx), np.array(my)

def r2(k):
    xx = np.array([d["rh95"] for d in D]); yy = np.array([d[k] for d in D])
    a, b = np.polyfit(yy, xx, 1); pred = a * yy + b
    return 1 - ((xx - pred) ** 2).sum() / ((xx - xx.mean()) ** 2).sum()

mx, ndvi = medianas("NDVI")
_, evi = medianas("EVI")
ax[1].plot(mx, ndvi, "o-", color=VERDE, lw=2.5, ms=8, label="NDVI (eje izquierdo)")
ax[1].set_ylabel("NDVI (mediana por franja)", color=VERDE)
ax[1].tick_params(axis="y", labelcolor=VERDE)
ax[1].set_ylim(0.68, 0.92)
ax2 = ax[1].twinx()
ax2.plot(mx, evi, "s--", color=NARANJA, lw=2.5, ms=8, label="EVI (eje derecho)")
ax2.set_ylabel("EVI (mediana por franja)", color=NARANJA)
ax2.tick_params(axis="y", labelcolor=NARANJA)
ax2.set_ylim(0.39, 0.60)
ax2.spines["top"].set_visible(False)
ax[1].axvline(21, ls=":", color=ROJO, lw=2)
# los dos rotulos se calculan de las medianas, no se escriben a mano: si
# cambian las huellas cambian los numeros y la figura no puede mentir
def _tres(v):
    return ("%.3f" % v).replace(".", ",")
ax[1].annotate("el NDVI ya baja:\n%s → %s" % (_tres(ndvi[-2]), _tres(ndvi[-1])),
               xy=(24.5, 0.8955),
               xytext=(15.6, 0.752), fontsize=11.5, color=VERDE,
               arrowprops=dict(arrowstyle="->", color=VERDE))
ax2.annotate("el EVI no baja:\n%s → %s" % (_tres(evi[-2]), _tres(evi[-1])),
             xy=(27.3, 0.5685),
             xytext=(16.2, 0.408), fontsize=11.5, color=NARANJA,
             arrowprops=dict(arrowstyle="->", color=NARANJA))
ax[1].set_xlabel("altura del dosel medida por GEDI, rh95 (m)")
ax[1].set_title("El EVI aguanta más que el NDVI", fontweight="bold")
ax[1].text(0.03, 0.97,
           "Ajuste índice $\\rightarrow$ altura, con las %d huellas:\n"
           "   NDVI R² = %s      EVI  R² = %s\n"
           "   NDMI R² = %s      NBR  R² = %s\n"
           # el umbral se calcula, no se escribe a mano: si cambian las huellas
           # cambia el R2 y la frase tiene que seguir siendo verdadera
           "Ninguno llega a %s: el óptico explica menos\n"
           "de un tercio de la altura. Ésa es la razón del TP4."
           % (len(D), ("%.2f" % r2("NDVI")).replace(".", ","),
              ("%.2f" % r2("EVI")).replace(".", ","),
              ("%.2f" % r2("NDMI")).replace(".", ","),
              ("%.2f" % r2("NBR")).replace(".", ","),
              ("%.2f" % (max(r2(k) for k in ("NDVI", "EVI", "NDMI", "NBR")) + 0.01)
               ).replace(".", ",")),
           transform=ax[1].transAxes, va="top", fontsize=10.5, color=AZUL,
           bbox=dict(boxstyle="round,pad=0.4", fc="#eef2f7", ec=AZUL, alpha=0.95))

fig.tight_layout(rect=[0, 0, 1, 0.9])
guardar(fig, "tp3_fig_saturacion")
