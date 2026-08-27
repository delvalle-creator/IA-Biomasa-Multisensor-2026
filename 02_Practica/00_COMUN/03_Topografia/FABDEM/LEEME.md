# FABDEM — el suelo desnudo que audita a las dos misiones LiDAR

**FABDEM V1-2** (Universidad de Bristol) es un modelo global de elevación de
30 m construido sobre el Copernicus GLO-30 al que se le removieron **bosques y
edificios** con aprendizaje automático. Donde el GLO-30 del curso
(`../DEM/dem_*.tif`) ve la *superficie* (copas incluidas), FABDEM estima el
*terreno*. Esa diferencia es la que lo vuelve útil acá: es un suelo desnudo
independiente de GEDI y de ICESat-2, y por eso puede auditar el terreno que
cada misión creyó detectar (`TP2_15_control_terreno_FABDEM.py`).

| Archivo | Recinto | Origen |
|---|---|---|
| `fabdem_BOSQUE_NW_02_wgs84.tif` | bosque | recorte de la tesela S43W072 |
| `fabdem_ESTEPA_NW_02_wgs84.tif` | estepa | recorte de la tesela S43W072 |

Recortes en EPSG:4326 con ~1,3 km de margen alrededor de cada recinto (cubre
el efecto de borde de los segmentos ATL08 de 100 m). La tesela completa y su
zip de origen quedan en `../../08_Originales_crudos/FABDEM/`.

**Datum vertical: ortométrico EGM2008.** Las alturas satelitales del TP2 son
elipsoidales WGS84; para comparar hay que sumar la ondulación del geoide
(`../GEOIDES/`). El paso 15 lo hace y lo declara.

**FABDEM audita, nunca corrige**: no se resta a ninguna altura ni reemplaza a
ningún terreno medido. Un segmento que no pasa el control se descarta con
criterio declarado, y eso es todo.

Fuente: Hawker et al. (2022), *A 30 m global map of elevation with forests and
buildings removed*, Environ. Res. Lett. 17, 024016. Licencia
**CC BY-NC-SA 4.0** (la misma del curso). Descarga:
https://data.bris.ac.uk/data/dataset/s5hqmjcdj8yo2ibzi9b4ew3sn
