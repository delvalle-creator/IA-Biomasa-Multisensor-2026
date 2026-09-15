#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_03c_nisar_post_y_fusion.py

Incorpora al practico las dos escenas NISAR GCOV POSTERIORES al incendio y
arma con ellas la fusion de orbita ascendente y descendente.

QUE PROBLEMA RESUELVE
---------------------
El radar mira de costado. En un valle cordillerano eso deja tres defectos
geometricos: layover (la ladera que mira al sensor se vuelca sobre el valle),
sombra (la ladera opuesta no recibe senal) y acortamiento. Ninguno se arregla
con un filtro, porque donde no hubo senal no hay nada que filtrar.

La salida es mirar el mismo terreno desde las dos geometrias. Este programa toma
la escena ascendente y la descendente, las recorta a la grilla comun del
practico y las combina.

Ahora bien, conviene separar dos cosas que suelen mezclarse. Una es la
COBERTURA: cuantas celdas sin dato rellena la segunda orbita. En un producto
GCOV eso suele ser poco, porque viene con correccion radiometrica de terreno y
la mascara de la mision deja pocos huecos. La otra es el SESGO GEOMETRICO:
cuanto cambia el valor medido segun desde donde se mire, aunque las dos orbitas
tengan dato. Eso si es grande, y es lo que el programa mide e informa al final.

LAS DOS ESCENAS
---------------
    24/08/2026   traza 169, frame 4005, DESCENDENTE
    25/08/2026   traza 003, frame 4005, ASCENDENTE

Son las mismas trazas y el mismo frame que tres de las escenas anteriores al
incendio, de modo que cada par se compara sin cambiar de geometria:

    ascendente    04/12/2025 y 28/12/2025   contra   25/08/2026
    descendente   08/01/2026                contra   24/08/2026

SOBRE LA FECHA, QUE HAY QUE TENER PRESENTE
------------------------------------------
Agosto es pleno invierno y son siete meses posteriores al fuego. Para medir el
cambio producido por el incendio no son comparables con la Sentinel-1 del
27/02 ni con la Sentinel-2 del 05/03. Para el problema geometrico, que es a lo
que se las usa aqui, la fecha no interviene.

SI UNA ESCENA NO LLEGARA A CUBRIR UN RECINTO
--------------------------------------------
Cuando la franja de una escena no alcanza a cubrir el recinto entero, lo que
falta se escribe como NaN en vez de descartar la escena, y el programa informa
que porcentaje quedo sin dato. Las dos escenas de agosto de 2026 cubren los dos
recintos por completo.

QUE ESCRIBE
-----------
En 02_Subsets_SNAP_QGIS/NISAR/03_post_incendio_2026/<recinto>/NISAR_GCOV/

    NISAR_GCOV_20260824.tif / .dim   gamma0 HH y HV, descendente
    NISAR_GCOV_20260825.tif / .dim   gamma0 HH y HV, ascendente
    NISAR_GCOV_*_mask.tif            mascara de calidad del producto
    NISAR_FUSION_ASC_DES_202608.tif / .dim

La fusion lleva seis capas:

    HV_asc_db              HV ascendente en decibeles
    HV_des_db              HV descendente en decibeles
    HV_fusion_db           promedio de las dos, en potencia lineal
    HH_fusion_db           lo mismo en HH
    HV_asc_menos_des_db    la diferencia entre geometrias
    RVI_dual               indice de vegetacion radar, 4*HV/(HH+HV)

Las expresiones son las del grafo de SNAP Fusion_ASC_DES_NISAR.xml. Aqui no
hace falta el operador Collocate: las dos escenas se recortan a la misma grilla
comun de 1500 x 1500 pixeles, con lo que quedan superpuestas celda a celda sin
remuestrear nada.

POR QUE NO SE ABRE EL GCOV DIRECTAMENTE EN SNAP
-----------------------------------------------
SNAP 14 no trae lector de GCOV. El complemento NISAR GCOV Reader, de autoria de
H. F. del Valle, resuelve esa lectura: abre el HDF5 en QGIS y convierte el
producto entero a BEAM-DIMAP para SNAP. Esta en la carpeta 09_Herramientas de
este mismo practico.
Este programa no lo necesita —lee el HDF5 con h5py y recorta por ventana, igual
que TP4_03_recortar_nisar.py— pero es la herramienta con la que se trabaja la
escena completa.

