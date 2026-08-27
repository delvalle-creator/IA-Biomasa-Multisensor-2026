# -*- coding: utf-8 -*-
"""Figura: SAOCOM y NISAR, los dos en banda L, sobre los dos sitios y en las dos
   polarizaciones. Fechas casi simultaneas (10/01 y 08/01/2026), bosque en pie.
   Uso: python gen_tp4_fig_saocom_vs_nisar.py"""
import numpy as np, rasterio
import matplotlib.pyplot as plt
from _comun_fig import *

SENS = [("SAOCOM-1B\n10/01/2026", "SAOCOM/*/%s/*/*20260110*.tif"),
        ("NISAR\n08/01/2026", "NISAR/*/%s/*/NISAR_GCOV_20260108.tif")]
SITIOS = [("BOSQUE_NW_02", "Bosque"), ("ESTEPA_NW_02", "Estepa")]
POLS = [(1, "HH"), (2, "HV")]
# escala FIJA por polarizacion: la misma para los dos sensores, a proposito
ESCALA = {"HH": (-22, -2), "HV": (-30, -8)}

fig, ax = plt.subplots(2, 4, figsize=(17, 9.2))
fig.suptitle("Los dos radares de banda L sobre los mismos sitios, con dos días de diferencia\n"
             "escala de grises FIJA e idéntica para los dos sensores en cada polarización",
             fontweight="bold", fontsize=16)
for i, (aoi, sitio) in enumerate(SITIOS):
    j = 0
    for nom, pat in SENS:
        for b, pol in POLS:
            a, T = leer_db(pat, aoi, b)
            lo, hi = ESCALA[pol]
            ax[i, j].imshow(a, cmap="gray", vmin=lo, vmax=hi)
            med = np.nanmedian(a)
            if i == 0:
                ax[i, j].set_title("%s\nγ⁰ %s" % (nom, pol), fontweight="bold", fontsize=13)
            ax[i, j].text(0.035, 0.965, "mediana %s dB" % ("%.1f" % med).replace(".", ","),
                          transform=ax[i, j].transAxes, ha="left", va="top",
                          fontsize=12.5, fontweight="bold", color="black",
                          bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="none", alpha=0.85))
            ax[i, j].set_xticks([]); ax[i, j].set_yticks([])
            j += 1
    ax[i, 0].set_ylabel(sitio, fontsize=15, fontweight="bold")
fig.tight_layout(rect=[0, 0.03, 1, 0.91])
guardar(fig, "tp4_fig_saocom_vs_nisar")

# ------------------------------------------------ composicion en falso color
def rgb(pat, aoi):
    """Composicion R=HH, G=HV, B=HH-HV.

    OJO CON EL ESTIRAMIENTO. Una version anterior de esta figura usaba
    R=(HH+20)/16 y G=(HV+28)/18. Con esos limites, la estepa de SAOCOM
    (HH=-20,8 y HV=-29,4 dB) caia POR DEBAJO del piso en los dos canales, se
    recortaba a cero y salia azul electrico sin textura. Ese azul no era senal:
    era el recorte. La estepa de NISAR, 4,8 dB mas arriba, sobrevivia al recorte
    y salia violeta. Es decir: la diferencia de color entre las dos estepas la
    fabricaba la escala, no los sensores.

    Los limites de abajo abarcan el rango real de los cuatro casos, de modo que
    NADA se recorta. NISAR sigue viendose mas brillante que SAOCOM, que es
    verdad y hay que mostrarlo; pero ahora las dos estepas son comparables.

    Leccion general: en una composicion en falso color, revise siempre que
    ningun canal este saturando. Un color puro y sin textura casi siempre
    delata un recorte, no un fenomeno."""
    hh, _ = leer_db(pat, aoi, 1)
    hv, _ = leer_db(pat, aoi, 2)
    r = np.clip((hh + 28) / 24, 0, 1)          # HH   : abarca de -28 a -4 dB
    g = np.clip((hv + 36) / 26, 0, 1)          # HV   : abarca de -36 a -10 dB
    b = np.clip((hh - hv - 2) / 10, 0, 1)      # HH-HV: abarca de 2 a 12 dB
    return np.dstack([r, g, b])

fig, ax = plt.subplots(2, 2, figsize=(11.5, 11.5))
fig.suptitle("Composición en falso color de radar\n"
             "R = γ⁰ HH   ·   G = γ⁰ HV   ·   B = HH − HV\n"
             "escala común a los cuatro paneles, sin recorte en ningún canal",
             fontweight="bold", fontsize=15)
for i, (aoi, sitio) in enumerate(SITIOS):
    for j, (nom, pat) in enumerate(SENS):
        ax[i, j].imshow(rgb(pat, aoi))
        if i == 0:
            ax[i, j].set_title(nom.replace("\n", " · "), fontweight="bold", fontsize=14)
        ax[i, j].set_xticks([]); ax[i, j].set_yticks([])
    ax[i, 0].set_ylabel(sitio, fontsize=15, fontweight="bold")
ax[0, 0].text(0.03, 0.03, "verde = HV alto = volumen de ramas", transform=ax[0, 0].transAxes,
              color="white", fontsize=12, fontweight="bold")
ax[1, 0].text(0.03, 0.03, "azul/violeta = poco HV = superficie", transform=ax[1, 0].transAxes,
              color="white", fontsize=12, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.90])
guardar(fig, "tp4_fig_composicion_radar")

print("\n%-14s %-8s %8s %8s %10s" % ("sensor", "sitio", "HH", "HV", "HH-HV"))
print("=" * 54)
for nom, pat in SENS:
    for aoi, sitio in SITIOS:
        hh, _ = leer_db(pat, aoi, 1); hv, _ = leer_db(pat, aoi, 2)
        mh, mv = np.nanmedian(hh), np.nanmedian(hv)
        print("%-14s %-8s %8.2f %8.2f %10.2f" % (nom.split("\n")[0], sitio, mh, mv, mh - mv))
