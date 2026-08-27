# Qué contestó la IA, y qué había que mirarle

## La respuesta al prompt inicial

Un script de unas 40 líneas: `earthaccess.login()`, búsqueda por bounding box,
descarga, lectura de `rh95` con h5py, `numpy.mean()`. Limpio, comentado, correcto
en su sintaxis.

## Los cuatro problemas que había que detectar

**Usaba `quality_flag`, que en la versión V003 no existe.** GEDI renombró las
variables: ahora es `l2a_quality_flag_rel3`. El script no fallaba: `h5py` devuelve
`None` cuando la variable no está, y el filtro con `None` no filtra nada. Pasaban
todos los disparos. **Éste es el error más peligroso del práctico**, porque no da
error: da un resultado.

**Buscaba por bounding box y daba por buena la respuesta del catálogo.** El
catálogo devuelve todo lo que TOCA el rectángulo, no lo que lo cubre. Y la huella
del gránulo no dice dónde hay dato utilizable.

**Promediaba sin contar.** No informaba cuántos disparos entraban en el promedio.
Con 6.288 disparos o con 12, la salida se ve igual.

**No mencionaba la hibernación de GEDI.** El instrumento estuvo apagado entre
marzo de 2023 y abril de 2024. Si se piden datos de ese período, no hay, y el
script devolvía una lista vacía sin explicar por qué.

## Cómo se detectaron

No leyendo el código con más atención, sino **comparando contra algo
independiente**: al filtrar bien, quedaba el 12,3 % de los disparos. La primera
versión daba el 100 %. Esa diferencia era la señal.

La regla general: a una respuesta de IA no se la audita releyéndola. Se la audita
buscando una medida externa con la que tenga que coincidir.
