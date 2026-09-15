# Artículos revisados por pares — TP4

Todas verificadas: nómina completa de autores y DOI que resuelve. Son las mismas
que cierran la guía del práctico.

## El artículo fundacional del práctico

**Small, D. (2011).** Flattening gamma: Radiometric terrain correction for SAR imagery. *IEEE Transactions on Geoscience and Remote Sensing, 49*(8), 3081-3093. https://doi.org/10.1109/TGRS.2011.2120616

> **Es la referencia que sostiene todo el TP4.** Formula y demuestra γ⁰ con terrain
> flattening. Sin esto, en un bosque andino uno mide topografía y cree medir
> vegetación.

## El speckle

**Lee, J.-S., Wen, J.-H., Ainsworth, T. L., Chen, K.-S. y Chen, A. J. (2009).** Improved sigma filter for speckle filtering of SAR imagery. *IEEE Transactions on Geoscience and Remote Sensing, 47*(1), 202-213. https://doi.org/10.1109/TGRS.2008.2002881

> El filtro que usa el script TP4_06. Promedia menos donde detecta un borde.

## Banda C contra banda L (la pregunta del práctico)

**Huang, X., Ziniti, B., Torbick, N. y Ducey, M. J. (2018).** Assessment of forest above ground biomass estimation using multi-temporal C-band Sentinel-1 and polarimetric L-band PALSAR-2 data. *Remote Sensing, 10*(9), Artículo 1424. https://doi.org/10.3390/rs10091424

> Compara C y L sobre el mismo terreno y las mismas parcelas. Dice explícitamente
> que la banda C satura mucho antes por su penetración limitada del dosel. Es lo
> que este práctico mide con sus propios datos.

## La saturación de la banda L

**Khati, U. y Singh, G. (2022).** Combining L-band Synthetic Aperture Radar backscatter and TanDEM-X canopy height for forest aboveground biomass estimation. *Frontiers in Forests and Global Change, 5*, Artículo 918408. https://doi.org/10.3389/ffgc.2022.918408

> Mide la saturación de banda L en **~105 Mg/ha** con un criterio explícito, y
> recoge que los valores publicados van de **40 a 150 Mg/ha** según el bosque. No
> hay un número universal.

**Bouvet, A., Mermoz, S., Le Toan, T., Villard, L., Mathieu, R., Naidoo, L. y Asner, G. P. (2018).** An above-ground biomass map of African savannahs and woodlands at 25 m resolution derived from ALOS PALSAR. *Remote Sensing of Environment, 206*, 156-173. https://doi.org/10.1016/j.rse.2017.12.030

> Encuentra ~85 Mg/ha en sabanas africanas. Confirma que el umbral depende del
> bosque.

## Las misiones

**Palomeque, M., Ferreyra, J. y Thibeault, M. (2025).** Monitoring results of the SAOCOM-1 constellation: A mission overview and summary of results. *IEEE Geoscience and Remote Sensing Magazine, 13*(2), 49-57. https://doi.org/10.1109/MGRS.2024.3475228

**Rosen, P. A., Bawden, G. W., Barela, P., Chapman, B., Fattahi, H., Jones, C. E., Joughin, I. R., Lavalle, M., Lohman, R. B., Simons, M., Siqueira, P., Das, A., Desai, N. M., Kumar, R., Putrevu, D., Sharma, R. y Shrikant, C. V. (2025).** The NASA-ISRO SAR Mission: A summary. *IEEE Geoscience and Remote Sensing Magazine, 13*(2), 8-34. https://doi.org/10.1109/MGRS.2025.3578258

**Shimada, M., Itoh, T., Motooka, T., Watanabe, M., Shiraishi, T., Thapa, R. y Lucas, R. (2014).** New global forest/non-forest maps from ALOS PALSAR data (2007-2010). *Remote Sensing of Environment, 155*, 13-31. https://doi.org/10.1016/j.rse.2014.04.014

> El producto de mosaico de JAXA.

**Shimada, M., Isoguchi, O., Tadono, T. e Isono, K. (2009).** PALSAR radiometric and geometric calibration. *IEEE Transactions on Geoscience and Remote Sensing, 47*(12), 3915-3932. https://doi.org/10.1109/TGRS.2009.2023909

> **De acá sale el factor −83,0 dB** de la ecuación γ⁰(dB) = 10·log₁₀(DN²) − 83,0
> que usa el script TP4_04. Cite ésta para el factor y la de 2014 para el mosaico.

## Modelo de elevación

