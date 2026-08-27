# -*- coding: utf-8 -*-
"""Figura: contraste bosque-estepa por sensor y polarizacion. Es la respuesta
   directa a 'por que la banda L'. Uso: python gen_tp4_fig_contraste.py"""
import numpy as np
import matplotlib.pyplot as plt
from _comun_fig import *

# fechas casi simultaneas, todas pre-incendio (el bosque en pie)
COMP = [("Sentinel-1\n10/01/2026", "C", "VV", "Sentinel_1/*/%s/S1_GRD/*20260110*.tif", 2),
        ("Sentinel-1\n10/01/2026", "C", "VH", "Sentinel_1/*/%s/S1_GRD/*20260110*.tif", 1),
        ("SAOCOM\n10/01/2026", "L", "HH", "SAOCOM/*/%s/*/*20260110*.tif", 1),
        ("SAOCOM\n10/01/2026", "L", "HV", "SAOCOM/*/%s/*/*20260110*.tif", 2),
        ("NISAR\n08/01/2026", "L", "HH", "NISAR/*/%s/*/NISAR_GCOV_20260108.tif", 1),
        ("NISAR\n08/01/2026", "L", "HV", "NISAR/*/%s/*/NISAR_GCOV_20260108.tif", 2),
        ("PALSAR-2\n2025", "L", "HH", "ALOS_PALSAR_2/*/%s/*/PALSAR2_2025.tif", 1),
        ("PALSAR-2\n2025", "L", "HV", "ALOS_PALSAR_2/*/%s/*/PALSAR2_2025.tif", 2)]

def med(pat, aoi, b):
    r = ruta(pat, aoi)
    if not r: return np.nan
    import rasterio
    with rasterio.open(r) as d:
        a = d.read(b).astype("f8")
    v = a[np.isfinite(a) & (a > 0)]
    return float(10 * np.log10(np.median(v))) if v.size > 1000 else np.nan

et, ban, pol, bos, est, con = [], [], [], [], [], []
for nom, banda, p, pat, b in COMP:
    x, y = med(pat, "BOSQUE_NW_02", b), med(pat, "ESTEPA_NW_02", b)
    if x != x or y != y: continue
    et.append(nom); ban.append(banda); pol.append(p); bos.append(x); est.append(y); con.append(x - y)

fig, ax = plt.subplots(1, 2, figsize=(15.5, 6.8))
fig.suptitle("El contraste bosque − estepa: la respuesta a «por qué la banda L»\n"
             "dos sitios vecinos, mismo clima y mismo relieve; lo que cambia es la biomasa",
             fontweight="bold", fontsize=15)
x = np.arange(len(et))

# --- izquierda: gamma0 de cada sitio
ax[0].bar(x - 0.19, bos, 0.38, label="Bosque", color=VERDE)
ax[0].bar(x + 0.19, est, 0.38, label="Estepa", color="#c9a227")
ax[0].set_xticks(x)
CORTO = {"Sentinel-1\n10/01/2026": "S1", "SAOCOM\n10/01/2026": "SAOCOM",
         "NISAR\n08/01/2026": "NISAR", "PALSAR-2\n2025": "PALSAR-2"}
ax[0].set_xticklabels(["%s\n%s" % (CORTO[e], p) for e, p in zip(et, pol)], fontsize=10)
ax[0].set_ylabel("γ⁰ mediano (dB)")
ax[0].set_title("γ⁰ de cada sitio", fontweight="bold")
# LA LEYENDA NUNCA TAPA LA FIGURA: va debajo del eje. Regla del 29/07/2026.
ax[0].legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2,
             frameon=False, fontsize=11)
ax[0].axhline(0, color="#333", lw=0.8)

# --- derecha: el contraste
col = [GRIS if b == "C" else (ROJO if p in ("HV", "VH") else NARANJA) for b, p in zip(ban, pol)]
ax[1].barh(x, con, color=col)
ax[1].set_yticks(x)
ax[1].set_yticklabels(["%s · %s · banda %s" % (e.replace("\n", " "), p, b)
                       for e, p, b in zip(et, pol, ban)], fontsize=10)
ax[1].invert_yaxis()
ax[1].set_xlabel("contraste bosque − estepa (dB)   →  más es mejor")
ax[1].set_title("Cuánto separa cada sensor los dos sitios", fontweight="bold")
for i, c in enumerate(con):
    ax[1].text(c + 0.15, i, ("%.1f dB" % c).replace(".", ","), va="center", fontsize=10.5)
ax[1].set_xlim(0, max(con) * 1.22)
from matplotlib.patches import Patch
ax[1].legend(handles=[Patch(color=GRIS, label="banda C (5,6 cm)"),
                      Patch(color=NARANJA, label="banda L (24 cm), co-polar"),
                      Patch(color=ROJO, label="banda L, polarización CRUZADA")],
             loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3,
             frameon=False, fontsize=10.5)
fig.tight_layout(rect=[0, 0, 1, 0.9])
guardar(fig, "tp4_fig_contraste")
for e, b, p, c in zip(et, ban, pol, con):
    print("   %-22s %s %-3s %6.2f dB" % (e.replace("\n", " "), b, p, c))
