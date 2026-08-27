# Cómo cambiar de área: llevar este flujo de trabajo a otra región

Todo el proyecto está construido para que los cinco prácticos trabajen
sobre la misma grilla, definida **una sola vez**. Esa decisión es la que
hace posible cambiar de área: no hay que tocar los scripts de
procesamiento — hay que cambiar la **configuración** y rehacer los **datos
que son propios del lugar**. Este documento dice exactamente qué, dónde y
en qué orden.

## 1. La regla de oro: una sola fuente de verdad, en seis copias

El área de estudio vive en `configuracion_comun.py`. El archivo existe en
**seis copias idénticas** — la de `00_COMUN\` y una en
`<práctico>\03_Scripts\configuracion\` de cada práctico, porque cada
script importa la copia de su práctico. Por eso la regla es:

> **Se edita la copia de `00_COMUN\` y se copia sobre las otras cinco.**
> Si una copia queda distinta, dos prácticos trabajarán sobre grillas
> distintas sin dar ningún error.

Desde el «Símbolo del sistema» (ajuste la ruta si su curso no está en
`C:\Temp`):

    cd C:\Temp\CURSO_BIOMASA_2026\02_Practica
    for %d in (TP1_Busqueda_IA TP2_LiDAR_GEDI_ICESat2 TP3_Datos_Opticos TP4_Radar_SAR TP5_Sinergia_Multisensor) do copy /Y 00_COMUN\configuracion_comun.py %d\03_Scripts\configuracion\

## 2. Qué cambiar dentro de `configuracion_comun.py`

Cinco bloques, en este orden:

**a) `EPSG` — la proyección.** Es la zona UTM del nuevo lugar:
`327xx` para el hemisferio sur, `326xx` para el norte, donde `xx` es la
zona (aquí, 19 → `32719`). Si el nuevo área cae a caballo de dos zonas,
elija la que contenga la mayor parte y declare la decisión.

**b) `PIXEL` y `NPIX` — la grilla.** `PIXEL = 10` m es la resolución común
(la de Sentinel-1 y 2; conviene no cambiarla) y `NPIX = 1500` define
recintos de 15 × 15 km. Un recinto más grande multiplica el volumen de
TODO lo que sigue: duplicar el lado cuadruplica los datos.

**c) `AOIS_UTM` — los recintos.** Las **claves** del diccionario son los
nombres de los sitios y las **esquinas** (xmin, ymin, xmax, ymax) van en
la proyección de `EPSG`, **alineadas a múltiplos de `PIXEL`** (terminadas
en 0 con píxel de 10 m): esa alineación es la que permite apilar los
sensores sin remuestrear. Los nombres de las claves se propagan solos:
los scripts recorren este diccionario, y las subcarpetas y archivos
derivados (`dem_<SITIO>.tif`, `fabdem_<SITIO>_wgs84.tif`, las carpetas por
sitio de `02_Subsets_SNAP_QGIS`…) toman su nombre de aquí. Puede haber
dos sitios, uno o más de dos — pero el diseño experimental del curso
(un sitio de interés y un **sitio control**) vale la pena conservarlo.

**d) `AOIS_WGS84` — los mismos recintos en grados.** Son los que se les
pasan a los catálogos. Recalcúlelos a partir de las esquinas UTM (QGIS lo
hace, o cualquier conversor UTM→WGS84; verifique que el rectángulo
geográfico CONTENGA al recinto UTM).

**e) `EPOCAS` e `INCENDIO` — el tiempo.** Ponga las fechas de su propio
estudio. Si el nuevo área no tiene un evento (incendio, tala, plaga),
puede trabajar con menos épocas; si lo tiene, la función
`dentro_del_incendio` protege de etiquetar como «antes» o «después» una
escena tomada DURANTE el evento — defina bien las dos fechas frontera.

## 3. Los datos de `00_COMUN\` que son del lugar y hay que rehacer

| Carpeta | Qué contiene | Qué hacer en otra área |
|---|---|---|
| `01_AOI\` | KML/GeoJSON de los recintos | Regenerarlos con las esquinas nuevas (QGIS o los scripts del TP1) |
| `02_Coberturas\BAP_SNMBN_2017` | Mapa de coberturas del bosque andino patagónico | **Es argentino.** Reemplazar por el mapa de coberturas local — la media estratificada del TP2 (paso 9) y los escenarios por clase dependen de él |
| `02_Coberturas\areas_quemadas` | El registro CONAE-AQD | Reemplazar por el registro oficial de incendios de la región (o quitar ese cruce) |
| `03_Topografia\DEM` | Copernicus GLO-30 recortado | Se regenera: SNAP lo descarga solo al correr Terrain Flattening |
| `03_Topografia\FABDEM` | El suelo desnudo, árbitro del control de terreno | Bajar el o los **tiles del área nueva**: los nombres son la esquina SW en grados (aquí `S43W072`); un recinto puede cruzar dos tiles |
| `03_Topografia\GEOIDES` | EGM2008 (subgrilla del AOI) y el geoide local | Bajar la subgrilla EGM2008 del área nueva; el geoide nacional local (aquí GEOIDE-Ar16) es opcional — en este proyecto difieren < 0,5 m, pero eso hay que **verificarlo**, no suponerlo |
| `08_Originales_crudos\` | Todas las descargas | Se llena corriendo el TP1 sobre el área nueva |

También es del lugar `TP3\02_Subsets_SNAP_QGIS\Mapas_forestales_Chubut`
(las capas provinciales): en otra región se reemplaza por la cartografía
local equivalente, o se omiten esos cruces declarándolo.

## 4. Lo que hay que revisar a mano, porque no es configuración

- **GEDI sólo existe entre ±51,6° de latitud.** Más al sur o más al norte
  no hay huellas — y sin GEDI no hay referencia: ahí la alternativa es
  ICESat-2/ATL08 (llega a latitudes altas), sabiendo lo que este curso
  midió sobre su comportamiento en dosel bajo.
- **Tile y órbita de Sentinel-2.** Aquí cada recinto cae en un tile
  (T18GYT y T19GCN, órbita R053). En el área nueva, TP1_03 busca por
  coordenadas y resuelve solo — pero si el recinto cae entre dos tiles
  conviene elegir uno y ser consistente.
- **Órbita de Sentinel-1.** Aquí se usa el track 164 ascendente para
  todas las fechas. En el área nueva, elija UN track y UNA dirección y
  quédese con ellos: mezclar geometrías arruina las series temporales.
- **SAOCOM** exige un pedido nuevo a la CONAE (el trámite modelo está en
  `00_COMUN\08_Originales_crudos\PEDIDO_SAOCOM_28jul2026.md`), y la
  cobertura cuadripolar no está garantizada en cualquier sitio — aquí no
  cubría la estepa.
- **Los estratos del GEDI L4A** (`predict_stratum`: DBT_SA, GSW_SA…)
  cambian con la región del mundo: el análisis de hoja caída del TP2 (paso
  11) está razonado para bosques deciduos templados y hay que repensarlo
  para otra vegetación.
- **Los umbrales declarados** — sensibilidad ≥ 0,9, el filtro de
  pendiente, el ± 5 m del control FABDEM, los cortes de Key y Benson para
  el dNBR — son defendibles en general, pero en el informe del área nueva
  deben **declararse y justificarse de nuevo**, no heredarse en silencio.
- **La alometría del TP5 no se toca:** los coeficientes a y b se ajustan
  con los propios datos de cada corrida, así que se recalculan solos para
  el área nueva.

## 5. El orden de trabajo y la comprobación

1. Editar `configuracion_comun.py` (§ 2) y copiarlo a los cinco prácticos (§ 1).
2. Rehacer los datos del lugar (§ 3): AOI, coberturas, FABDEM, geoides.
3. Correr `00_COMUN\comprobar_entorno.py` — el entorno no cambia con el área.
4. Correr el TP1 **empezando por los pasos 1 y 2**: verificar cobertura y
   bruma ANTES de descargar. La regla del TP1 es exactamente para esto: en
   un área nueva, nada garantiza que los productos existan, cubran y sirvan.
5. Seguir el `00_INSTRUCTIVO_DE_EJECUCION` de la raíz, en su orden. Si un
   script falla en el área nueva, lo primero que se revisa es la § 3: casi
   siempre falta un dato del lugar, no sobra un error del script.

Una advertencia final. Cambiar de área no es sólo cambiar coordenadas: los
**números del curso no viajan**. La supervivencia del filtrado, la razón
ATLAS/GEDI, el punto de saturación del NDVI, el piso del ensayo nulo —
todos son resultados de ESTE paisaje. En el área nueva habrá que medirlos
otra vez, y esa es precisamente la gracia: el flujo de trabajo es lo que
se lleva; las respuestas se ganan en cada lugar.
