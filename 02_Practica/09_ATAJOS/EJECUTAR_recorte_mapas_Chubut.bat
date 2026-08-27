@echo off
REM ===================================================================
REM  EJECUTAR_recorte_mapas_Chubut.bat
REM
REM  DOBLE CLIC. Recorta a los dos recintos las TRES capas pesadas del
REM  producto "Manejo Sostenible de los Bosques de Argentina" que no se
REM  pudieron evaluar por su tamano (unos 1,5 GB cada una):
REM
REM     3_Spatial_VegGreenness_Chubut.TIF     verdor espacial, 30 m
REM     4_Spatial_LSTSummer_Chubut.TIF        LST de verano, 30 m
REM     5_Spatial_LSTWinter_Chubut.TIF        LST de invierno, 30 m
REM
REM  SEIS SALIDAS (3 capas x 2 recintos), de unos pocos MB cada una, en
REM     TP3_Datos_Opticos\02_Subsets_SNAP_QGIS\Mapas_forestales_Chubut\
REM
REM  DECISION IMPORTANTE: NO SE REPROYECTA.
REM  El recorte sale en las coordenadas originales del producto, WGS 84
REM  geograficas (EPSG:4326). El motivo es que primero hay que SABER que
REM  contiene cada capa -si son grados, indices o clases- y recien despues
REM  decidir el remuestreo. Reproyectar ahora, sin saberlo, obligaria a
REM  elegir a ciegas entre bilineal y vecino mas proximo, y para una capa
REM  de clases el bilineal inventa valores en silencio. La reproyeccion a
REM  EPSG:32719 es un paso posterior y aparte.
REM
REM  Se recorta con 0,02 grados de margen, el mismo criterio que usan los
REM  grafos del SAOCOM, para que el borde del recinto no quede pegado al
REM  borde del archivo.
REM
REM  SIN REDIRECCION de la salida, por el mismo motivo explicado en
REM  EJECUTAR_consulta_BIOMASS.bat: la ventana se veria muda.
REM
REM  SI LA UNIDAD G: NO ESTA CONECTADA, el .bat lo dice y no hace nada.
REM ===================================================================

chcp 65001 >nul
setlocal enabledelayedexpansion
rem El atajo vive en 09_ATAJOS: la raiz del proyecto es la carpeta de arriba.
for %%I in ("%~dp0..") do set "RAIZ=%%~fI\"
REM  --- BLOQUE DE ORDENES EQUIVALENTES ---

echo.
echo ================================================================
echo  ESTE .bat EQUIVALE A ESCRIBIR, EN EL MINIFORGE PROMPT:
echo.
echo     conda activate aoi
echo.
echo     y despues, una vez por cada capa y cada recinto, seis en total:
echo.
echo     gdal_translate -projwin -71.6178 -42.5362 -71.3895 -42.7153 ^^
echo       ORIGEN\3_Spatial_VegGreenness_Chubut.TIF ^^
echo       DESTINO\3_Spatial_VegGreenness_BOSQUE_NW_02.tif
echo.
echo     El ORIGEN es la carpeta Chubut del disco del producto forestal; el
echo     DESTINO es TP3_Datos_Opticos\02_Subsets_SNAP_QGIS\Mapas_forestales_Chubut.
echo     Las otras cinco ordenes son iguales, cambiando la capa y el recinto.
echo.
echo  Si prefiere entender que pasa, cierre esta ventana y escribalo a
echo  mano. El atajo sirve para repetir, no para aprender.
echo ================================================================
echo.


REM -------------------------------------------------------------------
REM  CARPETA DE ORIGEN: SE BUSCA SOLA, Y ES A PROPOSITO
REM
REM  El nombre real de la carpeta lleva una comilla tipografica en
REM  ARGENTINA?S, que no es la comilla del teclado sino el caracter
REM  Unicode U+2019. Escrita dentro de un .bat, esa comilla depende de la
REM  pagina de codigos con que cmd lea el archivo, y si no coincide la
REM  ruta NO se encuentra, con un mensaje que hace pensar que falta el
REM  disco. Por eso aqui no se escribe: se busca con comodin, que evita
REM  el problema de raiz.
REM
REM  Si su unidad no es G:, agregue la letra a la lista de abajo.
REM -------------------------------------------------------------------
set "ORIG="
for %%U in (G H I J F E D) do (
  if not defined ORIG (
    for /d %%P in ("%%U:\MAP_PRODUCTS_SUSTAINABLE_MANAGEMENT_*") do (
      if exist "%%~fP\04 By Forest Regions\Chubut\Chubut\3_Spatial_VegGreenness_Chubut.TIF" (
        set "ORIG=%%~fP\04 By Forest Regions\Chubut\Chubut"
      )
    )
  )
)

