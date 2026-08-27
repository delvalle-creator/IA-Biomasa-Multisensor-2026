# -*- coding: utf-8 -*-
"""
buscar_biomass_L2.py   ---> que productos BIOMASS hay, de verdad, sobre los AOI.

QUE HACE Y QUE NO HACE
----------------------
SOLO CONSULTA. No descarga nada, no escribe ningun raster y NO NECESITA TOKEN:
la busqueda del catalogo de ESA MAAP es abierta. El token hace falta para bajar,
y de eso se ocupa descargar_biomass.py, que es el companiero de este script.

POR QUE HACE FALTA
------------------
En 08_Originales_crudos/03_post/BIOMASS_bandaP/ hay trece productos, todos SCS de NIVEL 1, en
dos ciclos: febrero de 2026 sobre la estepa y abril-junio de 2026 sobre el
bosque. Con eso NO se puede hacer biomasa:

  - un SCS es una imagen compleja en rango inclinado. Convertirla en biomasa no
    es aplicar una formula: requiere la pila tomografica de siete imagenes y la
    inversion propia de la mision. Con una escena sola se obtiene
    retrodispersion, no biomasa;
  - y sobre el bosque la primera adquisicion es del 23/04/2026, tres meses
    despues del incendio, asi que tampoco sirve para el analisis de cambio.

Lo unico de BIOMASS que podria aportar algo al proyecto es el producto de
NIVEL 2. Y ahi hay que ser preciso, porque no todos existen (verificado el
31/07/2026 contra el calendario oficial de la ESA):

    L2A altura de bosque        publicado el 30/06/2026    DISPONIBLE
    L2A perturbacion forestal   previsto para abril 2027   no existe aun
    L2B altura y BIOMASA (AGB)  previsto para mayo 2027    no existe aun
                                y hoy es de acceso restringido a usuarios
                                internos de la mision

O sea: **la biomasa de BIOMASS no va a existir antes de mayo de 2027**, nueve
meses despues de este curso. Perseguirla es perder el tiempo.

Lo que si existe desde el 30 de junio de 2026 es la ALTURA DE BOSQUE de nivel
2A, y para este proyecto es incluso mejor que la biomasa: el modelo del TP5
predice ALTURA (rh95), y la biomasa recien aparece despues, por la alometria.
Una altura de bosque derivada de banda P seria una validacion independiente de
exactamente la magnitud que el modelo estima, sin la amplificacion del exponente
2,605 de por medio.
Sobre un recinto de 15 x 15 km son 75 x 75 = 5.625 pixeles de AGB, de sobra para
comparar medias por clase de cobertura. Seria una estimacion INDEPENDIENTE hecha
por la mision disenada para eso, y ataca por otra via el problema de la escala
absoluta, que es donde el proyecto esta mas debil.

NOVEDAD DEL 01/08/2026, Y LO QUE OBLIGA A CAMBIAR
-------------------------------------------------
Una consulta al catalogo sobre un recuadro amplio -72,6 a -70,5 de longitud y
-46,1 a -41,5 de latitud, es decir toda la franja andina de Chubut- devolvio 54
productos de nivel 2A: 27 de altura de bosque y 27 de suelo cancelado, adquiridos
entre abril y junio de 2026 y publicados entre junio y julio. Hay franjas sobre
Lago Puelo, Esquel, Trevelin, Corcovado y Rio Pico.

La consulta que hacia este script el 31/07 preguntaba SOLO por los dos recintos
de 15 x 15 km y no devolvio nada de nivel 2. Las dos cosas pueden ser ciertas a
la vez, y confundirlas seria un error de bulto: que una franja no caiga sobre un
cuadrado de 15 km no significa que la mision no cubra la region.

Por eso ahora se consultan TRES zonas: los dos recintos, como siempre, y ademas
la region andina completa. La conclusion las informa por separado.

DOS PRECISIONES SOBRE LOS NOMBRES, verificadas contra la ficha oficial:
  - FP_FH__L2A es altura de dosel, y viene con SU CAPA DE CALIDAD. Los productos
    son de la primera version del procesador y estan en validacion: usar esa
    capa no es opcional.
  - FP_GN__L2A NO es elevacion del terreno. "GN" es Ground Notched: la
    retrodispersion calibrada con la contribucion del suelo cancelada, en las
    tres polarizaciones. Para biomasa forestal es mas util que un modelo de
    elevacion, y el nombre se presta a confusion.

La pregunta, entonces, es doble: ¿hay ALTURA DE BOSQUE de nivel 2A sobre estos
dos recintos, y si no la hay, la hay sobre la region? Este script las contesta.

COMO LA CONTESTA
----------------
1. Pide al catalogo la lista COMPLETA de colecciones, SIGUIENDO LA PAGINACION,
   y se queda con las de BIOMASS. No se asume ningun nombre: se leen los que el
   catalogo declare, porque los de nivel 2 pueden cambiar mientras la mision
   esta en fase tomografica.

   CUIDADO CON LA PAGINACION -error cometido el 31/07/2026-. El catalogo
   devuelve 10 colecciones por pagina y declara 297 en total. La primera version
   de este script leyo solo la primera pagina y contesto "no hay ninguna
   coleccion de BIOMASS", que era falso: no habia mirado el 97 % del catalogo.
   Ahora se sigue el enlace rel=next hasta agotarlo, se informa cuantas se
   leyeron contra cuantas declara el catalogo, y ADEMAS se pregunta por cada
   coleccion candidata por su nombre exacto, que no depende de la paginacion.
2. Para cada coleccion y cada AOI, busca por recuadro y por fecha.
3. Informa que hay, con fecha y tipo de producto, y separa NIVEL 1 de NIVEL 2.

INTERPRETACION DEL RESULTADO, que conviene tener decidida de antemano:
  - Si aparece AGB de nivel 2 -> vale la pena bajarlo y compararlo contra el mapa
    del TP5. Sera post-incendio contra post-incendio en el bosque, y hay que
    declararlo.
  - Si no aparece -> BIOMASS queda como material conceptual de la guia (la
    comparacion banda L contra banda P) y ASI HAY QUE ESCRIBIRLO en el informe,
    en vez de insinuar que se uso.

SALIDA    TP4_Radar_SAR/05_Resultados/04_Tablas/BIOMASS_catalogo_consulta.csv
USO (entorno conda 'aoi'):   python buscar_biomass_L2.py
"""
import csv
import json
import os
import sys

