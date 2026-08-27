# Prompt inicial del TP3 — el que se escribió primero

Se conserva sin corregir.

---

> Con las imágenes Sentinel-2 que ya tengo, calculame el NDVI antes y después del
> incendio y decime cuántas hectáreas se quemaron.

---

## Qué produjo

Un script que tomaba la escena más cercana a cada fecha, calculaba NDVI, restaba y
contaba píxeles. Devolvía un número de hectáreas.

## Los tres defectos

**1. Eligió la escena por cercanía a la fecha, no por calidad.** Tomó la del
09/01/2026, que era la más cercana al fuego. Esa escena tiene bruma: la banda azul
vale 0,158 contra los 0,024 normales del sitio. La máscara del producto sólo marcó
7,4 % de cirros y el script la dio por buena.

**2. Usó NDVI para medir área quemada.** El NDVI usa el rojo, que es de las bandas
más afectadas por los aerosoles. Con esa escena, el NDVI del bosque daba 0,34 en
vez de 0,80: inservible. El índice correcto para fuego es el NBR, que usa el
infrarrojo cercano y el de onda corta, casi inmunes a la bruma.

**3. No pidió el umbral ni su origen.** ¿A partir de qué diferencia un píxel está
quemado? El script inventó un corte. Los umbrales de severidad son los de Key y
Benson (2006), y hay que citarlos y discutirlos, no improvisarlos.

## La lección

El prompt pedía un número de hectáreas. Un número siempre sale. La pregunta que
faltaba era **con qué dato y con qué umbral**, y ésa es toda la diferencia entre un
resultado y una cifra inventada con buena letra.