set "DEST=%RAIZ%TP3_Datos_Opticos\02_Subsets_SNAP_QGIS\Mapas_forestales_Chubut"

set "CONDA="
for %%D in (
  "%USERPROFILE%\miniforge3" "%USERPROFILE%\miniconda3" "%USERPROFILE%\anaconda3"
  "%USERPROFILE%\mambaforge" "%LOCALAPPDATA%\miniforge3" "%LOCALAPPDATA%\miniconda3"
  "%PROGRAMDATA%\miniforge3" "%PROGRAMDATA%\Miniconda3" "%PROGRAMDATA%\Anaconda3"
  "C:\miniforge3" "C:\miniconda3"
) do if exist "%%~D\Scripts\activate.bat" set "CONDA=%%~D"
if "%CONDA%"=="" ( echo No encontre conda. & pause & exit /b 1 )
call "%CONDA%\Scripts\activate.bat" aoi
if errorlevel 1 ( echo No se pudo activar el entorno "aoi". & pause & exit /b 1 )

where gdal_translate >nul 2>&1
if errorlevel 1 ( echo Falta gdal_translate en el entorno "aoi". & pause & exit /b 1 )

if not defined ORIG (
  echo.
  echo No encontre la carpeta MAP_PRODUCTS_SUSTAINABLE_MANAGEMENT_... en
  echo ninguna de las unidades G H I J F E D.
  echo.
  echo Conecte el disco, o agregue la letra de su unidad a la lista
  echo   for %%%%U in ^(G H I J F E D^)
  echo que esta unas lineas mas arriba en este mismo archivo.
  echo.
  pause & exit /b 1
)
echo Origen encontrado:
echo    %ORIG%

if not exist "%DEST%" mkdir "%DEST%"

echo.
echo ================================================================
echo  RECORTE DE LAS TRES CAPAS PESADAS A LOS DOS RECINTOS
echo  Salida: %DEST%
echo  Sin reproyectar: quedan en EPSG:4326, como el original.
echo ================================================================
echo.

REM  -projwin va en el orden  ulx uly lrx lry, es decir
REM  lon minima, lat MAXIMA, lon maxima, lat MINIMA. Con 0,02 de margen.
REM  BOSQUE_NW_02  lon -71,5978 a -71,4095   lat -42,6953 a -42,5562
REM  ESTEPA_NW_02  lon -71,2138 a -71,0258   lat -42,8468 a -42,7084

for %%C in (3_Spatial_VegGreenness 4_Spatial_LSTSummer 5_Spatial_LSTWinter) do (

  echo ---- %%C ----

  echo    BOSQUE_NW_02 ...
  gdal_translate -q -projwin -71.6178 -42.5362 -71.3895 -42.7153 ^
    -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TILED=YES ^
    "%ORIG%\%%C_Chubut.TIF" "%DEST%\%%C_BOSQUE_NW_02.tif"
  if errorlevel 1 (echo    ERROR en BOSQUE) else (echo    hecho)

  echo    ESTEPA_NW_02 ...
  gdal_translate -q -projwin -71.2338 -42.6884 -71.0058 -42.8668 ^
    -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TILED=YES ^
    "%ORIG%\%%C_Chubut.TIF" "%DEST%\%%C_ESTEPA_NW_02.tif"
  if errorlevel 1 (echo    ERROR en ESTEPA) else (echo    hecho)
  echo.
)

echo ================================================================
echo  FICHA DE CADA RECORTE (tamano, tipo de dato y estadisticas)
echo  Esto es lo que hace falta para saber que contiene cada capa.
echo ================================================================
echo.
for %%F in ("%DEST%\*.tif") do (
  echo ---------------------------------------------------------------
  echo %%~nxF   ^(%%~zF bytes^)
  gdalinfo -stats -norat -noct "%%~fF" | findstr /C:"Size is" /C:"Type=" /C:"NoData" /C:"Minimum=" /C:"STATISTICS_MEAN" /C:"STATISTICS_STDDEV" /C:"Band "
  echo.
)

echo ================================================================
echo  LISTO. Quedaron en:
echo     %DEST%
echo  Avise cuando termine y las reviso.
echo ================================================================
echo.
pause
endlocal
