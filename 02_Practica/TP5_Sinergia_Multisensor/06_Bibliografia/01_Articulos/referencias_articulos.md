# Referencias

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
