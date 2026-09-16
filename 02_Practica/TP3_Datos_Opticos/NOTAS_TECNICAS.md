# TP3 — Estimación de biomasa con imágenes ópticas

> **Qué es este archivo.** Notas técnicas del práctico: advertencias, decisiones
> y errores que ya costaron tiempo. No es el punto de entrada. Para saber qué hay
> en cada carpeta, abra `00_LEEME.md`, que encabeza la lista de este práctico.

**Pregunta del práctico:** ¿cuánta biomasa puede explicar el óptico por sí solo?
Segundo eslabón de la comparación: **óptico solo**.

## Qué hay (todo en la grilla común: EPSG:32719, 10 m, 1500 × 1500 px)

| Fuente | Épocas | Resolución | Contenido |
|---|---|---|---|
| Sentinel-2 L2A | línea base, pre, post | 10 m | B2–B12 + SCL, 14 escenas |
| Landsat 9 OLI-2 | línea base, pre, post | 30 m nativo + versión 10 m | 7 bandas de reflectancia + QA_PIXEL, 6 escenas |

Landsat 9 está en **dos versiones**: la nativa de 30 m (el dato fiel) y una
remuestreada a 10 m con interpolación bilineal, para poder apilarla con el resto.
Remuestrear no agrega detalle: la resolución real sigue siendo de 30 m.

## Resultado ya obtenido: el incendio, medido con dNBR

El script `TP3_04_dnbr_incendio.py` compara el **25/11/2025** (última imagen
**limpia** antes del fuego) con el 05/03/2026 (primera después):

| Severidad (Key y Benson) | Bosque | Estepa |
|---|---|---|
| Alta | 9.668,7 ha (43,1 %) | 0,1 ha |
| Moderada-alta | 3.672,0 ha (16,4 %) | 0,9 ha |
| Moderada-baja | 2.825,6 ha (12,6 %) | 15,5 ha |
| Baja | 1.842,8 ha (8,2 %) | 397,0 ha |
| **TOTAL QUEMADO** | **18.009,2 ha (80,2 %)** | **413,5 ha (1,8 %)** |

El NBR del bosque cae de 0,512 a −0,200: **cambia de signo**, la firma
inequívoca de vegetación viva reemplazada por ceniza. La estepa, como control,
queda intacta. Landsat 9 lo confirma de forma independiente: NDVI del bosque
0,78 → 0,27.

### Por qué la fecha pre no es la más cercana al incendio

La escena del 09/01/2026 está más cerca del fuego, pero tiene **humo de los incendios**: su banda
azul vale 0,158 cuando lo normal en el sitio es 0,024. La máscara de nubes del
producto no la detectó (marcó apenas 7 % de cirros); la detecta el script
`TP1_02_detectar_bruma.py` del TP1. Con esa escena el resultado era 16.502 ha
(79,4 %): menos de un punto porcentual de diferencia, porque el NBR usa el
infrarrojo cercano y el de onda corta, que son las bandas menos afectadas por los
aerosoles. El NDVI de esa misma escena, en cambio, se derrumba de 0,80 a 0,34.
Habiendo una escena limpia disponible, se usa la limpia: además sube los píxeles
válidos del 92,3 % al 99,8 %.

## La saturación, medida con los datos del proyecto

Se cruzaron las 690 huellas GEDI válidas del bosque (TP2) con los índices de la
escena limpia del 25/11/2025. Las 690 caen en píxeles con índice utilizable.

| Índice | Modelo ajustado | R² | RMSE |
|---|---|---|---|
| NDVI | altura = 25,52 · NDVI − 11,05 | 0,23 | 6,17 m |
| EVI | altura = 33,12 · EVI − 6,81 | 0,22 | 6,25 m |
| NDMI | altura = 34,66 · NDMI + 0,66 | **0,31** | 5,86 m |
| NBR | altura = 25,33 · NBR − 3,91 | 0,29 | 5,94 m |

El NDVI sube con la altura hasta la franja de 15-18 m (mediana 0,888) y después
se aplana: 0,879, 0,897 y 0,893 en las tres franjas siguientes: **ahí satura**.
El EVI también se aplana (0,549 y 0,550 en las dos últimas).

Ningún índice explica más de un tercio de la altura del dosel (el mejor, el NDMI, el 31 %). Los dos que mejor
andan, NDMI y NBR, son los que usan el infrarrojo de onda corta, es decir, la
banda de mayor longitud de onda del sensor. La tendencia señala hacia dónde ir:
a longitudes de onda más largas, o sea, al radar de banda L del TP4.

## Las figuras

Las figuras de la guía se regeneran con los scripts de
`00_Guia_del_practico/figuras/generadores/`. Cada una se guarda en PNG y en SVG
(editable en Inkscape o Illustrator).
3. Texturas.
4. Modelos contra la referencia GEDI de TP2: regresión lineal y random forest.
5. Importancia de variables, validación cruzada y análisis de residuos.
6. Mapa de biomasa predicha con su incertidumbre, y comparación bosque vs. estepa.

## Scripts

    03_Scripts/01_Pre_procesamiento/remuestreo/          TP3_01_recortar_sentinel2.py, TP3_02_landsat9.py
    03_Scripts/02_Procesamiento/indices_vegetacion/      TP3_03_indices.py, TP3_04_dnbr_incendio.py
    03_Scripts/03_Analisis/regresion_lineal/             TP3_05_saturacion_y_modelo.py
    03_Scripts/05_Exportacion/                           TP3_06_exportar_para_gis.py
