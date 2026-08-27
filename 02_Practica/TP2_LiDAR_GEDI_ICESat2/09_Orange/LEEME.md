# 09_Orange — flujos de Orange Data Mining del TP2

Tres flujos listos para abrir con **Orange Data Mining** (versión 3.36 o
posterior; probados con 3.40). Instalación sugerida: el instalador de
https://orangedatamining.com, o `pip install orange3` en un entorno de
Miniforge propio (NO en el entorno `aoi`, para no mezclar dependencias).

**No mover los .ows de esta carpeta**: las rutas a las tablas son relativas
(`../05_Resultados/04_Tablas/...`). Si se copia un flujo a otro lado, Orange
va a pedir el archivo a mano.

| Flujo | Qué muestra |
|---|---|
| `TP2_flujo_GEDI_biomasa.ows` | Las huellas L4A con su biomasa: distribución de `agbd_Mg_ha`, caja por recinto, `rh98` contra biomasa. La referencia del curso, mirada de frente. |
| `TP2_flujo_ATLAS_control_terreno.ows` | El control de terreno del paso 15: distribución del `delta_terreno_m`, cajas por veredicto (`PASA`/`DESCARTADO`) y el gráfico clave — delta contra `h_canopy_m`: los segmentos con suelo malo son los del dosel inflado. Requiere haber corrido `TP2_15`. |
| `TP2_flujo_CCI_cotejo.ows` | La dicotomía del anexo, huella por huella: CCI 2024 contra L4A (comparar contra la diagonal 1:1 a ojo: ejes iguales), y CCI contra la pendiente del terreno. |

En cada flujo, los dos widgets **File** cargan bosque y estepa y
**Concatenate** los une agregando la clase `recinto`: por eso los gráficos
pueden colorear y agrupar por recinto. Las variables ya vienen
preseleccionadas; si algún gráfico se abriera vacío (versión de Orange muy
distinta), el título de cada widget dice qué elegir.

Estos flujos VEN los resultados: no los producen ni los modifican. La
autoridad de cada cifra sigue siendo el script numerado que la generó.
