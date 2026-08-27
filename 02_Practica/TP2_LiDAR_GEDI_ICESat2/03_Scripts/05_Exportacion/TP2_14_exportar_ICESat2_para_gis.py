# -*- coding: utf-8 -*-
"""
TP2_14_exportar_ICESat2_para_gis.py  ---> deja el cotejo GEDI / ICESat-2 en un
                                          GeoPackage, para mirarlo en QGIS.

POR QUE HACIA FALTA
-------------------
Del paso 13 salen dos tablas con numeros. Un numero no muestra DONDE las dos
misiones se contradicen, y eso es justamente lo que hay que ver: si la
discrepancia se concentra en las laderas, en el borde del recinto o en una sola
traza, entonces no es una propiedad del terreno sino un artefacto.

Este paso es el equivalente del paso 8 para la rama GEDI, y existe por la misma
razon: los resultados de este practico NO se creen, se miran.

POR QUE NO USA GDAL
-------------------
El paso 8 escribe su GeoPackage con GDAL, que es lo correcto cuando GDAL esta.
Este no lo usa, y no es capricho: un GeoPackage es un archivo SQLite con un
esquema documentado por el OGC, y el modulo sqlite3 viene con Python. Asi el
paso corre igual en el entorno 'aoi', en una maquina sin GDAL y dentro de un
contenedor pelado, que es donde se rompen las cadenas largas.

El archivo que produce cumple GeoPackage 1.2: application_id GPKG, user_version
10200, las tres tablas obligatorias, geometrias en GeoPackageBinary y una
entrada por capa en gpkg_contents y en gpkg_geometry_columns. Al terminar, el
propio programa lo vuelve a abrir y verifica lo que escribio.

El GeoPackage se arma primero en la carpeta temporal del sistema y recien
despues se copia a su lugar. SQLite necesita bloqueos de archivo que algunos
destinos no ofrecen -unidades de red, carpetas sincronizadas, sistemas de
archivos montados- y ahi falla con "disk I/O error" a la primera orden. Armarlo
en local y copiarlo evita el problema sin que el usuario tenga que saberlo.

QUE PRODUCE
-----------
Un GeoPackage con seis capas y dos estilos (.qml):

    atl08_operacional_bosque     segmentos ATL08, nivel operacional
    atl08_conservador_bosque     segmentos ATL08, nivel conservador
    atl08_operacional_estepa
    atl08_conservador_estepa
    cotejo_celdas                celdas de 500 m con la diferencia ATL08 - GEDI
    aoi_recintos_icesat2         los dos recuadros de 15 x 15 km

ENTRADA   04_Tablas_de_trabajo/06_ICESat2/ATL08_<RECINTO>_<nivel>_utm.csv   (paso 12)
          05_Resultados/04_Tablas/TP2_cotejo_GEDI_ICESat2_celdas.csv        (paso 13)

SALIDA    05_Resultados/03_Vectores/TP2_ICESat2_cotejo.gpkg
          05_Resultados/03_Vectores/atl08_segmentos.qml
          05_Resultados/03_Vectores/cotejo_celdas.qml

Los archivos de entrada NO se tocan. Todo sale con nombre nuevo.

QUE MIRAR, UNA VEZ ABIERTO
--------------------------
  1. Cargue tambien TP2_GEDI.gpkg. Las trazas de las dos misiones NO se
     superponen: son orbitas distintas. Donde se cruzan es donde el cotejo
     tiene sentido, y son pocos lugares. Verlo evita creer que se comparo
     todo el recinto.
  2. Coloree cotejo_celdas por 'diferencia_m'. Si las celdas con mayor
     discrepancia caen todas sobre las laderas, cruce con el DEM de
     00_COMUN/03_Topografia antes de sacar conclusiones.
  3. Pase de atl08_operacional_bosque a atl08_conservador_bosque. Si al
     hacerlo desaparecen sobre todo los segmentos altos, ese es el sesgo del
     filtro conservador hecho mapa. Es el punto del practico.

USO (entorno conda 'aoi'):   python TP2_14_exportar_ICESat2_para_gis.py
"""
import csv
import os
import shutil
import sqlite3
import struct
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
TP2 = os.path.abspath(os.path.join(AQUI, "..", ".."))

_d = AQUI
while _d != os.path.dirname(_d):
    if os.path.isdir(os.path.join(_d, "configuracion")):
        sys.path.insert(0, os.path.join(_d, "configuracion"))
        break
    _d = os.path.dirname(_d)

from configuracion_comun import AOIS_UTM, EPSG                      # noqa: E402

