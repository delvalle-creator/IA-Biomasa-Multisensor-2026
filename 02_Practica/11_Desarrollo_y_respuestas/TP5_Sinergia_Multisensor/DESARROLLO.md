# TP5 — Desarrollo completo, con los datos expuestos

El TP5 no descarga ni pre-procesa nada: apila sobre cada huella válida del
TP2 los índices ópticos del TP3 y el γ⁰ del TP4, ajusta los **cinco
modelos** (el quinto, sólo LiDAR, es el control), valida por sitio y por
franja de altura, mide el cambio de biomasa por severidad de incendio
**con su ensayo nulo**, y produce los mapas finales. Seis pasos más el
auxiliar de diagnóstico (`03_Scripts\00_ORDEN_DE_EJECUCION.md`).

## 1. La ejecución, paso a paso

    conda activate aoi
    cd C:\Temp\CURSO_BIOMASA_2026\02_Practica\TP5_Sinergia_Multisensor\03_Scripts

**Paso 1** (`TP5_01_dataset.py`) arma el dataset por huella y **hereda la
partición del TP2** — no la rehace (véase la P5 del TP2). El registro de la
corrida muestra la cobertura de predictores: en el bosque, 495 de 690
huellas con biomasa L4A (71,7 %) y 15 huellas (2,2 %) sin γ⁰ por la máscara
geométrica; en la estepa, 1.129 con L4A (36,6 %) y 45 (1,5 %) sin γ⁰.

**Paso 2** (`TP5_02_modelos.py`): los cinco modelos — óptico, SAR,
óptico+SAR, óptico+SAR+LiDAR, y sólo LiDAR como control — en versión lineal
y bosque aleatorio, para altura y para biomasa. **Paso 3**
(`TP5_03_validacion.py`): validación por sitio y **por franja de altura**.
**Paso 4** (`TP5_04_biomasa_quemada.py`): el cambio por clase de severidad
con su incertidumbre y el **ensayo nulo** sobre la clase «sin cambio».
**Paso 5** (`TP5_05_mapas.py`): los mapas de biomasa, cambio e
incertidumbre, con la máscara de validez geométrica del TP4. **Paso 6**
(`TP5_06_validacion_estricta.py`, en `03_Analisis`): la validación por
bloques espaciales. El auxiliar `TP5_06_diagnostico_del_piso.py` (en
`03_Analisis\incendio` — programa distinto pese al número repetido) averigua
de dónde sale el piso del ensayo nulo.

## 2. Los resultados, con los datos a la vista

### 2.1 Los cinco modelos (paso 2)

**Altura (rh95), los dos sitios juntos** — R² de validación del bosque
aleatorio (`TP5_modelos_altura.csv`):

| Modelo | R² validación | RMSE |
|---|---|---|
| óptico | 0,605 | 2,04 m |
| SAR | 0,601 | 2,05 m |
| óptico+SAR | 0,635 | 1,96 m |
| óptico+SAR+LiDAR | **0,964** | 0,61 m |
| **sólo LiDAR (control)** | **0,956** | 0,68 m |

**Biomasa (Mg/ha), los dos sitios juntos** — R² de validación lineal
(`TP5_modelos_biomasa.csv`):

| Modelo | R² validación | RMSE |
|---|---|---|
| óptico | 0,301 | 22,8 |
| SAR | 0,154 | 25,0 |
| óptico+SAR | 0,287 | 23,0 |
| óptico+SAR+LiDAR | **0,886** | 9,2 |
| **sólo LiDAR (control)** | **0,873** | 9,7 |

La lectura del control está en la P1. El detalle por sitio (sólo bosque,
sólo estepa, y los cruces entrena-en-uno-valida-en-el-otro) está en las
mismas tablas; los cruces muestran R² lineales **negativos** — un modelo de
bosque aplicado a la estepa es peor que responder siempre el promedio — y
el área de aplicabilidad (`TP5_area_de_aplicabilidad.csv`) lo cuantifica:
sólo el 6,4 % de la estepa cae dentro del dominio del modelo de bosque.

### 2.2 La validación por sitio y por franja (paso 3)

Por sitio (`TP5_validacion_sitio.csv`, modelo óptico+SAR): los dos juntos
R² 0,437; **bosque solo 0,393, RMSE 4,71 m, sesgo +0,57 m** — un global
que parece sano. Por franja (`TP5_validacion_franjas.csv`, bosque):

| Franja (m) | n | Sesgo | RMSE |
|---|---|---|---|
| 0–3 | 27 | **+3,93 m** | 4,02 m |
| 3–6 | 48 | +2,82 m | 3,01 m |
| 6–9 | 10 | +1,14 m | 2,17 m |
| 9–12 | 5 | −1,80 m | 2,01 m |
| 12–15 | 10 | −3,66 m | 3,84 m |
| 15–18 | 5 | −6,15 m | 6,21 m |
| 18–21 | 5 | **−9,27 m** | 9,31 m |

