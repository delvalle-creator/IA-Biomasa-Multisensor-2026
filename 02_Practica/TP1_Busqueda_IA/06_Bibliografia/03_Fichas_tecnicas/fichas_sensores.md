# Fichas técnicas de los sensores del proyecto

| Sensor | Tipo | Banda / λ | Píxel | Revisita | Qué aporta |
|---|---|---|---|---|---|
| **Sentinel-2 MSI** | óptico | 13 bandas, 490–2190 nm | 10–20 m | 5 días | Índices, dNBR del incendio |
| **Landsat 9 OLI-2** | óptico | 11 bandas | 30 m | 16 días | Árbitro independiente, serie histórica desde 1972 |
| **Sentinel-1 SAR** | radar | C, 5,6 cm | 10 m | 12 días | Serie densa. Control negativo: no ve biomasa |
| **SAOCOM-1** | radar | L, 24 cm | 10 m | 16 días | Banda L argentina. Único con polarimetría completa |
| **NISAR** | radar | L, 24 cm (+ S, 9,8 cm) | 10 m | 12 días | Banda L reciente, ya geocodificada y corregida |
| **PALSAR-2 mosaico** | radar | L, 24 cm | 25 m | anual | Continuidad interanual, ya corregido |
| **BIOMASS** | radar | P, 70 cm | 50–60 m (L1) | 3 días / 17 | Penetra hasta troncos. **Aún sin producto de biomasa** |
| **GEDI** | LiDAR | 1064 nm | huella 25 m | muestreo | La referencia de altura del dosel |

## Detalles que importan y no están en las tablas de folleto

**NISAR lleva DOS radares, y no siempre transmiten juntos.** Adquiere en modo
L-only, S-only o conjunto. Nuestros gránulos son L-only: `radarBand = 'L'`, y
dentro del archivo sólo existe el grupo `/science/LSAR`. La banda S la distribuye
ISRO por Bhoonidhi, no la NASA por ASF.

**`frequencyA` y `frequencyB` de NISAR son las dos banda L**, con distinto ancho de
banda: A sale a 10 m de píxel y B a 80 m. No son L y S. El código `DHDH` del nombre
de archivo es la polarización de esas dos frecuencias.

**La nubosidad del catálogo es de la escena entera** (110 × 110 km en Sentinel-2).
Nuestro AOI mide 15 × 15 km. Son dos números distintos.

**La huella del catálogo no es el dato.** Una franja de radar es un rectángulo
inclinado inscripto en una grilla rectangular: las esquinas están vacías.

## El nivel de un producto no es lo mismo que su fecha de publicación

Un catálogo puede ofrecer una colección cuyo contenido todavía no existe, o que
está reservado a los equipos de la misión. **Conocer un sensor incluye conocer su
calendario**, y volver a mirarlo cada tanto: lo que hoy no se puede usar puede
estar disponible en la próxima edición del curso.

El caso testigo es **BIOMASS**, y conviene tenerlo presente porque es la misión que
más promete para este tema. Verificado el 31/07/2026 contra el anuncio oficial:

| Producto | Publicación | Estado a julio de 2026 |
|---|---|---|
| Niveles 1A, 1B y 1C | ya publicados | acceso libre |
| **Nivel 2A — altura de bosque** | **30/06/2026** | **acceso libre** |
| Nivel 2A — perturbación forestal | abril 2027 | no existe |
| **Nivel 2B — altura y biomasa (AGB)** | **mayo 2027** | no existe; hoy interno |
| Nivel 2B — perturbación forestal | diciembre 2027 | no existe |

Es decir: **la biomasa de la misión llamada BIOMASS no existirá antes de mayo de
2027.** El nombre de la misión no es el nombre del producto disponible.

Y hay un giro que conviene subrayar: **para este trabajo, la altura vale más que la
biomasa, y ya está publicada.** La cadena del TP5 estima altura de dosel; la
biomasa aparece después, por una alometría de exponente ≈ 2,6 que amplifica
cualquier error —un metro de sesgo sobre un dosel de nueve se vuelve más de diez
Mg/ha—. Una altura derivada de banda P validaría la magnitud que el modelo estima
de verdad, antes de esa amplificación, que es donde hoy no hay ningún control
externo.

## Una escena puede estar en el catálogo, decir «L2A», y no servir

El 09/01/2026 hay una escena Sentinel-2C sobre el bosque, catalogada como producto
de reflectancia de superficie. **Su corrección atmosférica falló.** El visible
quedó inflado entre cuatro y seis veces —azul 0,1528 contra 0,0235 de una escena
sana— mientras el NIR y los SWIR quedaron iguales: la firma de la dispersión no
removida. Consecuencias medidas: NDVI de 0,38 sobre bosque cerrado, y la banda de
clasificación etiquetando el 78 % del recinto como «suelo desnudo».

Se detectó **cruzando sensores**: Landsat 9 del 04/01/2026, cinco días antes, da
NDVI 0,85 sobre el mismo bosque no quemado, igual que las escenas sanas de
Sentinel-2B de noviembre y marzo. Dos sensores independientes separados por cinco
días no difieren en 0,47 de NDVI.

De ahí el valor real de tener un segundo sensor óptico en el proyecto: **Landsat 9
no está para aportar resolución —tiene 30 m contra 10— sino para arbitrar.** El
detalle completo está en el LEEME de
`TP3_Datos_Opticos/02_Subsets_SNAP_QGIS/Sentinel_2/02_pre_incendio_2025_26/`.
