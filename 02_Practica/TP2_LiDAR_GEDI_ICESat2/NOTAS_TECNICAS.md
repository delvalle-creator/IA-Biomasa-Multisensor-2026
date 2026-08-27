# TP2 — GEDI como referencia LiDAR

> **Qué es este archivo.** Notas técnicas del práctico: advertencias, decisiones
> y errores que ya costaron tiempo. No es el punto de entrada. Para saber qué hay
> en cada carpeta, abra `00_LEEME.md`, que encabeza la lista de este práctico.

**Pregunta del práctico:** ¿qué nos dice el LiDAR espacial, por sí solo, sobre la
estructura del bosque? Es el primer eslabón de la comparación: **LiDAR solo**.

## Estado: completo. Insumos, cadena GEDI de once pasos numerados más el 1b, la rama ICESat-2 con su control de terreno FABDEM (pasos 12 a 16), el mapa contra el CCI (paso 17) y resultados; la rama tiene sus notas en `NOTAS_TECNICAS_ICESat2.md`

## Qué hay

- `02_Subsets_SNAP_QGIS/GEDI_L2A/` y `GEDI_L2B/` — los disparos GEDI ya recortados a los dos
  AOI, en CSV (coordenadas WGS84 y UTM 19S).
- L2A: `rh25`, `rh50`, `rh75`, `rh95`, `rh98`, `elev_lowestmode`, `quality_flag`, `sensitivity`
- L2B: `pai`, `fhd_normal`, `cover`, `l2b_quality_flag`
- **6288 disparos válidos de 11222** en total.

## Dos advertencias que ya costaron caro

1. **GEDI estuvo hibernado entre marzo de 2023 y abril de 2024.** No hay datos en
   ese período: por eso la referencia LiDAR es de sep. 2024 a mar. 2025 y **no es
   contemporánea** de la línea de base 2023-24. Hay que declararlo.
2. **La versión V003 renombró las variables.** Los flags de calidad pasaron a
   llamarse `l2a_quality_flag_rel3` y `l2b_quality_flag_rel3`, y las coordenadas
   se mudaron a la raíz del beam. Un script escrito para V002 devuelve columnas
   vacías **sin dar ningún error**.

## Lo que falta hacer

1. Filtrado de calidad: `quality_flag == 1`, `sensitivity > 0.95`, y descartar
   footprints en pendiente fuerte (usar el DEM de `00_COMUN/03_Topografia/`).
2. **Conservar los footprints descartados y el motivo del descarte** (lo pide la
   consigna): van a `05_Resultados/06_Control_calidad/`.
3. Métricas de altura de dosel (rh95/rh98) y comparación bosque vs. ecotono.
4. Biomasa GEDI de referencia (L4A si se incorpora, o modelo alométrico local).
5. Partición entrenamiento / validación para los prácticos siguientes.

## Scripts

    03_Scripts/01_Pre_procesamiento/recortar_AOI/       TP2_01_descargar_gedi.py, TP2_01b_descargar_gedi_l4a.py,
                                                       TP2_01c_reextraer_l4a.py, TP2_02_recortar_AOI.py
    03_Scripts/01_Pre_procesamiento/filtrar_calidad/    TP2_03_filtrar_calidad.py
    03_Scripts/01_Pre_procesamiento/filtrar_pendiente/  TP2_04_dem_y_pendiente.py, TP2_05_filtrar_pendiente.py
    03_Scripts/02_Procesamiento/altura_dosel/           TP2_06_metricas_estructura.py
    03_Scripts/02_Procesamiento/biomasa_GEDI/           TP2_07_biomasa_referencia.py
    03_Scripts/02_Procesamiento/cobertura_BAP/          TP2_09_cobertura_BAP.py
    03_Scripts/02_Procesamiento/auditoria_L4A/          TP2_10_auditoria_L4A.py, TP2_11_escenarios_hoja_caida.py
    03_Scripts/05_Exportacion/                          TP2_08_exportar_para_gis.py

## Verificar en QGIS (TP2_08)

El práctico produce un GeoPackage con estilos, para que los resultados NO haya que
creerlos: se miran.

    05_Resultados/03_Vectores/TP2_GEDI.gpkg
    05_Resultados/03_Vectores/*.qml          (estilos: Simbología -> Estilo -> Cargar estilo)

| capa | entidades | qué es |
|---|---|---|
| `gedi_aceptados_bosque` | 1.025 | las huellas que sobrevivieron los filtros |
| `gedi_descartados_bosque` | 5.263 | con el campo `motivo`: por qué se rechazó cada una |
| `gedi_aceptados_estepa` | 4.041 | |
| `gedi_descartados_estepa` | 7.181 | |
| `aoi_recintos` | 2 | los recuadros de 15 × 15 km |

Tres pasos: arrastrar el .gpkg a QGIS, cargar el .qml en cada capa, mirar.

Qué verificar: que el bosque tenga huellas altas y la estepa no (es el control del
proyecto, hecho mapa); que los descartados por pendiente caigan sobre las laderas
del DEM (si no, el filtro está mal); y que se vea la dispersión real de GEDI, que
son líneas de disparos con huecos enormes, no un mapa continuo.
