# TP1 — Objetivos

## Objetivo general
Diseñar, con asistencia de IA, una estrategia de búsqueda y selección de datos
satelitales para estimar biomasa forestal, y **auditarla críticamente**.

## Objetivos específicos
1. Formular prompts eficaces para descubrir qué sensores y productos existen
   para un problema y un área dados.
2. Consultar catálogos por API (Copernicus CDSE, NASA CMR/Earthdata, Planetary
   Computer STAC, JAXA, CONAE) y entender qué devuelve cada uno.
3. **Verificar la cobertura real** de cada producto contando píxeles válidos
   dentro del AOI, en lugar de confiar en la huella del catálogo.
4. Construir una matriz comparativa de datos y justificar la selección final.
5. Declarar las limitaciones **antes** de procesar, no después.

## Qué debe entregar
- La matriz de datos completa.
- El calendario de adquisiciones por sensor y época.
- Un informe que justifique cada elección y declare cada limitación.
- La bitácora de IA: prompt, respuesta, corrección humana y verificación.

## Criterio de evaluación
No se evalúa la cantidad de datos encontrados, sino **la calidad de la auditoría**:
detectar qué NO sirve y explicar por qué vale tanto como encontrar lo que sirve.
