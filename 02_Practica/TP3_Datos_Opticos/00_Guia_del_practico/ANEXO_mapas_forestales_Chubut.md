# Anexo al TP3. Qué aportan y qué no los mapas forestales de Chubut

*Sitios BOSQUE_NW_02 y ESTEPA_NW_02 · Curso de Posgrado*
*Héctor Francisco del Valle · CeReGeo (FCyT, UADER) y LEMIV (FI, UNPSJB)*

> Versión de lectura rápida. El desarrollo completo, con las seis tablas, está en
> la guía teórico-práctica, en el Trabajo Práctico 3
> (`02_Practica\00_Guia_teorica_practica`).

## Por qué existe este anexo

Un archivo no contiene lo que dice su nombre hasta que uno lo comprueba. Este anexo
documenta qué pasó al incorporar un conjunto de 21 capas sobre los bosques de Chubut,
publicado por una institución seria y con nombres que prometían exactamente lo que
hacía falta. La comprobación cambió la conclusión.

## Lo que sirve

**Seis capas de estructura forestal a 30 m** (Silveira et al., 2023): volumen de madera,
área basal, DAP, altura media, altura dominante y cobertura de copas. Son magnitudes de
inventario forestal, del tipo que se mide en parcelas de campo, y ningún sensor del curso
puede medirlas. Se construyeron sobre parcelas del inventario nacional, con predictores
de Sentinel-1 (VV y VH con textura), Sentinel-2 y coordenadas geográficas. **Los
predictores más importantes son VH y la longitud**: eso importa para lo que sigue.

En el recinto de **bosque**, el 89,8 % de los píxeles trae dato; medias de 162,42 m³/ha
de volumen, 24,22 m²/ha de área basal y 16,26 m de altura dominante. En el de **estepa**
sólo el 7,5 %, porque las capas están enmascaradas a bosque: allí no caracterizan el
sitio, apenas señalan dónde hay leñosas.

**Una coincidencia que vale como verificación.** Ese 89,8 % de píxeles con dato coincide
hasta el decimal con la cobertura arbórea que el anexo del TP2 calculó con los polígonos
del SNMBN 2017, por un camino enteramente distinto.

## El problema: huella por huella no coinciden con GEDI

657 de las 690 huellas del bosque caen sobre píxeles con dato. Las correlaciones de
rangos son bajas:

| Comparación | n | rho |
|---|---|---|
| rh95 contra altura dominante | 657 | 0,280 |
| cover contra cobertura de copas | 657 | 0,151 |
| AGBD contra volumen de madera | 471 | 0,238 |

Descartar las huellas tomadas sin hojas no mejora nada (0,280 → 0,269): el desacuerdo
no lo causa la fenología.

## La discrepancia del ñire

| Fuente y variable | Ñire (n=437) | Lenga (n=196) | Cociente |
|---|---|---|---|
| GEDI: altura rh95 | 5,17 m | 16,68 m | **3,23** |
| GEDI: biomasa AGBD | 13,87 Mg/ha | 86,69 Mg/ha | **6,25** |
| Mapa: altura dominante | 14,75 m | 15,40 m | **1,04** |
| Mapa: volumen de madera | 75,8 m³/ha | 114,6 m³/ha | **1,51** |

GEDI mide el ñire tres veces más bajo que la lenga. El mapa dice que miden casi lo mismo.

**Cómo se decide cuál creer.** GEDI mide directamente: si el eco vuelve desde cinco
metros, hay cinco metros. El mapa predice, y hay tres motivos —todos derivados de la
metodología publicada— por los que su predicción achata el contraste justamente aquí:

1. **La banda C satura.** Sentinel-1 trabaja a ~5,6 cm y responde sobre todo a hojas y
   ramas finas. Por encima de cierta densidad deja de crecer. Como VH es el predictor
   principal, lo que VH no distingue el modelo tampoco.
