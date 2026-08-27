#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_01_procesar_sar.py   ---> PRIMER script del TP4.
Procesa con SNAP (gpt) los productos SAR y los recorta a la grilla comun de
15 x 15 km (EPSG:32719, 10 m, 1500 x 1500 px).

Cadena (los grafos estan en ../ , junto a este script):
  orbita precisa -> [ruido termico, solo GRD] -> calibracion a beta0 ->
  recorte al AOI + buffer -> [deburst / multilook] -> TERRAIN FLATTENING (gamma0)
  -> correccion de terreno (DEM Copernicus GLO-30, grilla alineada) ->
  recorte exacto al AOI -> BEAM-DIMAP

SALIDA, en ../04_Tablas_de_trabajo/<AOI>/<sensor>/:
  *_gamma0_subset15km.dim + .data   PRODUCTO PRINCIPAL (formato nativo de SNAP).
                                    Conserva TODOS los metadatos: puede seguir
                                    procesandose en SNAP (polarimetria, filtros,
                                    descomposiciones, apilado).
  *_gamma0_subset15km.tif           copia GeoTIFF, solo para verlo en QGIS.
                                    NO usar como entrada de SNAP: pierde los
                                    metadatos.

El SLC / L1A original queda intacto en 00_COMUN/08_Originales_crudos/
para InSAR o PolSAR.

REQUISITOS: SNAP instalado ('gpt' en el PATH, o editar GPT mas abajo).
USO:  python TP4_01_procesar_sar.py                       (todo)
      python TP4_01_procesar_sar.py S1_GRD                (solo un sensor)
      python TP4_01_procesar_sar.py pre_incendio          (solo una epoca)
      python TP4_01_procesar_sar.py S1_SLC linea_base     (sensor + epoca)
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

try:
    from osgeo import gdal
except ImportError:
    sys.exit("Falta GDAL. Ejecutar: conda activate aoi")


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

from aoi_config import (AOIS_UTM, AOIS_WGS84, EPSG, PIXEL,
                        DESCARGAS, PROCESADOS, GRAFOS, EPOCAS,
                        dir_procesado)
import nombres

gdal.UseExceptions()

# Si 'gpt' no esta en el PATH, poner aqui la ruta completa. Ejemplos:
#   Windows: r"C:\Program Files\esa-snap\bin\gpt.exe"
#   Linux:   "/opt/esa-snap/bin/gpt"
GPT = "gpt"

BUFFER_GRADOS = 0.05                 # margen para el Terrain Flattening
UNIR_FRAMES = True                   # SLC: unir el frame contiguo (SliceAssembly)
                                     # cuando un solo frame no cubre el AOI
MEM_GPT = ["-c", "4G", "-q", "4"]    # cache y nucleos que usa SNAP

TRABAJOS = [   # (subcarpeta, grafo, patron de archivos)
    ("S1_GRD", "graph_s1_grd_tc_cli.xml", "*.zip"),
    ("S1_SLC", "graph_s1_slc_tc_cli.xml", "*.zip"),
    ("SAOCOM_L1A", "graph_saocom_tc_cli.xml", "*.xemt"),
]

# Los productos SAOCOM cubren los DOS AOI en una sola adquisicion: se guardan en
# una carpeta unica y se procesan una vez por cada AOI. SNAP abre el producto a
# traves de su archivo .xemt.
# SAOCOM: un mismo producto sirve a los dos AOI; vive en <epoca>/SAOCOM/
# argumentos: sensor (S1_GRD, S1_SLC, SAOCOM_L1A) y/o epoca (texto parcial)
ARGS = sys.argv[1:]
FILTRO = next((a for a in ARGS if a.upper() in
               ("S1_GRD", "S1_SLC", "SAOCOM_L1A")), "")
FILTRO_EPOCA = next((a for a in ARGS if a not in (FILTRO,)), "")


def wkt(aoi, buffer_grados=0.0):
    """AOI en WGS84 como POLYGON, con margen opcional."""
    lonmin, latmin, lonmax, latmax = AOIS_WGS84[aoi]
    b = buffer_grados
    lonmin, latmin = lonmin - b, latmin - b
    lonmax, latmax = lonmax + b, latmax + b
    return ("POLYGON((%f %f,%f %f,%f %f,%f %f,%f %f))"
            % (lonmin, latmin, lonmax, latmin, lonmax, latmax,
               lonmin, latmax, lonmin, latmin))


