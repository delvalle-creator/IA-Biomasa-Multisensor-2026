# 10_Procedimientos_y_resultados — el registro de cómo se hizo cada cosa

Esta carpeta es el **control de procedimientos y resultados** del curso: un
subdirectorio por proceso, cada uno con su `PROCEDIMIENTO.md` (qué entró, qué
se hizo paso a paso con los parámetros usados en esa ejecución, qué salió y
cómo se controló) y una carpeta `capturas\` con las imágenes del proceso.
Los estudiantes pueden consultarla sin correr nada: es la memoria del curso.

El molde es la guía del ALOS PALSAR-1 SLC (la más laboriosa de todas): datos
de entrada y diagnóstico, flujo completo y orden de operadores, cada paso con
sus "Parámetros usados en esta ejecución", resultados con interpretación y
control de calidad al final. Todo procedimiento nuevo debería imitarla.

| Subcarpeta | Proceso | Fecha |
|---|---|---|
| `TP2_control_terreno_FABDEM\` | Auditoría del terreno de ATL08 y GEDI contra FABDEM + geoides (pasos 15 y 16 del TP2) | 26/08/2026 |
| `TP2_mapa_biomasa_GEDI_CCI\` | Mapa de biomasa GEDI a 500 m contra CCI 2024 (paso 17 del TP2) | 26/08/2026 |
| `Orange_flujos\` | Los flujos .ows de Orange Data Mining (TP2 y TP5), su validación y el arreglo del error de versiones | 26/08/2026 |
| `TP4_ALOS_PALSAR1_SLC\` | Procesamiento polarimétrico completo de una escena ALOS PALSAR-1 SLC en SNAP (imagen completa; **pendiente repetirlo por recinto/AOI** para reducir volumen) | 08/2026 |

Regla de la carpeta: acá no vive ningún dato de trabajo — solo `.md` y
capturas `.png`. La autoridad de cada número sigue siendo el script que lo
produjo y su log en `06_Control_calidad` del práctico correspondiente.
