# Qué contestó la IA, y qué había que mirarle

## La respuesta

Un script prolijo: leía las dos escenas, calculaba NDVI con las bandas 4 y 8,
restaba, aplicaba un umbral de 0,3 y multiplicaba píxeles por 0,01 ha. Correcto
en todo, excepto en lo que importaba.

## Lo que había que detectar

**El umbral de 0,3 no salía de ningún lado.** Ni cita, ni justificación. Un número
plausible inventado con confianza.

**No enmascaraba nubes.** Los píxeles con nube entraban al cálculo. En una escena
declarada «limpia» eso parece inofensivo, hasta que la escena no está limpia.

**No comparaba contra nada.** Un solo índice, un solo par de fechas, ningún control.

## Cómo se detectó el problema real

No leyendo el script: **mirando la serie completa**. El NDVI del bosque daba 0,80
en octubre de 2023, 0,81 en enero de 2024, 0,81 en febrero de 2024, 0,80 en
noviembre de 2025... y 0,34 el 09/01/2026, dos meses antes del incendio. Un bosque
no pierde el 60 % de su verdor y lo recupera solo.

**El azul lo confirmó**: 0,158 contra 0,024 de mediana del sitio, casi siete veces.
Y **Landsat 9**, cinco días antes, daba NDVI 0,78 en ese mismo bosque.

## La regla

Una anomalía se detecta **contra la serie**, no contra la intuición. Si un valor
rompe el patrón de todas las demás fechas, la carga de la prueba la tiene el valor,
no el patrón.
