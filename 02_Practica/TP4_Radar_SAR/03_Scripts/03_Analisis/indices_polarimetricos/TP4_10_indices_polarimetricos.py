#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------
# POR QUE ESTE SCRIPT SIGUE EXISTIENDO (28/07/2026)
#
# Se habia decidido podarlo, dejando que SNAP calculara los indices con el
# operador Polarimetric-Parameters. La primera corrida real de
# graph_saocom_quad_indices.xml, sobre la escena SAOCOM S6 del 16/01/2024,
# desmintio esa decision para UN indice: la banda RVI que escribe SNAP no es
# el RVI.
#
#   banda RVI del producto .... mediana 0,00219
#   RVI recalculado ........... mediana 1,265
#   correlacion entre ambos ... 0,108   (7.034.926 pixeles)
#
# El factor tampoco es constante: entre 106x y 6.888x segun el pixel. Y esa
# banda correlaciona mas con el Span (0,39) que con el RVI. No es otra
# definicion del indice; no lo esta midiendo.
#
# Los demas indices de SNAP salieron correctos y NO hace falta reprogramarlos:
# RFDI 0,311 / CSI 0,495 / VSI 0,336 / BMI 0,285 / pedestal 0,194 / Span 0,609.
#
# En SNAP el reemplazo es una sola linea de Band Maths:
#     8 * HHVVRatio / (HHHVRatio * HHVVRatio + HHHVRatio + 2 * HHVVRatio)
#
# Mas abajo esta la misma cuenta hecha desde las intensidades, que es lo que
# hace falta para NISAR, donde no existe operador equivalente.
#
# Leccion, que es lo que hay que ensenar: un operador de SNAP puede entregar
# una banda con el nombre correcto y el contenido equivocado. La unica defensa
# es recalcular el indice por otra via y comparar pixel a pixel.
# ------------------------------------------------------------------