**Compresión hacia la media**: lo bajo se infla, lo alto se recorta — un
rodal de 20 m se predice de ~11. El sesgo global +0,57 m es el promedio de
dos errores grandes de signo contrario (véase la P3).

### 2.3 El cambio por severidad y el ensayo nulo (paso 4)

Bosque (`TP5_biomasa_por_severidad.csv`):

| Clase | Hectáreas | Pérdida (Mg/ha) |
|---|---|---|
| **Sin cambio (ensayo nulo)** | 4.170,5 | **−10,25** |
| Severidad baja | 1.842,7 | 11,50 |
| Severidad moderada-baja | 2.825,5 | 15,54 |
| Severidad moderada-alta | 3.672,0 | 12,81 |
| Severidad alta | 9.668,2 | 15,21 |

Sobre terreno del bosque que **no se quemó**, el procedimiento mide
−10,25 Mg/ha donde debería medir cero: ese es el piso de ruido de la
cadena, y las clases quemadas (11,5 a 15,5) apenas lo superan — señal
sobre ruido ≈ 1,5. En la estepa el ensayo nulo da **1,0 Mg/ha** con señales
de 3,7–4,0: la cadena es limpia donde el terreno es simple.

El auxiliar de diagnóstico (`TP5_diagnostico_del_piso.csv`) identifica al
culpable: no es el radar — es **un solo índice óptico, el EVI**. Con el
juego completo óptico+SAR el piso es −5,01 Mg/ha; quitando el EVI cae a
**−0,48**, y el cociente señal/piso sube de 1,5 a **15,3**.

### 2.4 La cadena de error (paso 4)

`TP5_cadena_de_error.csv`, bosque: el error del modelo de altura
(s1 = 4,32 m) se convierte por la alometría en 13,6 Mg/ha, contra un
piso de referencia L4A de 13,1 — **el error de la cadena óptico+radar es
del mismo tamaño que el de la referencia misma**. La propagación conjunta
por Montecarlo (`TP5_propagacion_conjunta.csv`) da 16,2 Mg/ha contra 14,7
de la suma en cuadratura: las correlaciones entre términos agregan un 10 %.

### 2.5 La validación estricta (paso 6) y los mapas (paso 5)

