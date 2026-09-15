# 09_Orange — flujos de Orange Data Mining del TP2

Tres flujos listos para abrir con **Orange Data Mining** (versión 3.36 o
posterior; probados con 3.40). Instalación sugerida: el instalador de
https://orangedatamining.com, o `pip install orange3` en un entorno de
Miniforge propio (NO en el entorno `aoi`, para no mezclar dependencias).

**No mover los .ows de esta carpeta**: las rutas a las tablas están guardadas
como relativas a la carpeta del flujo (`../05_Resultados/04_Tablas/...`), que
es lo que hace que funcionen en cualquier computadora sin tocar nada. Si se
copia un flujo a otro lado, Orange va a pedir el archivo a mano.

| Flujo | Qué muestra |
|---|---|
| `TP2_flujo_GEDI_biomasa.ows` | Las huellas L4A con su biomasa: distribución de `agbd_Mg_ha`, caja por recinto, `rh98` contra biomasa. La referencia del curso, mirada de frente. |
| `TP2_flujo_ATLAS_control_terreno.ows` | El control de terreno del paso 15: distribución del `delta_terreno_m`, cajas por veredicto (`PASA`/`DESCARTADO`) y el gráfico clave — delta contra `h_canopy_m`: los segmentos con suelo malo son los del dosel inflado. Requiere haber corrido `TP2_15`. |
| `TP2_flujo_CCI_cotejo.ows` | La dicotomía del anexo, huella por huella: CCI 2024 contra L4A (comparar contra la diagonal 1:1 a ojo: ejes iguales), y CCI contra la pendiente del terreno. |

En cada flujo, los dos widgets **File** cargan bosque y estepa y
**Concatenate** los une agregando la columna `recinto`: por eso los gráficos
pueden colorear y agrupar por recinto.

Estos flujos VEN los resultados: no los producen ni los modifican. La
autoridad de cada cifra sigue siendo el script numerado que la generó.

## Los parámetros de cada widget

Las tres tablas siguientes dicen qué trae elegido cada widget. Si alguno
abriera vacío —cosa que puede pasar con una versión de Orange muy distinta de
aquella en que se guardaron—, acá está exactamente qué elegir.

### `TP2_flujo_GEDI_biomasa.ows`

| Widget | Parámetros |
|---|---|
| Bosque (File) | `../05_Resultados/04_Tablas/biomasa_BOSQUE_NW_02.csv` |
| Estepa (File) | `../05_Resultados/04_Tablas/biomasa_ESTEPA_NW_02.csv` |
| Unir recintos (Concatenate) | Agrega la columna de origen con el nombre `recinto` |
| Distribución de agbd_Mg_ha | Variable: `agbd_Mg_ha` |
| agbd_Mg_ha por recinto (Box Plot) | Variable: `agbd_Mg_ha`. Agrupar por: `recinto` |
| rh98 contra agbd_Mg_ha (Scatter Plot) | Eje X: `rh98`. Eje Y: `agbd_Mg_ha`. Color: `recinto` |
| Estadísticos por columna (Feature Statistics) | Sin parámetros: muestra todas las columnas |
| Tabla de huellas (Data Table) | Sin parámetros |

### `TP2_flujo_ATLAS_control_terreno.ows`

| Widget | Parámetros |
|---|---|
| Bosque (File) | `../05_Resultados/04_Tablas/TP2_control_terreno_ATL08_BOSQUE_NW_02_operacional.csv` |
| Estepa (File) | `../05_Resultados/04_Tablas/TP2_control_terreno_ATL08_ESTEPA_NW_02_operacional.csv` |
| Unir recintos (Concatenate) | Agrega la columna de origen con el nombre `recinto` |
| Distribución de delta_terreno_m | Variable: `delta_terreno_m` |
| delta_terreno_m por control (Box Plot) | Variable: `delta_terreno_m`. Agrupar por: `control_terreno` |
| h_canopy_m por control (Box Plot) | Variable: `h_canopy_m`. Agrupar por: `control_terreno` |
| delta contra h_canopy (Scatter Plot) | Eje X: `delta_terreno_m`. Eje Y: `h_canopy_m`. Color: `control_terreno` |
| Tabla de segmentos (Data Table) | Sin parámetros |

### `TP2_flujo_CCI_cotejo.ows`

| Widget | Parámetros |
|---|---|
| Bosque (File) | `../05_Resultados/04_Tablas/TP2_cotejo_CCI_L4A_BOSQUE_NW_02.csv` |
| Estepa (File) | `../05_Resultados/04_Tablas/TP2_cotejo_CCI_L4A_ESTEPA_NW_02.csv` |
| Unir recintos (Concatenate) | Agrega la columna de origen con el nombre `recinto` |
| CCI contra L4A (Scatter Plot) | Eje X: `agbd_L4A_Mg_ha`. Eje Y: `agbd_CCI2024_Mg_ha`. Color: `recinto` |
| pendiente contra CCI (Scatter Plot) | Eje X: `pendiente_grados`. Eje Y: `agbd_CCI2024_Mg_ha`. Color: `recinto` |
| Correlaciones | Hay que elegirla a mano: la variable de referencia es `agbd_CCI2024_Mg_ha` |
| Estadísticos por columna (Feature Statistics) | Sin parámetros: muestra todas las columnas |
| Tabla del cotejo (Data Table) | Sin parámetros |

## Lo que hay que elegir a mano

Las variables de los gráficos vienen elegidas y se comprobó que Orange las
reconoce, tanto en la versión 3.39 como en la 3.40. Dos cosas, en cambio, no
están guardadas en el `.ows` y hay que fijarlas en pantalla.

**La variable de referencia del widget Correlaciones**, que en el flujo del
cotejo con el CCI es `agbd_CCI2024_Mg_ha`. Sin esa elección el widget ordena
todos los pares de variables entre sí, en lugar de responder cuál se parece
más a la biomasa del mapa. El título del widget en el lienzo dice cuál elegir.

**Las opciones de dibujo de los gráficos**: la recta de ajuste, el tamaño del
punto, el desplazamiento aleatorio que separa los puntos superpuestos y la
transparencia. Se encienden en el panel de la izquierda de cada gráfico y no
quedan guardadas en el flujo.

En los dos gráficos de dispersión conviene encender la recta de ajuste antes
de discutir la relación, y bajar el tamaño del punto cuando la estepa satura
la pantalla con sus miles de huellas.

## Cómo sacar una figura con calidad

Cada gráfico tiene un botón para guardar la imagen. Conviene guardar en
**SVG** lo que vaya a un informe, porque el texto queda como texto y se puede
corregir después, y en **PNG** lo que vaya a una diapositiva.

Antes de guardar hay que agrandar la ventana del widget. Orange exporta lo
que está viendo, de modo que una ventana chica devuelve una figura apretada,
con los rótulos encimados.
