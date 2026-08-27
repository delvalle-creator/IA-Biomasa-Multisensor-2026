# Prompt inicial del TP4 — el que se escribió primero

---

> Tengo imágenes Sentinel-1 y SAOCOM de un bosque. Procesalas y estimá la biomasa
> con el backscatter.

---

## Qué produjo

Un script de SNAP que calibraba a sigma0, geocodificaba y ajustaba una regresión
contra las huellas GEDI. Corría. Daba un modelo.

## Los cuatro defectos

**1. Calibró a σ⁰ en un bosque andino.** σ⁰ divide por el área proyectada sobre un
plano horizontal. En una ladera, la superficie realmente iluminada no es su
proyección: el resultado es que la misma vegetación se ve brillante en la ladera
que enfrenta al satélite y oscura en la de atrás. En terreno con relieve, esa
señal geométrica DOMINA sobre la de la vegetación, y se confunde con biomasa. Hay
que usar γ⁰ con terrain flattening (Small, 2011).

**2. Ajustó el modelo píxel a píxel.** El radar tiene speckle, que no es ruido del
instrumento sino física de la onda coherente: dos píxeles del mismo bosque difieren
varios dB sólo por cómo cayeron las fases. Un píxel suelto no es una medida.

**3. Mezcló Sentinel-1 con SAOCOM sin decir nada.** Banda C y banda L, distinto
ángulo de incidencia, distinta calibración. Los valores absolutos no son
comparables.

**4. No preguntó si la banda C sirve para esto.** Ésa era la pregunta, y el script
la dio por respondida.

## La lección

El prompt pedía «estimá la biomasa». El script obedeció y produjo un modelo. Un
modelo siempre sale. Lo que faltaba era preguntar **si el sensor puede ver lo que
se le pide ver**.
