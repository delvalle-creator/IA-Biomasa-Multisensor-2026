# TP2 — ICESat-2 / ATLAS como segunda referencia

> **Qué es este archivo.** Notas técnicas de la rama ICESat-2 del práctico:
> qué aporta, qué no, y las trampas que ya están identificadas. La rama GEDI
> tiene las suyas en `NOTAS_TECNICAS.md`. El punto de entrada del práctico sigue
> siendo `00_LEEME.md`.

**Pregunta de esta rama:** GEDI es la referencia contra la que se calibra todo el
curso, y nadie la verificó desde el suelo. **¿Qué dice un segundo LiDAR espacial,
independiente, sobre lo mismo?**

## Por qué ATL08 y no otro

| | GEDI (L2A/L2B/L4A) | ICESat-2 (ATL08) |
|---|---|---|
| Unidad | huella de 25 m | segmento de 100 m sobre la traza |
| Principio | láser de onda completa | conteo de fotones |
| Período disponible aquí | sep. 2024 a mar. 2025 | nov. 2018 a abr. 2026 |
| Cobertura latitudinal | hasta 51,6° | hasta 88° |
| Entrega biomasa | sí, L4A | no |
| Aceptados en bosque | 1.025 huellas | 1.949 segmentos operacionales |
| Aceptados en estepa | 4.041 huellas | 1.923 segmentos operacionales |

Lo que aporta ATL08 no es más dato del mismo tipo: es **otro instrumento, con
otro principio de medición, sobre el mismo terreno**. Donde los dos coinciden en
el espacio, la discrepancia entre sus alturas es la barra de error honesta que
este proyecto no tiene, porque no hay parcelas de campo. No la reemplaza —ATL08
también es una estimación satelital— pero acota.

Además tapa el hueco: **GEDI estuvo hibernado entre marzo de 2023 y abril de
2024**, y ATL08 no.

## Los dos niveles de filtrado, y por qué importan tanto

**Operacional**: altura válida, fotones de copa y terreno, sin nieve,
`cloud_flag_atm = 0`, `msw_flag = 0`, `terrain_flg = 0`.

**Conservador**: lo anterior **más** la disponibilidad de las incertidumbres de
copa y de terreno.

### El sesgo del conservador

El nivel conservador no es un escalón más de calidad. **Selecciona una población
distinta**, y en el bosque la corre entera:

| Recinto | Incertidumbre | n | Mediana `h_canopy_m` |
|---|---|---|---|
| Bosque | disponible | 905 | **10,98 m** |
| Bosque | no disponible | 1.044 | **20,51 m** |
| Estepa | disponible | 1.482 | 9,76 m |
| Estepa | no disponible | 441 | 13,26 m |

Los segmentos que **no** traen incertidumbre son casi el doble de altos. Como la
incertidumbre falta más donde la topografía es compleja y el dosel denso, el
filtro conservador descarta preferentemente el bosque alto. Y entonces:

| Nivel | Mediana bosque | Mediana estepa | Diferencia | IC95 | p |
|---|---|---|---|---|---|
| Operacional | 14,86 m | 11,11 m | **3,75 m** | 2,58 a 6,07 | 0,0001 |
| Conservador | 10,78 m | 10,29 m | **0,49 m** | −1,58 a 3,14 | 0,23 |

*(medianas por gránulo; Cliff delta 0,68 y 0,23 respectivamente)*

**La conclusión se da vuelta según el filtro.** Este es el material de aula más
valioso del paquete y encaja con el criterio de evaluación del TP2, que es la
honestidad del filtrado: un filtro más exigente no da una respuesta «más
verdadera» si además cambia la muestra.

## Cinco advertencias

1. **Las columnas `rh50_m` a `rh100_m` vienen vacías.** El extractor no leyó
   `canopy_h_metrics`. Se usan `h_canopy_m` (RH98) y `h_max_canopy_m` (RH100). Un
   script que promedie `rh95_m` devuelve columna vacía **sin dar error**.
2. **Segmento de 100 m contra huella de 25 m.** No hay correspondencia uno a uno.
   El cotejo se hace agregando: o se promedian las huellas GEDI que caen dentro
   del segmento, o se comparan distribuciones sobre celdas comunes. La decisión
   se documenta, no se improvisa.
3. **Pseudorreplicación.** Los segmentos contiguos comparten terreno, dosel y
   condición de adquisición. La unidad de inferencia del práctico es la **mediana
   por gránulo**, no el segmento.
4. **No hay contemporaneidad.** ATL08 acumula ocho años; GEDI, seis meses. Un
   segmento de 2019 y una huella de 2024 no describen el mismo bosque. Al cotejar
   hay que declarar la ventana temporal usada, y si se restringe ATL08 a la
   ventana de GEDI, decir cuánta muestra queda.
5. **Valores extremos.** El máximo del bosque es de 132,56 m, con un umbral de
   3 IQR en 57,50 m, y ese segmento tiene 24 fotones de copa y 1 de terreno. Es
   un artefacto, no un árbol. `12_valores_extremos.csv` los lista uno por uno.

## El cotejo contra GEDI: lea la razón, no sólo la diferencia

