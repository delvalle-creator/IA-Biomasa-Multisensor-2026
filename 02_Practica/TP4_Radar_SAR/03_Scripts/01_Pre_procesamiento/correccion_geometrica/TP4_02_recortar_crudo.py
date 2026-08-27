#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_02_recortar_crudo.py   ---> SEGUNDO script del TP4 (OPCIONAL).   (OPCIONAL: solo si va a hacer InSAR o polarimetria)

Recorta los productos SLC al AOI CONSERVANDO LA GEOMETRIA DE RADAR Y LA FASE
COMPLEJA. Es un producto distinto del que genera el script 04:

  TP4_01_procesar_sar.py  -> gamma0 GEOCODIFICADO en la grilla comun.
                         Sirve para radiometria y para comparar sensores.
                         PIERDE la fase: no sirve para interferometria.

  TP4_02_recortar_crudo.py -> SLC recortado, en geometria de radar, CON la fase
                         (bandas i y q). Sirve para InSAR y polarimetria.
                         NO esta geocodificado: no se apila con los demas.

Por que no se puede recortar el SAR sin procesarlo a la grilla comun: el AOI
esta definido en coordenadas cartograficas (UTM 19S), y un producto SAR crudo
esta en geometria de radar (rango-azimut). No hay correspondencia entre un pixel
y una esquina del AOI hasta que no se geocodifica, y geocodificar es procesar.
Por eso el recorte crudo se hace en la geometria propia del radar.

Sentinel-1 IW SLC: TOPSAR-Split selecciona la subfranja que cubre el AOI y solo
las rafagas necesarias. De 7,8 GB se baja a unos cientos de MB.
SAOCOM L1A: se recorta con Subset (si la geocodificacion aproximada lo permite).
Sentinel-1 GRD y Sentinel-2 no se incluyen: el GRD ya perdio la fase en origen y
el optico ya viene geocodificado.

