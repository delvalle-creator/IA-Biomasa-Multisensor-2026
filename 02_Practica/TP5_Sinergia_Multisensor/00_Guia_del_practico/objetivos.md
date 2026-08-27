# TP5 — Objetivos

## Objetivo general
Integrar óptico, radar y LiDAR para estimar biomasa, **cuantificar cuánto aporta
cada fuente** y evaluar el efecto del incendio.

## Objetivos específicos
1. Construir un dataset multisensor apilado sobre la grilla común.
2. Ajustar cinco modelos (óptico; SAR; óptico+SAR; óptico+SAR+LiDAR; y sólo
   LiDAR, que es el control) y
   compararlos con las mismas muestras y la misma validación.
3. Evaluar la **transferibilidad espacial**: entrenar en un sitio y probar en otro.
4. Comparar biomasa pre y post incendio y estimar la biomasa quemada.
5. Cuantificar y mapear la **incertidumbre**, no solo el valor predicho.

## Qué debe entregar
- Los cinco modelos, con métricas comparables entre sí.
- Mapas de biomasa pre y post incendio, y de cambio — el equivalente local,
  calibrado sobre GEDI, del mapa global **CCI Biomass** que el TP2 puso como
  contraste: donde el CCI rellena con un modelo global, aquí se rellena con
  los sensores propios del proyecto.
- Mapa de incertidumbre.
- Estimación de biomasa quemada con su intervalo.
- Una conclusión honesta sobre qué aportó realmente la fusión.

## Criterio de evaluación
Que la comparación entre modelos sea **justa**: mismas muestras, misma partición,
misma validación. Y que la conclusión distinga entre mejora real y sobreajuste.
