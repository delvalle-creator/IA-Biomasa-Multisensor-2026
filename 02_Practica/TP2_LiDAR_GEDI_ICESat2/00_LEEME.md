# TP2 — LiDAR espacial: GEDI e ICESat-2. Qué hay en cada carpeta

El práctico está **resuelto de punta a punta**. Usted lo recorre completo: desde el
prompt que se le escribió a la IA hasta el informe final. Nada está vacío por
descuido; si algo falta, está dicho.

> Los números de esta tabla los produce `00_COMUN/contar_archivos.py`, que
> los lee del disco. Si dejan de coincidir, vuelva a correrlo en lugar de
> corregirlos a mano.


## El recorrido, en orden

| Carpeta | Qué hay | Archivos |
|---|---|---|
| `00_Guia_del_practico/` | **Empiece por acá:** la guía sintética en PDF, con su LEEME, más los objetivos, las figuras, las diapositivas, el flujo de trabajo y los dos anexos: las huellas sin hojas y el cotejo con el CCI Biomass (con su mapa del paso 17) | 23 |
| `01_Prompt_IA/` | El prompt inicial, la respuesta de la IA, el prompt corregido y la verificación | 4 |
| `02_Subsets_SNAP_QGIS/` | Los datos de entrada, en CSV: GEDI L2A, L2B y L4A recortados a los dos recintos, y los segmentos **ICESat-2 / ATL08** con su LEEME. **Vienen en el repositorio** | 11 |
| `03_Scripts/` | Los diecisiete pasos numerados, más el 1b, en orden de ejecución, y el archivo que fija ese orden | 30 |
| `04_Tablas_de_trabajo/` | Huellas válidas y partición **por bloques espaciales estratificados por altura**. La crean los scripts 05 y 07. Los segmentos ATL08 proyectados los deja el 12, y su versión tras el control de terreno FABDEM, el 15 | 19 |
| `05_Resultados/` | Tablas, gráficos y control de calidad de las dos misiones, el cotejo con el CCI Biomass y el control de terreno; los mapas de biomasa GEDI y CCI del paso 17, y el GeoPackage de ATL08. Los GeoPackage de los pasos 8 y 14 los escriben esos pasos | 92 |
| `06_Bibliografia/` | Referencias de los artículos, manuales, fichas técnicas de GEDI y de ATL08, y enlaces | 6 |
| `07_Preguntas_y_entrega/` | Aquí deja el estudiante sus respuestas y su entrega | 1 |
| `09_Orange/` | Los tres flujos de Orange Data Mining (GEDI, ATLAS con su control de terreno, CCI), con variables preseleccionadas, y su LEEME | 4 |
| | Los cuatro archivos de la raíz: presentación, las dos notas técnicas y de dónde salen los insumos | 4 |
| | **TOTAL** | **194** |

Este práctico no usa grafos de SNAP, por eso no tiene `08_Grafos_SNAP`.

## La rama ICESat-2 / ATL08

Desde agosto de 2026 este práctico usa **dos** LiDAR espaciales, no uno.

GEDI es la referencia de biomasa del curso y nadie la verificó desde el suelo:
no hay parcelas de campo, y está declarado. ICESat-2 no resuelve eso —también
es una estimación satelital— pero es **otro instrumento, con otro principio de
medición, sobre el mismo terreno**. Donde las dos misiones pasan por el mismo
lugar, la diferencia entre lo que dicen acota la incertidumbre de la referencia.

Además cubre lo que GEDI no puede: ATL08 va de noviembre de 2018 a abril de
2026, e incluye la hibernación de GEDI entre marzo de 2023 y abril de 2024.

Lo técnico está en **`NOTAS_TECNICAS_ICESat2.md`**, que conviene leer antes de
correr el paso 12. En particular el apartado del sesgo del filtro conservador:
según qué filtro se use, la diferencia de altura entre bosque y estepa da
3,75 m con p < 0,001 o 0,49 m con p = 0,23. La conclusión cambia con el filtro,
y eso es exactamente lo que este práctico evalúa.

El práctico completo, con su fundamentación, está en la guía teórico-práctica: `02_Practica\00_Guia_teorica_practica`.

## Dónde escribe cada script

