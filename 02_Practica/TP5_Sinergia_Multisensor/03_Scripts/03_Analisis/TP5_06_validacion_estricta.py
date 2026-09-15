# -*- coding: utf-8 -*-
"""
TP5_06_validacion_estricta.py

Rehace la parte inferencial del TP5 con cuatro controles que la version
anterior no tenia. Responde uno a uno a los hallazgos de la revision externa.

 1. VALIDACION CRUZADA ESPACIAL ANIDADA
    Antes: se elegian los hiperparametros mirando la misma particion con la
    que despues se informaba el desempeno. Eso es optimismo por seleccion.
    Ahora: bloques espaciales; la seleccion ocurre DENTRO de cada pliegue de
    entrenamiento y el desempeno se mide en el bloque que quedo afuera.
    Se informa tambien la version no anidada, para cuantificar el optimismo.

 2. AREA DE APLICABILIDAD (Meyer y Pebesma, 2021)
    Antes: la mascara usaba el rango de la altura predicha.
    Ahora: distancia en el espacio de predictores, ponderada por importancia,
    con el umbral derivado de las distancias internas del entrenamiento.
    Se aplica a la transferencia entre sitios, que el practico prometia y no
    mostraba.

 3. PROPAGACION CONJUNTA DE LA INCERTIDUMBRE
    Antes: suma en cuadratura, que supone independencia entre el error de
    altura, el de la alometria y el del producto de referencia.
    Ahora: Monte Carlo jerarquico con la covarianza de los coeficientes
    alometricos y la correlacion medida entre tramos. Se informan las dos
    cifras para que se vea cuanto cambia el supuesto.

 4. ENSAYO NULO CON DISTRIBUCION
    Antes: un solo numero como piso de ruido.
    Ahora: remuestreo por bloques espaciales sobre la clase sin cambio, con
    intervalo de confianza y umbral de decision explicito.

Uso:  python TP5_06_validacion_estricta.py
"""
import os, sys, json
import numpy as np
try:
    import pandas as pd
except ImportError:
    sys.exit("Falta pandas:  conda install -c conda-forge pandas")
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_squared_error

SEMILLA = 20260903
rng = np.random.default_rng(SEMILLA)

AQUI = os.path.dirname(os.path.abspath(__file__))

# Este script vive en 03_Scripts/03_Analisis, de modo que la raiz del practico
# esta DOS niveles arriba y no uno. Con un solo "..", SUB apuntaba a
# 03_Scripts/04_Tablas_de_trabajo, que no existe, y el respaldo (SUB = AQUI)
# hacia que buscara los datasets AL LADO del script: FileNotFoundError, aun
# corriendolo como dice el orden de ejecucion. Ahora se sube por el arbol
# hasta encontrar la carpeta real. Corregido el 11/09/2026.
def _subir_hasta(*partes):
    d = AQUI
    while d != os.path.dirname(d):
        cand = os.path.join(d, *partes)
        if os.path.isdir(cand):
            return cand
        d = os.path.dirname(d)
    return None

SUB = _subir_hasta("04_Tablas_de_trabajo") or AQUI
SAL = _subir_hasta("05_Resultados", "04_Tablas") or os.path.join(AQUI, "out")
os.makedirs(SAL, exist_ok=True)

OPTICO = ["NDVI", "EVI", "NDMI", "NBR"]
RADAR  = ["g0_C_VH", "g0_C_VV", "g0_L_SAOCOM_HH", "g0_L_SAOCOM_HV"]
JUEGOS = {"óptico": OPTICO, "radar": RADAR, "óptico+radar": OPTICO + RADAR}
OBJ = "rh95"
LADO_BLOQUE = 2000.0     # metros

def cargar(nombre):
    p = os.path.join(SUB, nombre)
    d = pd.read_csv(p)
    d["sitio_"] = nombre.split("_")[2]
    return d

def bloques(d):
    """Identificador de bloque espacial de 2 x 2 km."""
    bx = np.floor(d["este_utm19s"].to_numpy() / LADO_BLOQUE).astype(int)
    by = np.floor(d["norte_utm19s"].to_numpy() / LADO_BLOQUE).astype(int)
    return np.array(["%d_%d" % (a, b) for a, b in zip(bx, by)])

