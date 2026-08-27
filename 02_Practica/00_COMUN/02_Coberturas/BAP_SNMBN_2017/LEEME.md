# Cobertura vegetal BAP / SNMBN 2017 — recortes de los dos recintos

## Que es esta capa

Es el relevamiento de bosque nativo del **Sistema Nacional de Monitoreo de
Bosques Nativos (SNMBN)**, capa **BAP** (Bosque Andino Patagonico) de la
provincia del Chubut, **año de referencia 2017**, recortada a los dos recintos
de 15 x 15 km del proyecto.

El recorte lo preparo el docente. Lo que se guarda aca es el resultado, sin
modificar: los atributos originales de la capa mas la superficie, el perimetro y
el porcentaje del recinto que ocupa cada fragmento.

## Por que importa

**El recinto BOSQUE_NW_02 no es bosque.** Es un mosaico:

| Cobertura (LEYENDA_N3) | % del recinto |
|---|---|
| Ñire Bajo | 34,84 |
| Lenga | 33,02 |
| Ñire | 11,57 |
| Cipres | 4,90 |
| Estepa | 3,68 |
| Lenga Baja | 3,15 |
| otras doce clases | 8,84 |

Y **ESTEPA_NW_02 es 84,64 % estepa**, con un 8,4 % de clases leñosas que
sobreviven en las quebradas y en los mallines: es un ecotono, no una estepa pura.

Cualquier promedio de biomasa calculado sobre el recinto entero mezcla lenga alta
con ñire de porte arbustivo. El numero que sale no describe a ninguno de los dos
y, ademas, depende de cuantas huellas de GEDI cayeron en cada clase, que es un
accidente de las orbitas. Por eso, a partir de ahora, **los resultados se informan
por clase de cobertura, no por recinto**.

## Archivos

| Archivo | Contenido |
|---|---|
| `BAP_<AOI>_recorte.shp` | poligonos BAP recortados al recinto, con atributos originales y metricas por fragmento |
| `BAP_<AOI>_resumen_N3.shp` | las mismas coberturas disueltas por `LEYENDA_N3`, con superficie y % del recinto |
| `BAP_<AOI>_resumen_N3.csv` | la tabla del resumen, en UTF-8 |
| `<AOI>_AOI.shp` | limite del recinto, con superficie y perimetro calculados |
| `QA_<AOI>.json` | controles geometricos del recorte |
| `*.qml` | simbologia categorizada original de la capa BAP |

## Campos que se usan aguas abajo

- **`LEYENDA_N3`** — la clase fina: `Lenga`, `Ñire Bajo`, `Cipres`, `Estepa`, ...
- **`LEYENDA_N2`` / `LEYENDA_N1`** — los dos niveles de agregacion superiores.
- **`GRUPO`** — agrupamiento corto: `lenga`, `nire`, `cipres`, `estepa`, `humedal`, ...
- **`BOSQUE`** — `SI` / `NO` segun el SNMBN. Ojo: `Ñire Bajo` figura como `SI`
  aunque su altura mediana medida por GEDI en este recinto sea de 3,8 m.
- **`AREA_HA`**, **`PCT_AOI`** — los pesos con los que se estratifica.

## Controles verificados

- Sistema de coordenadas **EPSG:32719** (WGS 84 / UTM 19S), el mismo de la
  grilla comun del proyecto. No hace falta reproyectar nada.
- Cobertura del recinto: **100,000 %** en los dos casos. Sin huecos ni
  solapamientos (`QA_<AOI>.json`).
- Superficie reconstruida al leer los shapefiles respetando los anillos
  interiores: **225,000000 km²** exactos en los dos recintos, contra los
  225 km² teoricos del cuadrado de 15 x 15 km.

## Limitacion que hay que declarar en clase

El relevamiento es de **2017** y las huellas de GEDI son de **2019-2024**. Entre
una fecha y otra puede haber cambios de cobertura que esta capa no registra. Para
el uso que se le da —estratificar, no medir— la desactualizacion es tolerable,
pero **no se puede usar esta capa como verdad de campo de la fecha de la huella**.

## Quien la usa

`TP2_LiDAR_GEDI_ICESat2/03_Scripts/02_Procesamiento/cobertura_BAP/TP2_09_cobertura_BAP.py`
le pega a cada huella GEDI la clase mayoritaria dentro de su circulo de 25 m de
diametro y genera los archivos `*_con_cobertura.csv`.
