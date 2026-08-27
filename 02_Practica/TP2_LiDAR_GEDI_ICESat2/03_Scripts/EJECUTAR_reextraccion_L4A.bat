@echo off
REM ===================================================================
REM  EJECUTAR_reextraccion_L4A.bat
REM
REM  Se hace DOBLE CLIC sobre este archivo. No hay que escribir nada.
REM
REM  Hace dos cosas, en este orden:
REM     1) TP2_01c_reextraer_l4a.py   vuelve a leer los granulos .h5 que YA
REM        estan en 00_COMUN\08_Originales_crudos\02_pre\GEDI_L4A y reescribe el CSV con
REM        los 20 campos. NO se conecta a internet y NO descarga nada.
REM     2) TP2_10_auditoria_L4A.py    vuelve a auditar el rechazo del L4A
REM        con las banderas nuevas.
REM
REM  Todo lo que aparece en pantalla queda ademas guardado en
REM     TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad\ULTIMA_EJECUCION.log
REM ===================================================================

chcp 65001 >nul
set PYTHONIOENCODING=utf-8
setlocal enabledelayedexpansion

set "AQUI=%~dp0"
set "REG=%AQUI%..\05_Resultados\06_Control_calidad"
if not exist "%REG%" mkdir "%REG%"
set "LOG=%REG%\ULTIMA_EJECUCION.log"

REM --- buscar donde esta instalado conda -----------------------------
set "CONDA="
for %%D in (
  "%USERPROFILE%\miniforge3"
  "%USERPROFILE%\miniconda3"
  "%USERPROFILE%\anaconda3"
  "%USERPROFILE%\mambaforge"
  "%LOCALAPPDATA%\miniforge3"
  "%LOCALAPPDATA%\miniconda3"
  "%PROGRAMDATA%\miniforge3"
  "%PROGRAMDATA%\Miniconda3"
  "%PROGRAMDATA%\Anaconda3"
  "C:\miniforge3"
  "C:\miniconda3"
) do (
  if exist "%%~D\Scripts\activate.bat" set "CONDA=%%~D"
)

if "%CONDA%"=="" (
  echo.
  echo No encontre la instalacion de conda en los lugares habituales.
  echo Abra el "Miniforge Prompt" desde el menu Inicio y escriba alli:
  echo.
  echo     conda activate aoi
  echo     cd /d "%AQUI%01_Pre_procesamiento\recortar_AOI"
  echo     python TP2_01c_reextraer_l4a.py
  echo.
  pause
  exit /b 1
)

echo Usando conda de: %CONDA%
call "%CONDA%\Scripts\activate.bat" aoi
if errorlevel 1 (
  echo.
  echo No se pudo activar el entorno "aoi".
  echo Para crearlo, en el Miniforge Prompt:
  echo     conda env create -f "%AQUI%configuracion\entorno_aoi.yml"
  echo.
  pause
  exit /b 1
)

cd /d "%AQUI%01_Pre_procesamiento\recortar_AOI"
echo.
echo ================================================================
echo  PASO 1 de 2 - releyendo los granulos .h5 que ya estan en disco
echo ================================================================
python TP2_01c_reextraer_l4a.py > "%LOG%" 2>&1
set "SALIO=%errorlevel%"
type "%LOG%"
if not "%SALIO%"=="0" (
  echo.
  echo El paso 1 termino con error. El detalle quedo en:
  echo    %LOG%
  pause
  exit /b 1
)

cd /d "%AQUI%02_Procesamiento\auditoria_L4A"
echo.
echo ================================================================
echo  PASO 2 de 2 - auditando el rechazo del L4A
echo ================================================================
python TP2_10_auditoria_L4A.py >> "%LOG%" 2>&1
set "SALIO=%errorlevel%"
type "%LOG%"

echo.
if "%SALIO%"=="0" (
  echo LISTO. Las tablas quedaron en 05_Resultados\06_Control_calidad\
) else (
  echo El paso 2 termino con error. El detalle esta en el log.
)
echo El registro completo quedo en:
echo    %LOG%
echo.
pause
