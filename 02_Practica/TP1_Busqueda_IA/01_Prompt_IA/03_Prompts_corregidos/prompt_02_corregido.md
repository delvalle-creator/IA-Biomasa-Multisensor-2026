# Prompt corregido del TP1 — el que produjo los scripts del práctico

Éste es el prompt reescrito después de detectar los cuatro defectos del primero.
Es el que generó los diez scripts que usted va a ver ejecutar.

> En esta misma carpeta hay un `PROMPT_IA.pdf`, que es la versión impresa de este
> mismo material. Este `.md` existe para que usted pueda **copiarlo y pegarlo** en
> la IA que prefiera, que es para lo que sirve un prompt. El PDF se conserva por
> si le resulta más cómodo leerlo.

---

> Contexto: dos AOI de 15 × 15 km en el noroeste de Chubut, Argentina. Uno de
> bosque andino de *Nothofagus* (BOSQUE_NW_02) y uno de ecotono de estepa
> (ESTEPA_NW_02), que funciona como control. Grilla común EPSG:32719, píxel 10 m.
> El bosque se incendió entre el 10/01 y el 27/02 de 2026.
>
> Necesito armar el inventario de imágenes disponibles sobre esos dos recintos,
> en cuatro épocas: línea de base 2023-2024, pre-incendio 2025-2026,
> post-incendio 2026, y una época de banda L de otra década (ALOS-1, 2007-2009).
>
> **Requisitos, no negociables:**
>
> 1. **Verificar antes de descargar, no después.** Para cada producto candidato,
>    leer una ventana del AOI sin bajar la escena entera —los productos en la nube
>    son COG y permiten lectura parcial— y contar los píxeles que efectivamente
>    traen dato dentro del recinto. Informar esa cifra **al lado** de la cobertura
>    que declara el catálogo, no en lugar de ella.
> 2. **No confiar en la nubosidad del catálogo.** Es la de la escena completa, de
>    110 × 110 km; el recinto mide 15 × 15. Recalcularla dentro del AOI con la
>    banda de calidad y mostrar las dos cifras.
> 3. **Detectar bruma, que la máscara oficial no marca.** La máscara de escena
>    está entrenada para nubes: objetos brillantes, opacos y con borde. La bruma es
>    semitransparente y la deja pasar. Usar la reflectancia del azul, que es la
>    banda que más se ensucia con aerosoles, y compararla contra las escenas
>    limpias de la misma zona. Informar la razón, no un sí o un no.
> 4. **Distinguir cuadripolar, dual polarización y haces múltiples**, y decirlo en
>    el inventario. No se procesan igual y decide qué análisis es posible.
> 5. **Fechas de los metadatos, nunca del sistema de archivos.** La fecha del
>    archivo suele ser la de descarga.
> 6. **Nunca escribir credenciales en el script.** Leerlas del entorno o de un
>    archivo fuera del árbol de scripts, y fallar con un mensaje claro si no están.
> 7. **No tomar la cantidad de archivos como medida de disponibilidad.** Un
>    producto puede traer muchos archivos y muy poca superficie útil.
> 8. Si un producto no está disponible —por ejemplo un nivel de proceso todavía no
>    publicado—, **dejar constancia escrita de la consulta y de su resultado**. Una
>    ausencia documentada es información; una ausencia silenciosa es un hueco.
>
> Cada script debe imprimir qué buscó, qué encontró, qué descartó y por qué, y
> cuál es el siguiente paso.

---

## Qué cambió respecto del primero

| Prompt inicial | Prompt corregido |
|---|---|
| "las mejores imágenes" | criterios explícitos, y cada uno verificable |
| le creía a la nubosidad del catálogo | la recalcula dentro del AOI |
| confundía huella con dato | cuenta píxeles con dato antes de descargar |
| no mencionaba la bruma | la detecta por el azul y declara la razón |
| no distinguía tipos de producto | los distingue y lo anota en el inventario |
| pedía archivos | pide archivos verificados y un registro de lo descartado |

## Lo que costó el defecto que más caro salió

El tercero. La huella que devuelve un catálogo es todo lo que **toca** el
rectángulo de búsqueda, no lo que lo **cubre**. Seis gránulos que el catálogo daba
como cubriendo entre el 69 % y el 76 % de la estepa tenían, contando píxeles con
dato, una cobertura real del 15 %. Doce gigabytes de descarga inútil, evitables con
dos líneas más en el pedido.

## La diferencia de fondo

El primer prompt pedía **archivos**. El segundo pide **archivos verificados y el
registro de lo que se descartó**. Fíjese que el corregido es largo, específico y
aburrido: así son los prompts que sirven. El conocimiento del dominio no lo pone el
modelo, lo pone usted, y se nota en el pedido.
