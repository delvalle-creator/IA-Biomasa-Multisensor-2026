# -*- coding: utf-8 -*-
"""
TP5_01_dataset.py   ---> PRIMER script del TP5.

QUE HACE
--------
Apila, para cada huella GEDI valida del TP2, todo lo que los practicos anteriores
midieron sobre ese mismo punto del terreno:

    del TP2   rh95, pai, cover, fhd, pendiente, biomasa del L4A y su error
    del TP3   NDVI, EVI, NDMI y NBR de la escena optica pre-incendio limpia
    del TP4   gamma0 de banda C (Sentinel-1) y de banda L (SAOCOM, NISAR, PALSAR-2)

y le pega la etiqueta de particion -entrenamiento o validacion- QUE YA DECIDIO EL
TP2. No la rehace. Si cada modelo del TP5 usara muestras distintas, compararlos
no significaria nada.

TRES DECISIONES QUE HAY QUE CONOCER ANTES DE LEER UN RESULTADO
--------------------------------------------------------------
1. VENTANAS DISTINTAS PARA OPTICO Y PARA RADAR, y a proposito. El optico se
   promedia en 3x3 pixeles (30 m, del orden de la huella de GEDI). El radar se
   promedia en 15x15 (150 m), porque el moteado obliga: el TP4 midio que el R2 de
   banda L sube de 0,178 a 0,275 al promediar hasta esa ventana. No es hacer
   trampa; lo que no se puede es corregirlo sin declararlo.

2. EL PROMEDIO DEL RADAR SE HACE EN POTENCIA, NUNCA EN DECIBELES. El dB es
   logaritmico: promediar dB da la media geometrica, que subestima, y el sesgo
   crece con la dispersion, o sea con el propio moteado. Medido sobre estos
   datos: entre 0,54 y 0,85 dB de sesgo, y creciendo con el tamano de ventana,
   que es justo la variable que se quiere estudiar.

3. TODO ES PRE-INCENDIO. Las fechas son casi simultaneas -S2 del 25/11/2025,
   Sentinel-1 y SAOCOM del 10/01/2026, NISAR del 08/01/2026, PALSAR-2 mosaico
   2025- para que la humedad del suelo y la fenologia sean parecidas. El post
   incendio entra recien en TP5_04, que es otra pregunta.

ENTRADA   TP2_LiDAR_GEDI_ICESat2/04_Tablas_de_trabajo/  (validas, entrenamiento y validacion)
          TP2_LiDAR_GEDI_ICESat2/05_Resultados/04_Tablas/biomasa_<AOI>.csv
          TP3_Datos_Opticos/02_Subsets_SNAP_QGIS/Sentinel_2/02_pre*/<AOI>/*20251125*.tif
          TP4_Radar_SAR/02_Subsets_SNAP_QGIS/...  (ver FUENTES_RADAR, mas abajo)
SALIDA    TP5_Sinergia_Multisensor/04_Tablas_de_trabajo/TP5_dataset_<AOI>.csv
          y un resumen de cobertura por columna, que hay que mirar

USO (entorno conda 'aoi'):   python TP5_01_dataset.py
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
TP2 = os.path.join(PROY, "TP2_LiDAR_GEDI_ICESat2")
S2 = os.path.join(PROY, "TP3_Datos_Opticos", "02_Subsets_SNAP_QGIS", "Sentinel_2")
I4 = os.path.join(PROY, "TP4_Radar_SAR", "02_Subsets_SNAP_QGIS")
SALIDA = os.path.join(TP5, "04_Tablas_de_trabajo")

AOIS = [("BOSQUE_NW_02", "01_Bosque"), ("ESTEPA_NW_02", "02_Estepa")]
ESCENA_OPTICA = "*20251125*.tif"          # la ultima limpia antes del fuego
SCL_MALAS = {0, 1, 3, 8, 9, 10, 11}
B2, B4, B8, B11, B12, SCL = 1, 3, 7, 9, 10, 11
RADIO_OPTICO = 1                          # 3x3 = 30 m, del orden de la huella
RADIO_RADAR = 7                           # 15x15 = 150 m, el optimo medido en TP4

# (columna, patron, numero de banda)
FUENTES_RADAR = [
    ("g0_C_VH",  "Sentinel_1/*/%s/S1_GRD/*20260110*.tif", 1),
    ("g0_C_VV",  "Sentinel_1/*/%s/S1_GRD/*20260110*.tif", 2),
    ("g0_L_SAOCOM_HH", "SAOCOM/*/%s/*/*20260110*.tif", 1),
    ("g0_L_SAOCOM_HV", "SAOCOM/*/%s/*/*20260110*.tif", 2),
    ("g0_L_NISAR_HH",  "NISAR/*/%s/*/NISAR_GCOV_20260108.tif", 1),
    ("g0_L_NISAR_HV",  "NISAR/*/%s/*/NISAR_GCOV_20260108.tif", 2),
    ("g0_L_PALSAR2_HH", "ALOS_PALSAR_2/*/%s/*/PALSAR2_2025.tif", 1),
    ("g0_L_PALSAR2_HV", "ALOS_PALSAR_2/*/%s/*/PALSAR2_2025.tif", 2),
]
INDICES = ["NDVI", "EVI", "NDMI", "NBR"]


def unico(patron):
    h = [x for x in sorted(glob.glob(patron)) if "_mask" not in x]
    return h[0] if h else None


def leer_csv(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def particion(aoi):
    """{shot_number: 'entrenamiento' | 'validacion'}, tal como la dejo el TP2."""
    et = {}
    for grupo, nombre in (("04_Entrenamiento", "entrenamiento"),
                          ("05_Validacion", "validacion")):
        p = os.path.join(TP2, "04_Tablas_de_trabajo", grupo,
                         "GEDI_%s_%s.csv" % (aoi, grupo.lower()))
        if not os.path.exists(p):
            continue
        for r in leer_csv(p):
            et[r["shot_number"]] = nombre
    return et


def biomasa(aoi):
    p = os.path.join(TP2, "05_Resultados", "04_Tablas", "biomasa_%s.csv" % aoi)
    if not os.path.exists(p):
        return {}
    return {r["shot_number"]: r for r in leer_csv(p)}


def indices_opticos(aoi):
    """Devuelve (dict de arrays, transform). Los calcula de la escena, que es la
    fuente; si el TP3 dejo los rasters de indices, dan lo mismo."""
    f = unico(os.path.join(S2, "02_pre*", aoi, ESCENA_OPTICA))
    if f is None:
        sys.exit("Falta la escena optica pre-incendio de %s en %s" % (aoi, S2))
    with rasterio.open(f) as d:
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
                                    2.5 * (ni - ro) / np.where(den == 0, 1, den),
                                    np.nan), -1, 1)}, T, os.path.basename(f)


def gamma0_db(patron, aoi, banda):
    """Lee una banda y la deja en dB, con nodata donde no hay senal."""
    f = unico(os.path.join(I4, patron % aoi))
    if f is None:
        return None, None, None
    with rasterio.open(f) as d:
        a = d.read(banda).astype("f8")
        T = d.transform
    sal = np.full(a.shape, np.nan)
    np.log10(a, where=a > 0, out=sal)          # out= explicito: si no, basura sin inicializar
    return np.where(a > 0, 10 * sal, np.nan), T, os.path.basename(f)


def ventana(arr, T, este, norte, radio, en_potencia):
    """Promedia una ventana centrada en la huella. EN POTENCIA si es radar."""
    ny, nx = arr.shape
    c = int((este - T.c) / T.a); f = int((norte - T.f) / T.e)
    if not (radio <= c < nx - radio and radio <= f < ny - radio):
        return None
    w = arr[f - radio:f + radio + 1, c - radio:c + radio + 1]
    w = w[np.isfinite(w)]
    if w.size == 0:
        return None
    if en_potencia:
        return float(10 * np.log10(np.mean(10 ** (w / 10.0))))
    return float(w.mean())


print(__doc__)
os.makedirs(SALIDA, exist_ok=True)
for aoi, sub in AOIS:
    print("=" * 72)
    print(aoi)
    print("=" * 72)
    origen = os.path.join(TP2, "04_Tablas_de_trabajo", sub,
                          "GEDI_%s_validos_con_estructura.csv" % aoi)
    if not os.path.exists(origen):
        print("   faltan las huellas validas del TP2, se omite")
        continue
    huellas = leer_csv(origen)
    parts, bio = particion(aoi), biomasa(aoi)
    IX, T_opt, nom_opt = indices_opticos(aoi)
    print("   optico : %s" % nom_opt)

    RAD = {}
    for col, patron, banda in FUENTES_RADAR:
        a, T, nom = gamma0_db(patron, aoi, banda)
        if a is None:
            print("   FALTA  : %s (no se encontro %s)" % (col, patron % aoi))
            continue
        RAD[col] = (a, T)
        if banda == 1:
            print("   radar  : %-16s %s" % (col.split("_")[2] if col.count("_") > 2
                                            else col, nom))

    filas, faltan = [], {}
    for r in huellas:
        try:
            e, n = float(r["este_utm19s"]), float(r["norte_utm19s"])
        except (KeyError, ValueError):
            continue
        d = {"shot_number": r["shot_number"], "aoi": aoi,
             "sitio": "bosque" if aoi.startswith("BOSQUE") else "estepa",
             "lat": r.get("lat", ""), "lon": r.get("lon", ""),
             "este_utm19s": r["este_utm19s"], "norte_utm19s": r["norte_utm19s"],
             "particion": parts.get(r["shot_number"], "")}
        for k in ("rh95", "rh50", "pai", "cover", "fhd_normal", "pendiente_grados"):
            d[k] = r.get(k, "")
        b = bio.get(r["shot_number"], {})
        d["agbd_Mg_ha"] = b.get("agbd_Mg_ha", "")
        d["agbd_se_Mg_ha"] = b.get("agbd_se_Mg_ha", "")
        d["predict_stratum"] = b.get("predict_stratum", "")
        # agbd_origen viaja hasta el final: 'certificada' si la NASA la avalo,
        # 'hoja_caida' si se recupero por el criterio del TP2_07. Sin esta
        # columna no se puede rehacer ningun resultado sin las recuperadas.
        d["agbd_origen"] = b.get("agbd_origen", "")
        d["leaf_off_flag"] = b.get("leaf_off_flag", "")
        for k in INDICES:
            v = ventana(IX[k], T_opt, e, n, RADIO_OPTICO, False)
            d[k] = "" if v is None else "%.5f" % v
            if v is None:
                faltan[k] = faltan.get(k, 0) + 1
        for col, (a, T) in RAD.items():
            v = ventana(a, T, e, n, RADIO_RADAR, True)
            d[col] = "" if v is None else "%.3f" % v
            if v is None:
                faltan[col] = faltan.get(col, 0) + 1
        filas.append(d)

    sal = os.path.join(SALIDA, "TP5_dataset_%s.csv" % aoi)
    with open(sal, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader(); w.writerows(filas)

    ne = sum(1 for x in filas if x["particion"] == "entrenamiento")
    nv = sum(1 for x in filas if x["particion"] == "validacion")
    nb = sum(1 for x in filas if x["agbd_Mg_ha"])
    print()
    print("   huellas apiladas : %d   (entrenamiento %d / validacion %d)" % (len(filas), ne, nv))
    print("   con biomasa L4A  : %d  (%.1f %%)" % (nb, 100.0 * nb / len(filas)))
    if faltan:
        print("   sin dato en alguna columna:")
        for k in sorted(faltan):
            print("      %-18s %4d huellas (%.1f %%)" % (k, faltan[k], 100.0 * faltan[k] / len(filas)))
    else:
        print("   todas las columnas completas en todas las huellas")
    print("   -> %s" % sal)

print()
print("SIGUIENTE PASO:  python TP5_02_modelos.py")
print("Antes de seguir, MIRE el resumen de arriba: si una columna de radar falta")
print("en muchas huellas, el modelo que la use no es comparable con los demas,")
print("porque no estara ajustado sobre las mismas muestras.")
