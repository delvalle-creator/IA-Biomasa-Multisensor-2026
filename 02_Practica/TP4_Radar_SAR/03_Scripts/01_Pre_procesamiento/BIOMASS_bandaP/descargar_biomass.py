#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
 DESCARGA DE IMAGENES BIOMASS (ESA) - BANDA P - SEPARADO POR AOI
============================================================================
 Curso de posgrado - material didactico. 2026.

 Version standalone (para PC con Python). Para Colab, usa el cuaderno
 BIOMASS_Colab.ipynb de esta misma carpeta.

 QUE HACE
 --------
 1) Convierte tu TOKEN OFFLINE de la ESA en un access token (paso obligatorio).
 2) Busca en el catalogo STAC de ESA MAAP los productos BIOMASS que caen
    sobre cada AOI (BOSQUE_NW_02 y ESTEPA_NW_02), POR SEPARADO.
 3) Descarga cada AOI en su propia carpeta (Imagenes/<AOI>/<coleccion>/).

 REQUISITOS (una sola vez)
 -------------------------
   Nada que instalar: solo usa requests, que ya esta en el entorno "aoi".
   Cuenta ESA "EO Sign In" + token offline generado en:
     https://portal.maap.eo.esa.int/ini/services/auth/token/  (Copy access token)

 NOTA sobre productos:
   - SCS  = Single-look Complex Slant-range (dato complejo de radar).
   - S1/S2/S3 = las tres franjas (swaths) que usa BIOMASS.
   - 1S = producto Standard (TRAE la imagen SAR).   <-- usar estos
   - 1M = producto Monitoring (version liviana SIN la imagen).
