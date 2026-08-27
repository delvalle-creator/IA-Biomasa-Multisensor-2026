# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un script correcto, comentado, que hacía exactamente lo pedido: consultar,
ordenar por nubosidad y descargar. Sin errores de sintaxis ni de ejecución.

## Lo que había que detectar, y no se ve leyendo el código

**Ordenaba por `eo:cloud_cover`, que es un metadato de la escena entera.** El
código es correcto; el criterio es inadecuado. Ningún linter marca eso.

**No contaba píxeles válidos.** Descargaba, recortaba, y el recorte podía salir
vacío. El script no fallaba: el archivo se creaba, abría, y estaba lleno de ceros.

**No cruzaba sensores.** Con un solo sensor no hay forma de detectar un problema
del sensor. Hace falta un segundo, independiente, que tenga que coincidir.

## Cómo se detectaron

**Contando.** No leyendo. Se leyó una ventana del AOI de cada producto —sin bajar
la escena entera, aprovechando el formato COG— y se contaron los píxeles con dato.
Ahí apareció el 15 % de cobertura real donde el catálogo prometía 76 %.

**Y comparando.** La escena Sentinel-2 del 09/01/2026 tenía 0,4 % de nubes según
la SCL y pasó todos los filtros. Recién al calcular índices se vio que el NDVI del
bosque daba 0,34 cuando en todas las demás fechas daba 0,80. Landsat 9, del 4 de
enero, daba 0,78 en ese mismo bosque. **Dos sensores independientes en desacuerdo:
ahí había algo.** Era bruma: la banda azul valía 0,158 contra los 0,024 habituales.
La máscara del producto no la vio, porque está entrenada para nubes opacas y la
bruma es un velo semitransparente.

## La regla

Un solo sensor no puede delatarse a sí mismo. Cuando dos sensores independientes
coinciden, se les puede creer a los dos; cuando discrepan, hay que ir a mirar.
