# -*- coding: utf-8 -*-
"""
nombres.py
Nombres cortos para las SALIDAS, con trazabilidad.

Windows limita la ruta completa a 260 caracteres. Los nombres originales de los
productos superan los 65 caracteres y, sumados a la carpeta .data del formato
BEAM-DIMAP (que a su vez contiene un archivo por banda), agotan ese limite y
provocan errores dificiles de diagnosticar.

REGLA: los productos ORIGINALES de 04_descargas/ NO se renombran nunca, porque
su nombre es su acta de nacimiento. Los nombres cortos se aplican solo a las
copias de trabajo de 04_Tablas_de_trabajo/, y la correspondencia entre unos y otros queda
registrada en 00_COMUN/07_Diccionario_datos/diccionario_nombres.csv

Ejemplos:
  S1A_IW_SLC__1SDV_20251123T234217_20251123T234244_062011_07C1DF_2611
      -> S1A_IW_SLC_20251123_062011_R164_2611
  S2B_MSIL2A_20251125T142709_N0511_R053_T18GYT_20251125T180610
      -> S2B_L2A_20251125_R053_T18GYT
  EOL1ASARSAO1B13870600  (adquirido el 2025-11-23)
      -> SAO1B_L1A_20251123_13870600
"""
import csv
import os

CSV_DICCIONARIO = "diccionario_nombres.csv"
ENCABEZADO = ["nombre_corto", "aoi", "sensor", "fecha", "nombre_original",
              "archivo_origen"]


def orbita_relativa(satelite, orbita_absoluta):
    """Track (orbita relativa) de Sentinel-1 a partir de la orbita absoluta."""
    desfase = {"S1A": 73, "S1B": 27, "S1C": 172}.get(satelite)
    if desfase is None:
        return None
    return (int(orbita_absoluta) - desfase) % 175 + 1


def corto_sentinel1(nombre):
    """Nombre corto de Sentinel-1, valido para GRD y para SLC.

    ATENCION: los dos tipos de producto se nombran distinto en origen. El SLC
    lleva DOS guiones bajos ("SLC__1SDV"), que al partir la cadena generan un
    campo vacio y desplazan una posicion todos los campos siguientes:

      S1A_IW_SLC__1SDV_20251123T234217_..._062011_07C1DF_2611
       0   1   2   3    4      5(fecha)      -3        -1
      S1A_IW_GRDH_1SDV_20251123T234218_..._062011_07C1DF_B6B6
       0   1    2   3      4(fecha)          -3        -1

    Se resuelve buscando el primer campo con formato de fecha, en lugar de
    confiar en una posicion fija.

    Ejemplos:
      ..._SLC__1SDV_20251123T234217_..._062011_07C1DF_2611
          -> S1A_IW_SLC_20251123_062011_R164_2611
      ..._GRDH_1SDV_20251123T234218_..._062011_07C1DF_B6B6
          -> S1A_IW_GRD_20251123_062011_R164_B6B6

    El sufijo final (2611, B6B6) es el identificador unico del producto: dos
    frames de la MISMA orbita y el MISMO dia -por ejemplo, el que cubre el
    bosque y el que cubre la estepa- solo se distinguen por el.
    """
    p = nombre.split("_")
    sat = p[0]                                 # S1A / S1B / S1C
    modo = p[1]                                # IW
    tipo = "GRD" if p[2].startswith("GRD") else p[2]   # GRDH -> GRD
    fecha = next(c[:8] for c in p
                 if len(c) == 15 and c[8] == "T" and c[:8].isdigit())
    orb_abs = p[-3]                            # orbita absoluta
    ident = p[-1]                              # identificador unico del producto
    rel = orbita_relativa(sat, orb_abs)
    corto = "%s_%s_%s_%s_%s_R%03d_%s" % (sat, modo, tipo, fecha, orb_abs,
                                         rel, ident)
    return corto, fecha


def corto_sentinel2(nombre):
    """S2B_MSIL2A_20251125T142709_N0511_R053_T18GYT_...
       -> (S2B_L2A_20251125_R053_T18GYT, fecha)"""
    p = nombre.split("_")
    sat = p[0]                       # S2A / S2B / S2C
    nivel = p[1].replace("MSIL", "L")    # MSIL2A -> L2A
    fecha = p[2][:8]
    orbita = p[4]                    # R053
    tile = p[5]                      # T18GYT
    return "%s_%s_%s_%s_%s" % (sat, nivel, fecha, orbita, tile), fecha


def corto_saocom(id_producto, fecha):
    """EOL1ASARSAO1B13870600 + 20251123 -> SAO1B_L1A_20251123_13870600"""
    sat = "SAO1B" if "SAO1B" in id_producto else "SAO1A"
    num = id_producto.split("SAO1B")[-1] if sat == "SAO1B" \
        else id_producto.split("SAO1A")[-1]
    return "%s_L1A_%s_%s" % (sat, fecha, num), fecha


def registrar(subsets_dir, fila):
    """Anota la equivalencia nombre corto <-> nombre original."""
    ruta = os.path.join(subsets_dir, CSV_DICCIONARIO)
    nuevo = not os.path.exists(ruta)
    filas = []
    if not nuevo:
        with open(ruta, newline="", encoding="utf-8") as f:
            filas = [r for r in csv.reader(f)][1:]
    # evitar duplicados: la clave es (nombre_corto, AOI), porque un mismo
    # producto SAOCOM se procesa para los dos AOI con el mismo nombre corto
    filas = [r for r in filas if r and (r[0], r[1]) != (fila[0], fila[1])]
    filas.append(fila)
    filas.sort(key=lambda r: (r[1], r[2], r[3]))
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(ENCABEZADO)
        w.writerows(filas)
