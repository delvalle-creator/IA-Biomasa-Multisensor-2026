# TP5 — Orden de ejecución

El TP5 **no descarga ni pre-procesa nada**: consume lo que dejaron los cuatro
prácticos anteriores. Por eso sus cinco pasos se corren enteros, y por eso es el
que más rápido falla si alguno de los anteriores quedó a medias.

| Paso | Script | Subcarpeta | Qué hace | Deja / produce |
|---|---|---|---|---|
| 1 | `TP5_01_dataset.py` | `01_Pre_procesamiento/dataset` | Apila cada huella válida del TP2 con sus índices ópticos (TP3), su γ⁰ de banda C y de banda L (TP4) y su pendiente. **Hereda la partición del TP2**, no la rehace | `04_Tablas_de_trabajo/` |
| 2 | `TP5_02_modelos.py` | `02_Procesamiento/modelos` | Los **cinco** modelos: óptico; SAR; óptico+SAR; óptico+SAR+LiDAR; y **sólo LiDAR, que es el control** | `04_Tablas/TP5_modelos_altura.csv` y `TP5_modelos_biomasa.csv` |
| 3 | `TP5_03_validacion.py` | `04_Validacion` | Validación por sitio y **por franja de altura**, para exponer la compresión hacia la media | `TP5_validacion_franjas.csv`, `TP5_validacion_sitio.csv` |
| 4 | `TP5_04_biomasa_quemada.py` | `03_Analisis/incendio` | Cambio aparente de biomasa por clase de severidad, con su incertidumbre, **incluido el ensayo nulo sobre la clase «sin cambio»** | `TP5_biomasa_por_severidad.csv`, `TP5_cadena_de_error.csv` |
| 5 (último) | `TP5_05_mapas.py` | `05_Exportacion` | Mapas de biomasa, de cambio y de incertidumbre, con la máscara de validez geométrica del TP4 | `05_Resultados/02_Rasters/` |

**Auxiliar:** `TP5_06_diagnostico_del_piso.py`, en `03_Analisis/incendio`. Ajusta el
mismo modelo con distintos juegos de predictores y compara el piso de ruido que
produce cada uno. No toca ningún resultado del práctico.

## El control del paso 2 es lo que da sentido al práctico

Los predictores derivados de GEDI comparten origen con la variable que se estima.
Con ellos adentro el modelo completo llega a R² = 0,964 sobre validación; el modelo
que usa **sólo** LiDAR llega a 0,956. La distancia entre ambos —ocho milésimas— es
todo lo que aportaron el óptico y el radar. **Sin la fila de control, ese mismo
resultado se presenta como un éxito de la sinergia multisensor.**

## El ensayo nulo del paso 4 no es opcional

Sobre la clase «sin cambio» del bosque, es decir terreno que no se quemó, el
procedimiento mide −10,25 Mg/ha donde debería medir cero. Las clases quemadas
cambian entre 11,5 y 15,5. Ninguna cifra de cambio puede informarse sin ese piso al
lado. El auxiliar `TP5_06` identificó de dónde sale: no del radar, como se
sospechaba, sino de un solo índice óptico. Quitándolo, el piso cae a −0,48 y el
cociente entre señal y ruido sube de 1,5 a 15,3.

## El paso 5 depende del TP4

Aplica la máscara de validez geométrica que produce `TP4_05_mascara_validez.py`. Si
no está, el script avisa por pantalla y sigue sin ella; en ese caso el mapa
incluirá píxeles en sombra de radar, y hay que decirlo en el informe.

## Los atajos

`09_ATAJOS\EJECUTAR_cadena_escenarioB.bat` corre los cinco pasos junto con los del TP2.
`09_ATAJOS\EJECUTAR_TP5_desde_modelos.bat` corre del paso 2 al 5, que es lo que hace falta
cuando se cambió algo en los modelos.

## La limitación que condiciona todo, y hay que declararla

**No hay parcelas de campo.** GEDI es la referencia, pero GEDI también es una
estimación satelital. Cualquier modelo de este práctico está calibrado contra otra
estimación, no contra una medición terrestre. **Ninguna conclusión puede
presentarse como una medición de biomasa.**

## Paso 6: la validación estricta

    conda activate aoi
    cd C:\Temp\CURSO_BIOMASA_2026\02_Practica
    python TP5_Sinergia_Multisensor\03_Scripts\03_Analisis\TP5_06_validacion_estricta.py

Produce cuatro tablas en `05_Resultados\04_Tablas`: la validación cruzada
espacial anidada, el área de aplicabilidad, la propagación conjunta de la
incertidumbre y el ensayo nulo con su distribución. No modifica el mapa: acota
lo que puede afirmarse a partir de él. Tarda unos siete minutos.
