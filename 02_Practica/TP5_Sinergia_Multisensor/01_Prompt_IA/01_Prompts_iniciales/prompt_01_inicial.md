# Prompt inicial del TP5 — el que se escribió primero

Se conserva **sin corregir**. Es el más instructivo de los cinco, porque no falló:
funcionó, entregó números razonables, y estaban mal.

---

> Tengo datos de GEDI con altura y biomasa, índices de Sentinel-2 e imágenes de
> radar de Sentinel-1 y SAOCOM sobre las mismas zonas. Combiná todo en un modelo
> de aprendizaje automático para estimar biomasa y hacé el mapa. Después calculá
> cuánta biomasa se perdió en el incendio.

---

## Qué produjo

Exactamente lo pedido, y sin un solo error. Un conjunto de datos que unía todas las
variables sobre las huellas de GEDI, un modelo de bosque aleatorio, un coeficiente
de determinación de **0,96** sobre validación, un mapa continuo de biomasa y una
cifra de pérdida por el incendio.

Un resultado excelente. Presentable. Publicable, incluso.

## Los cuatro defectos, y por qué ninguno hizo fallar al script

**1. No pidió un modelo de control.** El conjunto de predictores incluía variables
derivadas del propio GEDI, que es la fuente de la variable que se quería estimar.
Con eso adentro, el 0,96 no mide sinergia entre sensores: mide, en buena medida,
que el LiDAR predice al LiDAR. Basta entrenar un modelo **sólo con LiDAR** para
verlo: da 0,956. La distancia entre 0,964 y 0,956 es todo lo que aportaron el
óptico y el radar juntos. Sin esa fila de control, el mismo resultado se presenta
como un éxito de la combinación multisensor.

**2. No pidió validar por franjas.** El coeficiente global es un promedio, y un
promedio esconde el patrón. Validando por franja de altura, en el bosque el sesgo
va de **+3,9 m** de sobreestimación en la franja de 0 a 3 m a **−9,3 m** de
subestimación en la de 18 a 21 m. Es compresión hacia la media, le pasa a toda
regresión, y arruina justamente los extremos, que son los que interesan.

**3. No pidió un ensayo nulo.** Para saber cuánta biomasa se perdió hay que medir
antes cuánto "pierde" el método donde no pasó nada. Sobre el terreno **no quemado**
el procedimiento midió un cambio aparente de **−10,25 Mg/ha**, o sea una ganancia,
donde debía dar cero. Las clases quemadas pierden entre 11,5 y 15,5. La señal
apenas supera al ruido en un factor de entre 1,1 y 1,5, y el prompt no pedía
comprobarlo.

**4. Habló de "biomasa perdida" sin poder demostrarlo.** Lo que el procedimiento
mide es un cambio aparente de biomasa estimada entre dos fechas. Llamarlo pérdida
supone que todo el cambio se debe al fuego, que la estimación no tiene sesgo y que
las dos fechas son comparables. Ninguna de las tres cosas estaba comprobada.

## La lección

Los otros cuatro prácticos enseñan a detectar prompts que producen resultados
malos. **Éste enseña a detectar prompts que producen resultados buenos y falsos**,
que es mucho más difícil, porque nada avisa.

Un script que no falla no es un script que funciona. Y un coeficiente de 0,96 no es
una prueba: es una afirmación que todavía hay que verificar.
