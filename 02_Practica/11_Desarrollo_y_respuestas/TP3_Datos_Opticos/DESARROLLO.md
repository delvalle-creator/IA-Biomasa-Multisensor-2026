# TP3 — Desarrollo completo, con los datos expuestos

El TP3 calcula los índices ópticos, cartografía el incendio con el dNBR, y
cierra con el resultado que da sentido al práctico: **medir dónde satura
cada índice**, cruzándolo contra las huellas GEDI del TP2. Son seis pasos
(`03_Scripts\00_ORDEN_DE_EJECUCION.md`); el 5 exige el TP2 corrido.

## 1. La ejecución, paso a paso

    conda activate aoi
    cd C:\Temp\CURSO_BIOMASA_2026\02_Practica\TP3_Datos_Opticos\03_Scripts

**Pasos 1 y 2** recortan Sentinel-2 a la grilla común (SNAP) y descargan y
recortan Landsat 9. **Paso 3** (`TP3_03_indices.py`): NDVI, EVI, NDMI y NBR
sobre cada escena. **Paso 4** (`TP3_04_dnbr_incendio.py`): el dNBR
pre/post y las siete clases de severidad de Key y Benson. **Paso 5**
(`TP3_05_saturacion_y_modelo.py`): el cruce con GEDI — por cada huella se
promedia el índice en una ventana de 3×3 píxeles (30 × 30 m) de la escena
**pre-incendio**, porque GEDI es del bosque en pie. **Paso 6** exporta
estilos `.qml` y el área quemada vectorizada.

Las escenas empleadas: pre-incendio **S2B del 25/11/2025** (la del
9/1/2026, más próxima al fuego, se descarta por el humo del incendio —
véase la P1), post
**S2B del 5/3/2026**.

## 2. Los resultados, con los datos a la vista

### 2.1 Los índices por época (paso 3, salida real)

| Escena | Sitio | Píxeles útiles | NDVI mediano | NDMI mediano |
|---|---|---|---|---|
| pre (25/11/2025) | Bosque | 99,9 % | **0,802** | 0,236 |
| pre (25/11/2025) | Estepa | 100,0 % | 0,216 | −0,172 |
| post (5/3/2026) | Bosque | 99,8 % | **0,301** | −0,246 |
| post (5/3/2026) | Estepa | 99,5 % | 0,201 | −0,183 |

El bosque cae de 0,80 a 0,30 en NDVI y pierde toda su señal de agua (el
NDMI pasa de +0,24 a −0,25); la estepa casi no se mueve.

### 2.2 El incendio (paso 4, salida real)

**Bosque** — píxeles válidos en ambas fechas: 99,8 %.

| Clase | % | Hectáreas |
|---|---|---|
| Regeneración alta | 0,04 % | 8,3 |
| Regeneración baja | 1,14 % | 257,0 |
| Sin cambio | 18,58 % | 4.170,7 |
| Severidad baja | 8,21 % | 1.842,8 |
| Severidad moderada-baja | 12,59 % | 2.825,6 |
| Severidad moderada-alta | 16,36 % | 3.672,0 |
| **Severidad alta** | **43,08 %** | **9.668,7** |
| **QUEMADO (severidad ≥ baja)** | **80,24 %** | **18.009,2** |

dNBR mediano en el área quemada: **0,698**.

**Estepa** — píxeles válidos: 99,4 %.

| Clase | % | Hectáreas |
|---|---|---|
| **Sin cambio** | **96,47 %** | 21.583,8 |
| Quemado (severidad ≥ baja) | 1,85 % | 413,5 |

dNBR mediano en el área quemada: 0,125.

### 2.3 La saturación (paso 5, salida real): el resultado del práctico

Huellas cruzadas: 690 en el bosque, 3.083 en la estepa. La tabla de
saturación (índice mediano por franja de altura GEDI):

| Altura (m) | n | NDVI | EVI | NDMI | NBR |
|---|---|---|---|---|---|
| 0–3 | 132 | 0,712 | 0,437 | 0,160 | 0,413 |
| 3–6 | 259 | 0,769 | 0,446 | 0,211 | 0,470 |
| 6–9 | 80 | 0,797 | 0,464 | 0,236 | 0,525 |
| 9–12 | 48 | 0,832 | 0,497 | 0,267 | 0,559 |
| 12–15 | 35 | 0,855 | 0,517 | 0,298 | 0,587 |
| 15–18 | 22 | 0,888 | 0,544 | 0,339 | 0,643 |
| 18–21 | 50 | 0,879 | 0,532 | 0,317 | 0,625 |
| 21–25 | 46 | 0,897 | 0,549 | 0,352 | 0,656 |
| 25–30 | 17 | 0,893 | 0,550 | 0,348 | 0,642 |

