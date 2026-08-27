#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP1_07_descargar_nisar.py
Descarga los granulos NISAR GCOV SIN usar la biblioteca 'earthaccess'.

POR QUE EXISTE ESTE SCRIPT
--------------------------
'earthaccess' resulto poco fiable aqui: cortaba las descargas a mitad, daba por
buenos los archivos incompletos (le alcanza con que el NOMBRE exista) y en
ocasiones terminaba sin descargar nada y sin decir por que. Este script hace lo
mismo pero de forma transparente y controlable:

  1. Consulta el catalogo de la NASA (CMR) por REST y obtiene la URL de cada
     granulo, su tamano exacto y su huella geografica.
  2. Mide que fraccion de cada AOI cubre esa huella y descarta lo que no sirve.
  3. Descarga con 'requests', mostrando avance, velocidad y tiempo restante.
  4. REANUDA: si el archivo quedo a medias, pide solo los bytes que faltan
     (cabecera HTTP 'Range'), en vez de empezar de cero.
  5. VERIFICA: al terminar comprueba que el HDF5 este entero leyendo la
     direccion de fin de archivo que declara su superbloque. Si no lo esta,
     reintenta.

CREDENCIALES: usa las de NASA Earthdata guardadas en el archivo .netrc de su
usuario (C:\\Users\\<usuario>\\.netrc). Si no lo tiene, el script se lo crea la
primera vez, preguntandole usuario y contrasena una sola vez.