USO (entorno conda 'aoi'):   python TP4_03c_nisar_post_y_fusion.py
"""
import glob
import os
import struct
import sys
import warnings

try:
    import h5py
    import numpy as np
    from osgeo import gdal, osr
except ImportError:
    sys.exit("Falta h5py, numpy o GDAL. Activar el entorno conda 'aoi'.")

# --- para que Python encuentre funciones/ y configuracion/ del practico ---
_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d):
    if os.path.isdir(os.path.join(_d, "funciones")):
        sys.path.insert(0, os.path.join(_d, "funciones"))
        sys.path.insert(0, os.path.join(_d, "configuracion"))
        break
    _d = os.path.dirname(_d)

from aoi_config import (AOIS_UTM, DESCARGAS, PROCESADOS, EPSG, PIXEL,
                        TOPOGRAFIA, dir_procesado)
import nombres

gdal.UseExceptions()

RUTA = "science/LSAR/GCOV/grids/frequencyA"
EPOCA = "03_post"
NPIX = 1500
CAPAS = [("HHHH", "Gamma0_HH"), ("HVHV", "Gamma0_HV"),
         ("numberOfLooks", "numberOfLooks"), ("mask", "mask")]


# ---------------------------------------------------------------------------
# Lectura del HDF5
# ---------------------------------------------------------------------------
def h5_completo(ruta):
    """El superbloque HDF5 declara donde termina el archivo."""
    try:
        d = open(ruta, "rb").read(64)
        if d[:8] != b"\x89HDF\r\n\x1a\n":
            return False
        ver = d[8]
        eof = struct.unpack("<Q", d[40:48] if ver in (0, 1) else d[28:36])[0]
        return os.path.getsize(ruta) >= eof > 0
    except Exception:
        return False


def fecha_de(nombre):
    for t in nombre.split("_"):
        if len(t) == 15 and t[8:9] == "T" and t[:8].isdigit():
            return t[:8]
    return "00000000"


def orbita_de(nombre):
    """'A' ascendente o 'D' descendente, del septimo campo del nombre."""
    p = nombre.split("_")
    return p[6] if len(p) > 6 and p[6] in ("A", "D") else "?"


def ventana(grupo, clave, i0, j0, n, relleno):
    """Lee un cuadrado de n x n celdas del producto a partir de (i0, j0).

    Si la ventana se sale de la grilla, lo que falta se completa con 'relleno'
    en vez de descartar la escena entera: el recinto sale completo, con el
    hueco escrito como NaN y declarado en pantalla.
    """
    if clave not in grupo:
        return None, 0.0
    ny_p, nx_p = grupo[clave].shape
    ii0, ii1 = max(i0, 0), min(i0 + n, nx_p)
    jj0, jj1 = max(j0, 0), min(j0 + n, ny_p)
    if ii1 <= ii0 or jj1 <= jj0:
        return None, 1.0

    origen = grupo[clave][jj0:jj1, ii0:ii1]
    tipo = np.uint8 if origen.dtype == np.uint8 else np.float32
    destino = np.full((n, n), relleno, dtype=tipo)
    destino[jj0 - j0:jj1 - j0, ii0 - i0:ii1 - i0] = origen.astype(tipo)
    fuera = 1.0 - ((ii1 - ii0) * (jj1 - jj0)) / float(n * n)
    return destino, fuera


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------
def escribir_tif(ruta, capas, x0, y0, paso):
    """GeoTIFF georreferenciado. 'capas' = lista de (nombre, array)."""
    ny, nx = capas[0][1].shape
    tipos = {np.dtype("float32"): gdal.GDT_Float32,
             np.dtype("uint8"): gdal.GDT_Byte,
             np.dtype("uint16"): gdal.GDT_UInt16}
    ds = gdal.GetDriverByName("GTiff").Create(
        ruta, nx, ny, len(capas), tipos.get(capas[0][1].dtype, gdal.GDT_Float32),
        options=["COMPRESS=DEFLATE", "TILED=YES"])
    ds.SetGeoTransform((x0, paso, 0, y0, 0, -paso))
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(EPSG)
    ds.SetProjection(sr.ExportToWkt())
    for i, (nom, a) in enumerate(capas, 1):
        b = ds.GetRasterBand(i)
        b.WriteArray(a)
        b.SetDescription(nom)
        if a.dtype == np.float32:
            b.SetNoDataValue(float("nan"))
    ds.FlushCache()
    ds = None


_HDR = """ENVI
description = {%s}
samples = %d
lines   = %d
bands   = 1
header offset = 0
file type = ENVI Standard
data type = 4
interleave = bsq
byte order = 1
map info = {UTM, 1, 1, %.3f, %.3f, %.3f, %.3f, %d, South, WGS-84}
"""

_DIM = """<?xml version="1.0" encoding="ISO-8859-1"?>
<Dimap_Document name="%(nombre)s.dim">
    <Metadata_Id>
        <METADATA_FORMAT version="2.12.1">DIMAP</METADATA_FORMAT>
        <METADATA_PROFILE>BEAM-DATAMODEL-V1</METADATA_PROFILE>
    </Metadata_Id>
    <Dataset_Id>
        <DATASET_SERIES>BEAM-PRODUCT</DATASET_SERIES>
        <DATASET_NAME>%(nombre)s</DATASET_NAME>
    </Dataset_Id>
    <Production>
        <DATASET_PRODUCER_NAME />
        <PRODUCT_TYPE>NISAR_GCOV</PRODUCT_TYPE>
    </Production>
    <Coordinate_Reference_System>
        <WKT>%(wkt)s</WKT>
    </Coordinate_Reference_System>
    <Geoposition>
        <IMAGE_TO_MODEL_TRANSFORM>%(paso).10f,0.0,0.0,-%(paso).10f,%(x0).6f,%(y0).6f</IMAGE_TO_MODEL_TRANSFORM>
    </Geoposition>
    <Raster_Dimensions>
        <NCOLS>%(nx)d</NCOLS>
        <NROWS>%(ny)d</NROWS>
        <NBANDS>%(nb)d</NBANDS>
    </Raster_Dimensions>
    <Data_Access>
        <DATA_FILE_FORMAT>ENVI</DATA_FILE_FORMAT>
        <DATA_FILE_FORMAT_DESC>ENVI File Format</DATA_FILE_FORMAT_DESC>
        <DATA_FILE_ORGANISATION>BAND_SEPARATE</DATA_FILE_ORGANISATION>
