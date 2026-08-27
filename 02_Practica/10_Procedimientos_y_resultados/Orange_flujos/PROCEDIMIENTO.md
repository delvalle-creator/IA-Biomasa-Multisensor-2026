# Flujos de Orange Data Mining (.ows) — construcción y validación

**Proceso del 26/08/2026 · generados programáticamente y validados contra
Orange 3.39.0 y 3.40.0**

## Qué se construyó

Cuatro flujos con **parámetros fijados** (rutas relativas y variables
preseleccionadas), para que calcular y graficar no exija armar nada:

| Flujo | Dónde vive | Qué muestra |
|---|---|---|
| `TP2_flujo_GEDI_biomasa.ows` | `TP2\09_Orange\` | la referencia L4A: distribución de AGBD, cajas por recinto, rh98 vs AGBD |
| `TP2_flujo_ATLAS_control_terreno.ows` | `TP2\09_Orange\` | el control FABDEM del paso 15: delta, veredictos y el dosel inflado |
| `TP2_flujo_CCI_cotejo.ows` | `TP2\09_Orange\` | la dicotomía CCI vs L4A huella por huella, y CCI vs pendiente |
| `TP5_flujo_sinergia_multisensor.ows` | `TP5\09_Orange\` | ópticos (NDVI…) y radares (banda C y L) contra la biomasa GEDI |

Estructura común: dos **File** (bosque/estepa) → **Concatenate** (agrega la
clase `recinto`) → widgets de análisis. Rutas con prefijo `basedir`:
**los .ows no deben moverse de su carpeta**.

## El error que apareció, y su causa

Al abrir la primera versión en Orange **3.39** apareció
`KeyError: 'graph'` en el Scatter Plot. Causa: los contextos de los widgets
se habían escrito **sin el número de versión interno** (`__version__`).
Orange, al no encontrarlo, asumió contextos de una versión antigua y corrió
TODAS las migraciones; la del Scatter Plot busca la clave `'graph'` que esos
contextos nunca tuvieron. No era un problema de 3.39 contra 3.40: era un
contexto sin versionar.

**Arreglo:** cada contexto y cada bloque de settings lleva ahora el
`settings_version` real del widget, tomado de Orange 3.39 (la menor de las
dos versiones en uso): las migraciones no corren en 3.39 y corren las
correctas en 3.40.

## Control de calidad

Para cada .ows, en **ambas** versiones (3.39.0 y 3.40.0):

1. XML bien formado; todos los `qualified_name` existen en esa versión.
2. Cada bloque de propiedades se deserializa (pickle protocolo 2).
3. `migrate_settings` y `migrate_context` corren sin excepción.
4. **Match de contextos = 2 (perfecto)** contra el dominio real de cada
   tabla tras el Concatenate — las variables aparecen preseleccionadas.

Los CSV de entrada no se tocan: los flujos VEN los resultados; la autoridad
de cada cifra sigue siendo el script numerado que la generó.

Pendiente de cierre: la comprobación visual en el Orange de escritorio
(abrir cada flujo y recorrer sus widgets), que no puede hacerse desde la
nube.
