#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
configuracion_comun.py
Configuracion UNICA y compartida por los cinco practicos.

El documento del curso lo exige: "La resolucion, proyeccion y periodo de
analisis deben estar definidos en un archivo comun de configuracion". Este es
ese archivo. Ningun practico debe redefinir estos valores por su cuenta: todos
lo importan de aqui. Asi se garantiza que los cinco trabajen sobre exactamente
la misma grilla y que sus resultados sean comparables pixel a pixel.

COMO SE USA DESDE UN PRACTICO
   import sys
   sys.path.insert(0, r"C:\\Temp\\CURSO_BIOMASA_2026\\02_Practica\\00_COMUN")
   from configuracion_comun import AOIS_UTM, EPSG, PIXEL, ruta_practico
"""
import os

# ---------------------------------------------------------------- CARTOGRAFIA
EPSG = 32719          # WGS 84 / UTM zona 19 Sur
PIXEL = 10            # metros: la grilla comun de todo el proyecto
NPIX = 1500           # 1500 x 1500 pixeles = 15 x 15 km

# Esquinas de cada AOI en la proyeccion comun (xmin, ymin, xmax, ymax).
# Estan alineadas a multiplos de 10 m: los bordes de pixel coinciden entre
# todos los sensores, que es lo que permite apilarlos sin remuestrear.
AOIS_UTM = {
    "BOSQUE_NW_02": (287200.0, 5270200.0, 302200.0, 5285200.0),
    "ESTEPA_NW_02": (319100.0, 5254200.0, 334100.0, 5269200.0),
}

# Los mismos AOI en coordenadas geograficas (lonmin, latmin, lonmax, latmax),
# que es lo que piden los catalogos para buscar.
AOIS_WGS84 = {
    "BOSQUE_NW_02": (-71.5978, -42.6953, -71.4095, -42.5562),
    "ESTEPA_NW_02": (-71.2138, -42.8468, -71.0258, -42.7084),
}

# ------------------------------------------------------------------- EPOCAS
# El periodo de analisis, dividido en las cuatro epocas del estudio.
EPOCAS = {
    "00_alos":       {"desde": "20070101", "hasta": "20110101",
                                "que_es": "Banda L de otra decada (ALOS-1 quad-pol)"},
    "01_base":   {"desde": "20231001", "hasta": "20240401",
                                "que_es": "Bosque sin perturbar, un ano antes"},
    "02_pre": {"desde": "20251101", "hasta": "20260111",
                                "que_es": "Estado inmediatamente anterior al incendio"},
    "03_post":   {"desde": "20260227", "hasta": "20260701",
                                "que_es": "Estado posterior al incendio"},
}

# El incendio ocurrio entre estas dos fechas (establecido con los propios datos:
# dNBR, caida de gamma0 y NDVI, y confirmado por el registro CONAE-AQD).
INCENDIO = {"ultima_imagen_sana": "20260110", "primera_imagen_quemada": "20260227"}


def dentro_del_incendio(fecha):
    """True si la fecha AAAAMMDD cae DURANTE el incendio.

    Entre el 10/01 y el 27/02 de 2026 el bosque se estaba quemando: una escena
    de ese lapso no es ni "antes" ni "despues". Etiquetarla como cualquiera de
    las dos cosas arruina el dNBR sin dar ningun error.
    """
    return (INCENDIO["ultima_imagen_sana"] < fecha
            < INCENDIO["primera_imagen_quemada"])


def epoca_de(fecha):
    """Devuelve la epoca a la que pertenece una fecha AAAAMMDD."""
    for nombre, d in EPOCAS.items():
        if fecha < d["hasta"]:
            return nombre
    return "03_post"


# -------------------------------------------------------------------- RUTAS
def _localizar_comun():
    """Devuelve la carpeta 00_COMUN REAL, sea cual sea la copia que se importe.

    Existe una copia de este mismo archivo en cada
    <practico>/03_Scripts/configuracion/. Si se tomara el directorio del archivo
    como raiz —que es lo que se hacia antes—, al importar una de esas copias
    TODAS las rutas del proyecto colgarian de la carpeta de configuracion del
    practico: las descargas originales terminarian en
    03_Scripts/configuracion/08_Originales_crudos/ en vez de en 00_COMUN.
    Paso el 26/07/2026 con 2,7 GB de GEDI L4A.

    Se sube por el arbol hasta encontrar la carpeta que contiene 00_COMUN. Asi
    la fuente unica es unica de verdad, aunque el archivo este duplicado.
    """
    d = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(d) == "00_COMUN":
        return d
    p = d
    while p != os.path.dirname(p):
        cand = os.path.join(p, "00_COMUN")
        if os.path.isdir(cand):
            return cand
        p = os.path.dirname(p)
    return d          # no se encontro: se comporta como antes


RAIZ = _localizar_comun()                                  # .../00_COMUN
PROYECTO = os.path.dirname(RAIZ)                           # .../02_Practica

COMUN = RAIZ
AOI_DIR = os.path.join(COMUN, "01_AOI")
COBERTURAS = os.path.join(COMUN, "02_Coberturas")
TOPOGRAFIA = os.path.join(COMUN, "03_Topografia")
# METADATOS se quito el 29/07/2026: apuntaba a 00_COMUN/05_Metadatos, que NO
# existe, y ningun script la usaba. Una constante que apunta a una carpeta
# inexistente no da error: espera calladita a que alguien la use.
DICCIONARIO = os.path.join(COMUN, "07_Diccionario_datos")

# Las descargas originales viven en UN SOLO lugar y NO se modifican nunca.
# Los cinco practicos las leen de aqui; asi ningun archivo pesado se duplica.
DESCARGAS_ORIGINALES = os.path.join(COMUN, "08_Originales_crudos")

PRACTICOS = {
    "TP1": "TP1_Busqueda_IA",
    "TP2": "TP2_LiDAR_GEDI_ICESat2",
    "TP3": "TP3_Datos_Opticos",
    "TP4": "TP4_Radar_SAR",
    "TP5": "TP5_Sinergia_Multisensor",
}


def ruta_practico(codigo, *sub):
    """Ruta dentro de un practico. Ej: ruta_practico('TP3', '05_Resultados', '02_Rasters')"""
    return os.path.join(PROYECTO, PRACTICOS[codigo], *sub)


# --------------------------------------------------- CONVENCIONES DE VALORES
# Unidades en que se guardan los productos, para que sean comparables.
UNIDADES = {
    "SAR": "gamma0 LINEAL (no dB). Para pasar a dB: 10*log10(valor). "
           "Se usa gamma0 (no sigma0) porque el relieve es fuerte: ver TP4.",
    "OPTICO": "reflectancia de superficie (0 a 1), ya corregida atmosfericamente",
    "GEDI": "metros (alturas rh), fracciones (cover), y Mg/ha si hay biomasa",
}
NODATA = 0.0

if __name__ == "__main__":
    print(__doc__)
    print("Proyecto:", PROYECTO)
    print("Grilla comun: EPSG:%d, %d m, %d x %d px" % (EPSG, PIXEL, NPIX, NPIX))
    for a, v in AOIS_UTM.items():
        print("  %-14s %s" % (a, v))
    print("\nEpocas:")
    for e, d in EPOCAS.items():
        print("  %-24s %s" % (e, d["que_es"]))
