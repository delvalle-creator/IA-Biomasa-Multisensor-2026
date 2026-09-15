# Anexo del TP4 — NISAR posterior al incendio y fusión de órbitas

## El problema que este anexo cierra

El cuerpo del práctico deja planteado un límite del radar y no lo resuelve: la
geometría lateral. El sensor no mira hacia abajo, mira de costado, y en un valle
cordillerano eso produce tres defectos.

En el **layover**, la ladera que enfrenta al sensor devuelve su eco antes que el
fondo del valle y se dibuja volcada sobre él. En la **sombra**, la ladera opuesta
queda detrás del relieve y no recibe señal: el píxel no está oscuro, está vacío.
En el **acortamiento**, la pendiente que mira al sensor se comprime en menos
píxeles de los que le corresponden.

La vía para atacarlos es mirar el mismo terreno desde las dos geometrías. Ahora
bien, conviene anticipar el resultado, porque no es el que uno esperaría: en
estos productos la segunda órbita casi no agrega cobertura, y sin embargo revela
algo más importante.

## Las dos escenas

NISAR recorre la misma zona en dos sentidos. En la órbita **ascendente** el
satélite sube de sur a norte y mira hacia el este; en la **descendente** baja de
norte a sur y mira hacia el oeste. Sobre la ventana de Esquel el práctico
dispone de un par:

| Fecha | Traza | Marco | Órbita |
|---|---|---|---|
| 24/08/2026 | 169 | 4005 | descendente |
| 25/08/2026 | 003 | 4005 | ascendente |

Son las mismas trazas y el mismo marco que tres de las escenas anteriores al
incendio, de modo que cada comparación se hace sin cambiar de geometría:

| Órbita | Antes | Después |
|---|---|---|
| Ascendente | 04/12/2025 y 28/12/2025 | 25/08/2026 |
| Descendente | 08/01/2026 | 24/08/2026 |

La descendente anterior, del 8 de enero, es del día previo a la primera escena
óptica con humo. Es el estado inmediatamente anterior al fuego visto con la misma
geometría que la escena de agosto.

**Una advertencia sobre la fecha.** El 24 y el 25 de agosto es pleno invierno y
son siete meses posteriores al incendio. Como escena *después* para medir el
cambio producido por el fuego no son comparables con la Sentinel-1 del 27 de
febrero ni con la Sentinel-2 del 5 de marzo: entre medio hubo rebrote, nieve y
cambios de humedad del suelo, y el radar los ve todos. Para el problema
geométrico, que es a lo que se las usa en este anexo, la fecha no interviene: el
relieve no cambió.

## Cómo se generan los productos

Las escenas están en la carpeta común de originales:

```
02_Practica\00_COMUN\08_Originales_crudos\03_post\NISAR\GCOV\
```

Y el programa se corre desde el Miniforge Prompt:

```
conda activate aoi
cd C:\Temp\CURSO_BIOMASA_2026\02_Practica
python TP4_Radar_SAR\03_Scripts\01_Pre_procesamiento\TP4_03c_nisar_post_y_fusion.py
```

Recorta las dos escenas a la grilla común del proyecto —1500 × 1500 píxeles de
10 metros, EPSG:32719— y escribe, en cada recinto, los dos recortes y la fusión,
en GeoTIFF para QGIS y en BEAM-DIMAP para SNAP.

Conviene detenerse en un punto: aquí no hace falta el operador *Collocate* de
SNAP. Las dos escenas se recortan a la misma grilla, con los bordes de píxel
coincidentes, así que quedan superpuestas celda a celda sin remuestrear nada. El
grafo `Fusion_ASC_DES_NISAR.xml` de la carpeta `08_Grafos_SNAP` hace lo mismo
dentro de SNAP, con *Collocate* por vecino más cercano, y sirve para repetir el
ejercicio con la interfaz a la vista.

## Qué hay en la fusión

El producto `NISAR_FUSION_ASC_DES_202608` lleva seis capas.

