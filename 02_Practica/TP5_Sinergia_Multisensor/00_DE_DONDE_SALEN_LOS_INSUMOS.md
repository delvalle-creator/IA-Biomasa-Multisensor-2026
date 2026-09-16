# De dónde salen los insumos de este práctico

Las tres carpetas se llaman como lo que contienen, y conviene no confundirlas.

| Carpeta | Qué hay | Quién la escribe |
|---|---|---|
| `02_Subsets_SNAP_QGIS` | Este práctico no la tiene: lee los recortes en GeoTIFF y CSV de los otros cuatro prácticos, que vienen en el repositorio | — |
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

Este práctico **no descarga ni pre-procesa nada**: consume lo que dejaron los
cuatro anteriores en sus `02_Subsets_SNAP_QGIS`, `04_Tablas_de_trabajo` y
`05_Resultados`. Por eso no tiene `02_Subsets_SNAP_QGIS`.

Son 252 GB en total y no viajan en el repositorio: en el aula están en el disco
del curso. Se trabaja siempre sobre los recortes de `02_Subsets_SNAP_QGIS` de
cada práctico, que sí viajan y permiten repetir una cadena entera en minutos. El
original queda como respaldo y como prueba: si un recorte resulta dudoso, se
vuelve a él y se comprueba.
