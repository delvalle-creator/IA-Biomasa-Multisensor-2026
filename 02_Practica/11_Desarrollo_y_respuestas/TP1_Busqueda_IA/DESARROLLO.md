# TP1 — Desarrollo completo, con los datos expuestos

**Regla del práctico: verificar antes de descargar.** Todo lo que sigue es
la corrida real de los diez pasos de `03_Scripts\00_ORDEN_DE_EJECUCION.md`,
con las tablas que deja cada uno.

## 1. La ejecución, paso a paso

Los diez scripts se corren en orden, en el entorno conda `aoi`:

    conda activate aoi
    cd C:\Temp\CURSO_BIOMASA_2026\02_Practica

**Pasos 1 y 2 — verificar.** `TP1_01_verificar_cobertura.py` compara la
huella que declara cada catálogo con los píxeles que de verdad contienen
dato, y deja `05_Resultados\04_Tablas\verificacion_cobertura.csv`.
`TP1_02_detectar_bruma.py` revisa la reflectancia del azul de cada escena
óptica y deja `deteccion_bruma.csv`. Nada se descarga todavía.

**Pasos 3 a 8 — descargar.** Seis proveedores con script propio: Copernicus
(Sentinel-1 y 2), Planetary Computer (Landsat 9, recortado en el servidor),
NASA Earthdata (GEDI L2A y L2B), ASF (ALOS-1 y NISAR) y ESA MAAP (BIOMASS,
con token). El séptimo proveedor, la CONAE, **no tiene script y no es un
olvido**: el SAOCOM se obtiene por solicitud y autorización; el trámite real
está documentado en `00_COMUN\08_Originales_crudos\PEDIDO_SAOCOM_28jul2026.md`.

**Pasos 9 y 10 — documentar.** `TP1_09_inventario.py` recorre lo descargado
y deja `02_Subsets_SNAP_QGIS\03_Tablas\inventario.csv`;
`TP1_10_reconstruir_diccionario.py` regenera el diccionario de nombres
cortos.

## 2. Los resultados, con los datos a la vista

### 2.1 El inventario: qué quedó en el disco

`inventario.csv` cierra con **81 filas y 288,8 GB**, que son **68 productos
únicos y 252,4 GB**: las filas del SAOCOM se repiten porque un mismo producto
cubre los dos recintos y el inventario lo anota una vez por recinto. Los
productos únicos son 14 Sentinel-2 L2A, 14 Sentinel-1 GRD, 14 Sentinel-1 SLC,
13 SAOCOM L1A, 10 ALOS-1 quad-pol, 2 gránulos GEDI (L2A y L2B) y 1 NISAR GCOV,
repartidos en las cuatro épocas (línea de base, pre-incendio, post-incendio e
histórica ALOS). El inventario recorre `08_Originales_crudos`, de modo que no
incluye Landsat 9 ni los mosaicos de PALSAR-2: esos llegaron ya recortados y
no pasan por esa carpeta.

### 2.2 La matriz de datos: catorce fuentes, verificadas una por una

`05_Resultados\04_Tablas\matriz_datos.csv` es el producto de síntesis del
práctico. Algunas filas que conviene mirar:

| Fuente | Cobertura verificada | Estado |
|---|---|---|
| Sentinel-2 MSI L2A | 100 % en ambos AOI | 14 escenas descargadas y recortadas |
| Landsat 9 OLI-2 C2 L2 | 100 % ambos AOI — 0 % de nubes en el AOI | 6 escenas |
| Sentinel-1 IW (GRD y SLC) | 100 % ambos AOI, track 164 ascendente | 14 + 14 escenas |
| SAOCOM-1B S4DP (HH+HV) | 100 % ambos AOI, descendente | 3 escenas |
| SAOCOM quad-pol (línea de base) | 100 % del bosque; **no cubre la estepa** | 7 productos |
| NISAR GCOV beta | 100 % ambos AOI (trazas 003 y 169) | 3 fechas útiles **de 9** |
| ALOS-1 PALSAR L1.1 quad | bosque 99–100 %, **estepa 93 %** | 5 fechas (10 frames) |
| GEDI L2A/L2B | 6.288 disparos en el bosque, 11.222 en la estepa | el filtrado es asunto del TP2 |
| CONAE-AQD (área quemada oficial) | Cushamen y Futaleufú | estadísticas por departamento |

### 2.3 El área quemada oficial, como contexto del proyecto

`estadisticas_AQD_CONAE.csv` (CONAE-AQD por departamento) muestra la
magnitud del evento que atraviesa el curso: en enero de 2026 se quemaron
**43.757,5 ha en Cushamen (2,46 % del departamento)** y **26.537,6 ha en
Futaleufú (2,62 %)**, contra cientos o pocos miles de hectáreas en los meses
vecinos. El recinto de bosque del curso cae dentro de esa mancha.

## 3. Las figuras del procesamiento