try:
    import requests
except ImportError:
    sys.exit("Falta requests. Activar el entorno conda 'aoi'.")

CATALOGO = "https://catalog.maap.eo.esa.int/catalogue/"

# ---------------------------------------------------------------------------
# LA SALIDA VA A LA PANTALLA Y AL REGISTRO A LA VEZ, Y SIN BUFFER
# ---------------------------------------------------------------------------
# El 31/07/2026 este script parecio colgarse dos veces. No se colgaba: el .bat
# redirigia la salida a un archivo, y cuando Python escribe a un archivo en vez
# de a una consola usa BUFFER COMPLETO. Resultado: la ventana se queda negra
# hasta que el proceso termina. Si ademas la red no contesta, no termina nunca y
# parece un cuelgue.
#
# La solucion es que el script escriba el registro EL MISMO, duplicando cada
# linea a la consola con flush inmediato, y que el .bat NO redirija nada.
class _Duplicador(object):
    def __init__(self, ruta):
        self.consola = sys.stdout
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        self.archivo = io.open(ruta, "w", encoding="utf-8", newline="\n")

    def write(self, s):
        self.consola.write(s); self.consola.flush()
        self.archivo.write(s); self.archivo.flush()

    def flush(self):
        self.consola.flush(); self.archivo.flush()


