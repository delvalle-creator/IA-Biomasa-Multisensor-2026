# Lea esto primero

**Biomasa forestal en el ecotono bosque-estepa. Curso de posgrado, 14 al 19 de
septiembre de 2026.**

Héctor Francisco del Valle · CeReGeo (FCyT, UADER) · LEMIV (FI, UNPSJB)

---

## Antes que nada: la fe de erratas

`00_FE_DE_ERRATAS.md`, y el mismo texto en `00_FE_DE_ERRATAS.pdf`, es el primer
documento que hay que leer. Dice qué se corrigió respecto de la entrega v1.0.0
del repositorio, que es la que muchos ya descargaron, y qué diferencias quedan
en los PDF que no se rehicieron. Son cuarenta y dos archivos corregidos.
Ninguna corrección cambia las conclusiones del curso, pero varias cambian
resultados que el estudiante entrega.

---

## Qué es esta carpeta

`C:\Temp\CURSO_BIOMASA_2026` es **todo el curso en un solo lugar**: los documentos
que dicen qué hacer, y también los datos, los scripts y los resultados. No hay una
segunda carpeta que buscar.

Los archivos de la raíz están numerados y **se leen en ese orden**. Las carpetas
que vienen después son las de trabajo: la común y una por cada trabajo práctico.

## Ningún Word llega al estudiante

El estudiante recibe **PDF y `.md`**, nada más. Los originales en Word existen
porque son la fuente editable, pero viven apartados: en `_fuente\` y en
`99_PRIVADO_NO_DISTRIBUIR`. El atajo que arma la entrega excluye todo `.docx` y
todo `.pptx` estén donde estén, de modo que la regla no depende de que alguien se
acuerde. Lo que falta convertir está anotado en `_fuente\QUE_FALTA_CONVERTIR.md`.

## Por dónde empezar

La carpeta tiene ahora **tres documentos sueltos y nada más**. Todo lo demás vive
dentro del práctico al que pertenece.

```
CURSO_BIOMASA_2026\
    00_FE_DE_ERRATAS.md            qué se corrigió respecto de la v1.0.0
    00_FE_DE_ERRATAS.pdf           el mismo texto, en PDF
    00_LEEME_PRIMERO.md            este archivo
    00_INSTRUCTIVO_DE_EJECUCION    qué se ejecuta, en qué orden, y cómo saber
                                   que salió bien
    _fuente\                       los originales en Word. No se distribuyen
    01_Teoria\                     las clases teóricas
        01_Presentaciones_pdf\     lo que recibe el estudiante
        02_Fuentes_pptx\           los originales del docente
        03_Lecturas\               material de lectura: The SAR Handbook y
                                   el listado con los enlaces oficiales
    02_Practica\                   todo lo que se ejecuta
        00_Guia_teorica_practica\  la guía completa en PDF y su fuente
        00_COMUN\                  lo que comparten los cinco prácticos
        TP1_Busqueda_IA\           búsqueda, verificación y descarga
        TP2_LiDAR_GEDI_ICESat2\            LiDAR GEDI como referencia
        TP3_Datos_Opticos\         índices ópticos y severidad del incendio
        TP4_Radar_SAR\             radar: bandas C, L y P
        TP5_Sinergia_Multisensor\  sinergia multisensor y mapa final
        10_Procedimientos_y_resultados\  el registro de cómo se hizo cada proceso
        11_Desarrollo_y_respuestas\  el desarrollo resuelto de los cinco prácticos
        09_ATAJOS\                 los nueve .bat, para no escribir rutas a mano
    99_PRIVADO_NO_DISTRIBUIR\      material del docente
