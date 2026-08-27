# TP2 — Desarrollo completo, con los datos expuestos

El TP2 construye la **referencia de biomasa** del curso (GEDI), la audita
con un segundo LiDAR independiente (ICESat-2/ATL08), somete el terreno de
ambos al árbitro FABDEM, y pone el resultado en el mapa frente al producto
global CCI Biomass. Son **diecisiete pasos** más el auxiliar 1b y tres
auxiliares; el orden completo está en `03_Scripts\00_ORDEN_DE_EJECUCION.md`.

## 1. La ejecución, paso a paso

    conda activate aoi
    cd C:\Temp\CURSO_BIOMASA_2026\02_Practica\TP2_LiDAR_GEDI_ICESat2\03_Scripts

**Pasos 1 a 6 — de los gránulos a las huellas válidas.** Extracción de los
disparos GEDI de los HDF5, recorte a los recintos, y el filtrado de calidad
en cuatro etapas. La extracción deja **6.287 disparos en el bosque y 11.222
en la estepa**, con 27 columnas por disparo (registrado en
`05_Resultados\06_Control_calidad\ULTIMA_EJECUCION.log`).

**Pasos 7 a 11 — la referencia.** Biomasa L4A por huella, partición
entrenamiento/validación, media estratificada por cobertura, exportación
para SIG y los escenarios de hoja caída. El atajo
`09_ATAJOS\EJECUTAR_cadena_escenarioB.bat` corre estos cinco pasos junto
con los cinco del TP5; su registro completo queda en
`06_Control_calidad\CADENA_ESCENARIO_B.log`.

**Pasos 12 a 16 — la rama ICESat-2.** Carga de los segmentos ATL08, cotejo
de alturas contra GEDI, exportación para SIG, **control de terreno contra
FABDEM** (paso 15) y re-cotejo tras el control (paso 16). El atajo
`EJECUTAR_TP2_rama_ICESat2.bat` corre la rama completa.

**Paso 17 — el mapa.** `TP2_17_mapa_biomasa_GEDI_CCI.py` agrega la biomasa
GEDI a celdas de 500 m y la enfrenta al CCI Biomass en la misma escala.

## 2. Los resultados, con los datos a la vista

### 2.1 El filtrado: lo que queda y por qué

De la salida real de `TP2_07_biomasa_referencia.py` (en
`CADENA_ESCENARIO_B.log`):

| Sitio | Disparos extraídos | Válidos con estructura | Conserva | Biomasa mediana | EE mediano |
|---|---|---|---|---|---|
| Bosque | 6.287 | 690 | **11,0 %** | 15,0 Mg/ha | 13,1 Mg/ha |
| Estepa | 11.222 | 3.083 | **27,5 %** | 3,4 Mg/ha | 3,0 Mg/ha |

Las tablas de detalle por filtro quedan en
`06_Control_calidad\filtrado_calidad.csv` y `filtrado_pendiente.csv`.

### 2.2 La referencia estratificada (paso 9)

Del mismo log, la corrección del sesgo de muestreo por cobertura:

| Sitio | Media simple | Media estratificada | Superficie muestreada | Stock |
|---|---|---|---|---|
| Bosque | 36,43 | **44,32 ± 2,20 Mg/ha** | 22.177,9 ha (98,6 %) | 982.905 ± 48.733 Mg |
| Estepa | 8,59 | **7,28 ± 0,27 Mg/ha** | 22.324,8 ha (99,2 %) | 162.554 ± 6.133 Mg |

La media simple del bosque **subestima**: las huellas caen de más en el
ñire bajo y de menos en la lenga. La estratificación por cobertura lo
corrige (tabla `TP5_AGBD_estratificado.csv`, que el TP5 hereda).

### 2.3 El control de terreno FABDEM (pasos 15 y 16): el veredicto de la dicotomía

El paso 15 compara la altura de terreno de cada segmento ATL08 y de cada
huella GEDI contra el suelo desnudo FABDEM más el geoide EGM2008 (la
ondulación N en el AOI va de 19,8 a 21,9 m; el geoide argentino Ar16
difiere de EGM2008 menos de 0,5 m, así que la elección no cambia nada).
Umbral declarado: **±5 m**.

| Control de terreno | Bosque | Estepa |
|---|---|---|
| Segmentos ATL08 operacionales | 1.949 | 1.923 |
| Descartados por terreno | 462 | 245 |
| **Pasan el control** | **76,3 %** | **87,3 %** |
| ATL08 conservador pasa | 95,1 % | 98,1 % |
| GEDI ante el mismo árbitro (mediana del delta) | **+0,22 m** | **+0,47 m** |

El re-cotejo del paso 16, ya sin los segmentos de terreno dudoso:

| Razón de alturas ATLAS/GEDI | Antes del control | Después |
|---|---|---|
| Bosque | 2,70× | **1,87×** |
| Estepa | 3,28× | 3,21× (rho ≈ 0) |