En `capturas\`:

- `linea_tiempo.png` — la línea de tiempo de las adquisiciones de todos los
  sensores sobre los dos sitios, con las cuatro épocas y la fecha del
  incendio. Es la figura que ordena el práctico: muestra de un vistazo qué
  sensor tiene datos en qué época y dónde están los huecos.

Las **imágenes de todo lo que este práctico descargó** se ven, ya
procesadas y sitio por sitio, en las galerías de esta misma carpeta: las de
Sentinel-2 y Landsat 9 en `TP3_Datos_Opticos\capturas\`, y las de
Sentinel-1, SAOCOM, NISAR y PALSAR-2 en `TP4_Radar_SAR\capturas\`.

## 4. Respuestas modelo a las preguntas del práctico

**P1. ¿Por qué la huella declarada por un catálogo puede no coincidir con la
superficie que efectivamente contiene dato? Cuantifique la diferencia para
uno de los productos verificados e indique el origen del desvío.**

Porque la huella del catálogo describe el rectángulo de la adquisición, no
los píxeles válidos: bordes de escena, sombra del relieve, máscaras de
calidad y recortes de procesamiento comen superficie por dentro de ese
rectángulo. El caso cuantificado del proyecto es **ALOS-1 quad-pol sobre la
estepa: el catálogo la da por cubierta y los píxeles con dato son el 93 %**
(bosque: 99–100 %); el desvío viene del borde del frame, que cruza el recinto.
La cifra está en `matriz_datos.csv`, fila ALOS-1, no en
`verificacion_cobertura.csv`, que sólo guarda la verificación de las escenas
ópticas del 19/1/2026. Otro caso es NISAR: de 9
fechas listadas por el catálogo, solo **3 resultaron útiles** tras verificar
contenido y cobertura.

**P2. ¿Qué distingue que un producto exista de que un producto sea útil para
el objetivo del trabajo? Ejemplifique con un producto que haya descartado.**

Existir es figurar en el catálogo; ser útil es contener el dato que el
objetivo necesita, en la época, la cobertura y la calidad requeridas. El
ejemplo extremo del proyecto es la **colección de biomasa aérea de BIOMASS:
figura en el catálogo de la ESA y todavía no contiene datos** (su
publicación está calendarizada; el producto utilizable hoy es el de altura
L2A). Un ejemplo de descarte por calidad es la escena Sentinel-2 del 9 de
enero de 2026: existe, es la más próxima al incendio, y se descartó por
el humo del incendio (véase la P4 y el TP3).

**P3. ¿En qué circunstancias conviene descargar una escena completa y en
cuáles conviene recortarla en el servidor antes de transferirla?**

Conviene recortar en el servidor cuando el producto es grande respecto del
AOI y el proveedor lo permite: **Landsat 9 se pidió recortado vía Planetary
Computer** y las 6 escenas quedaron en una fracción del volumen original.
Conviene la escena completa cuando el procesamiento posterior necesita el
contexto (la órbita completa para la corrección geométrica del SLC, la fase
para polarimetría) o cuando el proveedor no recorta: los **SLC de Sentinel-1
y del SAOCOM** se bajaron completos, y por eso el inventario pesa 252,4 GB en
productos únicos (288,8 GB si se suman las filas repetidas por recinto).
La regla práctica: el recorte del servidor ahorra transferencia y disco; la
escena completa preserva opciones de procesamiento. Se decide por el uso,
no por comodidad.

**P4. ¿Qué información se pierde al confiar únicamente en la máscara de
nubes que acompaña al producto?**

Se pierde todo lo que la máscara no clasifica como nube: la **bruma y el
humo**, que atenúan la señal sin formar nubes discretas. El paso 2 lo mide
por la reflectancia del azul y detectó afectada la escena del **9 de enero
de 2026** — plena actividad del incendio — que la máscara SCL daba por
utilizable. Esa escena quedó registrada en `deteccion_bruma.csv` y su
descarte se confirma en el TP3 con dos evidencias independientes (la firma
del azul y la comparación de índices contra la escena limpia del 25 de
noviembre de 2025).

**P5. ¿Cómo debe documentarse una descarga para que un tercero pueda
repetirla dentro de dos años, cuando el catálogo haya cambiado de dirección
o de estructura?**

Registrando lo que identifica al dato y no a la interfaz: el
**identificador del producto** (no la URL), el proveedor y la colección con
su versión, la fecha de adquisición y la de descarga, el área pedida, los
filtros aplicados y las credenciales necesarias (sin incluirlas). Así están
construidos `inventario.csv` (un producto por fila, con época, sitio,
sensor, fecha, archivo y tamaño) y `matriz_datos.csv` (acceso, credenciales
y estado por fuente); el caso CONAE muestra el límite: cuando el acceso es
un trámite, lo que se documenta es el trámite
(`PEDIDO_SAOCOM_28jul2026.md`), y el propio pedido registra que los
identificadores entregados difieren de los solicitados.

## 5. De dónde sale cada cifra

`02_Subsets_SNAP_QGIS\03_Tablas\inventario.csv` (81 filas, 68 productos
únicos), `05_Resultados\04_Tablas\matriz_datos.csv` (las catorce fuentes),
`02_Subsets_SNAP_QGIS\03_Tablas\estadisticas_AQD_CONAE.csv` (área quemada
oficial), `05_Resultados\04_Tablas\verificacion_cobertura.csv` y
`deteccion_bruma.csv` (los dos controles previos a toda descarga).
