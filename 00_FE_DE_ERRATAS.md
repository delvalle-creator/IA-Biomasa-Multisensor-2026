# Fe de erratas del curso «IA multisensor para estimar biomasa en bosques andinos y pastizales del ecotono bosque-estepa»

Esquel, Chubut, del 14 al 19 de septiembre de 2026. Documento del 14 de septiembre de 2026, con la Parte G del 16 de septiembre y la Parte H del 17.

Este documento corrige la versión del curso que ustedes descargaron: el repositorio IA-Biomasa-Multisensor-2026, entrega v1.0.0. Los errores se encontraron haciendo el curso completo, paso a paso y como alumno, en los días previos al dictado, y revisando después todos los documentos contra los archivos de datos que producen los programas.

Se corrigieron 47 archivos de texto: 17 programas y 30 documentos, más seis presentaciones .pptx del docente (que no se distribuyen; su detalle está en el informe aparte sobre las presentaciones). Ninguna corrección cambia las conclusiones del curso. Sí cambian resultados que ustedes entregan, y por eso conviene aplicarlas antes de empezar.

## Cómo se aplica

Si usted trabaja con esta versión del curso, no tiene que hacer nada: las 47 correcciones ya están aplicadas en los archivos que acompañan a este documento. Esta fe de erratas queda como constancia de qué cambió respecto de la entrega v1.0.0 y por qué.

Si conserva la copia v1.0.0 que descargó y prefiere seguir con ella, lo más simple es descargar esta versión y reemplazarla entera. Si quiere corregir sólo lo necesario, cada punto de la Parte A dice qué archivo cambió y qué hace la corrección; el docente puede entregarle la carpeta con los 47 archivos corregidos, cada uno con la ruta exacta que le corresponde en el curso.

Si prefiere no reemplazar nada, puede trabajar con los archivos como están: en cada punto se explica qué va a ver en pantalla y cuál es el resultado correcto.

## Parte A. Errores que impiden o cambian resultados

Son ocho, y los ocho aparecen al correr los prácticos.

**A1. TP1, paso 1: nubosidad falsa del 85 % o del 99 %.** Archivo: TP1_Busqueda_IA\03_Scripts\01_Consulta_catalogos\TP1_01_verificar_cobertura.py.

En Sentinel-2 el programa contaba como nube todo píxel cuya banda de clasificación vale 0, que en realidad es píxel sin dato, fuera de la franja del satélite. En una escena que cubre el 14,7 % del recinto, el 85,3 % restante aparecía como nubosidad, con un aviso de que el catálogo se apartaba 85 puntos. Corregido: la nubosidad se mide sólo sobre los píxeles con dato, que es el criterio que el propio programa ya usaba para Landsat 9. Las dos escenas afectadas pasan de 85,3 % y 99,6 % a 0,0 %.

**A2. TP1, pasos 9 y 10: el inventario da casi todo sin procesar y el diccionario se niega a escribir.** Archivos: funciones\aoi_config.py, TP1_09_inventario.py y TP1_10_reconstruir_diccionario.py.

El programa buscaba los productos ya procesados en carpetas con el nombre corto de la época (01_base, 02_pre, 03_post), cuando en el disco se llaman con el nombre largo (01_linea_base_2023_24 y los demás). No encontraba nada y lo informaba como pendiente, sin ningún mensaje de error. Además, reconocía el producto procesado sólo si era .dim, y varios son .tif. Corregido: se traduce el nombre de la época y se aceptan los dos formatos. El inventario vuelve a coincidir fila por fila con el del 28 de julio.

**A3. TP1, consulta de BIOMASS (atajo EJECUTAR_consulta_BIOMASS.bat): mensaje de error al arrancar y registro vacío.** Archivo: TP4_Radar_SAR\03_Scripts\01_Pre_procesamiento\BIOMASS_bandaP\buscar_biomass_L2.py.

Faltaba importar el módulo io, de modo que el programa avisaba «no se pudo abrir el registro: name 'io' is not defined» y CONSULTA_BIOMASS.log quedaba vacío. Corregido con una línea. La consulta y la tabla no cambian.

**A4. TP3, paso 5: la saturación no se ve, y el modelo da un R² que contradice la conclusión del práctico.** Archivo: TP3_Datos_Opticos\03_Scripts\03_Analisis\regresion_lineal\TP3_05_saturacion_y_modelo.py.