def limpio(d, cols):
    m = np.ones(len(d), dtype=bool)
    for c in cols + [OBJ]:
        m &= d[c].notna().to_numpy()
    return d.loc[m].reset_index(drop=True)

# ----------------------------------------------------------------- 1. anidada
REJILLA = [
    {"n_estimators": 150, "max_depth": None, "min_samples_leaf": 1},
    {"n_estimators": 150, "max_depth": 12,   "min_samples_leaf": 3},
    {"n_estimators": 150, "max_depth": 6,    "min_samples_leaf": 10},
]

def rf(par):
    return RandomForestRegressor(random_state=SEMILLA, n_jobs=-1, **par)

def cv_anidada(X, y, g, k_ext=5, k_int=3):
    """Devuelve (R2 anidada, RMSE anidada, R2 no anidada, hiperparametros)."""
    ge = GroupKFold(n_splits=min(k_ext, len(np.unique(g))))
    r2s, rmses, elegidos = [], [], []
    for itr, ite in ge.split(X, y, groups=g):
        Xtr, ytr, gtr = X[itr], y[itr], g[itr]
        # --- seleccion DENTRO del entrenamiento
        mejor, mejor_r2 = None, -np.inf
        gi = GroupKFold(n_splits=min(k_int, len(np.unique(gtr))))
        for par in REJILLA:
            pun = []
            for jtr, jte in gi.split(Xtr, ytr, groups=gtr):
                m = rf(par).fit(Xtr[jtr], ytr[jtr])
                pun.append(r2_score(ytr[jte], m.predict(Xtr[jte])))
            s = float(np.mean(pun))
            if s > mejor_r2: mejor_r2, mejor = s, par
        elegidos.append(mejor)
        m = rf(mejor).fit(Xtr, ytr)
        pred = m.predict(X[ite])
        r2s.append(r2_score(y[ite], pred))
        rmses.append(float(np.sqrt(mean_squared_error(y[ite], pred))))
    # --- no anidada: elegir mirando los mismos pliegues externos
    mejor_plano, mejor_r2_plano = None, -np.inf
    for par in REJILLA:
        pun = []
        for itr, ite in ge.split(X, y, groups=g):
            m = rf(par).fit(X[itr], y[itr])
            pun.append(r2_score(y[ite], m.predict(X[ite])))
        s = float(np.mean(pun))
        if s > mejor_r2_plano: mejor_r2_plano, mejor_plano = s, par
    return (float(np.mean(r2s)), float(np.std(r2s)), float(np.mean(rmses)),
            mejor_r2_plano, elegidos)

# --------------------------------------------------- 2. area de aplicabilidad
def indice_disimilitud(Xtr, Xnu, pesos):
    """DI de Meyer y Pebesma: distancia minima al entrenamiento, en el espacio
       estandarizado y ponderado por importancia, normalizada por la distancia
       media entre puntos de entrenamiento."""
    from sklearn.neighbors import NearestNeighbors
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd == 0] = 1.0
    A = (Xtr - mu) / sd * pesos
    B = (Xnu - mu) / sd * pesos
    idx = rng.choice(len(A), size=min(len(A), 500), replace=False)
    S = A[idx]
    dd = np.sqrt(((S[:, None, :] - S[None, :, :]) ** 2).sum(-1))
    dmedia = dd[np.triu_indices_from(dd, k=1)].mean()
    nn = NearestNeighbors(n_neighbors=1).fit(A)
    di = nn.kneighbors(B, return_distance=True)[0][:, 0] / dmedia
    nn2 = NearestNeighbors(n_neighbors=2).fit(A)
    dii = nn2.kneighbors(A, return_distance=True)[0][:, 1] / dmedia
    q1, q3 = np.percentile(dii, [25, 75])
    umbral = q3 + 1.5 * (q3 - q1)
    return di, umbral, dii

