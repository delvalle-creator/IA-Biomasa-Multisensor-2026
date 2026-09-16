# TP3 — Datos ópticos: índices, incendio y el límite del método

El práctico está **resuelto de punta a punta**. Las únicas carpetas vacías son las que deben estarlo, y cada una dice por qué en la tabla de abajo.

> Los números de esta tabla los produce `00_COMUN/contar_archivos.py`, que
> los lee del disco. Si dejan de coincidir, vuelva a correrlo en lugar de
> corregirlos a mano.


## El recorrido, en orden

| Carpeta | Qué hay | Archivos |
|---|---|---|
| `00_Guia_del_practico/` | **Empiece por acá:** la guía sintética en PDF, con su LEEME, más los objetivos, las figuras con sus generadores, las diapositivas, el flujo de trabajo y el anexo de mapas forestales de Chubut. El desarrollo completo, en el capítulo 5 de la guía teórico-práctica | 19 |
| `01_Prompt_IA/` | El prompt inicial con sus defectos, el análisis de la respuesta, el prompt corregido y la verificación | 4 |
| `02_Subsets_SNAP_QGIS/` | Sentinel-2 (14 GeoTIFF) y Landsat 9 (24 GeoTIFF) recortados a la grilla común, por época y sitio, más los tres mapas forestales de Chubut recortados y el LEEME de la escena pre-incendio. **Vienen en el repositorio** | 45 |
| `03_Scripts/` | Los seis scripts, numerados en orden de ejecución, más configuración y funciones de apoyo, y el orden de ejecución | 11 |
| `04_Tablas_de_trabajo/` | El TP3 usa las huellas del TP2; ver su LEEME | 1 |
| `05_Resultados/` | Las tablas y los gráficos. Los rásters y el GeoPackage los escriben los scripts al correr | 10 |
| `06_Bibliografia/` | Referencias de los artículos, manuales, fichas de los sensores y enlaces | 5 |
| `07_Preguntas_y_entrega/` | Sólo el LEEME: **aquí deja el estudiante sus respuestas y su entrega** | 1 |
| `08_Grafos_SNAP/` | El grafo del Graph Builder que recorta Sentinel-2 | 1 |
| | Los tres archivos de la raíz: presentación, notas técnicas y de dónde salen los insumos | 3 |
| | **TOTAL** | **100** |

El práctico completo, con su fundamentación, está en la guía teórico-práctica: `02_Practica\00_Guia_teorica_practica`.

## Los seis scripts

| # | Script | Qué hace |
|---|---|---|
| 1 | `TP3_01_recortar_sentinel2.py` | Recorta Sentinel-2 a la grilla común (SNAP) |
| 2 | `TP3_02_landsat9.py` | Descarga y recorta Landsat 9 |
| 3 | `TP3_03_indices.py` | NDVI, EVI, NDMI y NBR en todas las escenas |
| 4 | `TP3_04_dnbr_incendio.py` | dNBR y clases de severidad |
| 5 | `TP3_05_saturacion_y_modelo.py` | Cruza con GEDI y **mide dónde satura cada índice** |
| 6 | `TP3_06_exportar_para_gis.py` | Estilos `.qml` y área quemada vectorizada, para QGIS |

Los scripts 3 a 6 escriben `05_Resultados/02_Rasters` y `03_Vectores` al
ejecutarse, y el 5 y el 6 dejan sus tablas en `04_Tablas`. Los productos de SNAP
del paso 1 (pares `.dim` + `.data`) no viajan en el repositorio: los programas
leen los GeoTIFF.

## Lo que este práctico demuestra

**Que el óptico no alcanza.** Y está medido, no citado:

- El **NDVI satura a partir de los 15–18 m** de dosel: llega a 0,888 y queda en
  0,879, 0,897 y 0,893 en las franjas siguientes, hasta los 30 m. El EVI también se aplana (0,549 y 0,550).
- **Ningún índice explica más de un tercio** de la altura en el bosque (el
  mejor ajuste llega a R² = 0,31 con un error de 5,86 m, sobre un bosque de
  5,07 m de altura mediana).
- Los dos índices que mejor andan, NDMI y NBR, son **los que usan el infrarrojo de
  onda corta**: la banda de mayor longitud de onda del sensor. La tendencia apunta
  al radar del TP4.

**Y que el óptico sí sirve para el fuego:** 18.009,2 ha quemadas (80,2 % del
área con dato), con el NBR cambiando de signo de 0,512 a −0,200.

## La decisión metodológica central

**La escena pre-incendio NO es la más cercana al fuego.** La del 09/01/2026 está a
un día del incendio, pero tiene humo de los incendios: azul 0,158 contra 0,024 normal, y la máscara
del producto sólo marcó 7,4 % de cirros. Se usa la del 25/11/2025.

Cambia poco el resultado (16.502 contra 18.009 ha) **porque el NBR no usa el rojo**.
Con NDVI habría sido inservible. Una escena no está mala en abstracto: está mala
**para un índice determinado**.

## Lo que hay que verificar en QGIS

Corra el script 6 y cargue:

    05_Resultados/02_Rasters/incendio/<AOI>/severidad_<AOI>.tif  + 02_Rasters/severidad.qml
    05_Resultados/03_Vectores/TP3_incendio.gpkg

**Sin el `.qml` el ráster de severidad se ve como siete grises casi iguales**: sus
valores 1 a 7 son códigos de clase, no cantidades.

Y la verificación que importa: superponga las huellas GEDI del TP2
(`TP2_LiDAR_GEDI_ICESat2/05_Resultados/03_Vectores/TP2_GEDI.gpkg`) y mire cuáles quedaron
dentro del área quemada. Ese cruce es el que hace el script 5 con números.

## Lo que NO está, y es información

- **`04_Tablas_de_trabajo` sólo tiene su LEEME**: el TP3 usa las huellas del TP2, no produce subconjuntos
  propios.
- **Los umbrales de severidad son importados** (Key y Benson, 2006, calibrados en
  Norteamérica). Las hectáreas totales son firmes; el reparto por clases, menos.
- **Este bosque es bajo**: la mitad de las huellas no llega a 9 m. En ese rango el
  óptico todavía no satura, así que la comparación con el TP4 está sesgada a favor
  del óptico.