El programa tomaba «la escena previa más cercana al fuego», que por orden alfabético es la del 09/01/2026: justamente la escena con humo que el curso decide no usar. Con ella, el NDVI del bosque alto da 0,55 en lugar de 0,90 y la curva de saturación no muestra ningún techo. Además ajustaba el modelo mezclando bosque y estepa, lo que infla el R² a 0,41 porque el ajuste aprende a separar los dos sitios.

Corregido: usa la escena limpia del 25/11/2025, la misma que el paso 4, e informa dos bloques de modelos, primero el del bosque (el que se interpreta) y después, rotulado, el de los dos sitios juntos. Con la corrección, la tabla de saturación y los ajustes reproducen el desarrollo del curso: el NDMI da R² 0,310 y error de 5,86 m sobre 690 huellas.

**A5. TP3, paso 2: vuelve a descargar Landsat 9 en carpetas duplicadas.** Archivo: TP3_Datos_Opticos\03_Scripts\01_Pre_procesamiento\remuestreo\TP3_02_landsat9.py.

Mismo defecto de nombres de carpeta que A2: no reconocía las 24 imágenes que ya estaban y las bajaba de nuevo en carpetas nuevas. Corregido: si los dos recintos ya tienen su escena, lo informa y no se conecta a internet.

**A6. TP4, paso 5: «sin productos SAR» y ninguna máscara escrita.** Archivos: TP4_Radar_SAR\03_Scripts\funciones\aoi_config.py y 04_Validacion\efecto_pendiente\TP4_05_mascara_validez.py.

Cada práctico tiene su copia de aoi_config.py, y la del TP4 arrastraba el defecto de A2. El paso 5 contestaba «sin productos SAR» en los dos recintos, sin error, y no escribía las máscaras de validez geométrica. Corregido: ahora informa la validez por sensor y descarta el 4,4 % del bosque y el 3,5 % de la estepa, las cifras de la guía. Esto además afecta al TP5: sus mapas se dibujaban sin la máscara.

**A7. TP4, paso 6: corta con un error de GDAL antes de producir nada.** Archivo: TP4_Radar_SAR\03_Scripts\02_Procesamiento\filtro_speckle\TP4_06_speckle.py.

La línea 222 encadenaba gdal.Open(archivo).GetRasterBand(b).ReadAsArray(). En GDAL 3, que es el que trae el entorno aoi, el archivo se cierra al terminar esa línea y la banda queda colgando: TypeError: in method 'Band_XSize_get'. Corregido guardando el archivo abierto en una variable. Le ocurre a cualquiera que corra ese paso.

**A8. TP5, validación estricta: FileNotFoundError aunque se sigan las instrucciones.** Archivo: TP5_Sinergia_Multisensor\03_Scripts\03_Analisis\TP5_06_validacion_estricta.py.

El programa vive dos niveles por debajo de la carpeta del práctico y buscaba los datos un solo nivel arriba; al no encontrar esa ruta, un respaldo interno lo hacía buscar los archivos al lado del programa. Corregido: sube por el árbol hasta encontrar 04_Tablas_de_trabajo y 05_Resultados\04_Tablas, de modo que funciona desde cualquier carpeta.

## Parte B. Mensajes y textos de los programas

No cambian ningún resultado, pero confunden.

| **Dónde**                     | **Decía**                                                                                                    | **Dice ahora**                                                 |
|---|---|---|
| TP1_01, rótulo de la consulta | Sentinel-2 L2A (pre-incendio), sobre una ventana del 1 al 20 de enero de 2026, que cruza el inicio del fuego | Sentinel-2 L2A (1 al 20/01/2026)                               |
| TP1_01, último renglón        | SIGUIENTE PASO: TP1_03_descargar_sentinel.py                                                                 | SIGUIENTE PASO: TP1_02_detectar_bruma.py                       |
| TP1_02, cierre                | 79,2 % contra 80,0 %                                                                                         | 79,4 % contra 80,2 %                                           |
| TP1_08, encabezado            | Remite a un tutorial en C:\Temp\BIOMASS y pide instalar con pip                                              | Remite a la guía teórico-práctica; el entorno aoi ya trae todo |
| TP1_08, arranque              | Pide el client_secret siempre, sin explicación                                                               | Lo pide sólo si hay token, y avisa para qué                    |
| TP1_08, nivel 2A              | 0 producto(s) 1S, que se lee como «no hay nivel 2A»                                                          | Cuenta y lista los productos de nivel 2A                       |
| TP3_04, comentario inicial    | 16.463 ha (79,2 %) y 17.959 ha (80,0 %)                                                                      | 16.502 ha (79,4 %) y 18.009 ha (80,2 %)                        |
| TP3_06 y LEEME del TP3        | Seis grises, valores 1 a 6                                                                                   | Siete grises, valores 1 a 7                                    |
| TP4_05, encabezado            | Declara la salida en 04_Tablas_de_trabajo                                                                    | 02_Subsets_SNAP_QGIS\mascaras\mascara_validez\_\<AOI\>.tif     |

