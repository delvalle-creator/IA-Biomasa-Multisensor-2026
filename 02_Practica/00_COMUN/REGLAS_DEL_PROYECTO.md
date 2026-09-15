# CURSO_BIOMASA_2026

> ## Nombres de las carpetas de descargas
>
> Son cortos a propósito, para que ninguna ruta del proyecto pase de los 260
> caracteres que admite Windows:
>
> | Carpeta | Qué guarda |
> |---|---|
> | `00_COMUN\08_Originales_crudos` | los 253 GB de productos originales, sin modificar |
> | `00_alos` | la serie histórica de ALOS-1 |
> | `01_base` | la línea de base, 2023 y 2024 |
> | `02_pre` | la época previa al incendio, 2025 y 2026 |
> | `03_post` | la época posterior, 2026 |
>
> Dentro de los originales van los `.zip` tal como llegan del proveedor, sin las
> carpetas `.SAFE` descomprimidas al lado: duplicarlas cuesta 150 GB y no aporta
> nada, porque los programas leen el `.zip`.


Proyecto único del curso de posgrado: estimación de biomasa en el bosque
andino-patagónico y su ecotono con la estepa, y evaluación del efecto de un
incendio, mediante integración multisensor asistida por IA.

**Sitios de estudio:** dos AOI de 15 × 15 km en el noroeste de Chubut.

- `BOSQUE_NW_02` — bosque andino. **Se incendió entre el 10/01 y el 27/02 de 2026.**
- `ESTEPA_NW_02` — ecotono de estepa. Sirve de control: no se quemó.

**Grilla común de todo el proyecto:** EPSG:32719 (UTM 19S), píxel de 10 m,
1500 × 1500 píxeles. Todos los sensores están alineados al píxel, de modo que
se pueden apilar y comparar directamente. Está definida en un único lugar:
`00_COMUN/configuracion_comun.py`.

---

## Los cinco prácticos

La secuencia es progresiva: primero se aprende a buscar y auditar los datos,
después se modela con cada sensor por separado, y al final se integran. Esto
permite comparar explícitamente qué aporta cada fuente y qué aporta la fusión.

| Práctico | Tema | Qué se compara |
|---|---|---|
| **TP1** | Búsqueda inteligente y evaluación crítica de datos | — (fundamento) |
| **TP2** | GEDI como referencia LiDAR | LiDAR solo |
| **TP3** | Biomasa con datos ópticos | Óptico solo |
| **TP4** | Sensibilidad de los radares SAR (bandas C y L) | Radar solo |
| **TP5** | Sinergia óptico–radar–LiDAR | Fusión óptico–radar y óptico–radar–LiDAR |

---

## Organización

    CURSO_BIOMASA_2026/
    ├── 01_Teoria/                 las clases teóricas y sus PDF
    ├── 02_Practica/               todo lo que se ejecuta
    │   ├── 00_Guia_teorica_practica/  la guía completa
    │   ├── 00_COMUN/              datos compartidos por los cinco prácticos
    │   │   ├── 01_AOI/            los dos sitios (KML y geojson)
    │   │   ├── 02_Coberturas/     áreas quemadas (estadísticas CONAE-AQD)
    │   │   ├── 03_Topografia/     DEM, pendiente, orientación, sombreado
    │   │   │                      ← la LLENA el script TP2_04, no viene con el proyecto
    │   │   ├── 07_Diccionario_datos/  qué significa cada archivo y cada banda
    │   │   ├── 08_Originales_crudos/  ← LOS DATOS CRUDOS, SIN MODIFICAR (253 GB)
    │   │   ├── GLOSARIO.md        ← el vocabulario del curso, en un solo lugar
    │   │   └── configuracion_comun.py  ← proyección, píxel, AOI y épocas: FUENTE ÚNICA

    No hay carpetas `04_Muestreo`, `05_Metadatos` ni `06_Simbologia`: ningún
    práctico las usa. Si alguno llegara a necesitarlas, se crean entonces y se
    anuncian acá.
    │   │
    │   ├── TP1_Busqueda_IA/
    │   ├── TP2_LiDAR_GEDI_ICESat2/
    │   ├── TP3_Datos_Opticos/
    │   ├── TP4_Radar_SAR/
    │   ├── TP5_Sinergia_Multisensor/
    │   └── 09_ATAJOS/             los nueve .bat
    └── 99_PRIVADO_NO_DISTRIBUIR/  material del docente, no se distribuye

Cada práctico repite la misma estructura: `00_Guia_del_practico`, `01_Prompt_IA`,
`02_Subsets_SNAP_QGIS`, `03_Scripts`, `04_Tablas_de_trabajo`, `05_Resultados`,
`06_Bibliografia`, `07_Preguntas_y_entrega` y `08_Grafos_SNAP`, más tres archivos
en su raíz: `00_LEEME.md`, `NOTAS_TECNICAS.md` y `00_DE_DONDE_SALEN_LOS_INSUMOS.md`.

`04_Tablas_de_trabajo` existe en los cinco, aunque en varios esté vacía a la espera de que
se corran los scripts que la llenan: cada una lleva un `LEEME.md` que dice cuál.
**Un hueco en la numeración significa siempre que falta algo**, de modo que no
se dejan huecos por comodidad.

---

## Reglas de trabajo

1. **Los originales no se tocan nunca.** Viven en `00_COMUN/08_Originales_crudos`
   y de ahí salen los recortes de `02_Subsets_SNAP_QGIS`, que son los datos de
   partida del práctico y tampoco se editan a mano. Todo archivo derivado va a
   `04_Tablas_de_trabajo` o a `05_Resultados`.
2. **Los archivos pesados no se duplican.** Las descargas originales viven en
   un único lugar: `00_COMUN/08_Originales_crudos/`. Los prácticos las leen
   de ahí a través de la configuración común.
3. **Los scripts se ejecutan siguiendo su numeración.**
4. **Cada resultado debe poder vincularse con el script y los parámetros que lo
   produjeron.** Por eso cada práctico documenta sus corridas.
5. **La resolución, la proyección y el período están en un solo archivo**
   (`00_COMUN/configuracion_comun.py`). Ningún práctico los redefine.
6. **De los datos de GEE que no se descargan** se guarda el identificador del
   catálogo, los filtros, las fechas y el script de consulta.
7. **Cada interacción importante con IA** se registra en `01_Prompt_IA` con el
   prompt, la respuesta, la corrección humana y la verificación.
8. **Nunca se guardan contraseñas, tokens ni credenciales** dentro de
   `03_Scripts`. Las credenciales van en el archivo `.netrc` del usuario o se
   piden al ejecutar.

---

## Épocas del estudio

| Época | Período | Qué representa |
|---|---|---|
| `00_alos` | 2007 – 2010 | Banda L quad-pol de otra década (ALOS-1) |
| `01_base` | oct. 2023 – mar. 2024 | Bosque sin perturbar, un año antes |
| `02_pre` | nov. 2025 – ene. 2026 | Estado inmediatamente anterior al fuego |
| `03_post` | feb. – mar. 2026 | Estado posterior al fuego |

La fecha del incendio no se tomó de una fuente externa: **se dedujo de los
propios datos** (dNBR, caída de γ⁰ y caída del NDVI, en tres sensores
independientes) y después se confirmó con el registro oficial CONAE-AQD.

---

## Entorno de trabajo

Los scripts usan Python con el entorno conda `aoi` (ver
`P0X/03_Scripts/configuracion/entorno_aoi.yml`) y SNAP para el procesamiento SAR.

    conda env create -f entorno_aoi.yml
    conda activate aoi
