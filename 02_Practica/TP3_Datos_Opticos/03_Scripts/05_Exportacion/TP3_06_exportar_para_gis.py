#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP3_06_exportar_para_gis.py   ---> SEXTO y ultimo script del TP3.

QUE HACE
--------
Deja los resultados del practico listos para abrir en QGIS: escribe los estilos
(.qml) de cada raster y vectoriza el area quemada por clase de severidad.

POR QUE HACE FALTA
------------------
Los scripts anteriores producen GeoTIFF correctos, pero QGIS no sabe como
mostrarlos, y sin estilo no se ve nada util:

  - El raster de SEVERIDAD es CATEGORICO: sus valores son 1 a 7, que son codigos
    de clase, no cantidades. QGIS lo abre por omision como banda gris con un
    estiraje continuo, y usted ve siete tonos de gris casi identicos. La paleta de
    Key y Benson lo convierte en un mapa legible.
  - El dNBR es CONTINUO y DIVERGENTE: tiene un cero que significa algo (sin
    cambio). Necesita una paleta divergente centrada en cero, no un degradado
    lineal.
  - Los indices salen en Float32 sin nodata declarado, y los NaN del enmascarado
    de nubes arruinan el estiraje automatico.

Un resultado que solo el script puede leer no es un resultado: es una promesa.

