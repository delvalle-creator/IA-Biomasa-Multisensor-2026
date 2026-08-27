# -*- coding: utf-8 -*-
"""
TP5_06_diagnostico_del_piso.py   ---> de donde sale el piso del ensayo nulo.

LA PREGUNTA
-----------
El TP5_04 mide, sobre la clase «Sin cambio» -terreno que NO se quemo-, una
variacion aparente de biomasa de **-10,25 Mg/ha en el bosque**, es decir una
ganancia. Deberia dar cero. Ese numero es el piso de ruido del metodo completo, y
es grande: las clases quemadas pierden entre 11,5 y 15,5 Mg/ha, o sea apenas
entre 1,1 y 1,5 veces el piso.

Mientras no se sepa DE DONDE sale, no se puede decidir que hacer con el. Restarlo
a ciegas subiria la cifra central del practico, que es justo la direccion que a
uno le conviene, y eso obliga a ser mas exigente, no menos.

LO QUE YA SE DESCARTO, MIDIENDO
-------------------------------
La primera sospecha fue el desfase fenologico: la escena PRE es del 25/11/2025
-primavera- y la POST del 05/03/2026 -verano-, y la lenga y el nire son
caducifolias. **Es falso.** Sobre el bosque no quemado el NDVI mediano da 0,8679
en noviembre y 0,8654 en marzo: 0,0031 de diferencia. El NBR difiere 0,0216. El
dosel es opticamente el mismo en las dos fechas. (Ver el LEEME de
TP3_Datos_Opticos/02_Subsets_SNAP_QGIS/Sentinel_2/02_pre_incendio_2025_26/.)

LO QUE QUEDA, Y QUE MIDE ESTE SCRIPT
------------------------------------
Si el optico no se movio, el piso tiene que venir del OTRO grupo de predictores.
Los del radar del PRE son del **10/01/2026** y los del POST del **27/02/2026**:
siete semanas en las que la humedad del suelo pudo cambiar, y con ella el gamma0.

El script ajusta el MISMO modelo de altura con tres juegos de variables y compara
el piso que produce cada uno:

    OPTICO         NDVI, EVI, NDMI, NBR
    SAR            gamma0 de banda C y de banda L
    OPTICO+SAR     los ocho juntos  (es el modelo que usa hoy el practico)

Si el piso se derrumba al quitar el radar, la causa son las fechas del radar y
queda identificada. Si no se mueve, la causa esta en otra parte y habra que
buscarla en la propia alometria.

POR QUE UN METRO ALCANZA PARA EXPLICAR TODO EL PISO
---------------------------------------------------
La conversion de altura a biomasa es alometrica, con exponente 2,605. Sobre un
dosel de 8,6 m y un stock de unos 40 Mg/ha, un corrimiento SISTEMATICO de un solo
metro en la altura predicha produce del orden de +13 Mg/ha. Por eso el script
informa, ademas del cambio de biomasa, **el cambio de ALTURA en metros**: es la
magnitud fisica donde el problema se ve sin amplificar.

ENTRADA   04_Tablas_de_trabajo/TP5_dataset_<AOI>.csv
          las mismas escenas opticas y de radar que usa el TP5_04
SALIDA    05_Resultados/04_Tablas/TP5_diagnostico_del_piso.csv
          No toca ningun resultado del practico: solo diagnostica.

USO (entorno conda 'aoi'):   python TP5_06_diagnostico_del_piso.py
"""
import csv
import glob
import os
import sys

import numpy as np
import rasterio

AQUI = os.path.dirname(os.path.abspath(__file__))
TP5 = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
PROY = os.path.abspath(os.path.join(TP5, ".."))
SUBSETS = os.path.join(TP5, "04_Tablas_de_trabajo")
TABLAS = os.path.join(TP5, "05_Resultados", "04_Tablas")
S2 = os.path.join(PROY, "TP3_Datos_Opticos", "02_Subsets_SNAP_QGIS", "Sentinel_2")
I4 = os.path.join(PROY, "TP4_Radar_SAR", "02_Subsets_SNAP_QGIS")