"""
TP4_10_indices_polarimetricos.py   ---> DECIMO script del TP4.

QUE HACE
--------
Calcula los indices polarimetricos RVI y RFDI sobre todos los productos de radar
del practico, los cruza con las huellas GEDI y responde tres preguntas que el
TP4_08 dejo abiertas:

  1. El indice, que es un COCIENTE, mejora el ajuste contra la altura del dosel
     respecto del gamma0 crudo? El cociente cancela relieve, humedad y errores de
     calibracion; la duda es si eso alcanza para levantar el R2 de 0,03 de la
     banda C. La respuesta puede ser que NO, y ese tambien es un resultado.

  2. Cuanto sube el RFDI donde paso el fuego? El RFDI es un indice de degradacion
     y perdida de biomasa, y SAOCOM tiene escenas antes y despues del incendio.

  3. Las tres bandas del proyecto, medidas con el MISMO indice y casi el MISMO
     dia, que diferencia muestran? El SAOCOM y el Sentinel-1 posteriores al fuego
     son del 27/02/2026 y hay un BIOMASS del 28/02/2026: un dia de diferencia.
     Al usar el mismo indice se cancela buena parte de la diferencia de
     calibracion entre sensores, y al ser casi simultaneas se cancela la
     temporal. Lo que queda es, en lo esencial, el efecto de la longitud de onda.

LAS FORMULAS, Y DE QUIEN ES CADA UNA
------------------------------------
No son intercambiables y hay que decir cual se uso.

  RVI quad-pol   (Kim y van Zyl, 2009; reproducida en el SAR Handbook)
      RVI = 8*g0HV / (g0HH + g0VV + 2*g0HV)
      Necesita las cuatro polarizaciones.

  RVI dual-pol   (Trudel, Charbonneau y Serrar, 2012)
      RVI = 4*g0cruzada / (g0co + g0cruzada)
      Alcanza con una co-polarizada y una cruzada. Es indiferente a la pareja:
      sirve con HH+HV y con VV+VH. Es la que habilita Sentinel-1.

  RFDI           (SAR Handbook, seccion 5.3)
      RFDI = (g0HH - g0HV) / (g0HH + g0HV)
      Necesita HH y HV. Se lee al reves que el RVI: valores BAJOS son bosque
      integro y biomasa alta; por encima de 0,6 el Handbook los asocia a
      superficie deforestada.

DOS DECISIONES DE METODO, DECLARADAS
------------------------------------
1. TODO SE PROMEDIA EN LINEAL. El gamma0 se promedia sobre la ventana en escala
   lineal y RECIEN DESPUES se forma el indice. Promediar en decibeles daria un
   sesgo negativo que crece con la heterogeneidad de la ventana, que es
   justamente lo que se esta midiendo. Es la misma regla del TP4_06 y del TP4_08.

2. EL INDICE SE FORMA CON LOS PROMEDIOS, no se promedian indices por pixel. Un
   cociente de dos valores ruidosos pixel a pixel es inestable; promediar primero
   cada polarizacion y dividir despues es mas robusto y no cambia el sentido.

UNA ADVERTENCIA QUE HAY QUE LEER ANTES DE INTERPRETAR LA ESTEPA
---------------------------------------------------------------
Mandal et al. (2020) advierten que los indices apoyados en la intensidad de la
polarizacion cruzada pueden indicar un valor ALTO aunque el dosel no este
desarrollado. Con una biomasa mediana de 3,4 Mg/ha, la estepa es exactamente ese
caso. Si el RVI de la estepa sale parecido al del bosque, sospeche del indice
antes que del bosque. La alternativa de esos autores es el DpRVI, que el producto
GCOV de NISAR habilita sin trabajo extra porque ya trae la matriz de covarianza.

Y no hay que esperar milagros de la banda C: el SAR Handbook (Tabla 4.1) pone en
UN METRO el techo de sensibilidad de la banda C a la altura del rodal, contra
diez metros de la banda L. Un cociente limpia ruido, no crea sensibilidad que la
longitud de onda no tiene.

ENTRADA   02_Subsets_SNAP_QGIS/**/*.tif  (gamma0, bandas con descripcion Gamma0_<POL>)
          ../TP2_LiDAR_GEDI_ICESat2/05_Resultados/04_Tablas/GEDI_L2A_<AOI>_aceptados.csv
SALIDA    05_Resultados/04_Tablas/indices_por_producto.csv
          05_Resultados/04_Tablas/ajustes_indices.csv
          05_Resultados/04_Tablas/rfdi_antes_despues.csv
          05_Resultados/04_Tablas/comparacion_tres_bandas.csv
          05_Resultados/04_Tablas/LEEME_indices.txt

USO (entorno conda 'aoi'):
  python TP4_10_indices_polarimetricos.py
  python TP4_10_indices_polarimetricos.py ESTEPA_NW_02    (el otro sitio)
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
TP4 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROYECTO = os.path.dirname(TP4)

gdal.UseExceptions()
INSUMOS = os.path.join(TP4, "02_Subsets_SNAP_QGIS")
RESULTADOS = os.path.join(TP4, "05_Resultados")
GEDI = os.path.join(PROYECTO, "TP2_LiDAR_GEDI_ICESat2", "05_Resultados", "04_Tablas")

AOI = sys.argv[1] if len(sys.argv) > 1 else "BOSQUE_NW_02"
RADIO = 7                      # ventana 15x15 = 150 m, la del TP4_08
CORTES = [0, 3, 6, 9, 12, 15, 18, 21, 25, 30]
MIN_HUELLAS = 30               # por debajo de esto no se ajusta nada

# La ventana del 27-28 de febrero de 2026: las tres bandas casi simultaneas.
VENTANA_TRES_BANDAS = ("20260227", "20260228", "20260225")


# ---------------------------------------------------------------- utilidades

def bandas_de_dim(dim):
    """BEAM-DIMAP: las bandas viven como .img (ENVI) dentro de la carpeta
    .data hermana. GDAL las abre de a una. Devuelve {POL: ruta_img}."""
    data = dim[:-4] + ".data"
    out = {}
    if not os.path.isdir(data):
        return out
    for img in sorted(glob.glob(os.path.join(data, "*.img"))):
        nom = os.path.splitext(os.path.basename(img))[0]
        if nom.lower().startswith("gamma0_"):
            pol = nom.split("_", 1)[1].upper()
            if pol in ("HH", "HV", "VH", "VV"):
                out[pol] = img
    return out


def polarizaciones(ruta):
    """Mapea polarizacion -> (dataset, numero de banda).

    SE PREFIERE EL .dim. El BEAM-DIMAP es el producto principal del proyecto
    porque conserva los metadatos y permite seguir procesando en SNAP; el
    GeoTIFF es una copia para QGIS que los pierde. Si hay .dim se lee de ahi,
    y el .tif queda como respaldo.

    La polarizacion se resuelve por el NOMBRE de la banda, no por su posicion:
    el orden cambia entre sensores (en Sentinel-1 la banda 1 es la cruzada, en
    NISAR es la co-polarizada) y confiar en el indice seria un error silencioso.
    """
    out = {}
    if ruta.lower().endswith(".dim"):
        for pol, img in bandas_de_dim(ruta).items():
            out[pol] = (gdal.Open(img), 1)
        return out
    ds = gdal.Open(ruta)
    for i in range(1, ds.RasterCount + 1):
        nom = (ds.GetRasterBand(i).GetDescription() or "").strip()
        if nom.lower().startswith("gamma0_"):
            pol = nom.split("_", 1)[1].upper()
            if pol in ("HH", "HV", "VH", "VV"):
                out[pol] = (ds, i)
    return out


def huellas():
    p = os.path.join(GEDI, "GEDI_L2A_%s_aceptados.csv" % AOI)
    if not os.path.exists(p):
        sys.exit("No hay huellas GEDI en %s. Ejecute antes el TP2 completo." % p)
    out = []
    for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
        try:
            out.append((float(r["este_utm19s"]), float(r["norte_utm19s"]),
                        float(r["rh95"]), r.get("shot_number", "")))
        except (KeyError, ValueError):
            continue
    return out


def medias_por_huella(ruta, pols, hs):
    """Devuelve [(shot, rh95, {POL: gamma0 medio LINEAL}), ...] por huella."""
    mapa = polarizaciones(ruta)
    if not mapa:
        return []
    gt = next(iter(mapa.values()))[0].GetGeoTransform()
    arr = {}
    for pol, (ds, b) in mapa.items():
        if pol not in pols:
            continue
        a = ds.GetRasterBand(b).ReadAsArray().astype("float64")
        arr[pol] = np.where(np.isfinite(a) & (a > 0), a, np.nan)
    if len(arr) < len(pols):
        return []
    ny, nx = next(iter(arr.values())).shape
    out = []
    for e, n, h, shot in hs:
        c = int((e - gt[0]) / gt[1])
        f = int((n - gt[3]) / gt[5])
        if not (RADIO <= c < nx - RADIO and RADIO <= f < ny - RADIO):
            continue
        vals = {}
        ok = True
        for pol, a in arr.items():
            w = a[f - RADIO:f + RADIO + 1, c - RADIO:c + RADIO + 1]
            w = w[np.isfinite(w)]
            if w.size == 0:
                ok = False
                break
            vals[pol] = float(w.mean())      # LINEAL
        if ok:
            out.append((shot, h, vals))
    return out


def rvi_quad(v):
    den = v["HH"] + v["VV"] + 2.0 * v["HV"]
    return 8.0 * v["HV"] / den if den > 0 else None


def rvi_dual(v, co, cruz):
    den = v[co] + v[cruz]
    return 4.0 * v[cruz] / den if den > 0 else None


def rfdi(v):
    den = v["HH"] + v["HV"]
    return (v["HH"] - v["HV"]) / den if den > 0 else None


def ajustar(x, y):
    """Ajusta x (indice o gamma0) contra y (rh95). Devuelve R2 y RMSE."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.size < MIN_HUELLAS:
        return None
    a, b = np.polyfit(y, x, 1)
    pred = a * y + b
    denom = ((x - x.mean()) ** 2).sum()
    if denom <= 0:
        return None
    r2 = 1 - ((x - pred) ** 2).sum() / denom
    rmse = float(np.sqrt(((x - pred) ** 2).mean()))
    return float(a), float(b), float(r2), rmse, int(x.size)