QUE PRODUCE
-----------
   05_Resultados/03_Vectores/TP3_incendio.gpkg
        severidad_bosque      poligonos por clase, con su superficie en hectareas
        severidad_estepa
   05_Resultados/02_Rasters/*.qml        estilos de severidad, dNBR e indices

COMO SE USA EN QGIS
-------------------
  RASTER. Cargue severidad_<AOI>.tif desde 05_Resultados/02_Rasters/incendio/. Propiedades ->
  Simbologia -> Estilo -> Cargar estilo -> severidad.qml. Va a ver las siete clases
  con los colores del estandar: verde el sin cambio, amarillo la severidad baja,
  naranja las moderadas, rojo oscuro la alta.

  Para el dNBR, cargue dNBR_<AOI>.tif y aplique dnbr.qml: paleta divergente
  centrada en cero, de -0,3 a 1,0.

  VECTOR. Cargue TP3_incendio.gpkg. Cada poligono tiene su clase y sus hectareas.
  Sirve para calcular superficies por cuenca, cruzar con catastro o exportar a un
  informe. Un raster no se puede intersecar con un catastro; un poligono si.

  LA VERIFICACION QUE HAY QUE HACER. Cargue encima las huellas GEDI del TP2
  (05_Resultados/03_Vectores/TP2_GEDI.gpkg del TP2). Va a ver cuales quedaron
  dentro del area quemada. Ese cruce es el que hace el script TP3_05 con numeros:
  ahora lo puede mirar antes de creerle.

ENTRADA   05_Resultados/02_Rasters/incendio/<AOI>/severidad_<AOI>.tif
          05_Resultados/02_Rasters/incendio/<AOI>/dNBR_<AOI>.tif
SALIDA    05_Resultados/03_Vectores/TP3_incendio.gpkg
          05_Resultados/02_Rasters/*.qml

USO (entorno conda 'aoi'):   python TP3_06_exportar_para_gis.py
"""
import glob
import os
import sys

try:
    from osgeo import gdal, ogr, osr
except ImportError:
    sys.exit("Falta GDAL. Active el entorno conda 'aoi'.")

AQUI = os.path.dirname(os.path.abspath(__file__))
TP3 = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROYECTO = os.path.dirname(TP3)
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

from configuracion_comun import AOIS_UTM, EPSG      # noqa: E402

gdal.UseExceptions(); ogr.UseExceptions()
RESULTADOS = os.path.join(TP3, "05_Resultados")
VECT = os.path.join(RESULTADOS, "03_Vectores")
RAST = os.path.join(RESULTADOS, "02_Rasters")

# Los colores son los del estandar de Key y Benson (USGS), no una eleccion estetica.
SEVERIDAD = [(1, "Regeneracion alta", "#7fbc41"), (2, "Regeneracion baja", "#b8e186"),
             (3, "Sin cambio", "#3a8c3a"),
             (4, "Severidad baja", "#ffeda0"), (5, "Severidad moderada-baja", "#feb24c"),
             (6, "Severidad moderada-alta", "#f4622e"), (7, "Severidad alta", "#a50f15")]


def rgb(h):
    return ",".join(str(int(h[i:i+2], 16)) for i in (1, 3, 5))


def qml_severidad(ruta):
    items = "".join('<paletteEntry value="%d" color="%s" label="%s" alpha="255"/>'
                    % (v, c, l) for v, l, c in SEVERIDAD)
    open(ruta, "w", encoding="utf-8").write(
        '<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">'
        '<pipe><rasterrenderer type="paletted" band="1" opacity="1" alphaBand="-1" nodataColor="">'
        '<colorPalette>%s</colorPalette></rasterrenderer></pipe></qgis>' % items)


def qml_dnbr(ruta):
    """Paleta DIVERGENTE centrada en cero. El cero del dNBR significa 'sin cambio':
    una paleta lineal lo escondería en el medio de un degradado."""
    P = [(-0.30, "#1a9850"), (-0.10, "#91cf60"), (0.00, "#ffffbf"),
         (0.27, "#fee08b"), (0.44, "#fc8d59"), (0.66, "#d73027"), (1.00, "#7f0000")]
    items = "".join('<item value="%f" color="%s" label="%.2f" alpha="255"/>' % (v, c, v)
                    for v, c in P)
    open(ruta, "w", encoding="utf-8").write(
        '<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">'
        '<pipe><rasterrenderer type="singlebandpseudocolor" band="1" opacity="1" '
        'classificationMin="-0.3" classificationMax="1">'
        '<rastershader><colorrampshader colorRampType="INTERPOLATED" clip="0">%s'
        '</colorrampshader></rastershader></rasterrenderer></pipe></qgis>' % items)


def qml_indice(ruta, lo, hi):
    P = [(lo, "#a50026"), ((lo+hi)/2, "#ffffbf"), (hi, "#006837")]
    items = "".join('<item value="%f" color="%s" label="%.2f" alpha="255"/>' % (v, c, v)
                    for v, c in P)
    open(ruta, "w", encoding="utf-8").write(
        '<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">'
        '<pipe><rasterrenderer type="singlebandpseudocolor" band="1" opacity="1" '
        'classificationMin="%f" classificationMax="%f">'
        '<rastershader><colorrampshader colorRampType="INTERPOLATED" clip="0">%s'
        '</colorrampshader></rastershader></rasterrenderer></pipe></qgis>' % (lo, hi, items))


def vectorizar(tif, ds_out, nombre):
    """Convierte el raster de severidad en poligonos, uno por mancha y clase."""
    src = gdal.Open(tif)
    banda = src.GetRasterBand(1)
    sr = osr.SpatialReference(); sr.ImportFromEPSG(EPSG)
    lyr = ds_out.CreateLayer(nombre, sr, ogr.wkbPolygon,
                             options=["DESCRIPTION=Severidad del incendio por clase"])
    lyr.CreateField(ogr.FieldDefn("clase", ogr.OFTInteger))
    gdal.Polygonize(banda, banda.GetMaskBand(), lyr, 0, [])
    # etiqueta y superficie
    lyr.CreateField(ogr.FieldDefn("severidad", ogr.OFTString))
    lyr.CreateField(ogr.FieldDefn("hectareas", ogr.OFTReal))
    etq = {v: l for v, l, _ in SEVERIDAD}
    lyr.StartTransaction()
    n = 0
    for f in lyr:
        c = f.GetField("clase")
        if c in (0, None):
            lyr.DeleteFeature(f.GetFID()); continue
        f.SetField("severidad", etq.get(c, "?"))
        f.SetField("hectareas", round(f.GetGeometryRef().GetArea() / 10000.0, 3))
        lyr.SetFeature(f); n += 1
    lyr.CommitTransaction()
    return n


def qml_vector(ruta):
    cats = "".join('<category render="true" symbol="%d" value="%s" label="%s"/>'
                   % (i, l, l) for i, (v, l, c) in enumerate(SEVERIDAD))
    sims = "".join('<symbol name="%d" type="fill" alpha="0.85" force_rhr="0" clip_to_extent="1">'
                   '<layer class="SimpleFill" enabled="1" pass="0" locked="0">'
                   '<prop k="color" v="%s,220"/><prop k="outline_color" v="60,60,60,90"/>'
                   '<prop k="outline_width" v="0.06"/></layer></symbol>' % (i, rgb(c))
                   for i, (v, l, c) in enumerate(SEVERIDAD))
    open(ruta, "w", encoding="utf-8").write(
        '<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">'
        '<renderer-v2 type="categorizedSymbol" attr="severidad" symbollevels="0" forceraster="0">'
        '<categories>%s</categories><symbols>%s</symbols></renderer-v2></qgis>' % (cats, sims))


print(__doc__)
os.makedirs(VECT, exist_ok=True); os.makedirs(RAST, exist_ok=True)

# --------------------------------------------------- estilos
qml_severidad(os.path.join(RAST, "severidad.qml"))
qml_dnbr(os.path.join(RAST, "dnbr.qml"))
for nom, lo, hi in (("ndvi", 0.0, 0.9), ("evi", 0.0, 0.7), ("ndmi", -0.2, 0.5), ("nbr", -0.4, 0.8)):
    qml_indice(os.path.join(RAST, "%s.qml" % nom), lo, hi)
qml_vector(os.path.join(VECT, "severidad_poligonos.qml"))
print("Estilos escritos en 05_Resultados/02_Rasters/ y 03_Vectores/")

# --------------------------------------------------- vectorizacion
gpkg = os.path.join(VECT, "TP3_incendio.gpkg")
if os.path.exists(gpkg):
    os.remove(gpkg)
tifs = sorted(glob.glob(os.path.join(RESULTADOS, "02_Rasters", "incendio", "*", "severidad_*.tif")))
if not tifs:
    print()
    print("No hay rasters de severidad todavia.")
    print("Ejecute antes:  python TP3_04_dnbr_incendio.py")
    print("Los estilos ya quedaron escritos: sirven igual cuando los genere.")
    sys.exit(0)

ds = ogr.GetDriverByName("GPKG").CreateDataSource(gpkg)
print()
print("=" * 66)
print("%-28s %12s" % ("capa", "poligonos"))
print("=" * 66)
for t in tifs:
    aoi = os.path.basename(t).replace("severidad_", "").replace(".tif", "")
    n = vectorizar(t, ds, "severidad_%s" % aoi.split("_")[0].lower())
    print("%-28s %12d" % ("severidad_%s" % aoi.split("_")[0].lower(), n))
ds = None

print()
print("Listo. -> 05_Resultados/03_Vectores/TP3_incendio.gpkg")
print()
print("QUE HACER EN QGIS")
print("  1. Cargue severidad_<AOI>.tif y aplique 02_Rasters/severidad.qml.")
print("     Sin ese estilo vera seis grises casi iguales: los valores 1 a 6 son")
print("     CODIGOS de clase, no cantidades.")
print("  2. Cargue dNBR_<AOI>.tif con dnbr.qml (paleta divergente en cero).")
print("  3. Cargue TP3_incendio.gpkg: cada poligono trae su clase y sus hectareas.")
print("  4. VERIFIQUE: agregue encima las huellas GEDI del TP2 y mire cuales")
print("     quedaron dentro del area quemada. Ese cruce es el que hace el TP3_05.")
