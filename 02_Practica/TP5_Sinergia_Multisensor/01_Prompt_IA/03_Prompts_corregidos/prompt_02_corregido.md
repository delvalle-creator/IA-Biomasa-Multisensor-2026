# Prompt corregido del TP5 — el que produjo los scripts del práctico

Éste es el prompt reescrito después de detectar los cuatro defectos del primero. Es
el que generó los cinco scripts de la cadena y el auxiliar de diagnóstico.

---

> Contexto: dos AOI de 15 × 15 km en el noroeste de Chubut, Argentina. Uno de
> bosque andino de *Nothofagus* (BOSQUE_NW_02) y uno de ecotono de estepa
> (ESTEPA_NW_02), que funciona como control. Grilla común EPSG:32719, píxel 10 m.
> El bosque se incendió entre el 10/01 y el 27/02 de 2026.
>
> Dispongo de tres grupos de predictores sobre las mismas huellas de GEDI: índices
> ópticos de Sentinel-2, retrodispersión de radar de Sentinel-1 (banda C) y SAOCOM
> (banda L), y métricas derivadas del propio GEDI. La variable a estimar —altura de
> dosel y biomasa aérea— **también proviene de GEDI**.
>
> Necesito cuantificar cuánto aporta realmente combinar sensores, y producir un
> mapa de biomasa con su incertidumbre.
>
> **Requisitos, no negociables:**
>
> 1. **Entrenar cinco modelos, no uno**: óptico solo, radar solo, óptico + radar,
>    los tres juntos, y **un control que use únicamente los predictores derivados
>    de GEDI**. Presentarlos en una sola tabla. Si el control iguala al modelo
>    completo, decirlo con todas las letras: la mejora no vino de la sinergia sino
>    de haber metido entre los predictores una variable que ya contiene la
>    respuesta.
> 2. **Evaluar siempre sobre datos que el ajuste no vio.** Informar el coeficiente
>    de entrenamiento y el de validación por separado, y también el error absoluto,
>    porque un coeficiente sin unidades no dice cuánto se equivoca el modelo.
> 3. **Validar por franja de altura y por sitio, no sólo en global.** Informar el
>    sesgo dentro de cada franja. Si aparece compresión hacia la media
>    —sobreestimar abajo y subestimar arriba—, cuantificarla y no disimularla.
> 4. **Ensayo nulo obligatorio.** Antes de informar cuánta biomasa cambió por el
>    incendio, aplicar exactamente el mismo procedimiento sobre la clase de
>    severidad «sin cambio», es decir sobre terreno que no se quemó. Ahí el
>    resultado debe ser cero. Lo que dé es el **piso de ruido del método completo**,
>    y ninguna cifra de cambio puede informarse sin ponerla al lado de ese piso.
> 5. **Si el piso resulta grande, no restarlo: averiguar de dónde sale.** Restar a
>    ciegas mejora la cifra central, que es justo la dirección conveniente, y eso
>    obliga a ser más exigente, no menos. Escribir un script auxiliar que ajuste el
>    mismo modelo con distintos juegos de predictores y compare el piso que produce
>    cada uno, hasta identificar la variable responsable.
> 6. **Propagar la incertidumbre por tramos y declararla:** la del modelo de
>    altura, la de la conversión de altura a biomasa y la del producto de biomasa
>    que sirvió de referencia. Informar las tres, no una suma opaca.
> 7. **Nombrar las cosas por lo que son.** No escribir «biomasa perdida» donde lo
>    que se mide es un cambio aparente de biomasa estimada entre dos fechas.
> 8. **Aplicar la máscara de validez geométrica** que produce el práctico de radar,
>    para que el mapa final no incluya píxeles en sombra ni en superposición. Si la
>    máscara no está, avisar por pantalla y continuar sin ella, dejando constancia.
> 9. Escribir el valor «sin dato» declarado en todos los rásters de salida, nunca
>    cero.
>
> Cada script debe imprimir qué leyó, cuántos registros entraron y salieron, y cuál
> es el paso siguiente.

---

## Qué cambió respecto del primero

| Prompt inicial | Prompt corregido |
|---|---|
| un modelo | cinco, incluido el control que revela la trampa |
| coeficiente global | coeficiente + error absoluto + sesgo por franja |
| cifra de pérdida directa | cifra de cambio **junto al piso de ruido** |
| "biomasa perdida" | "cambio aparente de biomasa estimada" |
| incertidumbre ausente | propagada y declarada por tramos |
| mapa completo | mapa con máscara de validez geométrica |

## La diferencia de fondo

El primer prompt pedía **un resultado**. El segundo pide **un resultado y las
pruebas que ese resultado tiene que sobrevivir**. La lista de esas pruebas —el
control, las franjas, el ensayo nulo— es el aporte del especialista, no del modelo.

Es el prompt más largo de los cinco prácticos, y no por casualidad: es el único
donde el error no se manifiesta como falla. Cuando nada avisa, las comprobaciones
hay que pedirlas de antemano.