```

Los cinco prácticos y `00_COMUN` son carpetas hermanas dentro de `02_Practica`, y
deben seguir siéndolo: los programas averiguan dónde están subiendo por el árbol
hasta encontrarse, y separarlos rompería esa cuenta.

**Primero el instructivo.** Es la secuencia completa, del primer paso al último,
sin teoría. Su sección «Las cuentas» es lo único que conviene resolver **antes**
de la primera clase, porque ninguna alta de catálogo es inmediata.

**Después, cada práctico por separado, en el orden de su número.** Al abrir
cualquiera de los cinco encuentra siempre lo mismo, y en el mismo orden:

```
TP2_LiDAR_GEDI_ICESat2\
    00_Guia_del_practico\          objetivos y figuras del práctico
    00_LEEME.md                    qué hay en cada subcarpeta
    00_DE_DONDE_SALEN_LOS_INSUMOS  qué recortes usa y de qué original salen
    01_Prompt_IA\                  el expediente de trabajo con la IA
    02_Subsets_SNAP_QGIS\                    lo que entra
    03_Scripts\                    lo que se ejecuta
    04_Tablas_de_trabajo\                    los insumos para SNAP y QGIS
    05_Resultados\                 lo que sale
    06_Bibliografia\               las referencias citadas
    07_Preguntas_y_entrega\        lo que responde y entrega el estudiante
    08_Grafos_SNAP\                los grafos del Graph Builder
    NOTAS_TECNICAS.md              advertencias: lo que ya costó caro
