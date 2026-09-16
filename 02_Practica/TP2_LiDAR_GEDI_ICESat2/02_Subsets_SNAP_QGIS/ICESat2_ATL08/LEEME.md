# ICESat-2 / ATLAS — producto ATL08, recortado a los dos recintos

Estos cuatro archivos son **insumo, no resultado**: llegan ya extraídos de los
`.h5` y recortados a `BOSQUE_NW_02` y `ESTEPA_NW_02`. Se trabaja sobre ellos igual
que sobre los recortes de GEDI de las carpetas vecinas.

## Qué es un segmento ATL08

ATL08 no entrega huellas: entrega **segmentos de 100 m a lo largo de la traza**,
uno por cada haz. GEDI entrega huellas de 25 m de diámetro. **No son la misma
unidad y no se comparan de a una**: para cotejarlos hay que agregar, y esa es
justamente la primera decisión del cotejo.

Cada segmento trae la altura del terreno (`h_te_best_fit_m`) y la altura del dosel
por encima de ese terreno (`h_canopy_m`).

## Los cuatro archivos

| Archivo | Recinto | Nivel | Segmentos |
|---|---|---|---|
| `ATL08_BOSQUE_operacional.csv` | BOSQUE_NW_02 | operacional | 1.949 |
| `ATL08_BOSQUE_conservador.csv` | BOSQUE_NW_02 | conservador | 905 |
| `ATL08_ESTEPA_operacional.csv` | ESTEPA_NW_02 | operacional | 1.923 |
| `ATL08_ESTEPA_conservador.csv` | ESTEPA_NW_02 | conservador | 1.482 |

**Operacional** exige: altura válida, fotones de copa y de terreno, suelo sin
nieve, `cloud_flag_atm = 0`, `msw_flag = 0` y `terrain_flg = 0`.

**Conservador** agrega un requisito: que estén disponibles las incertidumbres de
copa y de terreno. Lea con cuidado el apartado del sesgo en
`../../NOTAS_TECNICAS_ICESat2.md` antes de usar este nivel: **no es «más calidad»,
es otra población**.

## Las columnas que importan

| Columna | Qué es |
|---|---|
| `h_canopy_m` | Altura relativa del dosel al percentil 98 sobre el terreno estimado. Es el **RH98** de la literatura |
| `h_max_canopy_m` | Altura relativa máxima. Es el **RH100** |
| `h_te_best_fit_m` | Altura del terreno ajustada |
| `h_canopy_uncertainty_m`, `h_te_uncertainty_m` | Incertidumbres. Su **disponibilidad** define el nivel conservador |
| `canopy_openness_m` | Dispersión vertical de los fotones de copa |
| `n_ca_photons`, `n_te_photons` | Fotones de copa y de terreno del segmento |
| `segment_landcover`, `landcover_label` | Clase de cobertura del segmento |
| `night_flag` | 1 de noche. La adquisición nocturna tiene menos ruido solar |
| `beam` | `gt1l`…`gt3r`. Tres pares, uno fuerte y uno débil por par |
| `granule`, `rgt`, `cycle`, `acquisition_datetime` | Identificación de la adquisición |
| `qa_valid_height`, `qa_operational`, `qa_conservative` | Los filtros ya evaluados |

## Tres advertencias antes de escribir una línea de código

1. **Las columnas `rh50_m` a `rh100_m` están vacías.** El extractor no leyó
   `canopy_h_metrics`. Use `h_canopy_m` y `h_max_canopy_m`, que sí están y
   equivalen a RH98 y RH100. Un script que promedie `rh95_m` no da error: da nada.
2. **Faltan campos de calidad del producto**: no están `can_quality_score`,
   `te_quality_score`, `layer_flag`, `dem_removal_flag` ni `canopy_rh_conf`. La
   evaluación de calidad que se puede hacer con estos CSV es, por eso, parcial.
3. **Los segmentos contiguos no son observaciones independientes.** Comparar
   1.949 contra 1.923 segmentos como si lo fueran infla la significación. Las
   comparaciones del práctico se hacen sobre **medianas por gránulo**.

## De dónde salen

Paquete `ICESat2_ATLAS_BOSQUE_ESTEPA_CORREGIDO.zip`, producto **ATL08 V007**,
consulta del 14/10/2018 al 18/08/2026. El registro de auditoría del paquete está
en `05_Resultados/06_Control_calidad/ICESat2_ATL08/`.
