# Glosario del curso

El vocabulario del proyecto, en un solo lugar. Cada práctico lo usa; ninguno lo
redefine. Si un término le resulta confuso al leer una guía, búsquelo acá antes
de seguir.

## Los sensores del curso

Ocho fuentes, de siete proveedores. Conviene tener presente qué aporta cada una,
porque el curso se organiza en torno a esa diferencia.

| Misión | Tipo | Banda y λ | Qué aporta |
|---|---|---|---|
| **Sentinel-1** | radar | C, 5,6 cm | Serie temporal extensa y geometría estable. Satura pronto |
| **SAOCOM-1A y 1B** | radar | L, 23,5 cm | Sensor argentino, de la CONAE. Referencia de estructura del bosque; cuadripolar en la línea de base |
| **NISAR** | radar | L, 23,8 cm | Referencia independiente de banda L, ya corregida de terreno |
| **PALSAR-2 (mosaico)** | radar | L, 23,6 cm | Referencia anual de banda L, externa al proyecto |
| **ALOS-1 PALSAR** | radar | L | Serie histórica y polarimetría completa (quad-pol) |
| **BIOMASS** | radar | P, 70 cm | Penetra el dosel entero. Entra como demostración: sus adquisiciones son posteriores al incendio |
| **Sentinel-2 y Landsat 9** | óptico | — | Índices de vegetación, severidad del incendio y saturación |
| **GEDI** | LiDAR | — | La referencia de altura y de biomasa del curso |

**SAOCOM** — Satélite Argentino de Observación con Microondas, de la CONAE. Es el
único sensor del curso que no se descarga con un programa: su catálogo exige
registro, solicitud y autorización previas.

**BIOMASS** — Misión de la ESA lanzada para medir biomasa forestal con banda P.
Su nivel 2A se publicó el 30 de junio de 2026.

## Radar

**σ⁰ (sigma cero)** — Coeficiente de retrodispersión referido al área proyectada
sobre el plano horizontal. En terreno llano sirve; en relieve **no**, porque la
misma vegetación se ve brillante en una ladera y oscura en la opuesta. Esa señal
geométrica se confunde con biomasa.

**β⁰ (beta cero)** — Referido al área en el plano de la imagen (radar brightness).
Es el paso intermedio: **Terrain Flattening lo exige como entrada**. En SNAP,
`Calibration` con `outputBetaBand=true` y `outputSigmaBand=false`.

**γ⁰ (gamma cero)** — Referido al área **realmente iluminada** sobre el terreno
inclinado. Es el único defendible en un bosque andino, y es lo que este proyecto
usa siempre. **Se guarda en escala LINEAL, nunca en dB.**

**Terrain Flattening** — Corrección que pasa de β⁰ a γ⁰ usando un modelo de
elevación. Es lo que quita el efecto de la pendiente sobre el brillo.

**dB (decibeles)** — `10·log10(valor lineal)`. Se aplica **al final**, para mirar
y comparar. Nunca antes de promediar o filtrar: el promedio de los logaritmos no
es el logaritmo del promedio, y filtrar en dB sesga sistemáticamente hacia abajo.

**Speckle** — Granulado propio de las imágenes de radar. No es ruido del sensor,
es interferencia entre los dispersores dentro de cada píxel. Se atenúa
promediando, y ese promediado recupera capacidad de predicción.

**Layover, acortamiento de pendiente y sombra** — Distorsiones geométricas del radar en relieve. El
layover ocurre cuando la cima llega al sensor antes que la base; la sombra, cuando
la ladera opuesta no recibe señal. En esas zonas el dato no significa nada, y por
eso existe la máscara de validez.

**Polarización (HH, HV, VH, VV)** — Combinación de cómo se emite y cómo se recibe
la onda. **La cruzada (HV o VH) es la que responde a la biomasa leñosa**, porque
se genera por dispersión de volumen en ramas y troncos.

**Quad-pol y dual-pol** — Quad-pol registra las cuatro combinaciones y permite
descomponer la señal en sus mecanismos físicos; dual-pol registra dos y sólo da
indicadores indirectos.

**Ascendente y descendente** — Sentido de la órbita. Cambia desde qué lado mira el
radar, de modo que **γ⁰ de una misma ladera difiere sistemáticamente entre ambas**.
No se apilan ni se promedian juntas.

