# Análisis de la respuesta que dio la IA

Qué devolvió el modelo ante el prompt inicial, y por qué esa respuesta es correcta
como programación y equivocada como método.

---

## 1. Lo que la respuesta hizo bien

Conviene decirlo primero, porque importa para el argumento. El código estaba bien
escrito: leía las tablas, alineaba las variables sobre las huellas, separaba
entrenamiento de validación, ajustaba el modelo, evaluaba sobre datos que el ajuste
no había visto y escribía el mapa con su georreferenciación correcta. No hubo
alucinación de funciones, ni rutas inventadas, ni errores de unidades.

**El modelo hizo bien todo lo que se le pidió.** Ése es exactamente el problema.

## 2. Lo que la respuesta no podía hacer

Un modelo de lenguaje no sabe cuál de sus columnas es sospechosa. Le entregamos una
tabla con predictores ópticos, de radar y derivados de GEDI, y le pedimos que
estimara una variable que también viene de GEDI. Para el algoritmo son todas
columnas de números. Que una de ellas comparta origen con la variable a estimar es
un dato del **dominio**, no de la tabla, y el dominio lo pone quien pregunta.

Lo mismo con el resto:

| Lo que faltó | Por qué la IA no podía suplirlo |
|---|---|
| El modelo de control | Requiere saber qué variable comparte origen con la respuesta |
| La validación por franjas | Requiere saber que los extremos son lo que interesa |
| El ensayo nulo | Requiere saber que hay terreno no quemado que sirve de testigo |
| La cautela en el nombre | Requiere saber qué se puede afirmar y qué no |

Ninguna de las cuatro es una limitación técnica del modelo. Las cuatro son
conocimiento del problema.

## 3. La trampa específica de este práctico

En los otros cuatro prácticos, cuando el prompt estaba mal, algo se notaba: un
número imposible, un mapa con huecos, un script que se detenía. Aquí no. La
respuesta fue **plausible en todos sus tramos**: un coeficiente alto, un mapa
continuo y sin huecos, una cifra de pérdida del orden de magnitud esperado.

La única manera de detectarlo fue **agregar comprobaciones que el resultado tenía
que sobrevivir**. No revisar el código: someter el resultado a pruebas que un
resultado falso no pasa. Ésa es la diferencia entre auditar la herramienta y
auditar la conclusión.

## 4. Cómo se hizo evidente

Se ajustó el mismo modelo con distintos juegos de variables y se comparó el piso de
ruido que producía cada uno sobre terreno no quemado, donde el resultado correcto
es cero.

| Juego de predictores | Piso sobre terreno no quemado (Mg/ha) | Señal ÷ piso |
|---|---|---|
| Óptico (NDVI, EVI, NDMI, NBR) | −8,48 | 1,3 |
| Óptico + radar (los ocho) | −5,01 | 1,5 |
| Óptico sin EVI | −4,82 | 2,3 |
| **Óptico sin EVI + radar** | **−0,48** | **15,3** |

El resultado sorprendió: la primera sospecha había sido el radar, cuyas dos fechas
están separadas por siete semanas en las que la humedad del suelo pudo cambiar. Se
midió y era falso. **El piso lo aportaba un solo índice óptico.** Quitándolo, el
método pasa de distinguir la señal del ruido por un factor de 1,5 a distinguirla
por un factor de 15.

Ese resultado no salió de una intuición ni de leer el código: salió de medir. Y no
se habría medido nunca si el prompt no hubiera pedido el ensayo nulo.

## 5. Lo que hay que retener

La IA es una herramienta excelente para **ejecutar** un procedimiento y una
herramienta inútil para **decidir si el procedimiento responde la pregunta**. Esa
segunda parte no se delega. Se aprende.
