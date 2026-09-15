# Verificación de los resultados del TP3

## 1. La escena pre-incendio: por qué NO se usa la más cercana al fuego

| Escena pre | NBR pre | Píxeles válidos | Superficie quemada |
|---|---|---|---|
| 09/01/2026 (con humo del incendio) | 0,528 | 92,3 % | 16.463,1 ha (79,3 %) |
| **25/11/2025 (limpia)** | 0,512 | **99,8 %** | **18.009,2 ha (80,2 %)** |

La diferencia es menor a un punto porcentual, y la razón es instructiva: el NBR usa
NIR y SWIR2, las bandas que la bruma casi no toca. **Pero eso no se sabe de
antemano.** Con NDVI el resultado habría sido inservible. Una escena no está mala
en abstracto: está mala **para un índice determinado**.

Usar la limpia además sube los píxeles válidos del 92,3 % al 99,8 %.

## 2. El control: la estepa

| Severidad | Bosque | Estepa |
|---|---|---|
| Alta | 9.668,7 ha (43,1 %) | 0,1 ha |
| **TOTAL QUEMADO** | **18.009,2 ha (80,2 %)** | **413,5 ha (1,8 %)** |

El NBR del bosque pasa de 0,512 a −0,200: **cambia de signo**. Es la firma
inequívoca de vegetación viva reemplazada por ceniza. La estepa queda con el 96,5 %
sin cambio.

**Lo que falta verificar, y es tarea del alumno:** ese 1,8 % de la estepa, ¿es fuego
que cruzó, o es el pastizal secándose entre noviembre y marzo, como todos los años?
El dNBR no distingue. Compare contra la línea de base 2023-24, que cubre el mismo
par de estaciones sin incendio. Si allí también aparece ~2 %, es estacionalidad.

## 3. La saturación, medida contra GEDI

| Índice | R² contra rh95 | RMSE |
|---|---|---|
| NDVI | 0,235 | 6,17 m |
| EVI | 0,215 | 6,25 m |
| NBR | 0,291 | 5,94 m |
| **NDMI** | **0,310** | **5,86 m** |

El NDVI sube con la altura hasta la franja de 15–18 m (mediana 0,888) y después se
aplana: 0,879, 0,897 y 0,893 hasta los 30 m. **Ahí satura**. El EVI, que según Huete
et al. (2002) debería aguantar más, en estos datos también se aplana (0,549 y 0,550).

**Ningún índice explica más de un tercio de la altura** (el mejor, el NDMI, el 31 %). Ése es el techo del método
óptico, y no se arregla con otro modelo: la luz no atraviesa el dosel.

## 4. Las salvedades que hay que declarar

- **Los umbrales de severidad son importados.** Key y Benson (2006) los calibró en
  Norteamérica. Saulino et al. (2020) mostraron que aplicados sin recalibrar en
  bosque mediterráneo dan concordancia muy baja. Las **hectáreas totales son
  firmes** (el cambio de signo del NBR es enorme); **el reparto por clases, menos**.
- **El bosque es mayormente bajo**: la mitad de las huellas no llega a 9 m. En ese
  rango el óptico todavía no satura, así que el experimento está sesgado a favor
  del óptico y en contra del radar del TP4.

## La regla que resume el práctico

**Prevenga en el prompt, no corrija en el resultado.** Pida que la escena se elija
por calidad y no por fecha; pida el índice adecuado al fenómeno; pida el umbral con
su cita. Las tres cosas se piden en dos líneas y evitan un resultado falso que
igual se ve bien.