def hay_gpt():
    try:
        subprocess.run([GPT, "-h"], capture_output=True, timeout=180)
        return True
    except Exception:
        return False


def bandas_del_dim(dim):
    """Nombres de las bandas y rutas .img, en el orden del producto.

    Se exige que exista tambien el .hdr: GDAL lo necesita para leer el .img, y
    su ausencia delata un producto escrito a medias (por ejemplo, si se
    interrumpio SNAP). En ese caso conviene abortar y no generar una copia
    GeoTIFF invalida.
    """
    raiz = ET.parse(dim).getroot()
    carpeta = dim[:-4] + ".data"
    bandas, incompletas = [], []
    for b in raiz.findall(".//Spectral_Band_Info"):
        nombre = b.find("BAND_NAME").text
        img = os.path.join(carpeta, nombre + ".img")
        hdr = os.path.join(carpeta, nombre + ".hdr")
        if os.path.exists(img) and os.path.exists(hdr):
            bandas.append((nombre, img))
        elif os.path.exists(img):
            incompletas.append(nombre)
    if incompletas:
        print("   AVISO: faltan las cabeceras .hdr de %s: el producto quedo "
              "escrito a medias (\u00bfse interrumpio SNAP?). Borrelo y vuelva "
              "a ejecutar." % ", ".join(incompletas))
    return bandas


def copia_geotiff(dim, destino_tif):
    """Copia GeoTIFF (solo para QGIS) a partir del BEAM-DIMAP."""
    bandas = bandas_del_dim(dim)
    if not bandas:
        print("   aviso: no se pudo generar la copia GeoTIFF")
        return
    vrt = gdal.BuildVRT("", [img for _, img in bandas], separate=True)
    gdal.Translate(destino_tif + ".tmp", vrt, format="GTiff",
                   creationOptions=["COMPRESS=DEFLATE", "TILED=YES"])
    os.replace(destino_tif + ".tmp", destino_tif)
    ds = gdal.Open(destino_tif, gdal.GA_Update)
    for i, (nombre, _) in enumerate(bandas, 1):
        ds.GetRasterBand(i).SetDescription(nombre)
    ds = None


def verificar_grilla(dim, aoi):
    """Comprueba que el producto quedo en la grilla comun."""
    bandas = bandas_del_dim(dim)
    if not bandas:
        return "sin bandas"
    ds = gdal.Open(bandas[0][1])
    gt = ds.GetGeoTransform()
    x0, y0 = gt[0], gt[3]
    ancho, alto = ds.RasterXSize, ds.RasterYSize
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    ok = (abs(x0 - xmin) < 0.01 and abs(y0 - ymax) < 0.01
          and ancho == 1500 and alto == 1500)
    return ("grilla OK (%d x %d px)" % (ancho, alto) if ok else
            "REVISAR: %d x %d px, origen E %.0f N %.0f (esperado E %d N %d)"
            % (ancho, alto, x0, y0, xmin, ymax))


def fecha_saocom(xemt):
    """Fecha de adquisicion (AAAAMMDD) leida del .xemt de SAOCOM."""
    txt = open(xemt, encoding="utf-8", errors="ignore").read()
    m = re.search(r"<startTime>(\d{4})-(\d{2})-(\d{2})", txt)
    return "".join(m.groups()) if m else "00000000"


def borrar_producto(dim):
    """Elimina un producto BEAM-DIMAP (.dim y su carpeta .data)."""
    data = dim[:-4] + ".data"
    if os.path.isdir(data):
        shutil.rmtree(data, ignore_errors=True)
    if os.path.exists(dim):
        os.remove(dim)