```

Sabiendo dónde está una cosa en un práctico, se sabe dónde está en los otros
cuatro. La guía única reúne los cinco prácticos y cada uno de ellos tiene el
mismo orden interno: los objetivos de aprendizaje, la pregunta guía, los
insumos, el desarrollo paso a paso, la fundamentación teórico-práctica, los
controles de calidad, las preguntas que responde el estudiante, el producto a
entregar con sus criterios de evaluación, el resultado esperado y, al cierre,
los acrónimos y las referencias de ese práctico.

## Dos documentos, dos propósitos distintos

Es la distinción que más cuesta al principio, y la que más ordena una vez hecha.

| Tipo | Para qué sirve | Cuándo se usa | Dónde está |
|---|---|---|---|
| **Guía teórico-práctica** | **Hacer y entender.** El desarrollo paso a paso y el fundamento de cada decisión, con figuras y tablas | Antes de la clase para leerla, y durante la clase al lado del teclado | `02_Practica\00_Guia_teorica_practica`, en PDF |
| **Instructivo de ejecución** | **Ordenar la corrida.** Qué se ejecuta, en qué orden y cómo saber que salió bien | Durante la clase | En la raíz del curso |

A esos dos se suma, dentro de cada práctico, su **guía sintética en PDF**
(`00_Guia_del_practico\00_GUIA_TPn_sintetica.pdf`): pregunta, insumos, la
secuencia con su ubicación exacta, controles y evaluación. La guía única
desarrolla y fundamenta; la sintética ordena la corrida de ese práctico.

A esos tres se agrega `01_Prompt_IA`, que no es un documento sino un expediente:
el prompt inicial, la respuesta que dio la inteligencia artificial, el prompt
corregido y la verificación. Sirve para **destrabar** cuando algo falla, y es
además contenido del curso.

## Dentro de cada práctico, el primer archivo es el que orienta

Los cinco prácticos tienen la misma estructura, de modo que se busca sin
memorizar. Al abrir cualquiera de ellos:

- **`00_LEEME.md`** encabeza la lista: dice qué hay en cada subcarpeta y qué
  script deja cada resultado. Es el punto de entrada del práctico.
- `NOTAS_TECNICAS.md` reúne las advertencias técnicas: lo que ya costó caro.
  No es punto de entrada, y no hace falta leerlo para trabajar.
- `03_Scripts\00_ORDEN_DE_EJECUCION.md` da la secuencia exacta de ejecución.

## Cómo llega el material, y sobre qué se trabaja

Las descargas completas suman unos **252 GB** (inventario.csv, 68 productos únicos) y llegan en un disco. Usted ya las
tiene: no necesita bajarlas. La descarga **se practica igual**, sobre una escena o
dos, porque saber pedirle a un catálogo exactamente lo que uno necesita es parte
del oficio y no se aprende leyendo.

Del TP2 en adelante **se trabaja siempre sobre los recortes de los dos recintos**.
Pesan muy poco, caben en cualquier equipo y permiten repetir una cadena entera en
minutos. El original queda como respaldo y como prueba: si un recorte resulta
dudoso, se vuelve a él y se comprueba.

## Las cuentas, antes de empezar

Varios catálogos no responden sin una cuenta, y ninguna de esas altas es
inmediata. Están las siete en la Tabla 2 del instructivo, con su dirección
verificada. Dos aclaraciones que ahorran tiempo: **NASA Earthdata y ASF son una
sola cuenta**, no dos; y **ESA MAAP**, el de BIOMASS, es el único que además exige
generar una ficha de acceso de noventa días.

## Las tres marcas

Cada paso del instructivo lleva una de estas tres:

| Marca | Qué significa |
|---|---|
| **SE CORRE** | Lo ejecuta usted en clase. Son los scripts de Python de la cadena |
| **YA VIENE HECHO** | El producto está en la carpeta. Lo abre, lo inspecciona y sigue |
| **AUXILIAR** | Diagnóstico. Sólo si algo falló y hay que averiguar por qué |

No hay tiempos por paso. El curso corre de lunes a viernes, de 9 a 13 (teoría) y
de 14 a 18 (práctica): son veinte horas de práctica para cinco trabajos
prácticos, y poner minutos por paso agregaría presión sin agregar información.

## El entorno: se abre una vez y se deja abierto

```
conda activate aoi
cd C:\Temp\CURSO_BIOMASA_2026\02_Practica
python TP2_LiDAR_GEDI_ICESat2\03_Scripts\comprobar_entorno.py
```

La tercera orden no es un paso del práctico: comprueba que estén los paquetes que
la cadena necesita y, si falta alguno, imprime la línea exacta de instalación.

## Cuando algo falle

Va a fallar algo, y está previsto. El orden es: **leer el mensaje completo**,
**comprobar el paso anterior**, y sólo entonces **consultar a la IA** —pero
llevándole el material del `01_Prompt_IA` de ese práctico, no una pregunta suelta.
Esa diferencia es contenido del curso, no una muleta.

---

# Dónde vive cada cosa

## 2. Dentro de `00_COMUN`

| Subcarpeta | Qué contiene |
|---|---|
| `01_AOI` | Los polígonos de los dos recintos de 15 × 15 km |
| `02_Coberturas` | La capa de cobertura del suelo usada para estratificar |
| `03_Topografia` | Modelo de elevación, pendiente, orientación y sombreado |
| `07_Diccionario_datos` | Qué significa cada columna de cada tabla |
| `08_Originales_crudos` | **Los originales descargados: `.zip`, `.h5`, `.xemt`. 252 GB.** Están aquí y no en cada práctico porque una misma escena sirve a varios. No se tocan nunca |
| `GLOSARIO.md` | Términos del curso |
| `configuracion_comun.py` | Rutas, CRS y malla común. Lo importan todos los scripts |
| `COMO_CAMBIAR_DE_AREA.md` | Qué tocar (y qué rehacer) para llevar este flujo de trabajo a otros recintos u otra región |

## 3. Dentro de cada trabajo práctico

La estructura se repite en los cinco, lo que permite buscar sin memorizar.

| Subcarpeta | Qué contiene |
|---|---|
| `00_Guia_del_practico` | **La guía sintética del práctico, en PDF** (empiece por ella), su LEEME, y los objetivos, figuras, diapositivas y anexos. El desarrollo completo está en su capítulo de la guía teórico-práctica (`02_Practica\00_Guia_teorica_practica`) |
| `01_Prompt_IA` | Cuatro subcarpetas: prompt inicial, respuesta de la IA, prompt corregido y verificación |
| `02_Subsets_SNAP_QGIS` | **Sobre esto se trabaja.** Los recortes: pares `.dim` + `.data` y GeoTIFF, ya ajustados a los dos recintos |
| `03_Scripts` | Lo que se ejecuta, agrupado por etapa |
| `04_Tablas_de_trabajo` | Las tablas `.csv` intermedias: muestras, entrenamiento y validación |
| `05_Resultados` | Lo que sale: rásters, vectores, tablas y gráficos |
| `06_Bibliografia` | Las referencias citadas en la guía |
| `07_Preguntas_y_entrega` | Las preguntas del práctico y lo que entrega el estudiante |
| `08_Grafos_SNAP` | Los grafos del Graph Builder, con su `LEEME_grafos.md` |
| `00_LEEME.md` | **Qué hay en cada carpeta de este práctico.** Es el primer archivo de la lista, y por eso encabeza |
| `NOTAS_TECNICAS.md` | Advertencias técnicas del práctico: lo que ya costó caro y conviene no repetir |

La estructura se repite en los cinco, aunque algunas subcarpetas queden
vacías: el TP5, por ejemplo, no descarga ni pre-procesa nada y consume lo que
dejaron los cuatro anteriores, de modo que su `02_Subsets_SNAP_QGIS` está vacía
a propósito. El TP2 y el TP5 suman además `09_Orange\`, con los flujos de
Orange Data Mining del curso, y `02_Practica\10_Procedimientos_y_resultados\`
guarda el registro de cómo se hizo cada proceso, con sus capturas.
`02_Practica\11_Desarrollo_y_respuestas\` contiene el desarrollo resuelto de
los cinco prácticos — la corrida completa con los datos expuestos, las figuras
del bosque y de la estepa, y las respuestas modelo a las preguntas de cada
práctico. Conviene consultarla después de intentar el práctico, no en lugar de
intentarlo.

## 4. Los nueve atajos

| Archivo | Qué ejecuta | ¿Credenciales? |
|---|---|---|
| `09_ATAJOS\EJECUTAR_cadena_escenarioB.bat` | Diez pasos: los del TP2 desde el 7, más los cinco del TP5 | No |
| `09_ATAJOS\EJECUTAR_TP5_desde_modelos.bat` | Los cuatro últimos pasos del TP5, desde los modelos | No |
| `09_ATAJOS\EJECUTAR_diagnostico_del_piso.bat` | El auxiliar `TP5_06_diagnostico_del_piso`, que averigua de dónde sale el piso del ensayo nulo | No |
| `09_ATAJOS\EJECUTAR_consulta_BIOMASS.bat` | Consulta el catálogo de la ESA sobre los dos recintos y sobre la región andina | No |
| `09_ATAJOS\EJECUTAR_descarga_BIOMASS.bat` | Descarga los productos BIOMASS de nivel 2A | **Sí, ficha de 90 días** |
| `09_ATAJOS\EJECUTAR_recorte_mapas_Chubut.bat` | Recorta a los dos recintos tres capas del producto forestal de Chubut | No |
| `09_ATAJOS\EJECUTAR_TP2_rama_ICESat2.bat` | La rama ICESat-2 del TP2 completa, control de terreno incluido: pasos 12 a 16 | No |
| `09_ATAJOS\COPIAR_CRUDOS_A_RESPALDO.bat` | Copia los originales crudos al disco de respaldo (sólo lo que falta). Es del docente | No |
| `09_ATAJOS\CREAR_ENTREGA_ESTUDIANTES.bat` | Arma `_ENTREGA_ESTUDIANTES` con lo que se copia al estudiante | No |

Cada uno imprime al arrancar las órdenes equivalentes del Miniforge Prompt, de
modo que también sirve como documentación.

## 5. Dónde está cada tipo de archivo

| Busco… | Está en… |
|---|---|
| Un script para ejecutar | `TPn_*\03_Scripts\<etapa>\` |
| Un grafo de SNAP | `TP4_Radar_SAR\08_Grafos_SNAP\*.xml` |
| Un ráster de resultado | `TPn_*\05_Resultados\02_Rasters\` |
| Una tabla de resultado | `TPn_*\05_Resultados\04_Tablas\` |
| Una figura | `TPn_*\05_Resultados\05_Graficos\` |
| Un archivo de estilo para QGIS | Junto al ráster que estiliza, con extensión `.qml` |
| La escena original sin procesar | `00_COMUN\08_Originales_crudos\<época>\<sitio>\` |
| Qué significa una columna | `00_COMUN\07_Diccionario_datos\` |
| Un término que no entiendo | `00_COMUN\GLOSARIO.md` |
| Cómo usar estos scripts en OTRA área de estudio | `00_COMUN\COMO_CAMBIAR_DE_AREA.md` |

No todos los prácticos tienen todas esas subcarpetas: cada uno crea las que
necesita. Si una no existe, es porque ese práctico no produce ese tipo de salida.

## 6. Formatos que aparecen y cómo se abren

| Extensión | Qué es | Con qué se abre |
|---|---|---|
| `.tif` | Ráster georreferenciado | QGIS, o Python con rasterio |
| `.csv` | Tabla separada por comas | Planilla de cálculo, o Python con pandas |
| `.gpkg` | Paquete de geometría | QGIS |
| `.h5` | Gránulo jerárquico de GEDI | Sólo por script; no lo abra a mano |
| `.dim` + `.data` | Producto de SNAP | SNAP. **El par nunca se separa** |
| `.xml` | Grafo de procesamiento de SNAP | Graph Builder de SNAP |
| `.qml` | Estilo de capa | QGIS lo toma solo si comparte nombre con el ráster |
| `.md` | Documento de texto | Ver abajo |
| `.pdf` | Documento para leer | Cualquier lector de PDF |

### Los `.md` conviene leerlos formateados

Casi toda la documentación del curso está en archivos `.md`. Son texto, y se
abren con cualquier editor, pero escritos en un formato que marca los títulos
con almohadillas, la negrita con asteriscos y las tablas con barras verticales.
Abiertos en el Bloc de notas o en Word, esas marcas se ven crudas y estorban.

Hay dos maneras cómodas de leerlos, y ninguna exige instalar nada nuevo:

- **En el repositorio de GitHub**, haciendo clic en el archivo. Se ven
  formateados, con las tablas armadas y los títulos en su tamaño.
- **En Visual Studio Code**, abriendo el archivo y presionando
  **`Ctrl` + `Shift` + `V`**: se abre una pestaña con el documento formateado.
  Con `Ctrl` + `K` y después `V` queda al lado del texto, en dos columnas.

## 7. Tres advertencias

**La escena óptica anterior al incendio es la del 25 de noviembre de 2025**, no la
del 9 de enero de 2026, aunque esta última sea más cercana al evento: quedó mal
corregida atmosféricamente. El motivo está escrito en la propia carpeta de
insumos del TP3.

**Los grafos de SNAP que terminan en `_cli` no son para usted.** De los
veintiséis grafos del TP4, que ahora viven en `08_Grafos_SNAP`, nueve tienen un
gemelo con ese sufijo: son para la
línea de órdenes, los usa Python y no abren bien en la interfaz gráfica. Trabaje
siempre con los que no lo llevan.

**BIOMASS, la banda P, no interviene en el análisis.** Su nivel 2A se publicó el
30 de junio de 2026 y hay diez productos descargados, pero todas las
adquisiciones son posteriores al incendio, de modo que no permiten medir el
cambio. Entra como demostración del sensor, y así debe declararse al responder las preguntas del práctico.
