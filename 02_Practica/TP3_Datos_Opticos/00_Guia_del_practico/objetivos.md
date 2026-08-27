# TP3 — Objetivos

## Objetivo general
Estimar biomasa con datos ópticos y **medir hasta dónde llega** esa estimación.

## Objetivos específicos
1. Enmascarar nubes correctamente con la banda de clasificación de escena (SCL de
   Sentinel-2, QA_PIXEL de Landsat), verificando la nubosidad **dentro del AOI**.
2. Calcular índices espectrales y entender qué mide cada uno.
3. Cartografiar el incendio con dNBR y clasificar su severidad.
4. Ajustar modelos de biomasa contra la referencia GEDI.
5. **Reconocer el límite del óptico:** satura temprano y solo ve el dosel; no
   penetra hasta los troncos, donde está la biomasa. Este límite es lo que
   justifica el radar de TP4.

## Qué debe entregar
- Composiciones e índices.
- Mapa de severidad del incendio y estadísticas por sitio.
- Modelo de biomasa con validación cruzada, residuos e incertidumbre.
- Comparación bosque vs. estepa.

## Advertencia metodológica
Las capas categóricas (SCL, coberturas) se remuestrean **siempre** por vecino más
cercano: interpolar etiquetas crea clases que no existen. Ver el anexo en
`07_Preguntas_y_entrega/04_Anexos/`.
