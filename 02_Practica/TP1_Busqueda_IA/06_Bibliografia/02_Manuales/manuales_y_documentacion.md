# Manuales y documentación oficial — TP1

## Catálogos que se consultan en el práctico

- **Copernicus Data Space Ecosystem** (Sentinel-1 y Sentinel-2):
  https://dataspace.copernicus.eu/
- **Microsoft Planetary Computer** (STAC abierto, sin credenciales; es el que usa
  el script `TP1_01`): https://planetarycomputer.microsoft.com/
- **NASA Earthdata Search** (GEDI, NISAR): https://search.earthdata.nasa.gov/
- **ASF DAAC** (NISAR banda L): https://search.asf.alaska.edu/
- **Bhoonidhi, ISRO** (NISAR banda **S**; es otro portal, con otro registro):
  https://bhoonidhi.nrsc.gov.in/
- **JAXA / EORC** (mosaico global PALSAR-2):
  https://www.eorc.jaxa.jp/ALOS/en/dataset/fnf/fnf_index.htm
- **CONAE** (SAOCOM): https://catalogos.conae.gov.ar/

## Lo que hay que leer antes de descargar

El **Sentinel-2 Product Guide**, sección de la banda SCL: define qué clase es cada
valor. Es lo que permite entender por qué la SCL no marca la bruma.

## Especificaciones de producto

- **NISAR Data Product Format Document** (define el campo POLE del nombre de
  archivo, que es la polarización de las frecuencias primaria y secundaria):
  https://bhoonidhi.nrsc.gov.in/NISAR/NISAR_Data_Product_Format_Document_V1.2.1_digisigned.pdf
- **NISAR Data User Guide** (qué hay disponible y desde cuándo):
  https://nisar-docs.asf.alaska.edu/
