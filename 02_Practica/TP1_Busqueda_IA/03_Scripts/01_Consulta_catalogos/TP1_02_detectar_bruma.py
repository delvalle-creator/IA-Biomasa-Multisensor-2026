#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP1_02_detectar_bruma.py   ---> SEGUNDO script del TP1.

QUE HACE
--------
Detecta escenas opticas contaminadas por BRUMA O HUMO que la mascara de nubes
del propio producto NO marca. Lo hace midiendo la reflectancia de la banda AZUL.

POR QUE EXISTE ESTE SCRIPT
--------------------------
Este filtro se agrego despues de que el problema ocurriera de verdad en este
proyecto, y por eso conviene contar la historia completa.

La escena Sentinel-2 del 09/01/2026 fue elegida como imagen PRE-INCENDIO porque
su banda de clasificacion de escena (SCL) declaraba apenas un 0,4% de nubes.
Paso el filtro sin problemas. Recien al calcular los indices se noto que algo
estaba mal: el NDVI del bosque daba 0,34 cuando en todas las demas fechas daba
0,80. Un bosque no pierde el 60% de su verdor y lo recupera solo.

La causa estaba en la banda azul:

   escena           azul     rojo    NDVI
   25/11/2025      0,024    0,029    0,80     <- normal
   10/01/2024      0,018    0,028    0,81     <- normal
   09/01/2026      0,158    0,124    0,34     <- CONTAMINADA

El azul de esa escena era SIETE VECES mas alto que el de todas las demas.

POR QUE EL AZUL DELATA LA BRUMA
-------------------------------
La bruma y el humo son particulas finas en suspension (aerosoles). Esas
particulas dispersan la luz de manera muy desigual segun la longitud de onda:
dispersan MUCHISIMO las cortas (el azul) y casi nada las largas (el infrarrojo).
Es el mismo fenomeno por el que el cielo se ve azul.

Consecuencia: una escena con bruma tiene el azul inflado, el rojo bastante
inflado, el infrarrojo cercano poco afectado y el infrarrojo de onda corta casi
intacto. Como el NDVI usa el rojo, se desploma. El NBR, que usa el infrarrojo
cercano y el de onda corta, casi no se entera: por eso el NBR aguanta la bruma
y es el indice de eleccion para fuego.

POR QUE LA MASCARA SCL NO LA VE
-------------------------------
La SCL esta entrenada para detectar NUBES: objetos brillantes, opacos y con
bordes definidos. La bruma es semitransparente, difusa y no tiene borde: se
parece mas a un velo que a un objeto. La SCL la deja pasar, o la marca como
'cirros', que casi nadie filtra. En la escena del 09/01/2026 marco 7% de cirros
y nada mas.

Tarrio et al. (2020) documentan estas limitaciones al comparar los algoritmos de
deteccion de nubes disponibles para Sentinel-2.

COMO FUNCIONA EL FILTRO: DOS CRITERIOS, NO UNO
----------------------------------------------
Se compara cada escena contra las DEMAS ESCENAS DEL MISMO SITIO. No contra un
valor absoluto: el azul "normal" de un bosque oscuro y el de una estepa clara
son muy distintos, y un unico umbral serviria para uno y fallaria en el otro.

  Criterio 1 (azul): el azul se dispara por encima de 2,5 veces la mediana del
  sitio  ->  BRUMA. Es el caso grosero, inequivoco.

  Criterio 2 (azul + NDVI): el azul sube algo (mas de 1,5 veces) Y ADEMAS el
  NDVI cae por debajo del 70% de lo habitual del sitio  ->  SOSPECHOSA.

El segundo criterio existe por una razon concreta y comprobada aqui: sobre la
estepa, que es una superficie clara, la misma escena contaminada del 09/01/2026
solo llega a 1,6 veces el azul normal y el primer criterio la deja pasar. Pero
su NDVI cae de 0,25 a 0,15. La combinacion de las dos senales la detecta.

La leccion es general: un umbral unico casi nunca sirve para superficies con
brillos distintos. Conviene comparar cada escena contra su propio sitio.

