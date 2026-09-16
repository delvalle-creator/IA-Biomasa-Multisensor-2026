# Los grafos de SNAP del TP4 — qué hay, cómo se abren y qué alcance tienen

Los veintisiete grafos del TP4 viven **en esta carpeta**, `08_Grafos_SNAP`; los
dos de BIOMASS banda P están aparte, en
`03_Scripts\01_Pre_procesamiento\BIOMASS_bandaP`, junto al programa que
inspecciona el producto. El TP3 tiene el suyo en su propia carpeta
`08_Grafos_SNAP`.

De los veintisiete, **dieciocho son grafos y nueve son sus gemelos `_cli`**. Los
`_cli` los usa Python desde la línea de órdenes y no abren bien en la interfaz
gráfica: trabaje siempre con los que no llevan ese sufijo. De los dieciocho,
`Fusion_ASC_DES_NISAR.xml` es el único que se corre en clase, y es opcional: el
resto se lee, porque sus productos ya están en `02_Subsets_SNAP_QGIS`.

## Antes de abrir uno: qué está vacío a propósito y qué hay que completar

**El archivo de entrada y el de salida están vacíos** en los grafos de interfaz.
No es un olvido: son los dos campos que se completan en el Graph Builder al
abrirlo, eligiendo la escena y el destino.

**Varios parámetros vacíos tampoco son faltantes.** En SNAP, `sourceBands` vacío
significa «todas las bandas»; `externalDEMFile` vacío, «usar el modelo de
elevación que el operador descarga solo»; `tiePointGridNames` vacío, «ninguna
grilla auxiliar». Dejarlos así es lo correcto, y completarlos a mano suele
romper el grafo.

**Doce grafos llevan rutas escritas que empiezan en `C:\Temp\CURSO_BIOMASA_2026`.**
Son los tres de BIOMASS, `graph_s1_slc_tc`, los seis del SAOCOM cuadripolar y los
dos del TNA. Si el curso está en otra carpeta, esas rutas hay que cambiarlas al
abrir el grafo: SNAP no avisa que la ruta no existe hasta que se ejecuta.

**`graph_s1_slc_tc.xml` escribe en `05_Resultados\target.dim`**, que es el nombre
por omisión del Graph Builder. Conviene cambiarlo antes de ejecutarlo, o la
corrida siguiente pisa la anterior.

Los treinta grafos —los veintisiete de esta carpeta, los dos de BIOMASS y el del
TP3— están bien formados y abren en el Graph Builder con las cajas separadas y
la cadena a la vista.

## Los que existen y están completos

| Grafo | Cadena | Para qué |
|---|---|---|
| `graph_s1_grd_tc.xml` | Read → Apply-Orbit → ThermalNoise → Calibration(β⁰) → Subset → **Terrain-Flattening** → Terrain-Correction → Write | Sentinel-1 GRD a γ⁰ |
| `graph_s1_slc_tc.xml` | + TOPSAR-Deburst y Multilook | Sentinel-1 SLC a γ⁰ |
| `graph_s1_slc_tc_2frames.xml` | + SliceAssembly al principio | cuando el AOI cae entre dos frames |
| `graph_saocom_tc.xml` | Read → Calibration(β⁰) → Subset → Multilook → **Terrain-Flattening** → Terrain-Correction → Write | SAOCOM **StripMap** (S4, S6) a γ⁰ |
| `graph_s1_slc_crudo.xml` | Read → TOPSAR-Split → Apply-Orbit → Write | recorte **con fase** de Sentinel-1 |
| `graph_saocom_crudo.xml` | Read → Subset → Write | recorte **con fase** de SAOCOM |
| `BIOMASS_bandaP/procesamiento_BIOMASS.xml` | Read → Calibration(β⁰) → Multilook → Speckle → **Terrain-Flattening** → Terrain-Correction → Write | BIOMASS banda P a γ⁰ |
| `BIOMASS_bandaP/procesamiento_polarimetrico_BIOMASS.xml` | Read → Calibration(complejo) → Matrices **T3** → Orientation-Angle → Speckle pol. → **Terrain-Flattening** → Freeman-Durden → Terrain-Correction → Write | descomposición polarimétrica de BIOMASS |
| `graph_saocom_quad_indices.xml` | Read → Calibration(complejo) → Subset → **Polarimetric-Parameters** → Terrain-Correction → Write | RVI, RFDI, CSI, VSI, BMI del SAOCOM **S6 StripMap** del bosque |
| `graph_saocom_quad_polarimetria.xml` | Read → Calibration → Subset → Matrices T3 → **Terrain-Flattening** → Orientation-Angle → Speckle pol. → Freeman-Durden → Terrain-Correction → Write | descomposición polarimétrica del mismo S6 |
| `graph_saocom_tna_localizar.xml` | Read → BandSelect(una sub-franja) → Calibration(σ⁰) → Multilook 10×10 → Terrain-Correction 100 m → Write | **paso 0 de la estepa**: se corre cinco veces, S1 a S5, para ver cuál sub-franja cae sobre el AOI |
| `graph_saocom_tna_indices.xml` | Read → BandSelect → Calibration(complejo) → **Polarimetric-Parameters** → Terrain-Correction → Subset → Write | índices del SAOCOM **TNA TopSAR** de la estepa |