def mediana(v):
    v = sorted(v)
    n = len(v)
    if n == 0:
        return None
    return v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2])


# ---------------------------------------------------------------- inventario

def inventario():
    """Todos los gamma0 del practico, con las polarizaciones que trae cada uno."""
    prods = []
    # Primero los .dim, que son el producto principal; despues los .tif que no
    # tengan un .dim al lado, para no contar dos veces la misma escena.
    dims = sorted(glob.glob(os.path.join(INSUMOS, "**", "*.dim"), recursive=True))
    tifs = [t for t in sorted(glob.glob(os.path.join(INSUMOS, "**", "*.tif"),
                                        recursive=True))
            if not os.path.exists(t[:-4] + ".dim")]
    for ruta in dims + tifs:
        if "_mask" in ruta or "_nativo" in ruta or "_crudo" in ruta:
            continue
        if AOI not in ruta:
            continue
        try:
            mapa = polarizaciones(ruta)
        except Exception:
            continue
        if not mapa:
            continue
        rel = os.path.relpath(ruta, INSUMOS)
        sensor = rel.split(os.sep)[0]
        fecha = ""
        for tok in os.path.basename(ruta).replace(".", "_").split("_"):
            if len(tok) == 8 and tok.isdigit():
                fecha = tok
                break
        prods.append({"ruta": ruta, "rel": rel, "sensor": sensor,
                      "fecha": fecha, "pols": set(mapa),
                      "formato": "dim" if ruta.endswith(".dim") else "tif"})
    return prods


