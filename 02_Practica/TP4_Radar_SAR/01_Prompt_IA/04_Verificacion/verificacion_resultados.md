# Verificación de los resultados del TP4

## 1. El contraste bosque − estepa: la respuesta, medida

| Sensor | Banda | HH / VV | HV / VH |
|---|---|---|---|
| Sentinel-1 (10/01/2026) | C | 3,5 dB | 4,2 dB |
| SAOCOM (10/01/2026) | L | 8,1 dB | **11,7 dB** |
| NISAR (08/01/2026) | L | 8,0 dB | **9,9 dB** |
| PALSAR-2 (2025) | L | 8,3 dB | **11,6 dB** |

Dos sitios vecinos, mismo clima, mismo relieve; lo único que cambia es la biomasa.
**La banda L separa con casi el triple de contraste que la C**, y el máximo está
siempre en la polarización cruzada. Las dos cosas que predice la física.

## 2. El control cruzado que vale oro

NISAR y PALSAR-2 son misiones de agencias distintas, con órbitas, ángulos y
procesamientos distintos. Sobre el mismo bosque, en HV: **−13,2 dB y −12,5 dB**.
Coinciden dentro de 1 dB sin haberse puesto de acuerdo. Eso es una verificación de
calibración independiente.

**Y la contracara**: SAOCOM da −17,8 dB en ese mismo bosque, más de 4 dB abajo. No
está mal calibrado: tiene otro ángulo de incidencia. Su **contraste** (11,7 dB)
coincide con el de PALSAR-2 (11,6 dB). El valor absoluto difiere; la capacidad de
separar, no.

**La regla:** entre sensores distintos, compare formas y contrastes, no valores
absolutos.

## 3. El speckle: cuánta señal se come

R² del ajuste γ⁰ → altura del dosel según la ventana de promediado:

| Fuente | 30 m | 90 m | **150 m** | 310 m |
|---|---|---|---|---|
| Sentinel-1 VH (C), 10/01/2026 | 0,011 | 0,028 | 0,027 | 0,025 |
| NISAR HV (L), 08/01/2026 | 0,166 | 0,253 | **0,273** | 0,269 |
| PALSAR-2 HV (L), 2025 | 0,114 | 0,164 | 0,177 | 0,195 |
| SAOCOM HV (L), 10/01/2026 | 0,092 | 0,120 | 0,141 | 0,161 |

En banda L el promediado recupera cerca de diez puntos de R². **Conviene destacar que
el R² sigue subiendo más allá de los 150 m:** el máximo de NISAR cae en los 210 m
(0,275) y PALSAR-2 y SAOCOM siguen subiendo hasta los 310 m (0,195 y 0,161). La ventana
de 150 m, que es del orden de la huella de GEDI, se adopta igual como compromiso: más
allá se promedia bosque ajeno a la huella.

**En banda C no sube.** Su problema no es el speckle: la señal no está.

**La decisión que hay que declarar:** la ventana de 150 m se eligió como compromiso
entre recuperar R² y no salirse de la huella de GEDI. En la corrida actual el R²
sigue subiendo hasta los 210 o 310 m en varias fuentes, de modo que **el óptimo
numérico y el óptimo defendible no coinciden**, y eso hay que decirlo en la memoria
en lugar de esconderlo: es una decisión con criterio explícito, no una propiedad de
la naturaleza. Quien prefiera maximizar R² debe declarar la ventana mayor y asumir
que está promediando bosque ajeno a la huella.

## 4. La saturación: dónde deja de ver cada sensor

| Altura rh95 | S1 VH (C) | NISAR HV (L) |
|---|---|---|
| 0–3 m | −15,65 | −13,24 |
| 18–21 m | −15,47 | −11,47 |
| 21–25 m | −15,12 | −11,08 |
| 25–30 m | −15,13 | **−10,94** |
| **Gana** | **0,52 dB** | **2,19 dB** |

**La banda C es plana**: medio decibel en veinticinco metros de árbol. No es
cuestión de filtrar mejor.

**Y el resultado del curso**: donde el NDVI del TP3 se aplanó (0,888 a los 15–18 m,
y después 0,879, 0,897 y 0,893), la banda L **sigue subiendo** (−11,59 → −11,47 →
−11,08 → −10,94 dB). El óptico ya no ve; la banda L sí.

Los tres sensores de banda L arrancan en valores muy distintos (−13,2, −13,0 y
−18,1 dB) y los tres ganan alrededor de 2 dB en el mismo tramo. **Tres instrumentos
independientes describiendo el mismo fenómeno**: el fenómeno es real.

## 5. La conclusión incómoda, que también hay que declarar

| Sensor | Banda o índice | R² | TP |
|---|---|---|---|
| Sentinel-1 VH | radar C | 0,029 | TP4 |
| NISAR HV | radar L | 0,273 | TP4 |
| Sentinel-2 | NDMI | **0,310** | TP3 |

La banda L es **nueve veces mejor que la C**, pero **no le gana al NDMI del óptico**.
Tres razones, y ninguna es excusa:

1. **GEDI mide altura; la banda L responde a biomasa.** No son la misma variable.
2. **Este bosque es bajo**: la mitad de las huellas no llega a 9 m. Ahí el óptico
   todavía no satura. El experimento está sesgado en contra del radar, y aun así la
   banda L muestra su ventaja justo donde debe: en las franjas de arriba.
3. **El radar arrastra el relieve.** El terrain flattening corrige mucho, no todo.

**La conclusión no es «el radar gana». Es que ningún sensor solo alcanza.** Cada uno
falla donde el otro funciona. Ése es el argumento del TP5, construido con
mediciones.