**Guth, P. L. y Geoffroy, T. M. (2021).** LiDAR point cloud and ICESat-2 evaluation of 1 second global digital elevation models: Copernicus wins. *Transactions in GIS, 25*(5), 2245-2261. https://doi.org/10.1111/tgis.12825

> Justifica el DEM que usa el terrain flattening.

## Los indices polarimetricos: de donde sale cada formula

Conviene no mezclarlas, porque son dos formulas distintas de autores distintos y
dan valores distintos.

- **Kim, Y. y van Zyl, J. J. (2009).** _A time-series approach to estimate soil
  moisture using polarimetric radar data._ IEEE Transactions on Geoscience and
  Remote Sensing. Origen de la version **quad-pol** del RVI,
  `8*g0HV / (g0HH + g0VV + 2*g0HV)`, que es la que reproduce el SAR Handbook y la
  que corresponde a las escenas SAOCOM quad-pol, ALOS-1 y BIOMASS.
  _(Volumen, numero y paginas sin verificar: completar antes de citarlo en un
  trabajo formal.)_

- **Trudel, M., Charbonneau, F. y Serrar, S. (2012).** _Using RADARSAT-2
  polarimetric and ENVISAT-ASAR dual-polarization data for estimating soil
  moisture over agricultural fields._ Canadian Journal of Remote Sensing, 38(4),
  514. Origen de la version **dual** del RVI,
  `4*g0cruzada / (g0co + g0cruzada)`, planteada como modificacion de la anterior.
  Es indiferente a la pareja de polarizaciones: se usa con HH+HV y con VV+VH, de
  modo que **es la que habilita calcular RVI con Sentinel-1**.

- **Mandal, D. et al. (2020).** _Dual polarimetric radar vegetation index for
  crop growth monitoring using Sentinel-1 SAR data._ Remote Sensing of
  Environment, 247, 111954. DOI 10.1016/j.rse.2020.111954. Critica las formas
  basadas en la intensidad de la polarizacion cruzada, que pueden dar un valor
  alto con el dosel poco desarrollado —riesgo real en la estepa, con 3,4 Mg/ha de
  mediana— y propone el **DpRVI**, sobre el autovalor dominante y el grado de
  polarizacion, invariante a la base de polarizacion. Es el camino a seguir si el
  RVI dual da resultados raros en la estepa. El producto **NISAR GCOV ya trae la
  matriz de covarianza calculada**, de modo que el DpRVI no cuesta trabajo extra.

**Regla de cita para los informes del curso:** escribir siempre cual de las dos
formas se uso. Poner «RVI» a secas es ambiguo y en un informe se paga.

## El taller DGSE del Instituto Gulich (CONAE-UNC, 2021)

**Beltramone, G., Alvarez, M. P., Paccioretti, P., Albornoz, J., Nicolaus, D.,
Minotti, P., Villalba, R. y Marinelli, V. (2021).** _Taller Integrador DGSE:
evaluacion de indicadores satelitales SAR SAOCOM para el seguimiento temporal de
cultivos._ Doctorado en Geomatica y Sistemas Espaciales, Instituto Gulich
(CONAE-UNC), Cordoba. PDF en esta carpeta.

Sirve para dos cosas distintas y las dos importan.

**Como fuente tecnica.** Trae los cuatro grafos de SNAP para SAOCOM quad-pol, y
son la base de `graph_saocom_quad_indices.xml` y
`graph_saocom_quad_polarimetria.xml` de este practico. Confirma que el RVI y el
RFDI se calculan con el operador `Polarimetric-Parameters` de SNAP y no a mano.
Y usa para Sentinel-1 el RVI dual `4*VH/(VV+VH)` sobre sigma0 en lineal, que es
la forma de Trudel et al. (2012).

**IMPORTANTE**: sus grafos NO llevan Terrain Flattening, porque su area de
estudio es la llanura cordobesa. Los de este practico si lo llevan, y ademas
`Orientation-Angle-Correction`, porque los sitios estan en ladera andina.
Copiarlos tal cual seria un error.

**Como antecedente que hay que discutir en clase.** Su resultado es el OPUESTO
al del TP4: sobre cultivos, el RVI de Sentinel-1 en banda C supera al RVI de
SAOCOM en banda L para predecir altura, y en trigo es la variable mas importante
de todas. Acá la banda L le gana ocho veces a la C.

Los dos trabajos estan bien. La diferencia la explica el techo de UN METRO de la
banda C (SAR Handbook, Tabla 4.1): los cultivos de Cordoba miden de 20 a 300 cm
y caen dentro del rango util de la banda C; el dosel de este ecotono mide 5,07 m
y queda por encima. Cada uno midio de un lado distinto de la misma frontera. Ver
la seccion 4.7.3 de la guia.
