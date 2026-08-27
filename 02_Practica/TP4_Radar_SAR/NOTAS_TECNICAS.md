# TP4 — Sensibilidad de los radares SAR a la biomasa: bandas C, L y P

> **Qué es este archivo.** Notas técnicas del práctico: advertencias, decisiones
> y errores que ya costaron tiempo. No es el punto de entrada. Para saber qué hay
> en cada carpeta, abra `00_LEEME.md`, que encabeza la lista de este práctico.

**Pregunta del práctico:** ¿por qué la banda L y no la C? Tercer eslabón:
**radar solo**. Es el práctico con más carga conceptual del curso.

## Estado: completo. Diez scripts, bandas C, L y P, y guía con figuras

## Qué hay (todo en la grilla común, γ⁰ LINEAL)

| Fuente | Banda | Épocas | Polarización | Nº |
|---|---|---|---|---|
| Sentinel-1 GRD | C | las 4 | VV + VH, track 164 asc. | 14 |
| Sentinel-1 SLC | C | las 4 | VV + VH, track 164 asc. | 14 |
| SAOCOM-1B L1A | L | pre, post | HH + HV (S4DP, desc.) | 3 |
| SAOCOM-1A/1B L1A | L | línea base 2023-24 | **quad-pol (HH+HV+VH+VV)** | 5 |
| NISAR GCOV | L | pre-incendio | HH + HV | 3 fechas × 2 AOI |
| PALSAR-2 mosaico anual | L | 2023, 2024, 2025 | HH + HV | 3 años × 2 AOI |
| ALOS-1 PALSAR (en `00_COMUN`) | L | histórico 2007-10 | **quad-pol completo** | 5 fechas |

También: `02_Subsets_SNAP_QGIS/00_Recortes_crudos_fase/` (SLC y SAOCOM con la fase intacta,
para InSAR/polarimetría) y `02_Subsets_SNAP_QGIS/mascaras/` (máscaras de validez).

## El resultado que da sentido a todo el práctico

Contraste bosque − estepa en la mediana de γ⁰, con datos casi simultáneos:

| Sensor | Banda | Pol. | Contraste |
|---|---|---|---|
| Sentinel-1 (10/01/2026) | C | VV | 3,5 dB |
| Sentinel-1 (10/01/2026) | C | VH | 4,2 dB |
| NISAR (08/01/2026) | L | HH | 8,1 dB |
| NISAR (08/01/2026) | L | HV | **9,9 dB** |
| PALSAR-2 (2025) | L | HV | **11,7 dB** |

**La banda L separa el bosque de la estepa con casi el triple de contraste que la
banda C, y el máximo está en HV** — la polarización cruzada, que responde a la
dispersión de volumen de troncos y ramas gruesas. Eso *es* la señal de biomasa.
Además, NISAR y PALSAR-2 (misiones y agencias distintas) coinciden en el bosque:
−13,2 dB y −12,5 dB en HV. Control cruzado de calibración independiente.

## El concepto que decide la validez del producto: γ⁰, no σ⁰

En relieve fuerte **σ⁰ no sirve**: normaliza por un área plana que no existe. Se
usa **γ⁰ con Terrain Flattening** (DEM Copernicus GLO-30), que normaliza por el
área realmente iluminada. El `localIncidenceAngle` que acompaña a cada producto
es **diagnóstico**, no una segunda corrección.

Nota: NISAR GCOV y el mosaico PALSAR-2 **ya vienen con la corrección aplicada**;
Sentinel-1 y SAOCOM hay que corregirlos (script `TP4_01_procesar_sar.py`).

## Lo medido en el práctico

### El contraste bosque − estepa (fechas casi simultáneas, bosque en pie)

| Sensor | Banda | HH / VV | HV / VH |
|---|---|---|---|
| Sentinel-1 (10/01/2026) | C | 3,5 dB | 4,2 dB |
| SAOCOM (10/01/2026) | L | 8,1 dB | **11,7 dB** |
| NISAR (08/01/2026) | L | 8,0 dB | **9,9 dB** |
| PALSAR-2 (2025) | L | 8,3 dB | **11,6 dB** |

La banda L separa los dos sitios con casi el triple de contraste que la C, y el
máximo está siempre en la polarización cruzada. NISAR y PALSAR-2, misiones de
agencias distintas, coinciden dentro de 1 dB sobre el mismo bosque (−13,2 y
−12,5 dB en HV): control cruzado de calibración independiente.

### El speckle: cuánta señal se come, y cuánta recupera el promediado

R² del ajuste γ⁰ → altura del dosel según la ventana de promediado:

| Fuente | 30 m | 90 m | **150 m** | 310 m |
|---|---|---|---|---|
| Sentinel-1 VH (C) | 0,011 | 0,023 | 0,026 | 0,025 |
| NISAR HV (L) | 0,152 | 0,229 | **0,245** | 0,221 |
| PALSAR-2 HV (L) | 0,104 | 0,143 | 0,153 | 0,159 |

