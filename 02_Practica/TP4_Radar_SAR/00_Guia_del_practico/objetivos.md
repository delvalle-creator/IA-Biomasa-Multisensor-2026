# TP4 — Objetivos

## Objetivo general
Entender la sensibilidad del radar a la biomasa y **por qué la longitud de onda
decide** qué se puede medir.

## Objetivos específicos
1. Distinguir σ⁰, β⁰ y γ⁰, y comprender por qué en relieve complejo solo γ⁰ con
   Terrain Flattening es defendible.
2. Comparar banda C (Sentinel-1) y banda L (SAOCOM, NISAR, PALSAR-2) sobre el
   mismo bosque y con fechas casi simultáneas.
3. Analizar polarizaciones: por qué HV/VH responde a la biomasa leñosa.
4. Evaluar la **saturación**: a partir de qué biomasa cada banda deja de responder.
5. Separar el efecto del fuego del efecto de la humedad y de la pendiente.
6. Ejercitar polarimetría completa con ALOS-1 quad-pol.
7. Reconocer qué aporta la **banda P** de la misión BIOMASS (70 cm, totalmente
   polarimétrica, 50 a 60 m de resolución) y por qué en este proyecto entra como
   demostración del sensor y no como dato del análisis.

## Qué debe entregar
- Backscatter corregido y métricas SAR.
- Modelos de biomasa **separados** para banda C y banda L.
- Análisis de saturación y de los efectos de pendiente y humedad.
- Mapa de biomasa predicha con incertidumbre.

## Advertencias
- **No mezclar GRD y SLC en una misma serie temporal:** el γ⁰ derivado del SLC
  sale ~0,5 dB por encima del derivado del GRD (cambian el multilooking y la
  remoción de ruido térmico). Comparar GRD con GRD y SLC con SLC.
- Comparar sensores de radar exige fechas **y horas** semejantes: la humedad tiene
  ciclo diario y altera la constante dieléctrica.
- SAOCOM 2025-26 es dual-pol descendente; los quad-pol de línea de base son
  descendentes y los dual de esa época, ascendentes. Declarar la limitación.
- **La banda P no mide el cambio.** El nivel 2A de BIOMASS se publicó el 30 de
  junio de 2026 y todas sus adquisiciones son posteriores al incendio, de modo
  que no permiten calcular una diferencia. En los cuadros comparativos su fila
  va con guiones, y el guion significa que la magnitud no pudo calcularse, no
  que valga cero.
