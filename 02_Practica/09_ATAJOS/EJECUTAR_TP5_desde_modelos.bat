@echo off
REM ===================================================================
REM  EJECUTAR_TP5_desde_modelos.bat
REM
REM  DOBLE CLIC. Corre solo los cuatro ultimos pasos de la cadena:
REM     TP5_02_modelos  ->  TP5_03_validacion  ->  TP5_04_biomasa_quemada
REM     ->  TP5_05_mapas
REM
REM  Hace falta porque los tres primeros de esos cuatro estaban leyendo dos
REM  veces cada huella: al buscar los datasets por prefijo capturaban tambien
REM  los archivos *_cobertura.csv. Los n informados salian al doble y las
REM  incertidumbres divididas por raiz de 2. Corregido el 31/07/2026.
REM
REM  Los pasos 1 a 6 NO hace falta rehacerlos: leen los archivos por su
REM  nombre exacto y sus salidas son correctas.
REM
REM  Registro en
REM     TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad\CADENA_TP5_FINAL.log
REM ===================================================================

chcp 65001 >nul
set PYTHONIOENCODING=utf-8
setlocal enabledelayedexpansion
rem El atajo vive en 09_ATAJOS: la raiz del proyecto es la carpeta de arriba.
for %%I in ("%~dp0..") do set "RAIZ=%%~fI\"
REM  --- BLOQUE DE ORDENES EQUIVALENTES ---

echo.
echo ================================================================
echo  ESTE .bat EQUIVALE A ESCRIBIR, EN EL MINIFORGE PROMPT:
echo.
echo     conda activate aoi
echo     cd C:\Temp\CURSO_BIOMASA_2026\02_Practica\TP5_Sinergia_Multisensor\03_Scripts
echo.
echo     cd 02_Procesamiento\modelos
echo     python TP5_02_modelos.py
echo     cd ..\..\04_Validacion
echo     python TP5_03_validacion.py
echo     cd ..\03_Analisis\incendio
echo     python TP5_04_biomasa_quemada.py
echo     cd ..\..\05_Exportacion
echo     python TP5_05_mapas.py
echo.
echo  Si prefiere entender que pasa, cierre esta ventana y escribalo a
echo  mano. El atajo sirve para repetir, no para aprender.
echo ================================================================
echo.

set "REG=%RAIZ%TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad"
if not exist "%REG%" mkdir "%REG%"
set "LOG=%REG%\CADENA_TP5_FINAL.log"
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
if errorlevel 1 ( echo. & echo No se ejecuto ningun paso. & pause & exit /b 1 )

set "N=0"
call :correr "TP5_Sinergia_Multisensor\03_Scripts\02_Procesamiento\modelos" TP5_02_modelos.py
call :correr "TP5_Sinergia_Multisensor\03_Scripts\04_Validacion"            TP5_03_validacion.py
call :correr "TP5_Sinergia_Multisensor\03_Scripts\03_Analisis\incendio"     TP5_04_biomasa_quemada.py
call :correr "TP5_Sinergia_Multisensor\03_Scripts\05_Exportacion"           TP5_05_mapas.py

echo.
echo ================================================================
echo  LISTO. Los cuatro pasos terminaron bien.
echo  Registro: %LOG%
echo ================================================================
pause
exit /b 0

:correr
set /a N+=1
echo.
echo ================================================================
echo  PASO !N! de 4 - %~2
echo ================================================================
cd /d "%RAIZ%%~1"
echo. >> "%LOG%"
echo ############ PASO !N! - %~2 >> "%LOG%"
python "%~2" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo.
  echo EL PASO !N! FALLO: %~2
  powershell -NoProfile -Command "Get-Content -Tail 25 \"%LOG%\""
  echo.
  pause
  exit
)
echo    ok
exit /b 0
