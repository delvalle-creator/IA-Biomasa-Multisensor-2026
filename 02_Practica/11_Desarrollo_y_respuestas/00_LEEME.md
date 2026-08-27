# Guía de desarrollo de los prácticos — aquí quedan las respuestas

Esta carpeta contiene el **desarrollo completo de los cinco trabajos
prácticos, ejecutado tal como se propone en las guías**, con los datos a la
vista: lo que imprime cada script, las tablas que produce, las figuras del
procesamiento del bosque y de la estepa, y las **respuestas modelo** a las
preguntas de cada práctico, fundamentadas con esas cifras.

## Para qué sirve y para qué no

Sirve para **verificar**. Cuando usted corra un paso y dude de si el número
que obtuvo es razonable, aquí está el número que produce la misma corrida
sobre los mismos datos. Sirve también para **destrabarse**: si un paso falla
o un resultado lo desconcierta, el desarrollo muestra qué debía aparecer y
de qué archivo sale.

No sirve como sustituto del trabajo. Las respuestas a las preguntas están
redactadas aquí porque el curso entrega su propia resolución completa, pero
**el aprendizaje está en llegar a ellas con sus propias corridas**. La
recomendación es firme: ejecute primero, responda primero, y recién después
contraste con esta carpeta.

## Cómo está organizada

Una subcarpeta por práctico, con el mismo nombre que la carpeta del práctico:

| Carpeta | Contenido |
|---|---|
| `TP1_Busqueda_IA\` | `DESARROLLO.md` + `capturas\` |
| `TP2_LiDAR_GEDI_ICESat2\` | `DESARROLLO.md` + `ORANGE_resultados.md` + `capturas\` |
| `TP3_Datos_Opticos\` | `DESARROLLO.md` + `capturas\` |
| `TP4_Radar_SAR\` | `DESARROLLO.md` + `capturas\` (incluye las galerías de radar y los grafos de SNAP) |
| `TP5_Sinergia_Multisensor\` | `DESARROLLO.md` + `ORANGE_resultados.md` + `capturas\` |

Los `ORANGE_resultados.md` muestran, con las cifras y figuras reales, lo
que debe verse al abrir cada flujo de `09_Orange\` (TP2 y TP5).

Cada `DESARROLLO.md` sigue la misma estructura: la ejecución paso a paso con
las salidas reales, los resultados con los datos expuestos, las figuras del
procesamiento de los dos sitios, y las respuestas modelo con la fuente de
cada cifra.

## De dónde salen estas cifras

De **correr los scripts del curso, en su orden declarado, sobre los datos
del curso**. Los números citados coinciden con los archivos que quedan en
`05_Resultados\` de cada práctico y con los registros de
`05_Resultados\06_Control_calidad\` del TP2 (los logs de las cadenas
completas). Si usted repite la corrida sobre los mismos datos, debe obtener
estos mismos valores; una diferencia pequeña de redondeo en la última cifra
decimal es normal entre versiones de las bibliotecas, una diferencia mayor
no lo es y merece revisarse.

## Si usa estos mismos scripts y procedimientos EN OTRO SITIO

Los scripts están hechos para viajar: no hay que reescribirlos, hay que
cambiar la **configuración** y rehacer los **datos del lugar**. La guía
completa está en `00_COMUN\COMO_CAMBIAR_DE_AREA.md` — qué editar en
`configuracion_comun.py` (y sus seis copias), qué rehacer (AOI, coberturas,
FABDEM, geoides), y qué revisar a mano (GEDI sólo existe entre ±51,6° de
latitud; la órbita y el track se eligen de nuevo; los estratos del L4A y
los mapas provinciales son de esta región).

Pero la aclaración más importante es sobre ESTA carpeta: **las respuestas
de aquí no viajan con los scripts.** La supervivencia del filtrado (11,0 %
y 27,5 %), el punto de saturación del NDVI, la razón ATLAS/GEDI, las
18.009,2 ha quemadas, el piso del ensayo nulo — todos son resultados de
ESTE paisaje y de ESTE incendio. En otro sitio, el procedimiento es el
mismo y los números serán otros: habrá que medirlos de nuevo, declararlos
de nuevo y defenderlos de nuevo. Quien use esta carpeta como plantilla de
respuestas en otra región no está repitiendo el curso: está salteándoselo.

## La regla que atraviesa todo el curso

Ninguna cifra de biomasa de este proyecto es una **medición**: no hay
parcelas de campo, y la propia referencia (GEDI) es la estimación de un
modelo. Todas las respuestas modelo respetan esa regla — informan el error
junto al valor, el piso del ensayo nulo junto al cambio, y presentan las
conclusiones como estimaciones. Ese hábito es el producto principal del
curso.
