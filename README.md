# IA Multisensor para Estimar Biomasa en Bosques Andinos y su Ecotono Bosque–Estepa

Curso de posgrado — materiales completos: teoría, trabajos prácticos, scripts
y guías de desarrollo con respuestas.

**Autor:** Héctor Francisco del Valle
Centro Regional de Geomática (CeReGeo), Facultad de Ciencia y Tecnología (FCyT), Universidad Autónoma de Entre Ríos (UADER)
Laboratorio de Ecología, Meteorología y Gestión de Fuegos (LEMIV), Facultad de Ingeniería, Universidad Nacional de la Patagonia San Juan Bosco (UNPSJB)

ORCID: [0000-0002-3329-1057](https://orcid.org/0000-0002-3329-1057)

## Qué contiene

- **01_Teoria** — 10 presentaciones (PDF, 2 diapositivas por página) y sus fuentes pptx: fundamentos, GEDI, ICESat-2 ATLAS, CCI Biomass, ópticos, radares (2 partes), sinergia multisensor y conclusiones.
- **02_Practica** — cinco trabajos prácticos (TP1 Búsqueda IA, TP2 LiDAR GEDI/ICESat-2, TP3 Datos ópticos, TP4 Radar SAR, TP5 Sinergia multisensor), con scripts Python, guías paso a paso, procedimientos con resultados y la guía integral de desarrollo y respuestas (`11_Desarrollo_y_respuestas`).
- **00_INSTRUCTIVO_DE_EJECUCION.pdf** y **00_LEEME_PRIMERO.md** — por dónde empezar.

## Caso de estudio

Dos recintos de 15 × 15 km en el noroeste de Chubut (Patagonia, Argentina):
bosque andino incendiado entre el 10/01 y el 27/02 de 2026 (BOSQUE_NW_02) y
ecotono de estepa como control (ESTEPA_NW_02). Grilla única EPSG:32719,
píxel de 10 m. La referencia es satelital (GEDI): toda conclusión se declara
estimación sobre estimación.

## Software

Miniforge (Python), SNAP (ESA), QGIS y Orange Data Mining (3.39/3.40).

## Datos

Los datos crudos originales (~260 GB: Sentinel-1/2, Landsat 9, SAOCOM,
ALOS PALSAR-1/2, NISAR, BIOMASS, GEDI, ICESat-2, CCI Biomass) y los
productos intermedios pesados de SNAP no se distribuyen en este repositorio;
el instructivo de ejecución y los scripts de descarga de cada TP documentan
cómo obtenerlos de sus proveedores.

## Uso en otra área de estudio

Ver `02_Practica/00_COMUN/COMO_CAMBIAR_DE_AREA.md`: qué editar en
`configuracion_comun.py` (EPSG, AOIs, épocas), qué datos rehacer y qué
revisar a mano.

## Licencia y cita

Material bajo licencia **CC BY-NC-SA 4.0** (ver `LICENSE.md`).
Para citar este curso, ver `CITATION.cff` — versión archivada con DOI en Zenodo.
