# -*- coding: utf-8 -*-
"""Figura: cuanto aporta cada familia de variables cuando ya estan las otras.

Es el resultado central del TP5. NO compara sensores: mide contribucion
incremental, que es la unica pregunta que quedo en pie despues del TP4.
Uso:  python gen_fig01_aporte.py
"""
import numpy as np
import matplotlib.pyplot as plt
from _comun_fig import *

fig, ax = plt.subplots(1, 2, figsize=(15, 6.4))
for k, (sitio, titulo) in enumerate((("bosque", "Bosque"), ("estepa", "Estepa"))):
    D = datos(sitio)
    ent = [d for d in D if d["particion"] == "entrenamiento"]
    val = [d for d in D if d["particion"] == "validacion"]
    nom, r2e, r2v = [], [], []
    for etiqueta, cols in MODELOS:
        a, b, _, _ = ajuste(ent, val, cols)
        nom.append(etiqueta); r2e.append(a); r2v.append(b)
    x = np.arange(len(nom))
    a_ = ax[k]
    a_.bar(x - 0.19, r2e, 0.38, color=GRIS, label="entrenamiento")
    a_.bar(x + 0.19, r2v, 0.38, color=VERDE if k == 0 else NARANJA, label="validación")
    for i in range(1, len(nom)):
        d = r2v[i] - r2v[i - 1]
        a_.annotate("%s" % ("+" + coma(d, 3) if d >= 0 else coma(d, 3)),
                    xy=(x[i] + 0.19, r2v[i]), xytext=(0, 6), textcoords="offset points",
                    ha="center", fontsize=11.5, color=ROJO if d < 0 else AZUL,
                    fontweight="bold")
    a_.set_xticks(x); a_.set_xticklabels(nom, fontsize=11)
    a_.set_ylabel("R² del ajuste contra la altura del dosel")
    a_.set_ylim(0, max(max(r2e), max(r2v)) * 1.28)
    a_.set_title("%s (n = %d / %d)" % (titulo, len(ent), len(val)), fontweight="bold")
    # LA LEYENDA NUNCA TAPA LA FIGURA: va debajo del eje.
    a_.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2,
              frameon=False, fontsize=11)
fig.suptitle("Lo que aporta cada familia de variables cuando ya están las otras\n"
             "el número sobre cada barra es el aumento de R² respecto del modelo anterior",
             fontweight="bold", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.90])
guardar(fig, "fig01_aporte_incremental")
