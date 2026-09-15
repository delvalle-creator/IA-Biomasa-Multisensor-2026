# TP4 — Orden de ejecución

Los pasos 1 a 4 **ya fueron ejecutados**: sus resultados están en `02_Subsets_SNAP_QGIS`.
Usted corre del 5 en adelante: el 5 escribe la máscara de validez de cada recinto
(ver «Pendientes conocidos», más abajo). El 6 usa `scipy`, que el entorno `aoi` ya trae.

| Paso | Script | Subcarpeta | Qué hace | ¿SNAP? |
|---|---|---|---|---|
| 1 | `TP4_01_procesar_sar.py` | `01_Pre_procesamiento/terrain_flattening` | γ⁰ con Terrain Flattening (Sentinel-1 y SAOCOM) | sí |
| 2 | `TP4_02_recortar_crudo.py` | `01_Pre_procesamiento/correccion_geometrica` | Recortes con fase, para polarimetría | sí |
| 3 | `TP4_03_recortar_nisar.py` | `01_Pre_procesamiento` | NISAR GCOV, que ya viene corregido | no |
| 4 | `TP4_04_palsar2_mosaico.py` | `01_Pre_procesamiento` | Mosaico anual de JAXA | no |
| 5 | `TP4_05_mascara_validez.py` | `04_Validacion/efecto_pendiente` | Sombra, acortamiento de pendiente e inversión por relieve | no |
| 6 | `TP4_06_speckle.py` | `02_Procesamiento/filtro_speckle` | Mide el moteado y cuánto R² recupera el promediado | no |
| 7 | `TP4_07_contraste_C_vs_L.py` | `03_Analisis/contraste_bandas` | El contraste bosque − estepa, por banda y polarización | no |
| 8 | `TP4_08_saturacion_radar.py` | `03_Analisis/saturacion` | Cruza con GEDI. **El cierre del práctico** | no |
| 9 | `TP4_09_exportar_para_qgis.py` | `05_Exportacion` | Pasa a dB y deja los rásters listos | no |
| 10 (último) | `TP4_10_indices_polarimetricos.py` | `03_Analisis/indices_polarimetricos` | RVI, RFDI y demás índices del SAOCOM cuadripolar | no |

**Tres auxiliares**, en `01_Pre_procesamiento`. Ninguno es un paso de la cadena:

| Script | Cuándo |
|---|---|
| `TP4_03b_inspeccionar_gcov.py` | Para diagnosticar el producto NISAR |
| `TP4_03c_nisar_post_y_fusion.py` | Recorta las dos escenas NISAR posteriores al incendio y arma con ellas la fusión de las órbitas ascendente y descendente. Explicado en `00_Guia_del_practico/ANEXO_NISAR_fusion_ASC_DES.md` |
| `TP4_11_inspeccionar_biomass_L2A.py` | **Obligatorio antes de correr los grafos de BIOMASS.** Lista las bandas reales del producto e imprime la línea exacta que hay que pegar en el grafo |

## Los grafos de SNAP

En `08_Grafos_SNAP` hay veintisiete archivos `.xml`: dieciocho grafos y sus
nueve gemelos `_cli`. Los grafos produjeron los insumos de los pasos 1 a 5. **Se leen, no se corren**: se abren en
el Graph Builder para ver la cadena de operadores y los encabezados, que explican
cada decisión.

`Fusion_ASC_DES_NISAR.xml` es la excepción que sí se corre, y es opcional: colora
las dos escenas NISAR posteriores al incendio y combina sus polarizaciones. Hace
dentro de SNAP lo mismo que el auxiliar `TP4_03c_nisar_post_y_fusion.py`, para
quien prefiera seguir la cadena con la interfaz a la vista.

**Nueve tienen un gemelo terminado en `_cli`.** Ésos son para la línea de órdenes,
los usa Python y no abren bien en la interfaz gráfica. Trabaje siempre con los que
no llevan ese sufijo.

### Los dos pares de grafos de BIOMASS

`graph_biomass_l2a_altura.xml` y su gemelo `_cli` son la cadena de banda P, escrita
al publicarse el nivel 2A el 30 de junio de 2026. Toman la altura de dosel de
BIOMASS, descartan con `BandMaths` los píxeles que su capa de calidad marca como
malos, recortan al recinto y reproyectan a EPSG:32719 **conservando el píxel nativo
de unos 50 m**: llevar a 10 m una altura medida a 50 fabrica un detalle que el
sensor nunca vio.

