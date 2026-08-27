# Un área grande para mostrar en clase

**02/08/2026.** Escrito a partir de la pregunta: los productos se ven pixelados
por el tamaño de nuestros recintos, ¿se puede tomar un área mucho más grande?

## La respuesta corta: no hace falta bajar nada más

El producto que ya está descargando **es** el área grande. Un marco de BIOMASS
mide unos **146 × 83 km**. El recinto del curso mide 15 × 15. El marco es
**cincuenta y cuatro veces** el AOI.

Lo que se veía pixelado no era el producto: era el recorte. A 50 m de píxel, un
recuadro de 15 km da 300 × 300 píxeles, y trescientos píxeles en una pantalla se
ven como ladrillos. El mismo dato sin recortar da unos **1.660 × 2.920 píxeles**.

Para eso está `graph_biomass_l2a_region.xml`, que es el mismo grafo de siempre
pero **sin el nodo Subset**: deja el marco entero, enmascarado por su capa de
calidad y reproyectado a la grilla del proyecto.

## Una advertencia para decirla en voz alta frente a los alumnos

**Agrandar el área no mejora la resolución.** El píxel sigue midiendo 50 metros.
Lo único que cambia es cuánto terreno entra en la pantalla. La tentación de
"arreglar" el pixelado remuestreando a 10 m hay que resistirla y explicar por
qué: eso no agrega detalle, lo inventa. Es exactamente el mismo error que el
curso enseña a detectar en otros contextos, y acá aparece de la forma más
tentadora, porque el resultado *se ve* mejor.

## Qué marco elegir

Cobertura de cada marco, calculada de los recuadros que publica el catálogo.

### Pasada del 09/06/2026, traza T036

| Marco | Tamaño | Qué entra |
|---|---|---|
| F275 | 147 × 83 km | Lago Puelo, El Hoyo |
| **F274** | **146 × 83 km** | **Lago Puelo, El Hoyo, Epuyén, Esquel, Trevelin y los dos recintos del curso** |
| F273 | 146 × 83 km | Corcovado, Río Pico |
| F272 | 146 × 84 km | — |
| F271 | 179 × 90 km | — |

**F274 es el mejor de todos, y usted ya lo está bajando.** El alumno ve el bosque
andino entero, de Lago Puelo a Trevelin, y adentro, chiquito, el cuadrado donde
trabajó todo el curso. Esa imagen sola justifica el práctico.

### Pasada del 07/06/2026, traza T014

| Marco | Tamaño | Qué entra |
|---|---|---|
| F191 | 147 × 86 km | — |
| **F192** | 147 × 84 km | Epuyén, Esquel, Trevelin y los dos recintos. **No llega a Lago Puelo** |
| F193 | 147 × 84 km | Corcovado, Río Pico |
| F194 | 147 × 86 km | — |
| F195 | 147 × 87 km | — |

## Si quiere todavía más: la tira completa

Los marcos vecinos **de la misma pasada** se pegan sin costura, porque son la
misma órbita y el mismo día. No hay diferencia de fecha, ni de geometría, ni de
humedad del suelo entre uno y otro.

| Pasada | Tira de los cinco marcos |
|---|---|
| 09/06/2026, T036 | **684 × 192 km**, del paralelo 40,9 al 47,1 |
| 07/06/2026, T014 | 653 × 189 km, del paralelo 41,0 al 46,9 |

Sumando sólo F275 al norte y F273 al sur del 09/06 ya se arma una tira de unos
440 km, que cubre de Lago Puelo a Río Pico. Con tres marcos alcanza; los cinco
son para el mapa mural.

**Cuidado con mezclar pasadas.** Pegar un marco de la traza 014 con uno de la 036
sí tiene costura: son dos geometrías de observación y dos días distintos. Para
una figura de clase se nota, y además invita a una comparación que no
corresponde. Si se mezclan, hay que decirlo en el epígrafe.

## Cómo pedir los marcos vecinos al catálogo

La consulta es abierta, no necesita credenciales. Todo en una sola línea:

```
https://catalog.maap.eo.esa.int/catalogue/search?collections=BiomassLevel2a
   &bbox=-72.6,-46.1,-70.5,-41.5&limit=30&fields=id,bbox,assets.product
```

Devuelve el identificador, el recuadro de cada marco y el enlace de descarga.
Una advertencia comprobada el 02/08: **el filtro `datetime` de esa consulta no
siempre se respeta**; pedimos sólo el 09/06 y devolvió también los del 07/06.
Conviene filtrar por fecha mirando el identificador, que la lleva adentro, en
lugar de confiar en el parámetro.

## Orden sugerido para armar la figura

1. Descomprimir el marco y correr `TP4_11_inspeccionar_biomass_L2A.py` para
   conocer los nombres reales de banda.
2. Ejecutar `graph_biomass_l2a_region.xml` con esos nombres. Sale el marco
   entero, a 50 m, en EPSG:32719.
3. En QGIS, dibujar encima los dos recintos de `00_COMUN\01_AOI`. Ese contraste
   —el marco enorme y los dos cuadraditos— es la figura.
4. Si suma marcos vecinos, mosaicarlos **antes** de estilizar, para que la escala
   de color sea una sola y no una por marco.
