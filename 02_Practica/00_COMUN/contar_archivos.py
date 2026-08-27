#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contar_archivos.py
Cuenta los archivos de cada practico, carpeta por carpeta, y escribe la tabla en
formato Markdown lista para pegar en el LEEME.

POR QUE EXISTE
--------------
Los LEEME abren con una tabla de "cuantos archivos hay en cada carpeta". Escrita a
mano, esa tabla se desactualiza a la primera sesion de trabajo y despues nadie le
cree a la documentacion. Corriendo esto al cerrar cada sesion, el numero siempre
coincide con el disco.

USO:  python contar_archivos.py           (todos los practicos)
      python contar_archivos.py TP2       (uno solo)
"""
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
PROYECTO = os.path.dirname(RAIZ)
IGNORAR = {"_PARA_BORRAR", "99_PRIVADO_NO_DISTRIBUIR", "__pycache__"}
SIN_CONTAR = (".pyc", ".log")


def contar(carpeta):
    n = 0
    for _, dirs, files in os.walk(carpeta):
        dirs[:] = [d for d in dirs if d not in IGNORAR]
        n += len([f for f in files if not f.endswith(SIN_CONTAR)])
    return n


filtro = sys.argv[1] if len(sys.argv) > 1 else None
practicos = sorted(d for d in os.listdir(PROYECTO)
                   if d.startswith("TP") and os.path.isdir(os.path.join(PROYECTO, d)))

for tp in practicos:
    if filtro and not tp.startswith(filtro):
        continue
    base = os.path.join(PROYECTO, tp)
    print("=" * 72)
    print(tp)
    print("=" * 72)
    print("| Carpeta | Archivos |")
    print("|---|---|")
    total = 0
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d)
        if os.path.isdir(p) and d not in IGNORAR:
            n = contar(p)
            total += n
            print("| `%s/` | %d |" % (d, n))
    sueltos = len([f for f in os.listdir(base)
                   if os.path.isfile(os.path.join(base, f))])
    total += sueltos
    print("| (LEEME y README de la raiz) | %d |" % sueltos)
    print("| **TOTAL** | **%d** |" % total)
    print()