_AQUI = os.path.dirname(os.path.abspath(__file__))
# Cuatro niveles, no cinco: BIOMASS_bandaP -> 01_Pre_procesamiento ->
# 03_Scripts -> TP4_Radar_SAR -> raiz del proyecto.
_PROY = os.path.abspath(os.path.join(_AQUI, "..", "..", "..", ".."))
REGISTRO = os.path.join(_PROY, "TP2_LiDAR_GEDI_ICESat2", "05_Resultados",
                        "06_Control_calidad", "CONSULTA_BIOMASS.log")
try:
    sys.stdout = _Duplicador(REGISTRO)
except Exception as _e:
    print("(no se pudo abrir el registro: %s; sigo solo en pantalla)" % _e)


def alcanzable():
    """Una sola consulta corta antes de nada, para no colgarse esperando.

    Si el catalogo no contesta en diez segundos, es preferible decirlo y salir
    que encadenar seis consultas de veinticinco segundos cada una.
    """
    print("   probando si el catalogo responde ...", end=" ")
    sys.stdout.flush()
    try:
        r = requests.get(CATALOGO, timeout=10)
        print("responde (HTTP %d)" % r.status_code)
        return True
    except Exception as e:
        print("NO responde")
        print()
        print("   El catalogo de ESA MAAP no contesta desde esta maquina:")
        print("      %s" % e)
        print()
        print("   Puede ser la red, un proxy o un cortafuegos de la institucion.")
        print("   No es un problema del proyecto ni de los datos. Se puede probar")
        print("   abriendo en el navegador:")
        print("      %scollections" % CATALOGO)
        print("   Si en el navegador si abre, el bloqueo es de Python: revisar")
        print("   las variables HTTP_PROXY y HTTPS_PROXY del entorno.")
        return False

# Recuadros (lon_min, lat_min, lon_max, lat_max) tomados de los KML, los mismos
# que usa descargar_biomass.py.
AOIS = {
    "BOSQUE_NW_02": [-71.5977, -42.6952, -71.4096, -42.5563],
    "ESTEPA_NW_02": [-71.2137, -42.8468, -71.0259, -42.7084],
}

# TERCERA ZONA, AGREGADA EL 01/08/2026, Y EL MOTIVO IMPORTA
# --------------------------------------------------------
# Un recinto de 15 x 15 km es un punto para una mision de cobertura global. Que
# una franja de BIOMASS no caiga justo encima no significa que la mision no
# cubra la zona: significa que no cubre ESE cuadradito. Preguntar solo por los
# dos recintos confunde "no hay dato aqui" con "no hay dato". Por eso se agrega
# la region andina de Chubut, del paralelo 41,5 al 46,1 sur.
#
# Los resultados de esta tercera zona NO se mezclan con los de los recintos en
# la conclusion: sirven para mostrar el sensor, no para usarlo en el analisis.
REGION = {
    "REGION_ANDINA_CHUBUT": [-72.6, -46.1, -70.5, -41.5],
}

ZONAS = dict(AOIS)
ZONAS.update(REGION)

DESDE = "2025-04-29T00:00:00Z"      # lanzamiento de BIOMASS
HASTA = "2026-12-31T23:59:59Z"

AQUI = os.path.dirname(os.path.abspath(__file__))
TP4 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SALIDA = os.path.join(TP4, "05_Resultados", "04_Tablas", "BIOMASS_catalogo_consulta.csv")


ESPERA = 25          # segundos por consulta. Corto a proposito: si el catalogo
                     # no contesta en 25 s, no va a contestar, y es preferible
                     # decirlo a dejar la ventana colgada.


def pedir(url, **kw):
    """GET o POST con mensaje claro si el catalogo no contesta."""
    try:
        if "json" in kw:
            r = requests.post(url, timeout=ESPERA, **kw)
        else:
            r = requests.get(url, timeout=ESPERA, **kw)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("   no se pudo consultar %s\n      %s" % (url, e))
        return None


def nivel(cid, titulo):
    """Deduce el nivel del producto a partir del nombre de la coleccion."""
    t = (cid + " " + (titulo or "")).lower()
    if "level2" in t or "l2" in t or "agb" in t or "biomass_agb" in t or "height" in t:
        return "NIVEL 2"
    if "level1" in t or "l1" in t or "scs" in t or "dgm" in t:
        return "NIVEL 1"
    return "?"


