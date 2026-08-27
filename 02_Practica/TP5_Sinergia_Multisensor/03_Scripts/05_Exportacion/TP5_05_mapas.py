# -*- coding: utf-8 -*-
"""
TP5_05_mapas.py   ---> QUINTO y ULTIMO script del TP5.

QUE HACE
--------
Lleva el modelo del practico del punto al pixel. Aplica el modelo de altura sobre
TODA la grilla -no solo donde cayeron las huellas de GEDI-, convierte a biomasa
con la alometria del TP5_04 y escribe seis capas por sitio, mas sus estilos de
QGIS:

    altura_pre, altura_post          m
    biomasa_pre, biomasa_post        Mg/ha
    biomasa_cambio                   Mg/ha  (post menos pre: negativo = perdida)
    incertidumbre                    Mg/ha  (la cadena de error del TP5_04)

ESTO ES LO QUE GEDI NO PUEDE HACER SOLO, y es el argumento del curso entero: GEDI
mide bien pero en lineas de huellas separadas por kilometros; el optico y el radar
cubren el terreno entero pero no miden estructura. El mapa existe porque se
calibro uno contra el otro.

LA MASCARA NO ES UN ADORNO
--------------------------
Se enmascara todo pixel donde el modelo NO tiene derecho a hablar:
  - nube o sombra en cualquiera de las dos fechas opticas (banda SCL)
  - sin dato de radar
  - por ENCIMA del rango de altura con el que se ajusto el modelo: extrapolar
    una alometria de exponente mayor que 2 es multiplicar el error por su
    cuadrado. Por DEBAJO no se enmascara y se recorta a cero, porque un pixel
    quemado tiene altura casi nula de manera legitima
  - GEOMETRIA DEL RADAR (agregado el 31/07/2026): sombra de radar e inversion
    por relieve. Sentinel-1 mira en pasada ASCENDENTE y SAOCOM en DESCENDENTE,
    de modo que un pixel en sombra para uno puede estar iluminado para el otro y
    comparar ambos alli carece de sentido. La mascara la produce
    TP4_05_mascara_validez.py y hasta hoy este script NO la leia, pese a estar
    declarada en el TP4: los mapas incluian pixeles sobre los que el radar no
    tenia derecho a hablar. Si la mascara no existe todavia, el script AVISA y
    sigue sin ella, para no romper la cadena
Un pixel enmascarado NO es un fracaso: es honestidad. Un mapa que cubre el 100 %
del recinto casi siempre esta inventando en alguna parte.

ADVERTENCIA QUE VIAJA CON EL MAPA
---------------------------------
El TP5_03 midio que el modelo de altura SUBESTIMA los arboles altos, y la
alometria amplifica ese sesgo. El mapa de biomasa, por lo tanto, subestima los
rodales altos. Esta escrito en el .qml y en este encabezado para que no se pierda
cuando alguien abra el raster dentro de seis meses.

ENTRADA   04_Tablas_de_trabajo/TP5_dataset_<AOI>.csv y las escenas de TP3 y TP4
SALIDA    05_Resultados/02_Rasters/TP5_<capa>_<AOI>.tif  y  .qml
USO       python TP5_05_mapas.py
"""
import csv
import glob
import os
import sys

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.warp import Resampling, reproject

AQUI = os.path.dirname(os.path.abspath(__file__))
TP5 = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROY = os.path.abspath(os.path.join(TP5, ".."))
SUBSETS = os.path.join(TP5, "04_Tablas_de_trabajo")
RASTERS = os.path.join(TP5, "05_Resultados", "02_Rasters")
S2 = os.path.join(PROY, "TP3_Datos_Opticos", "02_Subsets_SNAP_QGIS", "Sentinel_2")
I4 = os.path.join(PROY, "TP4_Radar_SAR", "02_Subsets_SNAP_QGIS")