def origen_utm(dim):
    """Esquina superior izquierda (borde) y tamano del producto geocodificado.

    Se lee de la cabecera ENVI de la primera banda. En ENVI, 'map info' da la
    coordenada de la esquina superior izquierda del pixel de referencia, con
    indices que empiezan en 1.
    """
    data = dim[:-4] + ".data"
    hdrs = sorted(glob.glob(os.path.join(data, "*.hdr")))
    if not hdrs:
        return None
    txt = open(hdrs[0], encoding="utf-8", errors="ignore").read()
    m = re.search(r"map info\s*=\s*\{[^,]+,\s*([\d.]+)\s*,\s*([\d.]+)\s*,"
                  r"\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)", txt)
    if not m:
        return None
    refx, refy, este, norte, dx, dy = (float(g) for g in m.groups())
    x0 = este - (refx - 1) * dx          # borde izquierdo de la imagen
    y0 = norte + (refy - 1) * dy         # borde superior de la imagen
    ancho = int(re.search(r"samples\s*=\s*(\d+)", txt).group(1))
    alto = int(re.search(r"lines\s*=\s*(\d+)", txt).group(1))
    return x0, y0, dx, dy, ancho, alto


def recorte_exacto(dim_temp, dim_final, aoi):
    """Recorta a la grilla comun por REGION DE PIXELES, dentro de SNAP.

    No se usa geoRegion: un rectangulo en latitud/longitud no es un rectangulo
    en UTM, de modo que SNAP tomaria su caja envolvente y el resultado seria
    mayor que el AOI (salian 1591 px en lugar de 1500).
    """
    geo = origen_utm(dim_temp)
    if not geo:
        print("   ERROR: no se pudo leer la geocodificacion del producto")
        return False
    x0, y0, dx, dy, ancho, alto = geo
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    px = int(round((xmin - x0) / dx))
    py = int(round((y0 - ymax) / dy))
    nx = int(round((xmax - xmin) / dx))     # 1500
    ny = int(round((ymax - ymin) / dy))     # 1500
    if px < 0 or py < 0 or px + nx > ancho or py + ny > alto:
        print("   ERROR: el AOI se sale del producto (px=%d py=%d de %dx%d)"
              % (px, py, ancho, alto))
        return False
    r = subprocess.run(
        [GPT, "Subset"] + MEM_GPT
        + ["-Ssource=" + dim_temp,
           "-PcopyMetadata=true",
           "-Pregion=%d,%d,%d,%d" % (px, py, nx, ny),
           "-f", "BEAM-DIMAP", "-t", dim_final],
        capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dim_final):
        print("   ERROR en el recorte:")
        print("   " + (r.stderr or r.stdout or "")[-500:].replace("\n", "\n   "))
        return False
    return True


def frame_hermano(entrada, aoi, epoca):
    """Devuelve el frame CONTIGUO de la misma orbita y fecha, si existe.

    Los frames SLC de Sentinel-1 se solapan poco, y el borde de uno puede cortar
    el AOI: en la estepa, el frame propio dejaba sin datos el 21 % del sitio por
    el norte. La solucion es unir los dos frames contiguos de la misma pasada con
    el operador SliceAssembly de SNAP antes de procesar.

    El frame del OTRO AOI pertenece a la misma orbita y a la misma fecha (es el
    tramo siguiente de la misma pasada), de modo que sirve como hermano.
    """
    nombre = os.path.basename(entrada)
    p = nombre.split("_")
    orbita = p[-3]                      # orbita absoluta: identifica la pasada
    otros = [a for a in AOIS_UTM if a != aoi]
    for otro in otros:
        for cand in glob.glob(os.path.join(DESCARGAS, epoca, otro,
                                              "S1_SLC", "*.zip")):
            if os.path.basename(cand).split("_")[-3] == orbita:
                return cand
    return None