%(archivos)s
    </Data_Access>
    <Image_Interpretation>
%(bandas)s
    </Image_Interpretation>
</Dimap_Document>
"""

_BANDA = """        <Spectral_Band_Info>
            <BAND_INDEX>%(i)d</BAND_INDEX>
            <BAND_NAME>%(nombre)s</BAND_NAME>
            <BAND_DESCRIPTION>%(desc)s</BAND_DESCRIPTION>
            <BAND_RASTER_WIDTH>%(nx)d</BAND_RASTER_WIDTH>
            <BAND_RASTER_HEIGHT>%(ny)d</BAND_RASTER_HEIGHT>
            <DATA_TYPE>float32</DATA_TYPE>
            <PHYSICAL_UNIT>%(unidad)s</PHYSICAL_UNIT>
            <SCALING_FACTOR>1.0</SCALING_FACTOR>
            <SCALING_OFFSET>0.0</SCALING_OFFSET>
            <LOG10_SCALED>false</LOG10_SCALED>
            <NO_DATA_VALUE_USED>true</NO_DATA_VALUE_USED>
            <NO_DATA_VALUE>NaN</NO_DATA_VALUE>
        </Spectral_Band_Info>"""


def escribir_dimap(ruta_dim, capas, x0, y0, paso, unidades=None):
    """BEAM-DIMAP: un .dim y una carpeta .data con un ENVI por banda.

    Se escribe en BIG-ENDIAN y con byte order = 1, que es como BEAM-DIMAP
    guarda sus rasteres; SNAP 14 los abre con File > Open Product.
    """
    nombre = os.path.splitext(os.path.basename(ruta_dim))[0]
    carpeta = os.path.join(os.path.dirname(ruta_dim), nombre + ".data")
    os.makedirs(carpeta, exist_ok=True)
    unidades = unidades or {}
    ny, nx = capas[0][1].shape
    zona = EPSG % 100

    archivos, bandas = [], []
    for i, (nom, a) in enumerate(capas):
        a = a.astype(">f4")
        a.tofile(os.path.join(carpeta, nom + ".img"))
        with open(os.path.join(carpeta, nom + ".hdr"), "w") as fh:
            fh.write(_HDR % ("NISAR GCOV " + nom, nx, ny, x0, y0,
                             paso, paso, zona))
        archivos.append('        <Data_File>\n'
                        '            <DATA_FILE_PATH href="%s.data/%s.hdr" />\n'
                        '            <BAND_INDEX>%d</BAND_INDEX>\n'
                        '        </Data_File>' % (nombre, nom, i))
        bandas.append(_BANDA % {"i": i, "nombre": nom, "nx": nx, "ny": ny,
                                "desc": "NISAR GCOV " + nom,
                                "unidad": unidades.get(nom, "gamma0")})

    sr = osr.SpatialReference()
    sr.ImportFromEPSG(EPSG)
    with open(ruta_dim, "w") as fh:
        fh.write(_DIM % {"nombre": nombre, "wkt": sr.ExportToWkt(),
                         "paso": paso, "x0": x0, "y0": y0,
                         "nx": nx, "ny": ny, "nb": len(capas),
                         "archivos": "\n".join(archivos),
                         "bandas": "\n".join(bandas)})


# ---------------------------------------------------------------------------
# Cuentas
# ---------------------------------------------------------------------------
def a_db(lineal):
    """10*log10 donde hay potencia; NaN donde no la hay."""
    salida = np.full(lineal.shape, np.nan, dtype=np.float32)
    bien = np.isfinite(lineal) & (lineal > 0)
    salida[bien] = 10.0 * np.log10(lineal[bien])
    return salida


def promedio_db(a, b):
    """Promedio en potencia lineal, en decibeles. Si una sola tiene dato, esa."""
    ba = np.isfinite(a) & (a > 0)
    bb = np.isfinite(b) & (b > 0)
    salida = np.full(a.shape, np.nan, dtype=np.float32)
    dos = ba & bb
    salida[dos] = 10.0 * np.log10((a[dos] + b[dos]) / 2.0)
    solo_a = ba & ~bb
    salida[solo_a] = 10.0 * np.log10(a[solo_a])
    solo_b = bb & ~ba
    salida[solo_b] = 10.0 * np.log10(b[solo_b])
    return salida


def cociente_db(a, b):
    salida = np.full(a.shape, np.nan, dtype=np.float32)
    bien = np.isfinite(a) & (a > 0) & np.isfinite(b) & (b > 0)
    salida[bien] = 10.0 * np.log10(a[bien] / b[bien])
    return salida


def rvi_dual(hh_a, hv_a, hh_d, hv_d):
    """4*HV/(HH+HV) sobre el promedio de las dos orbitas."""
    salida = np.full(hh_a.shape, np.nan, dtype=np.float32)
    bien = np.ones(hh_a.shape, dtype=bool)
    for c in (hh_a, hv_a, hh_d, hv_d):
        bien &= np.isfinite(c) & (c > 0)
    hv = (hv_a[bien] + hv_d[bien]) / 2.0
    hh = (hh_a[bien] + hh_d[bien]) / 2.0
    salida[bien] = (4.0 * hv) / (hh + hv)
    return salida


def promediar(a, k):
    """Promedia el raster en bloques de k x k celdas.

    Un bloque entero sin dato da NaN, que es lo correcto; se silencia el aviso
    de numpy para que no ensucie la salida.
    """
    n = (a.shape[0] // k) * k
    b = a[:n, :n].reshape(n // k, k, n // k, k)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmean(np.nanmean(b, axis=3), axis=1)


def diagnostico(asc_db, des_db, fus_db, dif_db, looks):
    """Informa lo que la fusion aporta, que no es lo mismo en cada sitio.

    Dos cosas distintas, y conviene no confundirlas:

    1. COBERTURA. Cuantas celdas gana la fusion sobre una sola orbita. En un
       producto GCOV suele ser poco: viene con correccion radiometrica de
       terreno aplicada y la mascara de la mision deja pocos huecos.

    2. GEOMETRIA. Cuanto cambia el valor medido segun desde donde se mire,
       AUNQUE las dos orbitas tengan dato. Se mide promediando la diferencia
       entre orbitas en ventanas cada vez mas grandes: el moteado se promedia
       y baja como la raiz del numero de celdas, y lo que no baja asi es
       estructura. Si a 300 m queda bastante mas de lo que el moteado predice,
       lo que sobra es geometria (y, en parte, el cambio real entre las dos
       fechas).
    """
    con_asc = np.isfinite(asc_db)
    con_fus = np.isfinite(fus_db)
    ganadas = int(con_fus.sum() - con_asc.sum())
    print("     cobertura: ascendente %.2f%%, descendente %.2f%%, fusion %.2f%%"
          % (100 * con_asc.mean(), 100 * np.isfinite(des_db).mean(),
             100 * con_fus.mean()))
    print("     la fusion suma %d celdas sobre la ascendente sola (%.3f%%)"
          % (ganadas, 100.0 * ganadas / con_asc.size))
    if looks:
        print("     %.1f looks: el moteado solo explicaria %.2f dB de "
              "diferencia entre orbitas"
              % (looks, 10 / np.log(10) * np.sqrt(2.0 / looks)))
    v = dif_db[np.isfinite(dif_db)]
    base = float(v.std()) if v.size else 0.0
    print("     diferencia entre orbitas, promediada en ventanas:")
    print("        ventana   mediana   desv.est.   si fuera solo moteado")
    for k in (1, 3, 10, 30):
        d = promediar(dif_db, k)
        w = d[np.isfinite(d)]
        if not w.size:
            continue
        print("        %5d m   %6.2f    %6.2f dB      %6.2f dB"
              % (k * 10, np.median(w), w.std(), base / k))
    d = promediar(dif_db, 30)
    w = d[np.isfinite(d)]
    if w.size:
        print("     a 300 m la diferencia supera 1 dB en el %.1f%% de las "
              "celdas, y llega a %.1f dB"
              % (100 * (np.abs(w) > 1).mean(), np.abs(w).max()))


def moteado_local(a, k=5):
    """Desviacion tipica dentro de ventanas de k x k celdas: a esa escala el
    terreno no cambia y lo que se mide es el moteado."""
    n = (a.shape[0] // k) * k
    b = a[:n, :n].reshape(n // k, k, n // k, k).transpose(0, 2, 1, 3)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return float(np.nanmedian(np.nanstd(b.reshape(-1, k * k), axis=1)))


def contra_el_relieve(dif_db, aoi):
    """Cruza la diferencia entre orbitas con la pendiente y la orientacion.

    Es la comprobacion de que lo que sobrevive al promediado es geometria: si
    la diferencia crece con la pendiente y cambia de signo entre laderas
    opuestas, no puede ser ruido ni vegetacion.
    """
    pen = os.path.join(TOPOGRAFIA, "pendiente", "pendiente_%s.tif" % aoi)
    ori = os.path.join(TOPOGRAFIA, "orientacion", "orientacion_%s.tif" % aoi)
    if not (os.path.isfile(pen) and os.path.isfile(ori)):
        return
    p = gdal.Open(pen).GetRasterBand(1).ReadAsArray().astype("float64")
    o = gdal.Open(ori).GetRasterBand(1).ReadAsArray().astype("float64")
    if p.shape != dif_db.shape or o.shape != dif_db.shape:
        print("     (la pendiente no esta en la misma grilla: no se cruza)")
        return

    print("     la diferencia entre orbitas contra la pendiente del terreno:")
    print("        pendiente          celdas   mediana |dif|      p90")
    for lo, hi in ((0, 5), (5, 10), (10, 20), (20, 30), (30, 90)):
        m = np.isfinite(dif_db) & np.isfinite(p) & (p >= lo) & (p < hi)
        if m.sum() < 500:
            continue
        v = np.abs(dif_db[m])
        print("        %2d a %2d grados  %9d     %5.2f dB     %5.2f dB"
              % (lo, hi, m.sum(), np.median(v), np.percentile(v, 90)))

    print("     y contra la orientacion, en laderas de mas de 15 grados:")
    sectores = (("norte", (o >= 315) | (o < 45)), ("este", (o >= 45) & (o < 135)),
                ("sur", (o >= 135) & (o < 225)), ("oeste", (o >= 225) & (o < 315)))
    for nombre, sel in sectores:
        m = np.isfinite(dif_db) & sel & (p > 15)
        if m.sum() < 500:
            continue
        print("        mira al %-6s %9d     %+5.2f dB"
              % (nombre, m.sum(), np.median(dif_db[m])))


# ---------------------------------------------------------------------------
def recortar(h5path, aoi):
    """Recorta una escena a la grilla comun. Devuelve las capas o None."""
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    base = os.path.basename(h5path)
    fecha, orbita = fecha_de(base), orbita_de(base)

    with h5py.File(h5path, "r") as h:
        g = h[RUTA]
        epsg_prod = int(g["projection"].attrs["epsg_code"])
        if epsg_prod != EPSG:
            print("     OMITIDO: el producto esta en EPSG:%d" % epsg_prod)
            return None
        x, y = g["xCoordinates"][:], g["yCoordinates"][:]
        paso = abs(float(x[1] - x[0]))
        if abs(paso - PIXEL) > 1e-6:
            print("     OMITIDO: el producto viene a %g m y la grilla comun es "
                  "de %g m; usar TP4_03_recortar_nisar.py, que remuestrea"
                  % (paso, PIXEL))
            return None
        bx, by = x[0] - paso / 2.0, y[0] + paso / 2.0
        i0f, j0f = (xmin - bx) / paso, (by - ymax) / paso
        i0, j0 = int(round(i0f)), int(round(j0f))
        if abs(i0f - i0) > 1e-6 or abs(j0f - j0) > 1e-6:
            print("     OMITIDO: los bordes de pixel no caen sobre la grilla "
                  "comun; usar TP4_03_recortar_nisar.py, que remuestrea")
            return None

        capas, enteras, fuera = [], [], 0.0
        for clave, nom in CAPAS:
            relleno = 0 if clave == "mask" else np.nan
            a, f = ventana(g, clave, i0, j0, NPIX, relleno)
            if a is None:
                if clave in ("HHHH", "HVHV"):
                    print("     OMITIDO: la escena no cubre el recinto")
                    return None
                continue
            fuera = max(fuera, f)
            (enteras if a.dtype == np.uint8 else capas).append((nom, a))

    hh = capas[0][1]
    con_dato = float((np.isfinite(hh) & (hh > 0)).mean())
    return {"fecha": fecha, "orbita": orbita, "capas": capas,
            "enteras": enteras, "fuera": fuera, "con_dato": con_dato,
            "origen": base, "xmin": xmin, "ymax": ymax, "paso": paso}


def main():
    print(__doc__)
    carpeta = os.path.join(DESCARGAS, EPOCA, "NISAR", "GCOV")
    archivos = sorted(glob.glob(os.path.join(carpeta, "*.h5")))
    if not archivos:
        sys.exit("No hay .h5 en %s\nCopiar alli las dos escenas posteriores al "
                 "incendio antes de correr esto." % carpeta)

    total = 0
    for aoi in AOIS_UTM:
        print("\n" + "=" * 72)
        print(aoi)
        print("=" * 72)
        salida = dir_procesado("NISAR_GCOV", EPOCA, aoi)
        os.makedirs(salida, exist_ok=True)
        por_orbita = {}

        for f in archivos:
            base = os.path.basename(f)
            print("  %s  orbita %s" % (fecha_de(base), orbita_de(base)))
            if not h5_completo(f):
                print("     ARCHIVO TRUNCADO: volver a copiarlo")
                continue
            r = recortar(f, aoi)
            if r is None:
                continue

            corto = "NISAR_GCOV_%s" % r["fecha"]
            tif = os.path.join(salida, corto + ".tif")
            escribir_tif(tif, r["capas"], r["xmin"], r["ymax"], r["paso"])
            if r["enteras"]:
                escribir_tif(os.path.join(salida, corto + "_mask.tif"),
                             r["enteras"], r["xmin"], r["ymax"], r["paso"])
            escribir_dimap(os.path.join(salida, corto + ".dim"), r["capas"],
                           r["xmin"], r["ymax"], r["paso"])
            nombres.registrar(PROCESADOS, [corto, aoi, "NISAR_GCOV", r["fecha"],
                                           r["origen"].replace(".h5", ""),
                                           r["origen"]])
            print("     OK  %d x %d px  %.1f%% con dato%s"
                  % (NPIX, NPIX, 100 * r["con_dato"],
                     "" if r["fuera"] < 1e-9 else
                     "  (%.1f%% fuera de la franja, escrito como NaN)"
                     % (100 * r["fuera"])))
            por_orbita[r["orbita"]] = r
            total += 1

        if "A" in por_orbita and "D" in por_orbita:
            a, d = por_orbita["A"], por_orbita["D"]
            hh_a, hv_a = a["capas"][0][1], a["capas"][1][1]
            hh_d, hv_d = d["capas"][0][1], d["capas"][1][1]
            fus = [("HV_asc_db", a_db(hv_a)),
                   ("HV_des_db", a_db(hv_d)),
                   ("HV_fusion_db", promedio_db(hv_a, hv_d)),
                   ("HH_fusion_db", promedio_db(hh_a, hh_d)),
                   ("HV_asc_menos_des_db", cociente_db(hv_a, hv_d)),
                   ("RVI_dual", rvi_dual(hh_a, hv_a, hh_d, hv_d))]
            unidades = dict((n, "adimensional" if n == "RVI_dual" else "dB")
                            for n, _ in fus)
            nom = "NISAR_FUSION_ASC_DES_%s" % a["fecha"][:6]
            escribir_tif(os.path.join(salida, nom + ".tif"), fus,
                         a["xmin"], a["ymax"], a["paso"])
            escribir_dimap(os.path.join(salida, nom + ".dim"), fus,
                           a["xmin"], a["ymax"], a["paso"], unidades)
            print("\n  FUSION  %s" % nom)
            looks = None
            for nombre_capa, arr in a["capas"]:
                if nombre_capa == "numberOfLooks":
                    looks = float(np.nanmedian(arr))
            diagnostico(fus[0][1], fus[1][1], fus[2][1], fus[4][1], looks)
            print("     moteado, medido en ventanas de 50 m:")
            for nombre_capa, arr in (("ascendente", fus[0][1]),
                                     ("descendente", fus[1][1]),
                                     ("fusion", fus[2][1])):
                print("        %-12s %.2f dB" % (nombre_capa, moteado_local(arr)))
            print("        promediar dos escenas independientes lo baja a 0,71 "
                  "de lo que era")
            contra_el_relieve(fus[4][1], aoi)
            total += 1
        else:
            print("\n  Sin fusion: hacen falta una escena ascendente y una "
                  "descendente sobre este recinto.")

    print("\n" + "=" * 72)
    print("%d productos escritos." % total)
    print("Salida: TP4_Radar_SAR/02_Subsets_SNAP_QGIS/NISAR/"
          "03_post_incendio_2026/<recinto>/NISAR_GCOV/")
    print("Los .tif se abren en QGIS; los .dim, en SNAP con File > Open Product.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
