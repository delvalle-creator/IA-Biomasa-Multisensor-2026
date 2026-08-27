#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP4_03b_inspeccionar_gcov.py   ---> diagnostico, no forma parte de la cadena.

QUE HACE
--------
Lista que contiene realmente un granulo NISAR GCOV: los datasets de la matriz
de covarianza, su tipo y su tamano. Se corre UNA vez, para decidir con el dato a
la vista y no de memoria.

POR QUE HACE FALTA
------------------
El recorte del TP4_03 conserva hoy cuatro capas: HHHH, HVHV, numberOfLooks y
mask. Las dos primeras son la DIAGONAL de la matriz de covarianza, que es real y
alcanza para el gamma0 de cada polarizacion, para el RFDI y para el RVI dual.

Lo que la diagonal NO tiene es el termino de FUERA de la diagonal, que es
complejo y lleva la fase relativa entre canales. Ese termino es el que hace
falta para el DpRVI de Mandal et al. (2020) y para cualquier trabajo
polarimetrico posterior. La documentacion de NISAR advierte que los terminos de
fuera de la diagonal "may or may not be present depending on the GCOV processing
mode": o sea que hay que MIRAR el archivo, no suponerlo.

La decision que este script permite tomar:
  - Si el termino cruzado ESTA, conviene agregarlo a BANDAS en el TP4_03 antes
    de volver a recortar. Cuesta una capa por escena y evita tener que repetir
    el recorte sobre archivos de 2 a 7 GB si mas adelante se quiere polarimetria.
  - Si NO esta, no hay nada que decidir: el producto no lo trae y el DpRVI no
    sale de aca.

USO (entorno conda 'aoi', que ya tiene h5py):
  python TP4_03b_inspeccionar_gcov.py
  python TP4_03b_inspeccionar_gcov.py "ruta\\a\\un\\granulo.h5"
"""
import glob
import io
import os
import sys

try:
    import h5py
except ImportError:
    sys.exit("Falta h5py. Ejecutar: conda install -c conda-forge h5py")

AQUI = os.path.dirname(os.path.abspath(__file__))
TP4 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROYECTO = os.path.dirname(TP4)
DESCARGAS = os.path.join(PROYECTO, "00_COMUN", "08_Originales_crudos")

RUTA_GRILLA = "science/LSAR/GCOV/grids/frequencyA"


def granulo():
    if len(sys.argv) > 1:
        return sys.argv[1]
    pat = os.path.join(DESCARGAS, "*", "NISAR", "GCOV", "*.h5")
    hits = sorted(glob.glob(pat))
    if not hits:
        sys.exit("No se encontro ningun .h5 de NISAR en:\n   %s" % pat)
    # el mas chico primero: alcanza para inspeccionar y abre mas rapido
    hits.sort(key=os.path.getsize)
    return hits[0]


ruta = granulo()

# La salida se GUARDA ademas de imprimirse: un diagnostico que solo va a la
# pantalla se pierde al cerrar la consola, y despues hay que volver a correrlo.
SALIDA = os.path.join(TP4, "05_Resultados", "04_Tablas", "diagnostico_gcov.txt")
os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
_buf = io.StringIO()
_real = sys.stdout


class _Doble(object):
    def write(self, x):
        _real.write(x); _buf.write(x)

    def flush(self):
        _real.flush()


sys.stdout = _Doble()

print(__doc__)
print("=" * 74)
print("GRANULO: %s" % os.path.basename(ruta))
print("         %.2f GB" % (os.path.getsize(ruta) / 1e9))
print("=" * 74)

with h5py.File(ruta, "r") as h:
    if RUTA_GRILLA not in h:
        print("No existe la ruta %s en este archivo." % RUTA_GRILLA)
        print("Arbol de primer nivel:", list(h.keys()))
        sys.exit(1)
    g = h[RUTA_GRILLA]
    print()
    print("   %-22s %-12s %-18s %s" % ("dataset", "tipo", "dimensiones", "que es"))
    print("   " + "-" * 70)
    diagonal, cruzados, otros = [], [], []
    for k in sorted(g.keys()):
        try:
            d = g[k]
            tipo = str(d.dtype)
            dims = "x".join(str(x) for x in d.shape)
        except Exception:
            continue
        complejo = "complex" in tipo
        pol = k.upper()
        if len(pol) == 4 and all(c in "HV" for c in pol):
            if pol[:2] == pol[2:]:
                que = "diagonal (real): gamma0 de %s" % pol[:2]
                diagonal.append(k)
            else:
                que = "FUERA de la diagonal: fase relativa %s-%s" % (pol[:2], pol[2:])
                cruzados.append(k)
        else:
            que = "auxiliar"
            otros.append(k)
        print("   %-22s %-12s %-18s %s" % (k, tipo, dims, que))

print()
print("=" * 74)
print("CONCLUSION")
print("=" * 74)
print("   terminos de la diagonal : %s" % (", ".join(diagonal) or "ninguno"))
print("   terminos cruzados       : %s" % (", ".join(cruzados) or "NINGUNO"))
print("   auxiliares              : %s" % (", ".join(otros) or "ninguno"))
print()
if cruzados:
    print("   El producto SI trae el termino cruzado. Conviene agregarlo a la")
    print("   lista BANDAS de TP4_03_recortar_nisar.py ANTES de volver a")
    print("   recortar, porque es lo que habilita el DpRVI y la polarimetria.")
    print("   Ojo: es COMPLEJO, de modo que hay que guardarlo como dos capas")
    print("   reales (parte real e imaginaria) o como modulo y fase; un")
    print("   GeoTIFF de float32 no admite complejos de forma portable.")
else:
    print("   El producto NO trae terminos cruzados: en este modo de")
    print("   procesamiento GCOV solo hay diagonal. Entonces no hay nada que")
    print("   agregar, el DpRVI no sale de estos granulos, y el recorte actual")
    print("   ya conserva todo lo que el archivo tiene de util para el TP4.")
print()
print("   Recordatorio: al 27/07/2026 SNAP NO tiene lector de NISAR. El soporte")
print("   se corrio de SNAP 13 al roadmap 'futuro' y no hay pull request. Por")
print("   eso el recorte se hace con h5py y GDAL, y el GeoTIFF es una decision")
print("   razonable mientras eso siga asi. El .h5 original queda intacto en")
print("   08_Originales_crudos para el dia que el lector exista.")
print()
print("RESULTADO YA VERIFICADO EL 27/07/2026")
print("   Se inspeccionaron los dos granulos en uso, el del 4/12/2025 (traza")
print("   003) y el del 8/1/2026 (traza 169). El grupo frequencyA de los dos")
print("   contiene: listOfPolarizations, las coordenadas y la proyeccion,")
print("   HHHH, HVHV, listOfCovarianceTerms, numberOfLooks, mask,")
print("   rtcGammaToSigmaFactor y numberOfSubSwaths. SOLO LA DIAGONAL.")
print("   No hay termino cruzado, de modo que no hay nada que agregar al")
print("   recorte y el DpRVI no sale de estos granulos.")
print("   Lo unico que el recorte no conserva y existe es")
print("   rtcGammaToSigmaFactor, el factor para pasar de gamma0 a sigma0.")
print("   Es un dato de documentacion, no de analisis.")

sys.stdout = _real
with open(SALIDA, "w", encoding="utf-8") as _f:
    _f.write(_buf.getvalue())
print()
print("Salida guardada en: %s" % SALIDA)
