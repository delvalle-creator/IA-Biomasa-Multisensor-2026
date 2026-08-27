# Resúmenes de ICESat-2 / ATL08

Doce tablas derivadas de los CSV de `02_Subsets_SNAP_QGIS/ICESat2_ATL08/`. Vienen
con el paquete y **ya fueron auditadas contra los CSV de origen**; el registro de
esa auditoría está en `../../06_Control_calidad/ICESat2_ATL08/`.

| Tabla | Qué contesta | Filas |
|---|---|---|
| `01_resumen_calidad.csv` | Cuánto sobrevive a cada filtro, por recinto | 2 |
| `02_estadisticos_altura.csv` | Distribución de `h_canopy_m` en los cuatro niveles | 8 |
| `03_comparacion_bosque_estepa.csv` | **La comparación central**: bosque contra estepa, por segmento y por gránulo | 2 |
| `04_cobertura_estadisticos.csv` | Altura por clase de cobertura del suelo | 33 |
| `05_haces_estadisticos.csv` | Altura por haz. Sirve para ver si un haz débil sesga | 12 |
| `06_dia_noche_estadisticos.csv` | Altura de día y de noche | 4 |
| `07_anios_estadisticos.csv` | Altura año por año, 2018 a 2026 | 17 |
| `08_estaciones_estadisticos.csv` | Altura por estación del año | 8 |
| `09_granulos_medianas.csv` | Mediana de cada gránulo. **Es la unidad de inferencia del práctico** | 46 |
| `10_correlaciones.csv` | Spearman de la altura contra terreno, fotones e incertidumbres | 10 |
| `11_faltantes.csv` | Qué campo falta y en qué proporción | 22 |
| `12_valores_extremos.csv` | Los segmentos por encima del umbral de 3 IQR, uno por uno | 60 |

`ATL08_BOSQUE_ESTEPA_analisis.xlsx` es el libro del análisis anterior. Se conserva
como referencia; **no es la autoridad de ninguna conclusión**, que salen de los
CSV.

## Las tres cifras que hay que mirar primero

**Retención.** De 17.694 segmentos brutos en el bosque quedan 1.949 operacionales:
el **11,0 %**. En la estepa, 1.923 de 19.912: el **9,7 %**. Nueve de cada diez
segmentos se descartan, y conviene saber por qué antes de creerle al décimo.

**La diferencia entre recintos, con filtro operacional.** Mediana por gránulo:
bosque 14,86 m, estepa 11,11 m. Diferencia **3,75 m**, IC95 de 2,58 a 6,07 m,
Cliff delta 0,68, p = 0,0001. El bosque es más alto, y la diferencia se sostiene.

**La misma diferencia, con filtro conservador.** Bosque 10,78 m, estepa 10,29 m.
Diferencia **0,49 m**, IC95 de −1,58 a 3,14 m, p = 0,23. Desaparece.

No es que un filtro esté bien y el otro mal: es que el conservador selecciona
segmentos distintos. Ese es el asunto del práctico.
