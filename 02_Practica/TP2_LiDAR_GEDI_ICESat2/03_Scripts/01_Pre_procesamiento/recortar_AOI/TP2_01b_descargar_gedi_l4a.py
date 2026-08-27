#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_01b_descargar_gedi_l4a.py   ---> va JUSTO DESPUES del TP2_01.

Se numera 01b, y no 09, porque tiene que correr ANTES del TP2_07: es el 07 el
que necesita este producto para poder hablar de biomasa en vez de altura.

QUE HACE
--------
Descarga el producto GEDI L4A (Aboveground Biomass Density) sobre los dos AOI y
extrae, a un CSV por sitio, los disparos que caen dentro del recinto de 15 x 15
km. Es el insumo que le falta al TP2_07 para entregar BIOMASA en Mg/ha en vez
de altura de dosel.

POR QUE HACE FALTA
------------------
Hoy el proyecto entero se calibra contra rh95, la altura del dosel, porque el
L4A no esta descargado. Eso obliga a decir "altura" donde los objetivos dicen
"biomasa", y deja sin sustento el producto central del TP5, que es la biomasa
quemada en megagramos por hectarea. Con este script esa cadena se cierra.

Lo que aporta el L4A y no se puede improvisar: la NASA ajusto los modelos POR
GRUPO DE VEGETACION con parcelas de campo reales, y publica ademas el error
estandar de cada disparo. Inventar una alometria propia con coeficientes de
otro bosque produce numeros que parecen razonables y son falsos.

CREDENCIALES
------------
Se piden al ejecutar y NO quedan escritas en ningun archivo del proyecto
(regla 8 del README). Si usted ya tiene un ~/.netrc de Earthdata, earthaccess
lo usa solo. Registro gratuito en: https://urs.earthdata.nasa.gov

ATENCION AL PESO Y AL PERIODO
-----------------------------
Cada granulo pesa entre 200 y 500 MB. El script informa cuantos encontro y
cuanto ocupan ANTES de bajar nada; con --solo-buscar se queda solo en eso.

Y una advertencia que importa: la version 2.1 del L4A cubre el periodo anterior
a la hibernacion de GEDI. Si sobre este periodo (sep-2024 a mar-2025, el mismo
del L2A que ya se uso) no hubiera granulos, el script NO falla en silencio:
informa que hay cero y consulta que periodo SI esta disponible, para que la
decision se tome con el dato a la vista y no a ciegas.

ENTRADA   ninguna (descarga de NASA Earthdata)
SALIDA    00_COMUN/08_Originales_crudos/02_pre/GEDI_L4A/
          TP2_LiDAR_GEDI_ICESat2/02_Subsets_SNAP_QGIS/GEDI_L4A/GEDI04_A_<AOI>_shots15km.csv

USO (entorno conda 'aoi'):
  pip install earthaccess
  python TP2_01b_descargar_gedi_l4a.py                 (descarga y extrae)
  python TP2_01b_descargar_gedi_l4a.py --solo-buscar   (solo informa, no baja)