Resultado del paso 13, sobre celdas de 500 m con al menos tres observaciones de
cada misión:

| Recinto | Ventana | Celdas | GEDI `rh98` | ATL08 `h_canopy` | Diferencia pareada | Razón |
|---|---|---|---|---|---|---|
| Bosque | archivo completo | 30 | 6,23 m | 16,81 m | +3,82 m | **2,70 ×** |
| Bosque | ventana de GEDI | 0 | — | — | — | — |
| Estepa | archivo completo | 120 | 3,14 m | 10,30 m | +6,68 m | **3,28 ×** |
| Estepa | ventana de GEDI | 14 | 2,85 m | 9,46 m | +6,71 m | **3,32 ×** |

**La diferencia pareada sola engaña.** «ATL08 lee 3,82 m más alto» suena a un
desfasaje menor hasta que se ve que GEDI está leyendo 6,23 m: la discrepancia es
de casi el triple, no de un margen. Informe siempre las dos cifras juntas.

Nótese además que la diferencia pareada (mediana de las diferencias celda a
celda) y la diferencia de las medianas no coinciden: en el bosque dan 3,82 m y
10,58 m. No es un error de cálculo, es que las diferencias por celda están muy
dispersas, entre 0,07 y 16,7 m. **La cifra que corresponde informar es la
pareada**, porque cada celda es una comparación sobre el mismo terreno.

Una discrepancia de este tamaño obliga a una pregunta que el proyecto no puede
responder hoy: ¿ATL08 lee de más, o GEDI lee de menos? La sección 4.7 de la guía
describe un dosel mayormente bajo a partir de GEDI. Sin parcelas de campo no hay
manera de dirimirlo, y el informe tiene que decirlo en esos términos.

En el bosque, **dentro de la ventana temporal de GEDI no queda ninguna celda
comparable**: sólo hay 37 segmentos ATL08 en esos cinco meses. Es un resultado, no
una falla.

## Sobre el incendio de diciembre de 2025 – enero de 2026

ATL08 **sí puede** registrar pérdida de estructura por fuego. **Estas
adquisiciones no la cuantifican.** El 09/12/2025 hay 45 segmentos operacionales
del RGT 1314 y el 09/02/2026 hay 3 del RGT 872: distinta traza y distinto tamaño
de muestra. La diferencia entre sus medianas **no** mide el daño, y presentarla
como si lo hiciera sería exactamente el error que el curso enseña a no cometer.

Para cuantificarlo hace falta delimitar la cicatriz con dNBR o RdNBR, intersectar
los segmentos con el área quemada y comparar huellas espacialmente equivalentes.
Eso enlaza con el TP3.

## Dónde está cada cosa

| Ruta | Qué hay |
|---|---|
| `02_Subsets_SNAP_QGIS/ICESat2_ATL08/` | Los cuatro CSV de trabajo, con su `LEEME.md` |
| `05_Resultados/04_Tablas/ICESat2_ATL08/` | Los doce resúmenes y el libro de análisis |
| `05_Resultados/03_Vectores/TP2_ICESat2_ATL08.gpkg` | Seis capas para QGIS: `all`, `operational` y `conservative` de cada recinto |
| `05_Resultados/06_Control_calidad/ICESat2_ATL08/` | Auditoría del paquete, notas metodológicas y el LEEME original |
| `06_Bibliografia/04_Enlaces/ENLACES_ICESat2_ATL08.md` | Guía de usuario, diccionario de datos y errores conocidos del NSIDC |

## Verificar en QGIS

El paso 14 deja `05_Resultados/03_Vectores/TP2_ICESat2_cotejo.gpkg`, con seis
capas: los segmentos ATL08 de cada recinto en los dos niveles, las 164 celdas del
cotejo y los dos recuadros. A diferencia del paso 8, **no usa GDAL**: arma el
GeoPackage con `sqlite3` de la biblioteca estándar y al terminar lo vuelve a
abrir para verificar lo que escribió. Se comprobó que GDAL 3.8 lo lee sin
observaciones y que las 164 geometrías son válidas.

Hay también un mapa ya hecho en `05_Resultados/05_Graficos/TP2_cotejo_GEDI_ICESat2_mapa.png`,
que contesta la primera pregunta que uno se hace: **la discrepancia no está
concentrada**. No cae sobre una sola traza ni sobre un borde: aparece repartida
por los dos recintos, y es positiva —ATL08 más alto— en casi todas las celdas.
Sólo unas pocas del bosque salen negativas. Eso descarta el artefacto local y
deja en pie la explicación sistemática.


Arrastre `TP2_ICESat2_ATL08.gpkg` junto a `TP2_GEDI.gpkg` y mire tres cosas:

1. Que las trazas de ATL08 y las de GEDI **no coincidan**: son órbitas distintas.
   Donde se cruzan es donde el cotejo tiene sentido, y son pocos lugares.
2. Que `bosque_operational` tenga segmentos altos y `estepa_operational` no.
3. Que al pasar de `operational` a `conservative` en el bosque **desaparezcan
   justamente los segmentos altos**. Eso es el sesgo, hecho mapa.

Si la tercera no se ve, revise el filtro antes de seguir.
