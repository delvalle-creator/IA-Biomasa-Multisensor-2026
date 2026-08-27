# TP2 — Objetivos

## Objetivo general
Usar GEDI como **referencia estructural independiente** del bosque, aprender a
controlar su calidad antes de usarlo para calibrar nada — auditándolo con un
segundo LiDAR (ICESat-2/ATL08) y con el terreno desnudo FABDEM — y situar esa
referencia frente al producto global **CCI Biomass**, que es el mapa contra el
que el curso discute qué significa «medir» biomasa desde el espacio.

## Objetivos específicos
1. Entender qué mide GEDI: no es una imagen, son **huellas de 25 m** distribuidas
   irregularmente a lo largo de las órbitas.
2. Filtrar por calidad (`quality_flag`, `sensitivity`) y por pendiente, y
   **documentar cada descarte**.
3. Extraer métricas de altura (rh) y de estructura (pai, cover, fhd).
4. Comparar la estructura del bosque andino con la del ecotono de estepa.
5. Evaluar la limitación temporal: GEDI no es contemporáneo de la línea de base.
6. Cotejar la altura de GEDI contra ICESat-2/ATL08 y someter el terreno de
   ambos al control FABDEM (± 5 m sobre el geoide), separando el error de
   terreno del límite metodológico de cada misión.
7. Poner la biomasa de GEDI en el mapa, a la misma escala que el **CCI
   Biomass**, y explicar la discrepancia: GEDI muestrea puntos, el CCI
   integra el paisaje — **GEDI mide, el CCI rellena**.

## Qué debe entregar
- Footprints aceptados y rechazados, con el motivo de cada rechazo.
- Altura de dosel y biomasa de referencia.
- Estadísticas de calidad y distribuciones por sitio.
- Partición entrenamiento/validación reutilizable en TP3, TP4 y TP5.
- El cotejo GEDI–ICESat-2 con y sin control de terreno, y los mapas
  GEDI/CCI/diferencia del paso 17.

## Criterio de evaluación
La honestidad del filtrado. Un GEDI mal filtrado contamina los cuatro prácticos
siguientes, porque es la referencia contra la que se calibra todo.