ATL08 = os.path.join(TP2, "04_Tablas_de_trabajo", "06_ICESat2")
TABLAS = os.path.join(TP2, "05_Resultados", "04_Tablas")
SALIDA = os.path.join(TP2, "05_Resultados", "03_Vectores")
GPKG = os.path.join(SALIDA, "TP2_ICESat2_cotejo.gpkg")

CELDA = 500.0        # tiene que coincidir con el CELDA del paso 13

REALES = {"h_canopy_m", "h_max_canopy_m", "h_te_best_fit_m", "canopy_openness_m",
          "h_canopy_uncertainty_m", "h_te_uncertainty_m", "uncertainty_ratio",
          "longitude", "latitude", "n_ca_photons", "n_te_photons",
          "diferencia_m", "mediana_gedi_rh98_m", "mediana_atl08_hcanopy_m",
          "este_centro", "norte_centro", "fuera_del_borde_m", "delta_time"}
ENTEROS = {"year", "month", "rgt", "cycle", "night_flag", "cloud_flag_atm",
           "msw_flag", "terrain_flg", "segment_landcover", "segment_snowcover",
           "n_gedi", "n_atl08", "celda_col", "celda_fil"}

# Columnas que no aportan nada en un SIG y solo ensucian la tabla de atributos.
DESCARTAR = {"delta_time", "segment_id_beg", "segment_id_end", "orbit_number",
             "sc_orient", "region", "version", "revision", "segment_key",
             "rh50_m", "rh75_m", "rh90_m", "rh95_m", "rh98_m", "rh100_m"}

WKT_32719 = (
    'PROJCS["WGS 84 / UTM zone 19S",GEOGCS["WGS 84",DATUM["WGS_1984",'
    'SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
    'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],'
    'UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],'
    'AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],'
    'PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-69],'
    'PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],'
    'PARAMETER["false_northing",10000000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],'
    'AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32719"]]')


# --------------------------------------------------------- GEOPACKAGE BINARY
def _cabecera(srs_id, env):
    """Cabecera GeoPackageBinary: 'GP', version 0, little endian, con sobre."""
    bandera = 0b0000_0011          # bit0 little endian, envelope de 4 valores
    b = b"GP" + bytes([0, bandera]) + struct.pack("<i", srs_id)
    b += struct.pack("<4d", env[0], env[1], env[2], env[3])
    return b


def punto(x, y, srs_id=EPSG):
    wkb = struct.pack("<BI2d", 1, 1, x, y)
    return _cabecera(srs_id, (x, x, y, y)) + wkb


def poligono(anillo, srs_id=EPSG):
    """anillo: lista de (x, y), cerrada."""
    xs = [p[0] for p in anillo]
    ys = [p[1] for p in anillo]
    wkb = struct.pack("<BII", 1, 3, 1) + struct.pack("<I", len(anillo))
    for x, y in anillo:
        wkb += struct.pack("<2d", x, y)
    return _cabecera(srs_id, (min(xs), max(xs), min(ys), max(ys))) + wkb


# ------------------------------------------------------------- ESQUELETO GPKG
def crear_gpkg(ruta):
    if os.path.exists(ruta):
        os.remove(ruta)
    cx = sqlite3.connect(ruta)
    cx.execute("PRAGMA application_id = 1196444487")     # 'GPKG'
    cx.execute("PRAGMA user_version = 10200")            # GeoPackage 1.2
    cx.executescript("""
    CREATE TABLE gpkg_spatial_ref_sys (
        srs_name TEXT NOT NULL, srs_id INTEGER PRIMARY KEY,
        organization TEXT NOT NULL, organization_coordsys_id INTEGER NOT NULL,
        definition TEXT NOT NULL, description TEXT);
    CREATE TABLE gpkg_contents (
        table_name TEXT PRIMARY KEY, data_type TEXT NOT NULL,
        identifier TEXT UNIQUE, description TEXT DEFAULT '',
        last_change DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
        min_x DOUBLE, min_y DOUBLE, max_x DOUBLE, max_y DOUBLE,
        srs_id INTEGER REFERENCES gpkg_spatial_ref_sys(srs_id));
    CREATE TABLE gpkg_geometry_columns (
        table_name TEXT NOT NULL, column_name TEXT NOT NULL,
        geometry_type_name TEXT NOT NULL, srs_id INTEGER NOT NULL,
        z TINYINT NOT NULL, m TINYINT NOT NULL,
        CONSTRAINT pk_geom_cols PRIMARY KEY (table_name, column_name));
    """)
    cx.executemany(
        "INSERT INTO gpkg_spatial_ref_sys VALUES (?,?,?,?,?,?)",
        [("Undefined cartesian SRS", -1, "NONE", -1, "undefined", None),
         ("Undefined geographic SRS", 0, "NONE", 0, "undefined", None),
         ("WGS 84 geodetic", 4326, "EPSG", 4326,
          'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],'
          'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]',
          None),
         ("WGS 84 / UTM zone 19S", EPSG, "EPSG", EPSG, WKT_32719,
          "Grilla comun del proyecto")])
    cx.commit()
    return cx


