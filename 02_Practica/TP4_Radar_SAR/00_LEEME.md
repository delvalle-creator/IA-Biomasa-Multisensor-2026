# TP4 — Radar: por qué la banda L y no la C

El práctico está **resuelto de punta a punta**. Las únicas carpetas vacías son las que deben estarlo, y cada una dice por qué en la tabla de abajo.

> Los números de esta tabla los produce `00_COMUN/contar_archivos.py`, que
> los lee del disco. Si dejan de coincidir, vuelva a correrlo en lugar de
> corregirlos a mano.


## El recorrido, en orden

| Carpeta | Qué hay | Archivos |
|---|---|---|
| `00_Guia_del_practico/` | **Empiece por acá:** la guía sintética en PDF, con su LEEME, más los objetivos y las figuras con los generadores que las rehacen. El desarrollo completo, en el capítulo 6 de la guía teórico-práctica | 21 |
| `01_Prompt_IA/` | El prompt inicial con sus defectos, el análisis, el prompt corregido y la verificación | 5 |
| `02_Subsets_SNAP_QGIS/` | γ⁰ de los cuatro radares en la grilla común, los recortes con fase y las máscaras | 605 |
| `03_Scripts/` | Los diez scripts, los grafos de SNAP y el orden de ejecución | 27 |
| `04_Tablas_de_trabajo/` | El TP4 usa las huellas del TP2; ver su LEEME | 1 |
| `05_Resultados/` | Rásters en dB listos para QGIS y los gráficos | 172 |
| `06_Bibliografia/` | Artículos, manuales, fichas de los radares y enlaces | 6 |
| `07_Preguntas_y_entrega/` | El material de BIOMASS banda P. **Aquí deja el estudiante sus respuestas y su entrega** | 3 |
| `08_Grafos_SNAP/` | Los grafos del Graph Builder | 27 |
| | Los tres archivos de la raíz: presentación, notas técnicas y de dónde salen los insumos | 3 |
| | **TOTAL** | **870** |

El práctico completo, con su fundamentación, está en la guía teórico-práctica: `02_Practica\00_Guia_teorica_practica`.

## Los diez scripts

| # | Script | Necesita SNAP |
|---|---|---|
| 1 | `TP4_01_procesar_sar.py` — γ⁰ con terrain flattening (S1 y SAOCOM) | sí |
| 2 | `TP4_02_recortar_crudo.py` — recortes con fase, para polarimetría | sí (opcional) |
| 3 | `TP4_03_recortar_nisar.py` — NISAR GCOV, ya viene corregido | no |
| 4 | `TP4_04_palsar2_mosaico.py` — mosaico de JAXA | no |
| 5 | `TP4_05_mascara_validez.py` — sombra, acortamiento de pendiente e inversión por relieve | no |
| 6 | `TP4_06_speckle.py` — **mide el speckle y demuestra cuánto R² recupera el promediado** | no |
| 7 | `TP4_07_contraste_C_vs_L.py` — el contraste bosque − estepa | no |
| 8 | `TP4_08_saturacion_radar.py` — cruza con GEDI. **El cierre del práctico** | no |
| 9 | `TP4_09_exportar_para_qgis.py` — pasa a dB y deja los rásters listos | no |

Los 1 a 5 ya fueron ejecutados: sus resultados están en `02_Subsets_SNAP_QGIS`. Usted corre
del 6 en adelante. El 6 necesita `scipy` (`conda install -c conda-forge scipy`).

Los scripts 6 a 8 crean `05_Resultados/04_Tablas` y `05_Resultados/02_Rasters/filtrados`
al ejecutarse. Si no las ve, todavía no los corrió.

## Lo que este práctico demuestra, medido

**El contraste bosque − estepa** (dos sitios vecinos; lo único que cambia es la biomasa):

| Sensor | Banda | HV / VH |
|---|---|---|
| Sentinel-1 | C | 4,2 dB |
| NISAR | L | **9,9 dB** |
| PALSAR-2 | L | **11,6 dB** |
| SAOCOM | L | **11,7 dB** |

**La saturación** (γ⁰ de 0–3 m a más de 21 m de dosel):

- **Sentinel-1 (C): gana 0,53 dB.** Plano. No distingue un renoval de un bosque maduro.
- **NISAR (L): gana 2,59 dB.** Y donde el NDVI del TP3 se aplanó (0,896 → 0,894 sobre
  los 21 m), **la banda L sigue subiendo**: −12,22 → −11,73 → −11,55 dB.

**El control cruzado:** NISAR y PALSAR-2, misiones de agencias distintas, dan −13,2 y
−12,5 dB sobre el mismo bosque. Coinciden dentro de 1 dB sin haberse puesto de
acuerdo.

## Las dos cosas que definen si el producto sirve

**γ⁰, nunca σ⁰.** En una ladera, σ⁰ hace que la misma vegetación se vea brillante de
un lado y oscura del otro. En un bosque andino esa señal geométrica **domina** y se
confunde con biomasa (Small, 2011). El `localIncidenceAngle` es **diagnóstico, no
corrección**.

**Trabajar en γ⁰ lineal y pasar a dB al final.** El promedio de los logaritmos no es
el logaritmo del promedio: filtrar en dB sesga hacia abajo.

## Para abrirlos en QGIS

Corra el script 9 y use `05_Resultados/02_Rasters/*_dB.tif`. Los originales están en
γ⁰ **lineal**, con mediana 0,16 y máximo **202** en NISAR: el estiraje por defecto
los muestra negros.

**Para comparar SAOCOM con NISAR fije los mismos min/max a mano**: HH de −28 a −2 dB,
HV de −36 a −7 dB. Esos límites abarcan el rango real de los cuatro casos y no
recortan nada. Si deja que cada capa se estire sola, los 4,8 dB de diferencia real
entre los dos sensores desaparecen.

## Lo que NO está, y es información

- **No hay `04_Tablas_de_trabajo`**: el TP4 usa las huellas del TP2.
- **La línea de base SAOCOM está completa** (7 productos), pero **sin procesar**:
  ninguno pasó todavía por `TP4_01_procesar_sar.py`. Las 2 dual-pol S4 que
  faltaban (27/10/2023 y 23/01/2024) llegaron el 16/07/2026, con identificadores
  distintos a los del pedido. **Son ASCENDENTES**, mientras que las 5 quad-pol son
  descendentes: no se apilan ni se promedian juntas. Sirven como control de
  geometría —cuánto de γ⁰ depende de cómo mira el radar y no del bosque—, no como
  insumo. Se comparan contra la fecha descendente más próxima: 27/10 contra 29/11
  y 23/01 contra 16/01.
- **La banda S de NISAR no está confirmada.** Se distribuye por Bhoonidhi (ISRO) y su
  producción diaria arrancó el 08/07/2026. Ver `01_Prompt_IA/04_Verificacion/`.
- **El R² máximo es 0,25**, y no le gana al NDMI del óptico (0,30). No contradice
  nada: GEDI mide altura y la banda L responde a biomasa; y este bosque es bajo, así
  que el experimento está sesgado en contra del radar. Está explicado en el informe.
