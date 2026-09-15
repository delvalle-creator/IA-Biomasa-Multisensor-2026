# Artículos revisados por pares — TP3

Todas verificadas: nómina completa de autores y DOI que resuelve. Son las mismas
que cierran la guía del práctico.

## Los índices

**Rouse, J. W., Jr., Haas, R. H., Schell, J. A. y Deering, D. W. (1974).** Monitoring vegetation systems in the Great Plains with ERTS. En *Third Earth Resources Technology Satellite-1 Symposium. Volume 1: Technical presentations, section A* (NASA SP-351, pp. 309-317). NASA. https://ntrs.nasa.gov/citations/19740022614

> El trabajo original del NDVI. Sin DOI: es de 1974.

**Huete, A., Didan, K., Miura, T., Rodriguez, E. P., Gao, X. y Ferreira, L. G. (2002).** Overview of the radiometric and biophysical performance of the MODIS vegetation indices. *Remote Sensing of Environment, 83*(1-2), 195-213. https://doi.org/10.1016/S0034-4257(02)00096-2

> El EVI. Dice explícitamente que el NDVI satura en zonas de alta biomasa mientras
> el EVI sigue respondiendo. Es lo que el TP3_05 mide con nuestros datos.

**Gao, B.-C. (1996).** NDWI—A normalized difference water index for remote sensing of vegetation liquid water from space. *Remote Sensing of Environment, 58*(3), 257-266. https://doi.org/10.1016/S0034-4257(96)00067-3

> **Matiz importante:** el índice original usa 1,24 µm. Nosotros usamos 1,61 µm,
> que es la que ofrece Sentinel-2, y es la práctica habitual. Declárelo.

## El fuego

**Key, C. H. y Benson, N. C. (2006).** Landscape Assessment (LA): Sampling and analysis methods. En D. C. Lutes, R. E. Keane, J. F. Caratti, C. H. Key, N. C. Benson, S. Sutherland y L. J. Gangi (Eds.), *FIREMON: Fire effects monitoring and inventory system* (Gen. Tech. Rep. RMRS-GTR-164-CD, pp. LA-1–LA-55). USDA Forest Service. https://research.fs.usda.gov/treesearch/24066

> Los umbrales de severidad. **Calibrados en Norteamérica**, no en Nothofagus.

**Saulino, L., Rita, A., Migliozzi, A., Maffei, C., Allevato, E., Garonna, A. P. y Saracino, A. (2020).** Detecting burn severity across Mediterranean forest types by coupling medium-spatial resolution satellite imagery and field data. *Remote Sensing, 12*(4), Artículo 741. https://doi.org/10.3390/rs12040741

> **La salvedad que hay que citar junto a Key y Benson.** Aplicados sin recalibrar
> dan concordancia muy baja (0,15 < K < 0,21). Recién tras recalibrar localmente
> obtienen R² = 0,69.

**Delcourt, C. J. F., Combee, A., Izbicki, B., Mack, M. C., Maximov, T., Petrov, R., Rogers, B. M., Scholten, R. C., Shestakova, T. A., van Wees, D. y Veraverbeke, S. (2021).** Evaluating the differenced Normalized Burn Ratio for assessing fire severity using Sentinel-2 imagery in northeast Siberian larch forests. *Remote Sensing, 13*(12), Artículo 2311. https://doi.org/10.3390/rs13122311

**Escuin, S., Navarro, R. y Fernández, P. (2008).** Fire severity assessment by using NBR (Normalized Burn Ratio) and NDVI (Normalized Difference Vegetation Index) derived from LANDSAT TM/ETM images. *International Journal of Remote Sensing, 29*(4), 1053-1073. https://doi.org/10.1080/01431160701281072

## La bruma y las nubes

**Tarrio, K., Tang, X., Masek, J. G., Claverie, M., Ju, J., Qiu, S., Zhu, Z. y Woodcock, C. E. (2020).** Comparison of cloud detection algorithms for Sentinel-2 imagery. *Science of Remote Sensing, 2*, Artículo 100010. https://doi.org/10.1016/j.srs.2020.100010

> Por qué la máscara del producto no ve la bruma.

## La saturación

**Wu, Y., Ou, G., Huang, T., Zhang, X., Liu, C., Liu, Z., Yu, Z., Luo, H., Lu, C., Shi, K., Wang, L. y Xu, W. (2024).** Climate interprets saturation value variations better than soil and topography in estimating oak forest aboveground biomass using Landsat 8 OLI imagery. *Remote Sensing, 16*(8), Artículo 1338. https://doi.org/10.3390/rs16081338

> Mide la saturación óptica entre **104 y 182 Mg/ha** en veinte distritos.

**Mutanga, O., Masenyama, A. y Sibanda, M. (2023).** Spectral saturation in the remote sensing of high-density vegetation traits: A systematic review of progress, challenges, and prospects. *ISPRS Journal of Photogrammetry and Remote Sensing, 198*, 297-309. https://doi.org/10.1016/j.isprsjprs.2023.03.010

## La armonización con Landsat

**Claverie, M., Ju, J., Masek, J. G., Dungan, J. L., Vermote, E. F., Roger, J.-C., Skakun, S. V. y Justice, C. (2018).** The Harmonized Landsat and Sentinel-2 surface reflectance data set. *Remote Sensing of Environment, 219*, 145-161. https://doi.org/10.1016/j.rse.2018.09.002
