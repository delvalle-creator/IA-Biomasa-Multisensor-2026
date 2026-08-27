# TP3 — Orden de ejecución

| Paso | Script | Subcarpeta | Qué hace | Deja / produce |
|---|---|---|---|---|
| 1 | `TP3_01_recortar_sentinel2.py` | `01_Pre_procesamiento/remuestreo` | Recorta Sentinel-2 a la grilla común, con SNAP | `02_Subsets_SNAP_QGIS/Sentinel_2/` |
| 2 | `TP3_02_landsat9.py` | `01_Pre_procesamiento/remuestreo` | Descarga y recorta Landsat 9 | `02_Subsets_SNAP_QGIS/Landsat_8_9/` |
| 3 | `TP3_03_indices.py` | `02_Procesamiento/indices_vegetacion` | NDVI, EVI, NDMI y NBR en todas las escenas | `05_Resultados/02_Rasters/indices/` |
| 4 | `TP3_04_dnbr_incendio.py` | `02_Procesamiento/indices_vegetacion` | dNBR y las **siete clases** de severidad de Key y Benson | `05_Resultados/02_Rasters/incendio/` |
| 5 | `TP3_05_saturacion_y_modelo.py` | `03_Analisis/regresion_lineal` | Cruza con las huellas del TP2 y **mide dónde satura cada índice** | `05_Resultados/04_Tablas/` |
| 6 (último) | `TP3_06_exportar_para_gis.py` | `05_Exportacion` | Estilos `.qml` y área quemada vectorizada | `05_Resultados/02_Rasters/`, `03_Vectores/` |

**El 5 necesita que el TP2 esté corrido**: lee `TP2_LiDAR_GEDI_ICESat2/04_Tablas_de_trabajo/01_Bosque`
y `02_Estepa`. Si esas carpetas están vacías, el script lo avisa y le dice qué
correr antes.

**Sin el `.qml` del paso 6, el ráster de severidad se ve como siete grises casi
iguales**: sus valores 1 a 7 son códigos de clase, no cantidades.
