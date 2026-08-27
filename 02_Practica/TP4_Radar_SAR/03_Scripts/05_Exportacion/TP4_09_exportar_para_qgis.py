#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_09_exportar_para_qgis.py   ---> NOVENO script del TP4 (visualizacion).

QUE HACE
--------
Convierte los productos de radar a un GeoTIFF listo para abrir en QGIS o en SNAP
sin que se vean negros. Hace tres cosas, y las tres hacen falta:

  1. Pasa gamma0 de LINEAL a DECIBELES.
  2. Declara el valor nodata, para que los bordes vacios no cuenten.
  3. Agrega una banda con el cociente HH-HV, que es la que arma la composicion
     en falso color.

POR QUE HACE FALTA: LAS DOS TRAMPAS
-----------------------------------
TRAMPA 1. Los productos vienen en gamma0 LINEAL, no en dB. Son numeros chicos con
una cola larguisima:

   producto        mediana    maximo
   SAOCOM             0,054     1,82
   NISAR              0,161   202,13
   Sentinel-1 GRD     0,026     1,81

Si abre eso en QGIS, el estiraje por defecto va del minimo al maximo. En NISAR
eso significa repartir toda la escala de grises entre 0 y 202, cuando el 99,9%
de los pixeles esta por debajo de 1. Resultado: una imagen negra con tres puntos
blancos. El estudiante concluye que el archivo esta roto. No lo esta: esta en
lineal, y el radar tiene una cola de dispersores brillantes (techos, rocas,
estructuras) que se lleva toda la escala.

Los decibeles arreglan esto porque comprimen la cola: 10*log10() convierte ese
rango de cinco ordenes de magnitud en una escala de unos 40 dB, aproximadamente
normal, que se estira sola.

TRAMPA 2. SAOCOM y Sentinel-1 no traen nodata declarado. Los ceros del borde del
recorte se cuentan como dato. Como log10(0) es menos infinito, esos pixeles
arruinan cualquier estadistica y cualquier estiraje. Este script los marca.

COMO SE ABRE LO QUE PRODUCE ESTE SCRIPT
---------------------------------------
EN QGIS
  1. Capa -> Agregar capa -> Agregar capa raster, y elija el archivo _dB.tif.
  2. Doble clic en la capa -> Simbologia.
  3. Para ver una polarizacion sola: Banda gris, elija Gamma0_HH_dB o
     Gamma0_HV_dB, y en Valores min/max elija "Corte de conteo acumulativo
     2% - 98%". Ese corte es el que hace visible la imagen.
  4. Para la composicion en falso color: Color multibanda, y ponga
        R = Gamma0_HH_dB     G = Gamma0_HV_dB     B = HH_menos_HV_dB
     con el mismo corte acumulativo 2-98% en cada banda. El bosque sale
     verde-amarillo y la estepa azulada.

  OJO CON UNA COSA. Si usa "Corte de conteo acumulativo" cada capa se estira con
  SUS PROPIOS percentiles. Eso hace que dos sensores distintos se vean parecidos
  aunque tengan 5 dB de diferencia real. Para COMPARAR SAOCOM con NISAR hay que
  fijar los mismos min/max A MANO en las dos capas. Si no, el estiraje le esconde
  justamente lo que quiere ver.

  Y AL ELEGIR ESOS LIMITES, NO RECORTE. Este es un error facil y silencioso: si
  el minimo que fija queda por encima del p2 de alguna capa, esa capa satura, se
  ve de un color plano y sin textura, y usted cree estar viendo un fenomeno
  cuando esta viendo su propia escala. Los percentiles reales de los cuatro
  casos, medidos, son:

     capa                        p2       mediana      p98
     SAOCOM bosque HH         -20,96      -12,71      -8,72
     SAOCOM estepa HH         -26,26      -20,77     -11,14
     NISAR  bosque HH         -16,53       -7,92      -2,52
     NISAR  estepa HH         -22,27      -15,97      -5,25
     SAOCOM bosque HV         -27,96      -17,75     -13,78
     SAOCOM estepa HV         -34,39      -29,42     -17,69
     NISAR  bosque HV         -22,64      -13,16      -7,69
     NISAR  estepa HV         -28,63      -23,10     -11,61

  Limites que abarcan TODO sin recortar nada:  HH de -28 a -2 dB
                                               HV de -36 a -7 dB

EN SNAP
  Para Sentinel-1 y SAOCOM conviene abrir el .dim (BEAM-DIMAP) que esta al lado
  del .tif, NO el GeoTIFF: el .dim conserva los metadatos del producto (orbita,
  calibracion, geocodificacion) y el GeoTIFF los pierde. Para NISAR y PALSAR-2
  solo hay GeoTIFF, porque no salieron de SNAP.
  Una vez abierto: clic derecho en la banda -> Properties para ver la unidad, y
  Colour Manipulation para el estiraje. SNAP ya aplica un 2,5-97,5% por defecto,
  asi que suele verse bien de entrada.

  En SNAP el .dim de Sentinel-1 y SAOCOM ya trae gamma0 en LINEAL igual que el
  .tif. Si quiere verlo en dB sin tocar el dato: clic derecho sobre la banda ->
  "Linear to/from dB". Crea una banda virtual, no duplica el archivo.