def tipo_sql(campo):
    if campo in REALES:
        return "DOUBLE"
    if campo in ENTEROS:
        return "INTEGER"
    return "TEXT"


def valor(campo, v):
    if v is None or v == "":
        return None
    try:
        if campo in REALES:
            return float(v)
        if campo in ENTEROS:
            return int(float(v))
    except (TypeError, ValueError):
        return None
    return v


def crear_capa(cx, nombre, campos, tipo_geom, descripcion):
    cols = ", ".join('"%s" %s' % (c, tipo_sql(c)) for c in campos)
    cx.execute('CREATE TABLE "%s" (fid INTEGER PRIMARY KEY AUTOINCREMENT, '
               'geom BLOB%s)' % (nombre, (", " + cols) if cols else ""))
    cx.execute("INSERT INTO gpkg_geometry_columns VALUES (?,?,?,?,?,?)",
               (nombre, "geom", tipo_geom, EPSG, 0, 0))
    cx.execute("INSERT INTO gpkg_contents "
               "(table_name, data_type, identifier, description, srs_id) "
               "VALUES (?,?,?,?,?)",
               (nombre, "features", nombre, descripcion, EPSG))


def cerrar_extension(cx, nombre, xs, ys):
    if not xs:
        return
    cx.execute("UPDATE gpkg_contents SET min_x=?, min_y=?, max_x=?, max_y=? "
               "WHERE table_name=?",
               (min(xs), min(ys), max(xs), max(ys), nombre))


# ------------------------------------------------------------------ AUXILIARES
def leer(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def capa_puntos(cx, nombre, filas, descripcion):
    campos = [c for c in filas[0]
              if c not in ("este_utm19s", "norte_utm19s") and c not in DESCARTAR]
    crear_capa(cx, nombre, campos, "POINT", descripcion)
    ins = 'INSERT INTO "%s" (geom%s) VALUES (?%s)' % (
        nombre, "".join(', "%s"' % c for c in campos), ", ?" * len(campos))
    xs, ys, n = [], [], 0
    for r in filas:
        try:
            x, y = float(r["este_utm19s"]), float(r["norte_utm19s"])
        except (KeyError, TypeError, ValueError):
            continue
        cx.execute(ins, [punto(x, y)] + [valor(c, r.get(c)) for c in campos])
        xs.append(x); ys.append(y); n += 1
    cerrar_extension(cx, nombre, xs, ys)
    return n


def capa_celdas(cx, filas):
    nombre = "cotejo_celdas"
    campos = list(filas[0].keys())
    crear_capa(cx, nombre, campos, "POLYGON",
               "Celdas de %d m: diferencia ATL08 menos GEDI" % int(CELDA))
    ins = 'INSERT INTO "%s" (geom%s) VALUES (?%s)' % (
        nombre, "".join(', "%s"' % c for c in campos), ", ?" * len(campos))
    xs, ys, n = [], [], 0
    for r in filas:
        cx_, cy_ = float(r["este_centro"]), float(r["norte_centro"])
        x0, y0 = cx_ - CELDA / 2.0, cy_ - CELDA / 2.0
        x1, y1 = cx_ + CELDA / 2.0, cy_ + CELDA / 2.0
        anillo = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        cx.execute(ins, [poligono(anillo)] + [valor(c, r.get(c)) for c in campos])
        xs += [x0, x1]; ys += [y0, y1]; n += 1
    cerrar_extension(cx, nombre, xs, ys)
    return n


def capa_recintos(cx):
    nombre = "aoi_recintos_icesat2"
    crear_capa(cx, nombre, ["aoi", "lado_km"], "POLYGON",
               "Recintos de 15 x 15 km")
    xs, ys, n = [], [], 0
    for aoi, (xmin, ymin, xmax, ymax) in AOIS_UTM.items():
        anillo = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)]
        cx.execute('INSERT INTO "%s" (geom, aoi, lado_km) VALUES (?,?,?)' % nombre,
                   (poligono(anillo), aoi, 15))
        xs += [xmin, xmax]; ys += [ymin, ymax]; n += 1
    cerrar_extension(cx, nombre, xs, ys)
    return n