**Banda C, banda L, banda P** — Longitud de onda del radar. C (≈5,5 cm) interactúa
con hojas y ramas finas y **satura pronto**; L (≈23 cm) atraviesa el follaje y
llega a las ramas gruesas y los troncos, donde está la biomasa; P (≈70 cm)
penetra más todavía.

**Saturación** — Punto a partir del cual la señal deja de crecer aunque la
biomasa siga creciendo. Es el límite de cada método, y medirlo es un objetivo del
curso, no un fracaso.

## Óptico

**Reflectancia de superficie** — Proporción de luz reflejada, ya corregida de
atmósfera. Va de 0 a 1. Es lo que este proyecto usa (productos L2A y L2).

**NDVI** — `(NIR − ROJO) / (NIR + ROJO)`. El más conocido. **Satura pronto**: en
estos sitios se aplana a partir de los 15 a 18 m de dosel.

**EVI** — NDVI mejorado; corrige suelo de fondo y aerosol, y satura algo más tarde.

**NDMI** — `(NIR − SWIR1) / (NIR + SWIR1)`. Índice de humedad del dosel.

**NBR** — `(NIR − SWIR2) / (NIR + SWIR2)`. Índice de área quemada: una banda baja
y la otra sube con el fuego, por eso se desploma.

**dNBR** — `NBR_pre − NBR_post`. Cartografía el incendio. Se clasifica con los
umbrales de **Key y Benson (USGS)**, que son **siete clases contiguas**.

**SCL / QA_PIXEL** — Bandas de clasificación de escena (Sentinel-2 y Landsat) que
marcan nube, sombra, nieve. **Son categóricas: se remuestrean por vecino más
cercano.** Interpolarlas crea clases que no existen.

## LiDAR

**Huella (footprint)** — Cada disparo de GEDI ilumina un círculo de ≈25 m. GEDI
**no es una imagen**: son puntos repartidos a lo largo de las órbitas, con huecos.

**rh25, rh50, rh95, rh98** — Alturas relativas: la altura bajo la cual se acumula
ese porcentaje de la energía devuelta. **rh95 se usa como altura de dosel.**

**sensitivity** — Cuánta cobertura puede atravesar el láser y todavía detectar el
suelo. Si es baja, la huella no es confiable.

**pai, cover, fhd** — Índice de área foliar proyectada, cobertura y diversidad de
alturas del follaje. Describen la estructura vertical.

**L2A, L2B, L4A** — Niveles del producto GEDI. L2A da alturas; L2B, estructura;
**L4A da biomasa aérea en Mg/ha con su error estándar**, ajustada por grupo de
vegetación con parcelas de campo.

## Del proyecto

**AOI** — Área de interés. Acá son dos recintos de 15 × 15 km: `BOSQUE_NW_02`
(que se incendió) y `ESTEPA_NW_02` (control, que no se quemó).

**Grilla común** — EPSG:32719 (UTM 19S), píxel de 10 m, 1500 × 1500. Todos los
sensores están alineados al píxel, de modo que se pueden apilar directamente.
Está definida en un solo archivo: `configuracion_comun.py`.

**Época** — Cada uno de los cuatro estados temporales del conjunto: histórico
ALOS, línea de base 2023-24, pre-incendio 2025-26 y post-incendio 2026.

**BEAM-DIMAP (.dim)** — Formato nativo de SNAP y **producto principal**. El `.tif`
del mismo nombre es sólo una copia para mirar en QGIS: pierde los metadatos.

**Partición espacial** — Repartir entrenamiento y validación por **bloques de
terreno enteros**, no al azar. Como las huellas vecinas ven casi el mismo bosque,
una partición aleatoria evalúa el modelo con información que ya vio, y el R² sale
optimista. Es la diferencia entre medir ajuste y medir capacidad de predecir.

**Biomasa aérea (AGB)** — Materia seca sobre el suelo, en **megagramos por
hectárea (Mg/ha)**, equivalente a toneladas por hectárea.

## Una advertencia que vale para todo el curso

**No hay parcelas de campo.** La referencia es GEDI, que también es una estimación
satelital. Ninguna conclusión de este curso puede presentarse como una **medición**
de biomasa: son estimaciones calibradas contra otra estimación. Decirlo no debilita
el trabajo; ocultarlo sí lo invalidaría.
