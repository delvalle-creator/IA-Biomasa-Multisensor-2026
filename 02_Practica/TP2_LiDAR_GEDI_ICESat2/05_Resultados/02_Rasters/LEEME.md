# 02_Rasters — los mapas de biomasa en la grilla común de 500 m

Los crea `TP2_17_mapa_biomasa_GEDI_CCI.py` (carpeta `mapa_biomasa` de los
scripts). Todos en **EPSG:32719**, celda de **500 m** (la del cotejo del paso
13), unidad **Mg/ha**, nodata −9999. Listos para QGIS; las figuras asociadas
están en `../05_Graficos/TP2_mapa_AGB_GEDI_vs_CCI_*.png`.

| Archivo | Qué es |
|---|---|
| `TP2_AGB_GEDI_500m_<recinto>.tif` | mediana de `agbd_Mg_ha` de las huellas GEDI L4A por celda; celda vacía si hay menos de 3 huellas |
| `TP2_AGB_CCI2024_500m_<recinto>.tif` | el mapa CCI Biomass v7 de 2024 (100 m) promediado a la misma celda |
| `TP2_AGB_dif_CCI_menos_GEDI_500m_<recinto>.tif` | CCI − GEDI donde ambos existen (positivo = CCI más alto) |

**El mapa de GEDI tiene huecos a propósito.** GEDI es un muestreo orbital, no
una imagen: donde no pasó o no dejó 3 huellas válidas no hay celda, y
rellenar eso es tarea de un modelo (TP5), no del mapa. El mapa continuo del
CCI no es más cierto por ser continuo: es más modelo.

La tabla por celda (con n de huellas y los tres valores) está en
`../04_Tablas/TP2_mapa_AGB_celdas_<recinto>.csv`.