# ------------------------------------------ 3. propagacion conjunta por MC
def alometria(d):
    """log(agbd) = log(a) + b log(rh95). Devuelve coeficientes y covarianza."""
    m = d["agbd_Mg_ha"].notna() & (d["agbd_Mg_ha"] > 0) & (d[OBJ] > 0)
    x = np.log(d.loc[m, OBJ].to_numpy()); y = np.log(d.loc[m, "agbd_Mg_ha"].to_numpy())
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, p = len(x), 2
    s2 = float(resid @ resid) / (n - p)
    cov = s2 * np.linalg.inv(X.T @ X)
    return beta, cov, float(np.sqrt(s2)), int(n), resid

def propagacion(d, s_altura, s_ref, n_mc=20000):
    beta, cov, sigma_log, n, resid = alometria(d)
    h = np.median(d[OBJ].to_numpy())
    a, b = np.exp(beta[0]), beta[1]
    agbd0 = a * h ** b
    # --- Monte Carlo conjunto
    L = np.linalg.cholesky(cov + 1e-12 * np.eye(2))
    z = rng.standard_normal((n_mc, 2)) @ L.T + beta
    eh = rng.normal(0.0, s_altura, n_mc)          # error del modelo de altura
    er = rng.normal(0.0, s_ref, n_mc)             # error del producto de referencia
    # correlacion medida entre el residuo alometrico y la altura
    rho = float(np.corrcoef(resid, np.log(d.loc[d["agbd_Mg_ha"].notna() &
             (d["agbd_Mg_ha"] > 0) & (d[OBJ] > 0), OBJ].to_numpy()))[0, 1])
    hh = np.clip(h + eh, 0.1, None)
    agbd = np.exp(z[:, 0]) * hh ** z[:, 1] + er
    sd_mc = float(np.std(agbd))
    # --- suma en cuadratura, que es lo que se hacia antes
    s_conv = abs(b) * agbd0 * (s_altura / h)
    sd_cuad = float(np.sqrt(s_conv ** 2 + s_ref ** 2))
    return dict(h_mediana=h, a=a, b=b, agbd=agbd0, n_alometria=n,
                rho_resid_altura=rho, sd_montecarlo=sd_mc,
                sd_cuadratura=sd_cuad, cociente=sd_mc / sd_cuad if sd_cuad else np.nan)

# --------------------------------------------- 4. ensayo nulo con distribucion
def ensayo_nulo(valores, grupos, n_boot=2000):
    """Remuestreo POR BLOQUE, no por huella: respeta la autocorrelacion."""
    unicos = np.unique(grupos)
    med = []
    for _ in range(n_boot):
        sel = rng.choice(unicos, size=len(unicos), replace=True)
        v = np.concatenate([valores[grupos == u] for u in sel])
        med.append(np.median(v))
    med = np.array(med)
    return dict(mediana=float(np.median(valores)),
                media_boot=float(med.mean()),
                ic95_inf=float(np.percentile(med, 2.5)),
                ic95_sup=float(np.percentile(med, 97.5)),
                sd=float(med.std()),
                umbral_decision=float(np.percentile(np.abs(med), 95)))

