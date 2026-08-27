# -*- coding: utf-8 -*-
"""
TP4_11_inspeccionar_biomass_L2A.py  ---> que trae de verdad un producto BIOMASS L2A.

POR QUE EXISTE ESTE SCRIPT
==========================
Los productos de nivel 2A de BIOMASS se publicaron el 30/06/2026, y este curso se
arma en agosto de 2026. Cuando se escribio el grafo
graph_biomass_l2a_altura.xml todavia no habia ningun producto descargado en el
proyecto -la descarga exige autenticarse ante la ESA-, asi que LOS NOMBRES DE
BANDA DEL GRAFO SON PROVISIONALES.

Poner en un grafo un nombre de banda que no existe no siempre da un error
visible: puede dar una banda vacia, o una constante, que es peor que un error
porque se procesa sin protestar y llega hasta el informe.

Es exactamente el mismo problema que el TP2 tuvo con GEDI, cuando la mision
renombro quality_flag y un filtro que no encontraba la variable dejaba pasar
todo. La regla que salio de ahi vale igual aqui: NO SE ASUME UN NOMBRE, SE
VERIFICA, y si no esta se falla con un mensaje claro.

QUE HACE
========
Abre el producto, lista sus bandas con tipo, tamano y valor "sin dato", informa
el sistema de referencia y el tamano de pixel, y al final IMPRIME LAS DOS LINEAS
que hay que pegar en el grafo de la interfaz grafica y la orden de gpt completa
para el gemelo _cli. No modifica nada.

USO (entorno conda 'aoi'):
    python TP4_11_inspeccionar_biomass_L2A.py <carpeta o archivo del producto>

Si no se le pasa nada, busca solo en 00_COMUN/08_Originales_crudos y en
TP4_Radar_SAR/02_Subsets_SNAP_QGIS/BIOMASS_L2A.
"""
import glob
import os
import sys

try:
    import rasterio
except ImportError:
    sys.exit("Falta rasterio. Active el entorno conda 'aoi'.")

_AQUI = os.path.dirname(os.path.abspath(__file__))
# Tres niveles: 01_Pre_procesamiento -> 03_Scripts -> TP4_Radar_SAR -> raiz.
_PROY = os.path.abspath(os.path.join(_AQUI, "..", "..", ".."))

# Palabras que suelen aparecer en el nombre de cada capa. NO son certezas: son
# candidatas para ordenar la salida y ayudar a elegir. La decision la toma quien
# mira la lista completa, que este script imprime entera.
PISTAS_ALTURA = ("height", "fh", "canopy", "altura")
PISTAS_CALIDAD = ("quality", "qual", "flag", "qa", "conf")


def candidatos(ruta=None):
    if ruta:
        if os.path.isfile(ruta):
            return [ruta]
        pats = [os.path.join(ruta, "**", "*.tif"), os.path.join(ruta, "**", "*.tiff"),
                os.path.join(ruta, "**", "*.TIF")]
    else:
        pats = []
        for base in (os.path.join(_PROY, "00_COMUN", "08_Originales_crudos"),
                     os.path.join(_PROY, "TP4_Radar_SAR", "02_Subsets_SNAP_QGIS", "BIOMASS_L2A")):
            pats += [os.path.join(base, "**", "*FH*.tif"),
                     os.path.join(base, "**", "*GN*.tif"),
                     os.path.join(base, "**", "*L2A*.tif")]
    vistos, salida = set(), []
    for p in pats:
        for f in glob.glob(p, recursive=True):
            if f not in vistos:
                vistos.add(f)
                salida.append(f)
    return sorted(salida)


def elegir(nombres, pistas):
    """Primer nombre que contenga alguna de las pistas. None si ninguno."""
    for n in nombres:
        b = (n or "").lower()
        for p in pistas:
            if p in b:
                return n
    return None


