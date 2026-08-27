@echo off
REM ===================================================================
REM  EJECUTAR_TP2_rama_ICESat2.bat
REM
REM  DOBLE CLIC. Corre la rama ICESat-2 / ATL08 del TP2, completa:
REM     TP2_12_cargar_ATL08  ->  TP2_13_cotejar_GEDI_ICESat2
REM     ->  TP2_14_exportar_ICESat2_para_gis
REM     ->  TP2_15_control_terreno_FABDEM  ->  TP2_16_recotejar_tras_control
REM
REM  La rama es independiente de la cadena GEDI (pasos 1 a 11): no
REM  modifica ninguna salida de esa cadena y puede correrse o no sin
REM  afectarla. El 13 si necesita la salida del paso 6 de GEDI, que ya
REM  esta en el practico.
REM
REM  El 12 proyecta los segmentos ATL08 a la grilla comun y registra la
REM  retencion. El 13 compara rh98 de GEDI contra h_canopy de ATL08
REM  sobre celdas de 500 m. El 14 deja el GeoPackage del cotejo para QGIS.
REM
REM  Los pasos 12 a 14 corren con la biblioteca estandar de Python; el 15
REM  usa ademas rasterio y numpy, que ya estan en el entorno aoi. El 15
REM  audita el terreno de cada segmento contra FABDEM (con los geoides
REM  EGM2008 y Ar16) y el 16 repite el cotejo solo con los que pasan.
REM
REM  Registro en
REM     TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad\ICESat2_ATL08\CADENA_ICESAT2.log
REM ===================================================================

chcp 65001 >nul
set PYTHONIOENCODING=utf-8
setlocal
rem El atajo vive en 09_ATAJOS: la raiz del proyecto es la carpeta de arriba.
for %%I in ("%~dp0..") do set "RAIZ=%%~fI\"
REM  --- BLOQUE DE ORDENES EQUIVALENTES ---

echo.
echo ================================================================
echo  ESTE .bat EQUIVALE A ESCRIBIR, EN EL MINIFORGE PROMPT:
echo.
echo     conda activate aoi
echo     cd C:\Temp\CURSO_BIOMASA_2026\02_Practica\TP2_LiDAR_GEDI_ICESat2\03_Scripts
echo.
echo     cd 01_Pre_procesamiento\cargar_ICESat2
echo     python TP2_12_cargar_ATL08.py
echo     cd ..\..\02_Procesamiento\cotejo_ICESat2
echo     python TP2_13_cotejar_GEDI_ICESat2.py
echo     cd ..\..\05_Exportacion
echo     python TP2_14_exportar_ICESat2_para_gis.py
echo     cd ..\02_Procesamiento\control_terreno
echo     python TP2_15_control_terreno_FABDEM.py
echo     cd ..\cotejo_ICESat2
echo     python TP2_16_recotejar_tras_control.py
echo.
echo  Si prefiere entender que pasa, cierre esta ventana y escribalo a
echo  mano. El atajo sirve para repetir, no para aprender.
echo ================================================================
echo.

set "REG=%RAIZ%TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad\ICESat2_ATL08"
if not exist "%REG%" mkdir "%REG%"
set "LOG=%REG%\CADENA_ICESAT2.log"
break > "%LOG%"

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

python "%RAIZ%TP2_LiDAR_GEDI_ICESat2\03_Scripts\comprobar_entorno.py"
if errorlevel 1 ( echo. & echo No se ejecuto nada. & pause & exit /b 1 )

echo.
echo ================================================================
echo  Paso 12 de 16: cargar y proyectar ATL08
echo ================================================================
cd /d "%RAIZ%TP2_LiDAR_GEDI_ICESat2\03_Scripts\01_Pre_procesamiento\cargar_ICESat2"
python TP2_12_cargar_ATL08.py >> "%LOG%" 2>&1
if errorlevel 1 goto :fallo

echo.
echo ================================================================
echo  Paso 13 de 16: cotejar GEDI contra ICESat-2
echo ================================================================
cd /d "%RAIZ%TP2_LiDAR_GEDI_ICESat2\03_Scripts\02_Procesamiento\cotejo_ICESat2"
python TP2_13_cotejar_GEDI_ICESat2.py >> "%LOG%" 2>&1
if errorlevel 1 goto :fallo

echo.
echo ================================================================
echo  Paso 14 de 16: exportar el cotejo para QGIS
echo ================================================================
cd /d "%RAIZ%TP2_LiDAR_GEDI_ICESat2\03_Scripts\05_Exportacion"
python TP2_14_exportar_ICESat2_para_gis.py >> "%LOG%" 2>&1
if errorlevel 1 goto :fallo

echo.
echo ================================================================
echo  Paso 15 de 16: control de terreno contra FABDEM
echo ================================================================
cd /d "%RAIZ%TP2_LiDAR_GEDI_ICESat2\03_Scripts\02_Procesamiento\control_terreno"
python TP2_15_control_terreno_FABDEM.py >> "%LOG%" 2>&1
if errorlevel 1 goto :fallo

echo.
echo ================================================================
echo  Paso 16 de 16: re-cotejo con los segmentos que pasan
echo ================================================================
cd /d "%RAIZ%TP2_LiDAR_GEDI_ICESat2\03_Scripts\02_Procesamiento\cotejo_ICESat2"
python TP2_16_recotejar_tras_control.py >> "%LOG%" 2>&1
if errorlevel 1 goto :fallo

type "%LOG%"
echo.
echo LISTO. La rama ICESat-2 corrio completa, control de terreno incluido.
echo   Tablas del cotejo y del control en 05_Resultados\04_Tablas\
echo   GeoPackage en 05_Resultados\03_Vectores\TP2_ICESat2_cotejo.gpkg
echo Registro completo: %LOG%
echo.
pause
exit /b 0

:fallo
type "%LOG%"
echo.
echo Termino con error. El detalle esta en el registro: %LOG%
echo Los pasos siguientes NO se corrieron.
echo.
pause
exit /b 1