OPTICO = ["NDVI", "EVI", "NDMI", "NBR"]
SAR = ["g0_C_VH", "g0_C_VV", "g0_L_SAOCOM_HH", "g0_L_SAOCOM_HV"]
MODELO = OPTICO + SAR
PRE, POST = "*20251125*.tif", "*20260305*.tif"
RADAR_PRE = [("g0_C_VH", "Sentinel_1/*/%s/S1_GRD/*20260110*.tif", 1),
             ("g0_C_VV", "Sentinel_1/*/%s/S1_GRD/*20260110*.tif", 2),
             ("g0_L_SAOCOM_HH", "SAOCOM/*/%s/*/*20260110*.tif", 1),
             ("g0_L_SAOCOM_HV", "SAOCOM/*/%s/*/*20260110*.tif", 2)]
RADAR_POST = [("g0_C_VH", "Sentinel_1/*/%s/S1_GRD/*20260227*.tif", 1),
              ("g0_C_VV", "Sentinel_1/*/%s/S1_GRD/*20260227*.tif", 2),
              ("g0_L_SAOCOM_HH", "SAOCOM/*/%s/*/*20260227*.tif", 1),
              ("g0_L_SAOCOM_HV", "SAOCOM/*/%s/*/*20260227*.tif", 2)]
SCL_MALAS = {0, 1, 3, 8, 9, 10, 11}
B2, B4, B8, B11, B12, SCL = 1, 3, 7, 9, 10, 11
SUAVE = 15          # lado de la ventana de radar, en pixeles (150 m), como en TP5_01


def mascara_geometrica(aoi, T, crs, forma):
    """Mascara de validez geometrica del TP4, alineada a la grilla de salida.

    Devuelve un array booleano del tamano de 'forma', o None si la mascara no
    existe todavia. La produce TP4_05_mascara_validez.py, que la escribe como
    mascaras/mascara_validez_<AOI>.tif dentro de TP4_Radar_SAR/02_Subsets_SNAP_QGIS.

    Se remuestrea por VECINO MAS PROXIMO y nunca por interpolacion: es una
    mascara de clases, y promediar un 0 con un 1 devuelve un 0,5 que no
    significa nada.
    """
    cand = [os.path.join(I4, "mascaras", "mascara_validez_%s.tif" % aoi),
            os.path.join(I4, "mascaras", "mascara_validez.tif")]
    ruta = next((c for c in cand if os.path.exists(c)), None)
    if ruta is None:
        print("   AVISO: no encuentro la mascara de validez geometrica.")
        print("          Esperaba mascaras/mascara_validez_%s.tif en" % aoi)
        print("          TP4_Radar_SAR/02_Subsets_SNAP_QGIS. Corra antes")
        print("          TP4_05_mascara_validez.py. Se sigue SIN enmascarar por")
        print("          geometria, y el mapa incluira sombra de radar e")
        print("          inversion por relieve.")
        return None
    with rasterio.open(ruta) as d:
        if d.transform == T and d.crs == crs and d.shape == forma:
            m = d.read(1)
        else:
            m = np.empty(forma, dtype=d.dtypes[0])
            reproject(source=rasterio.band(d, 1), destination=m,
                      src_transform=d.transform, src_crs=d.crs,
                      dst_transform=T, dst_crs=crs,
                      resampling=Resampling.nearest)
            print("   mascara remuestreada a la grilla de salida (vecino mas proximo)")
    b = m > 0
    print("   mascara geometrica %-14s valida en %5.1f %% del recinto  [%s]"
          % (aoi, 100.0 * b.mean(), os.path.basename(ruta)))
    return b


def coma(x, d=1):
    return ("%.*f" % (d, x)).replace(".", ",")


def escena(aoi, patron):
    h = sorted(glob.glob(os.path.join(S2, "0[23]_*", aoi, patron)))
    if not h:
        return None
    with rasterio.open(h[0]) as d:
        T, crs = d.transform, d.crs
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
    return ix, T, crs, val


