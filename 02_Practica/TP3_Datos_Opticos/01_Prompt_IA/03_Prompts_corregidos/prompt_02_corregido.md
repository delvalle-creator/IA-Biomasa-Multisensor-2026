# Prompt corregido — el que produjo los scripts del TP3

---

> Contexto: Sentinel-2 L2A y Landsat 9, dos AOI de 15 × 15 km en el noroeste de
> Chubut, grilla común EPSG:32719 a 10 m. El bosque se incendió entre el 10/01 y el
> 27/02 de 2026; la estepa es el control. Las huellas GEDI filtradas del TP2 son la
> referencia de altura.
>
> **Requisitos, no negociables:**
>
> 1. **No elija la escena por cercanía a la fecha: elíjala por calidad.** Antes de
>    usar ninguna, compare cada escena contra la mediana del propio sitio en la
>    banda azul y en el NDVI. Los aerosoles inflan el azul y dejan casi intacto el
>    infrarrojo. Use dos criterios: azul > 2,5× la mediana (bruma grosera), o
>    azul > 1,5× con el NDVI por debajo del 70 % de lo habitual (sospechosa). Un
>    umbral único falla: sobre la estepa, que es clara, la misma escena
>    contaminada sólo llega a 1,6×.
> 2. **No confíe en la máscara de nubes del producto.** La SCL está entrenada para
>    nubes opacas; la bruma es un velo semitransparente y la deja pasar.
> 3. Calcule NDVI, EVI, NDMI y NBR. **Para el fuego use NBR**, no NDVI: el NBR usa
>    NIR y SWIR2, que la bruma casi no toca.
> 4. Los umbrales de severidad son los de **Key y Benson (2006)**. Cítelos, y
>    declare que fueron calibrados en Norteamérica y no en un bosque de Nothofagus.
>    Saulino et al. (2020) muestran que aplicados sin recalibrar dan concordancia
>    baja.
> 5. **Mida dónde satura cada índice** cruzando con las huellas GEDI del TP2,
>    ventana de 3×3 píxeles (≈ el tamaño de la huella). Reporte R² y RMSE.
> 6. Los píxeles descartados van a **nodata**, nunca a cero: un cero entra en los
>    promedios y los falsea.
> 7. **Exporte a QGIS con estilos**: el ráster de severidad es categórico y sin
>    paleta se ve como seis grises iguales.
>
> Cada script debe imprimir qué escena usó, por qué, cuántos píxeles válidos tuvo
> y cuál es el siguiente paso.

---

## La diferencia

El primero pedía **un número**. Éste pide **un número, la escena de la que sale, el
umbral con su cita, y el límite del método**. Es más largo y más aburrido. Así son
los prompts que sirven.
