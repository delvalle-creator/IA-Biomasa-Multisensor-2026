# -*- coding: utf-8 -*-
"""
TP2_17_mapa_biomasa_GEDI_CCI.py  ---> el mapa de biomasa de GEDI, puesto al
                                      lado del mapa del CCI, celda por celda.

POR QUE HACIA FALTA
-------------------
El anexo del TP2 cotejo CCI contra GEDI huella por huella y encontro donde
viven las diferencias (el matorral bajo de ladera) y donde no las hay (la
lenga alta, la estepa). Pero una tabla no muestra la GEOGRAFIA: para ver la
distribucion espacial de la biomasa -- donde esta el bosque denso, como cae
hacia el ecotono, que dibuja cada producto -- hacen falta los dos MAPAS con
la misma grilla, la misma escala y la misma unidad.

GEDI no es un mapa: es un muestreo a lo largo de orbitas. Para mapearlo se
agrega a celdas de 500 m (las mismas del cotejo del paso 13): en cada celda
con al menos 3 huellas validas se toma la MEDIANA de agbd_Mg_ha. Las celdas
sin muestra suficiente quedan VACIAS y se ven vacias: ese es el mapa honesto
de un muestreo. El CCI, que si es un mapa continuo de 100 m, se promedia a
las mismas celdas de 500 m (promedio de area, ~25 pixeles por celda).

    mapa GEDI   mediana de huellas L4A por celda de 500 m   (Mg/ha)
    mapa CCI    promedio de pixeles de 100 m por celda      (Mg/ha, mapa 2024)
    diferencia  CCI - GEDI donde ambos existen              (positivo = CCI mas alto)

QUE ESPERAR ANTES DE MIRAR
--------------------------
Del anexo: en la lenga alta los dos productos practicamente coinciden; en el
dosel bajo de ladera el CCI estima mas del doble que GEDI; en la estepa ambos
dan casi nada. Si el mapa muestra otra cosa, hay que volver al anexo, no
taparlo.

ENTRADA   05_Resultados/04_Tablas/biomasa_<RECINTO>.csv               (paso 7)
          00_COMUN/08_Originales_crudos/CCI_BIOMASS/*.zip (AGB 2024, sin descomprimir)

SALIDA    05_Resultados/02_Rasters/TP2_AGB_GEDI_500m_<RECINTO>.tif
          05_Resultados/02_Rasters/TP2_AGB_CCI2024_500m_<RECINTO>.tif
          05_Resultados/02_Rasters/TP2_AGB_dif_CCI_menos_GEDI_500m_<RECINTO>.tif
          05_Resultados/04_Tablas/TP2_mapa_AGB_celdas_<RECINTO>.csv
          05_Resultados/06_Control_calidad/TP2_17_mapa_biomasa.log

Los GeoTIFF salen en EPSG:32719 con celda de 500 m, listos para QGIS. Los
archivos de entrada NO se tocan.

USO (entorno conda 'aoi'):   python TP2_17_mapa_biomasa_GEDI_CCI.py
"""
import csv
import os
import statistics as est
import sys

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
sys.path.insert(0, os.path.join(TP2, "03_Scripts", "configuracion"))
from configuracion_comun import AOIS_UTM, EPSG                      # noqa: E402

COMUN = os.path.abspath(os.path.join(TP2, "..", "00_COMUN"))
CRUDOS = os.path.join(COMUN, "08_Originales_crudos", "CCI_BIOMASS")
TABLAS = os.path.join(TP2, "05_Resultados", "04_Tablas")
RASTERS = os.path.join(TP2, "05_Resultados", "02_Rasters")
CONTROL = os.path.join(TP2, "05_Resultados", "06_Control_calidad")

CELDA = 500.0        # metros; la misma grilla del cotejo del paso 13
MIN_HUELLAS = 3      # huellas L4A minimas por celda, como en el paso 13
ANIO_CCI = 2024      # el mapa CCI del cotejo del anexo
NODATA = -9999.0

