# Verificación de los resultados del TP5

El TP5 produce un mapa y una cifra. Las dos cosas son fáciles de producir y
difíciles de justificar. Aquí está cómo se verificaron.

---

## 1. El control revela cuánto aportó realmente la sinergia

Coeficiente de determinación sobre el conjunto de validación, altura de dosel, los
dos sitios juntos.

| Modelo | Lineal | Bosque aleatorio |
|---|---|---|
| Óptico | 0,464 | 0,605 |
| Radar | 0,346 | 0,601 |
| Óptico + radar | 0,437 | 0,635 |
| Óptico + radar + LiDAR | 0,832 | **0,964** |
| **Sólo LiDAR (control)** | 0,821 | **0,956** |

**Cómo se lee.** No por el número más alto, sino por la distancia entre las dos
últimas filas: 0,008. El salto de 0,635 a 0,964 no lo produjo la combinación de
sensores, lo produjo la entrada del LiDAR, que es la fuente de la variable
estimada. Lo que aportaron el óptico y el radar por encima del LiDAR solo es esa
diferencia de ocho milésimas.

Sobre biomasa el cuadro es el mismo: 0,899 el modelo completo contra 0,858 el
control.

**La regla, para prevenir:** cuando un predictor comparte origen con la variable
que se quiere estimar, hay que entrenar el modelo que usa **sólo** ese predictor.
Si iguala al completo, la sinergia es aparente.

## 2. El coeficiente global esconde el sesgo de los extremos

Sesgo por franja de altura en el recinto de bosque.

| Franja (m) | n | Sesgo (m) |
|---|---|---|
| 0 – 3 | 27 | **+3,93** |
| 3 – 6 | 48 | +2,82 |
| 6 – 9 | 10 | +1,14 |
| 9 – 12 | 5 | −1,80 |
| 12 – 15 | 10 | −3,66 |
| 15 – 18 | 5 | −6,15 |
| 18 – 21 | 5 | **−9,27** |

El modelo sobreestima sistemáticamente lo bajo y subestima sistemáticamente lo
alto. Es compresión hacia la media, le ocurre a toda regresión, y ataca justo los
extremos: el bosque maduro, que es donde está la biomasa, es donde más se
subestima.

**La regla:** un coeficiente global bueno no autoriza a usar el modelo en los
extremos. Hay que validar por estratos.

## 3. El ensayo nulo: cuánto "cambia" la biomasa donde no pasó nada

Aplicando el procedimiento completo sobre la clase «sin cambio» del recinto de
bosque —terreno que no se quemó—, el resultado debería ser cero. Dio **−10,25
Mg/ha**, es decir una ganancia aparente. Las clases quemadas cambian entre 11,5 y
15,5 Mg/ha. La señal apenas supera al ruido por un factor de 1,1 a 1,5.

**Qué se descartó midiendo.** La primera sospecha fue el desfase fenológico: la
escena anterior es de noviembre y la posterior de marzo, y lenga y ñire son
caducifolias. Es falso: sobre bosque no quemado el NDVI mediano da 0,8679 en
noviembre y 0,8654 en marzo, una diferencia de 0,0031. Ópticamente el dosel es el
mismo en las dos fechas.

**La segunda sospecha también era razonable y también era falsa.** Las escenas de
radar están separadas por siete semanas en las que la humedad del suelo pudo
cambiar. Se midió ajustando el mismo modelo con distintos juegos de predictores:

| Juego de predictores | Piso (Mg/ha) | Señal ÷ piso |
|---|---|---|
| Óptico (NDVI, EVI, NDMI, NBR) | −8,48 | 1,3 |
| Óptico + radar | −5,01 | 1,5 |
| Óptico sin EVI | −4,82 | 2,3 |
| **Óptico sin EVI + radar** | **−0,48** | **15,3** |

**El piso lo aportaba un solo índice óptico.** Quitarlo lleva el cociente entre
señal y ruido de 1,5 a 15,3, sin tocar el radar ni la alometría.

**La regla:** cuando un método arroja un piso de ruido grande, la salida honesta no
es restarlo sino identificarlo. Restar a ciegas mejora la cifra central, que es
exactamente la dirección que a uno le conviene.

## 4. La cadena de error, tramo por tramo

Incertidumbre en el recinto de bosque.

| Tramo | Aporte |
|---|---|
| Modelo de altura | 4,32 m |
| Conversión de altura a biomasa (alometría, exponente 2,605) | 13,58 Mg/ha |
| Producto de biomasa de referencia | 13,09 Mg/ha |

Los dos últimos tramos pesan cada uno unas tres veces más que el primero. Eso dice
dónde convendría invertir esfuerzo si se quisiera mejorar el mapa: no en un modelo
de altura más fino, sino en la alometría y en la referencia.

También explica por qué basta un metro de error en altura para generar todo el piso
del punto 3: con exponente 2,605, un error pequeño en la base se amplifica al
convertirlo en biomasa.

## 5. Cómo se nombra el resultado

El procedimiento mide **el cambio aparente de biomasa estimada entre dos fechas**,
dentro de cada clase de severidad. No mide biomasa perdida. Llamarla pérdida
supondría que todo el cambio se debe al fuego, que la estimación no tiene sesgo y
que las dos fechas son comparables — tres cosas que hay que demostrar por separado.

**La regla, y es la que cierra el curso:** el nombre de un resultado es parte del
resultado. Un nombre que afirma más de lo que se probó es un error, aunque el
número sea correcto.
