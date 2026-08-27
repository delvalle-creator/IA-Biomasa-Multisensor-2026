# -*- coding: utf-8 -*-
"""
TP5_03_validacion.py   ---> TERCER script del TP5.

QUE HACE
--------
Toma el mejor modelo de altura del TP5_02 y lo somete a las pruebas que un R2 de
validacion no contesta:

  1. POR SITIO      ¿funciona igual en el bosque que en la estepa?
  2. POR FRANJA     ¿donde se equivoca? El sesgo por franja de altura dice mas
                    que el RMSE global: un modelo puede tener buen R2 y estar
                    subestimando sistematicamente los arboles altos, que es
                    justamente donde esta la biomasa.
  3. PRE / POST     ¿el modelo ajustado ANTES del incendio sirve DESPUES?
                    Se aplica a las mismas huellas con el optico y el radar
                    posteriores al fuego. No hay verdad de campo post-incendio,
                    de modo que esto NO valida: MIDE EL CAMBIO. Un bosque quemado
                    tiene que dar altura predicha menor. Si no baja, el modelo
                    esta respondiendo a otra cosa.

POR QUE ESTE SCRIPT EXISTE
--------------------------
Porque el criterio de evaluacion del TP5 no es "que numero dio" sino "distinguir
mejora real de sobreajuste". Un modelo que anda bien en promedio y mal en la cola
alta es inservible para biomasa, y el R2 no lo delata. El sesgo por franja, si.

ENTRADA   04_Tablas_de_trabajo/TP5_dataset_<AOI>.csv          (del TP5_01)
          02_Subsets_SNAP_QGIS post-incendio, via TP3 y TP4   (para el punto 3)
SALIDA    05_Resultados/04_Tablas/TP5_validacion_sitio.csv
          05_Resultados/04_Tablas/TP5_validacion_franjas.csv
          05_Resultados/04_Tablas/TP5_cambio_pre_post.csv
USO       python TP5_03_validacion.py
"""
import csv
import glob
import os
import sys

import numpy as np
import rasterio

AQUI = os.path.dirname(os.path.abspath(__file__))
TP5 = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROY = os.path.abspath(os.path.join(TP5, ".."))
SUBSETS = os.path.join(TP5, "04_Tablas_de_trabajo")
TABLAS = os.path.join(TP5, "05_Resultados", "04_Tablas")
S2 = os.path.join(PROY, "TP3_Datos_Opticos", "02_Subsets_SNAP_QGIS", "Sentinel_2")
I4 = os.path.join(PROY, "TP4_Radar_SAR", "02_Subsets_SNAP_QGIS")

OPTICO = ["NDVI", "EVI", "NDMI", "NBR"]
SAR = ["g0_C_VH", "g0_C_VV", "g0_L_SAOCOM_HH", "g0_L_SAOCOM_HV",
       "g0_L_NISAR_HH", "g0_L_NISAR_HV", "g0_L_PALSAR2_HH", "g0_L_PALSAR2_HV"]
MODELO = OPTICO + SAR          # el modelo del practico: optico + radar, SIN LiDAR
# Sin LiDAR a proposito: el objetivo es predecir la altura DONDE NO HAY GEDI, que
# es todo el terreno entre orbita y orbita. Un modelo que necesita rh95 de entrada
# no sirve para eso. El de optico+SAR+LiDAR de TP5_02 mide otra cosa.
CORTES = [0, 3, 6, 9, 12, 15, 18, 21, 25, 30]
ESC_POST = "*20260305*.tif"
SCL_MALAS = {0, 1, 3, 8, 9, 10, 11}
B2, B4, B8, B11, B12, SCL = 1, 3, 7, 9, 10, 11
# El radar post-incendio es del 27/02/2026, seis dias antes que la escena optica
# del 05/03. Se declara: no son la misma fecha, y en radar seis dias de diferencia
# pueden traer un cambio de humedad de suelo. NISAR y PALSAR-2 no tienen
# adquisicion posterior al fuego, de modo que la comparacion pre/post se hace con
# las variables que SI existen en las dos fechas: optico, Sentinel-1 y SAOCOM.
POST_RADAR = [("g0_C_VH", "Sentinel_1/*/%s/S1_GRD/*20260227*.tif", 1),
              ("g0_C_VV", "Sentinel_1/*/%s/S1_GRD/*20260227*.tif", 2),
              ("g0_L_SAOCOM_HH", "SAOCOM/*/%s/*/*20260227*.tif", 1),
              ("g0_L_SAOCOM_HV", "SAOCOM/*/%s/*/*20260227*.tif", 2)]


