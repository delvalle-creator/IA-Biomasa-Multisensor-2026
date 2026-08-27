# Biomasa forestal por teledetección en el bosque andino chubutense

Presentación única concebida en cuatro archivos con numeración corrida de
láminas. **En el curso están solo las secciones 3 y 4**, con sus PDF de dos por
hoja en `01_Teoria\01_Presentaciones_pdf\Biomasa_Chubut\`. Los archivos 01 y 02
(láminas 1 a 99) no se incorporaron al curso, y sus temas —qué mide GEDI y su
cadena de descarga, filtrado y análisis— se cubren con `03_GEDI.pptx` de la
teoría (79 láminas).

| Archivo | Sección | Láminas | Tamaño |
|---|---|---|---|
| `03_Sinergia_multisensor.pptx` | 3 · Landsat 9, Sentinel-2, Sentinel-1, SAOCOM, NISAR y ALOS PALSAR | 100 a 155 | 6,7 MB |
| `04_BIOMASS_banda_P.pptx` | 4 · BIOMASS, el radar de banda P | 156 a 178 | 3,8 MB |

La numeración arranca en 100 porque conserva la de la presentación fusionada
original, cuyas dos primeras secciones quedaron fuera del curso.

## Qué se agregó

**Cinco láminas nuevas en la Sección 3**, escritas sobre copias exactas de láminas
del propio autor, de modo que conservan su diseño:

- **Landsat 9** (lámina 103): la cadencia de ocho días junto a Landsat 8, los 14
  bits del OLI-2, la Colección 2 Nivel 2 y las tres fechas que hay descargadas en
  el curso.
- **NISAR** (lámina 122): la misión conjunta de la NASA y la ISRO, banda L y S,
  el producto GCOV que llega ya geocodificado, y las tres fechas útiles de nueve
  que hay en el curso. Es la única fuente de banda L que no exige pedido previo.
- **NISAR frente a SAOCOM y PALSAR-2** (lámina 123): en qué estado llega cada uno
  y qué exige cada uno, más lo medido en el TP4: la polarización cruzada de NISAR
  es la que mejor sigue la altura del dosel, con R² de 0,18 a 30 m y 0,28 a 150 m.
- **ALOS-1 PALSAR** (lámina 124): la serie histórica de banda L, 2006-2011, el
  único cuadripolar completo del archivo, y las cinco fechas de 2007 a 2009 que
  hay en el proyecto.
- **ALOS-2 PALSAR-2** (lámina 125): el mosaico anual global de 25 m, qué conserva
  cada producto y los tres años que entran en el curso.

Los datos que afirman esas cinco láminas salen de la ficha de cada sensor y de la
matriz de datos del propio proyecto,
`02_Practica/TP1_Busqueda_IA/05_Resultados/04_Tablas/matriz_datos.csv`, que es la
que dice qué se descargó de verdad.

**La Sección 4 entera** es la presentación de BIOMASS, que entra como sección
aparte porque es la única misión que atraviesa el dosel completo y porque su
cadena de proceso es otra.

## Qué se cambió de forma

Se aplicaron las consignas del 6 de agosto de 2026:

- Arial en todo; título 26, bajada 20, texto 18.
- Justificado siempre e interlineado 1,5; línea única sólo donde 1,5 no entra.
- La viñeta es la tilde: los guiones que abrían cada renglón pasaron a ser
  viñetas de verdad.
- Los pies de fuente, que estaban en 6,5 pt y no se leían proyectados, subieron a 9.
- Las tablas y los rótulos de los esquemas subieron todo lo que su caja permite.

**Los bloques de órdenes van sobre fondo negro**, en Arial, con el cuerpo elegido
lámina por lámina: se toma el mayor de 14, 13, 12, 11 o 10 pt con el que ninguna
línea se corte ni se parta. El código no se justifica ni se abre a 1,5, porque una
orden se lee de corrido. Son seis bloques, todos en la Sección 2.

Nota: en la presentación de los prácticos esos mismos bloques están en Consolas,
que es monoespaciada y alinea las columnas del código. Aquí se usó Arial porque
así se pidió. Si prefiere unificar el criterio en las dos presentaciones, se
cambia en una pasada.

## Los diagramas de flujo

Las cadenas de pasos del panel derecho estaban tendidas en horizontal, en cajas
de una pulgada de ancho: a 18 pt las palabras se partían por la mitad
—«Correcci / ones», «Wavefor / m»— y lo que unía un paso con el siguiente era
una figura de altura cero, que se dibuja como una mota y no como una flecha.

Ahora la cadena **baja en vertical**, que es como se lee un flujo. Cada paso
ocupa el ancho entero del panel, lleva su número en un círculo verde y su rótulo
en una sola línea, y entre paso y paso hay una flecha de verdad. En la
presentación fusionada completa eran 58 diagramas (12 en la Sección 1, 22 en la
2 y 24 en la 3); en el curso están los 24 de la Sección 3.

En la Sección 4 las cadenas ya estaban bien armadas, en horizontal y con sitio
suficiente; lo único que se cambió fueron los quince conectores, que eran
segmentos sin punta y ahora son flechas.

## Qué conviene revisar

- Las cinco láminas nuevas: son mías, y aunque los datos salen del proyecto y de
  las fichas de los sensores, conviene que las lea antes de darlas por buenas.
- La Sección 4 mantiene su diseño propio; sólo se le igualaron el color del
  título, la marca de sección y la numeración para que combine con las otras tres.
