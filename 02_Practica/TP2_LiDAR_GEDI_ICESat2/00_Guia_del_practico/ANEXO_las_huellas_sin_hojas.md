# Anexo — Por qué aceptamos las huellas tomadas con el bosque sin hojas

*Nota metodológica. Se puede leer sin saber nada de teledetección.*

## 1. El problema, en una frase

De cada diez mediciones de biomasa que el satélite GEDI hizo sobre nuestro bosque,
la NASA nos deja usar solamente cuatro. Este anexo explica por qué descarta las
otras seis, por qué en **nuestro** bosque en particular ese descarte es
desproporcionado, y por qué decidimos recuperar una parte de ellas.

## 2. Qué es una huella de GEDI

GEDI es un instrumento láser que viaja en la Estación Espacial Internacional.
Dispara pulsos de luz hacia el suelo y mide cuánto tarda cada eco en volver. Como
la copa de un árbol devuelve el eco antes que el suelo, la forma completa del eco
dibuja el perfil vertical de la vegetación: dónde empieza el dosel, qué tan denso
es, dónde está el terreno.

Cada disparo ilumina un círculo de **25 metros de diámetro** en el suelo. A ese
círculo lo llamamos *huella*. En nuestro recinto de bosque de 15 × 15 km cayeron
690 huellas útiles.

A partir de la forma del eco, la NASA estima la **biomasa aérea** de ese círculo:
cuántas toneladas de materia vegetal viva hay por hectárea. Ése es el dato que
todo el curso usa como referencia.

## 3. Qué es "hoja caída" y por qué la NASA descarta esas huellas

Un árbol sin hojas devuelve un eco distinto del mismo árbol con hojas. Las ramas
desnudas dejan pasar mucha más luz, así que el eco es más débil y más "hueco". Un
modelo entrenado con árboles con follaje, aplicado a un árbol pelado, puede
equivocarse.

Por eso la NASA marca cada disparo con una bandera, `leaf_off_flag`, y **descarta
todos los que fueron tomados fuera de la temporada de follaje**. Es una decisión
prudente y, en general, correcta.

## 4. Por qué acá esa decisión sale carísima

La regla de la NASA es global. Pensada para el planeta entero, donde la mayor
parte del bosque monitoreado es perenne, descartar la temporada sin hojas cuesta
poco.

Nuestro bosque es exactamente el caso contrario. La **lenga** (*Nothofagus
pumilio*) y el **ñire** (*Nothofagus antarctica*) son **caducifolios**: pierden
la hoja todos los años. Y las órbitas de GEDI no eligen la fecha: pasan cuando
pasan.

El resultado, medido sobre nuestros datos:

- De las 419 huellas que la NASA descarta en el recinto de bosque, **224 —más de
  la mitad— se descartan únicamente por la hoja caída.**
- De las 162 huellas que cayeron sobre lenga, **93 se tomaron sin hojas** (33 con
  hoja presente y 36 sin bandera, por no tener biomasa del L4A).
- De las 220 huellas del gránulo del 06/11/2024, **170 son de hoja caída**: la lenga
  todavía no había brotado.

Traducido: la regla nos estaba dejando la clase más importante del recinto —la
lenga, que ocupa el 33 % de la superficie— sostenida por apenas **33 mediciones**.

## 5. La pregunta correcta

La pregunta no es "¿la NASA tiene razón en general?". Casi seguro que sí. La
pregunta es concreta y verificable:

> En **nuestro** bosque, ¿la falta de hojas cambia el valor de biomasa que el
> modelo calcula?

Si lo cambia, hay que descartarlas. Si no lo cambia, descartarlas sólo nos hace
perder precisión sin ganar nada.

## 6. Cómo se comprobó, y la trampa que casi nos engaña

El primer intento fue el obvio: comparar el promedio de biomasa de las huellas
aceptadas contra el de las huellas con hoja caída. El resultado parecía
concluyente — las de hoja caída daban mucho menos. Caso cerrado, descartarlas.