def verificar(ruta, esperado):
    """Reabre el archivo y comprueba lo que se escribio."""
    cx = sqlite3.connect(ruta)
    app = cx.execute("PRAGMA application_id").fetchone()[0]
    ver = cx.execute("PRAGMA user_version").fetchone()[0]
    problemas = []
    if app != 1196444487:
        problemas.append("application_id incorrecto: %s" % app)
    if ver != 10200:
        problemas.append("user_version incorrecto: %s" % ver)
    for t in ("gpkg_spatial_ref_sys", "gpkg_contents", "gpkg_geometry_columns"):
        if not cx.execute("SELECT 1 FROM sqlite_master WHERE name=?", (t,)).fetchone():
            problemas.append("falta la tabla %s" % t)
    for nombre, n in esperado.items():
        real = cx.execute('SELECT COUNT(*) FROM "%s"' % nombre).fetchone()[0]
        if real != n:
            problemas.append("%s: se escribieron %d de %d" % (nombre, real, n))
        nulas = cx.execute('SELECT COUNT(*) FROM "%s" WHERE geom IS NULL' % nombre).fetchone()[0]
        if nulas:
            problemas.append("%s: %d geometrias nulas" % (nombre, nulas))
        cab = cx.execute('SELECT geom FROM "%s" LIMIT 1' % nombre).fetchone()[0]
        if cab[:2] != b"GP":
            problemas.append("%s: la geometria no empieza con 'GP'" % nombre)
        srs = struct.unpack("<i", cab[4:8])[0]
        if srs != EPSG:
            problemas.append("%s: srs_id %d en la geometria" % (nombre, srs))
        if not cx.execute("SELECT 1 FROM gpkg_contents WHERE table_name=?",
                          (nombre,)).fetchone():
            problemas.append("%s: no figura en gpkg_contents" % nombre)
    cx.close()
    return problemas


QML_SEGMENTOS = """<!DOCTYPE qgis>
<qgis version="3.28" styleCategories="Symbology">
  <renderer-v2 type="graduatedSymbol" attr="h_canopy_m" graduatedMethod="GraduatedColor">
    <ranges>
      <range lower="0" upper="5" label="0 - 5 m" symbol="0"/>
      <range lower="5" upper="10" label="5 - 10 m" symbol="1"/>
      <range lower="10" upper="20" label="10 - 20 m" symbol="2"/>
      <range lower="20" upper="35" label="20 - 35 m" symbol="3"/>
      <range lower="35" upper="200" label="mas de 35 m (revisar)" symbol="4"/>
    </ranges>
    <symbols>
      <symbol type="marker" name="0"><layer class="SimpleMarker">
        <prop k="color" v="237,248,233,255"/><prop k="size" v="1.6"/>
        <prop k="outline_style" v="no"/></layer></symbol>
      <symbol type="marker" name="1"><layer class="SimpleMarker">
        <prop k="color" v="186,228,179,255"/><prop k="size" v="1.6"/>
        <prop k="outline_style" v="no"/></layer></symbol>
      <symbol type="marker" name="2"><layer class="SimpleMarker">
        <prop k="color" v="116,196,118,255"/><prop k="size" v="1.6"/>
        <prop k="outline_style" v="no"/></layer></symbol>
      <symbol type="marker" name="3"><layer class="SimpleMarker">
        <prop k="color" v="44,95,45,255"/><prop k="size" v="1.6"/>
        <prop k="outline_style" v="no"/></layer></symbol>
      <symbol type="marker" name="4"><layer class="SimpleMarker">
        <prop k="color" v="238,0,0,255"/><prop k="size" v="2.2"/>
        <prop k="outline_style" v="no"/></layer></symbol>
    </symbols>
  </renderer-v2>
</qgis>
"""

