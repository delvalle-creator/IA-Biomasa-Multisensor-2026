# 04_Tablas_de_trabajo — TP2

Acá van los subconjuntos derivados de las huellas de GEDI. **La carpeta se llena
al correr los scripts**; si está vacía, todavía no los corrió.

| Subcarpeta | Qué contiene | La crea |
|---|---|---|
| `01_Bosque/` | Huellas válidas de `BOSQUE_NW_02`, tras calidad y pendiente | `TP2_05_filtrar_pendiente.py` |
| `02_Estepa/` | Huellas válidas de `ESTEPA_NW_02` | `TP2_05_filtrar_pendiente.py` |
| `04_Entrenamiento/` | Tres de cada cuatro bloques, para ajustar (bosque 569 huellas, estepa 2.498) | `TP2_07_biomasa_referencia.py` |
| `05_Validacion/` | El cuarto bloque de cada grupo, para evaluar (bosque 121, estepa 585) | `TP2_07_biomasa_referencia.py` |
| `06_ICESat2/` | Segmentos ATL08 normalizados (`*_utm.csv`, paso 12) y su versión tras el control de terreno FABDEM (`*_terreno_utm.csv`, paso 15) | `TP2_12` y `TP2_15` |

## La partición no es al azar, y eso importa

Se reparten **bloques de terreno enteros de 3 × 3 km**, no huellas sueltas. Las
huellas de GEDI se alinean a lo largo de la órbita: dos vecinas distan 60 m y ven
prácticamente el mismo bosque. Con una partición aleatoria, una cae en
entrenamiento y la otra en validación, y el modelo termina evaluado con
información que ya vio: el R² sale optimista y no dice nada sobre la capacidad de
predecir en otro lado.

Repartiendo bloques enteros, la validación cae sobre terreno que el modelo no vio.
Es lo que exige el criterio de evaluación del TP5: **distinguir mejora real de
sobreajuste**.

## Los bloques tampoco se sortean: se estratifican por altura

El bloque entero como unidad evita la
filtración espacial, pero no garantiza que las dos partes se parezcan. En el
bosque los veintidós bloques tienen medianas de rh95 que van de 2,84 a 18,94 m,
y el sorteo mandaba los más altos a validación:

| | Entrenamiento (mediana rh95) | Validación (mediana rh95) | Desfase |
|---|---|---|---|
| Sorteo al azar | 4,26 m | 13,54 m | 9,28 m |
| Estratificado por altura | 5,35 m | 4,15 m | 1,20 m |

Un modelo entrenado con arbustos y validado con árboles no mide lo que se cree
que mide, y el R² que sale de ahí no es interpretable. La corrección ordena los
bloques por su mediana de altura y manda **uno de cada cuatro a validación**: los
bloques siguen enteros —no hay filtración— y las dos particiones cubren todo el
rango de alturas. El reparto es determinístico, sin semilla ni azar, de modo que
el TP3, el TP4 y el TP5 trabajan siempre con las mismas muestras.

El reparto resultante no es exactamente 70/30 sino cercano a 80/20, porque la
unidad es el bloque y no la huella: bosque 569 / 121, estepa 2.498 / 585.

Los subconjuntos de esta carpeta los consumen el TP3, el TP4 y el TP5.
