#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP2_08_exportar_para_gis.py   ---> OCTAVO y ultimo script del TP2.

QUE HACE
--------
Convierte las huellas GEDI de CSV a un GeoPackage con estilos, para que usted
pueda ABRIRLAS EN QGIS, verlas sobre el terreno y comprobar con sus propios ojos
lo que los scripts anteriores le dijeron con numeros.

POR QUE ESTE SCRIPT EXISTE, Y POR QUE SE AGREGO DESPUES
------------------------------------------------------
Este practico tenia un defecto grave, y conviene decirlo con todas las letras
porque la leccion vale mas que el script.

Los siete scripts anteriores calculaban bien: filtraban por calidad, por
pendiente, cruzaban con el DEM, y le informaban el resultado en tablas y en
graficos. Pero el unico que podia LEER esos resultados era el propio script. Los
footprints quedaban en un CSV: usted no podia verlos sobre un mapa, ni cliquear
uno para ver su altura, ni superponerlos al relieve para comprobar que los
descartados por pendiente estan efectivamente en las laderas.

Es decir: el script le pedia que le creyera. Y eso contradice exactamente lo que
este curso enseña, que es no creerle a nadie sin verificar. Una herramienta que
produce evidencia que solo ella puede leer no es una herramienta: es un oraculo.

Un dato geografico se audita en un SIG. Por eso este script existe.

QUE PRODUCE
-----------
Un GeoPackage (.gpkg) con cinco capas y tres estilos (.qml):

   gedi_aceptados_bosque      1.025 puntos    los que sobrevivieron los filtros
   gedi_descartados_bosque   5.263 puntos    con el MOTIVO de cada rechazo
   gedi_aceptados_estepa     4.041 puntos
   gedi_descartados_estepa   7.181 puntos
   aoi_recintos                 2 poligonos los recuadros de 15 x 15 km

Se eligio GeoPackage y no shapefile por tres razones: guarda varias capas en un
solo archivo, no trunca los nombres de campo a diez caracteres, y no tiene el
limite de 2 GB. El shapefile es un formato de 1998; conviene dejarlo.

QUE TIENE QUE MIRAR EN QGIS (ESTO ES PARTE DEL PRACTICO)
--------------------------------------------------------
1. Cargue gedi_aceptados_* con su estilo: los puntos salen coloreados por altura
   del dosel. Va a ver de un vistazo que el bosque tiene huellas altas y la
   estepa no. Eso es el control del proyecto, hecho mapa.

2. Cargue gedi_descartados_* y agregue encima el DEM
   (00_COMUN/03_Topografia/DEM/). Los descartados por pendiente tienen que caer
   en las laderas. Si no caen, algo esta mal en el filtro. Compruebelo: no
   alcanza con que el script diga que filtro bien.

3. Mire la densidad espacial. GEDI no cubre el terreno: son lineas de disparos a
   lo largo de la orbita, con huecos enormes entre ellas. En el mapa eso es
   evidente y en una tabla no. Esa es la limitacion de muestreo que usted tiene
   que declarar en su informe, y ahora la puede mostrar en vez de contarla.

4. Cliquee una huella con la herramienta de informacion. Va a ver todos sus
   atributos: rh95, rh98, sensitivity, calidad. Ese es el dato crudo detras de
   cada punto de las figuras del practico.

5. Cuando llegue al TP3, superponga estas huellas al dNBR. Va a ver cuales
   quedaron dentro del area quemada. Ese cruce es el que hace el TP3_05, y ahora
   lo puede verificar visualmente antes de creerle.

SOBRE EL TAMANO DE LA HUELLA
----------------------------
Se exportan como PUNTOS, que es el centro del disparo. La huella real es un
circulo de unos 25 m de diametro. Si quiere verla a escala, en QGIS use
Simbologia -> tamano 25 -> unidades "Metros a escala". Es un detalle que importa
cuando compare con pixeles de 10 m: una huella GEDI cubre unos 6 pixeles de
Sentinel-2, no uno.