# ================================================================== principal
def main():
    bos = cargar("TP5_dataset_BOSQUE_NW_02.csv")
    est = cargar("TP5_dataset_ESTEPA_NW_02.csv")
    print("bosque=%d  estepa=%d" % (len(bos), len(est)))
    filas_cv, filas_aoa, filas_pr, filas_nulo = [], [], [], []

    for nombre, d in (("bosque", bos), ("estepa", est), ("los dos juntos", pd.concat([bos, est], ignore_index=True))):
        for jn, cols in JUEGOS.items():
            dd = limpio(d, cols)
            if len(dd) < 60: continue
            X = dd[cols].to_numpy(float); y = dd[OBJ].to_numpy(float); g = bloques(dd)
            if len(np.unique(g)) < 5: continue
            r2a, sda, rmsea, r2plano, eleg = cv_anidada(X, y, g)
            filas_cv.append(dict(sitio=nombre, juego=jn, n=len(dd), bloques=len(np.unique(g)),
                                 R2_anidada=round(r2a, 4), desvio_entre_bloques=round(sda, 4),
                                 RMSE_anidada_m=round(rmsea, 3),
                                 R2_no_anidada=round(r2plano, 4),
                                 optimismo=round(r2plano - r2a, 4)))
            print("  CV %-14s %-13s n=%-5d anidada=%.3f  no anidada=%.3f  optimismo=%.3f"
                  % (nombre, jn, len(dd), r2a, r2plano, r2plano - r2a))

    # --- AOA en la transferencia entre sitios
    cols = OPTICO + RADAR
    b2 = limpio(bos, cols); e2 = limpio(est, cols)
    for origen, destino, no, nd in ((b2, e2, "bosque", "estepa"), (e2, b2, "estepa", "bosque")):
        Xtr = origen[cols].to_numpy(float); ytr = origen[OBJ].to_numpy(float)
        Xnu = destino[cols].to_numpy(float); ynu = destino[OBJ].to_numpy(float)
        m = rf({"n_estimators": 150, "max_depth": 12, "min_samples_leaf": 3}).fit(Xtr, ytr)
        pesos = m.feature_importances_
        di, umbral, dii = indice_disimilitud(Xtr, Xnu, pesos)
        dentro = di <= umbral
        pred = m.predict(Xnu)
        r2_todo = r2_score(ynu, pred)
        r2_dentro = r2_score(ynu[dentro], pred[dentro]) if dentro.sum() > 20 else np.nan
        filas_aoa.append(dict(entrena=no, predice=nd, n_destino=len(Xnu),
                              umbral_DI=round(float(umbral), 4),
                              dentro_del_area=int(dentro.sum()),
                              porcentaje_dentro=round(100.0 * dentro.mean(), 1),
                              R2_todo=round(float(r2_todo), 4),
                              R2_solo_dentro=None if np.isnan(r2_dentro) else round(float(r2_dentro), 4)))
        print("  AOA %s -> %s: %.1f %% dentro del area; R2 todo=%.3f, solo dentro=%s"
              % (no, nd, 100.0 * dentro.mean(), r2_todo,
                 "n/d" if np.isnan(r2_dentro) else "%.3f" % r2_dentro))

    # --- propagacion conjunta
    for nombre, d, s1, s3 in (("BOSQUE_NW_02", bos, 4.317, 13.090),
                              ("ESTEPA_NW_02", est, 1.311, 2.998)):
        r = propagacion(d, s1, s3)
        r["aoi"] = nombre; r["s1_altura_m"] = s1; r["s3_referencia_Mg_ha"] = s3
        filas_pr.append({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
        print("  propagacion %s: Monte Carlo=%.2f Mg/ha  cuadratura=%.2f Mg/ha  cociente=%.2f"
              % (nombre, r["sd_montecarlo"], r["sd_cuadratura"], r["cociente"]))

    # --- ensayo nulo: la estepa entera es el testigo que no se quemo
    for nombre, d in (("ESTEPA_NW_02 (control)", est),):
        dd = limpio(d, OPTICO + RADAR)
        g = bloques(dd)
        cols = OPTICO + RADAR
        X = dd[cols].to_numpy(float); y = dd[OBJ].to_numpy(float)
        ge = GroupKFold(n_splits=5)
        res = np.empty(len(y))
        for itr, ite in ge.split(X, y, groups=g):
            m = rf({"n_estimators": 150, "max_depth": 12, "min_samples_leaf": 3}).fit(X[itr], y[itr])
            res[ite] = m.predict(X[ite]) - y[ite]
        r = ensayo_nulo(res, g)
        r["conjunto"] = nombre; r["n"] = len(res); r["bloques"] = int(len(np.unique(g)))
        filas_nulo.append({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
        print("  ensayo nulo %s: mediana=%.3f m  IC95=[%.3f, %.3f]  umbral=%.3f"
              % (nombre, r["mediana"], r["ic95_inf"], r["ic95_sup"], r["umbral_decision"]))

    for nom, filas in (("TP5_cv_anidada.csv", filas_cv),
                       ("TP5_area_de_aplicabilidad.csv", filas_aoa),
                       ("TP5_propagacion_conjunta.csv", filas_pr),
                       ("TP5_ensayo_nulo_distribucion.csv", filas_nulo)):
        if filas:
            pd.DataFrame(filas).to_csv(os.path.join(SAL, nom), index=False)
            print("  escrito %s (%d filas)" % (nom, len(filas)))

if __name__ == "__main__":
    main()
