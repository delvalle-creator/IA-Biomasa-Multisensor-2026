# TP2 — Orden de ejecución

Los scripts se ejecutan **siguiendo su numeración**. Cada uno deja lo que el
siguiente necesita, de modo que saltearse uno hace fallar al que viene.

| Paso | Script | Subcarpeta | Qué hace | Deja / produce |
|---|---|---|---|---|
| 1 | `TP2_01_descargar_gedi.py` | `01_Pre_procesamiento/recortar_AOI` | Descarga GEDI L2A y L2B (NASA Earthdata) | `00_COMUN/08_Originales_crudos/GEDI/` |
| 1b | `TP2_01b_descargar_gedi_l4a.py` | `01_Pre_procesamiento/recortar_AOI` | Descarga el **L4A de biomasa** y extrae los disparos del AOI | `02_Subsets_SNAP_QGIS/GEDI_L4A/` |
| 2 | `TP2_02_recortar_AOI.py` | `01_Pre_procesamiento/recortar_AOI` | Extrae de los `.h5` los disparos dentro de cada AOI | `02_Subsets_SNAP_QGIS/GEDI_L2A/`, `GEDI_L2B/` |
| 3 | `TP2_03_filtrar_calidad.py` | `01_Pre_procesamiento/filtrar_calidad` | Filtra por calidad, órbita degradada y `sensitivity`, y documenta cada descarte | `05_Resultados/04_Tablas/`, `06_Control_calidad/` |
| 4 | `TP2_04_dem_y_pendiente.py` | `01_Pre_procesamiento/filtrar_pendiente` | DEM, pendiente, orientación y sombreado | `00_COMUN/03_Topografia/` |
| 5 | `TP2_05_filtrar_pendiente.py` | `01_Pre_procesamiento/filtrar_pendiente` | Descarta las huellas caídas en pendiente fuerte | `04_Tablas_de_trabajo/01_Bosque/`, `02_Estepa/` |
| 6 | `TP2_06_metricas_estructura.py` | `02_Procesamiento/altura_dosel` | Une el L2B: `pai`, `cover`, `fhd_normal` | `04_Tablas_de_trabajo/*_con_estructura.csv` |
| 7 | `TP2_07_biomasa_referencia.py` | `02_Procesamiento/biomasa_GEDI` | Pega la biomasa del L4A y **particiona por bloques espaciales estratificados por altura** | `05_Resultados/04_Tablas/`, `04_Tablas_de_trabajo/04_Entrenamiento/`, `05_Validacion/` |
| 8 | `TP2_08_exportar_para_gis.py` | `05_Exportacion` | GeoPackage y estilos para QGIS | `05_Resultados/03_Vectores/TP2_GEDI.gpkg` |
| 9 | `TP2_09_cobertura_BAP.py` | `02_Procesamiento/cobertura_BAP` | Asigna a cada huella su clase de cobertura del suelo | columnas `COB_N3`, `COB_GRUPO`, `COB_FRAC` |
| 10 | `TP2_10_auditoria_L4A.py` | `02_Procesamiento/auditoria_L4A` | Audita **por qué** el L4A descarta lo que descarta, por clase de cobertura | tabla de retención por clase |
| 11 | `TP2_11_escenarios_hoja_caida.py` | `02_Procesamiento/auditoria_L4A` | Cuantifica cuánto cambia el AGBD según qué se decida con las huellas tomadas sin hojas | tabla de escenarios |
| 12 | `TP2_12_cargar_ATL08.py` | `01_Pre_procesamiento/cargar_ICESat2` | Proyecta los segmentos ATL08 a la grilla común, verifica que caigan en el recinto y registra la retención | `04_Tablas_de_trabajo/06_ICESat2/` |
| 13 | `TP2_13_cotejar_GEDI_ICESat2.py` | `02_Procesamiento/cotejo_ICESat2` | Compara `rh98` de GEDI contra `h_canopy` de ATL08 sobre celdas de 500 m, en dos ventanas temporales | `05_Resultados/04_Tablas/TP2_cotejo_GEDI_ICESat2_*.csv` |
| 14 | `TP2_14_exportar_ICESat2_para_gis.py` | `05_Exportacion` | GeoPackage y estilos del cotejo, para QGIS | `05_Resultados/03_Vectores/TP2_ICESat2_cotejo.gpkg` |
| 15 | `TP2_15_control_terreno_FABDEM.py` | `02_Procesamiento/control_terreno` | Audita el terreno de ATL08 (y de GEDI) contra FABDEM + geoides; filtra con criterio declarado (±5 m) | `04_Tablas_de_trabajo/06_ICESat2/*_terreno_utm.csv`, `05_Resultados/04_Tablas/TP2_control_terreno_*.csv` |
| 16 | `TP2_16_recotejar_tras_control.py` | `02_Procesamiento/cotejo_ICESat2` | Repite el cotejo del paso 13 sólo con los segmentos que PASAN el control | `05_Resultados/04_Tablas/TP2_cotejo_GEDI_ICESat2_*_terreno*.csv` |
| 17 (último) | `TP2_17_mapa_biomasa_GEDI_CCI.py` | `02_Procesamiento/mapa_biomasa` | Mapa de AGBD GEDI (mediana por celda de 500 m) contra el CCI 2024, con su diferencia | `05_Resultados/02_Rasters/`, `04_Tablas/TP2_mapa_AGB_celdas_*.csv` |