def indices_disponibles(pols):
    """Que indices se pueden calcular con las polarizaciones presentes."""
    p = set(pols)
    out = []
    if {"HH", "VV", "HV"} <= p:
        out.append(("RVI_quad", "Kim y van Zyl (2009)"))
    if {"HH", "HV"} <= p:
        out.append(("RVI_dual_HH_HV", "Trudel et al. (2012)"))
        out.append(("RFDI", "SAR Handbook 5.3"))
    if {"VV", "VH"} <= p:
        out.append(("RVI_dual_VV_VH", "Trudel et al. (2012)"))
    return out


def calcular(v, nombre):
    if nombre == "RVI_quad":
        return rvi_quad(v)
    if nombre == "RVI_dual_HH_HV":
        return rvi_dual(v, "HH", "HV")
    if nombre == "RVI_dual_VV_VH":
        return rvi_dual(v, "VV", "VH")
    if nombre == "RFDI":
        return rfdi(v)
    return None


def pols_necesarias(nombre):
    return {"RVI_quad": {"HH", "VV", "HV"},
            "RVI_dual_HH_HV": {"HH", "HV"},
            "RVI_dual_VV_VH": {"VV", "VH"},
            "RFDI": {"HH", "HV"}}[nombre]


# ------------------------------------------------- autocomprobacion previa

def autocomprobacion():
    """Verifica las formulas contra casos con respuesta conocida ANTES de
    tocar los datos. Si esto falla, no tiene sentido seguir.

    Caso canonico: una nube de dipolos orientados al azar (volumen puro) tiene
    HV/HH = 1/3, y para ella el RVI vale exactamente 1, que es su maximo
    teorico. Una superficie lisa tiene HV ~ 0 y RVI ~ 0. El RFDI se lee al
    reves: 0 en volumen puro, cercano a 1 en superficie desnuda."""
    vol = {"HH": 1.0, "VV": 1.0, "HV": 1.0 / 3.0}
    liso = {"HH": 1.0, "VV": 1.0, "HV": 1e-6}
    pruebas = [
        ("RVI quad, volumen aleatorio", rvi_quad(vol), 1.0),
        ("RVI dual, volumen aleatorio", rvi_dual(vol, "HH", "HV"), 1.0),
        ("RVI quad, superficie lisa", rvi_quad(liso), 0.0),
        ("RFDI, volumen aleatorio", rfdi(vol), 0.5),
        ("RFDI, superficie lisa", rfdi(liso), 1.0),
    ]
    print("AUTOCOMPROBACION DE LAS FORMULAS")
    ok = True
    for nom, obt, esp in pruebas:
        bien = abs(obt - esp) < 1e-3
        ok = ok and bien
        print("   %-32s %8.4f  esperado %6.3f  %s"
              % (nom, obt, esp, "ok" if bien else "MAL"))
    if not ok:
        sys.exit("Las formulas no pasan la autocomprobacion. No se sigue.")
    print("   Las dos formas del RVI coinciden en 1,0 para el volumen puro: la")
    print("   normalizacion 8 de la quad y 4 de la dual es consistente.")
    print()
    return True


