# -*- coding: utf-8 -*-
"""Utilidades compartidas por los generadores de figuras del TP4."""
import csv, glob, os
import numpy as np, rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from _a_pptx import a_pptx

AQUI = os.path.dirname(os.path.abspath(__file__))
FIGURAS = os.path.abspath(os.path.join(AQUI, ".."))
PROY = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
I = os.path.join(PROY, "TP4_Radar_SAR", "02_Subsets_SNAP_QGIS")
# LAS HUELLAS SON LAS *VALIDAS* DEL TP2, NO LAS "ACEPTADAS". Corregido el
# 29/07/2026. "Aceptadas" (1.025 en el bosque) son las que pasaron el filtro de
# calidad del L2A; "validas" (690) son las que ademas pasaron el filtro de
# PENDIENTE de 20 grados y tienen estructura del L2B. Son las que el TP2 declara
# como su producto y las que consumen el TP3, el TP4 y el TP5.
#
# No es un detalle de contabilidad: en una ladera el pulso de GEDI abarca 25 m de
# desnivel y el rh95 sale inflado, de modo que las huellas de pendiente meten
# ruido justo en la variable que estas figuras miden. Comprobado: con las validas
# el R2 del gamma0 de banda L contra la altura SUBE (SAOCOM 0,127 -> 0,180;
# PALSAR-2 0,167 -> 0,190) y las conclusiones no cambian.
GEDI = os.path.join(PROY, "TP2_LiDAR_GEDI_ICESat2", "04_Tablas_de_trabajo")
SUB = {"BOSQUE_NW_02": "01_Bosque", "ESTEPA_NW_02": "02_Estepa"}


def csv_gedi(aoi):
    return os.path.join(GEDI, SUB[aoi], "GEDI_%s_validos_con_estructura.csv" % aoi)

VERDE, ROJO, AZUL, NARANJA = "#2d6a4f", "#a50f15", "#1d3557", "#d97706"
CIAN, VIOLETA, GRIS = "#0e7490", "#6d28d9", "#888888"
plt.rcParams.update({"font.family": "serif", "font.size": 12,
                     "axes.spines.top": False, "axes.spines.right": False,
                     # svg.fonttype="none" deja los textos como TEXTO dentro del
                     # SVG en vez de convertirlos en trazados. Sin esto el SVG se
                     # abre en Inkscape pero cada letra es un dibujo y NO se le
                     # puede cambiar el cuerpo ni el tipo de letra. Puesto el
                     # 29/07/2026, a pedido del docente, para poder ajustar los
                     # tamanos de letra al armar la guia general.
                     "svg.fonttype": "none"})

# (etiqueta, banda, patron, n_banda, color, estilo)
FUENTES = [
    ("Sentinel-1 VH", "C", "Sentinel_1/*/%s/S1_GRD/*20251123*.tif", 1, GRIS, "--"),
    ("Sentinel-1 VV", "C", "Sentinel_1/*/%s/S1_GRD/*20251123*.tif", 2, "#bbbbbb", "--"),
    ("NISAR HV", "L", "NISAR/*/%s/*/NISAR_GCOV_20260108.tif", 2, ROJO, "-"),
    ("PALSAR-2 HV", "L", "ALOS_PALSAR_2/*/%s/*/PALSAR2_2025.tif", 2, NARANJA, "-"),
    ("SAOCOM HV", "L", "SAOCOM/*/%s/*/*20260110*.tif", 2, VIOLETA, "-"),
]

def ruta(patron, aoi):
    h = [x for x in sorted(glob.glob(os.path.join(I, patron % aoi))) if "_mask" not in x]
    return h[0] if h else None

def leer_db(patron, aoi, banda):
    r = ruta(patron, aoi)
    if not r: return None, None
    with rasterio.open(r) as d:
        a = d.read(banda).astype("f8"); T = d.transform
    # out= explicito: sin el, numpy deja memoria SIN INICIALIZAR en las celdas
    # donde no calcula, y aunque np.where despues las descarte, cada corrida
    # emite un UserWarning. Corregido el 29/07/2026.
    sal = np.full(a.shape, np.nan)
    np.log10(a, where=a > 0, out=sal)
    return np.where(a > 0, 10 * sal, np.nan), T

def huellas(aoi="BOSQUE_NW_02"):
    p = csv_gedi(aoi)
    out = []
    for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
        try: out.append((float(r["este_utm19s"]), float(r["norte_utm19s"]), float(r["rh95"])))
        except (KeyError, ValueError): pass
    return out

def extraer(a, T, hs, radio):
    """Promedia gamma0 en una ventana centrada en cada huella. Devuelve (alturas, dB).

    EL PROMEDIO SE HACE EN POTENCIA, NO EN DECIBELES. Corregido el 29/07/2026.
    El decibel es logaritmico: promediar dB da la media GEOMETRICA de la potencia,
    que siempre es menor o igual que la aritmetica, y la diferencia crece con la
    dispersion. Como el moteado es justamente dispersion, promediar en dB
    subestima el gamma0 de las ventanas mas ruidosas, que son las chicas: el
    resultado es un sesgo que depende del tamano de la ventana, es decir
    exactamente la variable que la figura del moteado quiere medir.

    Se pasa a potencia lineal, se promedia, y recien ahi se vuelve a dB.
    """
    ny, nx = a.shape; X, Y = [], []
    for e, n, h in hs:
        c = int((e - T.c) / T.a); f = int((n - T.f) / T.e)
        if not (radio <= c < nx - radio and radio <= f < ny - radio): continue
        w = a[f - radio:f + radio + 1, c - radio:c + radio + 1]; w = w[np.isfinite(w)]
        if w.size:
            X.append(h)
            Y.append(float(10 * np.log10(np.mean(10 ** (w / 10.0)))))
    return np.array(X), np.array(Y)

def r2(x, y):
    p, q = np.polyfit(y, x, 1); pred = p * y + q
    return 1 - ((x - pred) ** 2).sum() / ((x - x.mean()) ** 2).sum()

def guardar(fig, nombre, dpi=110):
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(FIGURAS, nombre + "." + ext), dpi=dpi, bbox_inches="tight")
    a_pptx(fig, nombre, os.path.join(FIGURAS, "editables_pptx"))
    p = os.path.join(FIGURAS, nombre + ".png")
    print("  -> %s.png (%.1f MB) y %s.svg" % (nombre, os.path.getsize(p) / 1e6, nombre))
