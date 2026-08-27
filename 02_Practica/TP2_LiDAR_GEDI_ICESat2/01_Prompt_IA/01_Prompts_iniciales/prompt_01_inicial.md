# Prompt inicial del TP2 — el que se escribió primero

Éste es el prompt tal como se escribió al empezar, **sin corregir**. Se conserva a
propósito: sus defectos son la primera lección del práctico.

---

> Necesito descargar datos GEDI para dos zonas de la Patagonia, una de bosque y
> otra de estepa, y calcular la altura del dosel. Dame un script de Python que
> baje los datos y me saque la altura media de cada zona.

---

## Qué produjo

Un script que descargaba los `.h5`, leía la variable `rh95` y promediaba. Corría
sin errores. Devolvía un número.

## Qué estaba mal, y por qué importa

**1. No pedía filtrar nada.** GEDI trae disparos inservibles: los que pegaron en
una nube, los que no tenían energía para llegar al suelo, los tomados con la
órbita degradada. El script los promediaba todos. El número que devolvía era
falso, y no había forma de saberlo mirando la salida: un promedio siempre
devuelve un promedio.

**2. Pedía "altura media" sin preguntar de qué.** La media de una distribución
con cola larga está tironeada por los extremos. Y `rh95` no es "la altura": es el
percentil 95 de la energía devuelta. Son cosas distintas y el prompt las mezclaba.

**3. No decía nada del terreno.** En un bosque andino la pendiente distorsiona la
medición de GEDI: dentro de una misma huella de 25 m sobre una ladera de 30° hay
14 m de desnivel, y el instrumento no distingue si esos 14 m son montaña o árbol.
El prompt no lo mencionaba, así que el script tampoco.

**4. No pedía verificar nada.** Ni cobertura, ni cantidad de disparos válidos, ni
comparación entre los dos sitios. Pedía un resultado, no una comprobación.

## La lección

El script hizo exactamente lo que se le pidió. El problema no fue el modelo: fue
el prompt. **Un pedido que no menciona la calidad del dato produce un resultado
que no la tiene en cuenta, y encima no falla.** Un script que no falla no es lo
mismo que un script que funciona.
