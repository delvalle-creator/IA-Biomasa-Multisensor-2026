# IA Multisensor para Estimar Biomasa en Bosques Andinos y su Ecotono Bosque–Estepa

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22135139.svg)](https://doi.org/10.5281/zenodo.22135139)

> **Fe de erratas.** Antes de usar estos materiales lea
> [`00_FE_DE_ERRATAS.md`](00_FE_DE_ERRATAS.md): qué se corrigió respecto de la
> entrega v1.0.0 y qué diferencias quedan en los PDF que no se rehicieron.

Curso de posgrado — materiales completos: teoría, trabajos prácticos, scripts
y guías de desarrollo con respuestas.

**Autor:** Héctor Francisco del Valle
Centro Regional de Geomática (CeReGeo), Facultad de Ciencia y Tecnología (FCyT), Universidad Autónoma de Entre Ríos (UADER)
Laboratorio de Ecología, Meteorología y Gestión de Fuegos (LEMIV), Facultad de Ingeniería, Universidad Nacional de la Patagonia San Juan Bosco (UNPSJB)

ORCID: [0000-0002-3329-1057](https://orcid.org/0000-0002-3329-1057)

## Qué contiene

- **01_Teoria** — 10 presentaciones en PDF, a dos diapositivas por página: fundamentos, GEDI, ICESat-2 ATLAS, CCI Biomass, ópticos, radares (2 partes), sinergia multisensor y conclusiones.
- **01_Teoria/03_Lecturas** — material de lectura: *The SAR Handbook* (SERVIR/NASA, 2019), cuya licencia autoriza el uso educativo, y el listado `00_MATERIAL_DE_LECTURA.md` con la cita y el enlace oficial de las guías de usuario de GEDI e ICESat-2 ATL08 y del tutorial de sinergia Sentinel-1/Sentinel-2 de ESA.
- **02_Practica** — cinco trabajos prácticos (TP1 Búsqueda IA, TP2 LiDAR GEDI/ICESat-2, TP3 Datos ópticos, TP4 Radar SAR, TP5 Sinergia multisensor), con sus recortes de trabajo (`02_Subsets_SNAP_QGIS`), scripts Python, guías paso a paso, procedimientos con resultados y la guía integral de desarrollo y respuestas (`11_Desarrollo_y_respuestas`).
- **00_FE_DE_ERRATAS.md** y **00_FE_DE_ERRATAS.pdf** — qué se corrigió respecto de la entrega v1.0.0.
- **00_INSTRUCTIVO_DE_EJECUCION.pdf** y **00_LEEME_PRIMERO.md** — por dónde empezar.

## Qué no contiene, y por qué

Este repositorio **no distribuye ningún archivo de Word ni de PowerPoint**. Todo lo que el
estudiante lee viaja en PDF o en markdown. La regla vale también para las fuentes de las
figuras y de las presentaciones, y está escrita en el `.gitignore` para que no dependa de
acordarse.

Tampoco viajan los datos crudos, los productos de SNAP (pares `.dim` + `.data`), los
rásters de resultados que los programas vuelven a generar, ni los artículos de terceros: de
estos últimos van la lista de referencias con sus DOI y el archivo `.ris`. La única obra de
terceros incluida es *The SAR Handbook*, porque su licencia autoriza reproducirla con fines
educativos citando la fuente.

## Caso de estudio

Dos recintos de 15 × 15 km en el noroeste de Chubut (Patagonia, Argentina):
bosque andino incendiado entre el 10/01 y el 27/02 de 2026 (BOSQUE_NW_02) y
ecotono de estepa como control (ESTEPA_NW_02). Grilla única EPSG:32719,
píxel de 10 m. La referencia es satelital (GEDI): toda conclusión se declara
estimación sobre estimación.

## Software

Miniforge (Python), SNAP (ESA), QGIS y Orange Data Mining (3.39/3.40).

## Datos

**Los recortes de trabajo de los prácticos viajan en el repositorio** (2,4 GB), en
la carpeta `02_Subsets_SNAP_QGIS` de cada TP: 14 GeoTIFF de Sentinel-2 y 24 de
Landsat 9 (TP3); 28 GeoTIFF de Sentinel-1, 6 de SAOCOM, 22 de NISAR (máscaras
incluidas) y 6 de PALSAR-2, más las máscaras de validez (TP4); los disparos de GEDI L2A, L2B y L4A
y los segmentos ATL08 de ICESat-2, en CSV (TP2); el inventario (TP1), y los dos
recortes del CCI Biomass que usa el paso 17 del TP2. Son todos los insumos que
leen los programas, y ninguno supera los 100 MB.

Los datos crudos originales (unos 252 GB: Sentinel-1/2, Landsat 9, SAOCOM,
ALOS PALSAR-1/2, NISAR, BIOMASS, GEDI, ICESat-2), los productos de SNAP (pares
`.dim` + `.data`, que se rehacen con los grafos de `08_Grafos_SNAP`) y los
recortes con fase de `TP4_Radar_SAR/02_Subsets_SNAP_QGIS/00_Recortes_crudos_fase`
(archivos de más de 100 MB) no se distribuyen en este repositorio; el
instructivo de ejecución y los scripts de descarga de cada TP documentan cómo
obtenerlos de sus proveedores.

## Uso en otra área de estudio

Ver `02_Practica/00_COMUN/COMO_CAMBIAR_DE_AREA.md`: qué editar en
`configuracion_comun.py` (EPSG, AOIs, épocas), qué datos rehacer y qué
revisar a mano.

## Licencia y cita

Material bajo licencia **CC BY-NC-SA 4.0** (ver `LICENSE.md`). Las obras de
terceros de `01_Teoria/03_Lecturas` conservan su propia licencia.

Para citar este curso, ver `CITATION.cff`. El curso está archivado en Zenodo:

| DOI | Qué identifica |
|---|---|
| [10.5281/zenodo.22135139](https://doi.org/10.5281/zenodo.22135139) | La obra, en todas sus versiones. Lleva siempre a la más reciente y es el que conviene usar para citar el curso. |
| Versión 1.2.0 | El DOI figura en su página de Zenodo (Zenodo lo asigna al publicar el release) |
| [10.5281/zenodo.22792401](https://doi.org/10.5281/zenodo.22792401) | Versión 1.1.1 |
| [10.5281/zenodo.22781888](https://doi.org/10.5281/zenodo.22781888) | Versión 1.1.0 |
| [10.5281/zenodo.22135140](https://doi.org/10.5281/zenodo.22135140) | Versión 1.0.0 |

Cada versión tiene su propio DOI, que figura en su página de Zenodo.
