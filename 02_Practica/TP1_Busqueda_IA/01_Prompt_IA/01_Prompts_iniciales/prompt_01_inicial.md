# Prompt inicial del TP1 — el que se escribió primero

Se conserva **sin corregir**. Sus defectos son la materia del práctico.

---

> Necesito imágenes satelitales de dos zonas de la Patagonia para estudiar un
> incendio forestal, antes y después. Buscame las mejores imágenes disponibles y
> dame un script para descargarlas.

---

## Qué produjo

Un script que consultaba el catálogo, ordenaba por nubosidad y bajaba las escenas
con menos nubes. Corría bien. Descargaba archivos. Los archivos abrían.

## Los cuatro defectos, y lo que cada uno costó

**1. "Las mejores" no significa nada.** ¿Mejores en qué? ¿Menos nubes? ¿Más cerca
de la fecha? ¿Mayor resolución? El script eligió por nubosidad de catálogo, que es
el criterio más fácil de programar y uno de los peores.

**2. Le creyó al catálogo.** La nubosidad que informa el catálogo es de la escena
completa, de 110 × 110 km. Nuestro recinto mide 15 × 15 km. Una escena con 40 % de
nubes puede tener el AOI despejado, y una con 5 % puede tenerlo tapado.

**3. Confundió huella con dato.** El catálogo devuelve todo lo que TOCA el
rectángulo de búsqueda, no lo que lo CUBRE. Una franja de radar es un rectángulo
inclinado dentro de una grilla rectangular: las esquinas están vacías. **Este
defecto costó 12 GB de descarga inútil**: de 9 gránulos NISAR, la huella del
catálogo decía que 6 cubrían la estepa entre el 69 % y el 76 %; al contar los
píxeles con dato dentro del AOI, la cobertura real era del 15 %.

**4. No pidió verificar nada después de descargar.** Ni cobertura real, ni píxeles
válidos, ni coherencia entre sensores.

## La lección

El prompt pedía **archivos**. Debía pedir **archivos verificados**. La diferencia
son dos líneas en el pedido y varias horas de descarga.