**Ese razonamiento estaba mal**, y vale la pena entender por qué, porque es un
error que aparece en todas partes.

La NASA no tiene un solo modelo de biomasa: tiene varios, uno por tipo de
vegetación. A cada huella le aplica el que le corresponde según un mapa mundial
de tipos de vegetación. Y resulta que **las 224 huellas de hoja caída recibieron
todas el mismo modelo**, el de latifoliada caducifolia, mientras que las
aceptadas son una mezcla de tres modelos distintos, uno de los cuales devuelve
valores mucho más altos.

Es la misma trampa que comparar los promedios de dos brigadas que inventariaron
el mismo bosque: si una levantó sobre todo parcelas de lenga y la otra parcelas
de ñire, la diferencia entre sus resultados no mide los métodos, sino qué parte
del bosque recorrió cada una.

La comparación legítima es **dentro del mismo modelo**. Y ahí la respuesta se da
vuelta por completo:

| Cobertura (mismo modelo, DBT_SA) | Con hojas | Sin hojas |
|---|---|---|
| Lenga | 91,33 Mg/ha | 88,82 Mg/ha |
| Ñire | 2,66 Mg/ha | 3,95 Mg/ha |
| Ñire bajo | 0,06 Mg/ha | 0,65 Mg/ha |

**A igual modelo, la hoja caída no deprime la biomasa.** La diferencia aparente
era, entera, un efecto de composición.

Un dato más, decisivo: la NASA **corrió su modelo igual** sobre esas 224 huellas
—hay una bandera, `algorithm_run_flag`, que lo confirma en las 224—. No es que no
pudiera calcularlas. Las calculó y decidió no certificarlas.

## 7. Qué decidimos, y qué efecto tuvo

Aceptamos las huellas de hoja caída, con tres condiciones:

1. Que pasen **el mismo umbral de calidad de señal** que las certificadas.
2. Que la NASA **haya corrido efectivamente su modelo** sobre ellas.
3. Que queden **marcadas** en una columna, `agbd_origen`, con el valor
   `hoja_caida`, para que cualquiera pueda rehacer todos los cálculos sin ellas y
   comprobar qué cambia.

No inventamos ninguna fórmula propia. Usamos el número que la NASA ya había
calculado.

El efecto:

| | Antes | Después |
|---|---|---|
| Huellas con biomasa (bosque) | 271 | **495** |
| Huellas de lenga | 33 | **126** |
| Biomasa media del recinto | 45,56 Mg/ha | 44,32 Mg/ha |
| Incertidumbre de esa media | ± 3,33 | **± 2,20** |

Lo importante no es que el número baje un 2,7 %: es que **casi no se mueve
mientras la muestra casi se duplica**. En la lenga, cuadruplicar las mediciones
corrió el promedio de 91,33 a 94,64 Mg/ha. Que agregar 93 mediciones nuevas mueva
el promedio un 3,6 % es la mejor prueba posible de que las 33 originales ya eran
representativas — y ahora, además, lo podemos afirmar con casi cuatro veces más
respaldo.

## 8. Lo que queda declarado, y lo que sigue abierto

Lo que este anexo **no** resuelve: a qué huellas la NASA les aplicó el modelo
correcto. El ñire es una latifoliada caducifolia, pero 57 de sus 68 huellas
aceptadas recibieron el modelo de **conífera perenne**, que devuelve unas ocho
veces más biomasa. Si ese modelo está mal aplicado —y botánicamente lo parece—,
el ñire está sobrestimado.

No podemos decidirlo con datos satelitales. Hace falta **medición en el terreno**:
parcelas de campo donde alguien haya pesado la vegetación. Mientras tanto, el
resultado se informa con el rango que abarca las dos hipótesis posibles, entre
**40,7 y 45,6 Mg/ha**, y se declara de dónde viene esa horquilla.

Ésa es, en el fondo, la lección del anexo: **un dato de satélite no es una
medición, es una estimación de un modelo**, y saber qué modelo se aplicó importa
tanto como el número que devuelve.