2. **El relieve la contamina.** En el TP4 medimos 8,49 dB de diferencia entre laderas que
   encaran al sensor y las opuestas, antes de corregir por área iluminada.
3. **La longitud homogeneiza.** Está entre los predictores más importantes. Un modelo que
   se apoya en la coordenada interpola, y en nuestro recinto ñire y lenga están
   entreverados dentro de la misma franja de 15 km: el modelo los empuja a un valor común.

A eso se suma que el ñire bajo y abierto está poco representado en las parcelas de
inventario, y todo modelo tira hacia el centro de sus datos de entrenamiento.

**Esto no invalida el producto.** Indica que nuestro recinto cae fuera de la envolvente
donde ese mapa discrimina bien. Y **no resuelve** la duda del anexo del TP2 sobre el
modelo alométrico del ñire —eso exige parcelas de campo—, pero la acota.

## Tres capas que miden otra cosa (y el error de expectativa fue nuestro)

`3_Spatial_VegGreenness`, `4_Spatial_LSTSummer` y `5_Spatial_LSTWinter` no contienen
verdor ni temperatura. Basta mirar el rango: la LST de verano va de 0,10 a 3,00, y no hay
unidad de temperatura en que eso tenga sentido; el verdor va de 0,00 a 0,17, un décimo del
recorrido de cualquier índice normalizado.

Son **índices de heterogeneidad local calculados por textura de imagen** (Silveira et al.,
2021), diseñados para identificar sitios de interés para la **conservación de la
biodiversidad**. Nunca fueron predictores de biomasa. La prueba por medición es el signo: el verdor espacial correlaciona **negativamente** con
los cuatro índices de este práctico (NDVI −0,276, NBR −0,278, NDMI −0,257, EVI −0,220).
Si midiera el nivel de verdor el signo sería positivo y fuerte. Negativo y moderado es lo
propio de una medida de heterogeneidad: el paisaje es más disparejo donde la vegetación es
rala.

**Método a retener:** cuando no se sabe qué contiene un archivo, correlacionarlo con algo
conocido y mirar el signo dice más que leer el nombre del archivo.

Contra la estructura del bosque no dicen nada (AGBD −0,027 y −0,033; altura −0,102 y
−0,140), **que es el resultado esperado**: la heterogeneidad del hábitat predice riqueza de
especies, no cuánta madera hay. La expectativa equivocada fue la nuestra, por leer el
nombre del archivo en lugar del artículo que lo respalda. A cambio, cubren los dos
recintos completos, estepa incluida, porque no están enmascaradas.

## Antes de usar cualquiera de estas capas

Las 21 están en coordenadas geográficas y ninguna cae en la malla común. Hay que
reproyectar a **EPSG:32719** y alinear a la malla de 10 m.

- capas **continuas** → remuestreo **bilineal**
- capas **de clases** (son ocho) → **vecino más próximo**

Interpolar linealmente entre la clase 3 y la clase 7 devuelve un 5, que es una clase que
ese píxel no es, y el error es silencioso.

Pasar de 30 m a 10 m **no agrega información**: el remuestreo sirve para apilar, y la
resolución real sigue siendo la de origen.

## Ejercicio

Dos productos satelitales publicados discrepan en un factor de tres sobre la altura de la
misma cobertura y de seis sobre su biomasa. Argumente a cuál conviene creerle y por qué, y
diga qué medición concreta resolvería la cuestión sin lugar a dudas.

El material está completo en la carpeta del práctico. Se sugiere discutir, como mínimo,
qué mide físicamente cada sensor, con qué datos se ajustó cada modelo, y qué le ocurre a
un modelo estadístico aplicado a una cobertura poco representada en su entrenamiento.

## Lo que queda declarado