def coma(x, d=2):
    return ("%.*f" % (d, x)).replace(".", ",")


def cargar():
    # OJO CON EL NOMBRE DEL ARCHIVO (corregido el 31/07/2026)
    # ------------------------------------------------------------------
    # Antes esto decia   f.startswith("TP5_dataset_") and f.endswith(".csv")
    # y funcionaba mientras en 04_Tablas_de_trabajo solo estuvieran los dos datasets.
    # Cuando el TP2_09 empezo a escribir TP5_dataset_<AOI>_cobertura.csv en la
    # misma carpeta, ese prefijo paso a capturar TAMBIEN las copias con las
    # columnas de cobertura, y cada huella entro DOS VECES. El sintoma es
    # silencioso: el R2 y los coeficientes no cambian -duplicar todas las filas
    # no mueve un ajuste por minimos cuadrados- pero los n informados salen al
    # doble y cualquier error estandar sale dividido por raiz de 2.
    #
    # Ahora se nombran los dos archivos de forma exacta, y ademas se comprueba
    # que ninguna huella aparezca repetida. Si aparece, el script se detiene.
    filas = []
    for aoi in ("BOSQUE_NW_02", "ESTEPA_NW_02"):
        ruta = os.path.join(SUBSETS, "TP5_dataset_%s.csv" % aoi)
        if not os.path.isfile(ruta):
            continue
        with open(ruta, newline="", encoding="utf-8") as h:
            filas.extend(list(csv.DictReader(h)))
    if not filas:
        sys.exit("No hay dataset. Ejecute antes:  python TP5_01_dataset.py")

    vistas, repetidas = set(), 0
    for r in filas:
        sn = r.get("shot_number", "")
        if sn in vistas:
            repetidas += 1
        vistas.add(sn)
    if repetidas:
        sys.exit("ERROR: %d huellas repetidas en el dataset. No se puede seguir."
                 % repetidas)
    out = []
    for r in filas:
        if not r.get("particion"):
            continue
        try:
            d = {k: float(r[k]) for k in MODELO + ["rh95"]}
        except (KeyError, ValueError):
            continue
        d.update({"particion": r["particion"], "sitio": r["sitio"], "aoi": r["aoi"],
                  "este": float(r["este_utm19s"]), "norte": float(r["norte_utm19s"])})
        out.append(d)
    return out


def ajustar(entrena):
    X = np.array([[d[c] for c in MODELO] for d in entrena])
    A = np.column_stack([X, np.ones(len(entrena))])
    y = np.array([d["rh95"] for d in entrena])
    beta, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    return beta


def predecir(beta, filas, cols=None):
    cols = cols or MODELO
    X = np.array([[d[c] for c in cols] for d in filas])
    return np.column_stack([X, np.ones(len(filas))]) @ beta


def metricas(y, p):
    ss = ((y - y.mean()) ** 2).sum()
    return (1 - ((y - p) ** 2).sum() / ss if ss > 0 else float("nan"),
            float(np.sqrt(((y - p) ** 2).mean())), float((p - y).mean()))


print(__doc__)
os.makedirs(TABLAS, exist_ok=True)
D = cargar()
entrena = [d for d in D if d["particion"] == "entrenamiento"]
valida = [d for d in D if d["particion"] == "validacion"]
beta = ajustar(entrena)
print("=" * 72)
print("MODELO: altura del dosel a partir de optico + radar (%d variables)" % len(MODELO))
print("=" * 72)
print("   ajustado con %d huellas de entrenamiento, de los dos sitios" % len(entrena))
print("   SIN variables de GEDI entre las predictoras: el modelo tiene que servir")
print("   donde NO hay huellas, que es casi todo el terreno.")

