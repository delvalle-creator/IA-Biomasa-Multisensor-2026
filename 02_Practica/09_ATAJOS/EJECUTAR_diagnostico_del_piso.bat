@echo off
REM ===================================================================
REM  EJECUTAR_diagnostico_del_piso.bat
REM
REM  DOBLE CLIC. Corre un solo script y no toca ningun resultado del
REM  practico: solo diagnostica de donde sale el piso del ensayo nulo.
REM
REM  Ajusta el modelo de altura con tres juegos de variables -solo optico,
REM  solo radar, y los dos juntos- y compara el piso que produce cada uno.
REM  Si el piso se derrumba al quitar el radar, la causa son las fechas
REM  del radar: PRE 10/01/2026 contra POST 27/02/2026.
REM
REM  Tarda unos minutos: abre las escenas opticas y las de radar.
REM
REM  Registro en
REM     TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad\DIAGNOSTICO_DEL_PISO.log
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
echo     cd C:\Temp\CURSO_BIOMASA_2026\02_Practica\TP5_Sinergia_Multisensor\03_Scripts\03_Analisis\incendio
echo     python TP5_06_diagnostico_del_piso.py
echo.
echo     Es un auxiliar de diagnostico: no toca ningun resultado del practico.
echo.
echo  Si prefiere entender que pasa, cierre esta ventana y escribalo a
echo  mano. El atajo sirve para repetir, no para aprender.
echo ================================================================
echo.

set "REG=%RAIZ%TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad"
if not exist "%REG%" mkdir "%REG%"
set "LOG=%REG%\DIAGNOSTICO_DEL_PISO.log"

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
echo  Diagnostico del piso del ensayo nulo
echo ================================================================
cd /d "%RAIZ%TP5_Sinergia_Multisensor\03_Scripts\03_Analisis\incendio"
python TP5_06_diagnostico_del_piso.py > "%LOG%" 2>&1
set "SALIO=%errorlevel%"
type "%LOG%"
echo.
if "%SALIO%"=="0" (
  echo LISTO. Tabla en 05_Resultados\04_Tablas\TP5_diagnostico_del_piso.csv
) else (
  echo Termino con error. El detalle esta en el registro.
)
echo Registro completo: %LOG%
echo.
pause
