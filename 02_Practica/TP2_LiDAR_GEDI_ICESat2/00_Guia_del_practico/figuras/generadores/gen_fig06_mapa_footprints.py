# -*- coding: utf-8 -*-
"""Figura: donde caen las huellas de GEDI sobre cada sitio.

Muestra las tres poblaciones -descartadas por calidad, descartadas por pendiente
y validas- para que se vea de un golpe que GEDI NO cubre el terreno de forma
continua, sino en lineas a lo largo de la orbita, y que los descartes por
pendiente NO estan repartidos al azar: caen sobre las laderas.
Uso:  python gen_fig06_mapa_footprints.py
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from _comun_fig import *

fig, ax = plt.subplots(1, 2, figsize=(16, 7.6))
for k, (aoi, sitio) in enumerate(SITIOS):
    xmin, ymin, xmax, ymax = AOIS[aoi]
    des = leer(os.path.join(TABLAS, "GEDI_L2A_%s_descartados.csv" % aoi))
    pen = leer(os.path.join(TABLAS, "GEDI_%s_descartados_pendiente.csv" % aoi))
    val = validos(aoi)
    a = ax[k]
    for filas, c, s, z, et in (
            (des, GRIS, 3, 1, "descartadas por calidad (%s)"),
            (pen, NARANJA, 7, 2, "descartadas por pendiente (%s)"),
            (val, VERDE, 7, 3, "válidas (%s)")):
        lo, la = col(filas, "lon"), col(filas, "lat")
        a.scatter(lo, la, s=s, c=c, lw=0, zorder=z, alpha=0.75,
                  label=et % "{:,}".format(len(lo)).replace(",", "."))
    a.plot([xmin, xmax, xmax, xmin, xmin], [ymin, ymin, ymax, ymax, ymin],
           color=AZUL, lw=1.4, ls="--", zorder=4)
    a.set_title("%s — recinto de 15 × 15 km" % sitio, fontweight="bold")
    a.set_xlabel("longitud (°)"); a.set_ylabel("latitud (°)")
    a.set_aspect(1.0 / np.cos(np.radians(abs(ymin))))
    # pocas marcas y con coma decimal: con las de matplotlib se solapaban
    from matplotlib.ticker import MaxNLocator, FuncFormatter
    a.xaxis.set_major_locator(MaxNLocator(4)); a.yaxis.set_major_locator(MaxNLocator(5))
    f = FuncFormatter(lambda v, _: ("%.2f" % v).replace(".", ",").replace("-", "−"))
    a.xaxis.set_major_formatter(f); a.yaxis.set_major_formatter(f)
    # LA LEYENDA NUNCA TAPA LA FIGURA: va debajo del eje. Regla del 29/07/2026.
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2,
             frameon=False, fontsize=10.5, markerscale=2.2)
fig.suptitle("GEDI no cubre el terreno: son líneas de disparos a lo largo de la órbita\n"
             "y los descartes por pendiente no están repartidos al azar, caen sobre las laderas",
             fontweight="bold", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.91])
guardar(fig, "fig06_mapa_footprints")
