# ICESat-2 / ATL08 — documentación de referencia

Producto usado en el práctico: **ATL08 versión 007**, *Land and Vegetation
Height*, distribuido por el NSIDC.

| Documento | Para qué se consulta | Enlace |
|---|---|---|
| Guía de usuario ATL08 V007 | Qué mide cada variable y cómo se construye el segmento | https://nsidc.org/sites/default/files/documents/user-guide/atl08-v007-userguide.pdf |
| Diccionario de datos ATL08 V007 | El nombre exacto y la unidad de cada campo | https://nsidc.org/sites/default/files/documents/technical-reference/icesat2_atl08_data_dict_v007.pdf |
| Errores conocidos ATL08 V007 | Antes de explicar una anomalía, mirar si ya está documentada | https://nsidc.org/sites/default/files/documents/technical-reference/icesat2_atl08_known_issues_v007.pdf |

## Dos definiciones que conviene tener a mano

- **`h_canopy`** es la altura relativa del dosel al **percentil 98** sobre la
  superficie de terreno estimada. Equivale al RH98 de la literatura.
- **`h_max_canopy`** es la altura relativa máxima y equivale al **RH100**.

Confundirlas cambia las cifras sin que nada falle.

## Cómo citar el producto

Neuenschwander, A. L., Pitts, K. L., Jelley, B. P., Robbins, J., Markel, J.,
Popescu, S. C., Nelson, R. F., Harding, D., Pederson, D., Klotz, B., & Sheridan, R.
(2025). *ATLAS/ICESat-2 L3A Land and Vegetation Height* (ATL08, versión 7)
[Conjunto de datos]. Boulder, Colorado, EE. UU.: NASA National Snow and Ice Data
Center Distributed Active Archive Center. https://doi.org/10.5067/ATLAS/ATL08.007

*(Cita verificada el 21/08/2026 contra https://nsidc.org/data/atl08/versions/7)*