Bajando por la columna del NDVI: sube con la altura mientras el dosel se
cierra y **a partir de los ~15–18 m se aplana** (0,888 → 0,897 → 0,893 con
diez metros más de árbol). El EVI aguanta apenas más; el NDMI y el NBR,
parecido. Ese techo es la limitación estructural del óptico, y es la razón
de ser del TP4.

El modelo simple (índice → altura) sobre los dos sitios juntos (n = 3.773):
el mejor índice es el NDMI con **R² 0,416 y RMSE 3,08 m**; el NDVI da
0,382 y 3,17 m. Ese R² es engañosamente amable: junta dos nubes separadas
(bosque alto, estepa baja) y el índice acierta sobre todo al distinguirlas.
Restringido al bosque, que es donde importa, el ajuste se desploma: el
mejor modelo óptico ronda **R² 0,3 con un error superior a los 5 m sobre un
bosque de 5,07 m de altura mediana** (la validación por bloques del TP5 lo
cifra en 0,38 y 5,39 m para el óptico solo; la guía general, en 0,31 y
5,86 m). Esa es la cifra que el práctico pide interpretar.

## 3. Las figuras del procesamiento

En `capturas\`:

- `S2_galeria_BOSQUE_NW_02.png` y `S2_galeria_ESTEPA_NW_02.png` — **las
  siete escenas Sentinel-2 procesadas de cada sitio**, en color verdadero,
  por época: las cuatro de la línea de base, las dos pre-incendio —
  incluida la del 9/1/2026, cubierta por el **humo del incendio**, visible
  a simple vista, y por eso descartada — y la post-incendio.
- `L9_galeria_BOSQUE_NW_02.png` y `L9_galeria_ESTEPA_NW_02.png` — las tres
  escenas Landsat 9 de cada sitio (línea de base, pre y post), remuestreadas
  a la grilla común de 10 m.
- `tp3_fig_composiciones.png` — las composiciones color pre y post de los
  dos sitios: el incendio a simple vista.
- `TP3_ndvi_pre_post.png` — el NDVI antes y después, bosque y estepa, de la
  corrida de esta guía.
- `tp3_fig_dnbr_severidad.png` y `TP3_dnbr_severidad.png` — el dNBR y las
  clases de severidad: el bosque arrasado, la estepa intacta.
- `tp3_fig_firma_espectral.png` — la firma espectral por cubierta: por qué
  cada índice usa las bandas que usa.
- `tp3_fig_saturacion.png` — la curva de saturación de la Tabla 18, dibujada.

## 4. Respuestas modelo a las preguntas del práctico

**P1. La escena del 9 de enero de 2026 fue descartada pese a ser la más
próxima al incendio. Fundamente la decisión con al menos dos evidencias
independientes.**

Primera evidencia: la **reflectancia del azul** — el detector del TP1 la
marca afectada; lo que cubre la escena no es bruma atmosférica cualquiera,
es **el humo del propio incendio**, activo en esos días, que eleva el azul
de manera difusa sin formar nubes que la máscara SCL clasifique. Segunda evidencia, independiente de la primera: los **índices
calculados sobre esa escena se apartan** de los de la escena limpia del
25/11/2025 en zonas que el fuego aún no había tocado — un corrimiento
espectral generalizado, no un cambio localizado como el que produce el
fuego. Cada evidencia sola podría discutirse; juntas, y siendo de naturaleza
distinta (una radiométrica del azul, una de consistencia temporal de los
índices), la decisión queda fundamentada. La lección excede la escena: la
proximidad temporal no es un mérito si la atmósfera contamina la señal.

**P2. ¿Por qué el NBR tolera la bruma que inutiliza al NDVI de la misma
escena?**

Por las bandas que usa cada uno. El NDVI combina el **rojo (~665 nm)** con
el infrarrojo cercano: el rojo está en plena zona de dispersión de los
aerosoles, que crece hacia las longitudes de onda cortas, así que la bruma
lo infla y el NDVI baja artificialmente. El NBR combina el infrarrojo
cercano (~842 nm) con el **SWIR (~2.190 nm)**: las dos bandas más largas
del juego, donde los aerosoles finos del humo dispersan poco. El humo
atraviesa casi transparente las bandas del NBR y opaca las del NDVI — mismo
píxel, misma atmósfera, distinta sensibilidad. Por eso el dNBR sigue siendo
utilizable en fechas cercanas al fuego en las que el NDVI ya no lo es.

**P3. Observe la Tabla 18 por columnas. ¿En qué franja de altura deja de
crecer cada índice, y por qué?**

En la corrida de este proyecto (§ 2.3): el **NDVI** crece con firmeza hasta
los 15–18 m (0,888) y de ahí en adelante queda clavado entre 0,88 y 0,90 —
diez metros más de árbol no lo mueven. El **EVI** llega a 0,544 en 15–18 m
y termina en 0,550: mismo techo, apenas más tardío, con su ventaja teórica
sobre dosel denso reducida a centésimas. El **NDMI** y el **NBR** se
aplanan en la misma franja (0,34–0,35 y 0,64–0,66). La explicación es la
geometría de la observación: un índice óptico ve el **dosel desde arriba**;
mientras el dosel está abierto, más altura significa más copa visible y el
índice sube; cuando el dosel se cierra —en esta lenga, hacia los 15 m— lo
que hay debajo deja de verse, y el tronco puede seguir acumulando biomasa
sin que ningún cociente de reflectancias se entere. El índice no mide
biomasa: mide cuánta luz intercepta la primera capa de hojas.

**P4. El mejor ajuste alcanza un R² de 0,31 y un error de 5,86 m sobre un
bosque de 5,07 m de altura mediana. ¿Qué conclusión metodológica se
desprende para la estimación de biomasa con datos ópticos?**

Que el óptico solo **no puede sostener una estimación de biomasa en este
bosque**: el error del modelo de altura supera a la propia mediana de
altura (5,86 > 5,07), o sea que la predicción típica se equivoca en más de
un bosque entero. Y como la biomasa crece de forma no lineal con la altura
(alometría de exponente > 2), ese error se **amplifica** al convertir
altura en Mg/ha. La causa está en la P3: pasada la clausura del dosel, la
señal óptica ya no contiene la información. La conclusión no es «el óptico
no sirve» — sirve para cartografiar el incendio, las clases de cobertura y
la fenología — sino que **para biomasa el óptico necesita un socio que vea
la estructura**: el radar de banda L (TP4) y el LiDAR (TP2), que es
exactamente la síntesis que ensaya el TP5.

**P5. La estepa permanece sin cambio en el 96,5 % de su superficie. ¿Qué
habría significado que ese porcentaje fuera considerablemente menor?**

La estepa funciona como **control experimental**: apenas fue tocada por el
fuego (1,85 % quemado), de modo que allí el dNBR «verdadero» es cero casi
en todas partes. Que el procedimiento mida 96,47 % sin cambio confirma que
la cadena — correcciones, co-registro de fechas, umbrales de Key y Benson —
no fabrica cambio donde no lo hay: el falso positivo queda acotado a un par
de puntos porcentuales. Si el porcentaje hubiera sido considerablemente
menor, el método estaría detectando «quemado» en terreno intacto — por
diferencia de fechas fenológica, por desajuste geométrico o por umbral mal
puesto — y entonces **las 18.009,2 ha del bosque serían indefendibles**,
porque no habría manera de saber qué parte es fuego y qué parte es
artefacto. Sin control no hay cifra creíble; con el control limpio, el
80,2 % del bosque queda en pie como resultado.

## 5. De dónde sale cada cifra

Los logs de la corrida de los pasos 3 a 6 y sus tablas:
`05_Resultados\04_Tablas\estadisticas_incendio.csv` (las clases y
hectáreas), `saturacion.csv` (la tabla de la § 2.3), `cruce_gedi_indices.csv`
(cada huella con sus índices), `modelo_altura.txt` (los ajustes), y
`05_Resultados\03_Vectores\TP3_incendio.gpkg` (54.683 polígonos de
severidad en el bosque, 9.143 en la estepa). Los rásters, en
`05_Resultados\02_Rasters\indices\` e `incendio\`.