# TIPOS DE PRODUCTO DE NIVEL 2A, verificados el 01/08/2026 contra la ficha
# oficial de la coleccion en ESA Earth Online:
#
#   FP_FH__L2A   Forest Height. Dos imagenes: altura del dosel y SU CAPA DE
#                CALIDAD. Es el producto que le interesa a este proyecto,
#                porque el modelo del TP5 predice altura, no biomasa.
#   FP_GN__L2A   Ground Notched. NO es elevacion del terreno, error facil de
#                cometer por el nombre: es la retrodispersion calibrada CON LA
#                CONTRIBUCION DEL SUELO CANCELADA, en las tres polarizaciones.
#                Para biomasa forestal es mas util que un modelo de elevacion.
#   FP_FD__L2A   Forest Disturbance. Previsto para abril de 2027: no existe aun.
TIPOS_L2A = {
    "FP_FH__L2A": "altura de dosel + capa de calidad",
    "FP_GN__L2A": "retrodispersion con el suelo cancelado (HH/HV/VV)",
    "FP_FD__L2A": "perturbacion forestal",
}


def tipo_producto(idp):
    """Devuelve el codigo de tipo que aparezca en el identificador, si lo hay."""
    for t in TIPOS_L2A:
        if t in idp:
            return t
    for t in ("SCS__1S", "RAW__0S"):
        if t in idp:
            return t
    return ""


# Nombres que ya usa descargar_biomass.py. Se preguntan uno por uno, ademas de
# recorrer el catalogo, para no depender de la paginacion ni de que el titulo
# contenga la palabra "biomass".
CANDIDATAS = ["BiomassLevel1a", "BiomassLevel1b", "BiomassLevel1c",
              "BiomassLevel2a", "BiomassLevel2b", "BiomassLevel3"]


MAX_PAGINAS = 40     # 40 paginas cubren de sobra las 297 colecciones declaradas


def todas_las_colecciones():
    """Recorre /collections siguiendo rel=next, informando el avance.

    Imprime una linea por pagina. Sin eso la ventana se queda muda treinta
    llamadas seguidas y parece colgada, que fue lo que paso el 31/07/2026.
    Ademas corta si el enlace 'next' se repite -algunos catalogos lo devuelven
    apuntando a si mismo y el recorrido no terminaria nunca-.
    """
    url = CATALOGO.rstrip("/") + "/collections?limit=100"
    vistas, declaradas, paginas, ya_vistas = [], None, 0, set()
    while url and paginas < MAX_PAGINAS:
        if url in ya_vistas:
            print("      el catalogo devolvio un enlace repetido; se corta aqui")
            break
        ya_vistas.add(url)
        datos = pedir(url)
        if not datos:
            print("      sin respuesta en la pagina %d; se sigue con lo leido" % (paginas + 1))
            break
        paginas += 1
        if declaradas is None:
            declaradas = datos.get("numberMatched") or datos.get("context", {}).get("matched")
        nuevas = datos.get("collections", [])
        vistas.extend(nuevas)
        print("      pagina %2d: %3d colecciones  (acumulado %d de %s)"
              % (paginas, len(nuevas), len(vistas),
                 declaradas if declaradas is not None else "?"))
        if not nuevas:
            break
        url = None
        for e in datos.get("links", []):
            if e.get("rel") == "next" and e.get("href"):
                url = e["href"]; break
    if paginas >= MAX_PAGINAS:
        print("      se alcanzo el tope de %d paginas" % MAX_PAGINAS)
    return vistas, declaradas, paginas


print(__doc__)
print("=" * 78)
print("0. COMPROBACION PREVIA")
print("=" * 78)
if not alcanzable():
    sys.exit(2)

print()
print("=" * 78)
print("1. COLECCIONES DE BIOMASS QUE DECLARA EL CATALOGO")
print("=" * 78)