def media_movil(a, lado):
    """Promedio en ventana cuadrada IGNORANDO los NaN, con imagen integral.
    Se usa para el radar: replica en el raster la misma ventana de 150 m con la
    que se extrajo el valor de cada huella en TP5_01."""
    v = np.isfinite(a)
    x = np.where(v, a, 0.0)
    r = lado // 2
    def integral(m):
        s = np.pad(np.cumsum(np.cumsum(m, 0), 1), ((1, 0), (1, 0)))
        f0 = np.clip(np.arange(m.shape[0]) - r, 0, m.shape[0])
        f1 = np.clip(np.arange(m.shape[0]) + r + 1, 0, m.shape[0])
        c0 = np.clip(np.arange(m.shape[1]) - r, 0, m.shape[1])
        c1 = np.clip(np.arange(m.shape[1]) + r + 1, 0, m.shape[1])
        return (s[np.ix_(f1, c1)] - s[np.ix_(f0, c1)]
                - s[np.ix_(f1, c0)] + s[np.ix_(f0, c0)])
    n = integral(v.astype("f8"))
    return np.where(n > 0, integral(x) / np.where(n == 0, 1, n), np.nan)


def radar_db(fuentes, aoi):
    """gamma0 en dB, promediado EN POTENCIA en ventana de 150 m."""
    out = {}
    for col, patron, banda in fuentes:
        h = [x for x in sorted(glob.glob(os.path.join(I4, patron % aoi))) if "_mask" not in x]
        if not h:
            continue
        with rasterio.open(h[0]) as d:
            a = d.read(banda).astype("f8")
        pot = np.where(a > 0, a, np.nan)          # el dato ya es potencia lineal
        out[col] = 10 * np.log10(media_movil(pot, SUAVE))
    return out


def cargar_puntos(aoi):
    p = os.path.join(SUBSETS, "TP5_dataset_%s.csv" % aoi)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def escribir(ruta, arr, T, crs, nodata=-9999.0):
    a = np.where(np.isfinite(arr), arr, nodata).astype("float32")
    with rasterio.open(ruta, "w", driver="GTiff", height=a.shape[0], width=a.shape[1],
                       count=1, dtype="float32", crs=crs, transform=T, nodata=nodata,
                       compress="DEFLATE", tiled=True) as d:
        d.write(a, 1)


QML = """<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">
  <!-- %s
       ADVERTENCIA: el modelo de altura subestima los arboles altos (sesgo medido
       de casi 10 m por encima de 15 m) y la alometria lo amplifica. Este mapa
       SUBESTIMA los rodales altos. Ver TP5_03 y TP5_04. -->
  <pipe><rasterrenderer type="singlebandpseudocolor" band="1" opacity="1">
    <rastershader><colorrampshader classificationMode="1" colorRampType="INTERPOLATED">
      %s
    </colorrampshader></rastershader>
  </rasterrenderer></pipe>
</qgis>
"""


def rampa(paradas):
    return "\n      ".join('<item value="%s" color="%s" label="%s"/>' % (v, c, l)
                           for v, c, l in paradas)


