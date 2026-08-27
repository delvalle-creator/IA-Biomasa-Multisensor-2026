#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP1_08_descargar_biomass.py   ---> OCTAVO script del TP1.

Descarga imagenes BIOMASS (ESA, radar banda P) recortadas por AOI desde el
catalogo STAC de ESA MAAP. Es la contraparte de banda P del bloque de radar:
Sentinel-1 (banda C), NISAR/ALOS (banda L) y aqui BIOMASS (banda P).

A diferencia de los otros satelites, BIOMASS EXIGE un token de la ESA. El
procedimiento completo (crear la cuenta "EO Sign In" y generar el token
offline) esta en C:\\Temp\\BIOMASS\\04_Informe\\TUTORIAL_paso_a_paso.docx.
Este script es la version integrada al TP1 del que vive en esa carpeta.

Como pasar el token (una de las dos):
  - variable de entorno:   set BIOMASS_TOKEN=<tu_token_offline>
  - o exportarlo antes:  set BIOMASS_TOKEN=...   (NUNCA pegarlo en el codigo)
Sin token, el script SOLO busca y lista (no descarga).

USO (entorno conda 'aoi', con pystac-client instalado):
  pip install pystac-client requests shapely      (una sola vez)
  python TP1_08_descargar_biomass.py

Cada producto se guarda en:
  08_Originales_crudos/<epoca>/BIOMASS/<AOI>/<coleccion>/
Usar los productos 1S (traen la imagen SAR); los 1M son livianos sin imagen.
Abrir las imagenes con ESA SNAP 13+ (Microwave Toolbox).

SIGUIENTE PASO:  python TP1_09_inventario.py
"""
import os
import getpass
import sys

try:
    import requests
    from pystac_client import Client
except ImportError:
    sys.exit("Falta requests o pystac-client. Ejecute: pip install pystac-client requests shapely")

AQUI = os.path.dirname(os.path.abspath(__file__))
PROYECTO = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, os.path.join(PROYECTO, "00_COMUN"))

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

from configuracion_comun import AOIS_WGS84, DESCARGAS_ORIGINALES, epoca_de  # noqa: E402

# --- token de la ESA (offline -> access) ---------------------------------
OFFLINE_TOKEN = os.environ.get("BIOMASS_TOKEN", "").strip()
TOKEN_URL = "https://iam.maap.eo.esa.int/realms/esa-maap/protocol/openid-connect/token"
CLIENT_ID = "offline-token"
CLIENT_SECRET = (os.environ.get("BIOMASS_CLIENT_SECRET", "").strip()
                 or getpass.getpass("client_secret de ESA MAAP: "))
# Regla 8 del README: no se guardan secretos en 03_Scripts. Se toma de la
# variable de entorno BIOMASS_CLIENT_SECRET o se pide al ejecutar.

CATALOG_URL = "https://catalog.maap.eo.esa.int/catalogue/"
COLECCIONES = ["BiomassLevel1a", "BiomassLevel1b", "BiomassLevel1c", "BiomassLevel2a"]
FECHA_INICIO = "2025-09-01T00:00:00Z"
FECHA_FIN = "2026-12-31T23:59:59Z"
SOLO_1S = True
MAX_POR_AOI = None


def obtener_access_token():
    if not OFFLINE_TOKEN:
        return ""
    r = requests.post(TOKEN_URL, data={
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token", "refresh_token": OFFLINE_TOKEN,
        "scope": "offline_access openid"}, timeout=60)
    r.raise_for_status()
    return r.json()["access_token"]


ACCESS_TOKEN = obtener_access_token()
print("Access token OK." if ACCESS_TOKEN else "Sin token: solo BUSQUEDA (sin descarga).")


def es_1S(item):
    return "__1S" in item.id or "_1S_" in item.id


def carpeta_de(item, aoi, col):
    try:
        fecha = item.datetime.strftime("%Y%m%d")
        epoca = epoca_de(fecha)
    except Exception:
        epoca = "02_pre"
    return os.path.join(DESCARGAS_ORIGINALES, epoca, "BIOMASS", aoi, col)


def descargar_item(item, carpeta):
    global ACCESS_TOKEN
    os.makedirs(carpeta, exist_ok=True)
    for nombre_asset, asset in item.assets.items():
        destino = os.path.join(carpeta, "%s__%s" % (item.id, nombre_asset))
        if os.path.exists(destino) and os.path.getsize(destino) > 0:
            print("      ya estaba ->", os.path.basename(destino)); continue
        for intento in (1, 2):
            try:
                h = {"Authorization": "Bearer %s" % ACCESS_TOKEN}
                with requests.get(asset.href, headers=h, stream=True, timeout=600) as r:
                    if r.status_code == 401 and intento == 1:
                        ACCESS_TOKEN = obtener_access_token(); continue
                    r.raise_for_status()
                    with open(destino, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            f.write(chunk)
                print("      OK ->", os.path.basename(destino)); break
            except Exception as e:
                if intento == 2:
                    print("      ERROR", nombre_asset, ":", str(e)[:70])


def main():
    print(__doc__)
    catalogo = Client.open(CATALOG_URL)
    print("Conectado al catalogo STAC de ESA MAAP\n")
    for aoi in AOIS_WGS84:
        bbox = list(AOIS_WGS84[aoi])
        print("=" * 72)
        print("AOI: %s  bbox=%s" % (aoi, [round(v, 4) for v in bbox]))
        print("=" * 72)
        for col in COLECCIONES:
            try:
                s = catalogo.search(collections=[col], bbox=bbox,
                                    datetime=[FECHA_INICIO, FECHA_FIN], max_items=300)
                items = list(s.items())
                if SOLO_1S:
                    items = [it for it in items if es_1S(it)]
                print("   %s: %d producto(s) 1S" % (col, len(items)))
                if ACCESS_TOKEN:
                    sel = items if MAX_POR_AOI is None else items[:MAX_POR_AOI]
                    for it in sel:
                        print("     descargando %s ..." % it.id)
                        descargar_item(it, carpeta_de(it, aoi, col))
            except Exception as e:
                print("   %s: ERROR %s" % (col, str(e)[:70]))
        print()
    print("Listo. Productos BIOMASS en 08_Originales_crudos/<epoca>/BIOMASS/")
    print("SIGUIENTE PASO:  python TP1_09_inventario.py")


if __name__ == "__main__":
    main()
