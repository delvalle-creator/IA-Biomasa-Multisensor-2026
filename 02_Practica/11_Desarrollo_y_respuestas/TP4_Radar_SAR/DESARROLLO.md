# TP4 — Desarrollo completo, con los datos expuestos

El TP4 lleva los cuatro radares del proyecto (Sentinel-1 en banda C;
SAOCOM, NISAR y PALSAR-2 en banda L) a una grilla común en γ⁰, demuestra el
moteado y cuánto se recupera promediando, mide el contraste bosque–estepa
por banda y polarización, y cruza el γ⁰ con las huellas GEDI. Diez pasos
más dos auxiliares (`03_Scripts\00_ORDEN_DE_EJECUCION.md`); los pasos 1 a 5
ya están ejecutados y sus productos en `02_Subsets_SNAP_QGIS\` — usted
corre del 6 en adelante.

## 1. La ejecución, paso a paso

    conda activate aoi
    cd C:\Temp\CURSO_BIOMASA_2026\02_Practica

**Pasos 1 a 5 (ya corridos).** γ⁰ con Terrain Flattening para Sentinel-1 y
SAOCOM (los grafos de SNAP de `08_Grafos_SNAP\` — 26 xml: 17 grafos y 9
gemelos `_cli` — se **leen, no se corren**); NISAR GCOV y el mosaico
PALSAR-2 llegan ya corregidos; y la **máscara de validez geométrica**
común, que descarta lo inválido para cualquiera de las dos geometrías
(Sentinel-1 asciende, SAOCOM desciende): **4,4 % del recinto de bosque y
3,5 % del de estepa**.

**Paso 6** (`TP4_06_speckle.py`) mide el moteado y cuánto R² recupera el
promediado. **Paso 7** (`TP4_07_contraste_C_vs_L.py`), el contraste
bosque − estepa. **Paso 8** (`TP4_08_saturacion_radar.py`), el cruce con
GEDI — el cierre del práctico. **Pasos 9 y 10**, exportación a dB para QGIS
e índices polarimétricos del SAOCOM cuadripolar. **Auxiliar TP4_11**,
obligatorio antes de los grafos de BIOMASS: lista las bandas reales del
producto L2A.

## 2. Los resultados, con los datos a la vista

### 2.1 El moteado y el promediado (paso 6)

R² del ajuste de γ⁰ contra la altura del dosel, según la ventana de
promediado:

| Fuente (fecha) | 30 m | 50 m | 90 m | 150 m | 210 m | 310 m |
|---|---|---|---|---|---|---|
| Sentinel-1 VH (banda C), 10/01/2026 | 0,011 | 0,018 | 0,028 | 0,027 | 0,027 | 0,025 |
| NISAR HV (banda L), 08/01/2026 | 0,166 | 0,220 | 0,253 | **0,273** | 0,275 | 0,269 |
| PALSAR-2 HV (banda L), 2025 | 0,114 | 0,137 | 0,164 | 0,177 | 0,188 | 0,195 |
| SAOCOM HV (banda L), 10/01/2026 | 0,092 | 0,103 | 0,120 | 0,141 | 0,153 | 0,161 |
| BIOMASS HV (banda P) | — | — | — | — | — | — |

Dos lecturas. Por filas: en NISAR, promediar de 30 a 150 m recupera casi
diez puntos de R² (0,166 → 0,273) que el moteado se estaba llevando.

**Conviene destacarlo, porque es donde la medición y la decisión no
coinciden:** el R² **no** cae apenas se pasa de los 150 m. En NISAR el
máximo cae en los 210 m (0,275) y a los 310 m todavía vale 0,269; en
PALSAR-2 y en SAOCOM sube hasta el final de la serie (0,195 y 0,161 a
310 m). De modo que **no hay un óptimo numérico en 150 m**: la ventana de
150 m se adopta como **compromiso**, porque es del orden de la huella de
GEDI (25 m de diámetro, con error de geolocalización de unos 10 m) y
porque más allá se promedia bosque que ya no pertenece a la huella que se
está tratando de explicar. Es una decisión declarada, con criterio
explícito, no una propiedad de la naturaleza: si el criterio fuera
maximizar R², la ventana sería de 210 m o más. Por la fila de la
banda C: por más que se promedie, Sentinel-1 no pasa de 0,03 — su problema
no era el moteado. Los guiones de BIOMASS no son ceros: son ausencia (sus
adquisiciones son posteriores al incendio; no existe banda P del bosque en
pie para cruzar con GEDI).

### 2.2 El contraste bosque − estepa (paso 7): la respuesta al título del curso

| Fuente (fecha) | Banda | Pol. | Bosque | Estepa | Contraste |
|---|---|---|---|---|---|
| Sentinel-1 (10/1/2026) | C | VV | −10,15 dB | −13,63 dB | 3,5 dB |
| Sentinel-1 (10/1/2026) | C | VH | −16,10 dB | −20,30 dB | 4,2 dB |
| SAOCOM (10/1/2026) | L | HH | −12,68 dB | −20,74 dB | 8,1 dB |
| SAOCOM (10/1/2026) | L | HV | −17,79 dB | −29,46 dB | **11,7 dB** |
| NISAR (8/1/2026) | L | HH | −7,96 dB | −16,01 dB | 8,0 dB |
| NISAR (8/1/2026) | L | HV | −13,17 dB | −23,11 dB | 9,9 dB |
| PALSAR-2 (2025) | L | HH | −8,05 dB | −16,39 dB | 8,3 dB |
| PALSAR-2 (2025) | L | HV | −12,53 dB | −24,18 dB | **11,6 dB** |

Las regularidades: **la banda L separa los dos sitios con casi el triple de
contraste que la banda C**; dentro de cada banda, la polarización cruzada
(HV/VH) separa más que la co-polar; y NISAR y SAOCOM difieren 4,8 dB sobre
el mismo bosque con dos días de diferencia — advertencia, no resultado
(véase la P4).

### 2.3 El piso de ruido

El canal cruzado del SAOCOM sobre la estepa da mediana **−29,8 dB, con el
64 % de los píxeles por debajo de −28**: eso no describe el pastizal,
describe el ruido del instrumento (véase la P5).

## 3. Las figuras del procesamiento

En `capturas\`, primero las galerías con **todas las imágenes de radar
procesadas**, sitio por sitio (composición RGB: co-polar en dB, cruzada en
dB, y su diferencia — el canal que «enciende» la estructura leñosa):

- `S1_GRD_galeria_*.png` y `S1_SLC_galeria_*.png` — las siete fechas de
  Sentinel-1 de cada sitio (cuatro de línea de base, dos pre y una post),
  en sus dos productos, GRD y SLC, ambos llevados a γ⁰ con Terrain
  Flattening. En el bosque, la escena post-incendio del 27/2/2026 muestra
  el cambio de comportamiento del área quemada.
- `SAOCOM_galeria_*.png` — las tres fechas del SAOCOM-1B (23/11/2025,
  10/1/2026 y 27/2/2026) de cada sitio. En la estepa se ve el piso de
  ruido del canal cruzado: el pastizal queda oscuro porque casi no
  despolariza.
- `NISAR_galeria_*.png` — las tres fechas útiles de NISAR GCOV
  (4/12/2025, 28/12/2025 y 8/1/2026) de cada sitio.
- `PALSAR2_galeria_*.png` — los tres mosaicos anuales de JAXA (2023, 2024
  y 2025) de cada sitio.
- `SAOCOM_quad_T3_Pauli_16ene2024.png` — la escena cuadripolar del SAOCOM
  de la línea de base (16/1/2024), procesada hasta la matriz de coherencia
  T3 y compuesta al estilo Pauli (doble rebote / volumen / superficie).
  **Atención: el análisis polarimétrico está hecho sobre la ESCENA
  COMPLETA, en geometría de radar — no es el recinto BOSQUE_NW_02.**
- `SAOCOM_quad_T3_Pauli_BOSQUE_16ene2024.png` — la misma matriz T3
  **recortada de manera aproximada al recinto BOSQUE_NW_02** (por las
  esquinas declaradas de la escena, todavía sin ortorrectificar). El
  recorte fino del quad-pol a los recintos, sobre la grilla común, es
  justamente el paso pendiente (TP4_01/TP4_02); recién ahí será el insumo
  de los índices polarimétricos del paso 10.
- `ALOS_PALSAR1_SLC\` — las **nueve capturas del procesamiento
  polarimétrico del ALOS PALSAR-1 histórico** (escena SLC quad-pol del
  21/7/2007, banda L): calibración, matriz de coherencia, descomposiciones
  y ortorrectificación en SNAP. El procedimiento completo, paso a paso,
  está en `02_Practica\10_Procedimientos_y_resultados\TP4_ALOS_PALSAR1_SLC\`.
  **También aquí el proceso es de la escena completa, no del recinto de
  bosque**; queda pendiente repetirlo recortado a los recintos.
- `mapa_ubicacion_AOIs.png` — la ubicación de los dos recintos, del
  paquete BIOMASS banda P. **De BIOMASS no hay imagen procesada que
  mostrar**: sus adquisiciones sobre estos recintos son posteriores al
  incendio y la descarga del L2A exige la ficha de la ESA — los grafos
  están listos y el paso previo obligatorio es `TP4_11` (véase la P6).

El estado de cada radar del proyecto, entonces: **procesados y en
galería** Sentinel-1 (GRD y SLC), SAOCOM dual S4DP, NISAR GCOV y los
mosaicos PALSAR-2; **procesado sobre la escena completa** el cuadripolar
histórico ALOS-1 (con su procedimiento documentado) y la primera escena
quad del SAOCOM (hasta T3); **pendientes de procesar por recinto** los
siete productos quad-pol del SAOCOM de la línea de base (pasos 1 y 2) y
los frames restantes del ALOS-1; **pendiente de datos** la banda P de
BIOMASS.

**Los grafos de SNAP, dibujados** (los 17 de `08_Grafos_SNAP\`, con la
cadena real de operadores leída de cada XML — se leen mucho mejor que
abriéndolos de a uno en el Graph Builder):

- `grafos_SNAP_cadenas_gamma0.png` (1 de 5) — las cuatro cadenas de
  Sentinel-1: GRD a γ⁰, SLC a γ⁰, la variante de dos frames, y el recorte
  crudo con fase. El color dice qué hace cada operador: radiometría en
  naranja (el Terrain Flattening destacado en rojo), geometría en azul.
- `grafos_SNAP_SAOCOM_gamma0.png` (2 de 5) — las cuatro cadenas del
  SAOCOM dual: a γ⁰, el recorte crudo con fase, y los dos grafos TNA.
- `grafos_SNAP_polarimetria_quad.png` (3 de 5) — las cuatro cadenas del
  cuadripolar: la matriz T3 preparada, la polarimetría completa, su
  variante con Terrain Flattening, y los índices (RVI, RFDI…).
- `grafos_SNAP_quad_coherentes.png` (4 de 5) — las descomposiciones
  coherentes en abanico: un solo tronco alimenta Pauli, Sinclair,
  Krogager y Cameron.
- `grafos_SNAP_quad_incoherentes.png` (5 de 5) — las ocho descomposiciones
  incoherentes (Freeman-Durden, Yamaguchi, van Zyl, H-A-Alpha, Cloude,
  Touzi, Huynen y Model-Free), que parten de la T3 ya preparada.
- `grafos_SNAP_biomass_bandaP.png` — los tres grafos de BIOMASS: altura
  L2A, región, y la colocación sobre la malla común con `collocateWith`,
  conservando el píxel nativo de ~50 m.

Y las figuras de análisis del práctico:

- `tp4_fig_speckle.png` — el moteado a ventana creciente y la curva de
  recuperación del R²: la demostración del paso 6.
- `tp4_fig_contraste.png` — el contraste bosque − estepa por banda y
  polarización: la tabla de § 2.2 dibujada.
- `tp4_fig_composicion_radar.png` — la composición color de radar de los
  dos sitios: el bosque brilla en banda L, la estepa se apaga.
- `tp4_fig_saocom_vs_nisar.png` — las dos misiones de banda L sobre el
  mismo bosque: formas parecidas, niveles distintos (los 4,8 dB de la P4).
- `tp4_fig_saturacion.png` — el cruce γ⁰–GEDI del paso 8.

## 4. Respuestas modelo a las preguntas del práctico

**P1. ¿Por qué el moteado no se reduce con un instrumento mejor, y qué
procedimiento sí lo reduce?**

Porque el moteado no es ruido del instrumento sino **interferencia propia
de la iluminación coherente**: dentro de un píxel conviven miles de
dispersores cuyas ondas vuelven con fases distintas y se suman
reforzándose o cancelándose al azar. Un radar «mejor» sigue siendo
coherente, así que dos píxeles del mismo bosque seguirán difiriendo varios
decibeles por puro azar de fases. Lo que sí lo reduce es **promediar
miradas independientes** (multilooking espacial): la curva medida en la
tabla de § 2.1 lo demuestra — NISAR HV pasa de R² 0,166 con ventana de
30 m a 0,273 con 150 m, recuperando casi diez puntos que el moteado
ocultaba. **Y también muestra el costo, que no es el que uno esperaría:**
en esta corrida el R² no cae al pasar de 150 m (en NISAR el máximo está en
210 m, y en PALSAR-2 y SAOCOM sigue subiendo hasta 310 m). El límite no lo
pone la curva sino la huella: con ventanas mayores se promedia bosque que
ya no pertenece a la huella de GEDI que se quiere explicar, y el R² sube
por una razón que no es la que interesa. Por eso se adopta 150 m como
compromiso y **se declara la decisión**. Se promedia con criterio medido,
no por costumbre.

**P2. La banda C no supera un R² de 0,03 por más que se promedie. ¿Qué le
falta a la banda C, y por qué la banda L sí lo consigue?**

Le falta **penetración**. La fila de Sentinel-1 VH es plana (0,011 → 0,028
→ 0,025): si el problema fuera el moteado, el promediado la levantaría,
como levanta a NISAR. La onda de ~5,5 cm de la banda C interactúa con
hojas y ramitas de su propio tamaño: se dispersa en la **superficie del
dosel** y satura apenas el follaje se cierra — a partir de ahí, veinte
metros de lenga y cinco de ñire devuelven casi lo mismo. La onda de ~24 cm
de la banda L atraviesa el follaje e interactúa con **ramas gruesas y
troncos**, que es donde se acumula la biomasa y donde la estructura sigue
diferenciándose con la altura: por eso NISAR HV alcanza 0,245 con el mismo
promediado que a la banda C no le sirve de nada. No es una falla de
Sentinel-1: es la física de la longitud de onda frente a la estructura de
este bosque.

**P3. ¿Por qué la polarización cruzada separa el bosque de la estepa mejor
que la co-polar?**

Porque la despolarización exige **dispersión múltiple en un volumen**. El
retorno co-polar (HH, VV) lo generan bien las superficies: suelo, roca,
pastizal — un rebote directo conserva el plano de polarización. El retorno
cruzado (HV, VH) aparece cuando la onda rebota varias veces en elementos
orientados al azar — ramas, troncos, el volumen del dosel — y cada rebote
gira un poco el plano de polarización. La estepa, casi sin volumen leñoso,
despolariza poco (SAOCOM HV: −29,46 dB, en el piso de ruido); el bosque,
puro volumen, despolariza mucho (−17,79 dB). Por eso el contraste HV de la
banda L (11,7 dB) casi triplica al VV de la banda C (3,5 dB): el canal
cruzado es, en la práctica, un **detector de estructura leñosa**.

**P4. NISAR y SAOCOM difieren 4,8 dB sobre el mismo bosque. ¿Qué conclusión
es incorrecta y qué comparación sí es legítima?**

Incorrecta: que uno de los dos esté mal calibrado, o «midiendo mal». Las
dos misiones observan con **ángulos de incidencia distintos y calibraciones
absolutas independientes**; el γ⁰ absoluto de un mismo bosque puede diferir
varios dB entre ellas sin que ninguna esté equivocada. Legítimo es comparar
**formas y contrastes dentro de cada misión**: el contraste bosque − estepa
de NISAR HV (9,9 dB) contra el de SAOCOM HV (11,7 dB) — magnitudes
relativas, cada una medida contra sí misma — y la forma espacial de ambos
mapas (`tp4_fig_saocom_vs_nisar.png`: parecidos en estructura, corridos en
nivel). Confundir valores absolutos con contrastes es el error más
frecuente al mezclar productos de misiones distintas, y este par de fechas
casi simultáneas lo deja demostrado con datos propios.

**P5. El canal cruzado del SAOCOM sobre la estepa da una mediana de
−29,8 dB. ¿Qué significa esa cifra y qué decisión metodológica impone?**

Que ahí ya no se está midiendo el pastizal sino el **piso de ruido del
instrumento** (NESZ): el 64 % de los píxeles queda por debajo de −28 dB,
donde la señal devuelta por la escena es comparable o inferior al ruido
propio del sistema. Los valores registrados en esa zona no son
retrodispersión de la estepa: son azar instrumental con forma de mapa. La
decisión que impone: **el canal cruzado de banda L no se usa
cuantitativamente en la estepa**, y así queda declarado en los productos —
se lo excluye de los modelos y de las estadísticas de ese sitio. La lección
general: antes de usar un canal, comprobar que la escena esté por encima
del piso de ruido; un número siempre aparece, pero no siempre significa.

**P6. El catálogo de BIOMASS ofrece una colección de biomasa aérea que
todavía no contiene datos. ¿Qué distinción conceptual explica esa
situación, y qué producto de la misión sí resulta hoy utilizable?**

La distinción entre **que un producto exista y que un producto esté
publicado** — la misma del TP1, en su versión extrema: la colección figura
en el catálogo porque la misión publica por etapas según su calendario
oficial, y la entrada del catálogo se crea antes que su contenido. Hoy lo
utilizable es el **producto de altura de dosel L2A** (publicado el 30 de
junio de 2026): el proyecto tiene sus grafos listos
(`graph_biomass_l2a_altura` y `graph_biomass_a_malla_comun`, que conserva
el píxel nativo de ~50 m — llevarlo a 10 m fabricaría un detalle que el
sensor nunca vio), previa corrida obligatoria de
`TP4_11_inspeccionar_biomass_L2A.py` para verificar los nombres reales de
banda. La biomasa L2 de banda P está calendarizada para 2027; cuando
llegue, la fila de guiones de la tabla de § 2.1 deberá ser la de mayor
contraste de todas, y este práctico deberá reescribirse.

**P7. La combinación de las órbitas ascendente y descendente de NISAR
agrega muy pocas celdas con dato y, sin embargo, revela una diferencia
sistemática entre geometrías. Explique por qué ocurren ambas cosas,
indique qué procedimiento permite distinguir esa diferencia del moteado, y
por qué el promedio de las dos órbitas debe calcularse en potencia lineal
y no en decibeles.**

**Por qué aporta tan poca cobertura.** Un producto GCOV llega con la
corrección radiométrica de terreno ya aplicada y con la máscara de la
misión puesta, de modo que casi no deja huecos que rellenar: sobre el
recinto de bosque cada órbita tiene dato en el 99,97 % de las celdas, y la
fusión agrega **574 celdas de 2.250.000**, el 0,03 %; sobre la estepa,
tres. La segunda geometría sólo rellena donde la primera quedó en sombra y
ella mira desde el lado correcto, y eso aquí casi no ocurrió. Quien espere
ver aparecer laderas enteras que una órbita no medía, no las va a
encontrar en estos productos.

**Por qué sí aparece una diferencia sistemática.** Son dos preguntas
distintas: no cuántas celdas tienen dato, sino cuánto cambia el valor
medido según desde dónde se mire. La retrodispersión depende del ángulo
entre el haz y la superficie, y con relieve ese ángulo cambia con la
órbita. La diferencia **crece con la pendiente** —de 2,06 dB de mediana
entre 0 y 5° a 3,19 dB por encima de 30°, en el bosque— y **cambia de
signo con la orientación de la ladera**: sobre pendientes de más de quince
grados, las que miran al oeste las mide 1,54 dB más alto la ascendente, y
las que miran al este, 0,75 dB más alto la descendente. Cada órbita lee
mejor la ladera que le da la cara. Por eso el sesgo general también
invierte el signo entre recintos: en el bosque la ascendente mide 0,36 dB
por encima, y en la estepa la descendente mide 0,79 por encima.

**Cómo se separa del moteado.** Promediando la diferencia en ventanas cada
vez más grandes. El moteado baja con la raíz del número de celdas
promediadas; lo que no baja de ese modo es estructura del terreno.

| Ventana | Desviación típica medida | Si fuera sólo moteado |
|---|---|---|
| 10 m | 3,40 dB | 3,40 dB |
| 30 m | 1,87 dB | 1,13 dB |
| 100 m | 1,08 dB | 0,34 dB |
| 300 m | **0,72 dB** | 0,11 dB |

A diez metros la cifra no dice nada sobre la geometría: los 3,40 dB son
del orden de los 2,79 que predice la estadística para las 4,8 vistas del
producto. A trescientos metros, en cambio, el moteado ya debería haber
caído a 0,11 dB y todavía quedan 0,72. Eso ya no es ruido: el 17,2 % de
esas celdas se aparta más de un decibel en el bosque, y el 35,2 % en la
estepa.

**Por qué el promedio va en potencia lineal.** El decibel es un logaritmo,
y promediar logaritmos equivale a la media geométrica de las potencias:
tira el resultado hacia el valor más bajo y no corresponde a ninguna
magnitud física. Se promedian las potencias y recién después se pasa a
decibeles con 10·log₁₀. Donde una sola de las dos órbitas tiene dato, la
fusión usa esa y no promedia nada.

**Lo que la combinación no arregla.** Baja el moteado, porque son dos
adquisiciones independientes —el HV pasa de 2,26 y 2,28 dB a 1,72 en el
bosque, una razón de 0,76 contra el 0,71 que predice promediar dos
escenas—, y deja legible el relieve abrupto, donde las dos órbitas
discrepan hasta 8,55 dB. Pero no corrige la geometría: donde hubo layover
los dos ecos llegaron ya sumados en la misma celda y ninguna media los
separa, y el acortamiento sigue comprimiendo la ladera. La prueba está en
las propias cifras: si el promedio corrigiera el problema, la diferencia
residual a trescientos metros no seguiría creciendo con la pendiente. Para
eso está la máscara de validez del paso 5, que no arregla nada pero dice
dónde no hay que medir.

## 5. De dónde sale cada cifra

Las tablas de los pasos 6 a 8 en `05_Resultados\04_Tablas\` (curva de
promediado, contraste por banda y polarización, cruce γ⁰–GEDI); la máscara
de validez y sus porcentajes, del paso 5 (`04_Validacion\`); el piso de
ruido del SAOCOM, del análisis del paso 7 sobre la estepa; el estado de la
colección BIOMASS, de `06_Control_calidad\CONSULTA_BIOMASS.log` del TP2 y
del calendario oficial reproducido en la guía general (capítulo 6, Tablas
26 a 30). Las cifras citadas coinciden con las de ese capítulo. Las de la
combinación de órbitas de NISAR —cobertura agregada, diferencia por
ventana, por pendiente y por orientación de ladera, y moteado— salen de
la corrida de `TP4_03c_nisar_post_y_fusion.py` sobre los dos recortes de
agosto de 2026, y están reunidas en
`00_Guia_del_practico\ANEXO_NISAR_fusion_ASC_DES.md`.
