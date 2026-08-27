# -*- coding: utf-8 -*-
"""Figura: DONDE se equivoca el modelo de altura.

Es el hallazgo mas importante del TP5 y el que un R2 no muestra: el modelo
sobrestima los arboles bajos y subestima los altos, de manera monotona. La barra
va coloreada segun el signo y el numero de huellas de cada franja se declara,
porque la cola alta esta poco poblada y eso condiciona la lectura.
Uso:  python gen_fig02_sesgo.py
"""
import numpy as np
import matplotlib.pyplot as plt
from _comun_fig import *

MODELO = OPTICO + SAR      # sin GEDI: el modelo tiene que servir donde no hay huellas
fig, ax = plt.subplots(1, 2, figsize=(15, 6.6))
for k, (sitio, titulo) in enumerate((("bosque", "Bosque"), ("estepa", "Estepa"))):
    D = datos(sitio)
    ent = [d for d in D if d["particion"] == "entrenamiento"]
    val = [d for d in D if d["particion"] == "validacion"]
    _, r2v, rmse, pv = ajuste(ent, val, MODELO)
    y = np.array([d["rh95"] for d in val])
    a_ = ax[k]
    cen, ses, ns = [], [], []
    for i in range(len(CORTES) - 1):
        m = (y >= CORTES[i]) & (y < CORTES[i + 1])
        if m.sum() < 5:
            continue
        cen.append((CORTES[i] + CORTES[i + 1]) / 2.0)
        ses.append(float((pv[m] - y[m]).mean())); ns.append(int(m.sum()))
    col = [VERDE if s >= 0 else ROJO for s in ses]
    a_.bar(cen, ses, width=2.4, color=col, edgecolor="white", lw=0.6)
    for c, s, n in zip(cen, ses, ns):
        a_.annotate("n=%d" % n, xy=(c, s), xytext=(0, 6 if s >= 0 else -16),
                    textcoords="offset points", ha="center", fontsize=10, color="#555555")
    a_.axhline(0, color="#333333", lw=1.2)
    a_.set_xlabel("altura del dosel medida por GEDI, rh95 (m)")
    a_.set_ylabel("sesgo del modelo (m)   ↑ sobrestima   ↓ subestima")
    a_.set_title("%s — R² %s, RMSE %s m" % (titulo, coma(r2v, 3), coma(rmse)),
                 fontweight="bold")
    alto = y >= 15
    if alto.sum() >= 5:
        a_.annotate("por encima de 15 m\nel sesgo medio es %s m" % coma(float((pv[alto] - y[alto]).mean())),
                    xy=(0.97, 0.06), xycoords="axes fraction", ha="right", fontsize=11.5,
                    color=ROJO, fontweight="bold")
fig.suptitle("Dónde se equivoca el modelo: sobrestima lo bajo y subestima lo alto\n"
             "el R² global no lo muestra; la tabla por franja, sí. Es regresión a la media",
             fontweight="bold", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.90])
guardar(fig, "fig02_sesgo_por_franja")