## Parte C. Cifras corregidas en los documentos

Se corrigieron en los archivos .md del curso. Las cifras nuevas salen de las tablas que producen los propios programas.

| **Documento**                                                   | **Decía**                                                                                                     | **Dice ahora**                                                                                                       |
|---|---|---|
| TP1, 00_LEEME y Prompt_IA (respuesta)                           | La escena del 9/1 declaraba 0,4 % de nubes                                                                    | 7,4 % (deteccion_bruma.csv)                                                                                          |
| TP1, Prompt_IA (verificación)                                   | 16.463,1 ha (79,3 %)                                                                                          | 16.502 ha (79,4 %)                                                                                                   |
| TP1, fichas de sensores                                         | azul 0,1528; NDVI 0,38; Landsat 0,85; difieren 0,47                                                           | 0,1577; 0,34; 0,78; 0,44                                                                                             |
| TP2, Prompt_IA (verificación)                                   | Bosque: ~10 m (rango 2–38 m)                                                                                  | 5,07 m (rango 1,98–35,57 m)                                                                                          |
| TP2, notas técnicas de ICESat-2                                 | Diferencias por celda entre 0,07 y 16,7 m                                                                     | Entre −11,40 y 16,70 m                                                                                               |
| TP2, anexo de las huellas sin hojas                             | 104 huellas de lenga sin hojas; 199 de 220 en noviembre de 2024                                               | 93 de lenga; 170 de 220 en ese gránulo                                                                               |
| TP2, 07_Preguntas_y_entrega                                     | Apartados 4.9 y 4.10 de la guía                                                                               | 4.11 y 4.12                                                                                                          |
| TP3, Prompt_IA (verificación)                                   | NDVI 0,19; EVI 0,20; NBR 0,27; NDMI 0,30 y el EVI «todavía sube»                                              | 0,235; 0,215; 0,291; 0,310, y el EVI también se aplana                                                               |
| TP3, objetivos                                                  | Remite a 07_Preguntas_y_entrega\04_Anexos, que no existe                                                      | Remite al anexo de mapas forestales de Chubut                                                                        |
| TP4, LEEME, notas técnicas, ficha SAR y Prompt_IA               | La banda L gana 2,59 dB; R² máximo 0,25; ocho veces mejor que la C                                            | 2,19 dB; 0,276; nueve veces                                                                                          |
| TP4, notas técnicas                                             | Una tabla de contraste asignaba a NISAR y PALSAR-2 los valores del SAOCOM                                     | Las cuatro misiones con sus propias cifras                                                                           |
| TP4, notas técnicas                                             | «Pendiente de datos» las dos SAOCOM de la línea de base                                                       | Están descargadas desde el 16/07/2026; falta procesarlas                                                             |
| TP5, LEEME de 04_Tablas_de_trabajo                              | «Hoy está vacía porque el TP5 todavía no se construyó»                                                        | Describe el dataset que contiene                                                                                     |
| TP5, 00_LEEME                                                   | R² de los otros prácticos (0,19 / 0,20 / 0,25 / 0,27 / 0,30) y «NDVI satura a los 21 m»                       | 0,235 / 0,215 / 0,273 / 0,291 / 0,310 y satura a partir de los 15–18 m                                               |
| 00_LEEME_PRIMERO y GLOSARIO                                     | 250 y 253 GB de descargas; seis cuentas; NDVI satura a los 21 m                                               | 252 GB; siete cuentas; satura a partir de los 15–18 m                                                                |
| REGLAS_DEL_PROYECTO                                             | 09_ATAJOS, los siete .bat                                                                                     | Los nueve .bat                                                                                                       |
| TP4, desarrollo con las respuestas (§ 2.1 y P1)                 | Curva de R² por ventana de una corrida anterior (NISAR 0,152 → 0,245) y «existe un óptimo, y ronda los 150 m» | La corrida actual (NISAR 0,166 → 0,273, y 0,275 a 210 m) y la aclaración de que 150 m es un compromiso, no el máximo |
| Teoría, LEEME de la presentación fusionada (lámina 123)         | NISAR: R² de 0,18 a 30 m y 0,28 a 150 m                                                                       | 0,17 y 0,27                                                                                                          |
| TP1, desarrollo con las respuestas (§ 2.1, § 2.2, P1, P3 y § 5) | «75 productos y 275,9 GB», «quince fuentes», y el 93 % de ALOS-1 atribuido a la verificación del paso 1       | 81 filas y 288,8 GB, o 68 productos únicos y 252,4 GB; catorce fuentes; el 93 % sale de matriz_datos.csv             |
| TP2, desarrollo con las respuestas (§ 1, § 2.1, P1 y P5)        | 6.287 disparos en el bosque; el GeoPackage «del paso 10»; la partición «del paso 8»                           | 6.288 disparos; el GeoPackage es del paso 8 y la partición del paso 7                                                |
| TP3, desarrollo con las respuestas (P5)                         | «el 80,2 % del bosque queda en pie como resultado», que se lee al revés                                       | «la cifra del 80,2 % del bosque quemado queda en pie como resultado»                                                 |

