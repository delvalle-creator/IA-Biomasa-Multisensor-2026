# Verificación de los resultados del TP2

Los scripts dicen cosas. Acá está cómo se comprobó cada una **contra algo
independiente**, que es la única forma de auditar a una IA.

## 1. El filtrado descarta la mayor parte de los disparos. ¿Es creíble?

| Sitio | Disparos en el AOI | Aceptados por calidad | Válidos tras pendiente | Sobrevive |
|---|---|---|---|---|
| Bosque | 6.288 | 1.025 | 690 | 11,0 % |
| Estepa | 11.222 | 4.041 | 3.084 | 27,5 % |

**Cómo se verificó.** No creyéndole al script. Primero, las dos tasas difieren
—11,0 % en el bosque y 27,5 % en la estepa— y esa diferencia tiene explicación
física: un pastizal ralo devuelve formas de onda simples, sin estructura vertical
que confunda, y el láser llega al suelo en casi todos los disparos. Si las dos
tasas hubieran coincidido, habría habido que sospechar del filtro. Segundo, la
literatura
coincide: Adam et al. (2020) y Moudrý et al. (2024) reportan tasas de supervivencia del
orden del diez al quince por ciento en bosques templados, que es donde cae el bosque. Tercero, y esto es lo que cierra: los descartes
se guardaron con su motivo, y al abrirlos en QGIS **los rechazados por pendiente
caen sobre las laderas del DEM**. Eso no se puede fingir.

**La distinción que hay que fijar antes de contar.** Caer dentro del AOI es una
condición NECESARIA pero NO SUFICIENTE:

| Los disparos del bosque | Qué es | Cuántos |
|---|---|---|
| **CAEN en el AOI** | criterio geográfico: dice dónde están, no si sirven | 6.288 |
| de ésos, fuera por calidad | forma de onda, órbita, energía | 5.263 |
| de ésos, fuera por pendiente | ladera de más de veinte grados | 335 |
| de ésos, **VÁLIDOS** | **caen en el AOI Y ADEMÁS pasan los filtros. Es la muestra real** | **690** |

Los 690 son un **subconjunto** de los 6.288, no una categoría aparte. La regla:
nunca informe los disparos del AOI como si fueran su muestra. Informe siempre las
dos cifras y la tasa entre ellas.

## 2. La altura del dosel: ¿el control funciona?

| Sitio | rh95 mediana | Interpretación |
|---|---|---|
| Bosque | ~10 m (rango 2–38 m) | dosel real |
| Estepa | bajo, sin cola alta | sin dosel |

**Cómo se verificó.** Es el control del proyecto. Si la estepa tuviera huellas de
25 m, o el bosque ninguna, habría un error en los AOI y todo lo que sigue sería
inválido. Se comprueba de un vistazo en QGIS cargando `gedi_aceptados_*` con su
estilo: el bosque tiene puntos verdes oscuros, la estepa no.

## 3. La verificación que hay que dejar puesta siempre

**Verifique que la variable exista ANTES de usarla.** La versión V003 renombró el
indicador de calidad: antes `quality_flag`, ahora `l2a_quality_flag_rel3`. Un
script que busca el nombre viejo NO da error: `h5py` devuelve `None`, el filtro no
filtra, y pasan los 6.288 disparos con una salida idéntica a una correcta. Por eso
el script 03 lista las claves del `.h5` y se detiene si falta alguna.

**Y deje puesto el control de la tasa de supervivencia.** Si da cerca del 100 %, el
filtro no está funcionando. En GEDI sobre bosque templado lo esperable es 10-15 %
(Adam et al., 2020; Moudrý et al., 2024). Ese umbral es la alarma: cuesta nada
programarlo y detecta el fallo silencioso antes de que contamine todo lo demás.

## 4. Lo que NO se pudo verificar, y hay que declararlo

- **No hay parcelas de campo.** GEDI es la referencia, pero GEDI también es una
  estimación. Todo el proyecto se apoya en una medición satelital sin validación
  terrestre. Es la limitación más seria y no tiene arreglo con los datos que hay.
- **GEDI no es contemporáneo.** Los datos son de sep. 2024 a mar. 2025; la línea
  de base es 2023-24. El instrumento estuvo hibernado entre medio. No es un
  descuido: no existen datos de ese período.
- **GEDI muestrea, no mapea.** Son líneas de disparos con huecos enormes. Alcanza
  para calibrar un modelo, no para cubrir el terreno.

## La regla que resume el práctico

A una respuesta de IA no se la audita releyéndola: se la audita buscando una
medida externa con la que tenga que coincidir. Acá fueron tres: la coincidencia
entre los dos sitios, la literatura, y el mapa en QGIS.
