# -*- coding: utf-8 -*-
"""Figura 1 del Informe_de_la_estructura: la evidencia del incendio.

La version dibujada a mano mostraba el dNBR con RAMPA CONTINUA y sin leyenda,
mientras el texto del informe hablaba de "severidad alta en 9.669 hectareas": el
lector no tenia como ver esa clase en la figura. Aca el panel de severidad va
clasificado en las SIETE clases contiguas de Key y Benson, las mismas de
TP3_04_dnbr_incendio.py, con su leyenda al pie y las hectareas calculadas.

Uso:  python gen_fig_incendio.py
"""
import glob, os
import numpy as np, rasterio
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from _a_pptx import a_pptx

AQUI = os.path.dirname(os.path.abspath(__file__))
FIGURAS = os.path.abspath(os.path.join(AQUI, ".."))
PROY = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
S2 = os.path.join(PROY, "TP3_Datos_Opticos", "02_Subsets_SNAP_QGIS", "Sentinel_2")
SITIOS = [("BOSQUE_NW_02", "Bosque"), ("ESTEPA_NW_02", "Estepa")]
PRE, POST = "*20251125*.tif", "*20260305*.tif"
MAL = [0, 1, 3, 8, 9, 10, 11]
B2, B3, B4, B8, B12, SCL = 1, 2, 3, 7, 10, 11
CLASES = [("Regeneración alta", "#1a9850", -np.inf, -0.250),
          ("Regeneración baja", "#a6d96a", -0.250, -0.100),
          ("Sin cambio",        "#d9d9d9", -0.100,  0.100),
          ("Baja",              "#ffeda0",  0.100,  0.270),
          ("Moderada-baja",     "#feb24c",  0.270,  0.440),
          ("Moderada-alta",     "#f4622e",  0.440,  0.660),
          ("Alta",              "#a50f15",  0.660,  np.inf)]
plt.rcParams.update({"font.family": "serif", "font.size": 12, "svg.fonttype": "none"})


def leer(aoi, patron):
    f = sorted(glob.glob(os.path.join(S2, "0[23]_*", aoi, patron)))[0]
    with rasterio.open(f) as d:
        r, g, b = (d.read(B4).astype("f4"), d.read(B3).astype("f4"), d.read(B2).astype("f4"))
        ni, sw = d.read(B8).astype("f4"), d.read(B12).astype("f4")
        v = (~np.isin(d.read(SCL), MAL)) & (ni > 0) & (sw > 0)
    v = v & (r > 0)
    # Estirado por percentiles, no por una constante: estos .tif guardan la
    # reflectancia como flotante entre 0 y 1, y una division por 3000 los deja
    # NEGROS. Se usa el 2 y el 98 % para que el contraste sea el mismo en las
    # cuatro escenas y las diferencias que se vean sean del terreno.
    def estirar(x):
        lo, hi = np.nanpercentile(np.where(v, x, np.nan), (2, 98))
        return np.clip((x - lo) / max(hi - lo, 1e-6), 0, 1)
    rgb = np.dstack([estirar(x) for x in (r, g, b)])
    nbr = np.where(v, (ni - sw) / np.where(ni + sw == 0, 1, ni + sw), np.nan)
    return rgb, nbr.astype("f4"), v


fig, ax = plt.subplots(2, 3, figsize=(16, 12.0),
                       gridspec_kw={"hspace": 0.18, "wspace": 0.04})
for i, (aoi, sitio) in enumerate(SITIOS):
    rgb0, nbr0, v0 = leer(aoi, PRE)
    rgb1, nbr1, v1 = leer(aoi, POST)
    v = v0 & v1
    d = np.where(v, nbr0 - nbr1, np.nan)
    sev = np.full(d.shape, np.nan)
    for k, (_, _, lo, hi) in enumerate(CLASES):
        sev[v & (d >= lo) & (d < hi)] = k
    ax[i, 0].imshow(rgb0); ax[i, 1].imshow(rgb1)
    cmap = ListedColormap([c for _, c, _, _ in CLASES])
    ax[i, 2].imshow(sev, cmap=cmap, norm=BoundaryNorm(range(len(CLASES) + 1), cmap.N))
    quemado = float(np.isin(sev, [3, 4, 5, 6]).sum()) / 100.0
    alta = float((sev == 6).sum()) / 100.0
    ax[i, 0].set_title("%s — antes (25/11/2025)" % sitio, fontweight="bold", fontsize=13)
    ax[i, 1].set_title("%s — después (05/03/2026)" % sitio, fontweight="bold", fontsize=13)
    ax[i, 2].set_title("%s — severidad (dNBR)\n%s ha quemadas, %s con severidad alta"
                       % (sitio, ("%.0f" % quemado).replace(",", "."),
                          ("%.0f" % alta).replace(",", ".")),
                       fontweight="bold", fontsize=13)
    for a in ax[i]:
        a.set_xticks([]); a.set_yticks([])

# LA LEYENDA VA AL PIE, FUERA DE LOS MAPAS. Regla del 29/07/2026.
fig.legend(handles=[Patch(facecolor=c, edgecolor="0.35", lw=0.6, label=n)
                    for n, c, _, _ in CLASES][::-1],
           loc="lower center", ncol=7, frameon=False, fontsize=11.5,
           bbox_to_anchor=(0.5, -0.005))
fig.suptitle("La evidencia del incendio: el bosque se quemó y la estepa, que es el control, no.\n"
             "Severidad clasificada con los siete umbrales contiguos de Key y Benson (2006)",
             fontweight="bold", fontsize=16)
fig.tight_layout(rect=[0, 0.04, 1, 0.945])
for ext in ("png", "svg"):
    fig.savefig(os.path.join(FIGURAS, "fig_incendio." + ext), dpi=105, bbox_inches="tight")
a_pptx(fig, "fig_incendio", os.path.join(FIGURAS, "editables_pptx"))
print("  -> fig_incendio.png, .svg y .pptx en %s" % FIGURAS)