ENTRADA   05_Resultados/04_Tablas/*.csv
          05_Resultados/04_Tablas/*.csv
SALIDA    05_Resultados/03_Vectores/TP2_GEDI.gpkg
          05_Resultados/03_Vectores/*.qml   (estilos: cargarlos con Estilo -> Cargar estilo)

USO (entorno conda 'aoi'):   python TP2_08_exportar_para_gis.py
"""
import csv
import os
import sys

try:
    from osgeo import ogr, osr
except ImportError:
    sys.exit("Falta GDAL. Active el entorno conda 'aoi'.")

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROYECTO = os.path.dirname(TP2)
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

from configuracion_comun import AOIS_UTM, EPSG          # noqa: E402

ogr.UseExceptions()
SUBSETS = os.path.join(TP2, "04_Tablas_de_trabajo")
RESULTADOS = os.path.join(TP2, "05_Resultados")
SALIDA = os.path.join(RESULTADOS, "03_Vectores")
GPKG = os.path.join(SALIDA, "TP2_GEDI.gpkg")

# que campos son numeros. El resto va como texto.
REALES = {"rh25", "rh50", "rh75", "rh95", "rh98", "sensitivity", "elev_lowestmode",
          "lat", "lon", "pendiente_grados", "cover", "pai", "fhd_normal",
          "agbd_Mg_ha", "agbd_se_Mg_ha"}
ENTEROS = {"l2a_quality_flag_rel3", "degrade_flag"}


def tipo_de(campo):
    if campo in REALES:
        return ogr.OFTReal
    if campo in ENTEROS:
        return ogr.OFTInteger
    return ogr.OFTString


def leer(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def capa_puntos(ds, nombre, filas, desc):
    sr = osr.SpatialReference(); sr.ImportFromEPSG(EPSG)
    lyr = ds.CreateLayer(nombre, sr, ogr.wkbPoint,
                         options=["DESCRIPTION=%s" % desc])
    campos = [k for k in filas[0] if k not in ("este_utm19s", "norte_utm19s")]
    for k in campos:
        lyr.CreateField(ogr.FieldDefn(k, tipo_de(k)))
    lyr.StartTransaction()
    for r in filas:
        f = ogr.Feature(lyr.GetLayerDefn())
        for k in campos:
            v = r.get(k)
            if v is None or v == "":
                continue
            try:
                if tipo_de(k) == ogr.OFTReal:
                    f.SetField(k, float(v))
                elif tipo_de(k) == ogr.OFTInteger:
                    f.SetField(k, int(float(v)))
                else:
                    f.SetField(k, v)
            except (TypeError, ValueError):
                pass
        p = ogr.Geometry(ogr.wkbPoint)
        p.AddPoint(float(r["este_utm19s"]), float(r["norte_utm19s"]))
        f.SetGeometry(p)
        lyr.CreateFeature(f)
        f = None
    lyr.CommitTransaction()
    return lyr.GetFeatureCount()


def capa_recintos(ds):
    sr = osr.SpatialReference(); sr.ImportFromEPSG(EPSG)
    lyr = ds.CreateLayer("aoi_recintos", sr, ogr.wkbPolygon,
                         options=["DESCRIPTION=Recintos de 15 x 15 km"])
    lyr.CreateField(ogr.FieldDefn("aoi", ogr.OFTString))
    lyr.CreateField(ogr.FieldDefn("lado_km", ogr.OFTInteger))
    for aoi, (x0, y0, x1, y1) in AOIS_UTM.items():
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetField("aoi", aoi); f.SetField("lado_km", 15)
        anillo = ogr.Geometry(ogr.wkbLinearRing)
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)):
            anillo.AddPoint(x, y)
        pol = ogr.Geometry(ogr.wkbPolygon); pol.AddGeometry(anillo)
        f.SetGeometry(pol); lyr.CreateFeature(f); f = None
    return lyr.GetFeatureCount()


# ------------------------------------------------------------------ estilos
def estilo_aceptados(ruta):
    """Puntos graduados por altura del dosel. Los cortes son los mismos que usan
    las tablas del TP3 y del TP4, para que las tres cosas se puedan comparar."""
    R = [(0, 3, "#d9f0a3", "0 - 3 m (matorral)"), (3, 6, "#addd8e", "3 - 6 m"),
         (6, 9, "#78c679", "6 - 9 m"), (9, 12, "#41ab5d", "9 - 12 m"),
         (12, 15, "#238443", "12 - 15 m"), (15, 18, "#006837", "15 - 18 m"),
         (18, 21, "#00441b", "18 - 21 m"), (21, 25, "#00301a", "21 - 25 m (aqui satura el NDVI)"),
         (25, 45, "#001a0d", "25 m o mas (bosque maduro)")]
    def sim(i, c):
        rgb = ",".join(str(int(c[j:j+2], 16)) for j in (1, 3, 5))
        return ('<symbol name="%d" type="marker" alpha="1" force_rhr="0" clip_to_extent="1">'
                '<layer class="SimpleMarker" enabled="1" pass="0" locked="0">'
                '<prop k="name" v="circle"/><prop k="color" v="%s,255"/>'
                '<prop k="outline_color" v="35,35,35,180"/><prop k="outline_width" v="0.2"/>'
                '<prop k="size" v="2.4"/><prop k="size_unit" v="MM"/></layer></symbol>' % (i, rgb))
    rangos = "".join('<range render="true" symbol="%d" lower="%f" upper="%f" label="%s"/>'
                     % (i, lo, hi, lab) for i, (lo, hi, c, lab) in enumerate(R))
    sims = "".join(sim(i, c) for i, (lo, hi, c, lab) in enumerate(R))
    open(ruta, "w", encoding="utf-8").write(
        '<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">'
        '<renderer-v2 type="graduatedSymbol" attr="rh95" graduatedMethod="GraduatedColor" '
        'symbollevels="0" forceraster="0" enableorderby="0">'
        '<ranges>%s</ranges><symbols>%s</symbols></renderer-v2></qgis>' % (rangos, sims))


def estilo_descartados(ruta, valores):
    """Puntos categorizados por el motivo del rechazo.

    OJO: los valores NO se inventan, se leen del propio dato. Una version previa
    de este estilo usaba etiquetas supuestas ('calidad', 'pendiente') y QGIS
    mostraba todo gris bajo 'otros', porque los valores reales son frases
    completas. Es un error silencioso y muy facil de cometer."""
    COL = {"calidad": "#b30000", "degradado": "#e6550d",
           "sensibilidad": "#fdae61", "pendiente": "#fee08b"}
    def color(v):
        for k, c in COL.items():
            if v.startswith(k):
                return c
        return "#999999"
    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
    def sim(i, c):
        rgb = ",".join(str(int(c[j:j+2], 16)) for j in (1, 3, 5))
        return ('<symbol name="%d" type="marker" alpha="1" force_rhr="0" clip_to_extent="1">'
                '<layer class="SimpleMarker" enabled="1" pass="0" locked="0">'
                '<prop k="name" v="cross2"/><prop k="color" v="%s,255"/>'
                '<prop k="outline_color" v="%s,255"/><prop k="outline_width" v="0.3"/>'
                '<prop k="size" v="1.8"/><prop k="size_unit" v="MM"/></layer></symbol>' % (i, rgb, rgb))
    cats = "".join('<category render="true" symbol="%d" value="%s" label="%s"/>'
                   % (i, esc(v), esc(v)) for i, v in enumerate(valores))
    sims = "".join(sim(i, color(v)) for i, v in enumerate(valores))
    open(ruta, "w", encoding="utf-8").write(
        '<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">'
        '<renderer-v2 type="categorizedSymbol" attr="motivo" symbollevels="0" forceraster="0">'
        '<categories>%s</categories><symbols>%s</symbols></renderer-v2></qgis>' % (cats, sims))


def estilo_recintos(ruta):
    open(ruta, "w", encoding="utf-8").write(
        '<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">'
        '<renderer-v2 type="singleSymbol" symbollevels="0" forceraster="0"><symbols>'
        '<symbol name="0" type="fill" alpha="1" force_rhr="0" clip_to_extent="1">'
        '<layer class="SimpleFill" enabled="1" pass="0" locked="0">'
        '<prop k="style" v="no"/><prop k="outline_color" v="29,53,87,255"/>'
        '<prop k="outline_width" v="0.8"/><prop k="outline_style" v="solid"/>'
        '</layer></symbol></symbols></renderer-v2></qgis>')


print(__doc__)
os.makedirs(SALIDA, exist_ok=True)
if os.path.exists(GPKG):
    os.remove(GPKG)
ds = ogr.GetDriverByName("GPKG").CreateDataSource(GPKG)
if ds is None:
    sys.exit("No se pudo crear el GeoPackage. Revise permisos en %s" % SALIDA)

print("=" * 72)
print("%-32s %10s" % ("capa", "entidades"))
print("=" * 72)
motivos = set()
for aoi in AOIS_UTM:
    corto = aoi.split("_")[0].lower()
    # QUE SE EXPORTA, Y POR QUE ASI.
    #
    # Los "aceptados" son los DEFINITIVOS: los que sobrevivieron calidad Y
    # pendiente, y que ya traen las metricas de estructura y la biomasa. Antes
    # este script exportaba la salida del TP2_03, es decir, huellas que el filtro
    # de pendiente ya habia rechazado, y ademas sin las columnas de pendiente,
    # cover, pai ni agbd. Con eso era IMPOSIBLE hacer la verificacion que el
    # propio script pide mas abajo: comprobar en el mapa que los descartados por
    # pendiente caen sobre las laderas.
    #
    # Por eso ahora son tres capas por sitio, y no dos: los definitivos, los
    # descartados por calidad y los descartados por pendiente, que son cosas
    # distintas y se ven distinto en el mapa.
    sub = "01_Bosque" if "BOSQUE" in aoi else "02_Estepa"
    fuentes = (
        # Se lee biomasa_<AOI>.csv y no el _con_estructura: tiene las MISMAS
        # huellas mas las columnas agbd_Mg_ha y agbd_se_Mg_ha. Sin ellas no se
        # puede hacer en QGIS la comprobacion que este mismo script sugiere:
        # que la biomasa alta caiga en el bosque y no en la estepa.
        # Si el TP2_07 todavia no corrio, se cae al archivo anterior.
        ("aceptados", os.path.join(RESULTADOS, "04_Tablas", "biomasa_%s.csv" % aoi)
                      if os.path.exists(os.path.join(RESULTADOS, "04_Tablas",
                                                     "biomasa_%s.csv" % aoi))
                      else os.path.join(SUBSETS, sub,
                                        "GEDI_%s_validos_con_estructura.csv" % aoi)),
        ("descartados", os.path.join(RESULTADOS,
                                     "04_Tablas/GEDI_L2A_%s_descartados.csv" % aoi)),
        ("descartados_pendiente", os.path.join(RESULTADOS,
                                  "04_Tablas/GEDI_%s_descartados_pendiente.csv" % aoi)),
    )
    for estado, ruta in fuentes:
        filas = leer(ruta)
        if not filas:
            print("   falta %s de %s: ejecute antes los scripts 03, 05, 06 y 07"
                  % (estado, aoi))
            continue
        n = capa_puntos(ds, "gedi_%s_%s" % (estado, corto), filas,
                        "Huellas GEDI %s en %s" % (estado, aoi))
        print("%-32s %10d" % ("gedi_%s_%s" % (estado, corto), n))
        if estado.startswith("descartados"):
            motivos |= {r.get("motivo", "") for r in filas if r.get("motivo")}
print("%-32s %10d" % ("aoi_recintos", capa_recintos(ds)))
ds = None

estilo_aceptados(os.path.join(SALIDA, "gedi_aceptados.qml"))
estilo_descartados(os.path.join(SALIDA, "gedi_descartados.qml"), sorted(motivos))
estilo_recintos(os.path.join(SALIDA, "aoi_recintos.qml"))

print()
print("Listo. -> 05_Resultados/03_Vectores/TP2_GEDI.gpkg")
print("Estilos: gedi_aceptados.qml, gedi_descartados.qml, aoi_recintos.qml")
print()
print("MOTIVOS DE DESCARTE ENCONTRADOS EN EL DATO (asi se coloreo el estilo):")
for m in sorted(motivos):
    print("   %s" % m)
print()
print("COMO ABRIRLO EN QGIS")
print("  1. Arrastre TP2_GEDI.gpkg a QGIS y elija las capas.")
print("  2. Por cada capa: Propiedades -> Simbologia -> Estilo -> Cargar estilo")
print("     y elija el .qml del mismo nombre.")
print("  3. Agregue el DEM de 00_COMUN/03_Topografia/DEM/ debajo de los")
print("     descartados y compruebe que los rechazados por pendiente caen en")
print("     las laderas. No le crea al script: mirelo.")
