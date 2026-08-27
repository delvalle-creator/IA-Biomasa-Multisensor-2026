# -*- coding: utf-8 -*-
"""Genera la Figura 1.5 de la guia del TP1b: flujo de trabajo multisensor.
   Los nombres de script y de carpeta salen de la Tabla de orden de ejecucion
   de la propia guia (pasos 11 a 16) y del arbol real del proyecto.

   Actualizada el 24/8/2026: la columna LiDAR suma ICESat-2 ATL08 (segunda
   referencia, TP2 pasos 12-14) y el CCI Biomass v7 (referencia de mapa,
   cotejada en el TP2); TP1_05 descarga ahora GEDI e ICESat-2; y la caja de
   SALIDA nombra la carpeta real de los recortes (02_Subsets_SNAP_QGIS).
   Deja PNG, SVG y un .pptx editable en figuras/ y figuras/editables_pptx/."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrow
from matplotlib import font_manager

AQUI = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.abspath(os.path.join(AQUI, ".."))

SERIF = "Liberation Serif"
plt.rcParams["font.family"] = SERIF
plt.rcParams["mathtext.fontset"] = "stix"

AZUL_CAB = "#1F4E79"
VERDE    = "#2E7D32"
MORADO   = "#8C24A8"
ROJO     = "#C62828"
AZUL_CL  = "#5B9BD5"
MOR_CL   = "#7C4792"
ROJ_CL   = "#E57373"
OSCURA   = "#2F4254"
SALIDA   = "#37474F"
FLECHA   = "#8C8C8C"

W, H = 16.13, 8.36          # pulgadas a 100 dpi -> 1613 x 836 px, igual que el original
fig, ax = plt.subplots(figsize=(W, H), dpi=100)
ax.set_xlim(0, 1613); ax.set_ylim(836, 0); ax.axis("off")
fig.subplots_adjust(0, 0, 1, 1)

def caja(x, y, w, h, color, textos, tam=15, radio=8, colort="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0,rounding_size=%d" % radio,
        linewidth=0, facecolor=color, mutation_aspect=1))
    if isinstance(textos, str): textos=[textos]
    n=len(textos)
    for k, t in enumerate(textos):
        ax.text(x+w/2, y+h/2 + (k-(n-1)/2)*(tam*1.42), t, ha="center", va="center",
                fontsize=tam, color=colort, fontweight="bold", family=SERIF)

def flecha(x, y0, y1):
    ax.annotate("", xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.55",
                                color=FLECHA, linewidth=1.6))

# --- entrada
caja(8, 14, 1597, 56, AZUL_CAB,
     "ENTRADA:   2 archivos KML  →  aoi_config.py   "
     "(grilla común EPSG:32719 · UTM 19S · 10 m · 1500 × 1500)", tam=17)

COL = [(8, 515, VERDE, AZUL_CL), (551, 517, MORADO, MOR_CL), (1104, 501, ROJO, ROJ_CL)]
TIT = ["ÓPTICOS", "RADAR (SAR)", "LiDAR"]
for (x, w, c, _), t in zip(COL, TIT):
    caja(x, 92, w, 44, c, t, tam=18)

PROD = [
  ["Sentinel-2 L2A · óptico (JP2, 10 m)", "Landsat 9 OLI-2 · C2L2 (30 m)"],
  ["Sentinel-1 SLC · banda C · dual-pol (VV+VH)",
   "Sentinel-1 GRD · banda C · dual-pol (VV+VH)",
   "SAOCOM L1A · banda L · quad-pol y dual-pol",
   "NISAR GCOV · banda L · dual-pol (HH+HV)",
   "BIOMASS L1 · banda P · full-pol (HH HV VH VV)"],
  ["GEDI L2A / L2B / L4A V003 · la referencia",
   "ICESat-2 ATL08 V007 · segunda referencia",
   "CCI Biomass v7 · 100 m · referencia de mapa"]]
for (x, w, _, cc), lista in zip(COL, PROD):
    for k, t in enumerate(lista):
        caja(x+14, 150+k*54, w-28, 40, cc, t, tam=12.5, radio=7)

# --- descarga
DESC = [["TP1_03_descargar_sentinel.py (CDSE)",
         "Landsat 9: Planetary Computer (sin credencial)"],
        ["TP1_03_descargar_sentinel.py (CDSE)",
         "SAOCOM: CONAE · BIOMASS / NISAR: ESA / ASF"],
        ["TP1_05_descargar_gedi.py · GEDI e ICESat-2",
         "(NASA Earthdata) · CCI: portal ESA, manual"]]
for (x, w, _, _), lista in zip(COL, DESC):
    caja(x, 425, w, 82, OSCURA, lista, tam=14)

# --- procesamiento  (nombres reales: pasos 11, 12 y 15 de la guia)
PROC = [["TP3_01_recortar_sentinel2.py",
         "JP2 / GeoTIFF → recorte al AOI",
         "reproyección UTM 19S · remuestreo 10 m"],
        ["TP4_01_procesar_sar.py (ESA SNAP · gpt)",
         "órbita precisa → calibración →",
         r"Terrain Flattening ($\mathbf{\gamma^{0}}$) → speckle →",
         "Range-Doppler Terrain Correction"],
        ["TP2_02_recortar_AOI.py · HDF5 → CSV",
         "TP2_12_cargar_ATL08.py · segmentos a la grilla",
         "cotejos del TP2: GEDI–ICESat-2 (TP2_13)",
         "y GEDI–CCI Biomass (04_Tablas)"]]
for (x, w, _, _), lista in zip(COL, PROC):
    caja(x, 545, w, 138, OSCURA, lista, tam=14)

# --- flechas
for (x, w, _, _), lista in zip(COL, PROD):
    y0 = 150+len(lista)*54 - 12
    flecha(x+w/2, y0, 421)
for (x, w, _, _) in COL:
    flecha(x+w/2, 509, 541)
    flecha(x+w/2, 685, 717)

# --- salida
caja(8, 721, 1597, 100, SALIDA,
     ["SALIDA:   02_Subsets_SNAP_QGIS de cada práctico   —   GeoTIFF 1500 × 1500 en grilla común "
      "(EPSG:32719, 10 m)   +   CSV GEDI y ATL08",
      "listos para el análisis multisensor de biomasa en el ecotono bosque – estepa"], tam=17)

fig.savefig(os.path.join(FIG_DIR, "fig15_flujo_multisensor.png"), dpi=100, facecolor="white")
plt.rcParams["svg.fonttype"] = "none"
fig.savefig(os.path.join(FIG_DIR, "fig15_flujo_multisensor.svg"), facecolor="white")
try:
    from _a_pptx import a_pptx
    a_pptx(fig, "fig15_flujo_multisensor", os.path.join(FIG_DIR, "editables_pptx"))
except ImportError:
    print("  (sin python-pptx: no se genero el .pptx editable)")
print("generada en %s" % FIG_DIR)
