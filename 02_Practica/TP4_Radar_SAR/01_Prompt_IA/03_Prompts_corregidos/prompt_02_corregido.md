# Prompt corregido — el que produjo los scripts del TP4

---

> Contexto: Sentinel-1 GRD (banda C), SAOCOM-1 L1A, NISAR GCOV y mosaico PALSAR-2
> (banda L), sobre dos AOI de 15 × 15 km en el noroeste de Chubut. Bosque andino de
> Nothofagus con relieve fuerte, y estepa como control. Grilla común EPSG:32719 a
> 10 m. Las huellas GEDI filtradas del TP2 son la referencia de altura.
>
> La pregunta del práctico es: **¿por qué la banda L y no la C?** No la dé por
> respondida: mídala.
>
> **Requisitos, no negociables:**
>
> 1. **γ⁰ con terrain flattening, NUNCA σ⁰.** En este relieve σ⁰ mide topografía
>    disfrazada de vegetación (Small, 2011). En SNAP: `outputBetaBand=true` y
>    después `Terrain-Flattening` con el DEM Copernicus GLO-30.
> 2. El `localIncidenceAngle` es **diagnóstico, no corrección**. No lo use para
>    dividir de nuevo.
> 3. **Trabaje en γ⁰ lineal y pase a dB al final.** El promedio de los logaritmos
>    no es el logaritmo del promedio: filtrar en dB sesga hacia abajo.
> 4. **Mida el speckle antes de modelar.** Calcule el ENL de cada producto y
>    demuestre con los datos cuánto R² recupera el promediado según el tamaño de
>    ventana. No asuma un tamaño: encuentre el óptimo.
> 5. **Compare los dos sitios**: el contraste bosque − estepa en dB es la medida
>    directa de la utilidad del sensor. Hágalo por banda y por polarización.
> 6. **Repita el experimento del TP3_05 con radar**: mismas huellas, mismo bosque,
>    misma métrica. Sólo cambia el sensor. Si cambia algo más, no es comparable.
> 7. **Compare formas y contrastes entre sensores, no valores absolutos.** Distinto
>    ángulo de incidencia y distinta calibración: SAOCOM y NISAR no tienen por qué
>    coincidir en valor, pero sí en forma.
> 8. **Declare las tres limitaciones**: el tamaño de ventana es una decisión suya;
>    la geometría invalida píxeles (sombra, acortamiento de pendiente, inversión); y γ⁰ responde a la
>    humedad, así que compare fechas cercanas.
> 9. **Exporte a QGIS**: los productos están en γ⁰ lineal con cola larga (NISAR
>    llega a 202). Sin pasar a dB y sin declarar nodata, QGIS los muestra negros.
>
> Cada script debe imprimir qué hizo, cuántos datos entraron y salieron, y cuál es
> el siguiente paso.

---

## La diferencia

El primero pedía **un modelo de biomasa**. Éste pide **medir si el sensor puede
verla**, y deja explícito que la respuesta puede ser que no.