OPTICO = ["NDVI", "EVI", "NDMI", "NBR"]
SIN_EVI = ["NDVI", "NDMI", "NBR"]
SAR_PRE = ["g0_C_VH", "g0_C_VV", "g0_L_SAOCOM_HH", "g0_L_SAOCOM_HV"]

# POR QUE SE PRUEBA TAMBIEN SIN EVI  (medido el 31/07/2026)
# ---------------------------------------------------------
# Sobre el bosque NO quemado, entre el 25/11/2025 y el 05/03/2026, TODAS las
# reflectancias bajan: azul -31 %, verde -25 %, rojo -14 %, NIR -16 %, SWIR -22 %.
# Es una caida de banda ancha, y en terreno montanoso con el sol mas bajo en marzo
# que en noviembre eso es sombreado topografico, no cambio de la vegetacion.
#
# Los indices normalizados absorben esa caida porque son cocientes: el NDVI se
# mueve 0,0037, el NBR 0,0216 y el NDMI 0,0316. Pero el EVI NO es un cociente
# puro: lleva un "+1" en el denominador
#
#     EVI = 2,5 (NIR - ROJO) / (NIR + 6 ROJO - 7,5 AZUL + 1)
#
# y ese termino constante le rompe la invariancia de escala. Si todas las bandas
# se multiplican por un factor menor que uno, el numerador se escala y el
# denominador no del todo. Resultado medido: el EVI cae 0,0821, veinte veces mas
# que el NDVI. Como el modelo de altura usa EVI, ese corrimiento entra entero en
# la prediccion.
# INDICES DE COCIENTE DEL RADAR  (agregados el 31/07/2026 a pedido del docente)
# ---------------------------------------------------------------------------
# Si el problema del optico fue que el EVI no es invariante a la iluminacion,
# la pregunta obvia es que pasa con los indices de COCIENTE del radar, que por
# construccion si lo son. Y el radar, ademas, no depende del sol en absoluto.
#
# Con lo que hay para 2026 -Sentinel-1 dual VV/VH y SAOCOM dual HH/HV- se pueden
# calcular, para las DOS fechas del incendio:
#
#     RFDI = (sigma_co - sigma_cruz) / (sigma_co + sigma_cruz)
#     Span = sigma_co + sigma_cruz            (potencia total, en dB)
#
# UNA ADVERTENCIA ALGEBRAICA QUE CONVIENE SABER. En dual-pol, el RVI y el RFDI
# NO son variables distintas. Con la definicion dual habitual
#
#     RVI = 4 sigma_cruz / (sigma_co + sigma_cruz)
#
# y como  1 - RFDI = 2 sigma_cruz / (sigma_co + sigma_cruz),  resulta
#
#     RVI = 2 (1 - RFDI)
#
# es decir, uno es funcion lineal exacta del otro. Meter los dos en el mismo
# modelo es meter la misma variable dos veces: la matriz queda singular y el
# ajuste no gana nada. Por eso aca va el RFDI, y el RVI queda declarado como lo
# que es, su equivalente lineal. Con quad-pol completo -HH, VV, HV- SI serian
# distintos, pero las unicas escenas quad-pol del proyecto son de enero de 2024,
# tres anios antes del incendio, y no forman par pre/post.
#
# LO QUE HAY QUE VIGILAR: la auditoria midio que RVI, RFDI y CSI tienen
# correlacion de rangos entre fechas de 0,00 a 0,11, mientras que el Span da 0,74
# a 0,91. Un cociente de dos cantidades con moteado es mucho mas ruidoso que
# cualquiera de las dos por separado. PERO esa medicion se hizo a resolucion
# nativa, y aca el radar se promedia en ventanas de 15x15 EN POTENCIA -unas 225
# vistas-, que es justamente el remedio del moteado. Por eso vale la pena medirlo
# en estas condiciones y no dar por sentado ninguno de los dos resultados.
COCIENTES = ["RFDI_C", "RFDI_L"]
SPANES = ["Span_C", "Span_L"]

JUEGOS = [("OPTICO", OPTICO),
          ("OPTICO sin EVI", SIN_EVI),
          ("SAR", SAR_PRE),
          ("RFDI C y L", COCIENTES),
          ("Span C y L", SPANES),
          ("RFDI + Span", COCIENTES + SPANES),
          ("OPTICO+SAR", OPTICO + SAR_PRE),
          ("sin EVI + SAR", SIN_EVI + SAR_PRE)]


