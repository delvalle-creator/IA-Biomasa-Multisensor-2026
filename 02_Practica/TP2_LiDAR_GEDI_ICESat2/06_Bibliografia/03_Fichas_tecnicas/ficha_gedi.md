# Ficha técnica — GEDI

| | |
|---|---|
| **Instrumento** | LiDAR de forma de onda completa (full-waveform) |
| **Plataforma** | Estación Espacial Internacional |
| **Cobertura** | 51,6° N a 51,6° S (la órbita de la ISS). Chubut queda dentro. |
| **Huella** | círculo de ~25 m de diámetro |
| **Separación** | ~60 m entre disparos a lo largo de la órbita; ~600 m entre pistas |
| **Muestreo** | **NO es un mapa**: son líneas de disparos con huecos enormes |
| **Longitud de onda** | 1064 nm (infrarrojo cercano) |
| **Operativo desde** | diciembre de 2018 |
| **Hibernación** | **marzo 2023 – abril 2024**: no hay datos de ese período |

## Variables que usa este práctico

| Variable | Producto | Qué es |
|---|---|---|
| `rh95` | L2A | percentil 95 de la energía devuelta. Se usa como altura del dosel. **No es "la altura": es un percentil.** |
| `rh98` | L2A | percentil 98. Más sensible a ramas aisladas. |
| `l2a_quality_flag_rel3` | L2A | calidad de la forma de onda. **En V003 se llama así; antes era `quality_flag`.** |
| `degrade_flag` | L2A | puntería u órbita anómalas |
| `sensitivity` | L2A | si el láser tuvo energía para llegar al suelo |
| `cover` | L2B | fracción de suelo cubierta por dosel |
| `pai` | L2B | índice de área foliar de la columna |
| `agbd` | L4A | biomasa aérea, Mg/ha, con su error estándar |

## Las tres limitaciones que hay que declarar siempre

1. **Muestrea, no mapea.** Alcanza para calibrar, no para cubrir.
2. **La pendiente lo arruina.** En una huella de 25 m sobre 30° de ladera hay
   14 m de desnivel. El instrumento no distingue montaña de árbol.
3. **Hibernó.** Marzo 2023 a abril 2024 no existe.

## Cifras de este proyecto

| Sitio | En el AOI | Válidos | Sobrevive |
|---|---|---|---|
| Bosque | 6.288 | 690 | 11,0 % |
| Estepa | 11.222 | 3.084 | 27,5 % |
