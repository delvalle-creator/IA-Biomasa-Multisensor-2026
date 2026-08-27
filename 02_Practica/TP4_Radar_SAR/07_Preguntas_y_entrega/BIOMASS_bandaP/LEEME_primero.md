# Proyecto BIOMASS — Descarga por AOI (BOSQUE y ESTEPA)

Paquete de trabajo para descargar imágenes del satélite **BIOMASS** (ESA, radar banda P)
sobre dos áreas de la Patagonia, separadas por AOI.

## Por dónde empezar
👉 El procedimiento —cuentas, ficha de acceso y descarga— está en las
**secciones 3.3 y 3.4 de la guía teórico-práctica**
(`02_Practica\00_Guia_teorica_practica`). El tutorial original
(`Informe/TUTORIAL_paso_a_paso.docx`) viene dentro de `BIOMASS.zip`, en esta
misma carpeta.

## Contenido de `BIOMASS.zip`

- **Prompt_IA/** — un prompt para pedirle a una IA que haga la descarga.
- **Script/**
  - `BIOMASS_Colab.ipynb` — cuaderno para Google Colab (recomendado). Pegás el token y corrés.
  - `descargar_biomass.py` — el mismo proceso como script de Python para PC.
- **Imagenes/**
  - `BOSQUE_NW_02.kml`, `ESTEPA_NW_02.kml` — las dos áreas de interés.
  - `mapa_ubicacion_AOIs.png` — mapa de ubicación.
  - `BOSQUE_NW_02/`, `ESTEPA_NW_02/` — donde caen las descargas de cada zona.
- **Informe/**
  - `TUTORIAL_paso_a_paso.docx` — el tutorial original (el procedimiento vigente
    está en la guía teórico-práctica, secciones 3.3 y 3.4).
  - `Informe_BIOMASS.docx` — informe técnico del sensor.
- **SNAP/**
  - `Guia_SNAP_BIOMASS.docx` — cómo procesar el producto en ESA SNAP.
  - los dos grafos `.xml` listos para el Graph Builder, con su esquema.

## Resumen de resultados
- **ESTEPA**: cobertura en **verano** (febrero 2026).
- **BOSQUE**: cobertura en **otoño** (abril–junio 2026).
- Usar los productos **`1S`** (traen la imagen); los `1M` son livianos sin imagen.
- Abrir las imágenes con **ESA SNAP 13+** (Microwave Toolbox).

## Recordatorio del token
Para descargar necesitás tu **token offline** de la ESA:
https://portal.maap.eo.esa.int/ini/services/auth/token/ → *Copy access token*.
Se pega en el cuaderno/script (es secreto, no lo compartas).
