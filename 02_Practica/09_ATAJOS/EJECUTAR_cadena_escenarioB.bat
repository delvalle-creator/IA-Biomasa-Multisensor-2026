@echo off
REM ===================================================================
REM  EJECUTAR_cadena_escenarioB.bat
REM
REM  DOBLE CLIC. No hay que escribir nada.
REM
REM  Vuelve a correr toda la cadena que depende de la biomasa, ahora con
REM  el criterio nuevo: se aceptan tambien las huellas GEDI tomadas con el
REM  dosel sin hojas, marcadas en la columna agbd_origen.
REM
REM  ANTES de tocar nada comprueba que el entorno tenga todos los paquetes.
REM  Si falta alguno lo dice y se detiene, sin dejar el trabajo a medias.
REM
REM  Registro completo en
REM     TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad\CADENA_ESCENARIO_B.log
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
echo     cd C:\Temp\CURSO_BIOMASA_2026
echo.
echo     cd TP2_LiDAR_GEDI_ICESat2\03_Scripts\02_Procesamiento\biomasa_GEDI
echo     python TP2_07_biomasa_referencia.py
echo     cd ..\..\05_Exportacion
echo     python TP2_08_exportar_para_gis.py
echo     cd ..\..\..\TP5_Sinergia_Multisensor\03_Scripts\01_Pre_procesamiento\dataset
echo     python TP5_01_dataset.py
echo     ...y asi con los siete pasos restantes, en este orden:
echo     TP2_09_cobertura_BAP.py    TP2_10_auditoria_L4A.py
echo     TP2_11_escenarios_hoja_caida.py   TP5_02_modelos.py
echo     TP5_03_validacion.py   TP5_04_biomasa_quemada.py   TP5_05_mapas.py
echo.
echo     La ruta completa de cada uno esta en la tabla 3 del instructivo.
echo.
echo  Si prefiere entender que pasa, cierre esta ventana y escribalo a
echo  mano. El atajo sirve para repetir, no para aprender.
echo ================================================================
echo.

set "REG=%RAIZ%TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad"
if not exist "%REG%" mkdir "%REG%"
set "LOG=%REG%\CADENA_ESCENARIO_B.log"
break > "%LOG%"

set "CONDA="
for %%D in (
  "%USERPROFILE%\miniforge3" "%USERPROFILE%\miniconda3" "%USERPROFILE%\anaconda3"
  "%USERPROFILE%\mambaforge" "%LOCALAPPDATA%\miniforge3" "%LOCALAPPDATA%\miniconda3"
  "%PROGRAMDATA%\miniforge3" "%PROGRAMDATA%\Miniconda3" "%PROGRAMDATA%\Anaconda3"
  "C:\miniforge3" "C:\miniconda3"
) do if exist "%%~D\Scripts\activate.bat" set "CONDA=%%~D"
if "%CONDA%"=="" (
  echo No encontre conda. Abra el Miniforge Prompt y escriba: conda activate aoi
  pause & exit /b 1
)
call "%CONDA%\Scripts\activate.bat" aoi
if errorlevel 1 ( echo No se pudo activar el entorno "aoi". & pause & exit /b 1 )

echo.
echo ================================================================
echo  PASO 0 de 10 - comprobando el entorno
echo ================================================================
python "%RAIZ%TP2_LiDAR_GEDI_ICESat2\03_Scripts\comprobar_entorno.py"
if errorlevel 1 (
  echo.
  echo No se ejecuto ningun paso. Instale lo que falta y vuelva a hacer doble clic.
  pause
  exit /b 1
)

set "N=0"
call :correr "TP2_LiDAR_GEDI_ICESat2\03_Scripts\02_Procesamiento\biomasa_GEDI"        TP2_07_biomasa_referencia.py
call :correr "TP2_LiDAR_GEDI_ICESat2\03_Scripts\05_Exportacion"                       TP2_08_exportar_para_gis.py
call :correr "TP5_Sinergia_Multisensor\03_Scripts\01_Pre_procesamiento\dataset" TP5_01_dataset.py
call :correr "TP2_LiDAR_GEDI_ICESat2\03_Scripts\02_Procesamiento\cobertura_BAP"       TP2_09_cobertura_BAP.py
call :correr "TP2_LiDAR_GEDI_ICESat2\03_Scripts\02_Procesamiento\auditoria_L4A"       TP2_10_auditoria_L4A.py
call :correr "TP2_LiDAR_GEDI_ICESat2\03_Scripts\02_Procesamiento\auditoria_L4A"       TP2_11_escenarios_hoja_caida.py
call :correr "TP5_Sinergia_Multisensor\03_Scripts\02_Procesamiento\modelos"   TP5_02_modelos.py
call :correr "TP5_Sinergia_Multisensor\03_Scripts\04_Validacion"              TP5_03_validacion.py
call :correr "TP5_Sinergia_Multisensor\03_Scripts\03_Analisis\incendio"       TP5_04_biomasa_quemada.py
call :correr "TP5_Sinergia_Multisensor\03_Scripts\05_Exportacion"             TP5_05_mapas.py

echo.
echo ================================================================
echo  LISTO. Los diez pasos terminaron bien.
echo  Registro completo: %LOG%
echo ================================================================
pause
exit /b 0

:correr
set /a N+=1
echo.
echo ================================================================
echo  PASO !N! de 10 - %~2
echo ================================================================
cd /d "%RAIZ%%~1"
echo. >> "%LOG%"
echo ############ PASO !N! - %~2 >> "%LOG%"
python "%~2" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo.
  echo EL PASO !N! FALLO: %~2
  echo Las ultimas lineas del registro:
  powershell -NoProfile -Command "Get-Content -Tail 25 \"%LOG%\""
  echo.
  echo El registro completo esta en: %LOG%
  pause
  exit
)
echo    ok
exit /b 0