La lectura: en el bosque, buena parte de la discrepancia entre los dos
LiDAR **era suelo mal detectado por ATL08 bajo dosel denso** — controlado el
terreno, la razón cae de 2,70× a 1,87×. En la estepa el control casi no
mueve la aguja: ahí la discrepancia es el **límite metodológico de ATL08
sobre dosel bajo y ralo**, no un error de terreno. GEDI, ante el mismo
árbitro, clava el suelo a centímetros. La referencia del curso pasa el
control que su auditor falla en parte.

**El resultado negativo también queda:** con la altura controlada de ATL08
no se puede calibrar biomasa en estos recintos (16 celdas, R² ≈ 0,03). Está
documentado en `02_Practica\10_Procedimientos_y_resultados\`.

### 2.4 El mapa contra el CCI (paso 17)

En las celdas de 500 m del bosque, la mediana de GEDI es **8,4 Mg/ha** y la
del CCI **136,0 Mg/ha**; en la estepa, 3,2 contra 2,1. Por huella (cotejo
`TP2_cotejo_CCI_L4A_*.csv`, 495 pares en el bosque): mediana L4A 15,0
contra CCI 146,0; media 36,4 contra 135,1. Pero en las huellas de bosque
alto (L4A ≥ 150 Mg/ha, n = 35) las medias **convergen: 182,9 contra
175,3**. La discrepancia no es un error de uno de los dos productos: GEDI
muestrea puntos y su mediana la dominan las huellas de ñire bajo; el CCI
integra el paisaje a 100 m y rellena donde GEDI no pisó. **GEDI mide, el
CCI rellena** — y el TP5 construye el mapa continuo a partir de GEDI.

## 3. Las figuras del procesamiento

En `capturas\`:

- `fig01_flujo.png` — el flujo completo del práctico (los 17 pasos y los
  auxiliares).
- `fig04_embudo_filtrado.png` — el embudo del filtrado: de los disparos
  extraídos a las huellas válidas, en los dos sitios.
- `fig05_alturas_bosque_estepa.png` — las distribuciones de altura rh98:
  bosque y estepa lado a lado.
- `fig06_mapa_footprints.png` — dónde cayeron las huellas válidas en cada
  recinto.
- `scatter_control_terreno_bosque.png` y
  `scatter_control_terreno_estepa.png` — el control de terreno del paso 15:
  cada segmento ATL08 según su delta contra FABDEM + geoide, con el umbral
  ±5 m y lo que pasa (verde) y se descarta (rojo).
- `TP2_cotejo_GEDI_ICESat2_mapa.png` — el cotejo espacial de los dos LiDAR.
- `TP2_mapa_AGB_GEDI_vs_CCI_BOSQUE_NW_02.png` y `..._ESTEPA_NW_02.png` — el
  paso 17: GEDI en celdas de 500 m, el CCI, y la diferencia, por sitio.
- `TP2_mapa_AGB_estilo_CCI_BOSQUE_NW_02.png` y `..._ESTEPA_NW_02.png` — los
  dos productos a la **misma escala de color 0–350 Mg/ha**, que es la
  comparación honesta.
- `TP2_mapa_AGB_GEDI_100y500_vs_CCI_BOSQUE_NW_02.png` y
  `..._ESTEPA_NW_02.png` — el triple que explica por qué GEDI no puede
  competir como mapa: a 100 m (la resolución del CCI) **sólo el 1,7 % de
  las celdas del bosque tiene huella GEDI**; a 500 m el mapa se llena de a
  parches; el CCI, al lado, es continuo. GEDI mide, el CCI rellena.

## 4. Respuestas modelo a las preguntas del práctico

**P1. ¿Por qué una tasa de supervivencia del filtrado cercana al 100 %
debería despertar sospecha en lugar de satisfacción?**

Porque cada filtro tiene una población que debe eliminar, y esa población
existe en cualquier adquisición real: `quality_flag` descarta disparos que
el propio algoritmo de GEDI marca como no confiables; `degrade_flag`,
disparos tomados con el apuntamiento degradado; `sensitivity` (≥ 0,9 en el
bosque), disparos cuya energía no alcanzó a ver el suelo a través del
dosel; y el filtro de pendiente, huellas donde el relieve dentro de los
25 m mezcla suelo y copa. Si sobrevive casi todo, lo más probable no es que
los datos sean perfectos sino que **algún filtro no está funcionando** — un
nombre de columna mal escrito, un umbral leído como texto, una máscara
vacía. La supervivencia del proyecto (11,0 % en el bosque, 27,5 % en la
estepa) es la esperable para GEDI sobre relieve andino; y la comprobación
no es numérica sino espacial: los descartes por pendiente deben caer en las
laderas (véase `fig06_mapa_footprints.png` y el gpkg del paso 10).

**P2. El bosque conserva el 11,0 % de los disparos y la estepa el 27,5 %.
Explique la diferencia a partir de la manera en que cada cubierta devuelve
la forma de onda.**

En el bosque, el pulso debe atravesar un dosel denso y a veces cerrado:
mucha energía vuelve desde las copas y poca desde el suelo, de modo que el
retorno del terreno queda débil y el filtro de sensibilidad (que exige
haber visto el suelo) elimina una fracción grande. Además el bosque del
recinto ocupa las laderas, donde el filtro de pendiente descarta más. En la
estepa, la vegetación baja y rala deja pasar el pulso: el retorno del suelo
es nítido, la sensibilidad requerida se alcanza con facilidad y el relieve
del recinto es más suave. La diferencia 11,0 % contra 27,5 % **no es un
defecto del procesamiento: es la física del LiDAR de forma de onda operando
sobre dos estructuras distintas** — y por eso mismo la estepa aporta más
huellas por hectárea a la referencia.

**P3. Un disparo cae dentro del recinto de bosque pero no supera el filtro
de pendiente. ¿Qué mide realmente ese disparo y por qué su altura resulta
inutilizable?**

Dentro de la huella de 25 m con pendiente fuerte, el terreno mismo cambia
de cota varios metros entre un borde y el otro. El algoritmo identifica
como «suelo» el retorno más bajo y como «copa» el más alto, pero sobre una
ladera el retorno más bajo es el pie de la huella y el más alto puede ser
el suelo del extremo de arriba — o una copa que crece más abajo. La
«altura» que resulta es en parte **relieve dentro de la huella**, no
vegetación: el disparo mide la mezcla de dosel y pendiente. Por eso el
umbral de pendiente se declara y se aplica antes de usar rh98 como
estructura, y por eso el control del paso 15 usa un DEM de suelo desnudo
(FABDEM) como árbitro externo: es la misma confusión suelo/dosel vista
desde otro instrumento.

**P4. El error estándar mediano de la biomasa equivale al 87 % de la
mediana tanto en el bosque como en la estepa. Indique tres afirmaciones
que ese dato permite sostener y tres que no.**

El EE mediano es 13,1 Mg/ha sobre una mediana de
15,0 en el bosque y 3,0 sobre 3,4 en la estepa — el 87 % que el propio
TP2_07 imprime en pantalla: la incertidumbre **por
huella** es del orden de la propia estimación. Permite sostener: (1) que la
biomasa de una huella individual no es citable sola — 15,0 ± 13,1 no
distingue esa huella de su vecina; (2) que las comparaciones válidas son
**agregadas**, donde el error estándar de la media cae con n (por eso la
media estratificada del bosque se informa 44,32 ± 2,20, un error relativo
del 5 %); (3) que la dicotomía bosque–estepa sí está resuelta, porque
44,32 ± 2,20 contra 7,28 ± 0,27 no se solapan ni de lejos. No permite
sostener: (1) que una huella de 20 Mg/ha tenga más biomasa que una de 10;
(2) que un cambio pequeño entre fechas por huella sea real; (3) que la
referencia sea una «medición» — es la estimación de un modelo (L4A) con su
error declarado, y todo lo que el curso construye encima hereda ese piso.

**P5. ¿Por qué la partición en entrenamiento y validación se hereda sin
modificación en los tres prácticos siguientes? ¿Qué ocurriría si cada uno
la rehiciera?**

Porque la validación solo es honesta si las huellas de validación **nunca
participaron de ningún ajuste de la cadena**. El TP5 apila sobre cada
huella del TP2 los índices del TP3 y el γ⁰ del TP4: si cada práctico
rehiciera la partición al azar, una huella usada para entrenar en un paso
aparecería como «independiente» en el siguiente, y los R² de validación
quedarían inflados sin que nadie hubiera hecho trampa a propósito — fuga de
información entre conjuntos. La partición se hace una sola vez (paso 8), se
guarda en las tablas de trabajo, y los tres prácticos siguientes la leen.
Es la misma razón por la que la validación estricta del TP5 (paso 6) separa
además **por bloques espaciales**: las huellas vecinas se parecen, y
repartirlas al azar entre entrenamiento y validación también filtra
información.

## 5. De dónde sale cada cifra

`05_Resultados\06_Control_calidad\CADENA_ESCENARIO_B.log` y
`ULTIMA_EJECUCION.log` (conteos, medianas, estratificada);
`filtrado_calidad.csv` y `filtrado_pendiente.csv` (el detalle por filtro);
las tablas de control del paso 15 y los cotejos `_terreno` del 16 en
`05_Resultados\04_Tablas\`; `TP2_cotejo_CCI_L4A_*.csv` (495 y 1.129 pares);
los mapas del paso 17 en `05_Resultados\02_Rasters\` con sus tablas por
celda; `TP5_AGBD_estratificado.csv` (media estratificada y stock).
