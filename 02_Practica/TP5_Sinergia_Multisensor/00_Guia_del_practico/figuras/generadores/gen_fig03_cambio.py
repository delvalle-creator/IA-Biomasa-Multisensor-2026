# -*- coding: utf-8 -*-
"""Figura: el mapa de biomasa antes, despues y su cambio.

Es lo que GEDI no puede hacer solo: GEDI mide bien pero en lineas separadas por
kilometros; el optico y el radar cubren todo pero no miden estructura. El mapa
existe porque se calibro uno contra el otro.
Uso:  python gen_fig03_cambio.py
"""
import os
import numpy as np, rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from _comun_fig import *

AOI = "BOSQUE_NW_02"
PISO = 10.5      # piso de ruido medido por TP5_04 con la clase "Sin cambio"


def capa(nombre):
    with rasterio.open(os.path.join(RASTERS, "TP5_%s_%s.tif" % (nombre, AOI))) as d:
        a = d.read(1).astype("f4"); nd = d.nodata
    return np.where(a == nd, np.nan, a)


pre, post, cam = capa("biomasa_pre"), capa("biomasa_post"), capa("biomasa_cambio")
fig, ax = plt.subplots(1, 3, figsize=(16, 6.6))
vmax = float(np.nanpercentile(pre, 98))
for a_, arr, tit in ((ax[0], pre, "Antes del incendio (25/11/2025)"),
                     (ax[1], post, "Después (05/03/2026)")):
    im = a_.imshow(arr, cmap="YlOrBr", vmin=0, vmax=vmax)
    a_.set_title(tit, fontweight="bold", fontsize=13)
    cb = fig.colorbar(im, ax=a_, fraction=0.046, pad=0.03)
    cb.set_label("biomasa (Mg/ha)")
lim = float(np.nanpercentile(np.abs(cam), 99))
im = ax[2].imshow(cam, cmap="RdBu", norm=TwoSlopeNorm(vcenter=0, vmin=-lim, vmax=lim))
ax[2].set_title("Cambio (post − pre)", fontweight="bold", fontsize=13)
cb = fig.colorbar(im, ax=ax[2], fraction=0.046, pad=0.03)
cb.set_label("Mg/ha   (negativo = pérdida)")
for a_ in ax:
    a_.set_xticks([]); a_.set_yticks([])
perd = cam[np.isfinite(cam) & (cam < 0)]
fig.suptitle("Biomasa del sitio de bosque antes y después del incendio\n"
             "pérdida acumulada %s Mg sobre %s ha · el piso de ruido del método es %s Mg/ha"
             % ("{:,}".format(int(-perd.sum() * 0.01)).replace(",", "."),
                "{:,}".format(int(perd.size * 0.01)).replace(",", "."), coma(PISO, 1)),
             fontweight="bold", fontsize=15)
fig.text(0.5, 0.012,
         "El modelo subestima los rodales altos (sesgo de −9,45 m por encima de 15 m) y la "
         "alometría lo amplifica: este mapa es un mínimo, no una medición.",
         ha="center", fontsize=11.5, color=ROJO)
fig.tight_layout(rect=[0, 0.045, 1, 0.90])
guardar(fig, "fig03_cambio_biomasa")