REQUISITOS: SNAP ('gpt' en el PATH o editar GPT) y el entorno conda 'aoi'.
USO:  python TP4_02_recortar_crudo.py
"""
import glob
import os
import re
import subprocess
import sys
import time
import zipfile
import xml.etree.ElementTree as ET


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

from aoi_config import AOIS_WGS84, DESCARGAS, CRUDOS, EPOCAS
import nombres

GPT = "gpt"                       # o la ruta completa a gpt.exe
MEM_GPT = ["-c", "4G", "-q", "4"]
GRAFOS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "08_Grafos_SNAP")
BUFFER = 0.02                     # margen en grados (~2 km)



def wkt(aoi, buffer_grados=BUFFER):
    lonmin, latmin, lonmax, latmax = AOIS_WGS84[aoi]
    b = buffer_grados
    lonmin, latmin, lonmax, latmax = (lonmin - b, latmin - b,
                                      lonmax + b, latmax + b)
    return ("POLYGON((%f %f,%f %f,%f %f,%f %f,%f %f))"
            % (lonmin, latmin, lonmax, latmin, lonmax, latmax,
               lonmin, latmax, lonmin, latmin))


def hay_gpt():
    try:
        subprocess.run([GPT, "-h"], capture_output=True, timeout=180)
        return True
    except Exception:
        return False


def subswath_del_aoi(zip_slc, aoi):
    """Determina cual subfranja (IW1, IW2, IW3) cubre el AOI.

    Se leen las anotaciones del .SAFE: cada subfranja trae una grilla de puntos
    de geolocalizacion, de la que se toma la envolvente.

    ATENCION: las subfranjas se SOLAPAN entre si, de modo que el centro del AOI
    puede caer dentro de dos de ellas a la vez. Elegir la primera que contenga
    el centro es, por lo tanto, un error: podria devolver una subfranja que
    cubra el AOI solo parcialmente. Se exige que la envolvente contenga el AOI
    COMPLETO; si ninguna lo hace, se toma la de mayor solapamiento y se avisa.
    """
    lonmin, latmin, lonmax, latmax = AOIS_WGS84[aoi]
    completas, mejor, mejor_area = [], None, 0.0
    with zipfile.ZipFile(zip_slc) as z:
        anot = [n for n in z.namelist()
                if "/annotation/" in n and n.endswith(".xml")
                and "-vv-" in n.lower() and "calibration" not in n]
        for n in anot:
            m = re.search(r"-(iw[123])-", os.path.basename(n).lower())
            if not m:
                continue
            swath = m.group(1).upper()
            raiz = ET.fromstring(z.read(n))
            lats = [float(p.findtext("latitude"))
                    for p in raiz.iter("geolocationGridPoint")]
            lons = [float(p.findtext("longitude"))
                    for p in raiz.iter("geolocationGridPoint")]
            if not lats:
                continue
            s_lonmin, s_lonmax = min(lons), max(lons)
            s_latmin, s_latmax = min(lats), max(lats)
            ancho = max(0.0, min(s_lonmax, lonmax) - max(s_lonmin, lonmin))
            alto = max(0.0, min(s_latmax, latmax) - max(s_latmin, latmin))
            area = ancho * alto
            if (s_lonmin <= lonmin and s_lonmax >= lonmax
                    and s_latmin <= latmin and s_latmax >= latmax):
                completas.append((area, swath))
            if area > mejor_area:
                mejor, mejor_area = swath, area
    if completas:
        # si mas de una contiene el AOI entero, la de envolvente mas ajustada
        completas.sort()
        return completas[0][1]
    if mejor:
        print("   AVISO: ninguna subfranja contiene el AOI completo; se usa %s "
              "(la de mayor solapamiento). Revise el resultado." % mejor)
    return mejor


def tamano(carpeta_dim):
    data = carpeta_dim[:-4] + ".data"
    total = sum(os.path.getsize(os.path.join(d, f))
                for d, _, fs in os.walk(data) for f in fs)
    return total / 1e9


print(__doc__)
if not hay_gpt():
    sys.exit("No se encontro '%s'. Instalar SNAP o editar la variable GPT." % GPT)

hechos, fallidos = 0, 0
FILTRO_EPOCA = sys.argv[1] if len(sys.argv) > 1 else ""
for epoca in EPOCAS:
  if FILTRO_EPOCA and FILTRO_EPOCA not in epoca:
    continue
  for aoi in AOIS_WGS84:
    # ---------------- Sentinel-1 SLC ----------------
    slcs = sorted(glob.glob(os.path.join(DESCARGAS, epoca, aoi, "S1_SLC", "*.zip")))
    if slcs:
        print("\n=== %s | S1_SLC: %d productos ===" % (aoi, len(slcs)), flush=True)
    for z in slcs:
        original = os.path.basename(z)[:-4]
        corto, fecha = nombres.corto_sentinel1(original)
        outdir = os.path.join(CRUDOS, epoca, aoi, "S1_SLC")
        os.makedirs(outdir, exist_ok=True)
        dim = os.path.join(outdir, corto + "_crudo.dim")
        print(" ", corto, flush=True)
        if os.path.exists(dim):
            print("   ya existe, se omite")
            continue
        sw = subswath_del_aoi(z, aoi)
        if not sw:
            print("   ERROR: no se pudo determinar la subfranja")
            fallidos += 1
            continue
        print("   subfranja %s | TOPSAR-Split + orbita precisa..." % sw, flush=True)
        t0 = time.time()
        r = subprocess.run(
            [GPT, os.path.join(GRAFOS, "graph_s1_slc_crudo_cli.xml")] + MEM_GPT
            + ["-Pentrada=" + z, "-Psalida=" + dim,
               "-Psubswath=" + sw, "-Pgeowkt=" + wkt(aoi)],
            capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(dim):
            print("   ERROR en gpt:")
            print("   " + (r.stderr or r.stdout or "")[-500:].replace("\n", "\n   "))
            fallidos += 1
            continue
        orig_gb = os.path.getsize(z) / 1e9
        print("   OK (%.1f min) %.2f GB -> %.2f GB  (%.0f%% del original)"
              % ((time.time() - t0) / 60, orig_gb, tamano(dim),
                 100 * tamano(dim) / orig_gb), flush=True)
        nombres.registrar(CRUDOS, [corto + "_crudo", aoi, "S1_SLC_crudo",
                                   fecha, original, os.path.basename(z)])
        hechos += 1

    # ---------------- SAOCOM L1A ----------------
    xemts = sorted(glob.glob(os.path.join(DESCARGAS, epoca, "SAOCOM", "*", "*.xemt")))
    if xemts:
        print("\n=== %s | SAOCOM_L1A: %d productos ===" % (aoi, len(xemts)),
              flush=True)
    for x in xemts:
        original = os.path.basename(os.path.dirname(x))
        txt = open(x, encoding="utf-8", errors="ignore").read()
        m = re.search(r"<startTime>(\d{4})-(\d{2})-(\d{2})", txt)
        fecha = "".join(m.groups()) if m else "00000000"
        corto, _ = nombres.corto_saocom(original, fecha)
        outdir = os.path.join(CRUDOS, epoca, aoi, "SAOCOM_L1A")
        os.makedirs(outdir, exist_ok=True)
        dim = os.path.join(outdir, corto + "_crudo.dim")
        print(" ", corto, flush=True)
        if os.path.exists(dim):
            print("   ya existe, se omite")
            continue
        t0 = time.time()
        r = subprocess.run(
            [GPT, os.path.join(GRAFOS, "graph_saocom_crudo_cli.xml")] + MEM_GPT
            + ["-Pentrada=" + x, "-Psalida=" + dim, "-Pgeowkt=" + wkt(aoi)],
            capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(dim):
            print("   ERROR en gpt:")
            print("   " + (r.stderr or r.stdout or "")[-500:].replace("\n", "\n   "))
            fallidos += 1
            continue
        print("   OK (%.1f min) -> %.2f GB" % ((time.time() - t0) / 60,
                                               tamano(dim)), flush=True)
        nombres.registrar(CRUDOS, [corto + "_crudo", aoi, "SAOCOM_L1A_crudo",
                                   fecha, original, os.path.basename(x)])
        hechos += 1

print("\nListo. %d recortes crudos, %d con error." % (hechos, fallidos))
print("Estan en 05_recortes_crudos/<AOI>/<sensor>/  (geometria de radar, CON "
      "fase: para InSAR y polarimetria).")
print("Los productos geocodificados en la grilla comun estan en "
      "04_Tablas_de_trabajo/ (gamma0, SIN fase).")