**Antes de ejecutarlos hay que correr `TP4_11_inspeccionar_biomass_L2A.py`.** Los
nombres de banda que trae el grafo son provisionales: se escribió sin tener el
producto a la vista, porque la descarga exige autenticarse ante la ESA. Un nombre
de banda equivocado no siempre da error, y una banda vacía que se procesa sin
protestar es peor que un error. Es la misma lección que el TP2 aprendió con
`quality_flag` de GEDI.

#### El segundo par: la colocación

`graph_biomass_a_malla_comun.xml` y su gemelo `_cli` dejan esa altura **exactamente
sobre la grilla del proyecto**: EPSG:32719, 10 m, 1500 × 1500, mismo origen. Sin ese
paso no se puede restar la capa de banda P de ninguna otra.

Usa `Reproject` con una segunda fuente en el parámetro `collocateWith`, que toma de
ella el sistema de referencia, el píxel, el origen y las dimensiones. Es preferible
a fijar `crs` y `pixelSize` a mano, porque así no hay forma de equivocarse en el
origen: **la desalineación de medio píxel es el error clásico de esta operación y no
se ve hasta que uno resta dos capas y le aparece un borde.** Se eligió `Reproject` y
no el operador `Collocate` porque los nombres de los parámetros de éste cambiaron
entre versiones de SNAP, y un grafo que no abre en la versión del alumno no sirve.

Lo que hay que declarar en el informe: pasar de 50 m a 10 m **no agrega
información**. Cada celda de 50 m se replica en veinticinco de 10 m con el mismo
valor —por eso el remuestreo es vecino más próximo y no bilineal—, así que cualquier
estadística sobre la capa colocada tiene en la práctica veinticinco veces menos
grados de libertad de los que sugiere el número de píxeles.

#### Por qué el resto del proyecto no necesita colocarse

Comprobado archivo por archivo: la escena de Sentinel-2, la de
Sentinel-1 GRD, la del SAOCOM, la de NISAR y el mosaico de PALSAR-2 son todas de
1500 × 1500 píxeles de 10 m, en EPSG:32719 y con el mismo origen, 287200 / 5285200,
coincidente hasta los 6 × 10⁻⁸ m. **La sinergia óptico-radar del TP5 ya está
colocada por construcción**, desde que el TP1 impuso la malla común. Además
`TP5_01_dataset.py` no depende de eso: convierte las coordenadas de cada huella a
fila y columna con el `transform` propio de cada ráster, de modo que sería correcto
aunque las grillas difirieran. Las que sí necesitan colocarse son las capas ajenas:
BIOMASS a 50 m y las tres del producto forestal de Chubut, a 30 m en EPSG:4326.

**BIOMASS entra como demostración del sensor, no como insumo del análisis.** Todas
las adquisiciones de nivel 2A son posteriores al incendio (10/01 al 27/02 de 2026),
así que no hay par con el cual medir cambio. Se abre, se mira, se explica, y se
declara por escrito que no intervino en ningún resultado.

## Pendientes conocidos

**La línea de base SAOCOM (`02_Subsets_SNAP_QGIS/SAOCOM/01_linea_base_2023_24`) está vacía.**
Los productos están descargados pero sin procesar. Si el TP5 la va a usar, hay que
correr antes:

    python TP4_01_procesar_sar.py SAOCOM_L1A linea_base

El script intenta cada escena contra los dos AOI, y éstas no cubren los dos: va a
ver errores esperables de `gpt` en las combinaciones que no corresponden. **No es
un error del script**: los cuenta como fallidos y sigue.

**El paso 5 escribe `mascara_validez_<AOI>.tif`, una por recinto.** Si en
`02_Subsets_SNAP_QGIS/mascaras` sólo aparece un archivo sin el sufijo del recinto,
hay que volver a correrlo para que el TP5 aplique la máscara que corresponde a
cada sitio.

## Nota sobre escalas

**γ⁰ se guarda LINEAL.** El paso 9 pasa a decibeles, y sólo al final: filtrar o
promediar en decibeles sesga sistemáticamente hacia abajo, porque el logaritmo de
un promedio no es el promedio de los logaritmos.