# PRIMERO la pregunta concreta: seis consultas, seis segundos. Si el barrido
# posterior tarda o falla, la respuesta que importa ya esta en pantalla.
print("   a) consulta directa por nombre exacto  (rapida, no depende del barrido)")
cols, ids = [], set()
for cid in CANDIDATAS:
    c = pedir(CATALOGO.rstrip("/") + "/collections/" + cid)
    if c and c.get("id"):
        tit = c.get("title", "") or ""
        cols.append((c["id"], tit, nivel(c["id"], tit))); ids.add(c["id"])
        print("      %-18s EXISTE  %s" % (cid, tit[:46]))
    else:
        print("      %-18s no existe" % cid)

# DESPUES el barrido completo, por si hay colecciones con otro nombre.
print()
print("   b) barrido del catalogo completo  (por si hay nombres que no preveo)")
todas, declaradas, paginas = todas_las_colecciones()
print("      leidas %d colecciones en %d pagina(s); el catalogo declara %s"
      % (len(todas), paginas, declaradas if declaradas is not None else "un total que no informa"))
if declaradas and len(todas) < declaradas:
    print("      ATENCION: se leyeron menos de las declaradas; la lista puede estar incompleta")
for c in todas:
    cid = c.get("id", "")
    tit = c.get("title", "") or ""
    if cid not in ids and "biomass" in (cid + " " + tit).lower():
        cols.append((cid, tit, nivel(cid, tit))); ids.add(cid)
        print("      encontrada en el barrido: %-24s %s" % (cid, tit[:40]))

if not cols:
    print()
    print("   No hay ninguna coleccion de BIOMASS en el catalogo.")
    print("   Muestra de lo que si hay, para verificar que la consulta funciono:")
    for c in todas[:8]:
        print("      %-34s %s" % (c.get("id", "")[:34], (c.get("title", "") or "")[:40]))
    sys.exit(0)
print()

print("   %-34s %-9s %s" % ("id de la coleccion", "nivel", "titulo"))
for cid, tit, niv in sorted(cols, key=lambda x: (x[2], x[0])):
    print("   %-34s %-9s %s" % (cid, niv, tit[:60]))

print()
print("=" * 78)
print("2. QUE HAY SOBRE CADA RECINTO")
print("=" * 78)

filas = []
for cid, tit, niv in sorted(cols, key=lambda x: (x[2], x[0])):
    for aoi, bbox in ZONAS.items():
        res = pedir(CATALOGO.rstrip("/") + "/search",
                    json={"collections": [cid], "bbox": bbox,
                          "datetime": "%s/%s" % (DESDE, HASTA), "limit": 200})
        if res is None:
            continue
        items = res.get("features", [])
        print("   %-30s %-14s %s" % (cid, aoi,
              "%d producto(s)" % len(items) if items else "sin datos"))
        for it in items:
            fecha = (it.get("properties", {}) or {}).get("datetime", "")[:10]
            filas.append({"coleccion": cid, "nivel": niv, "aoi": aoi,
                          "tipo": tipo_producto(it.get("id", "")),
                          "fecha": fecha, "id_producto": it.get("id", "")})
        for it in items[:6]:
            fecha = (it.get("properties", {}) or {}).get("datetime", "")[:10]
            print("        %s   %s" % (fecha, it.get("id", "")[:64]))
        if len(items) > 6:
            print("        ... y %d mas" % (len(items) - 6))

print()
if filas:
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(filas[0].keys()))
        w.writeheader(); w.writerows(filas)
    print("tabla  %s  (%d filas)" % (os.path.basename(SALIDA), len(filas)))

print()
print("=" * 78)
print("CONCLUSION")
print("=" * 78)
n2_todos = [f for f in filas if f["nivel"] == "NIVEL 2"]
n2 = [f for f in n2_todos if f["aoi"] in AOIS]
n2_reg = [f for f in n2_todos if f["aoi"] in REGION]

# La region se informa SIEMPRE, haya o no dato sobre los recintos: es la
# diferencia entre "la mision no cubre la zona" y "no cae sobre este cuadradito".
print("   Sobre la REGION ANDINA DE CHUBUT (41,5 a 46,1 S): %d producto(s) de"
      " nivel 2." % len(n2_reg))