# ---------------------------------------------------------------------- main

print(__doc__)
autocomprobacion()
hs = huellas()
print("AOI: %s" % AOI)
print("huellas GEDI validas: %d" % len(hs))
print("ventana: %dx%d pixeles (%d m)" % (2 * RADIO + 1, 2 * RADIO + 1,
                                         (2 * RADIO + 1) * 10))
print()

prods = inventario()
if not prods:
    sys.exit("No se encontro ningun gamma0 con bandas Gamma0_<POL> para %s.\n"
             "Ejecute antes TP4_01 (Sentinel-1 y SAOCOM) y TP4_03 (NISAR)." % AOI)

print("=" * 74)
print("PRODUCTOS ENCONTRADOS Y QUE INDICE ADMITE CADA UNO")
print("=" * 74)
filas_inv = []
for p in prods:
    idxs = indices_disponibles(p["pols"])
    nombres = ", ".join(n for n, _ in idxs) or "(ninguno: falta una pareja)"
    print("   %-46s [%s] %s" % (p["rel"][:46], p["formato"],
                                "+".join(sorted(p["pols"]))))
    print("        -> %s" % nombres)
    filas_inv.append({"producto": p["rel"], "sensor": p["sensor"],
                      "fecha": p["fecha"],
                      "polarizaciones": "+".join(sorted(p["pols"])),
                      "formato": p["formato"], "indices": nombres})
print()

# --- calculo por producto e indice ---------------------------------------
detalle = []      # una fila por huella, producto e indice
fuera_rango = {}  # RVI > 1: no deberia pasar en un blanco natural
ajustes = []      # una fila por producto e indice
crudos = {}       # gamma0 cruzada crudo, para comparar contra el indice

for p in prods:
    idxs = indices_disponibles(p["pols"])
    if not idxs:
        continue
    necesarias = set()
    for n, _ in idxs:
        necesarias |= pols_necesarias(n)
    datos = medias_por_huella(p["ruta"], necesarias, hs)
    if not datos:
        continue

    # gamma0 de la polarizacion cruzada, en dB, como referencia de comparacion
    cruz = "HV" if "HV" in p["pols"] else ("VH" if "VH" in p["pols"] else None)
    if cruz:
        xs = [10 * np.log10(v[cruz]) for _, _, v in datos if v.get(cruz, 0) > 0]
        ys = [h for _, h, v in datos if v.get(cruz, 0) > 0]
        r = ajustar(xs, ys)
        if r:
            crudos[p["rel"]] = r
            ajustes.append({"producto": p["rel"], "sensor": p["sensor"],
                            "fecha": p["fecha"],
                            "magnitud": "gamma0_%s_dB" % cruz,
                            "fuente_formula": "-",
                            "pendiente": "%.5f" % r[0], "R2": "%.4f" % r[2],
                            "RMSE": "%.4f" % r[3], "n": r[4]})

    for nombre, fuente in idxs:
        vals, alturas = [], []
        for shot, h, v in datos:
            x = calcular(v, nombre)
            if x is None or not np.isfinite(x):
                continue
            if nombre.startswith("RVI") and x > 1.0:
                fuera_rango[nombre] = fuera_rango.get(nombre, 0) + 1
            vals.append(x)
            alturas.append(h)
            detalle.append({"producto": p["rel"], "sensor": p["sensor"],
                            "fecha": p["fecha"], "indice": nombre,
                            "shot_number": shot, "rh95": "%.2f" % h,
                            "valor": "%.5f" % x})
        r = ajustar(vals, alturas)
        if r:
            ajustes.append({"producto": p["rel"], "sensor": p["sensor"],
                            "fecha": p["fecha"], "magnitud": nombre,
                            "fuente_formula": fuente,
                            "pendiente": "%.5f" % r[0], "R2": "%.4f" % r[2],
                            "RMSE": "%.4f" % r[3], "n": r[4]})