def derivados(v):
    """Agrega RFDI y Span de banda C y de banda L a un diccionario de gamma0 en dB.

    Todo se hace EN POTENCIA. Sumar o dividir decibeles no tiene sentido fisico:
    el dB es logaritmico. Se pasa a potencia, se opera, y el Span se devuelve en
    dB para que quede en la misma escala que el resto de los predictores.
    """
    def pot(x):
        return 10.0 ** (x / 10.0)

    for eti, co, cruz in [("C", "g0_C_VV", "g0_C_VH"), ("L", "g0_L_SAOCOM_HH", "g0_L_SAOCOM_HV")]:
        if co not in v or cruz not in v:
            continue
        a, b = pot(v[co]), pot(v[cruz])
        s = a + b
        v["RFDI_" + eti] = (a - b) / s if s > 0 else float("nan")
        v["Span_" + eti] = 10.0 * np.log10(s) if s > 0 else float("nan")
        # el RVI dual es 2(1 - RFDI): se deja calculado por si se quiere informar,
        # pero NO se usa como predictor porque seria colineal con el RFDI.
        v["RVI_" + eti] = 2.0 * (1.0 - v["RFDI_" + eti])
    return v

PRE, POST = "*20251125*.tif", "*20260305*.tif"
POST_RADAR = [("g0_C_VH", "Sentinel_1/*/%s/S1_GRD/*20260227*.tif", 1),
              ("g0_C_VV", "Sentinel_1/*/%s/S1_GRD/*20260227*.tif", 2),
              ("g0_L_SAOCOM_HH", "SAOCOM/*/%s/*/*20260227*.tif", 1),
              ("g0_L_SAOCOM_HV", "SAOCOM/*/%s/*/*20260227*.tif", 2)]
SCL_MALAS = {0, 1, 3, 8, 9, 10, 11}
B2, B4, B8, B11, B12, SCL = 1, 3, 7, 9, 10, 11
SEVERIDAD = [("Regeneración alta", -np.inf, -0.250), ("Regeneración baja", -0.250, -0.100),
             ("Sin cambio", -0.100, 0.100), ("Severidad baja", 0.100, 0.270),
             ("Severidad moderada-baja", 0.270, 0.440),
             ("Severidad moderada-alta", 0.440, 0.660), ("Severidad alta", 0.660, np.inf)]
QUEMADAS = [n for n, _, _ in SEVERIDAD if n.startswith("Severidad")]


def coma(x, d=1):
    return ("%.*f" % (d, x)).replace(".", ",")


def cargar():
    filas = []
    for aoi in ("BOSQUE_NW_02", "ESTEPA_NW_02"):
        ruta = os.path.join(SUBSETS, "TP5_dataset_%s.csv" % aoi)
        if os.path.isfile(ruta):
            with open(ruta, newline="", encoding="utf-8") as h:
                filas.extend(list(csv.DictReader(h)))
    if not filas:
        sys.exit("No hay dataset. Ejecute antes:  python TP5_01_dataset.py")
    vistas, rep = set(), 0
    for r in filas:
        if r.get("shot_number", "") in vistas:
            rep += 1
        vistas.add(r.get("shot_number", ""))
    if rep:
        sys.exit("ERROR: %d huellas repetidas en el dataset." % rep)
    return filas


def bandas(aoi, patron):
    h = sorted(glob.glob(os.path.join(S2, "0[23]_*", aoi, patron)))
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
    return {"NDVI": norm(ni, ro), "NDMI": norm(ni, s1), "NBR": norm(ni, s2),
            "EVI": np.clip(np.where(val & (den != 0),
                                    2.5 * (ni - ro) / np.where(den == 0, 1, den), np.nan),
                           -1, 1)}, T


def radar(patron, aoi, banda):
    h = [x for x in sorted(glob.glob(os.path.join(I4, patron % aoi))) if "_mask" not in x]
    if not h:
        return None, None
    with rasterio.open(h[0]) as d:
        a = d.read(banda).astype("f8"); T = d.transform
    sal = np.full(a.shape, np.nan)
    np.log10(a, where=a > 0, out=sal)
    return np.where(a > 0, 10 * sal, np.nan), T