Las dos cadenas de BIOMASS calibran a β⁰ y llevan Terrain Flattening; la
polarimétrica pasa por matrices T3 con corrección de ángulo de orientación. No
es un detalle de estilo: calibrar a σ⁰ o saltear el flattening cambia el
resultado en ladera, que es casi todo el recinto de bosque.

El orden de la estepa es: primero `localizar` (cinco corridas rápidas, minutos),
después `indices` sobre la sub-franja que haya salido. No al revés y no salteando
el primero: sin saber qué sub-franja es, el segundo se correría sobre la
equivocada.

Y en el TP3, `graph_s2_l2a_subset.xml`: Read → Resample(10 m) → Reproject →
Write. Verificado que **sí alinea a la grilla común**: fija esquina por
parámetro, `referencePixelX/Y = 0`, 1500 × 1500 a 10 m, EPSG:32719, y sale en
BEAM-DIMAP. Está bien.

## Los dos usos de un grafo, y por qué hay dos archivos

Un mismo XML no puede a la vez abrir limpio en la interfaz gráfica y ser
parametrizable desde un programa. Los marcadores del tipo `${entrada}` son de
línea de órdenes: `gpt` los sustituye, pero el Graph Builder los toma como texto
literal, y entonces la lista de bandas aparece vacía y el grafo se abre con el
error `For input string: "null"`. Por eso cada cadena que usa Python tiene dos
archivos:

| Se abre en el Graph Builder | Lo llama el programa de Python |
|---|---|
| `graph_s1_grd_tc.xml` | `graph_s1_grd_tc_cli.xml` |
| `graph_s1_slc_tc.xml` | `graph_s1_slc_tc_cli.xml` |
| `graph_s1_slc_tc_2frames.xml` | `graph_s1_slc_tc_2frames_cli.xml` |
| `graph_saocom_tc.xml` | `graph_saocom_tc_cli.xml` |
| `graph_s1_slc_crudo.xml` | `graph_s1_slc_crudo_cli.xml` |
| `graph_saocom_crudo.xml` | `graph_saocom_crudo_cli.xml` |

`TP4_01_procesar_sar.py` y `TP4_02_recortar_crudo.py` apuntan a la columna
derecha. Cada `_cli` es idéntico a su original salvo en el encabezado y en los
marcadores, y se comprobó archivo por archivo.

**Cuidado al mantenerlos:** si se cambia un parámetro en uno, hay que cambiarlo
en el otro. Se comprueba con cualquier comparador de archivos.

**`graph_s2_l2a_subset.xml` no entra en esto y no hay que tocarlo.** Sus cuatro
marcadores son necesarios: `TP3_01_recortar_sentinel2.py` le pasa la esquina de
la malla, que vale 287.200 / 5.285.200 en el bosque y 319.100 / 5.269.200 en la
estepa. Un valor fijo ahí procesaría los dos sitios sobre la misma esquina, y el
error sería silencioso.

## La trampa del TNA, que conviene entender antes de tocar la estepa

Es la razón de que la estepa necesite dos grafos en vez de uno.

El producto TNA trae **cinco sub-franjas** (S1 a S5), cada una con su propio
raster y sus cuatro polarizaciones. Uno esperaría recortar por coordenadas y
listo. No se puede: **SNAP le asigna al producto una sola geocodificación**, no
una por sub-franja. En `Tie-Point Grids` hay cuatro grillas para todo el producto
(latitude, longitude, incident_angle, slant_range_time), y `Analysis → Geo-Coding`
sobre cualquier banda devuelve las esquinas de la **huella completa**:

    Sup. izq.  40°21'24" S   69°06'35" W
    Sup. der.  40°04'41" S   70°27'42" W
    Inf. izq.  43°10'37" S   70°03'34" W
    Inf. der.  42°53'07" S   71°29'13" W

