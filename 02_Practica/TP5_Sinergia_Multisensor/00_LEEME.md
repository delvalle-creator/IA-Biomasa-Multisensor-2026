# TP5 — Sinergia multisensor

> Los números de esta tabla los produce `00_COMUN/contar_archivos.py`, que
> los lee del disco. Si dejan de coincidir, vuelva a correrlo en lugar de
> corregirlos a mano.



## El recorrido, en orden

| Carpeta | Qué hay | Archivos |
|---|---|---|
| `00_Guia_del_practico/` | **Empiece por acá:** la guía sintética en PDF, con su LEEME, más los objetivos y las figuras. El desarrollo completo, en el capítulo 7 de la guía teórico-práctica | 11 |
| `01_Prompt_IA/` | El prompt inicial con sus defectos, el análisis de la respuesta, el prompt corregido y la verificación | 4 |
| `03_Scripts/` | Los programas, numerados en orden de ejecución, y el archivo que fija ese orden | 12 |
| `04_Tablas_de_trabajo/` | Las tablas `.csv` del dataset multisensor: muestras, entrenamiento y validación | 5 |
| `05_Resultados/` | Las tablas. Los rásters del paso 5 los escribe ese paso | 16 |
| `06_Bibliografia/` | Referencias de los artículos y manuales (este práctico no lleva fichas de sensores ni enlaces propios) | 3 |
| `07_Preguntas_y_entrega/` | Las dos figuras de las áreas quemadas (por departamento y el incendio). **Aquí deja el estudiante sus respuestas y su entrega** | 3 |
| `09_Orange/` | El flujo de Orange Data Mining del dataset multisensor (ópticos y radar contra la biomasa GEDI), con su LEEME | 2 |
| | Los tres archivos de la raíz: presentación, notas técnicas y de dónde salen los insumos | 3 |
| | **TOTAL** | **59** |

Este práctico no descarga ni pre-procesa nada y no usa grafos de SNAP: por eso
no tiene `02_Subsets_SNAP_QGIS` ni `08_Grafos_SNAP`.

El práctico completo, con su fundamentación, está en la guía teórico-práctica: `02_Practica\00_Guia_teorica_practica`.

## Qué hace este práctico

No descarga ni pre-procesa nada: **consume lo que dejaron los cuatro anteriores**.
Arma un conjunto de datos que reúne, sobre cada huella válida de GEDI, los índices
ópticos del TP3, la retrodispersión de banda C y de banda L del TP4 y la pendiente;
ajusta modelos; los valida; y produce el mapa de biomasa con su incertidumbre.

## Lo que el práctico encontró, y es su contenido central

**1. La sinergia aporta menos de lo que parece.** El modelo que combina los tres
grupos de predictores llega a R² = 0,964 sobre validación. El modelo de control,
que usa **sólo** los predictores derivados de GEDI, llega a 0,956. La diferencia
—ocho milésimas— es todo lo que aportaron el óptico y el radar. El salto no vino de
combinar sensores sino de haber incluido la fuente de la variable estimada.

**2. El buen coeficiente global esconde el sesgo de los extremos.** Por franja de
altura, en el bosque el sesgo va de +3,93 m en la franja de 0 a 3 m a −9,27 m en la
de 18 a 21 m. Es compresión hacia la media, y ataca justamente donde está la
biomasa.

**3. El piso de ruido era grande, y no venía de donde se pensaba.** Sobre terreno
no quemado el procedimiento mide −10,25 Mg/ha donde debería medir cero. La sospecha
inicial fue el desfase de fechas del radar; medido, resultó falso. El piso lo
aportaba un solo índice óptico: quitándolo cae a −0,48 y el cociente entre señal y
ruido sube de 1,5 a 15,3.

**4. La incertidumbre no está donde uno cree.** De los tres tramos de la cadena de
error en el bosque —modelo de altura 4,32 m, conversión alométrica 13,58 Mg/ha,
producto de referencia 13,09 Mg/ha—, los dos últimos pesan cada uno unas tres veces
más que el primero. Mejorar el modelo de altura no mejoraría gran cosa el mapa.

## Lo que dejaron los otros prácticos, y por qué hacía falta combinar

| Sensor | Banda o índice | R² contra la altura del dosel | Dónde falla |
|---|---|---|---|
| Sentinel-1 VH | radar, banda C | 0,029 | No ve la biomasa: gana 0,52 dB en 25 m de árbol |
| Sentinel-2 | EVI | 0,215 | Se aplana con el dosel cerrado |
| Sentinel-2 | NDVI | 0,235 | **Satura a partir de los 15–18 m** |
| NISAR HV | radar, banda L | 0,273 | Moteado; y responde a biomasa, no a altura |
| Sentinel-2 | NBR | 0,291 | Satura |
| Sentinel-2 | **NDMI** | **0,310** | El mejor, y apenas llega a un tercio |

**Ninguno alcanza solo**, y ése era el argumento para combinarlos. Lo que el
práctico agrega es la medición de cuánto rinde efectivamente esa combinación, que
resultó ser bastante menos de lo que el argumento prometía. El resultado no
invalida el argumento: lo acota.

## La limitación que condiciona todo

**No hay parcelas de campo.** GEDI es la referencia, pero GEDI también es una
estimación satelital. Cualquier modelo de este práctico está calibrado contra otra
estimación, no contra una medición terrestre. **Ninguna conclusión puede
presentarse como una medición de biomasa.** Está dicho en el informe, no escondido.

## Dos precisiones de lectura

- El juego de predictores **sin EVI + radar** es el que baja el piso de ruido a
  −0,48 Mg/ha; los pasos 2 a 5 corren con el juego completo, y el ensayo nulo
  mide la diferencia.
- «Biomasa quemada», en las tablas y en el nombre de `TP5_04_biomasa_quemada.py`,
  significa **cambio aparente de AGBD asociado al incendio**: la estimación se
  apoya en GEDI, que es otra estimación, y no en una medición de campo.
