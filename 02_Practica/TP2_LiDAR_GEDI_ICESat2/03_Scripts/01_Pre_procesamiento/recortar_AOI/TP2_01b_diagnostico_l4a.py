#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_01b_diagnostico_l4a.py   ---> auxiliar, no es un paso del practico.

Le PREGUNTA al catalogo de la NASA que colecciones de GEDI existen hoy, en vez
de adivinar el nombre. Se escribio porque la busqueda del L4A devolvio cero
granulos incluso abriendo la ventana a toda la mision, lo cual no puede ser un
problema de cobertura: los AOI estan a 42,6 grados sur y GEDI llega a 51,6.

No descarga nada. Solo consulta y muestra.

USO (entorno conda 'aoi'):   python TP2_01b_diagnostico_l4a.py
"""
import os
import sys

try:
    import earthaccess
except ImportError:
    sys.exit("Falta earthaccess. Ejecutar:  pip install earthaccess")

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d):
    if os.path.isdir(os.path.join(_d, "funciones")):
        sys.path.insert(0, os.path.join(_d, "funciones"))
        sys.path.insert(0, os.path.join(_d, "configuracion"))
        break
    _d = os.path.dirname(_d)

from aoi_config import AOIS_WGS84

BBOX = AOIS_WGS84["BOSQUE_NW_02"]
PERIODO = ("2024-09-01", "2025-03-31")

print(__doc__)
auth = earthaccess.login(persist=True)
print("Autenticado:", bool(getattr(auth, "authenticated", False)))
print()

# ------------------------------------------------------------------ CONTROL
# Si esto tampoco devuelve nada, el problema NO son los nombres de coleccion
# sino la consulta o la autenticacion.
print("=" * 70)
print("CONTROL: el L2A que el practico YA uso, mismo AOI y mismo periodo")
print("=" * 70)
for sn, ver in (("GEDI02_A", "003"), ("GEDI02_A", None), ("GEDI02_B", "003")):
    try:
        kw = dict(short_name=sn, bounding_box=BBOX, temporal=PERIODO)
        if ver:
            kw["version"] = ver
        g = earthaccess.search_data(**kw)
        print("   %-10s v%-5s -> %d granulos" % (sn, ver or "(sin)", len(g)))
    except Exception as e:
        print("   %-10s v%-5s -> ERROR: %s" % (sn, ver or "(sin)", e))
print()

# ------------------------------------------------- QUE COLECCIONES GEDI HAY
print("=" * 70)
print("COLECCIONES DE GEDI EN EL CATALOGO (nombre corto y version)")
print("=" * 70)
vistos = set()
for consulta in ("GEDI L4A aboveground biomass density",
                 "GEDI aboveground biomass",
                 "GEDI L4",
                 "GEDI"):
    try:
        cols = earthaccess.search_datasets(keyword=consulta, count=40)
    except Exception as e:
        print("   consulta %-38s ERROR: %s" % (repr(consulta), e))
        continue
    print("\n   consulta: %s  -> %d colecciones" % (repr(consulta), len(cols)))
    for c in cols:
        try:
            u = c["umm"]
            sn = u.get("ShortName", "?")
            ver = u.get("Version", "?")
            if (sn, ver) in vistos:
                continue
            vistos.add((sn, ver))
            rng = ""
            try:
                r = u["TemporalExtents"][0]["RangeDateTimes"][0]
                rng = "%s a %s" % (r.get("BeginningDateTime", "")[:10],
                                   r.get("EndingDateTime", "en curso")[:10])
            except Exception:
                pass
            marca = "  <-- BIOMASA" if "L4A" in sn.upper() or "L4" in sn.upper() else ""
            print("      %-34s v%-6s %s%s" % (sn, ver, rng, marca))
        except Exception:
            continue

print()
print("=" * 70)
print("QUE HACER CON ESTO")
print("=" * 70)
print("Pasarle al asistente esta salida completa. Con el nombre corto y la")
print("version reales, se corrige la lista CANDIDATOS de")
print("TP2_01b_descargar_gedi_l4a.py y la descarga funciona.")
print()
print("Si el CONTROL de arriba tambien dio 0 granulos, el problema no son los")
print("nombres sino la consulta o las credenciales, y hay que mirar eso primero.")
