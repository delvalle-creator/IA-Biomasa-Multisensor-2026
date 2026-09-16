# De dónde salen los insumos de este práctico

Las tres carpetas se llaman como lo que contienen, y conviene no confundirlas.

| Carpeta | Qué hay | Quién la escribe |
|---|---|---|
| `02_Subsets_SNAP_QGIS` | Los recortes de trabajo en GeoTIFF: γ⁰ de Sentinel-1, SAOCOM, NISAR y PALSAR-2 en la grilla común, más las máscaras. **Es sobre esto que se trabaja en clase, y vienen en el repositorio.** Los pares `.dim` + `.data` de SNAP y los recortes con fase de `00_Recortes_crudos_fase` no viajan: los primeros se rehacen con los grafos y los segundos superan los 100 MB por archivo | Los programas del práctico |
| `04_Tablas_de_trabajo` | Las tablas `.csv` intermedias: muestras, datos de entrenamiento y de validación | Los programas del práctico |
| `05_Resultados` | Lo que sale: rásteres, vectores, tablas y gráficos | Los programas del práctico |

## Las imágenes originales no están aquí

Las descargas sin procesar —los `.zip`, los `.h5` de GEDI, los `.xemt` del
SAOCOM— **no se guardan en el práctico**, porque una misma escena sirve a más de
uno y no tiene sentido tener cinco copias que con el tiempo dejan de coincidir.
Están todas juntas en:

```
02_Practica\00_COMUN\08_Originales_crudos\
```

organizadas por época y por recinto:

| Subcarpeta | Qué época |
|---|---|
| `00_alos` | ALOS PALSAR, banda L, la serie histórica |
| `01_base` | La línea de base 2023-2024 |
| `02_pre` | Anterior al incendio, 2025-2026 |
| `03_post` | Posterior al incendio |

Le corresponden `00_alos` (ALOS PALSAR, 13,4 GB), `01_base\SAOCOM` y
`02_pre\SAOCOM` y `03_post\SAOCOM` (34 GB en total), `02_pre\NISAR` (30,5 GB),
los mosaicos `PALSAR2_MOSAIC` y `03_post\BIOMASS_bandaP` (27 productos, 6,4 GB),
más las escenas de Sentinel-1 de cada recinto.

Son 252 GB en total y no viajan en el repositorio: en el aula están en el disco
del curso. Se trabaja siempre sobre los recortes de `02_Subsets_SNAP_QGIS`, que
sí viajan (1,2 GB en este práctico) y permiten repetir una cadena entera en
minutos. El original queda como respaldo y como prueba: si un recorte resulta
dudoso, se vuelve a él y se comprueba.
