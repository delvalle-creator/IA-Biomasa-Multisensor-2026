# TP5 — El flujo de Orange Data Mining, con sus resultados

El flujo está en `TP5_Sinergia_Multisensor\09_Orange\
TP5_flujo_sinergia_multisensor.ows` (Orange 3.39 o 3.40; variables
preseleccionadas, rutas relativas — el `.ows` debe quedarse en su carpeta).
Carga el dataset multisensor del paso 1 (`TP5_dataset_<AOI>.csv`), une los
dos recintos con **Concatenate** (`recinto` como clase) y analiza. La figura
está en `capturas\Orange_TP5_sinergia.png`.

De las huellas del dataset, tienen biomasa L4A **495 en el bosque y 1.129
en la estepa** — sobre ellas trabajan los widgets.

- **Correlations** (contra `agbd_Mg_ha`, Spearman, los dos recintos
  juntos): el ranking cuenta la historia del curso en una tabla.
  Arriba, lejos, las variables de estructura del propio GEDI
  (`rh95` +0,83, `fhd_normal` +0,69, `pai` y `cover` +0,64) — el
  «parentesco» que obliga al modelo de control del paso 2. Después, **la
  banda L** (NISAR HH +0,49, PALSAR-2 HH +0,48, PALSAR-2 HV +0,47,
  NISAR HV +0,46, SAOCOM HV +0,46), apenas por encima de **los índices
  ópticos** (NDMI +0,45, NBR +0,45, NDVI +0,41) y de **la banda C**
  (VV +0,42, VH +0,39). Ningún sensor individual pasa de ~0,5: por eso
  se fusiona.
- **Scatter Plot** (`NDVI` contra `agbd_Mg_ha`): la saturación del TP3
  vista desde la biomasa — a NDVI ≈ 0,8–0,9 el bosque forma una **pared
  vertical**: el mismo índice para 20 y para 200 Mg/ha.
- **Scatter Plot** (`g0_L_PALSAR2_HV` contra `agbd_Mg_ha`): la banda L
  sigue distinguiendo dentro del bosque donde el óptico ya saturó, con la
  dispersión del moteado a la vista (TP4, § 2.1).
- **Feature Statistics**: la ficha del dataset completo — 31 columnas por
  huella: identidad y partición, estructura GEDI, biomasa con su error,
  los cuatro índices ópticos y los ocho canales de γ⁰.

Estas mismas relaciones, cuantificadas como modelos con validación, son la
tabla de los cinco modelos del paso 2 (véase el `DESARROLLO.md`, § 2.1): la
tabla de Correlations es su antesala visual.