if fuera_rango:
    print("=" * 74)
    print("AVISO: valores de RVI POR ENCIMA DE 1")
    print("=" * 74)
    for k, v in sorted(fuera_rango.items()):
        print("   %-18s %d huellas" % (k, v))
    print("   El maximo teorico del RVI es 1, y se alcanza en volumen puro")
    print("   (dipolos al azar, HV/HH = 1/3). Un valor mayor no corresponde a un")
    print("   blanco natural: revise la calibracion, el terrain flattening o la")
    print("   presencia de dobles rebotes muy fuertes en la ventana. No lo")
    print("   interprete como vegetacion densa.")
    print()

# --- la pregunta 1: el indice le gana al gamma0 crudo? --------------------
print("=" * 74)
print("PREGUNTA 1. EL INDICE MEJORA EL AJUSTE CONTRA LA ALTURA?")
print("=" * 74)
print("   %-34s %-16s %8s %8s" % ("producto", "magnitud", "R2", "RMSE"))
for a in sorted(ajustes, key=lambda z: (z["producto"], z["magnitud"])):
    print("   %-34s %-16s %8s %8s" % (a["producto"][-34:], a["magnitud"],
                                      a["R2"], a["RMSE"]))
print()
print("   Lea por producto: la fila 'gamma0_..._dB' es el crudo y las otras son")
print("   los indices. Si el indice sube el R2, el cociente estaba limpiando")
print("   ruido geometrico. Si no lo sube, el limite es de la longitud de onda")
print("   y no del procesamiento. Las dos respuestas cierran el argumento.")
print()

# --- la pregunta 2: RFDI antes y despues del fuego ------------------------
print("=" * 74)
print("PREGUNTA 2. EL RFDI ANTES Y DESPUES DEL INCENDIO")
print("=" * 74)
por_sensor = {}
for d in detalle:
    if d["indice"] != "RFDI":
        continue
    por_sensor.setdefault((d["sensor"], d["fecha"]), []).append(float(d["valor"]))
filas_rfdi = []
if por_sensor:
    print("   %-16s %-10s %8s %8s" % ("sensor", "fecha", "mediana", "n"))
    for (sensor, fecha), v in sorted(por_sensor.items()):
        m = mediana(v)
        print("   %-16s %-10s %8.4f %8d" % (sensor, fecha, m, len(v)))
        filas_rfdi.append({"sensor": sensor, "fecha": fecha,
                           "RFDI_mediano": "%.4f" % m, "n": len(v)})
    print()
    print("   El RFDI SUBE con la degradacion. Compare las fechas anteriores al")
    print("   10/1/2026 con las posteriores al 27/2/2026 del mismo sensor: la")
    print("   diferencia es la senal del fuego en banda L. Por encima de 0,6 el")
    print("   SAR Handbook asocia los valores a superficie deforestada.")
else:
    print("   No hay ningun producto con HH y HV: el RFDI no se puede calcular.")
print()

# --- la pregunta 3: las tres bandas casi simultaneas ----------------------
print("=" * 74)
print("PREGUNTA 3. LAS TRES BANDAS EN LA MISMA SEMANA (27-28/02/2026)")
print("=" * 74)
filas_tres = []
for a in ajustes:
    if a["fecha"] in VENTANA_TRES_BANDAS and a["magnitud"].startswith("RVI"):
        filas_tres.append(a)
if filas_tres:
    print("   %-16s %-10s %-16s %8s %8s" % ("sensor", "fecha", "indice", "R2", "n"))
    for a in sorted(filas_tres, key=lambda z: z["sensor"]):
        print("   %-16s %-10s %-16s %8s %8d" % (a["sensor"], a["fecha"],
                                                a["magnitud"], a["R2"], a["n"]))
    print()
    print("   Mismo indice, mismas huellas, mismo estado del terreno. Lo que")
    print("   diferencia estas filas es, en lo esencial, la longitud de onda.")
else:
    print("   Todavia no hay productos procesados en esa ventana de fechas.")
    print("   Faltaria procesar el BIOMASS del 28/02/2026 a gamma0 con las")
    print("   cuatro polarizaciones (grafo procesamiento_BIOMASS.xml).")
