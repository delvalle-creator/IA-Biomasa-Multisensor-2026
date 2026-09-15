# Artículos revisados por pares — TP2

Todas verificadas: nómina completa de autores y DOI que resuelve. Ninguna se
citó de memoria.

## La misión y sus productos

**Dubayah, R., Blair, J. B., Goetz, S., Fatoyinbo, L., Hansen, M., Healey, S., Hofton, M., Hurtt, G., Kellner, J., Luthcke, S., Armston, J., Tang, H., Duncanson, L., Hancock, S., Jantz, P., Marselis, S., Patterson, P. L., Qi, W. y Silva, C. (2020).** The Global Ecosystem Dynamics Investigation: High-resolution laser ranging of the Earth's forests and topography. *Science of Remote Sensing, 1*, Artículo 100002. https://doi.org/10.1016/j.srs.2020.100002

> El artículo de la misión. Se cita para describir qué es GEDI y cómo mide.

**Duncanson, L., Kellner, J. R., Armston, J., Dubayah, R., Minor, D. M., Hancock, S., Healey, S. P., Patterson, P. L., Saarela, S., Marselis, S., Silva, C. E., Bruening, J., Goetz, S. J., Tang, H., Hofton, M., Blair, B., Luthcke, S., Fatoyinbo, L., Abernethy, K., … Zgraggen, C. (2022).** Aboveground biomass density models for NASA's Global Ecosystem Dynamics Investigation (GEDI) lidar mission. *Remote Sensing of Environment, 270*, Artículo 112845. https://doi.org/10.1016/j.rse.2021.112845

> Es el respaldo del script TP2_07: describe los modelos del producto L4A,
> ajustados por grupo de vegetación con parcelas de campo reales. Es la razón por
> la que NO se inventa una alometría propia.
> Nota: tiene 118 autores. Por eso la cita lleva los primeros 19, puntos
> suspensivos y el último, según la norma APA 7 para más de veinte autores.

## Calidad del dato y filtrado (el corazón del práctico)

**Adam, M., Urbazaev, M., Dubois, C. y Schmullius, C. (2020).** Accuracy assessment of GEDI terrain elevation and canopy height estimates in European temperate forests: Influence of environmental and acquisition parameters. *Remote Sensing, 12*(23), Artículo 3948. https://doi.org/10.3390/rs12233948

> Cuantifica cómo la pendiente y las condiciones de adquisición degradan la
> estimación de altura. Es el respaldo del filtro de 20° del script TP2_05.

**Moudrý, V., Prošek, J., Marselis, S., Marešová, J., Šárovcová, E., Gdulová, K., Kozhoridze, G., Torresani, M., Rocchini, D., Eltner, A., Liu, X., Potůčková, M., Šedová, A., Crespo-Peremarch, P., Torralba, J., Ruiz, L. A., Perrone, M., Špatenková, O. y Wild, J. (2024).** How to find accurate terrain and canopy height GEDI footprints in temperate forests and grasslands? *Earth and Space Science, 11*(10), Artículo e2024EA003709. https://doi.org/10.1029/2024EA003709

> El más directamente aplicable: es una guía de cómo filtrar GEDI en bosques
> templados y pastizales, que es exactamente el caso de este proyecto (bosque y
> estepa). Justifica la tasa de rechazo alta que da el práctico.

## Uso de GEDI combinado con otros sensores (anticipa el TP3 y el TP5)

**Guo, Q., Du, S., Jiang, J., Guo, W., Zhao, H., Yan, X., Zhao, Y. y Xiao, W. (2023).** Combining GEDI and Sentinel data to estimate forest canopy mean height and aboveground biomass. *Ecological Informatics, 78*, Artículo 102348. https://doi.org/10.1016/j.ecoinf.2023.102348

**Potapov, P., Li, X., Hernandez-Serna, A., Tyukavina, A., Hansen, M. C., Kommareddy, A., Pickens, A., Turubanova, S., Tang, H., Silva, C. E., Armston, J., Dubayah, R., Blair, J. B. y Hofton, M. (2021).** Mapping global forest canopy height through integration of GEDI and Landsat data. *Remote Sensing of Environment, 253*, Artículo 112165. https://doi.org/10.1016/j.rse.2020.112165

> Los dos hacen lo que hará el TP5: usar GEDI como calibración de sensores que sí
> cubren el terreno de forma continua. Son el modelo del enfoque.

## Modelo de elevación

**Guth, P. L. y Geoffroy, T. M. (2021).** LiDAR point cloud and ICESat-2 evaluation of 1 second global digital elevation models: Copernicus wins. *Transactions in GIS, 25*(5), 2245-2261. https://doi.org/10.1111/tgis.12825

> Justifica por qué el script TP2_04 usa Copernicus GLO-30 y no SRTM o ASTER.
