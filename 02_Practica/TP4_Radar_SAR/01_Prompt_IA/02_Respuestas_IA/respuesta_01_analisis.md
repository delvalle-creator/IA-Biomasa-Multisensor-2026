# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un grafo de SNAP correcto: `Calibration` con `outputSigmaBand=true`, luego
`Terrain-Correction`, luego el ajuste. Todo estándar, todo documentado, todo mal
para este terreno.

## Lo que había que detectar

**`outputSigmaBand=true` en vez de `outputBetaBand=true` + `Terrain-Flattening`.**
Un parámetro. El grafo corre igual y produce un raster que abre y se ve bien. La
diferencia es que en relieve fuerte σ⁰ mide topografía disfrazada de vegetación.

**Usaba el `localIncidenceAngle` para dividir otra vez.** Es información de
diagnóstico, para ver dónde el terreno es problemático. No es una corrección. Si
se aplica después del terrain flattening, se corrige dos veces lo mismo.

**Ajustaba en dB.** El promedio de los logaritmos no es el logaritmo del promedio.
Filtrar o promediar en dB introduce un sesgo negativo sistemático que crece con la
varianza del speckle. Se trabaja en γ⁰ lineal y se pasa a dB al final.

## Cómo se detectó

**Mirando el mapa, no el código.** Con σ⁰, las laderas que enfrentan al satélite
salían brillantes y las opuestas oscuras, con el patrón exacto del relieve. Eso no
es un bosque: es una montaña.

## La regla

Cuando el resultado tiene la forma del terreno, está midiendo el terreno.