============================================================================
"""

import io
import os
import sys
import requests


# ---------------------------------------------------------------------------
# REGISTRO. AGREGADO EL 02/08/2026, Y POR UN MOTIVO CONCRETO
# ---------------------------------------------------------------------------
# El 02/08 a las 00:18 este script corrio, dijo "Listo" y no bajo ni un archivo.
# No quedo rastro de lo que habia pasado: la ventana se cerro y el script no
# escribia registro. Diagnosticar a ciegas lo que ya no se puede leer no es
# diagnosticar. Ahora deja registro SIEMPRE, y si no puede escribir donde
# corresponde, lo escribe al lado del script y LO DICE.
class _Duplicador(object):
    def __init__(self, ruta):
        self.consola = sys.stdout
        d = os.path.dirname(ruta)
        if d:
            os.makedirs(d, exist_ok=True)
        self.archivo = io.open(ruta, "w", encoding="utf-8", newline="\n")
        self.ruta = ruta

    def write(self, t):
        self.consola.write(t); self.consola.flush()
        self.archivo.write(t); self.archivo.flush()

    def flush(self):
        self.consola.flush(); self.archivo.flush()


def _abrir_registro():
    aqui = os.path.dirname(os.path.abspath(__file__))
    proy = os.path.abspath(os.path.join(aqui, "..", "..", "..", ".."))
    principal = os.path.join(proy, "TP2_LiDAR_GEDI_ICESat2", "05_Resultados",
                             "06_Control_calidad", "DESCARGA_BIOMASS.log")
    respaldo = os.path.join(aqui, "DESCARGA_BIOMASS.log")
    for ruta in (principal, respaldo):
        try:
            d = _Duplicador(ruta)
            sys.stdout = d
            print("Registro de esta corrida: %s" % ruta)
            if ruta == respaldo:
                print("   (no se pudo escribir en 06_Control_calidad; suele pasar")
                print("    si el .log quedo abierto en un editor)")
            return
        except Exception:
            continue
    print("AVISO: no se pudo abrir ningun registro. Solo queda lo de pantalla.")


_abrir_registro()

# SIN pystac_client NI shapely, desde el 02/08/2026.
# ==================================================
# Este script moria en la primera linea con
#     ModuleNotFoundError: No module named 'pystac_client'
# porque ese paquete NO esta en el entorno "aoi" del curso: no figura en la lista
# de comprobar_entorno.py y nunca se instalo. Pedirle al alumno que instale un
# paquete mas, en medio de una clase de cuatro horas, para hacer una consulta que
# el propio proyecto ya sabe hacer con requests, no tenia sentido.
#
# Ahora se consulta el catalogo STAC directamente con requests, exactamente igual
# que buscar_biomass_L2.py, que funciona desde julio. shapely tampoco hacia falta:
# solo se usaba para sacar el rectangulo que envuelve a cuatro puntos, que es un
# minimo y un maximo.
# Resultado: el script depende SOLO de requests, que ya esta en el entorno.

# ---------------------------------------------------------------------------
# 1) EL TOKEN: DE UN ARCHIVO SUYO, NO DE LA CONSOLA
# ---------------------------------------------------------------------------
# CORREGIDO EL 02/08/2026. La version anterior tenia dos trabas que hacian
# imposible arrancar, y ninguna de las dos daba un mensaje util:
#
#   1. Pedia un "client_secret" con getpass NADA MAS EMPEZAR, antes de cualquier
#      otra cosa. getpass NO MUESTRA lo que uno escribe -ni siquiera asteriscos-,
#      asi que la ventana parecia trabada. Y ademas ese secreto NO HACE FALTA:
#      el cliente "offline-token" de ESA MAAP es publico. Ahora es opcional y no
#      se pregunta nada: si la variable existe se usa, y si no, no se manda.
#
#   2. El token offline solo se podia pasar por variable de entorno, o sea
#      pegando en la consola una cadena de mas de mil caracteres. Pegar eso en el
#      Miniforge Prompt es incomodo y falla seguido.
#
# AHORA EL TOKEN SE LEE DE UN ARCHIVO DE TEXTO. Se abre el Bloc de notas, se pega
# el token, se guarda, y listo: no hay que pegar nada en ninguna consola.
#
# REGLA 8 DEL README, QUE SE RESPETA: nunca se guardan contrasenias, tokens ni
# credenciales dentro de 03_Scripts. Por eso el archivo va FUERA del proyecto,
# en la carpeta personal del docente. El script no lo copia ni lo imprime nunca.

ARCHIVO_TOKEN = os.environ.get("BIOMASS_TOKEN_FILE",
                               r"C:\Temp\Personal\biomass_token.txt")


def leer_credenciales():
    """Lee el archivo de credenciales. Admite los dos formatos posibles.

    FORMATO RECOMENDADO, que es el que documenta la propia ESA:

        CLIENT_ID=offline-token
        CLIENT_SECRET=<el que publica la base de conocimiento de MAAP>
        OFFLINE_TOKEN=<su token de 90 dias>

    FORMATO SIMPLE, que tambien se acepta: el archivo con el token y nada mas.
    En ese caso el client_secret tiene que venir por la variable de entorno.

    CORREGIDO EL 02/08/2026. Yo habia dado por hecho que el cliente
    "offline-token" era publico y saque el client_secret. ERA UN ERROR MIO: la
    documentacion de ESA MAAP publica un client_secret y el canje lo exige. Sin
    el, el intercambio falla y no se baja nada, que es exactamente lo que paso.
    """
    def limpiar(v, clave):
        """Saca los adornos que quedan al copiar de un ejemplo.

        AGREGADO EL 02/08/2026 despues de perder una hora por esto. El ejemplo
        que se le paso al docente decia   OFFLINE_TOKEN=<su token aca>   y el
        pego el token DENTRO de los signos, dejando  <eyJhbGci...>  . La ESA
        contesta "invalid_grant: Invalid refresh token", que apunta al token y
        manda a regenerarlo, cuando el token estaba perfecto y lo que sobraban
        eran dos caracteres. Un mensaje de error que acusa a la victima
        equivocada cuesta mas que no tener mensaje.
        """
        v = v.strip()
        for a, b in (("<", ">"), ('"', '"'), ("'", "'"), ("«", "»")):
            if v.startswith(a) and v.endswith(b) and len(v) > 2:
                v = v[1:-1].strip()
                print("   AVISO: %s venia entre %s%s y se los quite. Conviene" % (clave, a, b))
                print("   sacarlos del archivo: son del ejemplo, no del valor.")
        return v

    d = {}
    if os.path.exists(ARCHIVO_TOKEN):
        with io.open(ARCHIVO_TOKEN, encoding="utf-8") as h:
            crudo = h.read()
        if "=" in crudo:
            for linea in crudo.splitlines():
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                k, v = linea.split("=", 1)
                k = k.strip().upper()
                d[k] = limpiar(v, k)
        if not d.get("OFFLINE_TOKEN"):
            # Formato simple: todo el archivo es el token. Se juntan las lineas,
            # porque al pegar en el Bloc de notas suele quedar cortado.
            d["OFFLINE_TOKEN"] = limpiar("".join(crudo.split()), "OFFLINE_TOKEN")
    # La variable de entorno, si esta, manda sobre el archivo.
    for var, clave in (("BIOMASS_TOKEN", "OFFLINE_TOKEN"),
                       ("BIOMASS_CLIENT_SECRET", "CLIENT_SECRET"),
                       ("BIOMASS_CLIENT_ID", "CLIENT_ID")):
        v = os.environ.get(var, "").strip()
        if v:
            d[clave] = v
    return d


_CRED = leer_credenciales()
OFFLINE_TOKEN = _CRED.get("OFFLINE_TOKEN", "")

# Datos oficiales del intercambio (ESA MAAP) - NO cambiar
TOKEN_URL     = "https://iam.maap.eo.esa.int/realms/esa-maap/protocol/openid-connect/token"
CLIENT_ID     = _CRED.get("CLIENT_ID") or "offline-token"
# NO se escribe aca ningun valor: sale del archivo de credenciales, que vive
# fuera del proyecto. Regla 8 del README.
CLIENT_SECRET = _CRED.get("CLIENT_SECRET", "")


def explicar_como_poner_el_token():
    print()
    print("=" * 72)
    print(" FALTA EL TOKEN. No es un error del script: hay que darselo una vez.")
    print("=" * 72)
    print(" 1. Entre, con su cuenta EO Sign In, a la pagina del token de 90 dias:")
    print("       https://portal.maap.eo.esa.int/ini/services/auth/token/90dToken.php")
    print("    y genere uno nuevo. Es el token OFFLINE, no el de acceso.")
    print(" 2. Abra el Bloc de notas y escriba TRES lineas, asi:")
    print()
    print("       CLIENT_ID=offline-token")
    print("       CLIENT_SECRET=<el que publica la base de conocimiento de MAAP>")
    print("       OFFLINE_TOKEN=<el token que acaba de generar>")
    print()
    print("    Guardelo como:")
    print("       %s" % ARCHIVO_TOKEN)
    print(" 3. Vuelva a ejecutar este script. No hay que pegar nada en la consola.")
    print()
    print(" Si prefiere otra ubicacion, defina la variable BIOMASS_TOKEN_FILE con")
    print(" la ruta completa del archivo.")
    print()
    print(" El token NO va dentro de 03_Scripts, y este script no lo copia ni lo")
    print(" imprime nunca. Es la regla 8 del README del proyecto.")
    print("=" * 72)


def obtener_access_token():
    """Convierte el token offline (90 dias) en un access token fresco (minutos)."""
    if not OFFLINE_TOKEN:
        return ""
    datos = {
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": OFFLINE_TOKEN,
        "scope": "offline_access openid",
    }
    if CLIENT_SECRET:
        datos["client_secret"] = CLIENT_SECRET
    else:
        print("   AVISO: no hay CLIENT_SECRET en el archivo de credenciales.")
        print("   El canje de ESA MAAP normalmente lo exige y va a fallar.")
    r = requests.post(TOKEN_URL, data=datos, timeout=60)
    if r.status_code != 200:
        # Se informa lo que dice el servidor, en vez de cortar con una excepcion
        # sin texto. El motivo mas comun es que el token offline ya vencio.
        print("   El servidor de la ESA rechazo el token (HTTP %d)." % r.status_code)
        try:
            e = r.json()
            print("   %s: %s" % (e.get("error", "?"),
                                 e.get("error_description", "sin detalle")))
            if "invalid_grant" in str(e.get("error", "")):
                print("   Dos causas posibles, y conviene mirar la segunda primero")
                print("   porque es la mas facil de cometer:")
                print("     1. Al valor le sobran caracteres del ejemplo: signos")
                print("        menor y mayor, comillas, un espacio al final.")
                print("        Este script ya los saca solo, pero si el aviso de")
                print("        arriba aparecio, es senal de que estaban.")
                print("     2. El token offline vencio: duran 90 dias. En ese caso")
                print("        se genera uno nuevo en el portal.")
        except Exception:
            print("   %s" % r.text[:300])
        return ""
    return r.json().get("access_token", "")


ACCESS_TOKEN = obtener_access_token()
if ACCESS_TOKEN:
    print("Access token OK.")
elif not OFFLINE_TOKEN:
    explicar_como_poner_el_token()
    sys.exit(2)
else:
    # SE DETIENE. Antes seguia adelante, hacia las busquedas, no bajaba nada y
    # terminaba diciendo "Listo": la peor combinacion posible, porque parece que
    # funciono. Si hay token y no sirve, esto es un fallo y hay que decirlo asi.
    print()
    print("=" * 72)
    print(" EL TOKEN ESTA, PERO LA ESA NO LO ACEPTA. NO SE BAJO NADA.")
    print("=" * 72)
    print(" La causa mas probable, por lejos, es una confusion de nombres en el")
    print(" portal de MAAP. Hay DOS botones y hacen falta cosas distintas:")
    print()
    print("   'Copy access token'   -> token de ACCESO. Dura MINUTOS. NO SIRVE aca.")
    print("   'Copy offline token'  -> token OFFLINE, o de refresco. Dura 90 dias.")
    print("                            ES ESTE EL QUE HAY QUE PEGAR.")
    print()
    print(" Este script pide un token offline porque lo canjea por uno de acceso")
    print(" fresco cada vez, y ademas lo renueva solo si expira en mitad de una")
    print(" descarga larga. Con un token de acceso pegado en el archivo, el canje")
    print(" falla con invalid_grant, que es justamente lo que suele verse arriba.")
    print()
    print(" Que hacer: volver al portal, copiar el token OFFLINE, y reemplazar con")
    print(" el todo el contenido de:")
    print("   %s" % ARCHIVO_TOKEN)
    print()
    print(" La otra causa posible es que el token offline haya vencido: duran 90")
    print(" dias. En ese caso se genera uno nuevo, igual que la primera vez.")
    print("=" * 72)
    sys.exit(3)

# ---------------------------------------------------------------------------
# 2) AOIs (lon, lat) tomados de los KML
# ---------------------------------------------------------------------------
AOIS = {
    "BOSQUE_NW_02": [
        (-71.5977324, -42.6912349), (-71.4147861, -42.6952402),
        (-71.4095719, -42.5602750), (-71.5921243, -42.5562884),
        (-71.5977324, -42.6912349)],
    "ESTEPA_NW_02": [
        (-71.2137477, -42.8433829), (-71.0303041, -42.8467842),
        (-71.0258965, -42.7117874), (-71.2089427, -42.7084021),
        (-71.2137477, -42.8433829)],
}

# ---------------------------------------------------------------------------
# 3) CONFIGURACION
# ---------------------------------------------------------------------------
CATALOG_URL = "https://catalog.maap.eo.esa.int/catalogue/"

# Fechas. Amplio para ver toda la cobertura disponible.
# ESTEPA tuvo datos en verano (feb 2026); BOSQUE en otono (abr-jun 2026).
FECHA_INICIO = "2025-09-01T00:00:00Z"
FECHA_FIN    = "2026-12-31T23:59:59Z"

# QUE COLECCIONES SE BAJAN. Cambiado el 02/08/2026, en plena descarga.
# ===================================================================
# Estaban las cuatro, y las tres de nivel 1 tienen CUARENTA productos por recinto
# de medio giga cada uno: unos 40 GB para traer, al final de todo, los cuatro de
# nivel 2A que eran los que hacian falta. Ademas el nivel 2A quedaba ULTIMO en la
# lista, o sea que habia que esperar los 40 GB para llegar a lo que se buscaba.
#
# Por defecto se baja SOLO EL NIVEL 2A, que es lo que pide el curso: altura de
# dosel y suelo cancelado. Son pocos y tardan minutos.
#
# Para volver a bajar tambien el nivel 1, definir antes la variable
#     set BIOMASS_COLECCIONES=BiomassLevel1a,BiomassLevel1b,BiomassLevel1c,BiomassLevel2a
COLECCIONES = [c.strip() for c in
               (os.environ.get("BIOMASS_COLECCIONES") or "BiomassLevel2a").split(",")
               if c.strip()]
# DESTINO. Cambiado el 02/08/2026: antes escribia en 01_Pre_procesamiento/
# Imagenes, dentro de 03_Scripts. La regla del proyecto es que LOS ORIGINALES
# DESCARGADOS VIVEN EN 00_COMUN/08_Originales_crudos y no se tocan nunca mas; ahi estan ya los
# trece productos de nivel 1 de BIOMASS, planos y con nombre <ID>.zip. Se escribe
# en la misma carpeta y con el mismo criterio, para que no haya dos lugares
# distintos donde buscar lo mismo.
# Para volver al comportamiento anterior, definir BIOMASS_SALIDA con otra ruta.
_AQUI_D = os.path.dirname(os.path.abspath(__file__))
# Cuatro niveles: BIOMASS_bandaP -> 01_Pre_procesamiento -> 03_Scripts ->
# TP4_Radar_SAR -> raiz del proyecto.
_PROY_D = os.path.abspath(os.path.join(_AQUI_D, "..", "..", "..", ".."))
SALIDA = os.environ.get("BIOMASS_SALIDA") or os.path.join(
    _PROY_D, "00_COMUN", "08_Originales_crudos", "03_post", "BIOMASS_bandaP")

DESCARGAR = True                 # True = descargar (necesita token)
SOLO_1S   = True                 # True = solo productos con imagen (1S)
MAX_POR_AOI = None               # None = todos; o un numero para probar (ej. 1)

# ---------------------------------------------------------------------------
# 4) FUNCIONES
# ---------------------------------------------------------------------------
# Productos ya bajados EN ESTA CORRIDA. Hace falta porque tres de los cuatro
# productos de nivel 2A caen sobre LOS DOS recintos, y el bucle recorre un AOI
# despues del otro: sin esto se bajarian dos veces, con otro nombre de carpeta.
YA_BAJADOS = set()


def nombre_de_archivo(item, nombre_asset, asset):
    """Usa el nombre real que publica el catalogo, p. ej. <ID>.ZIP.

    Asi los productos nuevos quedan con el mismo aspecto que los trece de nivel 1
    que ya estan en 08_Originales_crudos, en vez de un <id>__product sin extension.
    """
    local = (asset or {}).get("file:local_path")
    if local:
        return os.path.basename(local)
    return "%s__%s" % (item["id"], nombre_asset)


def descargar_item(item, carpeta):
    """Descarga los assets del producto; renueva el access token si expira (401)."""
    global ACCESS_TOKEN
    if item["id"] in YA_BAJADOS:
        print("      ya bajado en esta corrida, se omite")
        return
    os.makedirs(carpeta, exist_ok=True)
    for nombre_asset, asset in preferir_producto(item).items():
        destino = os.path.join(carpeta, nombre_de_archivo(item, nombre_asset, asset))
        if os.path.exists(destino) and os.path.getsize(destino) > 0:
            # Reanudable: si ya esta, no se vuelve a bajar. Para forzarlo, borrar
            # el archivo. Un producto a medio bajar queda con tamano 0 y si se
            # reintenta.
            print("      ya estaba en la carpeta ->", os.path.basename(destino))
            YA_BAJADOS.add(item["id"])
            continue
        for intento in (1, 2):
            try:
                h = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
                with requests.get(asset["href"], headers=h, stream=True, timeout=600) as r:
                    if r.status_code == 401 and intento == 1:
                        ACCESS_TOKEN = obtener_access_token()   # renovar y reintentar
                        continue
                    r.raise_for_status()
                    with open(destino, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            f.write(chunk)
                print("      OK ->", os.path.basename(destino))
                YA_BAJADOS.add(item["id"])
                break
            except Exception as e:
                if intento == 2:
                    print("      ERROR", nombre_asset, ":", e)

def buscar(coleccion, bbox):
    """Consulta el catalogo STAC y devuelve la lista de productos.

    Equivale a lo que hacia catalogo.search(...).items() con pystac_client, pero
    con requests. Devuelve diccionarios simples, no objetos.
    """
    try:
        r = requests.post(CATALOG_URL.rstrip("/") + "/search",
                          json={"collections": [coleccion], "bbox": list(bbox),
                                "datetime": "%s/%s" % (FECHA_INICIO, FECHA_FIN),
                                "limit": 300},
                          timeout=120)
        if r.status_code != 200:
            print("   %s: el catalogo contesto HTTP %d" % (coleccion, r.status_code))
            return None                      # None = NO SE PUDO PREGUNTAR
        return r.json().get("features", [])
    except Exception as e:
        print("   %s: no se pudo consultar (%s)" % (coleccion, str(e)[:120]))
        return None


def rectangulo(puntos):
    """Rectangulo envolvente de una lista de (lon, lat). Reemplaza a shapely."""
    lons = [x for x, _ in puntos]
    lats = [y for _, y in puntos]
    return [min(lons), min(lats), max(lons), max(lats)]


def es_1S(item):
    """True si el producto es Standard (1S, con imagen)."""
    return "__1S" in item["id"] or "_1S_" in item["id"]


def es_nivel1(coleccion):
    """True para las colecciones de nivel 1, que son las unicas que tienen 1S/1M."""
    return "level1" in coleccion.lower()


# ERROR CORREGIDO EL 02/08/2026, Y CONVIENE ENTENDERLO
# ====================================================
# El filtro SOLO_1S se aplicaba a TODAS las colecciones, tambien a la de nivel 2A.
# Los identificadores de nivel 2 son de la forma BIO_FP_FH__L2A_... : no contienen
# "__1S" ni "_1S_", asi que es_1S() daba False para todos y el script informaba
#
#     BiomassLevel2a: 0 producto(s)
#
# sin un solo error. Ocho productos descartados en silencio por un filtro pensado
# para otra cosa. Es el mismo tipo de falla que el TP2 encontro en GEDI: un filtro
# que no encuentra lo que busca no avisa, simplemente deja pasar nada.
# Ahora SOLO_1S se aplica UNICAMENTE a las colecciones de nivel 1.


def preferir_producto(item):
    """Devuelve solo el asset del paquete completo si existe.

    Los productos de nivel 2A publican, ademas del ZIP, cada esquema XML por
    separado. Bajarlos todos duplica la descarga sin agregar nada: el ZIP ya los
    trae adentro. Si no hubiera asset 'product', se devuelven todos.
    """
    assets = item.get("assets", {}) or {}
    if "product" in assets:
        return {"product": assets["product"]}
    return assets

# ---------------------------------------------------------------------------
# 5) PRINCIPAL - separado por AOI
# ---------------------------------------------------------------------------
def main():
    print("Catalogo STAC de ESA MAAP: %s\n" % CATALOG_URL)

    for nombre, pts in AOIS.items():
        bbox = rectangulo(pts)
        print(f"=== AOI: {nombre}  bbox={[round(v, 4) for v in bbox]} ===")

        for col in COLECCIONES:
            try:
                items = buscar(col, bbox)
                if items is None:
                    # NO se imprime "0 producto(s)": no es que no haya, es que no
                    # se pudo preguntar. Confundir las dos cosas hace creer que un
                    # dato no existe cuando lo que fallo fue la consulta.
                    print("   %s: consulta fallida, se omite" % col)
                    continue
                # El filtro 1S/1M SOLO tiene sentido en nivel 1. Ver la nota de
                # es_nivel1(): aplicarlo al nivel 2A descartaba los ocho productos.
                if SOLO_1S and es_nivel1(col):
                    antes = len(items)
                    items = [it for it in items if es_1S(it)]
                    print(f"   {col}: {len(items)} producto(s) 1S "
                          f"(de {antes}; los 1M no traen imagen)")
                else:
                    print(f"   {col}: {len(items)} producto(s)")

                if DESCARGAR and ACCESS_TOKEN:
                    sel = items if MAX_POR_AOI is None else items[:MAX_POR_AOI]
                    # Sin subcarpeta por AOI: los productos que cubren los dos
                    # recintos son UN archivo, no dos. La pertenencia a cada AOI
                    # ya queda registrada en BIOMASS_catalogo_consulta.csv.
                    carpeta = SALIDA
                    for it in sel:
                        print("     Descargando", it["id"], "...")
                        descargar_item(it, carpeta)
            except Exception as e:
                print(f"   {col}: ERROR {e}")
        print()

    print("Listo. Archivos en:", os.path.abspath(SALIDA))

if __name__ == "__main__":
    main()
