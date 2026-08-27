# TP2 — Los tres flujos de Orange Data Mining, con sus resultados

Los flujos están en `TP2_LiDAR_GEDI_ICESat2\09_Orange\` y se abren con doble
clic (Orange 3.39 o 3.40; las variables ya vienen preseleccionadas y las
rutas son relativas — el `.ows` debe quedarse en su carpeta). Cada flujo
carga el bosque y la estepa con dos widgets **File**, los une con
**Concatenate** (la columna `recinto` queda como clase, y colorea todos los
gráficos), y de ahí salen los widgets de análisis. Lo que sigue es **lo que
debe verse al abrirlos**, con las cifras reales; las figuras están en
`capturas\Orange_TP2_*.png`.

## 1. `TP2_flujo_GEDI_biomasa.ows` — la referencia de biomasa

Carga las tablas del paso 7 (`biomasa_<AOI>.csv`): **690 huellas con
biomasa en el bosque y 3.083 en la estepa**.

- **Feature Statistics**: la mediana de `agbd_Mg_ha` es **15,0 Mg/ha en el
  bosque y 3,4 en la estepa**; el error estándar mediano (`agbd_se_Mg_ha`),
  13,1 y 3,0 — el 87 % de la mediana en ambos.
- **Distributions** (`agbd_Mg_ha`): las dos distribuciones son
  fuertemente asimétricas — la mayoría de las huellas tiene poca biomasa y
  una cola larga (la lenga) llega hasta ~250 Mg/ha. Por eso el curso
  informa **medianas** y una **media estratificada**, nunca la media simple.
- **Box Plot** (`agbd_Mg_ha` por `recinto`): la dicotomía en una caja —
  las cajas de bosque y estepa ni se rozan.
- **Scatter Plot** (`rh98` contra `agbd_Mg_ha`): la relación
  altura–biomasa que sostiene todo el curso, curvada (alometría, exponente
  > 2): a igual salto de altura, mucho más salto de biomasa arriba que
  abajo.

## 2. `TP2_flujo_ATLAS_control_terreno.ows` — el control de terreno

Carga las tablas del paso 15 (`TP2_control_terreno_ATL08_*_operacional.csv`):
**3.872 segmentos operacionales entre los dos recintos — 3.165 PASAN el
control y 707 se DESCARTAN** (los porcentajes por sitio: 76,3 % del bosque,
87,3 % de la estepa).

- **Distributions** (`delta_terreno_m`): el delta del terreno ATL08 contra
  FABDEM + EGM2008, con el umbral ± 5 m marcado. El pico está pegado a
  cero, con una **cola hacia los negativos**: donde ATL08 detectó el suelo
  demasiado abajo.
- **Box Plot** (`delta_terreno_m` por `control_terreno`): los que PASAN
  tienen mediana a centímetros de cero; los DESCARTADOS, en torno a
  **−7 m** — no es ruido simétrico, es un sesgo.
- **Box Plot** (`h_canopy_m` por `control_terreno`): la clave del práctico.
  Los segmentos descartados declaran un dosel de **mediana 19,9 m contra
  11,1 m de los que pasan**: el suelo mal detectado **inflaba la altura del
  dosel**, y es exactamente lo que corrige el re-cotejo del paso 16
  (la razón bosque baja de 2,70× a 1,87×).
- **Scatter Plot** (`delta` contra `h_canopy`): el mismo mensaje punto por
  punto — la nube roja (descartada) vive en delta negativo y dosel alto.

## 3. `TP2_flujo_CCI_cotejo.ows` — CCI Biomass contra GEDI, huella por huella

Carga el cotejo del anexo (`TP2_cotejo_CCI_L4A_*.csv`): **495 pares con
dato en ambos mapas en el bosque y 1.129 en la estepa**.

- **Scatter Plot** (`agbd_L4A_Mg_ha` contra `agbd_CCI2024_Mg_ha`): la
  dicotomía en un gráfico. El bosque se despega de la diagonal 1:1 hacia
  arriba — **mediana L4A 15,0 contra CCI 146,0 Mg/ha** — salvo en las
  huellas de bosque alto, donde las dos estimaciones convergen. La estepa
  se apila contra el cero del CCI (mediana 0,0 contra 3,4 de L4A).
- **Scatter Plot** (`pendiente_grados` contra CCI): la tercera línea de
  evidencia del anexo — el CCI infla el dosel bajo **de ladera**.
- **Correlations**: los coeficientes son bajos — bosque Pearson 0,27
  (Spearman 0,21); estepa Pearson 0,48 pero **Spearman 0,03**, porque la
  mitad de la estepa vale 0 en el CCI y el orden de rangos se pierde. La
  lección: dos mapas de biomasa del mismo lugar pueden ordenar el
  territorio de maneras casi independientes — cada producto responde a la
  pregunta para la que fue construido (véase la P5 del TP5).

Las cifras coinciden con `CADENA_ESCENARIO_B.log`, con las tablas de
`05_Resultados\04_Tablas\` y con el DESARROLLO de este práctico.
