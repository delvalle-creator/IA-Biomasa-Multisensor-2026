#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP1_06_alos_nisar_informe.py
Informa la disponibilidad y DESCARGA dos fuentes de banda L desde NASA Earthdata (ASF):

1) ALOS-1 PALSAR quad-pol (modo PLR, 2007-2010)
   Unica fuente de POLARIMETRIA COMPLETA (HH, HV, VH, VV) y de acceso libre en
   esta zona. Es historica: no coincide con las fechas de SAOCOM ni de
   Sentinel-1, y debe interpretarse como referencia estructural de otra epoca.
   Las escenas quad-pol tienen franja angosta (~30 km) y frames cortos, de modo
   que hacen falta DOS frames contiguos para cubrir cada AOI.

   Cobertura verificada (fraccion del AOI cubierta por la union de sus frames):
     BOSQUE_NW_02: 21/07/2007 100% | 05/09/2007 100% | 06/12/2007  99%
                   21/04/2009 100%
     ESTEPA_NW_02: 06/06/2009  93%  (la mejor disponible; ninguna llega al 100%)

2) NISAR (banda L, 2025-2026), producto GCOV y sus variantes complejas.
   GCOV  L2: matriz de covarianza GEOCODIFICADA y con correccion radiometrica
             de terreno ya aplicada (los valores son gamma0). Es el producto
             directo para analisis multitemporal: se recorta a la grilla comun
             sin mas (el recorte a la grilla comun se hace fuera del TP1). SNAP todavia no lo lee.
   GSLC  L2: complejo geocodificado.
   RSLC  L1: complejo en geometria de radar, para polarimetria propia e InSAR.

   ATENCION: son productos BETA (calibracion en curso). Y sobre esta zona NISAR
   adquiere en DUAL-POL HH/HV, no en polarimetria completa: para el practico de
   polarimetria hay que usar ALOS-1.

COBERTURA: SE VERIFICA ANTES DE DESCARGAR
-----------------------------------------
La busqueda se hace por la caja que engloba los dos AOI, y eso devuelve
granulos que TOCAN esa caja pero que pueden dejar afuera casi todo un AOI. Los
frames del track 075, por ejemplo, cubren la estepa entera y solo el 13% del
bosque. Por eso el script mide, granulo por granulo, que fraccion de cada AOI
cubre realmente la huella, imprime la tabla y descarta lo que no llegue al 90%
de algun AOI. Sin esta comprobacion se pueden bajar decenas de GB inservibles.

USO:
  python TP1_06_alos_nisar_informe.py                 solo INFORMA (no descarga)
  python TP1_06_alos_nisar_informe.py --alos          ALOS-1 quad-pol (6,3 GB)
  python TP1_06_alos_nisar_informe.py --gcov          NISAR GCOV
  python TP1_06_alos_nisar_informe.py --gslc          NISAR GSLC
  python TP1_06_alos_nisar_informe.py --rslc          NISAR RSLC (el mas pesado)
  python TP1_06_alos_nisar_informe.py --alos --gcov   (se pueden combinar)