print()

# --- salidas -------------------------------------------------------------
sal = os.path.join(RESULTADOS, "04_Tablas")
os.makedirs(sal, exist_ok=True)


def escribir(nombre, filas):
    if not filas:
        return
    with open(os.path.join(sal, nombre), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print("   escrito: %s (%d filas)" % (nombre, len(filas)))


print("=" * 74)
print("SALIDAS")
print("=" * 74)
escribir("inventario_polarizaciones.csv", filas_inv)
escribir("indices_por_producto.csv", detalle)
escribir("ajustes_indices.csv", ajustes)
escribir("rfdi_antes_despues.csv", filas_rfdi)
escribir("comparacion_tres_bandas.csv", filas_tres)

with open(os.path.join(sal, "LEEME_indices.txt"), "w", encoding="utf-8") as f:
    f.write("INDICES POLARIMETRICOS DEL TP4 - %s\n" % AOI)
    f.write("=" * 60 + "\n\n")
    f.write("Formulas y autoria (NO son intercambiables; en el informe hay que\n")
    f.write("decir cual se uso):\n\n")
    f.write("  RVI quad-pol  8*HV/(HH+VV+2*HV)     Kim y van Zyl (2009),\n")
    f.write("                                      reproducida en el SAR Handbook\n")
    f.write("  RVI dual-pol  4*cruzada/(co+cruzada) Trudel, Charbonneau y\n")
    f.write("                                      Serrar (2012)\n")
    f.write("  RFDI          (HH-HV)/(HH+HV)       SAR Handbook, seccion 5.3\n\n")
    f.write("Metodo: el gamma0 se promedia sobre la ventana de %d m en escala\n"
            % ((2 * RADIO + 1) * 10))
    f.write("LINEAL y el indice se forma DESPUES, con esos promedios. Promediar\n")
    f.write("en decibeles sesgaria el resultado; promediar indices por pixel\n")
    f.write("seria inestable.\n\n")
    f.write("Advertencia (Mandal et al., 2020): los indices apoyados en la\n")
    f.write("intensidad de la polarizacion cruzada pueden dar un valor alto\n")
    f.write("aunque el dosel no este desarrollado. En la estepa, con 3,4 Mg/ha\n")
    f.write("de mediana, ese riesgo es concreto. Si aparece, el camino es el\n")
    f.write("DpRVI, que el GCOV de NISAR habilita sin trabajo extra.\n\n")
    f.write("Techo de la banda C (SAR Handbook, Tabla 4.1): la sensibilidad a\n")
    f.write("la altura del rodal se pierde por encima de UN METRO, contra diez\n")
    f.write("metros en banda L. Un cociente limpia ruido, no crea sensibilidad.\n")
print("   escrito: LEEME_indices.txt")
print()
solo_tif = sorted({p["sensor"] for p in prods if p["formato"] == "tif"})
if solo_tif:
    print("AVISO DE FORMATO")
    print("   Estos sensores se leyeron desde GeoTIFF porque no tienen .dim:")
    for s_ in solo_tif:
        print("      - %s" % s_)
    print("   Para los indices de INTENSIDAD (RVI, RFDI) da igual: son cocientes")
    print("   de gamma0 y no necesitan la fase. Pero el GeoTIFF pierde los")
    print("   metadatos, de modo que esos productos NO se pueden seguir")
    print("   procesando en SNAP: ni matriz de covarianza, ni descomposiciones,")
    print("   ni DpRVI. El producto principal del proyecto es el BEAM-DIMAP.")
    print()

print("SIGUIENTE PASO")
print("   Para completar la comparacion de tres bandas falta procesar a gamma0,")
print("   con las cuatro polarizaciones, los productos que hoy estan descargados")
print("   y sin procesar: los cinco SAOCOM quad-pol de la linea de base 2023-24,")
print("   las escenas quad-pol de ALOS-1 y el BIOMASS del 28/02/2026. El grafo")
print("   de BIOMASS ya esta corregido y no fija polarizaciones, de modo que")
print("   entrega las cuatro.")