def procesar(entrada, grafo, aoi, etiqueta, epoca):
    # Nombre CORTO para la salida: Windows limita la ruta a 260 caracteres y el
    # nombre original, sumado a la carpeta .data (un archivo por banda), agota
    # ese limite. El producto original NO se renombra: queda intacto en
    # 08_Originales_crudos/ y la equivalencia se anota en diccionario_nombres.csv
    archivo = os.path.basename(entrada)
    if archivo.endswith(".xemt"):
        original = os.path.basename(os.path.dirname(entrada))
        corto, fecha = nombres.corto_saocom(original, fecha_saocom(entrada))
    else:
        original = archivo[:-4]
        corto, fecha = nombres.corto_sentinel1(original)

    # dir_procesado() resuelve el nivel <grupo> (Sentinel_1, SAOCOM, NISAR...).
    # Armar la ruta a mano se saltea ese nivel y crea un arbol paralelo que los
    # scripts de analisis (06, 07, 08) nunca miran: se procesaria todo y los
    # resultados no cambiarian, sin ningun error visible.
    outdir = dir_procesado(etiqueta, epoca, aoi)
    os.makedirs(outdir, exist_ok=True)
    base = os.path.join(outdir, corto)
    dim, tif = base + ".dim", base + ".tif"
    if os.path.exists(dim):
        print("   ya existe, se omite")
        return True

    t0 = time.time()
    temp = base + "_tmp.dim"

    # ETAPA 1: cadena SAR completa (recorte con margen -> gamma0 -> geocodificado
    # sobre una grilla alineada a los bordes de 10 m)
    print("   SNAP (1/2): orbita, beta0, Terrain Flattening, geocodificacion...",
          flush=True)
    params = ["-Pentrada=" + entrada,
              "-Psalida=" + temp,
              "-Pgeowkt=" + wkt(aoi, BUFFER_GRADOS)]
    grafo_usado = grafo
    if etiqueta == "S1_SLC" and UNIR_FRAMES:
        hermano = frame_hermano(entrada, aoi, epoca)
        if hermano:
            grafo_usado = "graph_s1_slc_tc_2frames_cli.xml"
            params.append("-Pentrada2=" + hermano)
            print("   SliceAssembly: se une el frame contiguo %s"
                  % os.path.basename(hermano)[:32], flush=True)
    cmd = ([GPT, os.path.join(GRAFOS, grafo_usado)] + MEM_GPT + params)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(temp):
        print("   ERROR en gpt:")
        print("   " + (r.stderr or r.stdout or "")[-700:].replace("\n", "\n   "))
        return False

    # ETAPA 2: recorte exacto a la grilla comun, por region de pixeles
    print("   SNAP (2/2): recorte exacto a 1500 x 1500 px...", flush=True)
    if not recorte_exacto(temp, dim, aoi):
        return False
    borrar_producto(temp)

    print("   %s" % verificar_grilla(dim, aoi), flush=True)
    print("   copia GeoTIFF para QGIS...", flush=True)
    copia_geotiff(dim, tif)
    nombres.registrar(PROCESADOS, [corto, aoi, etiqueta, fecha, original, archivo])
    print("   OK (%.1f min) -> %s.dim" % ((time.time() - t0) / 60, corto),
          flush=True)
    return True


print(__doc__)
if not hay_gpt():
    sys.exit("No se encontro '%s'. Instalar SNAP o editar la variable GPT "
             "en este script con la ruta completa a gpt(.exe)." % GPT)

hechos, fallidos = 0, 0
for epoca in EPOCAS:
    if FILTRO_EPOCA and FILTRO_EPOCA not in epoca:
        continue
    for aoi in AOIS_UTM:
        for etiqueta, grafo, patron in TRABAJOS:
            if FILTRO and etiqueta != FILTRO:
                continue
            if etiqueta == "SAOCOM_L1A":
                # el producto SAOCOM cubre los dos AOI: vive en <epoca>/SAOCOM/
                entradas = sorted(glob.glob(os.path.join(
                    DESCARGAS, epoca, "SAOCOM", "*", patron)))
            else:
                entradas = sorted(glob.glob(os.path.join(
                    DESCARGAS, epoca, aoi, etiqueta, patron)))
            entradas = [e for e in entradas if not e.endswith(".tmp")]
            if not entradas:
                continue
            print("\n=== %s | %s | %s: %d productos ==="
                  % (epoca, aoi, etiqueta, len(entradas)), flush=True)
            for e in entradas:
                print(" ", os.path.basename(e), flush=True)
                if procesar(e, grafo, aoi, etiqueta, epoca):
                    hechos += 1
                else:
                    fallidos += 1

print("\nListo. %d productos procesados, %d con error." % (hechos, fallidos))
print("PRINCIPAL: 04_Tablas_de_trabajo/<AOI>/<sensor>/*.dim  (BEAM-DIMAP, con metadatos: "
      "usar este en SNAP)")
print("Copia GIS: el .tif del mismo nombre, solo para visualizar en QGIS.")
