# Manuales y documentación oficial — TP2

## Productos GEDI

- **GEDI L2A** — Elevation and Height Metrics. Es de donde salen las métricas rh
  (rh25, rh50, rh75, rh95, rh98) y el indicador de calidad.
  https://lpdaac.usgs.gov/products/gedi02_av003/
- **GEDI L2B** — Canopy Cover and Vertical Profile Metrics. De acá salen `cover`,
  `pai` y `fhd_normal`.
  https://lpdaac.usgs.gov/products/gedi02_bv003/
- **GEDI L4A** — Aboveground Biomass Density. El producto de biomasa con su
  intervalo de predicción por disparo.
  https://daac.ornl.gov/cgi-bin/dsviewer.pl?ds_id=2056

## Lo que hay que leer antes de filtrar

El **User Guide del L2A** es el documento que define qué significa cada bandera
de calidad. Léalo antes de usar `l2a_quality_flag_rel3`: la V003 renombró las
variables respecto de versiones anteriores, y un filtro que busca el nombre viejo
no falla, simplemente no filtra.

## Acceso

- **NASA Earthdata Login** (gratuito, obligatorio): https://urs.earthdata.nasa.gov/
- **earthaccess** — la biblioteca de Python que usan los scripts 01 y 02:
  https://earthaccess.readthedocs.io/

## Modelo de elevación

- **Copernicus GLO-30 DEM**, 30 m, global:
  https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model