for t in sorted(set(f["tipo"] for f in n2_reg)):
    if t:
        print("      %-12s %-3d  %s" % (t, len([f for f in n2_reg if f["tipo"] == t]),
                                        TIPOS_L2A.get(t, "")))
print()

if n2:
    print("   HAY %d producto(s) de NIVEL 2 sobre los recintos." % len(n2))
    for aoi in AOIS:
        g = [f for f in n2 if f["aoi"] == aoi]
        print("      %-14s %d" % (aoi, len(g)))
    # DESGLOSE POR TIPO. Corregido el 01/08/2026: la version anterior de este
    # bloque hablaba de "comparar el AGB" y daba una fecha fija. Las dos cosas
    # estaban mal. El AGB es nivel 2B y no existe hasta 2027; lo que hay es
    # ALTURA DE DOSEL. Y la fecha estaba copiada del nivel 1, no del 2A.
    for t in sorted(set(f["tipo"] for f in n2)):
        if t:
            print("      %-12s %-3d  %s" % (t, len([f for f in n2 if f["tipo"] == t]),
                                            TIPOS_L2A.get(t, "")))
    fechas = sorted(f["fecha"] for f in n2 if f["fecha"])
    if fechas:
        print("      fechas       de %s a %s" % (fechas[0], fechas[-1]))
    print()

    # PRODUCTOS QUE CUBREN LOS DOS RECINTOS A LA VEZ: uno solo sirve para ambos.
    porid = {}
    for f in n2:
        porid.setdefault(f["id_producto"], set()).add(f["aoi"])
    ambos = sorted(i for i, a in porid.items() if len(a) == len(AOIS))
    if ambos:
        print("   %d producto(s) cubren LOS DOS recintos a la vez. Bajando uno de"
              % len(ambos))
        print("   estos alcanza para los dos sitios:")
        for i in ambos:
            print("      %s" % i)
        print()

    print("   Se bajan con descargar_biomass.py, que SI necesita token.")
    print()
    print("   QUE COMPARAR, Y QUE NO. Lo que hay es ALTURA DE DOSEL, no biomasa:")
    print("   el AGB es nivel 2B y no existe hasta 2027. La altura es, de hecho,")
    print("   mejor para este proyecto, porque es exactamente lo que estima el")
    print("   modelo del TP5, sin la alometria de exponente 2,605 de por medio.")
    print()
    print("   HAY QUE DECLARARLO ASI: el incendio fue del 10/01 al 27/02 de 2026 y")
    print("   TODAS las adquisiciones de nivel 2A son posteriores. Sirve para")
    print("   verificar la altura estimada, NO para medir el cambio por el fuego.")
elif n2_reg:
    print("   NO hay productos de nivel 2 que caigan sobre los dos recintos,")
    print("   pero SI los hay sobre la region andina de Chubut. Son dos cosas")
    print("   distintas y hay que escribirlas distinto:")
    print("      - la mision CUBRE la zona de estudio en sentido amplio;")
    print("      - las franjas disponibles no se superponen con estos dos")
    print("        cuadrados de 15 x 15 km.")
    print()
    print("   Entonces BIOMASS entra en el TP4 como DEMOSTRACION DEL SENSOR: se")
    print("   muestra un producto de la region, con su fecha, y se explica que")
    print("   es y que aportaria. No entra en el analisis del TP5. Declararlo")
    print("   asi en el informe, sin insinuar que se uso el dato.")
else:
    print("   NO hay productos de nivel 2 ni sobre los recintos ni sobre la")
    print("   region andina en el periodo consultado.")
    print()
    print("   Entonces BIOMASS queda en el proyecto como MATERIAL CONCEPTUAL: la")
    print("   comparacion banda L contra banda P, que esta bien hecha y es valiosa")
    print("   para la guia. Hay que escribirlo asi en el informe, sin insinuar que")
    print("   se uso el dato, porque no se uso.")
