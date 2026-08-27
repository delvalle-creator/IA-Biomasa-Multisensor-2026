# -*- coding: utf-8 -*-
"""Figura: tres escenas del bosque en color natural y en falso color SWIR.
   La del medio es la que tiene bruma: se ve. Uso: python gen_tp3_fig_composiciones.py"""
import numpy as np, rasterio
import matplotlib.pyplot as plt
from _comun_fig import *

AOI = "BOSQUE_NW_02"
ESCENAS = [("*20251125*.tif", "25/11/2025", "LIMPIA · es la referencia pre-incendio", VERDE),
           ("*20260109*.tif", "09/01/2026", "CON BRUMA · la SCL solo marcó 7 % de cirros", "#b45309"),
           ("*20260305*.tif", "05/03/2026", "LIMPIA · post-incendio", ROJO)]

def comp(pat, bandas, p2=2, p98=98):
    with rasterio.open(escena(AOI, pat)) as d:
        a = np.dstack([d.read(b).astype("f4") for b in bandas])
    out = np.zeros_like(a)
    for i in range(3):                       # realce por percentiles, banda a banda
        v = a[..., i][np.isfinite(a[..., i]) & (a[..., i] > 0)]
        lo, hi = np.percentile(v, p2), np.percentile(v, p98)
        out[..., i] = np.clip((a[..., i] - lo) / (hi - lo + 1e-9), 0, 1)
    return out

fig, ax = plt.subplots(2, 3, figsize=(16, 11.5))
fig.suptitle("El sitio de bosque (15 × 15 km) en tres fechas\n"
             "arriba: color natural (Rojo-Verde-Azul)   ·   abajo: falso color SWIR2-NIR-Rojo",
             fontweight="bold", fontsize=16)
for j, (pat, fecha, nota, col) in enumerate(ESCENAS):
    ax[0, j].imshow(comp(pat, (3, 2, 1)))
    ax[0, j].set_title("%s\n%s" % (fecha, nota), fontweight="bold", fontsize=13, color=col)
    ax[1, j].imshow(comp(pat, (10, 7, 3)))
for a_ in ax.ravel():
    a_.set_xticks([]); a_.set_yticks([])
ax[0, 0].set_ylabel("Color natural", fontsize=13)
ax[1, 0].set_ylabel("Falso color SWIR", fontsize=13)
ax[1, 0].text(0.03, 0.03, "vegetación viva = verde", transform=ax[1, 0].transAxes,
              color="white", fontsize=12, fontweight="bold")
ax[1, 2].text(0.03, 0.03, "área quemada = rojo/naranja", transform=ax[1, 2].transAxes,
              color="white", fontsize=12, fontweight="bold")
ax[0, 1].text(0.5, 0.5, "la bruma se VE:\nel velo gris tapa el bosque",
              transform=ax[0, 1].transAxes, ha="center", fontsize=13, color="#7c2d12",
              fontweight="bold", bbox=dict(boxstyle="round,pad=0.4", fc="white", alpha=0.75))
fig.tight_layout(rect=[0, 0, 1, 0.93])
guardar(fig, "tp3_fig_composiciones", dpi=85)
