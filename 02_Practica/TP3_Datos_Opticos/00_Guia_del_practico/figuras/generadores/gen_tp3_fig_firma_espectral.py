# -*- coding: utf-8 -*-
"""Figura: firma espectral REAL del bosque y de la estepa, antes y despues del
   incendio. Los valores son medianas medidas sobre las escenas del proyecto,
   NO son un esquema. Uso:  python gen_tp3_fig_firma_espectral.py"""
import numpy as np, rasterio
import matplotlib.pyplot as plt
from _comun_fig import *

def firma(aoi, pat):
    with rasterio.open(escena(aoi, pat)) as d:
        v = ~np.isin(d.read(11), MAL)
        out = []
        for i in range(1, 11):
            a = d.read(i).astype("f4")
            out.append(float(np.median(a[v & (a > 0)])))
    return np.array(out)

wl = [w for _, w, _ in BANDAS]
fig, ax = plt.subplots(1, 2, figsize=(15, 6), sharey=True)
fig.suptitle("Firma espectral medida sobre los datos del proyecto\n"
             "medianas de Sentinel-2 | pre: 25/11/2025  post: 05/03/2026",
             fontweight="bold", fontsize=15)
for j, (aoi, tit) in enumerate((("BOSQUE_NW_02", "Bosque (se quemó)"),
                                ("ESTEPA_NW_02", "Estepa (control, no se quemó)"))):
    pre, post = firma(aoi, PRE), firma(aoi, POST)
    ax[j].plot(wl, pre, "o-", color=VERDE, lw=2.5, ms=7, label="antes (25/11/2025)")
    ax[j].plot(wl, post, "s--", color=ROJO, lw=2.5, ms=7, label="después (05/03/2026)")
    ax[j].set_title(tit, fontweight="bold")
    ax[j].set_xlabel("banda de Sentinel-2 (y su longitud de onda, en nm)")
    # LA LEYENDA NUNCA TAPA LA FIGURA: va debajo del eje. Regla del 29/07/2026.
    ax[j].legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2,
                 frameon=False, fontsize=11)
    # solo se rotulan las bandas que usan los indices del practico
    ax[j].set_xticks([492, 665, 833, 1610, 2190])
    ax[j].set_xticklabels(["Azul\n492", "Rojo\n665", "NIR\n833",
                           "SWIR1\n1610", "SWIR2\n2190"], fontsize=10)
    ax[j].tick_params(axis="x", pad=4)
ax[0].set_ylabel("reflectancia (mediana del AOI)")
ax[0].set_ylim(0, 0.32)
# anotaciones solo en el bosque, que es donde se ve el cambio
ax[0].annotate("el NIR se desploma:\n0,267 → 0,104\n(el dosel desapareció)",
               xy=(833, 0.104), xytext=(980, 0.245), fontsize=11, color=AZUL,
               arrowprops=dict(arrowstyle="->", color=AZUL))
ax[0].annotate("el SWIR2 SUBE:\n0,086 → 0,131\n(ceniza y suelo seco)",
               xy=(2190, 0.131), xytext=(1280, 0.040), fontsize=11, color=AZUL,
               arrowprops=dict(arrowstyle="->", color=AZUL))
ax[1].annotate("las dos curvas casi se tocan:\nel control funciona", xy=(1610, 0.236),
               xytext=(640, 0.29), fontsize=11, color=AZUL,
               arrowprops=dict(arrowstyle="->", color=AZUL))
fig.tight_layout(rect=[0, 0.02, 1, 0.9])
guardar(fig, "tp3_fig_firma_espectral")
print("El NDVI usa Rojo y NIR; el NBR usa NIR y SWIR2: por eso el NBR es el")
print("indice del fuego (las dos bandas se mueven en sentidos opuestos).")