## Parte C bis. Las presentaciones del docente

Las presentaciones que citaban cifras del curso se corrigieron en su texto, sin tocar ninguna lámina, tipografía ni imagen. No se distribuyen a los estudiantes: se listan acá para que quede constancia de qué decían.

| **Presentación**                                     | **Lámina**      | **Decía**                                                                                                          | **Dice ahora**                                                                                    |
|---|---|---|---|
| 10_Conclusiones                                      | 4               | «6.288 disparos válidos de 11.222 sobre los dos recintos»: mezcla los dos recintos y llama válidos a los extraídos | 6.288 en el bosque y 11.222 en la estepa; válidos tras el filtrado, 690 y 3.083                   |
| 10_Conclusiones                                      | 7               | NDVI «satura a los 21 m: 0,896 → 0,894»; NDMI R² 0,30 y RMSE 6,5 m; escena del 9/1 con 0,4 % de nubes              | Se aplana a partir de los 15–18 m (0,888 → 0,879 → 0,897 → 0,893); 0,310 y 5,86 m; 7,4 % de nubes |
| 10_Conclusiones                                      | 10              | Sentinel-1 gana 0,53 dB; R² 0,03                                                                                   | 0,52 dB; R² 0,029                                                                                 |
| 10_Conclusiones                                      | 11              | γ⁰ −12,22 → −11,73 → −11,55 dB; R² 0,25 (0,18 a 30 m, 0,28 a 150 m)                                                | −11,47 → −11,08 → −10,94 dB; R² 0,273 (0,166 a 30 m, 0,273 a 150 m y 0,275 a 210 m)               |
| 10_Conclusiones                                      | 18              | Gradiente espectral de R² 0,03 (C) a 0,25 (L)                                                                      | De 0,029 (C) a 0,273 (L)                                                                          |
| 02_Trabajos_Practicos                                | 17              | «Los siete atajos» y el rótulo «7×»                                                                                | Nueve atajos y «9×»: en 09_ATAJOS hay nueve .bat                                                  |
| 02_Trabajos_Practicos                                | 27              | La escena del 9 de enero «declaraba 0,4 % de nubes»                                                                | 7,4 %                                                                                             |
| 02_Trabajos_Practicos                                | 28              | La banda del incendio: «17.959,2 ha quemadas»                                                                      | 18.009,2 ha (el 80,0 % sí coincide)                                                               |
| 02_Trabajos_Practicos                                | 43              | «El NDVI se aplana a los 21 m de dosel»                                                                            | A partir de los 15–18 m                                                                           |
| 09_Sinergia                                          | 24              | NISAR: R² de 0,18 a 30 m y 0,28 a 150 m                                                                            | 0,17 y 0,27                                                                                       |
| 09_Sinergia                                          | 29 y 59         | CCI Biomass en su versión 6.0: 2007, 2010 y 2015–2022                                                              | Versión 7.0: 2005–2012 y 2015–2024, dieciocho mapas anuales, con el DOI nuevo                     |
| 01_Fundamentos y 05_CCI_Biomass                      | 37 y 26         | La referencia del conjunto de datos CCI, en su versión 6.0                                                         | Versión 7.0, con el DOI nuevo                                                                     |

Los PDF de `01_Teoria\01_Presentaciones_pdf` salieron de esas mismas presentaciones **antes** de la corrección, con una excepción: el de `02_Trabajos_Practicos` está rehecho y lleva las cuatro láminas corregidas, de modo que en él no queda ninguna cifra vieja.

