# Ficha técnica — los sensores ópticos del TP3

| | Sentinel-2 MSI | Landsat 9 OLI-2 |
|---|---|---|
| **Agencia** | ESA | NASA / USGS |
| **Píxel** | 10 m (VIS/NIR), 20 m (SWIR) | 30 m |
| **Bandas** | 13 | 11 |
| **Revisita** | 5 días (2 satélites) | 16 días |
| **Archivo desde** | 2015 | **1972** (serie Landsat) |
| **Ancho de franja** | 290 km | 185 km |

## Las bandas que usa este práctico

| Banda S2 | λ (nm) | Para qué |
|---|---|---|
| B2 azul | 492 | **Detectar bruma**: los aerosoles la inflan |
| B4 rojo | 665 | NDVI, EVI. La clorofila lo absorbe |
| B8 NIR | 833 | NDVI, EVI, NDMI, NBR. La estructura de la hoja lo dispersa |
| B11 SWIR1 | 1610 | NDMI. El agua de la hoja lo absorbe |
| B12 SWIR2 | 2190 | NBR. Sube con la ceniza |
| SCL | — | Máscara de nubes del producto |

## Los índices

| Índice | Fórmula | Satura |
|---|---|---|
| NDVI | (NIR − Rojo) / (NIR + Rojo) | ~21 m de dosel (medido acá) |
| EVI | 2,5 · (NIR − Rojo) / (NIR + 6·Rojo − 7,5·Azul + 1) | más tarde |
| NDMI | (NIR − SWIR1) / (NIR + SWIR1) | — |
| NBR | (NIR − SWIR2) / (NIR + SWIR2) | — |

## Lo que hay que tener presente

**Un píxel remuestreado no gana resolución.** Los Landsat 9 de este proyecto están
remuestreados a 10 m para compartir la grilla común, pero **su resolución real
sigue siendo 30 m**. Están los dos archivos, el nativo y el remuestreado, para que
lo compruebe.

**La nubosidad del catálogo es de la escena entera** (110 × 110 km). Su AOI mide
15 × 15 km.

**La SCL no ve la bruma.** Detecta objetos opacos con bordes. La bruma es un velo.
