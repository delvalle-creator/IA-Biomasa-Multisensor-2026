# TP1 — Búsqueda inteligente y evaluación crítica de datos

> **Qué es este archivo.** Notas técnicas del práctico: advertencias, decisiones
> y errores que ya costaron tiempo. No es el punto de entrada. Para saber qué hay
> en cada carpeta, abra `00_LEEME.md`, que encabeza la lista de este práctico.

**Pregunta del práctico:** ¿qué datos existen para estimar biomasa en estos dos
sitios, cuáles sirven de verdad, y cómo se justifica cada elección?

Este práctico es el fundamento de los otros cuatro: acá no se procesa nada, se
**busca, se audita y se decide**. El producto central es la matriz de datos.

## Qué hay

- `05_Resultados/04_Tablas/matriz_datos.csv` — **el producto central**: 15
  fuentes evaluadas, con período, resolución, bandas, cobertura verificada del
  AOI, vía de acceso y credenciales necesarias.
- `02_Subsets_SNAP_QGIS/03_Tablas/manifiesto_adquisiciones.xlsx` — las listas de descarga finales.
- `05_Resultados/05_Graficos/linea_tiempo.png` — las fechas de cada sensor.
- `02_Subsets_SNAP_QGIS/03_Tablas/inventario.csv` — inventario de los productos adquiridos.
- La sección 3.7 de la guía teórico-práctica (`02_Practica\00_Guia_teorica_practica`) —
  **por qué se eligió cada producto**, con las limitaciones declaradas de antemano.
- `01_Prompt_IA/03_Prompts_corregidos/PROMPT_IA.pdf` — el prompt que reconstruye
  todo el flujo de trabajo.

## La lección central del práctico

**El catálogo miente por omisión.** Buscar por un rectángulo devuelve todo lo que
lo *toca*, no lo que lo *cubre con dato*. Tres casos reales de este trabajo:

1. **NISAR:** de 9 gránulos hallados, 6 tenían la huella sobre el AOI pero solo
   un 15 % de píxeles con dato real (el AOI caía en el borde de la franja).
   Se descartaron. Solo 3 servían.
2. **Sentinel-2 del 22/10/2023:** el catálogo devolvió el L1C en vez del L2A
   porque el L2A había sido reprocesado y cambiado de nombre.
3. **Nubosidad:** la que informa el catálogo es de la escena entera, no del AOI.

La verificación siempre se hace **contando píxeles válidos dentro del AOI**, no
leyendo metadatos.

## Scripts

    03_Scripts/01_Consulta_catalogos/      TP1_01_verificar_cobertura.py, TP1_02_detectar_bruma.py,
                                          TP1_03_descargar_sentinel.py, TP1_04_descargar_landsat.py,
                                          TP1_05_descargar_gedi.py
    03_Scripts/02_Disponibilidad_imagenes/ TP1_06_alos_nisar_informe.py, TP1_07_descargar_nisar.py,
                                          TP1_08_descargar_biomass.py
    03_Scripts/03_Exportacion_inventario/  TP1_09_inventario.py, TP1_10_reconstruir_diccionario.py

## El SAOCOM de la línea de base 2023-24

Los 7 productos SAOCOM de la línea de base (5 quad-pol descendentes y 2 dual-pol
S4 ascendentes) están descargados y figuran en `inventario.csv`; no están
procesados a γ⁰, y por eso `TP4_Radar_SAR/02_Subsets_SNAP_QGIS/SAOCOM` tiene sólo
las épocas pre y post. Cómo procesarlos está dicho en el orden de ejecución del
TP4.