"""
import csv
import glob
import os
import sys
import warnings

# earthaccess 1.0 avisa que .size pasa a ser atributo. El aviso sale de su
# propio codigo, no del nuestro, y solo ensucia la salida.
warnings.filterwarnings("ignore", category=FutureWarning)

try:
    import earthaccess
except ImportError:
    sys.exit("Falta el paquete 'earthaccess'. Ejecutar:  pip install earthaccess")
try:
    import h5py
except ImportError:
    sys.exit("Falta h5py. Ejecutar: conda install -c conda-forge h5py pyproj")
try:
    from pyproj import Transformer
except ImportError:
    sys.exit("Falta pyproj. Ejecutar: conda install -c conda-forge h5py pyproj")


# --- para que Python encuentre funciones/ y configuracion/ del practico ---
# Se sube por el arbol hasta dar con la carpeta 'funciones', de modo que el
# script corra desde cualquier directorio de trabajo y a cualquier profundidad.
_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d):
    if os.path.isdir(os.path.join(_d, "funciones")):
        sys.path.insert(0, os.path.join(_d, "funciones"))
        sys.path.insert(0, os.path.join(_d, "configuracion"))
        break
    _d = os.path.dirname(_d)

from aoi_config import AOIS_WGS84, EPSG, DESCARGAS

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
DESTINO_CSV = os.path.join(TP2, "02_Subsets_SNAP_QGIS", "GEDI_L4A")

# Mismo periodo que el L2A/L2B ya usados: la referencia tiene que ser la misma
# poblacion de disparos, no otra.
PERIODO = ("2024-09-01", "2025-03-31")
EPOCA = "02_pre"

# Los nombres cortos del ORNL DAAC llevan un SUFIJO NUMERICO (el numero de
# dataset): la coleccion no se llama "GEDI_L4A_AGB_Density_V2_1" sino
# "GEDI_L4A_AGB_Density_V2_1_2056". Sin ese sufijo la busqueda devuelve cero sin
# dar ningun error, que es exactamente lo que paso la primera vez.
#
# Verificado contra el catalogo el 26/07/2026 con TP2_01b_diagnostico_l4a.py:
#   GEDI_L4A_AGB_Density_V3_2508     v3     2019-04-04 a en curso   <- la vigente
#   GEDI_L4A_AGB_Density_V2_1_2056   v2.1   2019-04-17 a 2025-07-09
# Las dos cubren el periodo del L2A que usa el practico (sep-2024 a mar-2025).
CANDIDATOS = [
    ("GEDI_L4A_AGB_Density_V3_2508", "3"),
    ("GEDI_L4A_AGB_Density_V3_2508", None),
    ("GEDI_L4A_AGB_Density_V2_1_2056", "2.1"),
    ("GEDI_L4A_AGB_Density_V2_1_2056", None),
]

SOLO_BUSCAR = "--solo-buscar" in sys.argv

# La lista de campos del L4A y la rutina que los extrae viven en
# funciones/gedi_l4a.py, porque las comparte con TP2_01c_reextraer_l4a.py. Una
# sola lista para los dos: si estuviera duplicada, una de las dos copias
# quedaria vieja y el CSV saldria distinto segun quien lo hubiera generado.
from gedi_l4a import extraer_h5


def buscar(bbox, temporal):
    """Devuelve (granulos, short_name, version) del primer candidato con datos."""
    for short_name, version in CANDIDATOS:
        try:
            kw = dict(short_name=short_name, bounding_box=bbox, temporal=temporal)
            if version:
                kw["version"] = version
            g = earthaccess.search_data(**kw)
        except Exception:
            continue
        if g:
            return g, short_name, version

    # Ninguno de los nombres conocidos sirvio. Antes de darse por vencido, se le
    # pregunta al catalogo: asi el script sobrevive a la proxima version.
    try:
        cols = earthaccess.search_datasets(
            keyword="GEDI L4A aboveground biomass density", count=40)
    except Exception:
        return [], None, None
    for c in cols:
        try:
            sn = c["umm"]["ShortName"]
        except Exception:
            continue
        if "L4A" not in sn.upper():
            continue
        try:
            g = earthaccess.search_data(short_name=sn, bounding_box=bbox,
                                        temporal=temporal)
        except Exception:
            continue
        if g:
            print("   (coleccion hallada por busqueda automatica: %s)" % sn)
            return g, sn, None
    return [], None, None


def tamano_gb(granulos):
    total = 0.0
    for g in granulos:
        try:
            t = g.size
            total += float(t() if callable(t) else t)      # MB
        except Exception:
            pass
    return total / 1024.0


def diagnostico_cobertura(bbox):
    """Si no hay granulos en el periodo pedido, averigua cual SI hay."""
    print()
    print("   " + "!" * 66)
    print("   No hay granulos de L4A entre %s y %s sobre este AOI." % PERIODO)
    print("   Consultando que periodo esta disponible...")
    g, sn, ver = buscar(bbox, ("2019-01-01", "2027-12-31"))
    if not g:
        print("   El catalogo no devuelve NINGUN granulo de L4A sobre este AOI.")
        print("   En ese caso el TP2_07 sigue trabajando con rh95 (altura de")
        print("   dosel), y los objetivos de TP3, TP4 y TP5 tienen que redactarse")
        print("   en terminos de altura, no de biomasa.")
    else:
        fechas = []
        for x in g:
            try:
                fechas.append(x["umm"]["TemporalExtent"]["RangeDateTime"]
                              ["BeginningDateTime"][:10])
            except Exception:
                pass
        fechas.sort()
        print("   Coleccion: %s" % sn)
        if fechas:
            print("   Hay %d granulos, entre %s y %s."
                  % (len(g), fechas[0], fechas[-1]))
        else:
            print("   Hay %d granulos (sin fecha legible)." % len(g))
        print()
        print("   DECISION QUE HAY QUE TOMAR: el L4A no cubre el mismo periodo")
        print("   que el L2A ya descargado. Usar biomasa de un periodo y")
        print("   estructura de otro mezcla dos estados del bosque. Conviene")
        print("   consultar antes de seguir.")
    print("   " + "!" * 66)


def extraer(carpeta_h5, aoi):
    """Vuelca a CSV los disparos del L4A que caen dentro del AOI.

    La implementacion esta en funciones/gedi_l4a.py; aca queda el nombre para no
    tocar el resto del script.
    """
    return extraer_h5(carpeta_h5, aoi, DESTINO_CSV)


print(__doc__)

auth = earthaccess.login(persist=True)
if not auth.authenticated:
    sys.exit("No se pudo autenticar en Earthdata.")

resumen = []
for aoi, bbox in AOIS_WGS84.items():
    print("=" * 72)
    print(aoi)
    print("=" * 72)
    granulos, short_name, version = buscar(bbox, PERIODO)
    if not granulos:
        diagnostico_cobertura(bbox)
        resumen.append((aoi, 0, 0))
        continue

    print("   coleccion : %s%s"
          % (short_name, " v%s" % version if version else ""))
    print("   granulos  : %d" % len(granulos))
    print("   tamano    : %.1f GB aproximadamente" % tamano_gb(granulos))

    if SOLO_BUSCAR:
        resumen.append((aoi, len(granulos), 0))
        continue

    carpeta = os.path.join(DESCARGAS, EPOCA, "GEDI_L4A", aoi)
    os.makedirs(carpeta, exist_ok=True)
    for p in glob.glob(os.path.join(carpeta, "partial_*")):
        os.remove(p)

    for intento in range(3):
        try:
            earthaccess.download(granulos, carpeta, threads=2)
            break
        except Exception as e:
            print("   interrupcion (%s); reintento %d/3..." % (e, intento + 1))

    n = extraer(carpeta, aoi)
    resumen.append((aoi, len(granulos), n))
    print()

print("=" * 72)
print("RESUMEN")
print("=" * 72)
for aoi, ng, n in resumen:
    print("   %-14s %3d granulos, %6d disparos extraidos" % (aoi, ng, n))
print()
if SOLO_BUSCAR:
    print("Esto fue solo una BUSQUEDA: no se descargo ni se extrajo nada, y por eso")
    print("la columna de disparos figura en cero. No es un fallo.")
    print()
    if any(ng for _, ng, _ in resumen):
        print("Hay granulos disponibles. Para descargarlos de verdad, corra el mismo")
        print("comando SIN --solo-buscar:")
        print("   python TP2_01b_descargar_gedi_l4a.py")
    else:
        print("No se encontraron granulos. Revise el periodo y la coleccion antes")
        print("de intentar la descarga.")
elif any(n for _, _, n in resumen):
    print("SIGUIENTE PASO. Vuelva a correr, en este orden:")
    print("   python TP2_07_biomasa_referencia.py")
    print("      (ahora si encuentra el L4A: pega agbd y agbd_se a cada huella")
    print("       y rehace la particion por bloques espaciales)")
    print("   python TP2_08_exportar_para_gis.py")
    print("      (para verificar en QGIS que la biomasa alta caiga en el bosque")
    print("       y no en la estepa)")
    print()
    print("Y despues, en el TP3 y el TP4, los que cruzan con GEDI:")
    print("   python TP3_05_saturacion_y_modelo.py")
    print("   python TP4_08_saturacion_radar.py")
else:
    print("No se extrajo ningun disparo. El TP2_07 seguira usando rh95 (altura")
    print("de dosel) como referencia, y hay que decirlo en el informe.")