USO:  python TP1_07_descargar_nisar.py
"""
import getpass
import glob
import os
import struct
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("Falta 'requests'. Ejecutar:  pip install requests")


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

CMR = "https://cmr.earthdata.nasa.gov/search/granules.umm_json"
COLECCION = "NISAR_L2_GCOV_BETA_V1"
PERIODO = "2025-09-01T00:00:00Z,2026-07-13T23:59:59Z"
EPOCA = "02_pre"
# Umbral deliberadamente PERMISIVO. La huella que publica el catalogo es la del
# dato valido de la franja y subestima: los frames del track 075 dan 69-76% de
# la estepa aunque su grilla contiene el AOI entero. Aqui solo se descarta lo
# que claramente no sirve; la verificacion definitiva (cuantos pixeles VALIDOS
# hay realmente dentro del AOI) la hace el recorte de NISAR (en un practico posterior, fuera del TP1).
MIN_COBERTURA = 0.60
DESTINO = os.path.join(DESCARGAS, EPOCA, "NISAR", "GCOV")


def netrc_ok():
    """Se asegura de que exista el .netrc con las credenciales de Earthdata."""
    ruta = os.path.join(os.path.expanduser("~"),
                        "_netrc" if os.name == "nt" else ".netrc")
    if os.path.exists(ruta) and "urs.earthdata.nasa.gov" in open(ruta).read():
        return ruta
    print("No se encontraron credenciales de NASA Earthdata en", ruta)
    u = input("  Usuario Earthdata: ").strip()
    c = getpass.getpass("  Contrasena Earthdata: ")
    with open(ruta, "a") as f:
        f.write("\nmachine urs.earthdata.nasa.gov login %s password %s\n" % (u, c))
    try:
        os.chmod(ruta, 0o600)
    except OSError:
        pass
    print("  Guardadas en", ruta, "(no se volveran a pedir)")
    return ruta


def cobertura(puntos, aoi):
    """Fraccion del AOI cubierta por la huella. Sin shapely: se usa la caja
    envolvente de la huella, que para estos frames (poligonos convexos y muy
    grandes frente al AOI) es equivalente y no agrega dependencias."""
    lons = [p["Longitude"] for p in puntos]
    lats = [p["Latitude"] for p in puntos]
    x0, y0, x1, y1 = AOIS_WGS84[aoi]
    ix = max(0.0, min(max(lons), x1) - max(min(lons), x0))
    iy = max(0.0, min(max(lats), y1) - max(min(lats), y0))
    return ix * iy / ((x1 - x0) * (y1 - y0))


def tamano_declarado(ruta):
    """Bytes que el superbloque HDF5 dice que deberia tener el archivo."""
    try:
        d = open(ruta, "rb").read(64)
        if d[:8] != b"\x89HDF\r\n\x1a\n":
            return 0
        ver = d[8]
        return struct.unpack("<Q", d[40:48] if ver in (0, 1) else d[28:36])[0]
    except Exception:
        return 0


def h5_completo(ruta):
    """El superbloque HDF5 declara donde termina el archivo: si el tamano en
    disco es menor, la descarga se corto."""
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


def fmt(seg):
    seg = int(seg)
    if seg >= 3600:
        return "%dh%02dm" % (seg // 3600, (seg % 3600) // 60)
    return "%02dm%02ds" % (seg // 60, seg % 60)


def barra(f, ancho=22):
    n = int(f * ancho)
    return "#" * n + "-" * (ancho - n)


def descargar(ses, url, destino, tamano_hint=0):
    """Descarga con reanudacion. Devuelve True si el archivo quedo entero.

    El tamano NO se toma del catalogo (a veces no lo informa): se toma de la
    respuesta HTTP, que es la fuente autorizada. Con 'Range' se piden solo los
    bytes que faltan, de modo que una descarga cortada se retoma donde quedo.
    """
    hecho = os.path.getsize(destino) if os.path.exists(destino) else 0
    cab = {"Range": "bytes=%d-" % hecho} if hecho else {}
    r = ses.get(url, headers=cab, stream=True, timeout=180, allow_redirects=True)
    if r.status_code == 416:            # ya estaba entero
        return h5_completo(destino)
    if r.status_code not in (200, 206):
        print("      HTTP %d" % r.status_code)
        return False

    # tamano TOTAL del archivo, segun el servidor
    if r.status_code == 206 and "Content-Range" in r.headers:
        total = int(r.headers["Content-Range"].split("/")[-1])
        modo = "ab"
        print("      reanudando desde %.2f GB de %.2f GB"
              % (hecho / 1e9, total / 1e9))
    else:
        total = int(r.headers.get("Content-Length", 0)) or tamano_hint
        modo, hecho = "wb", 0

    t0, tult = time.time(), 0.0
    inicio = hecho
    with open(destino, modo) as f:
        for bloque in r.iter_content(chunk_size=8 * 1024 * 1024):
            f.write(bloque)
            hecho += len(bloque)
            ahora = time.time()
            if ahora - tult > 0.5:
                tult = ahora
                vel = (hecho - inicio) / max(ahora - t0, 0.1)
                if total:
                    frac = min(hecho / total, 1.0)
                    print("\r      [%s] %3.0f%%  %5.2f/%.2f GB  %5.1f MB/s  "
                          "ETA %s " % (barra(frac), 100 * frac, hecho / 1e9,
                                       total / 1e9, vel / 1e6,
                                       fmt((total - hecho) / max(vel, 1))),
                          end="", flush=True)
                else:
                    print("\r      %.2f GB  %.1f MB/s " % (hecho / 1e9, vel / 1e6),
                          end="", flush=True)
    print()
    return h5_completo(destino)


print(__doc__)
netrc_ok()
ses = requests.Session()          # requests lee el .netrc automaticamente

print("Consultando el catalogo de la NASA...")
r = requests.get(CMR, params={"short_name": COLECCION, "page_size": 100,
                              "temporal": PERIODO,
                              "bounding_box": "%f,%f,%f,%f" % (
                                  min(v[0] for v in AOIS_WGS84.values()),
                                  min(v[1] for v in AOIS_WGS84.values()),
                                  max(v[2] for v in AOIS_WGS84.values()),
                                  max(v[3] for v in AOIS_WGS84.values()))},
                 timeout=90)
r.raise_for_status()
items = r.json()["items"]
print("  %d granulos hallados\n" % len(items))

plan = []
print("COBERTURA DE CADA AOI (medida sobre la huella del granulo):")
for it in items:
    u = it["umm"]
    nom = u["GranuleUR"]
    fecha = next((t[:8] for t in nom.split("_")
                  if len(t) == 15 and t[8:9] == "T"), "?")
    pts = (u["SpatialExtent"]["HorizontalSpatialDomain"]["Geometry"]
           ["GPolygons"][0]["Boundary"]["Points"])
    cobs = {a: cobertura(pts, a) for a in AOIS_WGS84}
    url = next(x["URL"] for x in u["RelatedUrls"]
               if x.get("Type") == "GET DATA" and x["URL"].endswith(".h5"))
    # El tamano del catalogo es solo orientativo (a veces viene vacio):
    # el valor real lo da el servidor al descargar.
    tam = 0
    try:
        for inf in u["DataGranule"]["ArchiveAndDistributionInformation"]:
            if str(inf.get("Name", "")).endswith(".h5") or "Size" in inf:
                tam = int(float(inf["Size"]) * 1024 * 1024)
                break
    except Exception:
        pass
    sirve = max(cobs.values()) >= MIN_COBERTURA
    print("   %s  %s  %s" % (fecha,
          "  ".join("%s=%3.0f%%" % (a.split("_")[0][:6], 100 * c)
                    for a, c in cobs.items()),
          "SE DESCARGA" if sirve else "se descarta (no cubre ningun AOI)"))
    if sirve:
        plan.append((nom, url, tam, fecha))

os.makedirs(DESTINO, exist_ok=True)
for p in glob.glob(os.path.join(DESTINO, "partial_*")):
    os.remove(p)
    print("\n  (resto de earthaccess eliminado: %s)" % os.path.basename(p))

print("\n" + "=" * 72)
pend = []
for nom, url, tam, fecha in plan:
    ruta = os.path.join(DESTINO, nom + ".h5")
    existe = os.path.exists(ruta)
    en_disco = os.path.getsize(ruta) if existe else 0
    declara = tamano_declarado(ruta) if existe else 0
    if not existe:
        print("  %s  FALTA: no descargado (%.2f GB)" % (fecha, tam / 1e9))
        pend.append((nom, url, tam, fecha, ruta))
    elif h5_completo(ruta):
        print("  %s  YA COMPLETO   en disco %.2f GB = declarado %.2f GB"
              % (fecha, en_disco / 1e9, declara / 1e9))
    else:
        print("  %s  INCOMPLETO    en disco %.2f GB < declarado %.2f GB "
              "(catalogo: %.2f GB)"
              % (fecha, en_disco / 1e9, declara / 1e9, tam / 1e9))
        pend.append((nom, url, tam, fecha, ruta))
print("=" * 72)
if not pend:
    sys.exit("\nNo falta nada. El recorte de NISAR se hace en un practico posterior (fuera del TP1).")

total = sum(p[2] for p in pend)
print("\nA descargar: %d granulos%s\n"
      % (len(pend), " (~%.1f GB)" % (total / 1e9) if total else ""))
errores = []
for i, (nom, url, tam, fecha, ruta) in enumerate(pend, 1):
    print("[%d/%d] %s%s" % (i, len(pend), fecha,
          "  (~%.2f GB)" % (tam / 1e9) if tam else ""))
    for intento in (1, 2, 3):
        if descargar(ses, url, ruta, tam):
            print("      OK, HDF5 integro")
            break
        print("      se corto; reintento %d/3" % intento)
    else:
        errores.append(nom)
        print("      ERROR: no se pudo completar")

print("\n=== FIN ===")
if errores:
    print("Fallaron %d. Vuelva a ejecutar este script: reanuda donde quedo."
          % len(errores))
else:
    print("Todos los granulos NISAR estan completos.")
    print("Siguiente paso: el recorte de NISAR a la grilla comun (fuera del TP1).")
