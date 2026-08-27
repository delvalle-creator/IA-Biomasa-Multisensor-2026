# -*- coding: utf-8 -*-
"""Figura 1.4 de la GUIA_TP1a: los diez pasos del TP1, en tres fases.

Por que este generador existe:
  1. La figura anterior no tenia fuente reproducible.
  2. Citaba una "Tabla 19" que no existe: las tablas del anexo son 1.6 y 1.7.
  3. Estaba dibujada sobre un lienzo de 1802 px que, llevado al ancho de la
     caja de texto (15,9 cm), dejaba la letra en unos 5 pt: ilegible impresa.
     Aca el lienzo es de 1000 px, de modo que la misma letra se lee a ~9 pt.

Los diez pasos y sus nombres salen de
TP1_Busqueda_IA/03_Scripts/00_ORDEN_DE_EJECUCION.md.

Uso:  python gen_fig14_flujo.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.abspath(os.path.join(AQUI, ".."))

ROSA, GRIS, VERDE, LILA = "#F8C8CE", "#DEE2E6", "#BFE3C0", "#F3DBF5"
BORDE, ROJO, VERDEOSC, VIOLETA = "#2B3A4A", "#B01B2E", "#1B7A3E", "#6A1B9A"
W, H = 1000, 545
F_COD, F_DESC, F_FASE, F_PIE = 15, 13, 14, 13.5

plt.rcParams.update({"font.family": "serif", "svg.fonttype": "none"})
fig, ax = plt.subplots(figsize=(W / 100.0, H / 100.0), dpi=100)
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.invert_yaxis(); ax.axis("off")


def caja(x, y, w, h, cod, desc, color, guiones=False):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0,rounding_size=14",
                       facecolor=color, edgecolor=ROJO if guiones else BORDE,
                       lw=1.5, linestyle=(0, (5, 3)) if guiones else "solid",
                       mutation_aspect=1)
    ax.add_patch(p)
    ax.text(x + w / 2, y + 24, cod, ha="center", va="center",
            fontsize=F_COD, fontweight="bold", color="#111111")
    lineas = desc.split("\n")
    y0 = y + h / 2 + 14 - (len(lineas) - 1) * 9.5
    for k, ln in enumerate(lineas):
        ax.text(x + w / 2, y0 + k * 19, ln, ha="center", va="center",
                fontsize=F_DESC, color="#111111")


def flecha(x0, y0, x1, y1, color=BORDE):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=13, lw=1.4, color=color))


def fase(x, y, texto, color):
    ax.text(x, y, texto, fontsize=F_FASE, fontweight="bold", style="italic",
            color=color, ha="left", va="center")


# ---- 1 · AUDITAR
fase(12, 16, "1 · AUDITAR primero", ROJO)
caja(11, 32, 244, 90, "TP1_01", "Verificar cobertura", ROSA, guiones=True)
caja(265, 32, 224, 90, "TP1_02", "Detectar bruma", ROSA)
flecha(257, 77, 263, 77)
flecha(111, 124, 111, 150, ROJO)

# ---- 2 · DESCARGAR
fase(12, 164, "2 · DESCARGAR sólo lo verificado", "#5A6472")
paso2 = [("TP1_03", "Descargar\nSentinel-1/2", GRIS),
         ("TP1_04", "Descargar\nLandsat 9", GRIS),
         ("TP1_05", "Descargar\nGEDI e\nICESat-2", GRIS),
         ("TP1_06", "ALOS-1 y\nNISAR\n(informe y\ndescarga)", ROSA),
         ("TP1_07", "Descargar\nNISAR", GRIS),
         ("TP1_08", "Descargar\nBIOMASS", GRIS)]
BW, SEP, X0, Y2, BH = 160, 5, 9, 178, 112
for i, (cod, desc, col) in enumerate(paso2):
    x = X0 + i * (BW + SEP)
    caja(x, Y2, BW, BH, cod, desc, col)
    if i:
        flecha(x - SEP + 1, Y2 + BH / 2, x - 1, Y2 + BH / 2)
flecha(90, Y2 + BH + 2, 90, Y2 + BH + 28)

# ---- 3 · DOCUMENTAR
fase(12, 326, "3 · DOCUMENTAR", VERDEOSC)
caja(11, 342, 244, 90, "TP1_09", "Inventario final", VERDE)
caja(265, 342, 224, 90, "TP1_10", "Diccionario\nde nombres", VERDE)
flecha(257, 387, 263, 387)

ax.add_patch(FancyBboxPatch((508, 342), 481, 90,
                            boxstyle="round,pad=0,rounding_size=14",
                            facecolor=LILA, edgecolor=VIOLETA, lw=1.6))
LILA_TXT = [("Descargas MANUALES (sin script):", True),
            ("SAOCOM y mosaico PALSAR-2 (banda L).", False),
            ("CONAE y JAXA no ofrecen API:", False),
            ("se bajan a mano — ver Tabla 1.7.", False)]
for k, (ln, neg) in enumerate(LILA_TXT):
    ax.text(748, 364 + k * 20, ln, ha="center", va="center", fontsize=11.5,
            fontweight="bold" if neg else "normal", color=VIOLETA)

ax.text(W / 2, 470, "La regla del práctico: nunca se descarga antes de verificar",
        ha="center", va="center", fontsize=F_PIE, fontweight="bold",
        style="italic", color=ROJO)
ax.text(W / 2, 495, "que el dato existe dentro del AOI. En rosa, los pasos de auditoría.",
        ha="center", va="center", fontsize=F_PIE, fontweight="bold",
        style="italic", color=ROJO)

# --- control: ningun texto puede sobresalir de su caja ---
fig.canvas.draw()
ren = fig.canvas.get_renderer()
inv = ax.transData.inverted()
cajas = [(p.get_x(), p.get_y(), p.get_x() + p.get_width(), p.get_y() + p.get_height())
         for p in ax.patches if isinstance(p, FancyBboxPatch)]
malos = 0
for t in ax.texts:
    bb = t.get_window_extent(renderer=ren)
    x0, y1 = inv.transform((bb.x0, bb.y0))
    x1, y0 = inv.transform((bb.x1, bb.y1))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for bx0, by0, bx1, by1 in cajas:
        if bx0 <= cx <= bx1 and by0 <= cy <= by1:
            if x0 < bx0 + 5 or x1 > bx1 - 5:
                print("  DESBORDA: %r  texto %.0f..%.0f  caja %.0f..%.0f"
                      % (t.get_text()[:32], x0, x1, bx0, bx1))
                malos += 1
            break
print("  textos que desbordan:", malos)

fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.savefig(os.path.join(SALIDA, "fig14_flujo_TP1.png"), dpi=100,
            bbox_inches="tight", pad_inches=0.03)
print("  -> fig14_flujo_TP1.png en %s" % SALIDA)
