# -*- coding: utf-8 -*-
"""
aoi_config.py   ---> PUENTE DE COMPATIBILIDAD. NO ES LA CONFIGURACION REAL.

La configuracion real y unica del proyecto esta en:

    00_COMUN/configuracion_comun.py

Este archivo existe solo para que los scripts escritos ANTES de la
reorganizacion en practicos sigan funcionando sin tocarlos. Se limita a
reexportar lo que define configuracion_comun y a traducir los nombres de
carpeta antiguos a las rutas nuevas:

    nombre antiguo          carpeta nueva
    ---------------------   ------------------------------------------
    DESCARGAS               00_COMUN/08_Originales_crudos
    PROCESADOS              <este practico>/02_Subsets_SNAP_QGIS
    CRUDOS                  <este practico>/02_Subsets_SNAP_QGIS/00_Recortes_crudos_fase
    DOCUMENTACION           <este practico>/05_Resultados
    GRAFOS                  <este practico>/03_Scripts/01_Pre_procesamiento
    SCRIPTS                 <este practico>/03_Scripts

Si escribe un script NUEVO, no importe de aqui: importe de
configuracion_comun, que es la fuente unica de verdad.
"""
import os
import sys

FUNCIONES = os.path.dirname(os.path.abspath(__file__))     # <TP>/03_Scripts/funciones
SCRIPTS = os.path.dirname(FUNCIONES)                       # <TP>/03_Scripts
BASE = os.path.dirname(SCRIPTS)                            # <TP>
PROYECTO = os.path.dirname(BASE)                           # 02_Practica

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

from configuracion_comun import (          # noqa: E402,F401
    EPSG, PIXEL, NPIX, AOIS_UTM, AOIS_WGS84, EPOCAS, INCENDIO, epoca_de,
    ruta_practico, DESCARGAS_ORIGINALES, TOPOGRAFIA, UNIDADES, NODATA,
    AOI_DIR, COBERTURAS, DICCIONARIO, PRACTICOS,
)

# ------------------------------- alias historicos de rutas -------------------
DESCARGAS = DESCARGAS_ORIGINALES
PROCESADOS = os.path.join(BASE, "02_Subsets_SNAP_QGIS")
CRUDOS = os.path.join(PROCESADOS, "00_Recortes_crudos_fase")
DOCUMENTACION = os.path.join(BASE, "05_Resultados")
GRAFOS = os.path.join(BASE, "08_Grafos_SNAP")
SUBSETS = os.path.join(BASE, "04_Tablas_de_trabajo")


# --------------------- donde vive REALMENTE cada producto --------------------
# CUIDADO con PROCESADOS y CRUDOS de aqui arriba: se resuelven contra el
# practico donde vive el script que importa. Sirven cuando un practico busca
# SUS propios productos, pero NO cuando un script de TP1 quiere localizar los
# productos de TP3 o de TP4.
#
# Ademas, tras la reorganizacion los .dim no cuelgan de <practico>/02_Subsets_SNAP_QGIS/
# <epoca>/..., sino que estan agrupados por sensor:
#
#     <practico>/02_Subsets_SNAP_QGIS/<grupo>/<epoca>/<AOI>[/<sensor>]/*.dim
#
# Las funciones de abajo traducen sensor -> ubicacion real. Uselas en lugar de
# armar la ruta a mano: si manana se mueve una carpeta, se cambia aca y no en
# cada script.

UBICACION = {
    # sensor            practico  grupo             subcarpeta por sensor
    "S2_L2A":          ("TP3", "Sentinel_2",    False),
    "S1_GRD":          ("TP4", "Sentinel_1",    True),
    "S1_SLC":          ("TP4", "Sentinel_1",    True),
    "SAOCOM_L1A":      ("TP4", "SAOCOM",        True),
    "NISAR_GCOV":      ("TP4", "NISAR",         True),
    "ALOS_PALSAR_2":   ("TP4", "ALOS_PALSAR_2", True),
    # El mosaico de JAXA cuelga del grupo ALOS_PALSAR_2 pero su carpeta hoja
    # se llama PALSAR2_MOSAIC, que no es lo mismo que el nombre del grupo.
    "PALSAR2_MOSAIC":  ("TP4", "ALOS_PALSAR_2", True),
}


def dir_procesado(sensor, epoca, aoi):
    """Carpeta real de los productos ya procesados de <sensor>.

    Devuelve None si el sensor no tiene productos procesados (por ejemplo el
    ALOS_QP historico, que se deja crudo).
    """
    if sensor not in UBICACION:
        return None
    tp, grupo, con_sensor = UBICACION[sensor]
    partes = [grupo, epoca, aoi] + ([sensor] if con_sensor else [])
    return ruta_practico(tp, "02_Subsets_SNAP_QGIS", *partes)


def dir_crudo(sensor, epoca, aoi):
    """Carpeta real de los recortes crudos con fase. Solo SAR, y solo en TP4."""
    return ruta_practico("TP4", "02_Subsets_SNAP_QGIS", "00_Recortes_crudos_fase",
                         epoca, aoi, sensor)


def dir_gedi():
    """Los CSV de GEDI no se separan por epoca ni por carpeta de AOI: el AOI va
    en el nombre del archivo. Viven en TP2."""
    return ruta_practico("TP2", "02_Subsets_SNAP_QGIS")
