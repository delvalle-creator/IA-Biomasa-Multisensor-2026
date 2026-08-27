#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_descargar_sentinel.py
Descarga desde Copernicus Data Space (CDSE) los productos Sentinel-1 y
Sentinel-2 listados en lista_descargas_sentinel.csv (mismos nombres que el
manifiesto XLSX).

USO:
  python 01_descargar_sentinel.py                     (pre/post incendio)
  python 01_descargar_sentinel.py --linea-base       (linea de base 2023-24)
  python 01_descargar_sentinel.py --solo-principal   (omite alternativas)

Cada producto se guarda en la carpeta de su epoca, que se deduce de su fecha.

Pide usuario y contrasena de dataspace.copernicus.eu. Todo queda en
./descargas/<AOI>/<sensor>/. Si se corta, volver a ejecutar: los archivos
completos no se repiten.
"""
import csv
import getpass
import re
import os
import sys
import time
import urllib.parse

try:
    import requests
except ImportError:
    sys.exit("Falta el paquete 'requests'. Ejecutar:  pip install requests")


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

from aoi_config import DESCARGAS, SCRIPTS

# Lista a descargar segun la epoca:
#   (por defecto)   lista_descargas_sentinel.csv     -> pre/post incendio 2025-26
#   --linea-base    lista_descargas_linea_base.csv   -> linea de base 2023-24
if "--linea-base" in sys.argv:
    LISTA = os.path.join(SCRIPTS, "lista_descargas_linea_base.csv")
    EPOCA = "01_base"
else:
    LISTA = os.path.join(SCRIPTS, "lista_descargas_sentinel.csv")
    EPOCA = None      # se deduce de la fecha de cada producto
DESTINO = DESCARGAS
CATALOGO = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
TOKEN_URL = ("https://identity.dataspace.copernicus.eu/auth/realms/CDSE"
             "/protocol/openid-connect/token")
SOLO_PRINCIPAL = "--solo-principal" in sys.argv


def fmt_tiempo(seg):
    seg = int(seg)
    if seg >= 3600:
        return f"{seg//3600}h{(seg%3600)//60:02d}m"
    return f"{seg//60:02d}m{seg%60:02d}s"


def barra(frac, ancho=20):
    n = int(frac * ancho)
    return "#" * n + "-" * (ancho - n)


def obtener_token():
    r = requests.post(TOKEN_URL, data={
        "client_id": "cdse-public", "grant_type": "password",
        "username": USUARIO, "password": CLAVE}, timeout=60)
    if r.status_code == 200:
        return r.json()["access_token"]

    # --- diagnostico detallado: el servidor dice POR QUE rechaza ---
    try:
        j = r.json()
        error = j.get("error", "")
        detalle = j.get("error_description", "")
    except Exception:
        error, detalle = "", r.text[:200]

    print("\n" + "=" * 70)
    print("ERROR DE AUTENTICACION EN COPERNICUS (HTTP %d)" % r.status_code)
    print("=" * 70)
    print("  respuesta del servidor: %s | %s" % (error, detalle))
    print()
    if error == "invalid_grant":
        print("  Significa que el usuario o la contrasena no son correctos.")
        print("  Cosas para revisar, en este orden:")
        print("   1. El USUARIO es su EMAIL completo (no un alias).")
        print("   2. La contrasena se escribe A CIEGAS: no se ve nada al teclear,")
        print("      ni siquiera asteriscos. Escribala completa y pulse Enter.")
        print("      Si la PEGA con Ctrl+V, en algunas consolas no funciona:")
        print("      use el boton derecho del raton para pegar.")
        print("   3. Compruebe que puede entrar en https://dataspace.copernicus.eu")
        print("      con esas mismas credenciales, desde el navegador.")
        print("   4. Si cambio la contrasena hace poco, use la nueva.")
        print("   5. Si tiene el teclado en otra distribucion, cuidado con los")
        print("      caracteres especiales (@ # ! etc.).")
    elif r.status_code == 401:
        print("  Credenciales rechazadas. Verifique usuario y contrasena.")
    elif r.status_code == 400:
        print("  Peticion mal formada o cuenta no habilitada.")
    else:
        print("  Puede ser un problema temporal del servidor: reintente en unos")
        print("  minutos. Estado del servicio: https://dataspace.copernicus.eu")
    print("=" * 70)
    sys.exit(1)


def buscar_id(nombre):
    """Localiza el producto en el catalogo de Copernicus.

    ATENCION: no se busca por nombre exacto. Copernicus REPROCESA su archivo
    historico (las llamadas 'colecciones'), y al hacerlo cambia la linea base de
    procesamiento que figura en el nombre: un producto que en 2024 se llamaba
    ...N0510... hoy puede llamarse ...N0511... y el nombre antiguo ya no existe.
    Buscar por nombre exacto funciona con productos recientes y falla con los
    historicos, con un desconcertante 'no encontrado'.

    Se busca, en cambio, por los datos que NO cambian nunca: la fecha y la hora
    exactas de la adquisicion, y el tile (Sentinel-2) o el identificador unico
    del producto (Sentinel-1).
    """
    # 1) intento directo por nombre (rapido, sirve para productos recientes)
    for n in (nombre, nombre + ".SAFE", nombre.replace(".SAFE", "")):
        url = CATALOGO + "?" + urllib.parse.urlencode(
            {"$filter": "Name eq '%s'" % n, "$top": "1"})
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and r.json().get("value"):
            v = r.json()["value"][0]
            return v["Id"], v.get("ContentLength", 0), v["Name"]

    # 2) busqueda por atributos invariantes
    p = nombre.split("_")
    if nombre.startswith("S2"):
        # S2A_MSIL2A_20240110T142711_N0510_R053_T18GYT_...
        instante = p[2]                       # 20240110T142711
        tile = next((x for x in p if x.startswith("T") and len(x) == 6), "")
        # IMPRESCINDIBLE incluir el NIVEL (MSIL2A / MSIL1C): en la misma fecha y
        # el mismo tile conviven el L1C y el L2A. Si no se filtra por nivel, el
        # catalogo puede devolver primero el L1C y se descarga el producto
        # equivocado (sin correccion atmosferica ni banda SCL).
        nivel = p[1]                          # MSIL2A
        claves = [nivel, instante, tile]
        coleccion = "SENTINEL-2"
    else:
        # S1A_IW_SLC__1SDV_20231017T234232_..._050811_061FC5_C2DB
        # Aqui tambien conviven GRDH y SLC de la misma pasada: se filtra por tipo.
        instante = next(x for x in p if len(x) == 15 and x[8] == "T")
        tipo = p[2]                           # GRDH o SLC
        claves = [tipo, instante, p[-1]]      # tipo + instante + identificador
        coleccion = "SENTINEL-1"

    condiciones = ["Collection/Name eq '%s'" % coleccion]
    condiciones += ["contains(Name,'%s')" % c for c in claves if c]
    url = CATALOGO + "?" + urllib.parse.urlencode(
        {"$filter": " and ".join(condiciones), "$top": "5"})
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        return None, 0, ""
    v = r.json().get("value", [])
    # red de seguridad: descartar cualquier candidato que no lleve TODAS las
    # claves (nivel/tipo, instante, tile/identificador) en el nombre.
    v = [x for x in v if all(c in x["Name"] for c in claves if c)]
    if not v:
        return None, 0, ""
    if v[0]["Name"] != nombre and v[0]["Name"] != nombre + ".SAFE":
        print("   (reprocesado: ahora se llama %s)" % v[0]["Name"][:58])
    return v[0]["Id"], v[0].get("ContentLength", 0), v[0]["Name"]


def esta_en_linea(pid):
    """Los productos antiguos pueden estar en el archivo historico (offline).

    En ese caso hay que SOLICITARLOS: Copernicus los devuelve al disco en unos
    minutos u horas, y recien entonces pueden descargarse. Sin este control, la
    descarga falla con un error incomprensible.
    """
    url = CATALOGO + "(%s)?$select=Online" % pid
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        return True                     # ante la duda, se intenta descargar
    return bool(r.json().get("Online", True))


def solicitar_del_archivo(pid, nombre):
    """Pide a Copernicus que restaure un producto archivado."""
    url = ("https://download.dataspace.copernicus.eu/odata/v1/Products(%s)/OData."
           "CSC.Order" % pid)
    r = requests.post(url, headers={"Authorization": "Bearer %s" % TOKEN},
                      timeout=60)
    if r.status_code in (200, 201, 202):
        print("   SOLICITADO al archivo historico. Copernicus lo restaura en un")
        print("   plazo de minutos a horas. Vuelva a ejecutar el script mas tarde.")
    else:
        print("   no se pudo solicitar (HTTP %d): %s" % (r.status_code, r.text[:120]))


def descargar(pid, destino, tamano, etiqueta, global_hecho, global_total):
    """Descarga con barra de progreso. Devuelve bytes bajados o -1 si fallo."""
    global TOKEN
    url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({pid})/$value"
    for intento in range(4):
        r = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"},
                         stream=True, timeout=120)
        if r.status_code == 401:          # el token dura ~10 minutos
            TOKEN = obtener_token()
            continue
        if r.status_code != 200:
            print(f"\n   HTTP {r.status_code}, reintento {intento+1}/4")
            time.sleep(10)
            continue
        parcial = destino + ".parcial"
        bajado, t0, t_ult = 0, time.time(), 0.0
        with open(parcial, "wb") as f:
            for bloque in r.iter_content(chunk_size=4 * 1024 * 1024):
                f.write(bloque)
                bajado += len(bloque)
                ahora = time.time()
                if ahora - t_ult > 0.5 and tamano:   # refrescar cada 0.5 s
                    t_ult = ahora
                    vel = bajado / max(ahora - t0, 0.1)     # bytes/s
                    eta = (tamano - bajado) / max(vel, 1)
                    frac = bajado / tamano
                    tot = (global_hecho + bajado) / 1e9
                    print(f"\r{etiqueta} [{barra(frac)}] {100*frac:3.0f}%  "
                          f"{bajado/1e9:5.2f}/{tamano/1e9:.2f} GB  "
                          f"{vel/1e6:5.1f} MB/s  ETA {fmt_tiempo(eta)}  "
                          f"| TOTAL {tot:.1f}/{global_total/1e9:.1f} GB   ",
                          end="", flush=True)
        print()
        os.rename(parcial, destino)
        return bajado
    print("\n   ERROR: no se pudo descargar")
    return -1


print(__doc__)
USUARIO = input("Usuario CDSE (email): ").strip()
CLAVE = getpass.getpass("Contrasena CDSE: ")
TOKEN = obtener_token()
print("Autenticacion OK.\n")

with open(LISTA, newline="", encoding="utf-8") as f:
    filas = [x for x in csv.DictReader(f)
             if not (SOLO_PRINCIPAL and x["prioridad"] != "PRINCIPAL")]

# --- 1) Consultar el catalogo y armar el plan de descarga ---
print(f"Consultando catalogo ({len(filas)} productos)...")
plan, ya_listos, errores, archivados = [], 0, [], []
total_bytes = 0
from aoi_config import epoca_de
for fila in filas:
    nombre = fila["producto"]
    fe = re.search(r"(20\d{2})(\d{2})(\d{2})T", nombre)
    ep = EPOCA or epoca_de("".join(fe.groups()) if fe else "20260101")
    destino_dir = os.path.join(DESTINO, ep, fila["aoi"], fila["sensor"])
    destino = os.path.join(destino_dir, nombre.replace(".SAFE", "") + ".zip")
    if os.path.exists(destino):
        ya_listos += 1
        continue
    print("  buscando %s ..." % nombre[:52], flush=True)
    pid, tam, nombre_real = buscar_id(nombre)
    if not pid:
        print("   NO ENCONTRADO en el catalogo de Copernicus")
        errores.append(nombre)
        continue
    # El .zip debe llamarse EXACTAMENTE como el .SAFE que lleva dentro. Si el
    # producto fue reprocesado, el nombre de la lista es el viejo y el del
    # catalogo es el nuevo: si se guarda con el viejo, el lector de Sentinel-2
    # de SNAP no encuentra el tile dentro del zip y falla al leerlo.
    destino = os.path.join(destino_dir,
                           nombre_real.replace(".SAFE", "") + ".zip")
    if os.path.exists(destino):
        ya_listos += 1
        continue
    if not esta_en_linea(pid):
        print("   ARCHIVADO (no esta en linea): se solicita su restauracion")
        solicitar_del_archivo(pid, nombre)
        archivados.append(nombre)
        continue
    os.makedirs(destino_dir, exist_ok=True)
    plan.append((fila, pid, tam, destino))
    total_bytes += tam

print(f"\nPlan: {len(plan)} por descargar ({total_bytes/1e9:.1f} GB) | "
      f"{ya_listos} ya completos | {len(archivados)} archivados | "
      f"{len(errores)} no encontrados\n")

# --- 2) Descargar con progreso ---
hecho_bytes = 0
t_inicio = time.time()
for i, (fila, pid, tam, destino) in enumerate(plan, 1):
    print(f"[{i}/{len(plan)}] {fila['aoi']} | {fila['sensor']} | "
          f"{fila['fecha_objetivo']} | {fila['prioridad']}")
    print(f"      {fila['producto']}")
    n = descargar(pid, destino, tam, "      ", hecho_bytes, total_bytes)
    if n < 0:
        errores.append(fila["producto"])
    else:
        hecho_bytes += n

print(f"\n=== FIN ===  {hecho_bytes/1e9:.1f} GB en {fmt_tiempo(time.time()-t_inicio)}")
if archivados:
    print("\n%d producto(s) estaban ARCHIVADOS y ya se solicitaron a Copernicus."
          % len(archivados))
    print("La restauracion tarda de unos minutos a algunas horas. Vuelva a")
    print("ejecutar este mismo script mas tarde y se descargaran solos.")
    for a in archivados:
        print("   -", a[:62])
if errores:
    print("Con errores (volver a ejecutar el script para reintentar):")
    for e in errores:
        print(" -", e)
else:
    print("Todas las descargas completas.")