Eso no puede ser una sub-franja: el raster de S1 tiene 3725 muestras con paso de
1,67 × 10⁻⁸ s, o sea 2,5 m en rango inclinado, unos 9 km, que en tierra son
quince o veinte kilómetros. Las esquinas de arriba abarcan ciento quince.

**Consecuencia práctica:** un `Raster → Subset` con la pestaña *Geo Coordinates*
sobre la banda de una sub-franja convierte las coordenadas a píxeles con una
geocodificación que no corresponde a ese raster, y devuelve un recorte **en el
lugar equivocado, sin ningún mensaje de error**. La única geometría confiable es
la posterior al `Terrain-Correction`, que resuelve la posición con la órbita y el
DEM. Por eso en `graph_saocom_tna_indices.xml` el `Subset` va **después** del
Terrain-Correction, al revés que en el grafo del bosque. Cuesta más —hay que
geocodificar los 344 km de la sub-franja entera para quedarse con 15 × 15 km—
pero es lo correcto. Ése es también el rodeo al problema de fondo: el lector de
SAOCOM de SNAP 13 lee mal los productos TOPSAR Narrow de cinco sub-franjas.

**Sobre las ráfagas y el deburst:** cada sub-franja tiene 10 ráfagas de 876
líneas, con repetición de 0,2431 Hz, o sea una cada 4,11 s. La adquisición dura
43,1 s y cubre unos 344 km: cada ráfaga cubre entonces unos 34 km. El AOI de la
estepa mide 15 km, así que **entra dentro de una sola ráfaga** y no hace falta
unir ninguna. Por eso los grafos del TNA no llevan deburst. Y de todos modos no
se podría: `TOPSAR-Deburst` está escrito para Sentinel-1 —«the input to the
operator is the Sentinel-1 TOPSAR IW or EW SLC product»— y ni siquiera abre su
diálogo sobre un producto SAOCOM. Si al mirar el resultado aparecieran costuras
horizontales, quiere decir que el AOI cayó justo en un empalme; ahí conviene
correr el recorte por separado sobre cada mitad o desplazar levemente el AOI.

## Cuatro decisiones de cadena que conviene no deshacer

**`Polarimetric-Parameters` no acepta matrices.** Ni C3 ni T3. Necesita el
producto full-pol, con las cuatro polarizaciones como bandas. Por eso los dos
grafos de índices no llevan `Polarimetric-Matrices`, ni corrección de ángulo de
orientación —que también convierte a matriz—, ni filtro de speckle polarimétrico.
No es simplificación: no se puede. El filtrado no se pierde, está adentro del
operador, en `useMeanMatrix` con ventana 5×5.

**El Terrain-Correction va siempre al final**, nunca antes de la polarimetría,
porque remuestrear destruye las relaciones de fase. Y en el grafo de la estepa el
recorte va después del Terrain-Correction.

**El Terrain-Flattening no cambia el RVI ni el RFDI** —el factor se cancela en el
cociente— pero sí cambia el Span, el BMI, el CSI y el VSI. Esos cuatro, en
ladera, mezclan pendiente con vegetación.

**Todos los grafos que producen un subset escriben BEAM-DIMAP**, no GeoTIFF. El
`.dim` más su carpeta `.data` es el producto principal porque conserva los
metadatos y permite seguir procesando en SNAP; el GeoTIFF es una copia para QGIS
que los pierde. La única excepción del proyecto es NISAR, que se recorta con h5py
y GDAL porque **SNAP todavía no tiene lector de NISAR**: el soporte se corrió de
SNAP 13 al roadmap «futuro». Esa excepción está justificada y el `.h5` original
queda intacto.

Otras dos decisiones que conviene conocer: `saveLayoverShadowMask` está en `true`
en los diez grafos que geocodifican y en sus gemelos `_cli`, de modo que la
máscara de sombra y layover sale del propio procesamiento y no de una
aproximación por ángulo de incidencia; y `grSquarePixel` está declarado
explícitamente en los cuatro grafos con Multilook, para que el comportamiento no
dependa de un valor por omisión no registrado.

## La banda RVI de SNAP no sirve

Corriendo `graph_saocom_quad_indices.xml` sobre la escena SAOCOM S6 del
16/01/2024, el grafo entero funciona y casi todo sale bien, pero
`Polarimetric-Parameters` escribe una banda `RVI` que **no es el RVI**:

    banda RVI del producto ... mediana 0,00219   (p1 0,0001 · máx 0,179)
    RVI recalculado ......... mediana 1,265     (p5 0,458 · p95 2,172)