## Los tres auxiliares

No son pasos de la cadena. Se corren sólo si algo falló.

| Script | Subcarpeta | Cuándo |
|---|---|---|
| `TP2_01b_diagnostico_l4a.py` | `01_Pre_procesamiento/recortar_AOI` | Para revisar que el L4A traiga los campos esperados |
| `TP2_01c_reextraer_l4a.py` | `01_Pre_procesamiento/recortar_AOI` | Para releer los `.h5` del L4A sin volver a descargarlos |
| `TP2_04_diagnostico_dem.py` | `01_Pre_procesamiento/filtrar_pendiente` | Si falla la descarga del modelo de elevación |

## Notas

**El 1b va antes del 7, no al final.** Se numera así, y no `09`, porque es el 7 el
que necesita ese producto: sin el L4A, el 7 no puede entregar biomasa y cae en su
alternativa honesta, que es usar `rh95` (altura de dosel) y decirlo.

**El paso 8 no es un trámite.** Existe para que usted verifique en un mapa lo que
los scripts afirman: que el bosque tenga huellas altas y la estepa no, que los
descartes por pendiente caigan sobre las laderas, y que se vea la dispersión real
de GEDI, que son líneas con huecos y no un mapa continuo.

## La rama ICESat-2, de cinco pasos

**El 12 va antes del 13, y el 13 antes del 14.** El 12 no depende de ningún paso
de GEDI: sus insumos son los cuatro CSV de `02_Subsets_SNAP_QGIS/ICESat2_ATL08/`,
que llegan ya extraídos. El 13 sí necesita las dos cosas: la salida del 12 y la
del **paso 6**, que es la que tiene las huellas GEDI con `rh98`.

**El 13 no dice cuál de las dos misiones tiene razón.** Devuelve la discrepancia
entre ambas, que es una cota inferior de la incertidumbre de la referencia. Ninguna
de las dos fue verificada desde el suelo, y el informe tiene que decirlo así.

**El 14 es al 13 lo que el 8 es al 7**: existe para mirar en un mapa lo que la
tabla afirma. Si la discrepancia se concentra sobre las laderas o sobre una sola
traza, no es una propiedad del terreno.

A diferencia del 8, **el 14 no necesita GDAL**: arma el GeoPackage con `sqlite3`,
que viene con Python, y al terminar lo reabre y verifica lo que escribió. Si la
carpeta temporal del sistema está sin espacio, avisa y no deja un archivo a
medias.

**Los pasos 7 a 11** son los que el atajo
`09_ATAJOS\EJECUTAR_cadena_escenarioB.bat` corre de una vez, junto con los cinco
del TP5 (diez pasos en total; el TP5_01 se intercala después del paso 8).
