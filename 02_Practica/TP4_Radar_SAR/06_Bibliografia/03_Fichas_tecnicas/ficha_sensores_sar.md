# Ficha técnica — los radares del TP4

| Sensor | Banda | λ | Polarizaciones | Píxel | Época | Corregido de fábrica |
|---|---|---|---|---|---|---|
| **Sentinel-1 GRD** | C | 5,6 cm | VV + VH | 10 m | las cuatro | no (script TP4_01) |
| **SAOCOM-1** | L | 24 cm | HH + HV (quad-pol en 2023-24) | 10 m | base, pre, post | no (script TP4_01) |
| **NISAR GCOV** | L | 24 cm | HH + HV | 10 m | pre-incendio | **sí** |
| **PALSAR-2 mosaico** | L | 24 cm | HH + HV | 25 m | 2023, 2024, 2025 | **sí** |
| **BIOMASS** | P | 70 cm | totalmente polarimétrica | 50–60 m | post-incendio | **sí** (nivel 2A) |

## La física en una línea

Una onda **interactúa con los objetos de su tamaño y atraviesa los más chicos**.

- **Banda C, 5,6 cm**: el tamaño de una hoja. Rebota en el dosel. **Mide follaje.**
- **Banda L, 24 cm**: le pasa de largo a las hojas. Rebota en ramas gruesas y
  troncos. **Mide madera**, que es donde está la biomasa.
- **Banda P, 70 cm**: penetra más todavía y llega al tronco y a la parte baja del
  perfil. Es la banda que la misión BIOMASS lleva por primera vez al espacio.

**Por qué la banda P no aparece en las cifras de más abajo.** El nivel 2A de
BIOMASS se publicó el 30 de junio de 2026 y todas las adquisiciones sobre estos
recintos son posteriores al incendio. Sirve para ver el sensor y su producto de
altura de bosque, no para medir el cambio. Por eso su fila lleva guiones en los
cuadros comparativos.

## La polarización

- **Co-polar (HH, VV)**: emite y recibe igual. Una superficie lisa la devuelve sin
  cambios.
- **Cruzada (HV, VH)**: para volver cambiada, la onda tuvo que rebotar varias veces
  en un volumen desordenado. **Eso es una copa de árbol.**

**Consecuencia contraintuitiva:** HV devuelve MENOS señal (−13,2 dB contra −8,0 de
HH en NISAR) y sin embargo **separa mejor**. No importa cuánta señal vuelve, sino
cuánto distingue una clase de otra.

## γ⁰ y no σ⁰: la decisión que define si el producto sirve

| | Divide por | Sirve en |
|---|---|---|
| σ⁰ | el área proyectada sobre un plano horizontal | terreno llano |
| **γ⁰** | **el área realmente iluminada** (con DEM) | **cualquier relieve** |

En una ladera, σ⁰ hace que la misma vegetación se vea brillante de un lado y oscura
del otro. En un bosque andino esa señal geométrica **domina** y se confunde con
biomasa (Small, 2011).

El `localIncidenceAngle` que trae cada producto es **diagnóstico, no corrección**.

## El speckle

No es ruido del instrumento: es física de la onda coherente. Dentro de un píxel hay
miles de dispersores y sus ondas se suman con fases distintas. **Dos píxeles del
mismo bosque difieren varios dB por azar.** Un satélite diez veces mejor tendría el
mismo speckle.

Se combate promediando. En este proyecto el óptimo está en **150 m**.

## Cifras medidas en este proyecto

| | Contraste bosque − estepa (HV) | Gana de 0–3 m a >21 m |
|---|---|---|
| Sentinel-1 (C) | 4,2 dB | 0,53 dB |
| NISAR (L) | 9,9 dB | 2,59 dB |
| PALSAR-2 (L) | 11,6 dB | 2,16 dB |
| SAOCOM (L) | 11,7 dB | 1,98 dB |
| BIOMASS (P) | — | — |
