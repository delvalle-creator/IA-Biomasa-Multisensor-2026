# TP5 — Sinergia óptico–radar–LiDAR

> **Qué es este archivo.** Notas técnicas del práctico: advertencias, decisiones
> y errores que ya costaron tiempo. No es el punto de entrada. Para saber qué hay
> en cada carpeta, abra `00_LEEME.md`, que encabeza la lista de este práctico.

**Pregunta del práctico:** ¿cuánto gana la estimación al fusionar? Es el cierre:
compara **óptico solo**, **radar solo**, **óptico+radar** y **óptico+radar+LiDAR**
contra el control de **sólo LiDAR**, y estima la **biomasa quemada**.

## Estado: completo. Los cinco modelos, el ensayo nulo, el mapa final y el informe

## De dónde vienen sus insumos

Este práctico **no descarga nada**. Sus insumos son los productos ya procesados:

El `02_Subsets_SNAP_QGIS` de este práctico está **vacío a propósito**: el
TP5_01 lee directamente lo que dejaron los otros prácticos, sin copiarlo:

| Insumo | Lo lee de |
|---|---|
| Huellas válidas, partición y biomasa | `TP2\04_Tablas_de_trabajo\` y `TP2\05_Resultados\04_Tablas\biomasa_<AOI>.csv` |
| Índices ópticos (escena pre del 25/11/2025) | `TP3\02_Subsets_SNAP_QGIS\Sentinel_2\02_pre*` |
| γ⁰ de banda C y L (S1, SAOCOM, NISAR, PALSAR-2) | `TP4\02_Subsets_SNAP_QGIS\` |
| dNBR y severidad (para la biomasa quemada) | `TP3\05_Resultados\02_Rasters\incendio\` |
| Pendiente | `00_COMUN\03_Topografia\` |

## Lo que el práctico hace

1. Apila cada huella válida del TP2 con sus predictores (paso 1), heredando la
   partición por bloques del TP2 sin rehacerla.
2. Ajusta los **cinco modelos** de la comparación explícita del curso: óptico;
   SAR; óptico+SAR; óptico+SAR+LiDAR; y **sólo LiDAR, que es el control** (paso 2).
3. Valida por sitio y **por franja de altura** (paso 3).
4. **Biomasa quemada** = biomasa pre-incendio × severidad, con su incertidumbre
   y su ensayo nulo (paso 4).
5. Mapas de biomasa, cambio e incertidumbre, con la máscara de validez del TP4
   (paso 5), y la **validación estricta** que acota lo que puede afirmarse (paso 6).

## La comparación que el curso quiere demostrar

| Subconjunto | Práctico | Hipótesis a contrastar |
|---|---|---|
| LiDAR solo | TP2 | Muy preciso pero disperso: no es un mapa continuo |
| Óptico solo | TP3 | Satura temprano, solo ve el dosel |
| Radar solo | TP4 | Banda L penetra hasta los troncos; banda C no |
| Óptico + radar | TP5 | Se complementan |
| Óptico + radar + LiDAR | TP5 | El LiDAR calibra y ancla la escala |

## Nota sobre la biomasa quemada

El bosque perdió **18.009 ha (80,2 %)**, casi la mitad con severidad alta. La
biomasa quemada se estima aplicando el modelo pre-incendio sobre esa superficie.
La referencia de banda L pre-incendio (NISAR 08/01/2026 y PALSAR-2 2025) es clave:
es el último registro del bosque en pie.