# ---------------------------------------------------------------- 1. por sitio
print()
print("1. POR SITIO")
f1 = []
for et, sub in (("los dos juntos", valida),
                ("bosque", [d for d in valida if d["sitio"] == "bosque"]),
                ("estepa", [d for d in valida if d["sitio"] == "estepa"])):
    if len(sub) < 10:
        continue
    y = np.array([d["rh95"] for d in sub]); p = predecir(beta, sub)
    r2, rm, sesgo = metricas(y, p)
    print("   %-16s n=%4d   R2 %5.3f   RMSE %4.2f m   sesgo %+5.2f m"
          % (et, len(sub), r2, rm, sesgo))
    f1.append({"grupo": et, "n": len(sub), "R2": "%.4f" % r2,
               "RMSE_m": "%.3f" % rm, "sesgo_m": "%.3f" % sesgo})

# ------------------------------------------------------------- 2. por franja
print()
print("2. POR FRANJA DE ALTURA   (donde se equivoca, que es lo que el R2 esconde)")
f2 = []
for sitio in ("bosque", "estepa"):
    sub = [d for d in valida if d["sitio"] == sitio]
    if len(sub) < 20:
        continue
    y = np.array([d["rh95"] for d in sub]); p = predecir(beta, sub)
    print("   %s" % sitio)
    print("      %-10s %5s %10s %10s" % ("franja", "n", "sesgo", "RMSE"))
    for i in range(len(CORTES) - 1):
        m = (y >= CORTES[i]) & (y < CORTES[i + 1])
        if m.sum() < 5:
            continue
        s = float((p[m] - y[m]).mean()); r = float(np.sqrt(((y[m] - p[m]) ** 2).mean()))
        print("      %2d-%2d m %6d %8s m %8s m" % (CORTES[i], CORTES[i + 1], m.sum(),
                                                   coma(s), coma(r)))
        f2.append({"sitio": sitio, "franja": "%d-%d" % (CORTES[i], CORTES[i + 1]),
                   "n": int(m.sum()), "sesgo_m": "%.3f" % s, "RMSE_m": "%.3f" % r})
    alto = y >= 15
    if alto.sum() >= 5:
        print("      -> en las huellas de mas de 15 m (n=%d) el sesgo es %s m"
              % (alto.sum(), coma(float((p[alto] - y[alto]).mean()))))
        print("         Si es muy negativo, el modelo SUBESTIMA los arboles altos,")
        print("         que es justo donde esta la biomasa. Hay que declararlo.")

for nombre, filas_ in (("TP5_validacion_sitio", f1), ("TP5_validacion_franjas", f2)):
    if filas_:
        with open(os.path.join(TABLAS, nombre + ".csv"), "w", newline="",
                  encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas_[0])); w.writeheader(); w.writerows(filas_)

# --------------------------------------------------------- 3. pre contra post
print()
print("3. PRE CONTRA POST INCENDIO")
print("   No hay verdad de campo despues del fuego: esto NO valida el modelo,")
print("   MIDE EL CAMBIO. El bosque quemado tiene que bajar; la estepa, no.")


def indices(aoi, patron):
    h = [x for x in sorted(glob.glob(os.path.join(S2, "0[23]_*", aoi, patron)))]
    if not h:
        return None, None
    with rasterio.open(h[0]) as d:
        T = d.transform
        az = d.read(B2).astype("f4"); ro = d.read(B4).astype("f4")
        ni = d.read(B8).astype("f4"); s1 = d.read(B11).astype("f4")
        s2 = d.read(B12).astype("f4")
        val = (~np.isin(d.read(SCL), list(SCL_MALAS))) & (ni > 0) & (ro > 0)

    def norm(a, b):
        den = a + b
        return np.where(val & (den != 0), (a - b) / np.where(den == 0, 1, den), np.nan)
    den = ni + 6 * ro - 7.5 * az + 1
    return ({"NDVI": norm(ni, ro), "NDMI": norm(ni, s1), "NBR": norm(ni, s2),
             "EVI": np.clip(np.where(val & (den != 0),
                                     2.5 * (ni - ro) / np.where(den == 0, 1, den),
                                     np.nan), -1, 1)}, T)


