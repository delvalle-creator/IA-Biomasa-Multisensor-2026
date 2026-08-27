# -*- coding: utf-8 -*-
"""Utilidades compartidas por los generadores de figuras del TP5.

Todos los numeros se leen del dataset y se recalculan aca: ninguna figura del
TP5 tiene una cifra escrita a mano. Reglas de siempre: la leyenda va FUERA del
dibujo, el SVG lleva el texto editable y cada figura deja tambien un .pptx.
"""
import csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from _a_pptx import a_pptx

AQUI = os.path.dirname(os.path.abspath(__file__))
FIGURAS = os.path.abspath(os.path.join(AQUI, ".."))
TP5 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SUBSETS = os.path.join(TP5, "04_Tablas_de_trabajo")
RASTERS = os.path.join(TP5, "05_Resultados", "02_Rasters")

VERDE, ROJO, AZUL, NARANJA = "#2d6a4f", "#a50f15", "#1d3557", "#d97706"
GRIS, VIOLETA = "#9aa5b1", "#6d28d9"
OPTICO = ["NDVI", "EVI", "NDMI", "NBR"]
SAR = ["g0_C_VH", "g0_C_VV", "g0_L_SAOCOM_HH", "g0_L_SAOCOM_HV",
       "g0_L_NISAR_HH", "g0_L_NISAR_HV", "g0_L_PALSAR2_HH", "g0_L_PALSAR2_HV"]
LIDAR = ["pai", "cover", "fhd_normal"]
MODELOS = [("óptico", OPTICO), ("SAR", SAR),
           ("óptico\n+ SAR", OPTICO + SAR),
           ("óptico + SAR\n+ LiDAR", OPTICO + SAR + LIDAR)]
CORTES = [0, 3, 6, 9, 12, 15, 18, 21, 25, 30]

plt.rcParams.update({"font.family": "serif", "font.size": 12,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "none"})


def coma(x, d=2):
    return ("%.*f" % (d, x)).replace(".", ",").replace("-", "−")


def datos(sitio=None):
    """Filas completas del dataset, con particion y todas las variables."""
    out = []
    for f in sorted(os.listdir(SUBSETS)):
        if not (f.startswith("TP5_dataset_") and f.endswith(".csv")):
            continue
        # Los *_cobertura.csv repiten las mismas huellas con una columna mas: si
        # se leen tambien, cada huella entra dos veces y los n informados salen
        # al doble. Es el mismo error que se corrigio en la cadena el 31/07/2026
        # y que habia quedado en pie aqui. Los R2 no cambian; los n, si.
        if f.endswith("_cobertura.csv"):
            continue
        with open(os.path.join(SUBSETS, f), newline="", encoding="utf-8") as h:
            for r in csv.DictReader(h):
                if not r.get("particion"):
                    continue
                if sitio and r["sitio"] != sitio:
                    continue
                try:
                    d = {k: float(r[k]) for k in OPTICO + SAR + LIDAR + ["rh95"]}
                except (KeyError, ValueError):
                    continue
                d["particion"] = r["particion"]; d["sitio"] = r["sitio"]
                out.append(d)
    return out


def ajuste(entrena, valida, cols, objetivo="rh95"):
    """Devuelve (R2 entrenamiento, R2 validacion, RMSE validacion, prediccion)."""
    Xe = np.array([[d[c] for c in cols] for d in entrena])
    Xv = np.array([[d[c] for c in cols] for d in valida])
    ye = np.array([d[objetivo] for d in entrena])
    yv = np.array([d[objetivo] for d in valida])
    A = np.column_stack([Xe, np.ones(len(Xe))])
    beta, _, _, _ = np.linalg.lstsq(A, ye, rcond=None)
    pe = A @ beta
    pv = np.column_stack([Xv, np.ones(len(Xv))]) @ beta
    def r2(y, p):
        ss = ((y - y.mean()) ** 2).sum()
        return 1 - ((y - p) ** 2).sum() / ss if ss > 0 else np.nan
    return r2(ye, pe), r2(yv, pv), float(np.sqrt(((yv - pv) ** 2).mean())), pv


def guardar(fig, nombre, dpi=110):
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(FIGURAS, nombre + "." + ext), dpi=dpi, bbox_inches="tight")
    a_pptx(fig, nombre, os.path.join(FIGURAS, "editables_pptx"))
    print("  -> %s.png, .svg y .pptx" % nombre)
