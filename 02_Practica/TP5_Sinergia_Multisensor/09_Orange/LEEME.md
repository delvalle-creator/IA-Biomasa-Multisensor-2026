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
09_Orange` — Orange 3.36 o posterior, no mover el .ows de esta carpeta
(las rutas están guardadas como relativas a ella), y recordar que el flujo VE
los resultados: la regresión formal con partición por bloques vive en los
scripts del TP5, no acá.

## Los parámetros de cada widget

| Widget | Parámetros |
|---|---|
| Bosque (File) | `../04_Tablas_de_trabajo/TP5_dataset_BOSQUE_NW_02.csv` |
| Estepa (File) | `../04_Tablas_de_trabajo/TP5_dataset_ESTEPA_NW_02.csv` |
| Unir recintos (Concatenate) | Agrega la columna de origen con el nombre `recinto` |
| Correlaciones | Hay que elegirla a mano: la variable de referencia es `agbd_Mg_ha` |
| NDVI contra agbd_Mg_ha (Scatter Plot) | Eje X: `NDVI`. Eje Y: `agbd_Mg_ha`. Color: `recinto` |
| PALSAR-2 HV contra agbd_Mg_ha (Scatter Plot) | Eje X: `g0_L_PALSAR2_HV`. Eje Y: `agbd_Mg_ha`. Color: `recinto` |
| Estadísticos por columna (Feature Statistics) | Sin parámetros: muestra todas las columnas |
| Tabla del dataset (Data Table) | Sin parámetros |

## Lo que hay que elegir a mano

Las variables de los dos gráficos de dispersión vienen elegidas y se comprobó
que Orange las reconoce, tanto en la versión 3.39 como en la 3.40. Dos cosas,
en cambio, no están guardadas en el `.ows` y hay que fijarlas en pantalla.

**La variable de referencia del widget Correlaciones**, que en este flujo es
`agbd_Mg_ha`. Es el primer paso del práctico en Orange: sin esa elección el
widget ordena todos los pares de variables entre sí, en lugar de responder
cuál explica mejor la biomasa, que es la pregunta central del TP5. El título
del widget en el lienzo dice cuál elegir.

**Las opciones de dibujo de los gráficos**: la recta de ajuste, el tamaño del
punto, el desplazamiento aleatorio que separa los puntos superpuestos y la
transparencia. Se encienden en el panel de la izquierda de cada gráfico y no
quedan guardadas en el flujo.

En los dos gráficos de dispersión conviene encender la recta de ajuste antes
de discutir la saturación del NDVI, y bajar el tamaño del punto cuando la
estepa satura la pantalla con sus miles de huellas.

## Cómo sacar una figura con calidad

Cada gráfico tiene un botón para guardar la imagen. Conviene guardar en
**SVG** lo que vaya a un informe, porque el texto queda como texto y se puede
corregir después, y en **PNG** lo que vaya a una diapositiva.

Antes de guardar hay que agrandar la ventana del widget. Orange exporta lo
que está viendo, de modo que una ventana chica devuelve una figura apretada,
con los rótulos encimados.
