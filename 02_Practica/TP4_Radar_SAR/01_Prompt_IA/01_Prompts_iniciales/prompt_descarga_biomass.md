# Prompt para solicitar a una IA la descarga de datos BIOMASS (banda P)

> Copiá y pegá el texto de la sección **PROMPT** en una IA con capacidad de ejecutar
> código / navegar (por ejemplo Claude, con acceso a terminal o a un entorno Python).
> Está redactado para ser reproducible y verificable.

---

## PROMPT

**Rol:** Actuá como especialista en teledetección y radar SAR.

**Objetivo:** Ayudarme a **buscar y descargar imágenes del satélite ESA BIOMASS
(radar de banda P, 435 MHz)** para dos áreas de interés (AOI) ubicadas en la
Patagonia (Argentina/Chile), definidas en los archivos KML adjuntos
`BOSQUE_NW_02.kml` y `ESTEPA_NW_02.kml`.

**Contexto técnico que debés respetar:**

1. Los datos de BIOMASS son abiertos y gratuitos desde el **19/12/2025**.
2. El acceso oficial es vía el **catálogo STAC de ESA MAAP**:
   `https://catalog.maap.eo.esa.int/catalogue/`
3. La **búsqueda** en el catálogo NO requiere credenciales.
   La **descarga** requiere una cuenta gratuita **ESA "EO Sign In"** y un
   **Personal Access Token** (válido 90 días) que se genera en
   `https://portal.maap.eo.esa.int/biomass/` (menú Tools → "Generate Data Access Token").
4. Colecciones abiertas: `BiomassLevel1a` (SLC), `BiomassLevel1b` (DGM),
   `BiomassLevel1c` (stacks co-registrados) y `BiomassLevel2a` (biofísico).
5. La cobertura del radar EXCLUYE Norteamérica, Centroamérica, Europa y parte del
   Ártico (restricción de defensa de EE.UU.). La Patagonia SÍ está cubierta.

**Tareas que te pido, en orden:**

1. Leé cada KML y extraé el *bounding box* (lon_min, lat_min, lon_max, lat_max).
2. Consultá el catálogo STAC y listá los productos disponibles que intersectan
   cada AOI, para las 4 colecciones abiertas, indicando fecha, tipo y órbita.
3. Preguntame por mi Personal Access Token (no lo inventes ni lo asumas).
4. Descargá los productos seleccionados a una carpeta `Imagenes/<AOI>/`.
5. Recortá/enmascará cada imagen al polígono exacto del KML (no solo al bbox).
6. Devolveme un resumen: qué se descargó, fechas, tamaño y rutas.

**Restricciones:**
- No uses fuentes no oficiales ni mirrors.
- Si un paso falla, explicá el error y proponé alternativa; no reintentes en bucle.
- Verificá siempre las URLs contra el dominio oficial `earth.esa.int` / `maap.eo.esa.int`.

**Entregables:** la lista de productos, los archivos descargados, los recortes por AOI,
y un log de lo realizado.

---

## Notas de uso

- Adjuntá los dos `.kml` junto con este prompt.
- Si la IA no puede ejecutar código, pedile que te genere el script de Python
  equivalente (ver carpeta `Script`).