En los otros cuatro sí quedan, y ésta es la referencia mientras tanto. `10_Conclusiones.pdf` conserva las cinco diferencias de sus láminas 4, 7, 10, 11 y 18, tal como figuran en la tabla de arriba: sigue diciendo «6.288 disparos válidos de 11.222», «satura a los 21 m», 0,53 dB, −12,22 → −11,73 → −11,55 dB y el gradiente de 0,03 a 0,25. `09_Sinergia.pdf` sigue dando el R² de NISAR como 0,18 a 30 m y 0,28 a 150 m, cuando son 0,17 y 0,27.

Las otras dos son de la referencia del conjunto de datos CCI Biomass. `01_Fundamentos.pdf` la cita como Santoro y Cartus (2025), con el DOI 10.5285/95913ffb6467447ca72c4e9d8cf30501. `05_CCI_Biomass.pdf` trae la cita nueva pero conserva a su lado la anterior, Santoro y Cartus (2024), v6.0. En los dos casos la que vale es la de la versión 7.0: Santoro, M. y Cartus, O. (2026), doi:10.5285/6429d1aafe1e43b9b414e4a5a7f8b903.

El producto CCI Biomass aparecía descripto y citado en su **versión 6.0** (2007, 2010 y 2015–2022) mientras el curso trabaja con la **7.0**. Se actualizó el 12/09/2026 en las cuatro láminas que lo nombran, con los años correctos y el DOI nuevo, verificado ese día en el catálogo del CEDA: Santoro, M. y Cartus, O. (2026), v7.0, doi:10.5285/6429d1aafe1e43b9b414e4a5a7f8b903. La guía del usuario (PUG) que citan las presentaciones sigue siendo la 6.0, porque no se comprobó que exista una 7.0.

Lo que esta revisión no alcanza: las cifras que estén dibujadas dentro de una imagen o de un gráfico incrustado, porque no son texto.

## Parte D. Lo que queda sin corregir en los PDF

La guía teórico-práctica, las guías sintéticas de cada práctico, el instructivo de ejecución y el desarrollo con las respuestas están en PDF y no se modificaron. Estas son las diferencias que quedan, para tenerlas presentes al leerlos.

| **Documento**                                             | **Qué dice**                                                                                                         | **Qué corresponde**                                                                                                               |
|---|---|---|
| Guía completa, Tabla 11 y pregunta 4 del TP2              | El error de la biomasa del bosque es el 62 % de la mediana; la pregunta dice 87 %                                    | 62 % con las 271 huellas certificadas; 87 % con las 495 que retiene el paso 7, que es la corrida vigente                          |
| Guía completa, §4.6.3, y notas técnicas del TP2           | Pide declarar el umbral de sensibilidad y no lo declara; las notas dicen 0,95                                        | El programa aplica 0,90, con la opción --sensibilidad 0.95                                                                        |
| Guía completa, §4.8, instructivo y guía sintética del TP2 | La mediana del control de terreno queda «a centímetros de cero»                                                      | En el bosque, con el nivel operacional de ATL08, da −1,46 m; la idea es correcta, la cifra no                                     |
| Guía completa, Tablas 18 y 19 del TP3                     | Franja de 15 a 18 m: NDVI 0,886, NDMI 0,337, NBR 0,639, y dos coeficientes                                           | 0,888, 0,339 y 0,643; difieren en centésimas                                                                                      |
| Guía completa, Tablas 26 y 27 del TP4                     | Curva de promediado y contraste con las cifras de una corrida anterior; además la numeración de las tablas se repite | Ver las cifras de la Parte C                                                                                                      |
| Desarrollo (PDF) del TP5                                  | Nada: se auditó cifra por cifra contra las trece tablas del práctico                                                 | Los cinco modelos, la validación por franja, el ensayo nulo, la cadena de error y la validación estricta coinciden con las tablas |
| Guía completa, §6.8 y §6.9 del TP4                        | Enumera seis preguntas y después pide «las respuestas a las cinco preguntas»                                         | Son seis                                                                                                                          |
| Guía completa y desarrollo del TP4                        | Piso de ruido del SAOCOM en la estepa: −29,8 dB, con el 64 % por debajo de −28                                       | La corrida da −29,42 dB; el 64 % no lo produce ningún programa del curso                                                          |
| Guía completa, §7 del TP5                                 | El sesgo por franja alcanza −9,45 m                                                                                  | −9,27 m en la franja de 18 a 21 m                                                                                                 |
| Desarrollo (PDF) del TP2                                  | 6.287 disparos; la partición en el «paso 8»; el gpkg «del paso 10»                                                   | 6.288; la partición es del paso 7 y el GeoPackage del paso 8                                                                      |
| Desarrollo (PDF) del TP1                                  | Inventario de 75 productos y 275,9 GB                                                                                | 81 filas y 288,8 GB, o 68 productos únicos y 252,4 GB (las filas de SAOCOM se repiten por recinto)                                |
| Desarrollo (PDF) del TP4                                  | Curva de promediado con una fila por sensor                                                                          | El programa escribe una fila por fecha, y ninguna reproduce esas cifras                                                           |
| Guías sintéticas del TP2, TP3 y TP4                       | Preguntas, producto a entregar y criterios de evaluación distintos de los de la guía completa                        | Conviene decir en clase cuál rige: el desarrollo responde las de la guía completa                                                 |
| Guía completa, apartados 3.2 y 3.3 | «los siete proveedores» y «Intervienen siete proveedores» | Son ocho: la Tabla 4 los lista, y el párrafo siguiente ya habla de «las ocho fuentes». Corregido en el Word de origen |
| Guía completa y guía sintética del TP4 | No traen el apartado de la fusión de órbitas ascendente y descendente de NISAR ni la séptima pregunta del 6.8 | Están en el Word del 13 de septiembre y en 00_Guia_del_practico\ANEXO_NISAR_fusion_ASC_DES.md |