| # | Script | Deja el resultado en |
|---|---|---|
| 1 | `TP2_01_descargar_gedi.py` | `00_COMUN/08_Originales_crudos/` |
| 1b | `TP2_01b_descargar_gedi_l4a.py` | `02_Subsets_SNAP_QGIS/GEDI_L4A/` ← **la biomasa de referencia** |
| 2 | `TP2_02_recortar_AOI.py` | `02_Subsets_SNAP_QGIS/GEDI_L2A/` y `GEDI_L2B/` |
| 3 | `TP2_03_filtrar_calidad.py` | `05_Resultados/04_Tablas/` y `06_Control_calidad/` |
| 4 | `TP2_04_dem_y_pendiente.py` | `00_COMUN/03_Topografia/DEM/` |
| 5 | `TP2_05_filtrar_pendiente.py` | `04_Tablas_de_trabajo/01_Bosque`, `02_Estepa` |
| 6 | `TP2_06_metricas_estructura.py` | `05_Resultados/04_Tablas/` |
| 7 | `TP2_07_biomasa_referencia.py` | `04_Tablas_de_trabajo/04_Entrenamiento`, `05_Validacion` |
| 8 | `TP2_08_exportar_para_gis.py` | `05_Resultados/03_Vectores/` ← **esto se abre en QGIS** |
| 12 | `TP2_12_cargar_ATL08.py` | `04_Tablas_de_trabajo/06_ICESat2/` |
| 13 | `TP2_13_cotejar_GEDI_ICESat2.py` | `05_Resultados/04_Tablas/` ← **el cotejo entre las dos misiones** |
| 14 | `TP2_14_exportar_ICESat2_para_gis.py` | `05_Resultados/03_Vectores/` ← **esto también se abre en QGIS** |

Los scripts están en `03_Scripts/`, repartidos por etapa: pre-procesamiento,
procesamiento y exportación. El orden completo, con lo que produce cada uno,
está en `03_Scripts/00_ORDEN_DE_EJECUCION.md`.

**`TP2_01b_descargar_gedi_l4a.py`** baja el producto de biomasa L4A. Se numera
01b, y no 09, porque tiene que correr ANTES del 07: es el 07 el que lo necesita
para entregar biomasa en Mg/ha en vez de altura de dosel.

## Las carpetas que escriben los scripts

- `04_Tablas_de_trabajo/01_Bosque` y `02_Estepa` — las escribe el script 05.
- `04_Tablas_de_trabajo/04_Entrenamiento` y `05_Validacion` — las escribe el script 07.
- `02_Subsets_SNAP_QGIS/GEDI_L4A` — viene con los dos CSV del producto de biomasa.
  Si faltaran, el script 07 lo avisa y calibra contra altura, diciéndolo.
- `05_Resultados/03_Vectores/TP2_GEDI.gpkg` y `TP2_ICESat2_cotejo.gpkg` — los
  escriben los pasos 8 y 14.

## Lo que NO está, y es información

- **No hay parcelas de campo.** Es la limitación más seria del proyecto entero, y
  está declarada en el informe: GEDI es la referencia, pero GEDI también es una
  estimación satelital que nadie verificó desde el suelo. Por eso ninguna
  conclusión de este curso puede presentarse como una medición de biomasa.
- **No hay conjunto de test**, solo entrenamiento y validación (tres bloques de
  cada cuatro contra el cuarto, unas 82/18 huellas de cada cien). Con ~770
  huellas en el bosque, partir en tres dejaría grupos demasiado chicos para que
  las métricas signifiquen algo.
- **No hay rásters ni modelos en este práctico**: GEDI produce puntos y tablas,
  ATL08 produce segmentos y tablas. Los rásters aparecen en el TP3 y el TP4; los
  modelos, en el TP5.
- **ICESat-2 no entrega biomasa.** ATL08 da altura y estructura, no Mg/ha. La
  biomasa de referencia sigue saliendo del L4A de GEDI. Lo que ATL08 aporta es
  un control independiente de esa altura, no una segunda fuente de biomasa.

## Lo que tiene que verificar usted

No le crea al script. El octavo paso existe para eso:

    05_Resultados/03_Vectores/TP2_GEDI.gpkg   (+ los .qml)

Arrástrelo a QGIS, cargue el estilo de cada capa, y compruebe tres cosas: que el
bosque tenga huellas altas y la estepa no; que los descartados por pendiente caigan
sobre las laderas del DEM; y que se vea la dispersión real de GEDI, que son líneas
con huecos, no un mapa.

Si alguna de las tres no se cumple, hay un error, y encontrarlo es parte del
práctico.