ENTRADA   02_Subsets_SNAP_QGIS/<sensor>/<epoca>/<AOI>/*/*.tif   (gamma0 LINEAL)
SALIDA    05_Resultados/02_Rasters/<sensor>_<fecha>_<AOI>_dB.tif
             banda 1: Gamma0_<pol1>_dB
             banda 2: Gamma0_<pol2>_dB
             banda 3: HH_menos_HV_dB   (o VV_menos_VH_dB en Sentinel-1)

USO (entorno conda 'aoi'):   python TP4_09_exportar_para_qgis.py
"""
import glob
import os
import sys

try:
    import numpy as np
    from osgeo import gdal, osr
except ImportError:
    sys.exit("Falta numpy o GDAL. Active el entorno conda 'aoi'.")

AQUI = os.path.dirname(os.path.abspath(__file__))
TP4 = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROYECTO = os.path.dirname(TP4)
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

from configuracion_comun import AOIS_UTM, EPSG, PIXEL      # noqa: E402

gdal.UseExceptions()
INSUMOS = os.path.join(TP4, "02_Subsets_SNAP_QGIS")
SALIDA = os.path.join(TP4, "05_Resultados", "02_Rasters")
NODATA = -99.0            # en dB: ningun gamma0 real llega ahi

FUENTES = [
    ("SAOCOM", "SAOCOM/*/%s/*/*.tif"),
    ("NISAR", "NISAR/*/%s/*/NISAR_GCOV_*.tif"),
    ("PALSAR2", "ALOS_PALSAR_2/*/%s/*/PALSAR2_*.tif"),
    ("S1_GRD", "Sentinel_1/*/%s/S1_GRD/*.tif"),
]


def a_db(a):
    """gamma0 lineal -> dB, marcando como nodata todo lo que no sea positivo."""
    return np.where(a > 0, 10 * np.log10(a, where=a > 0), NODATA).astype("float32")


def escribir(ruta, capas, aoi):
    xmin, ymin, xmax, ymax = AOIS_UTM[aoi]
    ny, nx = capas[0][1].shape
    ds = gdal.GetDriverByName("GTiff").Create(
        ruta, nx, ny, len(capas), gdal.GDT_Float32,
        options=["COMPRESS=DEFLATE", "TILED=YES"])
    ds.SetGeoTransform((xmin, PIXEL, 0, ymax, 0, -PIXEL))
    sr = osr.SpatialReference(); sr.ImportFromEPSG(EPSG)
    ds.SetProjection(sr.ExportToWkt())
    for i, (nom, arr) in enumerate(capas, 1):
        b = ds.GetRasterBand(i)
        b.WriteArray(arr)
        b.SetDescription(nom)
        b.SetNoDataValue(NODATA)          # <- la trampa 2, resuelta
        b.SetUnitType("dB")
    ds.FlushCache(); ds = None


print(__doc__)
os.makedirs(SALIDA, exist_ok=True)
n_ok = 0
print("=" * 80)
print("%-10s %-14s %-22s %8s %8s" % ("sensor", "aoi", "salida", "med pol1", "med pol2"))
print("=" * 80)
for etq, patron in FUENTES:
    for aoi in AOIS_UTM:
        for f in sorted(glob.glob(os.path.join(INSUMOS, patron % aoi))):
            if "_mask" in f or "_nativo" in f:
                continue
            ds = gdal.Open(f)
            if ds.RasterCount < 2:
                continue
            n1 = ds.GetRasterBand(1).GetDescription() or "banda1"
            n2 = ds.GetRasterBand(2).GetDescription() or "banda2"
            a1 = a_db(ds.GetRasterBand(1).ReadAsArray().astype("float64"))
            a2 = a_db(ds.GetRasterBand(2).ReadAsArray().astype("float64"))
            val = (a1 > NODATA) & (a2 > NODATA)
            coc = np.where(val, a2 - a1, NODATA).astype("float32")   # co-pol menos cruzada
            # el orden de las bandas cambia entre sensores: en S1 la 1 es la cruzada
            if "VH" in n1 or "HV" in n1:
                coc = np.where(val, a2 - a1, NODATA).astype("float32")
                nom_coc = "%s_menos_%s_dB" % (n2.split("_")[-1], n1.split("_")[-1])
            else:
                coc = np.where(val, a1 - a2, NODATA).astype("float32")
                nom_coc = "%s_menos_%s_dB" % (n1.split("_")[-1], n2.split("_")[-1])
            base = os.path.basename(f).replace(".tif", "")
            sal = os.path.join(SALIDA, "%s_%s_dB.tif" % (base, aoi))
            escribir(sal, [(n1 + "_dB", a1), (n2 + "_dB", a2), (nom_coc, coc)], aoi)
            n_ok += 1
            print("%-10s %-14s %-22s %8.2f %8.2f"
                  % (etq, aoi[:6], os.path.basename(sal)[:22],
                     float(np.median(a1[val])), float(np.median(a2[val]))))

print()
print("Listo. %d archivos -> 05_Resultados/02_Rasters/" % n_ok)
print()
print("PARA COMPARAR DOS SENSORES, FIJE LOS MISMOS MIN/MAX EN LAS DOS CAPAS:")
print("   HH  : de -28 a -2 dB        HV  : de -36 a -7 dB")
print("   (esos limites abarcan el rango real de los cuatro casos: no recortan nada)")
print("Con esos valores va a VER que NISAR es mas brillante que SAOCOM (unos 5 dB")
print("de diferencia de calibracion y de angulo). Si deja que cada capa se estire")
print("sola, esa diferencia desaparece y las dos se ven iguales.")
print()
print("COMPOSICION EN FALSO COLOR (Color multibanda):")
print("   R = Gamma0_HH_dB    G = Gamma0_HV_dB    B = HH_menos_HV_dB")
print("   bosque -> verde-amarillo (mucho HV: volumen de ramas)")
print("   estepa -> azulado       (poco HV: superficie)")