## Parte E. Una decisión ya tomada y una que queda pendiente

**La ventana de promediado del TP4: resuelto el 12/09/2026.** Los documentos decían que el óptimo está en 150 m «porque maximiza el R²». Con la corrida actual eso no es cierto: en NISAR el máximo cae en los 210 m (0,275) y en PALSAR-2 y en SAOCOM el R² sigue subiendo hasta los 310 m (0,195 y 0,161).

Se mantiene la ventana de 150 m, pero como **compromiso declarado**, no como óptimo: es del orden de la huella de GEDI, y más allá la ventana promedia bosque que ya no pertenece a la huella que se quiere explicar. Y se destaca expresamente, en el desarrollo del TP4, en las notas técnicas, en la verificación del Prompt_IA y en la ficha de sensores SAR, que el R² sigue subiendo más allá de los 150 m: el óptimo numérico y el óptimo defendible no coinciden, y eso se declara en la memoria en lugar de esconderlo.

**Los archivos de Word dentro de un ZIP: resuelto.** El material de BIOMASS banda P que se entrega en TP4_Radar_SAR\07_Preguntas_y_entrega\BIOMASS_bandaP\BIOMASS.zip traía tres archivos .docx, que el filtro por extensión no veía porque están dentro de un ZIP. El ZIP se rehizo con esos tres documentos en PDF (Informe_BIOMASS.pdf, TUTORIAL_paso_a_paso.pdf y Comparativa_SAOCOM_vs_BIOMASS.pdf), y no contiene ningún Word.

## Parte F. Correcciones del 14 de septiembre de 2026

Se hallaron repasando las órdenes del Miniforge práctico por práctico y cotejando cada documento contra los programas que describe. Ninguna cambia una cifra del curso.

De la madrugada:

| **Dónde** | **Decía** | **Dice ahora** |
|---|---|---|
| TP1_01, pie del paso 1 | «(recién ahora, con la verificación hecha, se descarga)», debajo del anuncio del paso siguiente | «(la descarga es el paso 3: antes falta verificar la bruma)» |
| comprobar_entorno.py, cuando falta un paquete | Mandaba a hacer doble clic en EJECUTAR_cadena_escenarioB.bat, que es el atajo del TP5 | «Cuando termine, vuelva a correr este comprobador y siga con el práctico» |
| Los cinco DESARROLLO.md | cd a <práctico>\03_Scripts, desde donde las órdenes escritas no funcionan | cd a 02_Practica, igual que en los cinco documentos de órdenes |
| DESARROLLO.md del TP4, apartado 6.8 | Respondía seis de las siete preguntas de la guía completa | Responde también la séptima, la de la combinación de órbitas ascendente y descendente de NISAR, con las cifras medidas del anexo |

De la noche:

