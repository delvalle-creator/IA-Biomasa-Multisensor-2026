# Manuales y documentación oficial — TP3

## Productos

- **Sentinel-2 L2A** (reflectancia de superficie): https://sentiwiki.copernicus.eu/web/s2-products
- **Landsat 9 Collection 2 Level-2**: https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products

## Lo que hay que leer antes de filtrar nubes

El **Sentinel-2 Product Guide**, sección de la banda **SCL** (Scene
Classification Layer): define qué significa cada valor de 0 a 11. Es lo que
permite entender por qué la clase 10 (cirros) casi nadie la filtra, y por qué la
bruma no tiene clase propia.

Clases que este práctico descarta: 0 (sin dato), 1 (saturado), 3 (sombra de nube),
8 y 9 (nube media y alta probabilidad), 10 (cirros), 11 (nieve).

## Herramientas

- **SNAP** (recorte y remuestreo de Sentinel-2): https://step.esa.int/main/download/snap-download/
- **QGIS**: https://qgis.org/
- **Planetary Computer** (lectura de ventanas COG sin descargar la escena):
  https://planetarycomputer.microsoft.com/docs/

## Un detalle de formato que importa

Los productos están en **COG** (Cloud Optimized GeoTIFF). Eso permite leer sólo la
ventana del AOI sin bajar la escena entera de 1 GB. Es lo que hace el script
`TP1_01` para verificar cobertura antes de descargar.
