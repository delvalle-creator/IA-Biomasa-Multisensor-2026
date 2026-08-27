# -*- coding: utf-8 -*-
"""
TP5_04_biomasa_quemada.py   ---> CUARTO script del TP5.

QUE HACE
--------
Es el ultimo eslabon de la cadena del curso: convierte la ALTURA predicha en
BIOMASA, cruza el resultado con las clases de severidad del incendio y estima
cuanta biomasa se perdio, CON SU INCERTIDUMBRE.

POR QUE LA BIOMASA ENTRA RECIEN ACA, Y NO COMO OBJETIVO DEL MODELO
------------------------------------------------------------------
Porque la biomasa del GEDI L4A no es una medicion independiente: la NASA la
modelo a partir de las metricas de altura del L2A. Ajustar un modelo que prediga
`agbd` con `rh95` adentro es reconstruir el modelo de la NASA y llamarlo sinergia.
Poniendola al final, la cadena queda explicita y auditable:

    optico + radar  --modelo del TP5_02-->  ALTURA
    ALTURA          --relacion alometrica-->  BIOMASA

LAS TRES FUENTES DE ERROR, Y POR QUE SE SUMAN ASI
--------------------------------------------------
  s1  error del modelo de altura            (RMSE de TP5_03, por sitio)
  s2  error de la conversion altura-biomasa (RMSE de este ajuste, en validacion)
  s3  error del propio L4A                  (su error estandar mediano por disparo)

s1 esta en metros y hay que pasarlo a Mg/ha antes de sumarlo: se propaga por la
derivada de la relacion, db/dh. Las tres se combinan en cuadratura porque son
independientes entre si. NO se suman directamente: eso exageraria el resultado.

    s_total = raiz( (db/dh * s1)^2 + s2^2 + s3^2 )

LO QUE ESTE SCRIPT NO PUEDE ARREGLAR, Y DECLARA
------------------------------------------------
El TP5_03 midio que el modelo de altura SUBESTIMA los arboles altos: por encima
de 15 m el sesgo es de casi diez metros. Como la biomasa crece mas que
proporcionalmente con la altura, ese sesgo se amplifica al convertir. Por eso el
script informa SIEMPRE dos columnas: la biomasa desde la altura PREDICHA y la
biomasa desde la altura OBSERVADA por GEDI. La diferencia entre ambas es el
tamano del problema, y no hay que esconderla.

ENTRADA   04_Tablas_de_trabajo/TP5_dataset_<AOI>.csv
          Escenas Sentinel-2 pre y post, para el dNBR y las clases de severidad
SALIDA    05_Resultados/04_Tablas/TP5_biomasa_por_severidad.csv
          05_Resultados/04_Tablas/TP5_cadena_de_error.csv
USO       python TP5_04_biomasa_quemada.py
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
SAR_PRE = ["g0_C_VH", "g0_C_VV", "g0_L_SAOCOM_HH", "g0_L_SAOCOM_HV"]
MODELO = OPTICO + SAR_PRE      # las que existen ANTES y DESPUES del fuego
PRE, POST = "*20251125*.tif", "*20260305*.tif"
POST_RADAR = [("g0_C_VH", "Sentinel_1/*/%s/S1_GRD/*20260227*.tif", 1),
              ("g0_C_VV", "Sentinel_1/*/%s/S1_GRD/*20260227*.tif", 2),
              ("g0_L_SAOCOM_HH", "SAOCOM/*/%s/*/*20260227*.tif", 1),
              ("g0_L_SAOCOM_HV", "SAOCOM/*/%s/*/*20260227*.tif", 2)]
SCL_MALAS = {0, 1, 3, 8, 9, 10, 11}
B2, B4, B8, B11, B12, SCL = 1, 3, 7, 9, 10, 11
# Los mismos SIETE umbrales contiguos de Key y Benson que usa TP3_04
SEVERIDAD = [(1, "Regeneración alta", -np.inf, -0.250), (2, "Regeneración baja", -0.250, -0.100),
             (3, "Sin cambio", -0.100, 0.100), (4, "Severidad baja", 0.100, 0.270),
             (5, "Severidad moderada-baja", 0.270, 0.440), (6, "Severidad moderada-alta", 0.440, 0.660),
             (7, "Severidad alta", 0.660, np.inf)]
HA_POR_PIXEL = 0.01            # 10 x 10 m


def coma(x, d=1):
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
    ix = {"NDVI": norm(ni, ro), "NDMI": norm(ni, s1), "NBR": norm(ni, s2),
          "EVI": np.clip(np.where(val & (den != 0), 2.5 * (ni - ro) / np.where(den == 0, 1, den),
                                  np.nan), -1, 1)}
    return ix, T


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


def ajuste_lineal(X, y):
    A = np.column_stack([X, np.ones(len(X))])
    beta, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    return beta


def aplicar(beta, X):
    return np.column_stack([X, np.ones(len(X))]) @ beta


print(__doc__)
os.makedirs(TABLAS, exist_ok=True)
filas = cargar()
por_sev, cadena = [], []

for aoi in sorted(set(r["aoi"] for r in filas)):
    sitio = "bosque" if aoi.startswith("BOSQUE") else "estepa"
    print("=" * 72)
    print("%s  (%s)" % (aoi, sitio))
    print("=" * 72)
    sub = [r for r in filas if r["aoi"] == aoi and r.get("particion")]

    # ------------------------------------------------ 1. modelo de altura
    D = []
    for r in sub:
        try:
            d = {k: float(r[k]) for k in MODELO + ["rh95"]}
        except (KeyError, ValueError):
            continue
        d["particion"] = r["particion"]
        d["este"] = float(r["este_utm19s"]); d["norte"] = float(r["norte_utm19s"])
        d["agbd"] = r.get("agbd_Mg_ha", ""); d["agbd_se"] = r.get("agbd_se_Mg_ha", "")
        D.append(d)
    ent = [d for d in D if d["particion"] == "entrenamiento"]
    val = [d for d in D if d["particion"] == "validacion"]
    if len(ent) < 30 or len(val) < 10:
        print("   muestra insuficiente, se omite"); continue
    beta_h = ajuste_lineal(np.array([[d[c] for c in MODELO] for d in ent]),
                           np.array([d["rh95"] for d in ent]))
    yv = np.array([d["rh95"] for d in val])
    pv = aplicar(beta_h, np.array([[d[c] for c in MODELO] for d in val]))
    s1 = float(np.sqrt(((yv - pv) ** 2).mean()))
    print("   s1  error del modelo de altura      %s m   (n validacion %d)" % (coma(s1, 2), len(val)))

    # -------------------------------- 2. relacion altura -> biomasa (alometrica)
    con = [d for d in D if d["agbd"] and float(d["agbd"]) > 0 and d["rh95"] > 0]
    ce = [d for d in con if d["particion"] == "entrenamiento"]
    cv = [d for d in con if d["particion"] == "validacion"]
    if len(ce) < 20 or len(cv) < 5:
        print("   pocas huellas con biomasa del L4A (%d), no se puede ajustar la conversion" % len(con))
        continue
    # agbd = a * rh95^b   ->   log(agbd) = log(a) + b*log(rh95)
    b_, la = np.polyfit(np.log([d["rh95"] for d in ce]), np.log([float(d["agbd"]) for d in ce]), 1)
    a_ = float(np.exp(la))

    def biomasa(h):
        h = np.clip(np.asarray(h, dtype="f8"), 0.1, None)
        return a_ * h ** b_

    obs = np.array([float(d["agbd"]) for d in cv])
    pre_ = biomasa([d["rh95"] for d in cv])
    s2 = float(np.sqrt(((obs - pre_) ** 2).mean()))
    r2c = 1 - ((obs - pre_) ** 2).sum() / ((obs - obs.mean()) ** 2).sum()
    print("   relacion ajustada:  biomasa = %s · altura^%s   (R² %s en validación, n %d)"
          % (coma(a_, 2), coma(b_, 3), coma(r2c, 3), len(cv)))
    print("   s2  error de la conversión          %s Mg/ha" % coma(s2))
    s3 = float(np.median([float(d["agbd_se"]) for d in con if d["agbd_se"]]))
    print("   s3  error del propio L4A            %s Mg/ha" % coma(s3))

    # ------------------------------------------- 3. dNBR y clases de severidad
    ixp, Tp = bandas(aoi, PRE); ixq, Tq = bandas(aoi, POST)
    if ixp is None or ixq is None:
        print("   faltan escenas ópticas, se omite"); continue
    dnbr = ixp["NBR"] - ixq["NBR"]
    RADq = {}
    for col, patron, banda in POST_RADAR:
        a, T = radar(patron, aoi, banda)
        if a is not None:
            RADq[col] = (a, T)

    # altura predicha PRE y POST, y biomasa de cada una, huella por huella
    reg = []
    for d in D:
        v = [ventana(ixq[c], Tq, d["este"], d["norte"], 1, False) for c in OPTICO]
        v += [ventana(RADq[c][0], RADq[c][1], d["este"], d["norte"], 7, True)
              if c in RADq else None for c in SAR_PRE]
        if any(x is None for x in v):
            continue
        cd = ventana(dnbr, Tp, d["este"], d["norte"], 1, False)
        if cd is None or not np.isfinite(cd):
            continue
        h_pre = float(aplicar(beta_h, np.array([[d[c] for c in MODELO]]))[0])
        h_post = float(aplicar(beta_h, np.array([v]))[0])
        clase = next(n for c, n, lo, hi in SEVERIDAD if lo <= cd < hi)
        reg.append({"clase": clase, "dnbr": cd,
                    "b_pre": float(biomasa([h_pre])[0]), "b_post": float(biomasa([h_post])[0]),
                    "b_obs": float(biomasa([d["rh95"]])[0])})

    # superficie de cada clase, contada sobre el raster completo
    valido = np.isfinite(dnbr)
    ha = {}
    for c, nombre, lo, hi in SEVERIDAD:
        ha[nombre] = float((valido & (dnbr >= lo) & (dnbr < hi)).sum()) * HA_POR_PIXEL

    print()
    print("   %-24s %9s %11s %11s %13s" % ("clase de severidad", "hectáreas", "huellas",
                                           "pérdida", "biomasa perdida"))
    print("   %-24s %9s %11s %11s %13s" % ("", "", "", "Mg/ha", "Mg (± incert.)"))
    tot_ha = tot_mg = tot_var = 0.0
    for c, nombre, lo, hi in SEVERIDAD:
        g = [r for r in reg if r["clase"] == nombre]
        if not g or ha[nombre] < 1:
            continue
        perd = float(np.mean([r["b_pre"] - r["b_post"] for r in g]))
        # propagacion: s1 en metros pasa a Mg/ha por la derivada de la alometria
        h_med = float(np.mean([max(0.1, (r["b_pre"] / a_) ** (1.0 / b_)) for r in g]))
        dbdh = a_ * b_ * h_med ** (b_ - 1)
        s_tot = float(np.sqrt((dbdh * s1) ** 2 + s2 ** 2 + s3 ** 2))
        mg = perd * ha[nombre]
        inc = s_tot * ha[nombre] / np.sqrt(len(g))     # el promedio por clase promedia el error
        print("   %-24s %9s %11d %11s %13s" % (nombre, coma(ha[nombre]), len(g), coma(perd),
                                               "%s ± %s" % (coma(mg, 0), coma(inc, 0))))
        por_sev.append({"aoi": aoi, "clase": nombre, "hectareas": "%.1f" % ha[nombre],
                        "huellas": len(g), "perdida_Mg_ha": "%.2f" % perd,
                        "biomasa_perdida_Mg": "%.0f" % mg, "incertidumbre_Mg": "%.0f" % inc,
                        "s_total_Mg_ha": "%.2f" % s_tot})
        if nombre.startswith("Severidad"):
            tot_ha += ha[nombre]; tot_mg += mg; tot_var += inc ** 2
    print("   %-24s %9s %11s %11s %13s" % ("TOTAL QUEMADO", coma(tot_ha), "", "",
                                           "%s ± %s" % (coma(tot_mg, 0), coma(np.sqrt(tot_var), 0))))

    # ---- ENSAYO NULO: la clase "Sin cambio" tendria que dar cero
    g0 = [r for r in reg if r["clase"] == "Sin cambio"]
    if g0 and ha["Sin cambio"] >= 1:
        p0 = float(np.mean([r["b_pre"] - r["b_post"] for r in g0]))
        print()
        print("   ENSAYO NULO. En la clase «Sin cambio» no hubo fuego, de modo que la")
        print("   pérdida tendría que dar CERO. Da %s Mg/ha sobre %s ha." % (coma(p0), coma(ha["Sin cambio"])))
        print("   Ése es el PISO DE RUIDO del método completo, y hay dos motivos claros:")
        print("   el óptico compara noviembre contra marzo, o sea dos estaciones, y el")
        print("   radar del 27/02 puede tener otra humedad de suelo que el del 10/01.")
        print("   Regla para el informe: la pérdida de una clase sólo es creíble si es")
        print("   bastante mayor que %s Mg/ha en valor absoluto." % coma(abs(p0)))
        if abs(p0) > 1e-9:
            print("   Comparación: la clase «Severidad alta» pierde %s Mg/ha, o sea %s veces el piso."
                  % (coma(float(np.mean([r["b_pre"] - r["b_post"]
                                         for r in reg if r["clase"] == "Severidad alta"] or [0]))),
                     coma(abs(float(np.mean([r["b_pre"] - r["b_post"]
                                             for r in reg if r["clase"] == "Severidad alta"] or [0])) / p0), 1)))

    # el aviso que no se puede omitir
    if reg:
        sesgo = float(np.mean([r["b_pre"] - r["b_obs"] for r in reg]))
        print()
        print("   AVISO. Biomasa desde la altura PREDICHA contra la OBSERVADA por GEDI:")
        print("   la predicha da en promedio %s Mg/ha %s. Es el sesgo del modelo de altura"
              % (coma(abs(sesgo)), "MENOS" if sesgo < 0 else "MAS"))
        print("   trasladado a biomasa: el TP5_03 midió que subestima los árboles altos, y")
        print("   la alometría lo amplifica porque la biomasa crece con la altura elevada a %s."
              % coma(b_, 2))
    cadena.append({"aoi": aoi, "s1_altura_m": "%.3f" % s1, "s2_conversion_Mg_ha": "%.3f" % s2,
                   "s3_L4A_Mg_ha": "%.3f" % s3, "alometria_a": "%.4f" % a_,
                   "alometria_b": "%.4f" % b_, "R2_conversion": "%.4f" % r2c,
                   "n_con_biomasa": len(con)})
    print()

for nombre, datos in (("TP5_biomasa_por_severidad", por_sev), ("TP5_cadena_de_error", cadena)):
    if datos:
        with open(os.path.join(TABLAS, nombre + ".csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(datos[0])); w.writeheader(); w.writerows(datos)
        print("   -> %s.csv" % nombre)

print()
print("SIGUIENTE PASO:  python TP5_05_mapas.py")
print()
print("COMO SE LEE: la cifra de biomasa perdida NO es una medición, es una estimación")
print("con tres errores encadenados. Repórtela SIEMPRE con su ± y con la advertencia")
print("del sesgo. Un número sin incertidumbre, en este trabajo, es un número falso.")