CCI_EN_ZIP = {
    "BOSQUE_NW_02": ("ESA_CCI_Biomass_v7_BOSQUE_NW_02.zip",
                     "BOSQUE_NW_02/AGB/BOSQUE_NW_02_ESACCI-BIOMASS-L4-AGB-"
                     "MERGED-100m-%d-fv7.0.tif" % ANIO_CCI),
    "ESTEPA_NW_02": ("ESA_CCI_Biomass_v7_ESTEPA_NW_02.zip",
                     "ESTEPA_NW_02/AGB/ESTEPA_NW_02_ESACCI-BIOMASS-L4-AGB-"
                     "MERGED-100m-%d-fv7.0.tif" % ANIO_CCI),
}


def a_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def leer(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def guardar_tif(ruta, arr, transform, descripcion):
    with rasterio.open(ruta, "w", driver="GTiff", height=arr.shape[0],
                       width=arr.shape[1], count=1, dtype="float32",
                       crs="EPSG:%d" % EPSG, transform=transform,
                       nodata=NODATA, compress="deflate") as dst:
        dst.write(arr.astype("float32"), 1)
        dst.update_tags(CONTENIDO=descripcion, UNIDAD="Mg/ha",
                        CELDA="%d m" % int(CELDA))


def main():
    os.makedirs(RASTERS, exist_ok=True)
    os.makedirs(CONTROL, exist_ok=True)
    lineas = []

    def decir(s=""):
        lineas.append(s)
        print(s)

    decir("MAPA DE BIOMASA: GEDI L4A (mediana por celda de %d m) contra CCI %d"
          % (int(CELDA), ANIO_CCI))
    decir("celdas GEDI con menos de %d huellas: VACIAS (asi se ve un muestreo)"
          % MIN_HUELLAS)
    decir("")

    for recinto in ("BOSQUE_NW_02", "ESTEPA_NW_02"):
        xmin, ymin, xmax, ymax = AOIS_UTM[recinto]
        ncol = int(round((xmax - xmin) / CELDA))
        nfil = int(round((ymax - ymin) / CELDA))
        transform = from_origin(xmin, ymax, CELDA, CELDA)

        # ------------------------------------------------ GEDI: mediana por celda
        huellas = leer(os.path.join(TABLAS, "biomasa_%s.csv" % recinto))
        celdas = {}
        usadas = 0
        for x in huellas:
            e = a_float(x.get("este_utm19s"))
            n = a_float(x.get("norte_utm19s"))
            v = a_float(x.get("agbd_Mg_ha"))
            if None in (e, n, v):
                continue
            c = (int((e - xmin) // CELDA), int((n - ymin) // CELDA))
            if 0 <= c[0] < ncol and 0 <= c[1] < nfil:
                celdas.setdefault(c, []).append(v)
                usadas += 1

        gedi = np.full((nfil, ncol), NODATA)
        filas_csv = []
        for (cc, cf), vals in sorted(celdas.items()):
            if len(vals) < MIN_HUELLAS:
                continue
            med = est.median(vals)
            gedi[nfil - 1 - cf, cc] = med          # fila 0 = norte
            filas_csv.append({"celda_col": cc, "celda_fil": cf,
                              "este_centro": "%.1f" % (xmin + (cc + 0.5) * CELDA),
                              "norte_centro": "%.1f" % (ymin + (cf + 0.5) * CELDA),
                              "n_huellas": len(vals),
                              "agbd_gedi_Mg_ha": "%.1f" % med})

        # --------------------------------- CCI: promedio de area a la misma grilla
        zip_, interno = CCI_EN_ZIP[recinto]
        ruta_cci = "zip://" + os.path.join(CRUDOS, zip_) + "!" + interno
        cci = np.full((nfil, ncol), NODATA, dtype="float64")
        with rasterio.open(ruta_cci) as src:
            reproject(source=src.read(1).astype("float64"),
                      destination=cci,
                      src_transform=src.transform, src_crs=src.crs,
                      dst_transform=transform, dst_crs="EPSG:%d" % EPSG,
                      src_nodata=None, dst_nodata=NODATA,
                      resampling=Resampling.average)

        # ------------------------------------------------------------- diferencia
        ambos = (gedi != NODATA) & (cci != NODATA)
        dif = np.full((nfil, ncol), NODATA)
        dif[ambos] = cci[ambos] - gedi[ambos]

        # completar la tabla de celdas con el CCI y la diferencia
        for fila in filas_csv:
            i = nfil - 1 - int(fila["celda_fil"])
            j = int(fila["celda_col"])
            fila["agbd_cci%d_Mg_ha" % ANIO_CCI] = ("%.1f" % cci[i, j]
                                                   if cci[i, j] != NODATA else "")
            fila["dif_cci_menos_gedi_Mg_ha"] = ("%.1f" % dif[i, j]
                                                if dif[i, j] != NODATA else "")

        guardar_tif(os.path.join(RASTERS, "TP2_AGB_GEDI_500m_%s.tif" % recinto),
                    gedi, transform,
                    "mediana de agbd_Mg_ha de GEDI L4A por celda (min %d huellas)"
                    % MIN_HUELLAS)
        guardar_tif(os.path.join(RASTERS, "TP2_AGB_CCI%d_500m_%s.tif"
                                 % (ANIO_CCI, recinto)),
                    cci, transform,
                    "CCI Biomass v7 %d promediado de 100 m a la celda" % ANIO_CCI)
        guardar_tif(os.path.join(RASTERS, "TP2_AGB_dif_CCI_menos_GEDI_500m_%s.tif"
                                 % recinto),
                    dif, transform, "CCI - GEDI donde ambos existen")

        ruta_csv = os.path.join(TABLAS, "TP2_mapa_AGB_celdas_%s.csv" % recinto)
        with open(ruta_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(filas_csv[0].keys()))
            w.writeheader()
            w.writerows(filas_csv)

        con_gedi = int((gedi != NODATA).sum())
        vg = gedi[gedi != NODATA]
        vc = cci[ambos]
        vd = dif[dif != NODATA]
        decir("%s" % recinto)
        decir("   %d huellas L4A en %d celdas; %d celdas de %d con mediana valida"
              % (usadas, len(celdas), con_gedi, ncol * nfil))
        decir("   GEDI  (celdas con dato): mediana %.1f, p25 %.1f, p75 %.1f Mg/ha"
              % (np.median(vg), np.percentile(vg, 25), np.percentile(vg, 75)))
        decir("   CCI   (mismas celdas):   mediana %.1f, p25 %.1f, p75 %.1f Mg/ha"
              % (np.median(vc), np.percentile(vc, 25), np.percentile(vc, 75)))
        decir("   dif   (CCI - GEDI):      mediana %+.1f, p5 %+.1f, p95 %+.1f Mg/ha"
              % (np.median(vd), np.percentile(vd, 5), np.percentile(vd, 95)))
        decir("")

    decir("COMO SE LEE ESTO")
    decir("   El mapa de GEDI tiene huecos porque GEDI es un muestreo orbital,")
    decir("   no una imagen: donde no paso o no dejo 3 huellas validas, no hay")
    decir("   celda. Rellenar esos huecos es tarea de un MODELO (el TP5), no")
    decir("   del mapa. La diferencia repite en el espacio lo que el anexo")
    decir("   encontro en la tabla: acuerdo en la lenga alta y en la estepa,")
    decir("   CCI por encima en el dosel bajo de ladera. Un mapa continuo no")
    decir("   es mas cierto por ser continuo: es mas modelo.")

    with open(os.path.join(CONTROL, "TP2_17_mapa_biomasa.log"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
