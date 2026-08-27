# -*- coding: utf-8 -*-
"""Figura: distribucion de la altura del dosel (rh95) en los dos sitios.

Es el control de sensatez del practico: si el bosque no da alturas claramente
mayores que la estepa, hay un error en algun paso anterior. Todos los numeros
del rotulo se calculan de los CSV, no se escriben a mano.
Uso:  python gen_fig05_alturas_bosque_estepa.py
"""
import numpy as np
import matplotlib.pyplot as plt
from _comun_fig import *

fig, ax = plt.subplots(1, 2, figsize=(15, 6.2))
datos = {}
for k, (aoi, sitio) in enumerate(SITIOS):
    h = col(validos(aoi), "rh95")
    datos[sitio] = h
    a = ax[k]
    a.hist(h, bins=np.arange(0, np.ceil(h.max()) + 1, 1.0),
           color=VERDE if k == 0 else NARANJA, edgecolor="white", lw=0.5,
           label="%s huellas válidas" % "{:,}".format(len(h)).replace(",", "."))
    a.axvline(np.median(h), color=ROJO, lw=2.5, ls="--",
              label="mediana %s m" % coma(np.median(h)))
    a.set_xlabel("altura del dosel medida por GEDI, rh95 (m)")
    a.set_ylabel("número de huellas")
    a.set_title(sitio, fontweight="bold")
    a.set_xlim(0, 37)
    # LA LEYENDA NUNCA TAPA LA FIGURA: va debajo del eje. Regla del 29/07/2026.
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2,
             frameon=False, fontsize=11)
    a.annotate("máximo %s m" % coma(h.max()), xy=(h.max(), 1),
               xytext=(h.max() - 9, a.get_ylim()[1] * 0.42), fontsize=11, color=ROJO,
               arrowprops=dict(arrowstyle="->", color=ROJO))

b, e = datos["Bosque"], datos["Estepa"]
fig.suptitle("La altura del dosel separa los dos sitios: el control de sensatez del TP2\n"
             "mediana %s m en el bosque contra %s m en la estepa, un factor de %s"
             % (coma(np.median(b)), coma(np.median(e)),
                coma(np.median(b) / np.median(e))),
             fontweight="bold", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.90])
guardar(fig, "fig05_alturas_bosque_estepa")
for s_, h in datos.items():
    print("   %-7s n=%4d  mediana %.2f m  p95 %.2f  maximo %.2f m"
          % (s_, len(h), np.median(h), np.percentile(h, 95), h.max()))