| Capa | Qué es |
|---|---|
| `HV_asc_db` | HV de la órbita ascendente, en decibeles |
| `HV_des_db` | HV de la órbita descendente |
| `HV_fusion_db` | promedio de las dos, hecho en potencia lineal |
| `HH_fusion_db` | lo mismo en HH |
| `HV_asc_menos_des_db` | la diferencia entre geometrías |
| `RVI_dual` | índice de vegetación radar, 4·HV / (HH + HV) |

El promedio se hace **en potencia lineal y recién después se pasa a decibeles**.
Promediar decibeles sería promediar logaritmos, que da un valor sin significado
físico. Donde una sola de las dos órbitas tiene dato, la fusión usa esa.

## Lo que la fusión aporta, medido

Hay que separar dos cosas que suelen confundirse.

**La cobertura casi no mejora.** Un producto GCOV llega con la corrección
radiométrica de terreno ya aplicada, y la máscara de la misión deja muy pocos
huecos. Sobre el recinto de bosque, la ascendente tiene dato en el 99,97 % de las
celdas y la descendente también; la fusión agrega **574 celdas de 2.250.000**, el
0,03 %. Sobre la estepa agrega tres. Quien esperara ver aparecer laderas enteras
que una órbita no medía, no las va a ver aquí.

**El sesgo geométrico, en cambio, es grande.** Es la otra pregunta: no cuántas
celdas tienen dato, sino cuánto cambia el valor medido según desde dónde se mire.
La capa `HV_asc_menos_des_db` la responde, pero no puede leerse píxel a píxel,
porque a esa escala la domina el moteado. El procedimiento consiste en promediar
esa diferencia en ventanas cada vez más grandes: el moteado se promedia y baja
con la raíz del número de celdas, y lo que no baja así es estructura.

Sobre el recinto de bosque, con 4,8 vistas por celda:

| Ventana | Mediana | Desviación típica | Si fuera sólo moteado |
|---|---|---|---|
| 10 m | 0,36 dB | 3,40 dB | 3,40 dB |
| 30 m | 0,35 dB | 1,87 dB | 1,13 dB |
| 100 m | 0,31 dB | 1,08 dB | 0,34 dB |
| 300 m | 0,27 dB | 0,72 dB | 0,11 dB |

A diez metros la diferencia es casi todo moteado: los 3,40 decibeles medidos son
del orden de los 2,79 que predice la estadística para 4,8 vistas. Pero a
trescientos metros, donde el moteado ya debería haber caído a 0,11, todavía
quedan **0,72 decibeles**. Eso ya no es ruido. El 17,2 % de esas celdas de 300
metros se aparta más de un decibel, y las hay de hasta 5,7. En la estepa la
proporción sube al 35,2 %.

**Y el sesgo cambia de signo entre los dos recintos.** En el bosque la órbita
ascendente mide 0,36 decibeles por encima de la descendente; en la estepa, la
descendente mide 0,79 por encima de la ascendente. Un mismo sensor, dos días
seguidos, sobre dos sitios vecinos: lo único que cambió fue desde dónde se miró.

## De dónde viene esa diferencia: el relieve

Que sea geometría y no otra cosa se comprueba cruzando la diferencia con el
terreno. **Crece con la pendiente**, que es lo que debe ocurrir si la origina la
inclinación de la superficie respecto del haz:

| Pendiente | Bosque, mediana de \|asc − des\| | Percentil 90 | Estepa, mediana |
|---|---|---|---|
| 0 a 5° | 2,06 dB | 5,05 dB | 1,95 dB |
| 5 a 10° | 2,13 dB | 5,23 dB | 2,02 dB |
| 10 a 20° | 2,25 dB | 5,56 dB | 2,20 dB |
| 20 a 30° | 2,49 dB | 6,17 dB | 2,32 dB |
| más de 30° | 3,19 dB | 8,55 dB | 2,34 dB |

Y **cambia de signo según hacia dónde mira la ladera**. En el bosque, sobre
pendientes de más de quince grados:

| La ladera mira al | asc − des |
|---|---|
| oeste | +1,54 dB |
| norte | +0,58 dB |
| sur | +0,24 dB |
| este | −0,75 dB |

