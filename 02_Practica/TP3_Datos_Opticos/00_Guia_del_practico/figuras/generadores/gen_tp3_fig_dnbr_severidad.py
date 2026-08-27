# -*- coding: utf-8 -*-
"""Genera tp3_fig_dnbr_severidad.png y .svg (el .svg se edita en Inkscape o
   Illustrator: cada texto es un objeto). Fecha pre: 25/11/2025 (escena limpia).
   Uso:  python gen_tp3_fig_dnbr_severidad.py"""
import glob, os, sys
import numpy as np, rasterio
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
S2 = os.path.join(PROY, "TP3_Datos_Opticos", "02_Subsets_SNAP_QGIS", "Sentinel_2")
AOI = "BOSQUE_NW_02"
PRE, POST = "*20251125*.tif", "*20260305*.tif"
MAL = [0, 1, 3, 8, 9, 10, 11]
# SIETE clases de Key y Benson, con los limites CONTIGUOS. Corregido el
# 29/07/2026: antes eran cinco y los limites dejaban huecos (una clase terminaba
# en 0,269 y la siguiente empezaba en 0,270). Los pixeles caidos en esos huecos
# no recibian ninguna clase y desaparecian de la figura y de la tabla sin dar
# ningun error: 67,4 ha en el bosque y 13,9 ha en la estepa. Ademas, las dos
# clases de regeneracion (dNBR negativo) quedaban contadas dentro de "Sin
# cambio". Estos son los mismos umbrales que usa TP3_04_dnbr_incendio.py, que es
# la fuente de verdad.
CLASES = [("Regeneración alta", "#1a9850", -np.inf, -0.250),
          ("Regeneración baja", "#a6d96a", -0.250, -0.100),
          ("Sin cambio",        "#d9d9d9", -0.100,  0.100),
          ("Baja",              "#ffeda0",  0.100,  0.270),
          ("Moderada-baja",     "#feb24c",  0.270,  0.440),
          ("Moderada-alta",     "#f4622e",  0.440,  0.660),
          ("Alta",              "#a50f15",  0.660,  np.inf)]
# svg.fonttype="none": los textos quedan como TEXTO en el SVG, no como trazados,
# de modo que en Inkscape se les puede cambiar el cuerpo y el tipo de letra.
plt.rcParams.update({"font.family": "serif", "font.size": 13,
                     "svg.fonttype": "none"})

def nbr(pat):
    f = sorted(glob.glob(os.path.join(S2, "*", AOI, pat)))[0]
    with rasterio.open(f) as d:
        ni, sw, scl = d.read(7).astype("f4"), d.read(10).astype("f4"), d.read(11)
    v = (~np.isin(scl, MAL)) & (ni > 0) & (sw > 0)
    return np.where(v, (ni - sw) / np.where(ni + sw == 0, 1, ni + sw), np.nan).astype("f4"), v

a, va = nbr(PRE); b, vb = nbr(POST)
v = va & vb; d = np.where(v, a - b, np.nan); tot = int(v.sum())
sev = np.full(d.shape, np.nan)
for i, (_, _, lo, hi) in enumerate(CLASES):
    sev[v & (d >= lo) & (d < hi)] = i

# LA LEYENDA VA FUERA DE LOS PANELES, AL PIE DE LA FIGURA. Regla del 29/07/2026:
# una leyenda encima del mapa tapa justamente lo que hay que mirar. Se reserva
# una franja propia abajo (segunda fila del gridspec, con los ejes apagados) y
# la leyenda se dibuja ahi, en una sola fila de siete entradas.
fig = plt.figure(figsize=(20, 10.4))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.085], hspace=0.02, wspace=0.06)
ax = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
axl = fig.add_subplot(gs[1, :]); axl.axis("off")
fig.suptitle("El incendio medido con dNBR — AOI de bosque\n"
             "pre: 25/11/2025 (escena limpia)  |  post: 05/03/2026",
             fontweight="bold", fontsize=17)
im = ax[0].imshow(d, cmap="RdYlGn_r", vmin=-0.3, vmax=1.0)
ax[0].set_title("dNBR (continuo)", fontweight="bold")
cb = fig.colorbar(im, ax=ax[0], fraction=0.046, pad=0.04); cb.set_label("dNBR")
cmap = ListedColormap([c for _, c, _, _ in CLASES])
ax[1].imshow(sev, cmap=cmap, norm=BoundaryNorm(range(len(CLASES) + 1), cmap.N))
ax[1].set_title("Severidad (Key y Benson, siete clases)", fontweight="bold")
leyenda = []
for i, (nom, col, _, _) in enumerate(CLASES):
    n = int((sev == i).sum())
    leyenda.append(Patch(facecolor=col, edgecolor="0.35", linewidth=0.6,
                         label="%s — %.1f ha (%.2f %%)" % (nom, n / 100.0, 100.0 * n / tot)))
# invertida: de mayor a menor severidad, como en la Tabla 3.5
axl.legend(handles=leyenda[::-1], loc="upper center", ncol=7, frameon=False,
           fontsize=10.5, handlelength=1.4, columnspacing=1.0, handletextpad=0.45)
for a_ in ax: a_.set_xticks([]); a_.set_yticks([])
fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.01)
# La salida mide 1780 x 874 px (relacion 2,037). En los .docx la figura se
# inserta con 15,92 x 7,82 cm, que es el ancho util completo de la A4 con
# margenes de una pulgada. Si se cambia la relacion de la imagen hay que
# recalcular el alto en el documento, o Word la deforma.
for ext in ("png", "svg"):
    fig.savefig(os.path.join(AQUI, "..", "tp3_fig_dnbr_severidad." + ext), dpi=85,
                bbox_inches="tight")
q = int((sev >= 3).sum())      # de "Baja" (indice 3) para arriba: quemado
print("validos %.1f%% | quemado %d ha (%.1f%%)" % (100 * tot / v.size, q / 100, 100 * q / tot))
print("Figura -> tp3_fig_dnbr_severidad.png y .svg (el .svg es editable)")
