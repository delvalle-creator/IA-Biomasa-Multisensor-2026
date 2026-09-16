# TP1 — Búsqueda inteligente y evaluación crítica de datos

El práctico está **resuelto de punta a punta**, desde el prompt que se le escribió
a la IA hasta los resultados. Las únicas carpetas vacías son las que deben estarlo, y cada una dice por qué en la tabla de abajo.

> Los números de esta tabla los produce `00_COMUN/contar_archivos.py`, que
> los lee del disco. Si dejan de coincidir, vuelva a correrlo en lugar de
> corregirlos a mano.


## El recorrido, en orden

| Carpeta | Qué hay | Archivos |
|---|---|---|
| `00_Guia_del_practico/` | **Empiece por acá:** la guía sintética en PDF, con su LEEME, más los objetivos y las figuras (la fig15 del encadenamiento, con ICESat-2 y CCI Biomass, también en SVG) y los programas que las generan. El desarrollo completo, en el capítulo 3 de la guía teórico-práctica | 12 |
| `01_Prompt_IA/` | El prompt inicial con sus defectos, el análisis de la respuesta, el prompt maestro corregido y la verificación | 5 |
| `02_Subsets_SNAP_QGIS/` | El inventario de datasets evaluados (los AOI se leen de `00_COMUN/01_AOI/`) | 4 |
| `03_Scripts/` | Los diez scripts, numerados en orden de ejecución, más configuración y funciones de apoyo | 17 |
| `04_Tablas_de_trabajo/` | El TP1 no produce subconjuntos; ver su LEEME | 1 |
| `05_Resultados/` | La matriz de datos, las tablas de control de los pasos 1 y 2, y la línea de tiempo | 4 |
| `06_Bibliografia/` | Referencias de los artículos, manuales, fichas de los ocho sensores y enlaces | 5 |
| `07_Preguntas_y_entrega/` | La tabla maestra de sensores. **Aquí deja el estudiante sus respuestas y su entrega** | 2 |
| | Los tres archivos de la raíz: presentación, notas técnicas y de dónde salen los insumos | 3 |
| | **TOTAL** | **53** |

Este práctico no usa grafos de SNAP, por eso no tiene `08_Grafos_SNAP`.

El práctico completo, con su fundamentación, está en la guía teórico-práctica: `02_Practica\00_Guia_teorica_practica`.

## Los diez scripts

| # | Script | Qué hace |
|---|---|---|
| 1 | `TP1_01_verificar_cobertura.py` | Verifica cobertura real dentro del AOI |
| 2 | `TP1_02_detectar_bruma.py` | Detecta bruma/humo y descarta escenas malas |
| 3 | `TP1_03_descargar_sentinel.py` | Descarga Sentinel-1 y Sentinel-2 |
| 4 | `TP1_04_descargar_landsat.py` | Descarga Landsat 9 (Planetary Computer) |
| 5 | `TP1_05_descargar_gedi.py` | Descarga GEDI e ICESat-2 ATL08 |
| 6 | `TP1_06_alos_nisar_informe.py` | Informa/descarga ALOS y NISAR |
| 7 | `TP1_07_descargar_nisar.py` | Descarga NISAR GCOV |
| 8 | `TP1_08_descargar_biomass.py` | Descarga BIOMASS banda P (ESA MAAP) |
| 9 | `TP1_09_inventario.py` | Inventario de lo descargado |
| 10 | `TP1_10_reconstruir_diccionario.py` | Reconstruye el diccionario de nombres |

Los scripts 1 y 2 escriben sus tablas de control (`verificacion_cobertura.csv` y
`deteccion_bruma.csv`) en `05_Resultados/04_Tablas` al ejecutarse. Si no las ve,
todavía no los corrió.

## El séptimo proveedor: el SAOCOM no se descarga con un script

Los diez scripts cubren seis de los siete proveedores. El séptimo es la CONAE,
que distribuye el SAOCOM: su catálogo exige registro, solicitud y autorización
previas, y entrega después por un enlace personal. Por eso no hay un
`TP1_..._descargar_saocom.py`, y por eso el trámite está documentado como tal en
`00_COMUN/08_Originales_crudos/PEDIDO_SAOCOM_28jul2026.md`, que está en el disco
del curso y no viaja en el repositorio. Las escenas también están en el disco del curso, y sus recortes en γ⁰, en `TP4_Radar_SAR/02_Subsets_SNAP_QGIS/SAOCOM`.

## Lo que este práctico enseña, en una línea

**Verificar antes de descargar.** Consultar por un rectángulo devuelve todo lo que
lo *toca*, no lo que lo *cubre*; la nubosidad del catálogo es de la escena entera y
no de su recinto; y la máscara de nubes no ve la bruma.

Las tres reglas están medidas, no supuestas:

- 6 gránulos NISAR prometían 69–76 % de cobertura y tenían **15 %** real. **12 GB
  de descarga inútil** que se habrían evitado verificando primero.
- La escena del 09/01/2026 declaraba 7,4 % de nubes y tenía el azul **6,7 veces**
  por encima de lo normal del sitio.
- Landsat 9, cinco días antes, daba NDVI 0,78 donde Sentinel-2 daba 0,34. **Dos
  sensores independientes en desacuerdo: ahí hay que ir a mirar.**

## Lo que NO está, y es información

- **No hay `04_Tablas_de_trabajo`**: el TP1 no produce subconjuntos, sólo busca y evalúa. Los
  recortes empiezan en el TP3.
- **No hay rásters ni modelos**: este práctico produce decisiones y tablas.
- **Banda S de NISAR: confirmada SIN cobertura sobre los AOI.** Se
  distribuye por Bhoonidhi (ISRO), no por la NASA; su producción arrancó el
  08/07/2026. La búsqueda sobre BOSQUE y ESTEPA devuelve **0 escenas**: la banda S
  se adquiere sobre la India. NovaSAR-1 (banda S) tampoco cubre la zona y además es
  comercial. Ambas quedan **evaluadas y descartadas**. Verificado en Bhoonidhi y
  documentado en `01_Prompt_IA/04_Verificacion/`.
