# Prompt corregido — el que produjo los scripts del práctico

Éste es el prompt reescrito después de detectar los defectos del primero. Es el
que generó los ocho scripts que usted va a ejecutar.

---

> Contexto: dos AOI de 15 × 15 km en el noroeste de Chubut, Argentina. Uno de
> bosque andino de *Nothofagus* (BOSQUE_NW_02) y uno de ecotono de estepa
> (ESTEPA_NW_02), que funciona como control. Grilla común EPSG:32719, píxel 10 m,
> 1500 × 1500. El bosque se incendió entre el 10/01 y el 27/02 de 2026.
>
> Necesito construir la referencia de estructura del bosque con GEDI, para
> calibrar después modelos ópticos y de radar.
>
> **Requisitos de calidad, no negociables:**
>
> 1. Usar la versión V003 y **verificar el nombre real de cada variable en el
>    archivo antes de usarla**. No asumir nombres: listar las claves del `.h5` y
>    fallar con un mensaje claro si alguna no está. GEDI renombró
>    `quality_flag` a `l2a_quality_flag_rel3`, y un filtro que no encuentra la
>    variable no filtra: pasa todo.
> 2. Aplicar y **declarar por separado** tres filtros: calidad
>    (`l2a_quality_flag_rel3`), órbita degradada (`degrade_flag`) y sensitivity.
>    Informar cuántos disparos descarta cada uno.
> 3. **No descartar los rechazados: guardarlos** con un campo `motivo` que diga
>    por qué. El descarte es parte de la evidencia.
> 4. Filtrar por pendiente con el DEM Copernicus GLO-30, umbral 20°, y explicar
>    el porqué: en una huella de 25 m sobre 30° de ladera hay 14 m de desnivel,
>    que el instrumento no distingue del dosel.
> 5. Reportar **medianas, no medias**, y siempre acompañadas del n.
> 6. Comparar los dos sitios en cada paso. Si la estepa tuviera dosel alto, algo
>    está mal y hay que detenerse.
> 7. GEDI estuvo hibernado de marzo 2023 a abril 2024. Declararlo como limitación
>    temporal, no ocultarlo.
> 8. Para la biomasa usar el producto oficial L4A. **No inventar una ecuación
>    alométrica**: los coeficientes son específicos del tipo de bosque y una
>    ecuación amazónica aplicada a *Nothofagus* da números plausibles y falsos.
>    Si el L4A no está, avisar y calibrar contra altura, diciéndolo.
> 9. **Exportar a GeoPackage con estilos**, para poder abrir las huellas en QGIS
>    y verificar en un mapa lo que los números afirman.
>
> Cada script debe imprimir qué hizo, cuántos datos entraron y cuántos salieron,
> y cuál es el siguiente paso.

---

## Qué cambió respecto del primero

| Prompt inicial | Prompt corregido |
|---|---|
| "dame la altura media" | medianas con n, y comparación entre sitios |
| no mencionaba calidad | tres filtros, declarados por separado |
| no mencionaba el terreno | filtro de pendiente con su justificación física |
| daba por buenos los nombres de variables | exige verificarlos y fallar si no están |
| descartaba en silencio | guarda los descartes con el motivo |
| resultado numérico | resultado + verificación en QGIS |

## La diferencia de fondo

El primer prompt pedía **un resultado**. El segundo pide **un resultado y la
evidencia de que es correcto**. Es la diferencia entre usar la IA como oráculo y
usarla como herramienta.

Fíjese que el prompt corregido es largo, específico y aburrido. Así son los
prompts que sirven. El conocimiento del dominio no lo pone el modelo: lo pone
usted, y se nota en el pedido.