def ventana(a, T, e, n, radio, potencia):
    ny, nx = a.shape
    c = int((e - T.c) / T.a); f = int((n - T.f) / T.e)
    if not (radio <= c < nx - radio and radio <= f < ny - radio):
        return None
    w = a[f - radio:f + radio + 1, c - radio:c + radio + 1]; w = w[np.isfinite(w)]
    if w.size == 0:
        return None
    return float(10 * np.log10(np.mean(10 ** (w / 10.0)))) if potencia else float(w.mean())


def ajuste(X, y):
    beta, _, _, _ = np.linalg.lstsq(np.column_stack([X, np.ones(len(X))]), y, rcond=None)
    return beta


def aplicar(beta, X):
    return np.column_stack([X, np.ones(len(X))]) @ beta


print(__doc__)
os.makedirs(TABLAS, exist_ok=True)
filas = cargar()
salida = []

for aoi in sorted(set(r["aoi"] for r in filas)):
    print("=" * 78)
    print(aoi)
    print("=" * 78)
    sub = [r for r in filas if r["aoi"] == aoi and r.get("particion")]

    TODAS = OPTICO + SAR_PRE
    D = []
    for r in sub:
        try:
            d = {k: float(r[k]) for k in TODAS + ["rh95"]}
        except (KeyError, ValueError):
            continue
        d["particion"] = r["particion"]
        d["este"] = float(r["este_utm19s"]); d["norte"] = float(r["norte_utm19s"])
        d["agbd"] = r.get("agbd_Mg_ha", "")
        derivados(d)
        D.append(d)
    ent = [d for d in D if d["particion"] == "entrenamiento"]
    val = [d for d in D if d["particion"] == "validacion"]
    if len(ent) < 30 or len(val) < 10:
        print("   muestra insuficiente, se omite"); continue

    # alometria: no depende del juego de predictores, se ajusta una sola vez
    con = [d for d in D if d["agbd"] and float(d["agbd"]) > 0 and d["rh95"] > 0
           and d["particion"] == "entrenamiento"]
    if len(con) < 20:
        print("   pocas huellas con biomasa, se omite"); continue
    b_, la = np.polyfit(np.log([d["rh95"] for d in con]),
                        np.log([float(d["agbd"]) for d in con]), 1)
    a_ = float(np.exp(la))
    print("   alometría común a los tres juegos:  biomasa = %s · altura^%s"
          % (coma(a_, 2), coma(b_, 3)))

    def biomasa(h):
        return a_ * np.clip(np.asarray(h, dtype="f8"), 0.1, None) ** b_

    ixp, Tp = bandas(aoi, PRE); ixq, Tq = bandas(aoi, POST)
    if ixp is None or ixq is None:
        print("   faltan escenas ópticas, se omite"); continue
    dnbr = ixp["NBR"] - ixq["NBR"]
    RADq = {}
    for col, patron, banda in POST_RADAR:
        a, T = radar(patron, aoi, banda)
        if a is not None:
            RADq[col] = (a, T)

    # los valores POST de cada huella, una sola vez para los tres juegos
    post = {}
    for i, d in enumerate(D):
        v = {}
        ok = True
        for c in OPTICO:
            x = ventana(ixq[c], Tq, d["este"], d["norte"], 1, False)
            if x is None:
                ok = False; break
            v[c] = x
        if ok:
            for c in SAR_PRE:
                x = ventana(RADq[c][0], RADq[c][1], d["este"], d["norte"], 7, True) \
                    if c in RADq else None
                if x is None:
                    ok = False; break
                v[c] = x
        if not ok:
            continue
        cd = ventana(dnbr, Tp, d["este"], d["norte"], 1, False)
        if cd is None or not np.isfinite(cd):
            continue
        derivados(v)
        v["clase"] = next(n for n, lo, hi in SEVERIDAD if lo <= cd < hi)
        post[i] = v

    print("   huellas con PRE y POST completos: %d de %d" % (len(post), len(D)))
    print()
    print("   %-16s %6s %9s %9s %9s %11s %11s" %
          ("juego", "s1 m", "h_pre m", "h_post m", "Δh m", "Δbiomasa", "señal/piso"))
    print("   %-16s %6s %9s %9s %9s %11s %11s" %
          ("", "", "mediana", "mediana", "mediana", "Mg/ha", ""))

    for nombre, MOD in JUEGOS:
        if any(c not in ent[0] for c in MOD):
            print("   %-16s faltan variables, se omite" % nombre); continue
        beta = ajuste(np.array([[d[c] for c in MOD] for d in ent]),
                      np.array([d["rh95"] for d in ent]))
        s1 = float(np.sqrt((( np.array([d["rh95"] for d in val])
                             - aplicar(beta, np.array([[d[c] for c in MOD] for d in val])))
                            ** 2).mean()))
        reg = {}
        for i, v in post.items():
            d = D[i]
            hp = float(aplicar(beta, np.array([[d[c] for c in MOD]]))[0])
            hq = float(aplicar(beta, np.array([[v[c] for c in MOD]]))[0])
            reg.setdefault(v["clase"], []).append(
                (hp, hq, float(biomasa([hp])[0]) - float(biomasa([hq])[0])))

        sc = reg.get("Sin cambio", [])
        if not sc:
            print("   %-16s sin huellas en la clase «Sin cambio»" % nombre); continue
        piso = float(np.median([x[2] for x in sc]))
        dh = float(np.median([x[1] - x[0] for x in sc]))
        quem = [x[2] for n in QUEMADAS for x in reg.get(n, [])]
        senal = float(np.median(quem)) if quem else float("nan")
        razon = abs(senal / piso) if piso else float("inf")
        print("   %-16s %6s %9s %9s %9s %11s %11s"
              % (nombre, coma(s1, 2),
                 coma(float(np.median([x[0] for x in sc])), 2),
                 coma(float(np.median([x[1] for x in sc])), 2),
                 coma(dh, 2), coma(piso, 2), coma(razon, 2)))
        salida.append({"aoi": aoi, "juego": nombre, "n_variables": len(MOD),
                       "s1_altura_m": "%.3f" % s1, "n_sin_cambio": len(sc),
                       "h_pre_mediana_m": "%.3f" % float(np.median([x[0] for x in sc])),
                       "h_post_mediana_m": "%.3f" % float(np.median([x[1] for x in sc])),
                       "delta_h_mediana_m": "%.3f" % dh,
                       "piso_Mg_ha": "%.3f" % piso,
                       "senal_quemado_Mg_ha": "%.3f" % senal,
                       "razon_senal_piso": "%.3f" % razon})
    print()