print(__doc__)
os.makedirs(RASTERS, exist_ok=True)
for aoi in ("BOSQUE_NW_02", "ESTEPA_NW_02"):
    print("=" * 72)
    print(aoi)
    print("=" * 72)
    pts = cargar_puntos(aoi)
    if not pts:
        print("   falta el dataset del TP5_01, se omite"); continue
    D = []
    for r in pts:
        if not r.get("particion"):
            continue
        try:
            d = {k: float(r[k]) for k in MODELO + ["rh95"]}
        except (KeyError, ValueError):
            continue
        d["particion"] = r["particion"]
        d["agbd"] = r.get("agbd_Mg_ha", "")
        D.append(d)
    ent = [d for d in D if d["particion"] == "entrenamiento"]
    if len(ent) < 30:
        print("   muestra insuficiente, se omite"); continue
    A = np.column_stack([np.array([[d[c] for c in MODELO] for d in ent]), np.ones(len(ent))])
    beta, _, _, _ = np.linalg.lstsq(A, np.array([d["rh95"] for d in ent]), rcond=None)
    con = [d for d in D if d["agbd"] and float(d["agbd"]) > 0 and d["rh95"] > 0
           and d["particion"] == "entrenamiento"]
    b_, la = np.polyfit(np.log([d["rh95"] for d in con]),
                        np.log([float(d["agbd"]) for d in con]), 1)
    a_ = float(np.exp(la))
    h_min = float(np.percentile([d["rh95"] for d in ent], 1))
    h_max = float(np.percentile([d["rh95"] for d in ent], 99))
    print("   modelo de altura: %d variables, %d huellas de entrenamiento" % (len(MODELO), len(ent)))
    print("   alometría: biomasa = %s · altura^%s" % (coma(a_, 2), coma(b_, 3)))
    print("   rango con el que se ajustó: %s a %s m. Por encima se enmascara; por debajo se recorta a 0."
          % (coma(h_min), coma(h_max)))

    capas = {}
    for etiqueta, pat_opt, fuentes in (("pre", PRE, RADAR_PRE), ("post", POST, RADAR_POST)):
        e = escena(aoi, pat_opt)
        if e is None:
            print("   falta la escena óptica %s, se omite el sitio" % etiqueta); capas = {}; break
        ix, T, crs, val = e
        rad = radar_db(fuentes, aoi)
        if len(rad) < len(SAR):
            print("   falta radar %s (%d de %d bandas), se omite el sitio"
                  % (etiqueta, len(rad), len(SAR))); capas = {}; break
        pila = [ix[c] for c in OPTICO] + [rad[c] for c in SAR]
        h = np.full(ix["NDVI"].shape, np.nan)
        bueno = val.copy()
        for a in pila:
            bueno &= np.isfinite(a)
        # geometria del radar: sombra e inversion por relieve (ver encabezado)
        geo = mascara_geometrica(aoi, T, crs, bueno.shape)
        if geo is not None:
            antes = bueno.mean()
            bueno &= geo
            print("   %-5s  la mascara geometrica descarta %.1f %% mas del recinto"
                  % (etiqueta, 100.0 * (antes - bueno.mean())))
        acum = np.full(ix["NDVI"].shape, beta[-1])
        for k, a in enumerate(pila):
            acum = acum + beta[k] * np.where(np.isfinite(a), a, 0.0)
        h = np.where(bueno, acum, np.nan)
        # SOLO se enmascara la extrapolacion HACIA ARRIBA. Hacia abajo NO: un
        # pixel quemado tiene altura casi nula de manera legitima, y enmascararlo
        # borraria justamente lo que se quiere medir. La primera version de este
        # script enmascaraba los dos extremos y dejaba el bosque post-incendio con
        # 43,6 % de pixeles: se estaba tapando el incendio con la mascara.
        h = np.where(bueno & (h <= h_max), np.clip(h, 0.0, None), np.nan)
        capas["altura_" + etiqueta] = (h, T, crs)
        capas["biomasa_" + etiqueta] = (a_ * np.clip(h, 0.1, None) ** b_, T, crs)
        print("   %-5s  píxeles con dato: %5.1f %%" % (etiqueta, 100.0 * np.isfinite(h).mean()))
    if not capas:
        continue
    T, crs = capas["altura_pre"][1], capas["altura_pre"][2]
    cambio = capas["biomasa_post"][0] - capas["biomasa_pre"][0]
    capas["biomasa_cambio"] = (cambio, T, crs)
    # incertidumbre, con la misma cadena del TP5_04
    val_ = [d for d in D if d["particion"] == "validacion"]
    pv = (np.column_stack([np.array([[d[c] for c in MODELO] for d in val_]),
                           np.ones(len(val_))]) @ beta)
    s1 = float(np.sqrt(((np.array([d["rh95"] for d in val_]) - pv) ** 2).mean()))
    cv = [d for d in D if d["agbd"] and float(d["agbd"]) > 0 and d["rh95"] > 0
          and d["particion"] == "validacion"]
    s2 = float(np.sqrt(((np.array([float(d["agbd"]) for d in cv])
                         - a_ * np.array([d["rh95"] for d in cv]) ** b_) ** 2).mean())) if cv else 0.0
    s3 = float(np.median([float(d["agbd_se_Mg_ha"]) for d in pts
                          if d.get("agbd_se_Mg_ha")] or [0.0]))
    hh = np.clip(capas["altura_pre"][0], 0.1, None)
    inc = np.sqrt((a_ * b_ * hh ** (b_ - 1) * s1) ** 2 + s2 ** 2 + s3 ** 2)
    capas["incertidumbre"] = (inc, T, crs)
    print("   cadena de error: s1 %s m | s2 %s Mg/ha | s3 %s Mg/ha"
          % (coma(s1, 2), coma(s2), coma(s3)))

    ESTILOS = {
        "altura": ("Altura del dosel predicha (m)",
                   [("0", "#f7fcf5", "0 m"), ("5", "#a1d99b", "5 m"),
                    ("15", "#41ab5d", "15 m"), ("30", "#00441b", "30 m")]),
        "biomasa": ("Biomasa aérea estimada (Mg/ha)",
                    [("0", "#ffffe5", "0"), ("25", "#fee391", "25"),
                     ("75", "#fe9929", "75"), ("150", "#993404", "150")]),
        "biomasa_cambio": ("Cambio de biomasa, post menos pre (Mg/ha). Negativo = pérdida",
                           [("-100", "#67001f", "-100"), ("-25", "#f4a582", "-25"),
                            ("0", "#f7f7f7", "0"), ("25", "#92c5de", "+25")]),
        "incertidumbre": ("Incertidumbre de la biomasa (Mg/ha), cadena completa",
                          [("0", "#ffffff", "0"), ("15", "#cccccc", "15"),
                           ("40", "#525252", "40")]),
    }
    for nombre, (arr, T_, crs_) in capas.items():
        ruta = os.path.join(RASTERS, "TP5_%s_%s.tif" % (nombre, aoi))
        escribir(ruta, arr, T_, crs_)
        clave = ("biomasa_cambio" if nombre == "biomasa_cambio"
                 else "incertidumbre" if nombre == "incertidumbre"
                 else nombre.split("_")[0])
        tit, par = ESTILOS[clave]
        with open(ruta[:-4] + ".qml", "w", encoding="utf-8") as f:
            f.write(QML % (tit, rampa(par)))
    print("   -> %d capas .tif con su .qml en 05_Resultados/02_Rasters/" % len(capas))
    perd = cambio[np.isfinite(cambio) & (cambio < 0)]
    if perd.size:
        print("   biomasa perdida sobre los píxeles con dato: %s Mg en %s ha"
              % (coma(float(-perd.sum() * 0.01), 0), coma(float(perd.size * 0.01))))
    print()

print("EL TP5 TERMINA ACA. Antes de usar estos mapas, tres cosas que hay que decir")
print("en el informe y que el .qml lleva escritas adentro:")
print("  1. El mapa SUBESTIMA los rodales altos: el modelo de altura tiene un sesgo")
print("     de casi 10 m por encima de 15 m y la alometría lo amplifica.")
print("  2. Los píxeles enmascarados no son un error: son donde el modelo no tiene")
print("     derecho a hablar. Informe qué porcentaje del recinto quedó sin dato.")
print("  3. La pérdida sólo es creíble por encima del piso de ruido que midió el")
print("     TP5_04 con la clase «Sin cambio». Compárela contra ese piso, no contra cero.")