El factor no es constante —entre 106× y 6.888× según el píxel—, y sobre todo la
**correlación entre esa banda y el RVI verdadero es 0,108**, medida píxel a píxel
sobre 7.034.926 píxeles. Correlaciona más con el Span (0,39) que con el RVI. No es
una definición alternativa del índice: una definición alternativa correlacionaría
fuerte.

**El RVI se calcula con Band Maths:**

    8 * HHVVRatio / (HHHVRatio * HHVVRatio + HHHVRatio + 2 * HHVVRatio)

Sale de sustituir HH = 1, HV = 1/HHHVRatio y VV = 1/HHVVRatio en la fórmula del
Handbook, 8·HV/(HH+VV+2·HV), y multiplicar arriba y abajo por
HHHVRatio·HHVVRatio. Las razones que entrega SNAP son **lineales, no en dB**: van
de 0,033 a 5.866 y son estrictamente positivas. El resultado da mediana 1,265,
p5 0,458 y p95 2,172, valores creíbles para bosque en banda L.

Conviene que el alumno escriba él la expresión. Es donde se ve de dónde sale el
índice, y de paso aprende algo que no está en ningún manual: **un operador de SNAP
puede entregar una banda con el nombre correcto y el contenido equivocado**, y la
única defensa es recalcular y comparar.

El control de que el recálculo vale: el RFDI del producto (0,311) y el recalculado
desde las mismas razones (0,394) coinciden en rango. Falla el índice, no la cadena.

Las demás bandas quedaron bien: RFDI 0,311 · CSI 0,495 · VSI 0,336 · BMI 0,285 ·
altura de pedestal 0,194 · Span 0,609. Y la geometría también: el producto contiene
el recinto BOSQUE_NW_02 con 7,7 a 8,6 km de margen, y la banda `elevation` va de
535 a 2.138 m con mediana 1.107, que es Los Alerces. Conviene además fijar
**no-data = 0**: el 28,6 % de ceros es el rectángulo que sobra fuera de la franja
rotada y ensucia histogramas y estadísticas zonales.

## El alcance de estos grafos, en orden de importancia

**1. No hay grafo polarimétrico para ALOS-1.**
Las escenas quad-pol de ALOS-1 no tienen cadena a C3/T3 ni a descomposiciones. La
estructura sería la de `graph_saocom_quad_polarimetria.xml`. El procedimiento
completo sobre la imagen entera, hecho en la interfaz de SNAP, está en
`02_Practica\10_Procedimientos_y_resultados\TP4_ALOS_PALSAR1_SLC`.

**2. No hay grafo para ALOS-1 PALSAR nivel 1.1.**
Las escenas (2007–2009, quad-pol) están descargadas en el disco del curso, sin
cadena de procesamiento por grafo.

**3. Los cuatro grafos quad-pol son plantillas.**
`graph_saocom_quad_indices.xml`, `graph_saocom_quad_polarimetria.xml` y los dos
del TNA no se corrieron sobre todos los productos del proyecto. Antes de usarlos
en serie, pruebe cada uno sobre **una** escena.

**4. `graph_saocom_tc.xml` no lleva `Apply-Orbit-File`.**
Los de Sentinel-1 sí. SNAP no distribuye órbitas precisas de SAOCOM, y el grafo
no lo anota.

**5. Landsat 8/9 se procesa con GDAL, no con SNAP.**
No es un error —el producto ya viene ortorrectificado— pero rompe la simetría con
el resto y explica por qué esos subsets no tienen `.dim`.

**6. `graph_saocom_quad_polarimetria_conTF.xml` es una reconstrucción**, no el
archivo con el que se produjo su resultado, que no se había guardado. El
resultado sí existe: `05_Resultados\SAOCOM_16ene2024_freeman_conTF.dim`. Sirve
como control congelado del experimento del Terrain Flattening.

## Y una aclaración de método que conviene tener presente

Los índices RVI y RFDI son cocientes de **intensidad** γ⁰ y no necesitan fase:
salen de los productos geocodificados. En cambio la matriz de covarianza, las
descomposiciones y el DpRVI necesitan los productos **con fase**, es decir los
SLC de `02_Subsets_SNAP_QGIS/00_Recortes_crudos_fase/`, que no viajan en el
repositorio porque sus archivos superan los 100 MB que admite GitHub: los produce
`TP4_02_recortar_crudo.py` desde la escena original, y en el aula están en el
disco del curso. Son dos niveles distintos y no conviene confundirlos.