QML_CELDAS = """<!DOCTYPE qgis>
<qgis version="3.28" styleCategories="Symbology">
  <renderer-v2 type="graduatedSymbol" attr="diferencia_m" graduatedMethod="GraduatedColor">
    <ranges>
      <range lower="-100" upper="-5" label="ATL08 mas bajo (menos de -5 m)" symbol="0"/>
      <range lower="-5" upper="-2" label="-5 a -2 m" symbol="1"/>
      <range lower="-2" upper="2" label="-2 a 2 m (coinciden)" symbol="2"/>
      <range lower="2" upper="5" label="2 a 5 m" symbol="3"/>
      <range lower="5" upper="100" label="ATL08 mas alto (mas de 5 m)" symbol="4"/>
    </ranges>
    <symbols>
      <symbol type="fill" name="0"><layer class="SimpleFill">
        <prop k="color" v="5,113,176,180"/><prop k="outline_color" v="120,120,120,255"/></layer></symbol>
      <symbol type="fill" name="1"><layer class="SimpleFill">
        <prop k="color" v="146,197,222,180"/><prop k="outline_color" v="120,120,120,255"/></layer></symbol>
      <symbol type="fill" name="2"><layer class="SimpleFill">
        <prop k="color" v="245,245,245,180"/><prop k="outline_color" v="120,120,120,255"/></layer></symbol>
      <symbol type="fill" name="3"><layer class="SimpleFill">
        <prop k="color" v="244,165,130,180"/><prop k="outline_color" v="120,120,120,255"/></layer></symbol>
      <symbol type="fill" name="4"><layer class="SimpleFill">
        <prop k="color" v="202,0,32,180"/><prop k="outline_color" v="120,120,120,255"/></layer></symbol>
    </symbols>
  </renderer-v2>
</qgis>
"""


def main():
    os.makedirs(SALIDA, exist_ok=True)
    # Se arma en temporal: ver la nota sobre los bloqueos de SQLite, arriba.
    tmpdir = tempfile.mkdtemp(prefix="tp2_gpkg_")
    libre = shutil.disk_usage(tmpdir).free
    if libre < 200 * 1024 * 1024:
        print("SIN ESPACIO en la carpeta temporal: %s" % tmpdir)
        print("   quedan %.1f MB y hacen falta unos 200." % (libre / 1048576.0))
        print("   Libere espacio ahi, o apunte la variable TMPDIR a otra unidad")
        print("   antes de correr este paso.")
        shutil.rmtree(tmpdir, ignore_errors=True)
        return 1
    provisorio = os.path.join(tmpdir, os.path.basename(GPKG))
    cx = crear_gpkg(provisorio)
    esperado = {}

    for recinto, corto in (("BOSQUE_NW_02", "bosque"), ("ESTEPA_NW_02", "estepa")):
        for nivel in ("operacional", "conservador"):
            filas = leer(os.path.join(ATL08, "ATL08_%s_%s_utm.csv" % (recinto, nivel)))
            if not filas:
                print("FALTA  ATL08_%s_%s_utm.csv  (corra antes el paso 12)"
                      % (recinto, nivel))
                continue
            nombre = "atl08_%s_%s" % (nivel, corto)
            n = capa_puntos(cx, nombre, filas,
                            "ATL08 %s, nivel %s" % (recinto, nivel))
            esperado[nombre] = n
            print("  %-28s %5d segmentos" % (nombre, n))

    celdas = leer(os.path.join(TABLAS, "TP2_cotejo_GEDI_ICESat2_celdas.csv"))
    if celdas:
        n = capa_celdas(cx, celdas)
        esperado["cotejo_celdas"] = n
        print("  %-28s %5d celdas" % ("cotejo_celdas", n))
    else:
        print("FALTA  TP2_cotejo_GEDI_ICESat2_celdas.csv  (corra antes el paso 13)")

    esperado["aoi_recintos_icesat2"] = capa_recintos(cx)
    cx.commit()
    cx.close()

    if len(esperado) <= 1:
        print("\nNo se escribio ninguna capa con datos.")
        shutil.rmtree(tmpdir, ignore_errors=True)
        return 1

    problemas = verificar(provisorio, esperado)
    if problemas:
        print("\nEL ARCHIVO NO PASO LA VERIFICACION:")
        for p in problemas:
            print("   " + p)
        print("Queda sin copiar, en %s" % provisorio)
        return 1

    # copyfile trunca el destino al abrirlo: no hace falta borrarlo antes, y
    # asi el paso funciona tambien donde no se permite borrar (carpetas
    # montadas, unidades de red con permisos de solo escritura).
    shutil.copyfile(provisorio, GPKG)
    shutil.rmtree(tmpdir, ignore_errors=True)

    with open(os.path.join(SALIDA, "atl08_segmentos.qml"), "w", encoding="utf-8") as f:
        f.write(QML_SEGMENTOS)
    with open(os.path.join(SALIDA, "cotejo_celdas.qml"), "w", encoding="utf-8") as f:
        f.write(QML_CELDAS)

    print("\nVerificado: %d capas, esquema GeoPackage 1.2, EPSG:%d en todas."
          % (len(esperado), EPSG))
    print("GeoPackage: %s" % GPKG)
    print("Estilos:    atl08_segmentos.qml  y  cotejo_celdas.qml")
    print("En QGIS:    Simbologia -> Estilo -> Cargar estilo, en cada capa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
