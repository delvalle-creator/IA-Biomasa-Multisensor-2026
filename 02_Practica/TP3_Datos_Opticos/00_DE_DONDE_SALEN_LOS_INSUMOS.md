# De dónde salen los insumos de este práctico

Las tres carpetas se llaman como lo que contienen, y conviene no confundirlas.

| Carpeta | Qué hay | Quién la escribe |
|---|---|---|
| `02_Subsets_SNAP_QGIS` | Los recortes de trabajo, en GeoTIFF: 14 escenas de Sentinel-2 y 24 archivos de Landsat 9, ya recortados a la grilla común de los dos recintos. **Es sobre esto que se trabaja en clase, y vienen en el repositorio.** Los pares `.dim` + `.data` que también escribe el paso 1 no viajan: los programas leen los GeoTIFF | Los programas del práctico |
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

Le corresponden las escenas ópticas de `01_base`, `02_pre` y `03_post` dentro de
`BOSQUE_NW_02` y `ESTEPA_NW_02`, que son las de Sentinel-2 y Landsat.

Son 252 GB en total y no viajan en el repositorio: en el aula están en el disco
del curso. Se trabaja siempre sobre los recortes de `02_Subsets_SNAP_QGIS`, que
sí viajan (1,2 GB en este práctico) y permiten repetir una cadena entera en
minutos. El original queda como respaldo y como prueba: si un recorte resulta
dudoso, se vuelve a él y se comprueba.