def ventana(a, T, e, n, radio, potencia):
    ny, nx = a.shape
    c = int((e - T.c) / T.a); f = int((n - T.f) / T.e)
    if not (radio <= c < nx - radio and radio <= f < ny - radio):
        return None
    w = a[f - radio:f + radio + 1, c - radio:c + radio + 1]; w = w[np.isfinite(w)]
    if w.size == 0:
        return None
    return float(10 * np.log10(np.mean(10 ** (w / 10.0)))) if potencia else float(w.mean())


f3 = []
for aoi in sorted(set(d["aoi"] for d in D)):
    sub = [d for d in D if d["aoi"] == aoi]
    IXp, Tp = indices(aoi, ESC_POST)
    if IXp is None:
        print("   %s: falta la escena optica post-incendio, se omite" % aoi)
        continue
    RADp = {}
    for col, patron, banda in POST_RADAR:
        h = [x for x in sorted(glob.glob(os.path.join(I4, patron % aoi))) if "_mask" not in x]
        if not h:
            continue
        with rasterio.open(h[0]) as d_:
            a = d_.read(banda).astype("f8"); Tr = d_.transform
        sal = np.full(a.shape, np.nan); np.log10(a, where=a > 0, out=sal)
        RADp[col] = (np.where(a > 0, 10 * sal, np.nan), Tr)
    if len(RADp) < len(POST_RADAR):
        print("   %s: falta parte del radar post-incendio." % aoi)
        print("      Se compara SOLO con las variables que existen en las dos fechas.")
    cols = OPTICO + sorted(RADp)
    if len(cols) < 5:
        print("   %s: no alcanza para comparar, se omite" % aoi)
        continue
    ent = [d for d in D if d["particion"] == "entrenamiento"]
    A = np.column_stack([np.array([[d[c] for c in cols] for d in ent]), np.ones(len(ent))])
    bb, _, _, _ = np.linalg.lstsq(A, np.array([d["rh95"] for d in ent]), rcond=None)
    pre, post = [], []
    for d in sub:
        v = []
        for c in OPTICO:
            v.append(ventana(IXp[c], Tp, d["este"], d["norte"], 1, False))
        for c in sorted(RADp):
            a, Tr = RADp[c]
            v.append(ventana(a, Tr, d["este"], d["norte"], 7, True))
        if any(x is None for x in v):
            continue
        pre.append(np.dot(np.array([d[c] for c in cols] + [1.0]), bb))
        post.append(np.dot(np.array(v + [1.0]), bb))
    if len(pre) < 20:
        print("   %s: pocas huellas con las dos fechas (%d), se omite" % (aoi, len(pre)))
        continue
    pre = np.array(pre); post = np.array(post)
    print("   %-14s n=%4d   altura predicha:  pre %s m -> post %s m   cambio %s m"
          % (aoi, len(pre), coma(float(np.median(pre))), coma(float(np.median(post))),
             coma(float(np.median(post - pre)))))
    f3.append({"aoi": aoi, "n": len(pre), "variables": " ".join(cols),
               "altura_pre_mediana_m": "%.3f" % np.median(pre),
               "altura_post_mediana_m": "%.3f" % np.median(post),
               "cambio_mediano_m": "%.3f" % np.median(post - pre)})
if f3:
    with open(os.path.join(TABLAS, "TP5_cambio_pre_post.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(f3[0])); w.writeheader(); w.writerows(f3)
    print()
    print("   El bosque tiene que dar un cambio NEGATIVO y la estepa uno cercano a")
    print("   cero. Si la estepa tambien baja, el modelo esta leyendo estacionalidad")
    print("   o humedad, no fuego, y hay que decirlo antes de seguir.")

print()
print("SIGUIENTE PASO:  python TP5_04_biomasa_quemada.py")