ENTRADA   ../../../TP3_Datos_Opticos/02_Subsets_SNAP_QGIS/Sentinel_2/<epoca>/<AOI>/*.tif
SALIDA    05_Resultados/04_Tablas/deteccion_bruma.csv

USO (entorno conda 'aoi'):   python TP1_02_detectar_bruma.py
"""
import csv
import glob
import os
import sys

try:
    import numpy as np
    from osgeo import gdal
except ImportError:
    sys.exit("Falta numpy o GDAL. Active el entorno conda 'aoi'.")

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

from configuracion_comun import AOIS_UTM, ruta_practico

gdal.UseExceptions()

S2 = os.path.join(PROYECTO, "TP3_Datos_Opticos", "02_Subsets_SNAP_QGIS", "Sentinel_2")
B2_AZUL, B4_ROJO, B8_NIR, SCL = 1, 3, 7, 11
SCL_MALAS = (0, 1, 3, 8, 9, 10, 11)
FACTOR_BRUMA = 2.5      # azul por encima de esto -> contaminacion grosera
FACTOR_DUDA = 1.5       # azul por encima de esto, con NDVI caido -> sospechosa
CAIDA_NDVI = 0.70       # NDVI por debajo de este % del habitual -> sospechosa


def medir(f):
    """Devuelve (azul, rojo, ndvi) medianos de los pixeles utiles."""
    ds = gdal.Open(f)
    if ds.RasterCount < SCL:
        return None
    azul = ds.GetRasterBand(B2_AZUL).ReadAsArray().astype("float32")
    rojo = ds.GetRasterBand(B4_ROJO).ReadAsArray().astype("float32")
    nir = ds.GetRasterBand(B8_NIR).ReadAsArray().astype("float32")
    scl = ds.GetRasterBand(SCL).ReadAsArray().astype("int16")
    v = (~np.isin(scl, SCL_MALAS)) & (rojo > 0) & (nir > 0)
    if v.sum() < 1000:
        return None
    ndvi = (nir[v] - rojo[v]) / (nir[v] + rojo[v] + 1e-9)
    nubes_scl = 100.0 * np.isin(scl, SCL_MALAS).mean()
    return (float(np.median(azul[v])), float(np.median(rojo[v])),
            float(np.median(ndvi)), nubes_scl)


print(__doc__)
filas = []
for aoi in AOIS_UTM:
    escenas = []
    for f in sorted(glob.glob(os.path.join(S2, "*", aoi, "*.tif"))):
        base = os.path.basename(f)
        fecha = next((t for t in base.split("_") if len(t) == 8 and t.isdigit()), "?")
        m = medir(f)
        if m:
            escenas.append((fecha, base, m))
    if len(escenas) < 3:
        print("%s: hacen falta al menos 3 escenas para comparar" % aoi)
        continue

    ref_azul = float(np.median([e[2][0] for e in escenas]))   # azul tipico del sitio
    ref_ndvi = float(np.median([e[2][2] for e in escenas]))    # NDVI tipico del sitio

    print("=" * 78)
    print("%s   (del sitio: azul %.4f | NDVI %.3f)" % (aoi, ref_azul, ref_ndvi))
    print("=" * 78)
    print("   %-10s %8s %8s %8s %9s   %s" %
          ("fecha", "azul", "rojo", "NDVI", "nubes SCL", "veredicto"))
    for fecha, base, (a, r, nd, nub) in escenas:
        veces = a / ref_azul if ref_azul else 1.0
        caida = nd / ref_ndvi if ref_ndvi else 1.0
        if veces > FACTOR_BRUMA:
            estado = "BRUMA"
            veredicto = "BRUMA (azul %.1fx lo normal)" % veces
        elif veces > FACTOR_DUDA and caida < CAIDA_NDVI:
            estado = "SOSPECHOSA"
            veredicto = "SOSPECHOSA (azul %.1fx y NDVI al %.0f%%)" % (veces, 100 * caida)
        else:
            estado = "limpia"
            veredicto = "limpia"
        print("   %-10s %8.4f %8.4f %8.3f %8.1f%%   %s"
              % (fecha, a, r, nd, nub, veredicto))
        if estado != "limpia":
            print("      >>> la SCL solo marco %.1f%% de nubes: NO la detecto" % nub)
        filas.append([aoi, fecha, "%.4f" % a, "%.4f" % r, "%.3f" % nd,
                      "%.1f" % nub, "%.2f" % veces, "%.2f" % caida, estado])
    print()

sal_dir = ruta_practico("TP1", "05_Resultados", "04_Tablas")
os.makedirs(sal_dir, exist_ok=True)
with open(os.path.join(sal_dir, "deteccion_bruma.csv"), "w", newline="",
          encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["aoi", "fecha", "azul_mediano", "rojo_mediano", "ndvi_mediano",
                "nubes_scl_pct", "azul_veces_lo_normal", "ndvi_fraccion_de_lo_normal",
                "veredicto"])
    w.writerows(filas)

print("Tabla -> 05_Resultados/04_Tablas/deteccion_bruma.csv")
print()
print("QUE HACER CON UNA ESCENA CONTAMINADA")
print("  No se descarta automaticamente: DEPENDE DEL INDICE que se vaya a usar.")
print("    - Para NDVI o EVI (usan el rojo): NO sirve. El rojo esta inflado.")
print("    - Para NBR o dNBR (usan NIR y SWIR2): se puede usar con cuidado, esas")
print("      bandas casi no se afectan. En este proyecto se comprobo: el area")
print("      quemada calculada con la escena con bruma y con la escena limpia")
print("      difiere en menos de un punto porcentual (79,2% contra 80,0%).")
print("  Aun asi, si hay una escena limpia disponible, se usa la limpia.")
print()
print("SIGUIENTE PASO:  python TP1_03_descargar_sentinel.py")