| **Dónde** | **Decía** | **Dice ahora** |
|---|---|---|
| TP1_05, mensaje final | «Ejecutar despues TP1_06_alos_nisar_informe.py para extraer los disparos» | «Ejecutar despues TP2_02_recortar_AOI.py, en el TP2»: TP1_06 informa y descarga ALOS-1 y NISAR, y no extrae ningún disparo |
| TP1, 00_ORDEN_DE_EJECUCION, fila del paso 5 | «Descarga GEDI L2A y L2B (NASA Earthdata)», con destino 08_Originales_crudos\GEDI\ | El programa baja además el ATL08 de ICESat-2, y deja todo bajo el nivel de época: 02_pre\GEDI y 02_pre\ICESat2 |
| TP1, 00_ORDEN_DE_EJECUCION, último apartado | «El séptimo proveedor no tiene script: el SAOCOM» | Son ocho proveedores y dos no tienen programa: la CONAE, por el SAOCOM, y la JAXA, por el mosaico anual de PALSAR-2 |
| TP5, 00_ORDEN_DE_EJECUCION, paso 6 | cd hasta 03_Analisis y después python TP5_06_validacion_estricta.py | cd a 02_Practica y la ruta completa al programa, como en el resto del curso |

Los diez archivos afectados están en la carpeta de archivos corregidos, cada uno con su ruta exacta.

## Parte G. Los recortes de trabajo que faltaban en el repositorio

Ninguna de las tres versiones publicadas (v1.0.0, v1.1.0 y v1.1.1) incluía la carpeta 02_Subsets_SNAP_QGIS de los prácticos: el archivo .gitignore del repositorio la excluía desde la primera versión, y la documentación decía lo contrario. Sin esos recortes no se puede correr el TP2 (los CSV de GEDI y ATL08), el TP3 (los GeoTIFF de Sentinel-2 y Landsat 9), el TP4 (los GeoTIFF en γ⁰ de los cuatro radares y las máscaras) ni el TP5, que lee los de los anteriores. Los estudiantes lo advirtieron el 16 de septiembre, y tenían razón.

Desde la versión 1.2.0 los recortes viajan en el repositorio, en la carpeta 02_Subsets_SNAP_QGIS de cada práctico, y son todos los insumos que leen los programas:

| **Práctico** | **Qué viene** | **Archivos** | **Tamaño** |
|---|---|---|---|
| TP1 | El inventario de lo descargado y las listas de adquisiciones | 4 | 34 KB |
| TP2 | GEDI L2A, L2B y L4A y los segmentos ATL08, en CSV, con su LEEME | 11 | 12,5 MB |
| TP3 | 14 GeoTIFF de Sentinel-2 y 24 de Landsat 9, los tres mapas forestales de Chubut recortados y el LEEME de la escena pre-incendio | 45 | 1.167 MB |
| TP4 | 28 GeoTIFF de Sentinel-1, 6 de SAOCOM, 22 de NISAR (máscaras incluidas) y 6 de PALSAR-2, las tres máscaras de validez, el diccionario de nombres y el material de BIOMASS | 70 | 1.188 MB |
| 00_COMUN | Los dos recortes del CCI Biomass que lee el paso 17 del TP2 | 2 | 1,9 MB |

Lo que sigue sin viajar, y por qué: los pares .dim + .data de SNAP, porque los programas del curso trabajan con los GeoTIFF, que traen las mismas bandas, y los grafos de 08_Grafos_SNAP los rehacen desde la escena original; los recortes con fase de TP4_Radar_SAR\02_Subsets_SNAP_QGIS\00_Recortes_crudos_fase, porque sus archivos superan los 100 MB que admite GitHub (en el aula están en el disco del curso, y sólo hacen falta para la polarimetría con matrices de covarianza); y los rásters de 05_Resultados\02_Rasters, que los programas vuelven a generar, salvo los seis mapas de biomasa del paso 17 del TP2, que sí viajan con su LEEME.

En la misma versión se retiraron del repositorio restos de trabajo que no son material del curso: doce capturas de consola (salida_*.txt) de versiones anteriores de los programas del TP2, cuatro notas del paquete original de ICESat-2 en 05_Resultados\06_Control_calidad\ICESat2_ATL08, dos figuras viejas con sus generadores, en carpetas _ANTES_06ago2026 del TP3 y del TP4, una copia previa de TP5_06_diagnostico_del_piso.py y el archivo .dodsrc del TP1, que apuntaba a una carpeta de la máquina del docente. También se corrigieron, en los LEEME y notas técnicas de los cinco prácticos, los recuentos de archivos y las descripciones de carpetas para que digan lo que el repositorio contiene, y la tabla de GEDI de matriz_datos.csv del TP1, que atribuía las 690 y 3.083 huellas válidas a los filtros de calidad y pendiente cuando la tercera cifra sale después del filtro de estructura del paso 6 (tras calidad y pendiente son 690 y 3.084).

