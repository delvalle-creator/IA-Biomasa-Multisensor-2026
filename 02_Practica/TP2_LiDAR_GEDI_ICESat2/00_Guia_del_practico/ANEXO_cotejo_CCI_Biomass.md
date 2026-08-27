# Anexo — El mapa mundial de biomasa (CCI) contra nuestra referencia GEDI

*Nota metodológica. Se puede leer sin saber nada de teledetección.*

## 1. El problema, en una frase

El mapa mundial de biomasa de la ESA (CCI Biomass v7, 100 m) dice que nuestro
recinto de bosque tiene unas **135 Mg/ha**; nuestra referencia GEDI dice
**44**. Tres veces de diferencia sobre el mismo lugar. Este anexo muestra cómo
se averiguó quién tiene razón, y la respuesta no es «uno de los dos»: cada
producto acierta en una parte del paisaje y falla en otra.

## 2. Qué se comparó

El CCI Biomass es un mapa continuo: estima biomasa aérea en cada píxel de
100 m combinando radares (banda L y C) con calibración de LiDAR espacial. Se
recortaron sus capas anuales sobre los dos AOI y se leyó el valor del píxel
CCI de 2024 —anterior al incendio, igual que nuestra referencia— **debajo de
cada huella GEDI del práctico**: 495 pares en el bosque y 1.129 en la estepa.
Las tablas están en `05_Resultados\04_Tablas\TP2_cotejo_CCI_L4A_*.csv`.

## 3. El control de siempre: la estepa

En la estepa, CCI da 7,6 Mg/ha de media donde GEDI da 8,6, y las parcelas
publicadas para estepas patagónicas dan 5 a 10. **Los tres caminos coinciden.**
El CCI no está inflado en general; lo que le pase en el bosque hay que
buscarlo en el bosque.

## 4. La brecha no está donde uno cree

La diferencia por franja de altura del dosel (rh98 de GEDI, medianas):

| Dosel | n | GEDI L4A | CCI 2024 | Razón |
|---|---|---|---|---|
| 3–6 m | 188 | 2,1 | 130,5 | 62× |
| 6–9 m | 87 | 4,0 | 143,0 | 36× |
| 9–12 m | 47 | 15,6 | 158,0 | 10× |
| 15–18 m | 24 | 53,2 | 168,5 | 3,2× |
| 18–25 m | 69 | 105,7 | 181,0 | 1,7× |
| **25–60 m** | 28 | **175,0** | **174,5** | **1,0×** |

**En el bosque alto y cerrado —la lenga— los dos productos coinciden.** Toda
la diferencia de medias del recinto viene del dosel bajo: el ñire bajo, la
lenga achaparrada y el matorral, que ocupan dos tercios de la superficie, y
donde el CCI declara 130 Mg/ha bajo un dosel de cuatro metros.

## 5. Por qué ahí el CCI no puede tener razón

1. **La alometría lo prohíbe.** No existe ecuación de *Nothofagus* que ponga
   130 Mg/ha bajo 4 m de dosel; las parcelas de ñire publicadas dan decenas
   como máximo. El propio CCI dice 175 donde el dosel mide 25–60 m: no puede
   decir 130 donde mide 4.
2. **Su propia serie temporal lo delata.** La mediana del recinto salta de 97
   (2015) a 129 (2018) y 142 (2020): +45 Mg/ha en cinco años, un
   «crecimiento» imposible en este sistema, que coincide con el cambio de
   era de calibración del producto, no con el bosque.
3. **Infla donde hay ladera.** En las huellas de dosel menor de 9 m, los
   píxeles CCI mayores de 100 Mg/ha están a 10,3° de pendiente mediana; los
   menores de 50, a 4,7° (correlación 0,43). Es la retrodispersión de banda L
   inflada por el acortamiento de pendiente en matorral abierto — y por eso
   el CCI sí funciona en la estepa, que es llana.

## 6. Qué queda establecido

- **Lenga alta:** GEDI y CCI dicen lo mismo (~175 en las huellas más altas), y
  ambos quedan igual de lejos de las parcelas de rodal maduro (435–505
  Mg/ha): los dos productos satelitales comprimen el extremo alto. El mapa
  mundial no «rescata» la biomasa que a GEDI le falta ahí.
- **Dosel bajo:** la verdad probable está entre los dos y mucho más cerca de
  GEDI: el CCI es un artefacto de ladera; el L4A (2–4 Mg/ha) es quizás algo
  bajo frente a las parcelas de ñire (~5–30 según clase). Si algún día se
  corrige, será con alometría local declarada — no adoptando el CCI.
- **Estepa:** resuelto por triple coincidencia.

## 7. La lección del anexo

Un mapa mundial no es una referencia local: es **otro modelo**, con sus
propias zonas de validez. Antes de preferirlo hay que hacerle lo mismo que
este práctico le hace a todo: cruzarlo con lo que ya se conoce (la estepa
como control), desagregarlo (por franja de dosel, no el promedio), y buscarle
la física a la discrepancia (la pendiente). El promedio del recinto —44
contra 135— parecía una contradicción; desagregado, era un acuerdo en el
bosque alto y un artefacto en el matorral de ladera.

*Datos: ESA CCI Biomass v7.0 (recortes 2005–2024 sobre los dos AOI, 100 m).
Cotejo del 23/8/2026; tablas por huella y por franja en
`05_Resultados\04_Tablas\`. Parcelas citadas: Bertolin et al. (2015); Peri et
al.; Peri y Lasagno (2009, 2010).*

---

**Actualización del 26/8/2026 — el cotejo, llevado al mapa.** El paso 17
(`TP2_17_mapa_biomasa_GEDI_CCI.py`) traslada este cotejo al espacio: agrega
las huellas GEDI a celdas de 500 m (mediana, mínimo 3 huellas) y promedia el
mapa CCI de 2024 a la misma grilla. Los GeoTIFF quedan en
`05_Resultados\02_Rasters\` (listos para QGIS), las figuras en
`05_Resultados\05_Graficos\TP2_mapa_AGB_GEDI_vs_CCI_*.png` y la tabla por
celda en `04_Tablas\TP2_mapa_AGB_celdas_*.csv`. El mapa repite en el
territorio lo que este anexo encontró en la tabla: acuerdo en la estepa y en
la lenga alta, CCI por encima en el dosel bajo de ladera. El mapa de GEDI
tiene huecos a propósito: un muestreo orbital se mapea con sus huecos a la
vista, y rellenarlos es tarea del TP5, no del mapa.
