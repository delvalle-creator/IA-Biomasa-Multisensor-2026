# -*- coding: utf-8 -*-
"""
lector_bap.py  ---> lectura de los shapefiles de cobertura BAP / SNMBN 2017.

POR QUE EXISTE ESTE MODULO
--------------------------
Un shapefile guarda cada poligono como una lista de anillos sin decir cual es el
contorno exterior y cual es un hueco. La convencion es el sentido de giro: los
anillos exteriores van en sentido horario y los huecos en sentido antihorario.
Si eso se ignora, un lago dentro de un poligono de lenga se cuenta como lenga y
la superficie sale inflada.

El control esta al final del modulo: la suma de las superficies reconstruidas
tiene que dar 225,000000 km2 en los dos recintos, que es la superficie exacta
del AOI. Da.

DEPENDENCIAS   pyshp (import shapefile) y shapely. Las dos estan en el entorno
               conda 'aoi'.
"""
import shapefile
from shapely.geometry import Polygon, MultiPolygon
from shapely.validation import make_valid


def _area_con_signo(pts):
    """Formula del cordon de zapato. Negativa = sentido horario = anillo exterior."""
    s = 0.0
    for i in range(len(pts) - 1):
        s += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
    return s / 2.0


def _geometria(shape):
    """Reconstruye un poligono de shapefile respetando sus anillos interiores."""
    cortes = list(shape.parts) + [len(shape.points)]
    anillos = [shape.points[cortes[i]:cortes[i + 1]] for i in range(len(cortes) - 1)]

    exteriores, huecos = [], []
    for a in anillos:
        if len(a) < 4:                      # un anillo necesita 4 vertices (cierra)
            continue
        (exteriores if _area_con_signo(a) < 0 else huecos).append(a)
    if not exteriores:                      # el shape entero venia antihorario
        exteriores, huecos = huecos, []

    partes = []
    for e in exteriores:
        contorno = Polygon(e)
        dentro = [h for h in huecos
                  if contorno.contains(Polygon(h).representative_point())]
        p = Polygon(e, dentro)
        partes.append(p if p.is_valid else make_valid(p))

    if len(partes) == 1:
        g = partes[0]
    else:
        g = MultiPolygon([q for p in partes
                          for q in (p.geoms if p.geom_type == "MultiPolygon" else [p])])
    return g if g.is_valid else make_valid(g)


def leer(ruta_sin_extension):
    """Devuelve (lista de geometrias shapely, lista de diccionarios de atributos)."""
    r = shapefile.Reader(ruta_sin_extension)
    campos = [c[0] for c in r.fields[1:]]
    geometrias, atributos = [], []
    for sr in r.iterShapeRecords():
        g = _geometria(sr.shape)
        if g.is_empty:
            continue
        geometrias.append(g)
        atributos.append(dict(zip(campos, list(sr.record))))
    return geometrias, atributos
