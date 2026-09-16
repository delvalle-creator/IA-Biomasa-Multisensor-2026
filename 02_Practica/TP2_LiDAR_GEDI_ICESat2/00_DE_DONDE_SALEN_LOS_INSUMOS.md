# De dónde salen los insumos de este práctico

Las tres carpetas se llaman como lo que contienen, y conviene no confundirlas.

| Carpeta | Qué hay | Quién la escribe |
|---|---|---|
| `02_Subsets_SNAP_QGIS` | Los recortes de trabajo, en CSV: los disparos de GEDI L2A, L2B y L4A y los segmentos ATL08, ya recortados a los dos recintos. **Es sobre esto que se trabaja en clase, y vienen en el repositorio.** | Los programas del práctico |
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
| `CCI_BIOMASS` | Los recortes del mapa mundial de biomasa CCI v7 (2005-2024), para el anexo y el paso 17 |
| `FABDEM` | La tesela S43W072 del suelo desnudo FABDEM V1-2 (Univ. Bristol), auditor del terreno del paso 15 |
| `GEOIDES` | Las grillas EGM2008 (NGA) y GEOIDE-Ar16 (IGN) de las que salen los recortes de `00_COMUN\03_Topografia\GEOIDES` |

Le corresponden `02_pre\GEDI` (38 gránulos, 24,6 GB) y `02_pre\GEDI_L4A`
(19 archivos, 2,6 GB).

Son 252 GB en total y no viajan en el repositorio, salvo los dos recortes del
CCI Biomass (2 MB) que lee el paso 17: en el aula están en el disco del curso.
Se trabaja siempre sobre los recortes de `02_Subsets_SNAP_QGIS`, que sí viajan,
pesan poco y permiten repetir una cadena entera en minutos. El original queda
como respaldo y como prueba: si un recorte resulta dudoso, se vuelve a él y se
comprueba.