Las laderas orientadas al oeste las mide más alto la órbita ascendente; las
orientadas al este, la descendente. Es decir: cada órbita lee mejor la ladera que
le da la cara, y la que queda de espaldas la subestima. En la estepa el patrón es
el mismo una vez descontado su sesgo general de −0,79 decibeles: el oeste es el
sector menos negativo (+0,45) y el este el más negativo (−1,89).

## Lo que la combinación sí mejora, y lo que no

Con eso en la mano se entiende qué se gana al combinar las dos órbitas.

**Se lee mejor el relieve abrupto.** Cada ladera queda representada por la órbita
que la ve de frente en lugar de por la que la ve de canto, y el promedio deja el
valor a mitad de camino en vez de exagerado hacia un lado. Sobre laderas de más
de treinta grados, donde las dos órbitas discrepan hasta 8,55 decibeles, esa
diferencia es la que separa una imagen interpretable de una que no lo es.

**Y baja el moteado**, porque son dos adquisiciones independientes:

| Capa | Bosque | Estepa |
|---|---|---|
| HV ascendente | 2,26 dB | 2,09 dB |
| HV descendente | 2,28 dB | 2,01 dB |
| HV de la fusión | **1,72 dB** | **1,52 dB** |

La razón medida es 0,76 y 0,73, contra el 0,71 que predice promediar dos escenas
independientes. Coincide.

**Pero los tres defectos no desaparecen.** Conviene decirlo sin rodeos, porque es
donde la fusión se suele sobrevender. Donde hubo layover, dos ecos de puntos
distintos del terreno llegaron sumados en una misma celda, y ninguna media separa
lo que ya se mezcló. Donde hubo sombra, la otra órbita rellena sólo si mira desde
el lado correcto, y en estos productos eso apenas ocurrió: 574 celdas de dos
millones y medio. El acortamiento sigue comprimiendo la ladera en menos celdas de
las que le tocan. Y la prueba de que el problema persiste está en la propia tabla
de arriba: si el promedio lo corrigiera, la diferencia residual a trescientos
metros no seguiría creciendo con la pendiente.

La combinación **mejora la visualización y atenúa el sesgo; no corrige la
geometría**. Para eso hace falta la máscara de validez del quinto programa, que
no arregla nada pero dice dónde no hay que medir.

## Preguntas de discusión

1. La fusión agrega 574 celdas sobre 2.250.000 en el bosque y tres en la estepa.
   ¿Por qué aporta tan poca cobertura? ¿Qué tiene el producto GCOV que no tiene
   un producto de nivel 1 sin corregir?

2. A diez metros la diferencia entre órbitas tiene una desviación típica de 3,40
   decibeles y a trescientos metros conserva 0,72. Explique por qué la primera
   cifra no dice nada sobre la geometría y la segunda sí.

3. El sesgo entre órbitas es positivo en el bosque y negativo en la estepa.
   Proponga una explicación a partir del relieve de cada recinto y de la
   dirección de observación de cada órbita.

4. ¿Qué le ocurriría al análisis de cambio del práctico si se comparara una
   escena ascendente anterior al incendio con una descendente posterior? Estime
   el error a partir de las cifras de la tabla.

5. El RVI de la fusión se calcula sobre el promedio de las dos órbitas. ¿Qué
   ventaja tiene sobre el RVI de una sola? ¿Y qué se pierde al promediar?

6. Estas escenas son de agosto y el incendio fue en enero. Enumere qué
   conclusiones puede sostener con ellas y cuáles no.

## La herramienta de lectura

SNAP 14 no trae lector de GCOV, y el driver HDF5 de GDAL lee los valores pero no
la georreferencia, porque NISAR la guarda en dos arreglos aparte en lugar de un
geotransform.

El complemento **NISAR GCOV Reader**, de autoría de H. F. del Valle, resuelve esa
lectura: abre el producto en QGIS, reconstruye la georreferencia y lo exporta
como GeoTIFF o como BEAM-DIMAP para SNAP. Está en la carpeta `09_Herramientas`
de este práctico, con sus instrucciones de instalación y uso.

El programa del anexo no lo necesita, porque lee el HDF5 y recorta por ventana
igual que el resto de los programas del práctico. El complemento es la
herramienta para trabajar la **escena completa**: inspeccionarla, llevarla a
QGIS, o convertirla entera para procesarla en SNAP.
