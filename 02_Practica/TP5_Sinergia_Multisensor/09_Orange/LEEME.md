# 09_Orange — flujo de Orange Data Mining del TP5

`TP5_flujo_sinergia_multisensor.ows` abre el dataset multisensor del práctico
(`../04_Tablas_de_trabajo/TP5_dataset_*.csv`): cada fila es una huella GEDI
con su biomasa (`agbd_Mg_ha`), los índices ópticos del TP3 (`NDVI`, `EVI`,
`NDMI`, `NBR`) y la retrodispersión radar del TP4 (banda C: `g0_C_VH/VV`;
banda L: SAOCOM, NISAR y PALSAR-2, HH y HV). Es decir: **ópticos y radares en
un solo lugar**, contra la referencia LiDAR.

Qué hay adentro: **Correlations** ordena qué variable explica mejor la
biomasa (la pregunta central del TP5); dos **Scatter Plot** muestran los dos
extremos — `NDVI` (que satura en bosque denso) y `g0_L_PALSAR2_HV` (la banda
L, que penetra el dosel); **Feature Statistics** y **Data Table** para
recorrer el dataset.

Requisitos y reglas: los mismos del LEEME de `TP2_LiDAR_GEDI_ICESat2\
09_Orange` — Orange 3.36+, no mover el .ows de esta carpeta (rutas
relativas), y recordar que el flujo VE los resultados: la regresión formal
con partición por bloques vive en los scripts del TP5, no acá.
