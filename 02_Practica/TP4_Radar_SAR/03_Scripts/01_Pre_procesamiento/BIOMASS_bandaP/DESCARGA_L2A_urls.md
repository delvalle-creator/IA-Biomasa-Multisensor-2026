# BIOMASS nivel 2A sobre BOSQUE_NW_02: los ocho productos y sus enlaces

Obtenidos del catálogo de ESA MAAP, colección `BiomassLevel2a`, sobre el
recuadro del recinto de bosque. El catálogo informa `numberMatched: 8`, que
coincide exactamente con lo que devolvió `buscar_biomass_L2.py`.

La consulta es abierta; **la descarga requiere estar autenticado** ante la ESA
(`auth:refs: ["oidc"]`). Pegando el enlace en un navegador ya logueado, la
descarga arranca sola. El catálogo **no informa el tamaño** de estos paquetes:
se generan al vuelo, así que no hay cifra que anticipar.

## Consulta que produce esta lista

```
https://catalog.maap.eo.esa.int/catalogue/search?collections=BiomassLevel2a
   &bbox=-71.5977,-42.6952,-71.4096,-42.5563
   &limit=20&fields=id,properties.datetime,assets.product
```

Todo junto en una sola línea, con `&` de verdad. **Cuidado al copiar enlaces de
otras fuentes:** si los `&` vienen escritos como `%26`, el servidor lee toda la
cadena como un único parámetro y la búsqueda no filtra por lo que uno cree.

## Los cuatro recomendados

Cubren **los dos recintos a la vez**, así que con estos cuatro alcanza para
bosque y estepa. Son dos pasadas de órbitas distintas —una de la tarde, traza
014, y otra de la mañana, traza 036—, de modo que permiten comprobar si dos
geometrías independientes dan la misma altura sobre el mismo bosque.

| Fecha | Traza | Tipo | Identificador |
|---|---|---|---|
| 07/06/2026 | T014 F192 | altura de dosel | `BIO_FP_FH__L2A_20260607T223212_20260619T223240_T_G01_M03_C___T014_F192_02_DTZJH5` |
| 07/06/2026 | T014 F192 | suelo cancelado | `BIO_FP_GN__L2A_20260607T223212_20260619T223240_T_G01_M03_C___T014_F192_02_DTZJJ3` |
| 09/06/2026 | T036 F274 | altura de dosel | `BIO_FP_FH__L2A_20260609T105815_20260621T105843_T_G01_M03_C___T036_F274_02_DU0DEP` |
| 09/06/2026 | T036 F274 | suelo cancelado | `BIO_FP_GN__L2A_20260609T105815_20260621T105843_T_G01_M03_C___T036_F274_02_DU0DGJ` |

Enlaces de descarga, en el mismo orden:

```
https://catalog.maap.eo.esa.int/data/zipper/biomass-pdgs-01/BiomassLevel2a/2026/06/07/BIO_FP_FH__L2A_20260607T223212_20260619T223240_T_G01_M03_C___T014_F192_02_DTZJH5/BIO_FP_FH__L2A_20260607T223212_20260619T223240_T_G01_M03_C___T014_F192_02_DTZJH5
https://catalog.maap.eo.esa.int/data/zipper/biomass-pdgs-01/BiomassLevel2a/2026/06/07/BIO_FP_GN__L2A_20260607T223212_20260619T223240_T_G01_M03_C___T014_F192_02_DTZJJ3/BIO_FP_GN__L2A_20260607T223212_20260619T223240_T_G01_M03_C___T014_F192_02_DTZJJ3
https://catalog.maap.eo.esa.int/data/zipper/biomass-pdgs-01/BiomassLevel2a/2026/06/09/BIO_FP_FH__L2A_20260609T105815_20260621T105843_T_G01_M03_C___T036_F274_02_DU0DEP/BIO_FP_FH__L2A_20260609T105815_20260621T105843_T_G01_M03_C___T036_F274_02_DU0DEP
https://catalog.maap.eo.esa.int/data/zipper/biomass-pdgs-01/BiomassLevel2a/2026/06/09/BIO_FP_GN__L2A_20260609T105815_20260621T105843_T_G01_M03_C___T036_F274_02_DU0DGJ/BIO_FP_GN__L2A_20260609T105815_20260621T105843_T_G01_M03_C___T036_F274_02_DU0DGJ
```

## Verificación previa, antes de bajar

Cada producto publica una miniatura en `/public/`, **sin autenticación**, con el
mismo nombre del producto en minúsculas y terminada en `_fh_th.jpg`,
`_gn_th.jpg` o `_fhquality_th.jpg`. Mirarla es la aplicación directa de la regla
del TP1: comprobar antes de descargar.

Comprobadas las dos de altura de dosel recomendadas: **las dos
traen la franja completa, con relieve y estructura de bosque bien visibles.** No
hay huecos ni bandas sin dato.

Una advertencia sobre el método: la miniatura del producto del 07/06 apareció al
principio con la mitad inferior gris uniforme, y eso parecía falta de dato. **Era
la imagen a medio cargar.** Al recargarla salió completa. Conviene esperar a que
termine de cargar antes de descartar una escena: aquí estuvo a punto de
descartarse una escena buena por mirarla demasiado rápido.

## Los otros cuatro, por si hacen falta

Cubren el bosque pero no la estepa, o al revés.

| Fecha | Traza | Tipo | Identificador |
|---|---|---|---|
| 26/04/2026 | T014 F192 | altura de dosel | `..._20260426T223145_..._DSOJ82` |
| 26/04/2026 | T014 F192 | suelo cancelado | `..._20260426T223145_..._DSOJAA` |
| 17/05/2026 | T014 F192 | altura de dosel | `..._20260517T223159_..._DTF9M3` |
| 17/05/2026 | T014 F192 | suelo cancelado | `..._20260517T223159_..._DTF9O6` |

## Dónde guardarlos, y qué hacer después

Descomprimir en `00_COMUN\08_Originales_crudos\03_post\BIOMASS_bandaP\`, que es donde viven
los originales y no se tocan. Después:

1. `python TP4_11_inspeccionar_biomass_L2A.py <carpeta del producto>` para
   obtener los nombres reales de banda.
2. Pegar la línea que imprime en `graph_biomass_l2a_altura.xml` y ejecutarlo.
3. Si hace falta comparar píxel a píxel contra el mapa del TP5, encadenar
   `graph_biomass_a_malla_comun.xml`.

**Recordar al informar:** las cuatro adquisiciones son de junio de 2026 y el
incendio terminó el 27 de febrero. Sirven para verificar la altura que estima el
modelo, no para medir el cambio producido por el fuego.
