# Verificación de los resultados del TP1

El TP1 no produce mapas: produce **decisiones sobre qué dato usar**. Se verifican
así.

## 1. La huella del catálogo NO es el dato

| Producto | Cobertura según el catálogo | Píxeles con dato en el AOI | Decisión |
|---|---|---|---|
| 6 gránulos NISAR sobre estepa | 69 – 76 % | **15 %** | descartados (12 GB) |
| 3 gránulos NISAR restantes | — | suficiente | se usan |

**Cómo se verificó.** Leyendo una ventana del AOI de cada producto sin descargar
la escena entera —los productos son COG, permiten lectura parcial— y contando los
píxeles con valor. El script `TP1_01_verificar_cobertura.py` hace exactamente eso
y compara las dos cifras lado a lado.

**La regla, para prevenir:** verifique la cobertura ANTES de descargar, no después.
Consultar por un rectángulo devuelve todo lo que lo TOCA, no lo que lo CUBRE.

## 2. La nubosidad del catálogo NO es la del AOI

El catálogo informa la nubosidad de la escena completa (110 × 110 km). El recinto
mide 15 × 15 km. Son dos números distintos y pueden diferir muchísimo. El script
`TP1_01` recalcula la nubosidad real dentro del AOI con la banda de calidad y
muestra las dos.

## 3. La máscara de nubes no ve la bruma

| Escena (bosque) | Azul | NDVI | Nubes según la SCL | Veredicto |
|---|---|---|---|---|
| 25/11/2025 | 0,024 | 0,802 | 0,0 % | limpia |
| **09/01/2026** | **0,158** | **0,343** | **7,4 %** | **BRUMA: azul 6,7× lo normal** |
| 05/03/2026 | 0,021 | 0,301 | 0,0 % | limpia |

La SCL está entrenada para detectar nubes: objetos brillantes, opacos, con bordes.
La bruma es semitransparente y difusa; la deja pasar. Tarrio et al. (2020)
documentan estas limitaciones.

**Cómo se detecta, y por qué el azul.** Los aerosoles dispersan mucho más las
longitudes de onda cortas. Una escena con bruma tiene el azul inflado y el
infrarrojo casi intacto. El script `TP1_02_detectar_bruma.py` compara cada escena
contra la mediana del propio sitio, con dos criterios: azul por encima de 2,5×
(bruma grosera) o azul por encima de 1,5× con el NDVI caído por debajo del 70 %
(sospechosa). El segundo criterio hace falta porque sobre la estepa, que es clara,
la misma escena contaminada sólo llega a 1,6× y el primer criterio la dejaría pasar.

**La regla, para prevenir:** no confíe en la máscara de nubes del producto. Compare
cada escena contra las demás del mismo sitio, y use dos criterios, no uno. Un
umbral único casi nunca sirve para superficies con brillos distintos.

## 4. Confirmación independiente

Landsat 9 del 04/01/2026 da NDVI 0,78 en el mismo bosque donde Sentinel-2 del
09/01 daba 0,34. Cinco días de diferencia, dos agencias distintas. El bosque
estaba sano; la imagen estaba sucia.

## 5. Cuánto cambia el resultado si uno se equivoca

| Escena pre | Píxeles válidos | Superficie quemada |
|---|---|---|
| 09/01/2026 (con humo del incendio) | 92,3 % | 16.463,1 ha (79,3 %) |
| 25/11/2025 (limpia) | 99,8 % | 18.009,2 ha (80,2 %) |

Menos de un punto porcentual, porque el NBR usa las bandas que la bruma casi no
toca. **Pero eso no se sabe de antemano**: si el índice hubiera sido el NDVI, el
resultado habría sido inservible. Una escena no está mala en abstracto: está mala
para un índice determinado.

## Lo que NO se pudo verificar

- **La banda S de NISAR.** El instrumento lleva radares L y S, pero no siempre
  transmiten juntos: adquiere en modo L-only, S-only o conjunto. Nuestros gránulos
  son L-only (`radarBand = 'L'`, sólo el grupo `/science/LSAR`). La banda S se
  distribuye por Bhoonidhi (ISRO), no por la NASA, y su producción diaria empezó el
  08/07/2026. Queda pendiente confirmar si hay cobertura sobre Chubut.
- **Ojo con `frequencyA` y `frequencyB`**: las dos son banda L, con distinto ancho
  de banda (10 m y 80 m de píxel). No son L y S. El código `DHDH` del nombre es la
  polarización de esas dos frecuencias.