if salida:
    ruta = os.path.join(TABLAS, "TP5_diagnostico_del_piso.csv")
    with open(ruta, "w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(salida[0].keys()))
        w.writeheader(); w.writerows(salida)
    print("tabla  TP5_diagnostico_del_piso.csv  (%d filas)" % len(salida))

print()
print("COMO SE LEE ESTA TABLA")
print("  - 'piso' es la variacion aparente de biomasa sobre terreno NO quemado.")
print("    Deberia dar cero. Cuanto mas cerca de cero, mejor el metodo.")
print("  - 'delta h' es ese mismo piso ANTES de que la alometria lo amplifique.")
print("    Ahi se ve el problema en metros, que es donde se puede razonar.")
print("  - 'senal/piso' es cuantas veces la perdida en lo quemado supera al piso.")
print("    Por debajo de 2 el resultado no se distingue del ruido del metodo.")
print("  - Comparar OPTICO contra OPTICO sin EVI: si el piso se derrumba al sacar")
print("    el EVI, queda probado que el corrimiento lo introduce ese indice, por")
print("    no ser invariante a la iluminacion.")
print("  - Comparar SAR contra los juegos con optico: el radar no depende del sol.")
print("  - RFDI y Span: los cocientes del radar SI son invariantes a un factor")
print("    multiplicativo, que es lo que le falta al EVI. Lo que hay que mirar en")
print("    ellos es otra cosa: si el moteado los arruina. El Span, que es una suma,")
print("    deberia ser mas estable que el RFDI, que es un cociente.")
print("  - El RVI dual no figura porque es 2(1-RFDI): la misma variable.")
