# Orden de ejecucion de los scripts del TP1

Los scripts se ejecutan en el orden de su numero (TP1_01 -> TP1_10). Las
subcarpetas estan numeradas 1_, 2_, 3_ para que ese orden se vea de un vistazo.
Las carpetas `funciones/` y `configuracion/` son de APOYO (no son pasos): las
importan los scripts.

**Regla del practico: verificar antes de descargar.**

| Paso | Script | Subcarpeta | Que hace | Deja / produce |
|---|---|---|---|---|
| 1 (primero) | TP1_01_verificar_cobertura.py | 01_Consulta_catalogos | Compara la huella del catalogo con los pixeles con dato reales | 05_Resultados/04_Tablas/verificacion_cobertura.csv |
| 2 | TP1_02_detectar_bruma.py | 01_Consulta_catalogos | Detecta bruma/humo por la reflectancia del azul | 05_Resultados/04_Tablas/deteccion_bruma.csv |
| 3 | TP1_03_descargar_sentinel.py | 01_Consulta_catalogos | Descarga Sentinel-1 y Sentinel-2 (Copernicus) | 00_COMUN/08_Originales_crudos/ |
| 4 | TP1_04_descargar_landsat.py | 01_Consulta_catalogos | Descarga Landsat 9 C2 L2 recortado al AOI (Planetary Computer) | 00_COMUN/08_Originales_crudos/.../LANDSAT9/ |
| 5 | TP1_05_descargar_gedi.py | 01_Consulta_catalogos | Descarga GEDI L2A y L2B (NASA Earthdata) | 00_COMUN/08_Originales_crudos/GEDI/ |
| 6 | TP1_06_alos_nisar_informe.py | 02_Disponibilidad_imagenes | Informa y descarga ALOS-1 (quad-pol) y NISAR (ASF) | 00_COMUN/08_Originales_crudos/ |
| 7 | TP1_07_descargar_nisar.py | 02_Disponibilidad_imagenes | Descarga NISAR GCOV con verificacion de integridad | 00_COMUN/08_Originales_crudos/.../NISAR/GCOV/ |
| 8 | TP1_08_descargar_biomass.py | 02_Disponibilidad_imagenes | Descarga BIOMASS banda P (ESA MAAP, requiere token) | 00_COMUN/08_Originales_crudos/.../BIOMASS/ |
| 9 | TP1_09_inventario.py | 03_Exportacion_inventario | Inventario de todo lo descargado | 02_Subsets_SNAP_QGIS/03_Tablas/inventario.csv |
| 10 (ultimo) | TP1_10_reconstruir_diccionario.py | 03_Exportacion_inventario | Reconstruye el diccionario de nombres cortos | diccionario_nombres.csv |

Primero se VERIFICA (pasos 1-2), recien despues se DESCARGA (pasos 3-8), y al
final se DOCUMENTA lo obtenido (pasos 9-10).

## El septimo proveedor no tiene script: el SAOCOM

Los pasos 3 a 8 cubren seis de los siete proveedores del curso. Falta la CONAE,
que distribuye el SAOCOM-1A y 1B. **No hay script y no es un olvido:** el
catalogo de la CONAE (https://catalogos.conae.gov.ar/) no entrega los productos
por descarga directa, sino que exige registro, solicitud y autorizacion previas,
y la entrega llega despues por un enlace personal.

Ese tramite esta documentado en
`00_COMUN/08_Originales_crudos/PEDIDO_SAOCOM_28jul2026.md`, que es el pedido real
con el que se obtuvieron las escenas del proyecto. Conviene leerlo: la habilidad
que este practico ensena, la de pedirle a un catalogo exactamente lo que se
necesita, se ve mejor en un tramite con persona del otro lado que en una descarga
automatica.

Las escenas ya estan en el disco del curso, en
`00_COMUN/08_Originales_crudos/01_base/SAOCOM`, `02_pre/SAOCOM` y
`03_post/SAOCOM`, y se procesan en el Trabajo Practico 4.
