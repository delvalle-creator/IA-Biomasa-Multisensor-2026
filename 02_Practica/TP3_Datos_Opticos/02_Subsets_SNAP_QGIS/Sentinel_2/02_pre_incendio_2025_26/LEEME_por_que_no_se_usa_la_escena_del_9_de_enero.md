# Por qué la escena PRE es la del 25/11/2025 y no la del 09/01/2026

En esta carpeta hay dos escenas ópticas anteriores al incendio:

    S2B_L2A_20251125_...   25 de noviembre de 2025   Sentinel-2B
    S2C_L2A_20260109_...    9 de enero de 2026       Sentinel-2C

La segunda parece la mejor candidata: el incendio ocurrió entre el **10/01/2026** y el
**27/02/2026**, de modo que la del 9 de enero es pre-incendio por un día, y está a ocho semanas
de la escena post (05/03/2026), las dos en pleno verano. La de noviembre, en cambio, está a tres
meses y medio y en plena brotación de la lenga y el ñire, que son caducifolias.

**Y sin embargo hay que usar la de noviembre. La del 9 de enero está mal corregida
atmosféricamente y no sirve.**

## La medición que lo demuestra

Reflectancia mediana sobre el recinto BOSQUE_NW_02, banda por banda:

| Escena | B2 azul | B3 verde | B4 rojo | B8 NIR | B11 | B12 |
|---|---|---|---|---|---|---|
| 25/11/2025 (S2B) | 0,0235 | 0,0443 | 0,0290 | 0,2668 | 0,1666 | 0,0859 |
| **09/01/2026 (S2C)** | **0,1528** | **0,1450** | **0,1210** | 0,2543 | 0,1614 | 0,0827 |
| 05/03/2026 (S2B) | 0,0207 | 0,0292 | 0,0431 | 0,1034 | 0,1481 | 0,1309 |

El infrarrojo cercano y los dos SWIR son prácticamente iguales entre noviembre y enero. **Lo que
está inflado, entre cuatro y seis veces, es el visible**, y más cuanto más corta es la longitud
de onda: el azul es el peor. Ésa es la firma inconfundible de **dispersión atmosférica que no fue
removida**: la corrección a reflectancia de superficie falló, y el producto quedó, de hecho, en
reflectancia de tope de atmósfera.

## Las dos consecuencias que se ven aguas abajo

**El NDVI se desploma sin que cambie la vegetación.** Sobre el bosque no quemado, el NDVI mediano
da 0,8679 en noviembre y 0,8654 en marzo —prácticamente idénticos—, pero **0,3767 el 9 de enero**.
Un bosque cerrado no tiene NDVI de 0,38. El rojo inflado es el que hunde el índice.

**La máscara de nubes se vuelve loca.** La banda de clasificación de escena (SCL) etiqueta el
**78,3 % del recinto como «suelo desnudo»** y sólo el 13,8 % como vegetación, sobre un bosque
andino. Con reflectancia visible tan alta, el clasificador no puede hacer otra cosa. Además
declara un 7,0 % de cirros, que es coherente con el diagnóstico: había velo de alta nubosidad.

## Verificado contra el MAESTRO, no contra la copia

Una objeción legítima: los números de arriba se midieron sobre el GeoTIFF, que en este proyecto
es sólo **copia de intercambio**. El producto maestro es el **BEAM-DIMAP** (`.dim` + `.data`), y
si la falla estuviera en la exportación, el maestro estaría sano y la escena sería recuperable.

Se comprobó leyendo directamente los `.img` del `.data` —ENVI, float32, big-endian, con
`SCALING_FACTOR 1.0` y `SCALING_OFFSET 0.0` declarados en el `.dim`— y comparándolos banda por
banda contra el `.tif`:

| Escena | | B2 azul | B4 rojo | B8 NIR |
|---|---|---|---|---|
| 25/11/2025 | maestro `.data` | 0,0235 | 0,0290 | 0,2668 |
| 25/11/2025 | copia `.tif` | 0,0235 | 0,0290 | 0,2668 |
| 09/01/2026 | maestro `.data` | 0,1528 | 0,1210 | 0,2543 |
| 09/01/2026 | copia `.tif` | 0,1528 | 0,1210 | 0,2543 |

**Diferencia maestro menos copia: 0,000000 en las seis comparaciones.** La exportación a GeoTIFF
es fiel; el defecto está en el producto, no en la copia. Y el NDVI calculado sobre el propio
maestro confirma el diagnóstico: 0,8019 el 25/11 contra **0,3483 el 09/01**.

La escena, por lo tanto, **no es recuperable reprocesando la exportación**. Habría que volver a
corregirla atmosféricamente desde el L1C, y con un 7 % de cirros encima no vale la pena.

## Lo que sí se verificó de la escena de noviembre

- **0,00 % de píxeles inutilizables**: ni nube, ni sombra, ni nieve, ni sin dato.
- SCL: 93,8 % vegetación, 5,6 % suelo desnudo. Razonable para este bosque.
- Es **Sentinel-2B, el mismo sensor que la escena post**, de modo que la comparación pre/post no
  arrastra además una diferencia entre satélites.

## Y una sorpresa que conviene registrar

La intuición decía que comparar noviembre contra marzo tenía que introducir un desfase
fenológico grande, porque la lenga y el ñire pierden la hoja. **Medido, ese desfase no existe:**
sobre el bosque no quemado el NDVI cambia 0,0031 y el NBR 0,0216 entre las dos fechas. Para
principios de marzo la hoja todavía está, y para fines de noviembre ya brotó.

Esto importa porque descarta la fenología como explicación del piso de ruido del TP5_04 (véase la
sección 66 del CONTEXTO_IA.md). Había que medirlo antes de cambiar nada.

*Verificado el 31/07/2026 sobre los propios GeoTIFF, con la misma máscara SCL que usa el TP3_04.*