De las 21 capas: seis valen, tres tienen nombre engañoso y contenido sin relación con la
estructura, una toma una sola clase en el 100 % de los dos recintos, otra no tiene dato en
la estepa, y el resto sirve como contexto. Entre ese contexto, un dato para retener: la
huella humana promedia 0,07 sobre 1,00 en el bosque y 0,10 en la estepa, de modo que ambos
sitios están entre lo menos intervenido de la región.

Los dos hallazgos principales son **errores de expectativa nuestros**, no defectos ajenos:
se esperaba de unos índices de heterogeneidad que predijeran biomasa, y de un modelo
nacional que discriminara a escala de recinto lo que su predictor principal no distingue.
Los dos eran evitables leyendo las publicaciones. Y los dos, de no detectarse, habrían
tenido consecuencias silenciosas: un modelo de biomasa peor sin que nada avisara, y un
ñire descrito como bosque alto.

Este conjunto son cinco trabajos revisados por pares (2021–2023) que produjeron la primera
cartografía nacional continua de estructura forestal para los 463.000 km² de bosque nativo
argentino. Que nuestro recinto quede fuera de su envolvente no lo invalida: lo sitúa.
Saber situar un producto ajeno, con mediciones propias y sin descalificarlo, es una de las
capacidades que este curso enseña.

## Referencias

- Martinuzzi, S., Olah, A. O., Rivera, L., Politi, N., Silveira, E. M. O., Martínez Pastur, G., Rosas, Y. M., Lizárraga, L., Nazaro, P., Bardavid, S., Radeloff, V. C., y Pidgeon, A. M. (2023). Closing the research-implementation gap: Integrating species and human footprint data into Argentina's forest planning. *Biological Conservation, 286*, 110257. https://doi.org/10.1016/j.biocon.2023.110257
- Martinuzzi, S., Radeloff, V. C., Martínez Pastur, G., Rosas, Y. M., Lizárraga, L., Politi, N., Rivera, L., Huertas Herrera, A., Silveira, E. M. O., Olah, A., y Pidgeon, A. M. (2021). Informing forest conservation planning with detailed human footprint data for Argentina. *Global Ecology and Conservation, 31*, e01787. https://doi.org/10.1016/j.gecco.2021.e01787
- Silveira, E. M. O., Radeloff, V. C., Martinuzzi, S., Martínez Pastur, G., Bono, J., Politi, N., Lizárraga, L., Rivera, L. O., Ciuffoli, L., Rosas, Y. M., Olah, A. M., Gavier Pizarro, G., y Pidgeon, A. M. (2023). Nationwide native forest structure maps for Argentina based on forest inventory data, SAR Sentinel-1 and vegetation metrics from Sentinel-2 imagery. *Remote Sensing of Environment, 285*, 113391. https://doi.org/10.1016/j.rse.2022.113391
- Silveira, E. M. O., Radeloff, V. C., Martinuzzi, S., Martínez Pastur, G., Rivera, L., Politi, N., Lizárraga, L., Farwell, L. S., Elsen, P. R., y Pidgeon, A. M. (2021). Spatio-temporal remotely sensed indices identify hotspots of biodiversity conservation concern. *Remote Sensing of Environment, 258*, 112368. https://doi.org/10.1016/j.rse.2021.112368
- Silveira, E. M. O., Radeloff, V. C., Martínez Pastur, G., Martinuzzi, S., Politi, N., Lizárraga, L., Rivera, L. O., Gavier-Pizarro, G. I., Yin, H., Rosas, Y. M., Calamari, N. C., Navarro, M. F., Sica, Y., Olah, A. M., Bono, J., y Pidgeon, A. M. (2022). Forest phenoclusters for Argentina based on vegetation phenology and climate. *Ecological Applications, 32*(3), e2526. https://doi.org/10.1002/eap.2526
- SILVIS Lab. (2025). *Map products in support of sustainable management of Argentina's forests* [Colección cartográfica]. Universidad de Wisconsin-Madison. https://silvis.forest.wisc.edu/webmaps/forest_structure_maps_for_argentina/
