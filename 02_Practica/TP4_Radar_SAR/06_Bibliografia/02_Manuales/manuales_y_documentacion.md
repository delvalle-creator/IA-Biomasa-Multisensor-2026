# Manuales y documentación oficial — TP4

## SNAP y los grafos

- **SNAP** (ESA): https://step.esa.int/main/download/snap-download/
- **SNAP Command Line (gpt)**: https://step.esa.int/main/doc/tutorials/
- Los grafos del práctico están junto a los scripts que los usan, en
  `03_Scripts/01_Pre_procesamiento/*.xml`

**El orden que importa en el grafo:**

    Read -> Apply-Orbit-File -> Calibration (outputBetaBand=true)
         -> Terrain-Flattening -> Terrain-Correction -> Write

`Calibration` con `outputSigmaBand=true` es lo que NO hay que hacer en relieve.

## Productos

- **Sentinel-1 GRD/SLC**: https://sentiwiki.copernicus.eu/web/s1-products
- **SAOCOM** (CONAE): https://catalogos.conae.gov.ar/
- **NISAR GCOV**: https://nisar-docs.asf.alaska.edu/products-overview
- **Mosaico PALSAR-2** (JAXA/EORC):
  https://www.eorc.jaxa.jp/ALOS/en/dataset/fnf/fnf_index.htm

## Lo que hay que leer antes de procesar

El **Terrain Flattening** de SNAP y su base teórica en Small (2011). Es el paso que
decide si el producto sirve o no en este terreno.

## Un detalle de NISAR que confunde

`frequencyA` y `frequencyB` **son las dos banda L**, con distinto ancho de banda
(10 m y 80 m de píxel). No son L y S. El campo POLE del nombre de archivo (`DHDH`)
es la polarización de esas dos frecuencias, y está definido en el
**NISAR Data Product Format Document**:
https://bhoonidhi.nrsc.gov.in/NISAR/NISAR_Data_Product_Format_Document_V1.2.1_digisigned.pdf

## El SAR Handbook (2019), la referencia de fondo del practico

**Flores-Anderson, A. I., Herndon, K. E., Thapa, R. B. y Cherrington, E. (eds.)
(2019). _The SAR Handbook: Comprehensive Methodologies for Forest Monitoring and
Biomass Estimation_. SERVIR Global / NASA MSFC.**
https://ntrs.nasa.gov/citations/20190002563 — DOI 10.25966/nr2c-s697

Es de acceso libre y trae ejercicios resueltos. Lo que se usa en este practico:

- **Tabla 2.3 (p. 29)** — que aplicacion corresponde a cada banda. A la banda C
  le asigna mapeo global, deteccion de cambios y seguimiento de vegetacion baja;
  a la L, biomasa y mapeo de vegetacion; a la P, biomasa. Es la fuente del
  reparto de tareas entre bandas que plantea la seccion 4.7 de la guia.
- **Tabla 4.1 (p. 179)** — saturacion nominal de la retrodispersion HV frente a
  la altura del rodal: **10 cm en banda X, 1 m en banda C, 10 m en banda L**. Es
  la cifra que explica por que Sentinel-1 da R2 = 0,03 sobre un dosel de 5,07 m
  mientras NISAR en banda L llega a 0,25. El Handbook aclara que son valores
  nominales y que en una region concreta hay que fijarlos graficando la
  retrodispersion contra alturas de lidar: ese es el ejercicio de la seccion
  4.7.2.
- **Seccion 5.3 y Tabla 5.3** — los indices polarimetricos RVI y RFDI, sus
  formulas, sus rangos y con que polarizaciones se calcula cada uno. Es la fuente
  de la seccion 4.8.2.
- **Capitulo 4** — estimacion de altura de rodal (FSH) por InSAR de paso
  repetido. Explica por que el prototipado se concentro en banda L y por que
  Sentinel-1 no sirve para esa via: la longitud de onda corta hace que domine la
  decorrelacion temporal sobre vegetacion.