Las descargas se reanudan: los archivos ya completos se saltean, y los restos
de una interrupcion previa (parciales y .h5 truncados) se eliminan y se
vuelven a bajar.
"""
import glob
import os
import struct
import sys

try:
    import earthaccess
except ImportError:
    sys.exit("Falta 'earthaccess'. Ejecutar:  pip install earthaccess")


# La carpeta funciones/ es hermana de esta, no esta en el sys.path por defecto.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "funciones"))


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

from aoi_config import AOIS_WGS84, DESCARGAS

ARG = [a.lower() for a in sys.argv[1:]]
HACER_ALOS = "--alos" in ARG or "--solo-alos" in ARG
PEDIDAS = [c for c in ("gcov", "gslc", "rslc") if "--" + c in ARG]
if "--solo-nisar" in ARG or "--nisar" in ARG:
    PEDIDAS = ["gcov", "gslc", "rslc"]
SOLO_INFORME = not HACER_ALOS and not PEDIDAS

# ---------------------------------------------------------------- ALOS-1 QP
ALOS_QP = {
    "BOSQUE_NW_02": [
        ("2007-07-21", ["ALPSRP079284470", "ALPSRP079284480"], "100%"),
        ("2007-09-05", ["ALPSRP085994470", "ALPSRP085994480"], "100%"),
        ("2007-12-06", ["ALPSRP099414470", "ALPSRP099414480"], "99%"),
        ("2009-04-21", ["ALPSRP172576320", "ALPSRP172576330"], "100%"),
    ],
    "ESTEPA_NW_02": [
        ("2009-06-06", ["ALPSRP179286320", "ALPSRP179286330"], "93%"),
    ],
}
ALOS_COLECCION = "ALOS_PSR_L1.1"     # L1.1: complejo, apto para polarimetria

# ---------------------------------------------------------------- NISAR
NISAR = [
    ("NISAR_L2_GCOV_BETA_V1", "GCOV", "covarianza geocodificada (RTC aplicada)"),
    ("NISAR_L2_GSLC_BETA_V1", "GSLC", "complejo geocodificado"),
    ("NISAR_L1_RSLC_BETA_V1", "RSLC", "complejo en geometria de radar"),
]
NISAR_PERIODO = ("2025-09-01", "2026-07-13")
EPOCA_NISAR = "02_pre"
MIN_COBERTURA = 0.90


def bbox_union():
    lons = [v[0] for v in AOIS_WGS84.values()] + [v[2] for v in AOIS_WGS84.values()]
    lats = [v[1] for v in AOIS_WGS84.values()] + [v[3] for v in AOIS_WGS84.values()]
    return (min(lons), min(lats), max(lons), max(lats))


def cobertura_aoi(granulo, aoi):
    """Fraccion del AOI (0 a 1) que cubre realmente la huella del granulo."""
    try:
        from shapely.geometry import Polygon, box
    except ImportError:
        return None
    try:
        pts = (granulo["umm"]["SpatialExtent"]["HorizontalSpatialDomain"]
               ["Geometry"]["GPolygons"][0]["Boundary"]["Points"])
        huella = Polygon([(p["Longitude"], p["Latitude"]) for p in pts])
    except Exception:
        return None
    caja = box(*AOIS_WGS84[aoi])
    return huella.intersection(caja).area / caja.area


def fecha_granulo(nombre):
    for t in nombre.split("_"):
        if len(t) == 15 and t[8] == "T" and t[:8].isdigit():
            return t[:8]
    return "00000000"


def gb(granulos):
    try:
        return sum(g.size() for g in granulos) / 1024
    except Exception:
        return 0.0


def espacio_libre_gb(ruta):
    import shutil as _sh
    return _sh.disk_usage(ruta).free / 1e9


def h5_completo(ruta):
    """Dice si un .h5 esta ENTERO, sin abrirlo ni necesitar h5py.

    Todo archivo HDF5 empieza con un 'superbloque' que declara la direccion del
    final del archivo. Si el tamano real en disco es menor que esa direccion, la
    descarga se corto. Esta comprobacion es imprescindible: 'earthaccess' da por
    bueno cualquier archivo cuyo NOMBRE ya exista, aunque por dentro este a
    medias, y entonces lo saltea para siempre.
    """
    try:
        tam = os.path.getsize(ruta)
        d = open(ruta, "rb").read(64)
        if d[:8] != b"\x89HDF\r\n\x1a\n":
            return False
        ver = d[8]
        eof = struct.unpack("<Q", d[40:48] if ver in (0, 1) else d[28:36])[0]
        return tam >= eof > 0
    except Exception:
        return False


def limpiar_parciales(carpeta):
    """Borra los restos de una descarga interrumpida: 'partial_*' y .h5 truncados."""
    n = 0
    for p in glob.glob(os.path.join(carpeta, "partial_*")):
        try:
            os.remove(p)
            n += 1
        except OSError:
            pass
    for p in glob.glob(os.path.join(carpeta, "*.h5")):
        if not h5_completo(p):
            print("     TRUNCADO, se vuelve a descargar: %s (%.2f GB)"
                  % (os.path.basename(p)[:52], os.path.getsize(p) / 1e9))
            try:
                os.remove(p)
                n += 1
            except OSError:
                pass
    if n:
        print("     (%d archivo(s) incompleto(s) eliminado(s))" % n)


def ya_descargados(carpeta):
    """Solo cuenta los .h5 INTEGROS."""
    return len([p for p in glob.glob(os.path.join(carpeta, "*.h5"))
                if h5_completo(p)])


print(__doc__)
# 'interactive' OBLIGA a pedir usuario y contrasena aunque ya esten guardadas.
# Sin strategy, earthaccess busca primero en las variables de entorno, luego en
# el archivo ~/.netrc (donde persist=True las guardo la primera vez) y solo
# pregunta si no encuentra nada. Asi el script se puede dejar corriendo solo.
auth = earthaccess.login(persist=True)
if not auth.authenticated:
    sys.exit("No se pudo autenticar en NASA Earthdata.")

caja = bbox_union()

# ======================= INFORME PREVIO (siempre) =======================
print("\n" + "=" * 72)
print("INVENTARIO: que hay disponible, que cubre cada AOI y cuanto pesa")
print("=" * 72)
print("  Espacio libre en el disco: %.0f GB" % espacio_libre_gb(DESCARGAS))

inventario = {}
for coleccion, etiqueta, descripcion in NISAR:
    res = earthaccess.search_data(short_name=coleccion, bounding_box=caja,
                                  temporal=NISAR_PERIODO)
    print("\n  NISAR %s (%s): %d granulos hallados" % (etiqueta, descripcion,
                                                       len(res)))
    utiles = []
    for g in res:
        nom = g["umm"]["GranuleUR"]
        cobs = {a: cobertura_aoi(g, a) for a in AOIS_WGS84}
        if any(c is None for c in cobs.values()):
            utiles.append(g)          # sin shapely no se puede medir: se baja
            continue
        sirve = max(cobs.values()) >= MIN_COBERTURA
        detalle = "  ".join("%s=%3.0f%%" % (a.split("_")[0][:6], 100 * c)
                            for a, c in cobs.items())
        veredicto = "SE DESCARGA" if sirve else "se descarta (no cubre ningun AOI)"
        print("     %s  %s  ->  %s" % (fecha_granulo(nom), detalle, veredicto))
        if sirve:
            utiles.append(g)

    carpeta = os.path.join(DESCARGAS, EPOCA_NISAR, "NISAR", etiqueta)
    hechos = ya_descargados(carpeta) if os.path.isdir(carpeta) else 0
    inventario[etiqueta.lower()] = (utiles, carpeta, hechos)
    total = gb(utiles)
    falta = total * (1 - hechos / len(utiles)) if utiles else 0.0
    print("     --> %d utiles | %.1f GB | ya completos: %d | faltan ~%.1f GB"
          % (len(utiles), total, hechos, falta))

alos_n = sum(len(g) for f in ALOS_QP.values() for _, g, _ in f)
print("\n  ALOS-1 quad-pol (polarimetria completa, historica): %d frames | 6.3 GB"
      % alos_n)

if SOLO_INFORME:
    print("\n" + "=" * 72)
    print("No se descargo nada. Elija que bajar, por ejemplo:")
    print("   python TP1_06_alos_nisar_informe.py --alos --gcov")
    print("Para el analisis multitemporal alcanza con GCOV, que ya viene")
    print("geocodificado y con correccion radiometrica de terreno.")
    sys.exit(0)

# ============================ ALOS-1 quad-pol ============================
if HACER_ALOS:
    print("\n" + "=" * 72)
    print("ALOS-1 PALSAR quad-pol (polarimetria completa, 2007-2010)")
    print("=" * 72)
    for aoi, fechas in ALOS_QP.items():
        carpeta = os.path.join(DESCARGAS, "00_alos", aoi,
                               "ALOS_PALSAR_QP")
        os.makedirs(carpeta, exist_ok=True)
        for fecha, granulos, cobertura in fechas:
            print("\n  %s | %s | cobertura del AOI: %s" % (aoi, fecha, cobertura))
            destino = os.path.join(carpeta, fecha)
            os.makedirs(destino, exist_ok=True)
            for g in granulos:
                if any(g in f for f in os.listdir(destino)):
                    print("    %s: ya descargado" % g)
                    continue
                res = earthaccess.search_data(short_name=ALOS_COLECCION,
                                              granule_name=g)
                if not res:
                    print("    %s: NO ENCONTRADO en el catalogo" % g)
                    continue
                print("    %s: descargando (%.2f GB)..." % (g, gb(res)), flush=True)
                earthaccess.download(res, destino, threads=2)

# ================================= NISAR =================================
for etiqueta in PEDIDAS:
    res, carpeta, hechos = inventario[etiqueta]
    if not res:
        print("\nNISAR %s: no hay granulos que cubran ningun AOI." % etiqueta.upper())
        continue
    os.makedirs(carpeta, exist_ok=True)
    limpiar_parciales(carpeta)
    total = gb(res)
    libre = espacio_libre_gb(DESCARGAS)
    print("\n" + "=" * 72)
    print("NISAR %s: %d granulos utiles, %.1f GB | libre en disco: %.0f GB"
          % (etiqueta.upper(), len(res), total, libre))
    print("=" * 72)
    if total > libre * 0.9:
        print("  ATENCION: no hay espacio suficiente. Se omite esta coleccion.")
        continue

    for i, g in enumerate(res, 1):
        nombre = g["umm"]["GranuleUR"]
        destino = os.path.join(carpeta, nombre + ".h5")
        if h5_completo(destino):
            print("  [%d/%d] %s: ya completo" % (i, len(res), nombre[:44]))
            continue
        for intento in (1, 2, 3):
            print("  [%d/%d] %s: descargando (intento %d/3)..."
                  % (i, len(res), nombre[:44], intento), flush=True)
            earthaccess.download([g], carpeta, threads=1)
            for p in glob.glob(os.path.join(carpeta, "partial_*")):
                try:
                    os.remove(p)
                except OSError:
                    pass
            hallado = glob.glob(os.path.join(carpeta, nombre + "*"))
            if hallado and h5_completo(hallado[0]):
                print("        OK, archivo integro (%.2f GB)"
                      % (os.path.getsize(hallado[0]) / 1e9))
                break
            for h in hallado:
                try:
                    os.remove(h)
                except OSError:
                    pass
            print("        la descarga se corto; se reintenta")
        else:
            print("        ERROR: no se pudo completar tras 3 intentos.")

print("\nListo.")
print("  ALOS-1 quad-pol -> 00_COMUN/08_Originales_crudos/00_alos/<AOI>/ALOS_PALSAR_QP/")
print("  NISAR           -> 00_COMUN/08_Originales_crudos/%s/NISAR/<GCOV|GSLC|RSLC>/" % EPOCA_NISAR)
print("\nRecuerde: ALOS-1 es de 2007-2010 (referencia historica) y NISAR sobre "
      "esta zona\nadquiere en dual-pol HH/HV, no en polarimetria completa.")
print("El recorte de NISAR a la grilla comun NO es parte del TP1: se hace en un practico posterior.")