def inspeccionar(ruta):
    print("=" * 78)
    print(os.path.basename(ruta))
    print("=" * 78)
    with rasterio.open(ruta) as d:
        print("   tamano       %d x %d pixeles, %d banda(s)" % (d.width, d.height, d.count))
        print("   CRS          %s" % d.crs)
        px = abs(d.transform.a), abs(d.transform.e)
        print("   pixel        %.4g x %.4g (en las unidades del CRS)" % px)
        nd = d.nodatavals[0] if d.nodatavals else None
        print("   sin dato     %s" % (nd if nd is not None else "no declarado"))
        print()
        print("   %-4s %-34s %-10s %s" % ("n.o", "nombre de la banda", "tipo", "sin dato"))
        nombres = []
        for i in range(1, d.count + 1):
            desc = d.descriptions[i - 1] or d.tags(i).get("BAND_NAME") or ""
            nombres.append(desc if desc else "banda_%d" % i)
            print("   %-4d %-34s %-10s %s"
                  % (i, nombres[-1][:34], d.dtypes[i - 1], d.nodatavals[i - 1]))
    print()
    if not any(d for d in nombres if not d.startswith("banda_")):
        print("   AVISO: el archivo no trae nombres de banda; SNAP les pondra band_1,")
        print("   band_2, ... y hay que usar esos en el grafo. Mire el orden de arriba")
        print("   y confirmelo contra la ficha del producto antes de decidir cual es cual.")
        print()
    return nombres


def receta(ruta, nombres):
    alt = elegir(nombres, PISTAS_ALTURA)
    cal = elegir(nombres, PISTAS_CALIDAD)
    print("-" * 78)
    print("QUE PEGAR EN EL GRAFO")
    print("-" * 78)
    if not alt or not cal:
        print("   No pude identificar con confianza las dos capas.")
        print("   altura de dosel : %s" % (alt or "NO IDENTIFICADA"))
        print("   capa de calidad : %s" % (cal or "NO IDENTIFICADA"))
        print()
        print("   Eliga usted de la lista de arriba. NO adivine: si la lista no")
        print("   alcanza, la ficha oficial de la coleccion dice que el producto de")
        print("   altura trae dos imagenes, la altura y su capa de calidad.")
        return
    print("   altura de dosel : %s" % alt)
    print("   capa de calidad : %s" % cal)
    print()
    print("   1) En graph_biomass_l2a_altura.xml, la linea de la expresion queda:")
    print()
    print("        <expression>%s &gt; 0 ? %s : NaN</expression>" % (cal, alt))
    print()
    print("      OJO CON EL SENTIDO DEL UMBRAL. En unos productos la capa de")
    print("      calidad vale 1 donde el dato es bueno y en otros vale 0. Mire el")
    print("      histograma en SNAP antes de darlo por hecho: si al aplicar la")
    print("      mascara se le va casi todo, esta invertida.")
    print()
    print("   2) Para el gemelo de linea de ordenes, la orden completa es:")
    print()
    print("        gpt graph_biomass_l2a_altura_cli.xml ^")
    print("            -Pentrada=\"%s\" ^" % ruta)
    print("            -Psalida=\"%s\" ^"
          % os.path.join(_PROY, "TP4_Radar_SAR", "02_Subsets_SNAP_QGIS", "BIOMASS_L2A",
                         "BIOMASS_altura_BOSQUE_NW_02.tif"))
    print("            -Pgeowkt=\"POLYGON((-71.6178 -42.5362,-71.3895 -42.5362,"
          "-71.3895 -42.7153,-71.6178 -42.7153,-71.6178 -42.5362))\" ^")
    print("            -Paltura=\"%s\" -Pcalidad=\"%s\"" % (alt, cal))


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    archivos = candidatos(arg)
    if not archivos:
        print("No encontre ningun GeoTIFF de BIOMASS nivel 2A.")
        print()
        print("   Lo busque en:")
        print("      00_COMUN/08_Originales_crudos/**")
        print("      TP4_Radar_SAR/02_Subsets_SNAP_QGIS/BIOMASS_L2A/**")
        print()
        print("   Si todavia no descargo ninguno, primero hay que saber si hay")
        print("   productos sobre la zona. Eso lo contesta, sin credenciales:")
        print("      EJECUTAR_consulta_BIOMASS.bat")
        print("   La descarga si necesita autenticarse ante la ESA.")
        return 1
    print("Encontre %d archivo(s).\n" % len(archivos))
    for f in archivos:
        try:
            nombres = inspeccionar(f)
        except Exception as e:
            print("   no se pudo abrir: %s\n" % e)
            continue
        receta(f, nombres)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