En banda L el promediado recupera casi diez puntos de R², con un óptimo alrededor
de los 150 m; más allá, la ventana empieza a promediar bosque ajeno a la huella.
En banda C no sube: **su problema no es el speckle, es que la señal no está.**

### La saturación: γ⁰ por franja de altura (ventana 150 m)

| Altura rh95 | S1 VH (C) | NISAR HV (L) | PALSAR-2 HV (L) | SAOCOM HV (L) |
|---|---|---|---|---|
| 0–3 m | −16,19 | −14,32 | −13,65 | −18,56 |
| 12–15 m | −15,78 | −12,17 | −11,87 | −16,96 |
| 18–21 m | −16,00 | −12,22 | −11,84 | −16,87 |
| 21–25 m | −15,63 | −11,73 | −11,41 | −16,44 |
| 25–30 m | −15,76 | **−11,55** | −11,69 | −16,60 |
| **Gana** | **0,53 dB** | **2,59 dB** | **2,16 dB** | **1,98 dB** |

**El resultado del curso:** donde el NDVI del TP3 se aplanó (0,896 → 0,894 sobre
los 21 m), la banda L todavía sigue subiendo (−12,22 → −11,73 → −11,55 dB). El
óptico ya no ve; la banda L sí.

### La conclusión honesta

| Sensor | Banda o índice | R² | RMSE | TP |
|---|---|---|---|---|
| Sentinel-1 VH | radar, banda C | 0,03 | 7,6 m | TP4 |
| Sentinel-2 | NDVI | 0,19 | 6,9 m | TP3 |
| NISAR HV | radar, banda L | 0,25 | 7,1 m | TP4 |
| Sentinel-2 | NDMI | 0,30 | 6,5 m | TP3 |

La banda L es ocho veces mejor que la C, pero no le gana al NDMI del óptico. Y no
contradice nada: GEDI mide **altura** y la banda L responde a **biomasa**; este
bosque es bajo (la mitad de las huellas no llega a 9 m), y ahí el óptico todavía
no satura; y el radar arrastra el relieve. **Ningún sensor solo alcanza: ése es el
argumento del TP5, construido con mediciones y no con citas.**

## Scripts, en orden de ejecución

| # | Script | Necesita SNAP | Estado |
|---|---|---|---|
| 1 | `01_Pre_procesamiento/terrain_flattening/TP4_01_procesar_sar.py` | sí | ya ejecutado |
| 2 | `01_Pre_procesamiento/correccion_geometrica/TP4_02_recortar_crudo.py` | sí | ya ejecutado (opcional) |
| 3 | `01_Pre_procesamiento/TP4_03_recortar_nisar.py` | no | ya ejecutado |
| 4 | `01_Pre_procesamiento/TP4_04_palsar2_mosaico.py` | no | ya ejecutado |
| 5 | `04_Validacion/efecto_pendiente/TP4_05_mascara_validez.py` | no | ya ejecutado |
| 6 | `02_Procesamiento/filtro_speckle/TP4_06_speckle.py` | no | **lo corre el alumno** |
| 7 | `03_Analisis/contraste_bandas/TP4_07_contraste_C_vs_L.py` | no | **lo corre el alumno** |
| 8 | `03_Analisis/saturacion/TP4_08_saturacion_radar.py` | no | **lo corre el alumno** |
| 9 | `05_Exportacion/TP4_09_exportar_para_qgis.py` | no | **lo corre el alumno** |
| 10 | `03_Analisis/indices_polarimetricos/TP4_10_indices_polarimetricos.py` | sí | **lo corre el alumno** |
| 11 | `01_Pre_procesamiento/TP4_11_inspeccionar_biomass_L2A.py` | no | pendiente: exige descomprimir un L2A |

Los grafos de SNAP (`.xml`) están junto a los scripts que los usan.
El TP4_06 necesita `scipy` (`conda install -c conda-forge scipy`).

## Guía y figuras

El desarrollo del práctico, con sus tablas y referencias, está en el capítulo 6
de la guía teórico-práctica (`02_Practica\00_Guia_teorica_practica`).

Las figuras se regeneran con `00_Guia_del_practico/figuras/generadores/`; cada una
se guarda en PNG (para el Word) y SVG (editable). Las versiones editables en
PowerPoint nativo están en `TP4_Radar_SAR/00_Guia_del_practico/figuras/editables_pptx/`.

## Pendiente de datos

Las 2 SAOCOM dual-pol S4 de bosque de la línea de base (27/10/2023 y 23/01/2024).
No son imprescindibles: la serie quad-pol ya cubre la línea de base y la
polarimetría completa. Ver `00_COMUN/08_Originales_crudos/01_base/SAOCOM/LEEME.md`.

## Lo que queda para profundizar

1. Polarimetría completa (descomposiciones) con las quad-pol de SAOCOM y ALOS-1.
2. Series temporales: estabilidad de γ⁰ y efecto de la humedad entre fechas.
3. Texturas y cocientes de polarización como predictores adicionales.
