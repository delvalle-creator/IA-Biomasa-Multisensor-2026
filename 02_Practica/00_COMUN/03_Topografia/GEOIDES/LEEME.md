# Geoides — la ondulación N que une los datums verticales del TP2

Las alturas satelitales del práctico (`h_te_best_fit` de ATL08,
`elev_lowestmode` de GEDI) son **elipsoidales**: metros sobre el elipsoide
WGS84. FABDEM y las cotas de los mapas son **ortométricas**: metros sobre el
geoide. La ondulación N conecta ambas:

    h_elipsoidal = H_ortométrica + N

En este AOI, N ronda los **20 a 22 m**: comparar sin convertir sería un error
de veinte metros — más grande que el dosel que se quiere medir.

| Archivo | Modelo | Para qué |
|---|---|---|
| `geoide_egm2008_AOI.tif` | EGM2008 (NGA, grilla de 2,5′) | el datum nativo de FABDEM: es el N que usa el paso 15 |
| `geoide_ar16_AOI.tif` | GEOIDE-Ar16 (IGN) | la realización del sistema vertical argentino SRVN16 (EPSG:9255); control de sensibilidad |

Ambos son recortes al AOI. En este recinto los dos modelos difieren en menos
de **medio metro** (mediana ≈ −0,1 m): la conclusión del control de terreno no
depende de cuál se use, y el log del paso 15 lo deja registrado. Para cotas
oficiales argentinas corresponde GEOIDE-Ar16; para auditar FABDEM corresponde
EGM2008.

Los archivos de origen quedan en `../../08_Originales_crudos/GEOIDES/`:
`egm08_25.zip` (grilla GTX mundial de 2,5′, NGA) y `ar_ign_GEOIDE-Ar16.zip`
(grilla PROJ del IGN). `egm08_25_subgrid_AOI.bin` es un intermedio de
extracción de la ventana del AOI; el GeoTIFF de esta carpeta lo reemplaza para
todo uso.