Al preparar esta versión se corrigieron además dos cosas. El paso 5 del TP4, TP4_Radar_SAR\03_Scripts\04_Validacion\efecto_pendiente\TP4_05_mascara_validez.py, leía el ángulo de incidencia local sólo de los productos de SNAP (.dim + .data): sin ellos contestaba «sin productos SAR» y no escribía las máscaras. Ahora lee las mismas bandas del GeoTIFF, y las máscaras de los dos recintos salen idénticas a las que vienen en el repositorio (se descarta el 4,4 % del bosque y el 3,5 % de la estepa). Y el LEEME de TP4_Radar_SAR\07_Preguntas_y_entrega\BIOMASS_bandaP, junto con los textos de BIOMASS.zip, nombraban el tutorial, el informe y la guía de SNAP como archivos .docx, cuando el paquete trae los PDF; ahora dicen .pdf.

## Parte H. Correcciones del 17 de septiembre de 2026, versión 1.2.1

Se encontraron ejecutando los prácticos 3, 4 y 5 de punta a punta sobre la versión 1.2.0, en la notebook del curso, con la salida de cada programa guardada en un archivo.

**H1. TP5, auxiliar de diagnóstico del piso: se corta con UnicodeEncodeError cuando la salida se manda a un archivo.** Archivo: TP5_Sinergia_Multisensor\03_Scripts\03_Analisis\incendio\TP5_06_diagnostico_del_piso.py.

El programa imprime el símbolo Δ en el encabezado de su tabla. En pantalla funciona, pero si la salida se redirige a un archivo (python TP5_06_diagnostico_del_piso.py > salida.txt), Windows la codifica en cp1252, que no tiene ese carácter, y el programa se detiene con «UnicodeEncodeError: 'charmap' codec can't encode character '\u0394'» antes de escribir ninguna tabla. Corregido: al arrancar, el programa fuerza la salida en UTF-8, de modo que corre igual en pantalla y redirigido. No cambia ningún cálculo. Quien tenga la versión 1.2.0 puede escribir set PYTHONUTF8=1 en la consola antes de ejecutarlo, con el mismo efecto.

**H2. Una precisión de lectura sobre el piso de ruido del TP5, que no es un error de programa.** El paso 4 (TP5_04_biomasa_quemada.py) informa un piso de −10,25 Mg/ha sobre la clase «Sin cambio» del bosque, y el auxiliar de diagnóstico informa −5,01 Mg/ha para el mismo juego de predictores (óptico + SAR). Los dos son correctos: el paso 4 usa la media del cambio de biomasa sobre las 87 huellas de esa clase y el auxiliar usa la mediana, y como la distribución es asimétrica los dos estadísticos difieren. Lo que se compara entre ambos es el cociente señal/piso, que da 1,5 en los dos, y la conclusión, que es la misma: sin el EVI el cociente sube a 15,3. El 00_LEEME.md del TP5 cita el −10,25 del paso 4 y el −0,48 del auxiliar, que salen de programas distintos; esta nota lo deja dicho.

**H3. Lo que queda sin corregir en un PDF.** En 00_GUIA_TP3_sintetica.pdf, la Tabla 3.3 nombra 02_Insumos como carpeta de salida de los pasos 1 y 2. Es el nombre anterior de la carpeta que desde la versión 1.2.0 se llama 02_Subsets_SNAP_QGIS; se trata de la misma ubicación. El PDF se rehace con la próxima revisión de las guías.

## Cómo comprobar que quedó aplicado

Después de copiar los archivos, alcanza con correr el paso 1 del TP1 y mirar la columna de nubes: donde antes decía 85,3 % y 99,6 %, tiene que decir 0,0 %. Y el paso 5 del TP3, que debe informar indices_20251125.tif y una tabla de saturación en la que el NDVI llega a 0,888 y después se aplana.

Para la Parte G: en TP3_Datos_Opticos\02_Subsets_SNAP_QGIS\Sentinel_2 tiene que haber 14 GeoTIFF, en TP4_Radar_SAR\02_Subsets_SNAP_QGIS\Sentinel_1 28, y el paso 3 del TP2 tiene que encontrar los CSV de GEDI_L2A y GEDI_L2B sin pedir ninguna descarga.

Los programas corregidos llevan, en el lugar del cambio, un comentario que explica el motivo y la fecha. Nada quedó cambiado en silencio.