La validación por **bloques espaciales** (`TP5_cv_anidada.csv`) baja los R²
de la partición heredada a lo que valen sobre territorio no visto: bosque
óptico+radar **0,427** (RMSE 5,01 m), estepa 0,429, los dos juntos 0,545.
El optimismo de la partición al azar queda cuantificado (columna
`optimismo`). Los mapas del paso 5 (`05_Resultados\02_Rasters\`) aplican la
máscara de validez geométrica del TP4 y **enmascaran fuera del rango de
ajuste** (bosque: 2,0 a 26,3 m; estepa: 1,9 a 13,3 m): un píxel enmascarado
no es un fracaso, es honestidad.

## 3. Las figuras del procesamiento

En `capturas\`:

- `TP5_mapas_finales.png` — los mapas del paso 5: para el **bosque**, la
  biomasa pre-incendio, el cambio y la incertidumbre, con la máscara
  aplicada; para la **estepa**, sólo la biomasa pre-incendio — es el sitio
  control, el fuego tocó el 1,85 % de su superficie, y su papel no es un
  mapa de cambio sino el ensayo nulo del paso 4.

(Los rásters fuente para explorar en QGIS:
`TP5_biomasa_pre_*.tif`, `TP5_biomasa_cambio_*.tif`,
`TP5_incertidumbre_*.tif`, para los dos recintos.)

## 4. Respuestas modelo a las preguntas del práctico

**P1. El modelo completo alcanza 0,964 y el modelo que usa sólo LiDAR
alcanza 0,956. ¿Qué conclusión permite esa comparación y qué conclusión
errónea se habría extraído sin el modelo de control?**

La comparación dice que, con los predictores derivados de GEDI adentro,
**el óptico y el radar aportan ocho milésimas de R²**: casi toda la
capacidad del modelo completo ya estaba en el LiDAR, porque esos
predictores comparten origen con la variable que se estima. Sin la fila de
control, el 0,964 se habría presentado como un triunfo de la «sinergia
multisensor» — cuando en realidad es, sobre todo, GEDI prediciéndose a sí
mismo. La conclusión metodológica: **todo modelo con predictores
emparentados con la respuesta necesita un control que use sólo esos
predictores**, para separar lo que aporta la sinergia de lo que aporta el
parentesco. La sinergia real se mide donde el LiDAR no participa: en la
validación por bloques, óptico+radar mejora al óptico solo en los dos
sitios (bosque 0,377 → 0,427; estepa 0,340 → 0,429), y los mapas del paso 5
extienden la estimación a donde GEDI no pisó — ese es el aporte que sí es
sinergia.

**P2. En el bosque, el modelo de radar solo rinde peor que el óptico solo
y, sin embargo, sumado al óptico aporta puntos. Explique por qué ambas
cosas pueden ser ciertas a la vez.**

Porque rendimiento individual y aporte marginal son cosas distintas: lo que
importa al sumar un predictor no es cuánto explica por sí solo sino
**cuánto explica de lo que el otro no ve**. El óptico y el radar miran
cosas distintas — el óptico, el estado del dosel (verdor, agua); el radar
de banda L, la estructura leñosa debajo —, así que sus errores están poco
correlacionados: el radar acierta justamente en los rodales cerrados donde
el óptico satura (TP3, § 2.3). En el bosque, en altura
(`TP5_modelos_altura.csv`, solo bosque, modelo lineal), el SAR solo valida
0,429 contra 0,484 del óptico solo — rinde peor — pero óptico+SAR sube a
0,552: los **6,8 puntos** de la pregunta, información complementaria, no
redundante. El contraejemplo es la estepa: allí el radar cruzado está en el
piso de ruido (TP4, P5), no trae información nueva, y la suma casi no
mejora — complementariedad hay cuando cada sensor ve algo que el otro no,
no siempre.

**P3. El coeficiente global de validación del modelo de altura es 0,393 y
no revela el problema. ¿Qué revela la validación por franja, y por qué esa
distinción es decisiva para estimar biomasa?**

La validación por franja revela la **compresión hacia la media**: el modelo
infla lo bajo (+3,93 m en la franja 0–3) y recorta lo alto (−9,27 m en
18–21) — predice el bosque «promedio» en todas partes. El global 0,393 con
sesgo +0,57 m no lo muestra porque los dos errores se cancelan al
promediar. Para biomasa la distinción es decisiva por la alometría: la
biomasa crece con la altura elevada a ~2,6
(`TP5_cadena_de_error.csv`), así que el error no es simétrico — recortarle
9 m a un rodal de 20 le quita mucha más biomasa que la que le regala
inflarle 4 m a un matorral. Un mapa hecho con ese modelo **subestima
sistemáticamente los rodales altos, que es donde está el stock**: el sesgo
por franja se convierte en sesgo de inventario. Por eso la franja, y no el
global, es la validación que manda — y por eso los mapas del paso 5
enmascaran fuera del rango de ajuste en lugar de extrapolar.

**P4. El ensayo nulo arroja −10,25 Mg/ha sobre terreno que no se quemó.
¿Cómo debe informarse entonces un cambio medido de 15,5 Mg/ha en una clase
quemada?**

Junto a su piso, y nunca solo: «pérdida estimada de 15,5 Mg/ha, con un
ensayo nulo de −10,25 Mg/ha sobre terreno sin cambio del mismo sitio» — es
decir, una señal de apenas 1,5 veces el ruido de la cadena. Presentada
así, la cifra dice lo que puede decir: que hay pérdida detectable en las
clases quemadas, con una magnitud que no debe tomarse al valor nominal. El
diagnóstico del piso agrega la parte constructiva: el ruido sale de un solo
índice (el EVI), y sin él el piso cae a −0,48 con señal/ruido 15,3 — la
corrida de referencia mantiene el juego completo de predictores
precisamente para que el estudiante vea el problema y su diagnóstico. La
regla para el informe: **ninguna cifra de cambio sin su ensayo nulo al
lado**, como ninguna biomasa sin su error (TP2, P4).

**P5. Las correlaciones de rangos contra los mapas nacionales son de 0,280
en altura y 0,151 en cobertura. ¿Significa eso que alguno de los dos
productos está equivocado?**

No. Significa que se están comparando estimaciones hechas a **escalas
distintas para preguntas distintas**. Los mapas nacionales integran píxeles
grandes y clases amplias, calibrados para ser correctos en el agregado
regional; el mapa del práctico estima huella por huella sobre 15 × 15 km,
calibrado contra GEDI local. Una correlación de rangos baja entre ambos es
compatible con que **los dos sean correctos a su escala**: el nacional
puede ordenar bien los departamentos y mal los rodales; el local, al revés.
Lo que sí sería síntoma de error es una discrepancia del agregado (el stock
total del recinto contra lo que el nacional asigna a esa zona) o un
desacuerdo con la referencia común (GEDI). La lección cierra el curso: un
mapa no es «el verdadero» por ser oficial ni por ser propio — cada producto
responde a la pregunta para la que fue construido, y compararlos exige
declarar la escala.

## 5. De dónde sale cada cifra

Todas las tablas citadas están en `05_Resultados\04_Tablas\`:
`TP5_modelos_altura.csv` y `TP5_modelos_biomasa.csv` (los cinco modelos),
`TP5_validacion_sitio.csv` y `TP5_validacion_franjas.csv`,
`TP5_biomasa_por_severidad.csv`, `TP5_cadena_de_error.csv`,
`TP5_propagacion_conjunta.csv`, `TP5_diagnostico_del_piso.csv`,
`TP5_cv_anidada.csv`, `TP5_area_de_aplicabilidad.csv`,
`TP5_AGBD_estratificado.csv` y `TP5_escenarios_hoja_caida.csv`. Los mapas,
en `05_Resultados\02_Rasters\`; los registros completos de la cadena, en
`..\TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad\`
(`CADENA_ESCENARIO_B.log` y `CADENA_TP5_FINAL.log`).
