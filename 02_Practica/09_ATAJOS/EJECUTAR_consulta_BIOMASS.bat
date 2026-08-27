@echo off
REM ===================================================================
REM  EJECUTAR_consulta_BIOMASS.bat
REM
REM  DOBLE CLIC. Solo CONSULTA el catalogo de ESA MAAP: no descarga nada
REM  y NO NECESITA TOKEN. Contesta si existen productos BIOMASS de NIVEL 2
REM  -altura de bosque y biomasa AGB- sobre los dos recintos.
REM
REM  OJO CON LA REDIRECCION  (corregido el 31/07/2026)
REM  Este .bat NO redirige la salida a un archivo. Antes lo hacia, y eso
REM  dejaba la ventana muda: cuando Python escribe a un archivo en vez de a
REM  una consola usa buffer completo, asi que no aparecia nada hasta el
REM  final y parecia colgado. Ahora el script escribe el registro el mismo
REM  y duplica cada linea a la pantalla, al instante.
REM
REM  Se usa python -u para que ni siquiera quede buffer de por medio.
REM
REM  El registro queda igual en
REM     TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad\CONSULTA_BIOMASS.log
REM ===================================================================

chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
setlocal
rem El atajo vive en 09_ATAJOS: la raiz del proyecto es la carpeta de arriba.
for %%I in ("%~dp0..") do set "RAIZ=%%~fI\"
REM  --- BLOQUE DE ORDENES EQUIVALENTES ---

echo.
echo ================================================================
echo  ESTE .bat EQUIVALE A ESCRIBIR, EN EL MINIFORGE PROMPT:
echo.
echo     conda activate aoi
echo     cd C:\Temp\CURSO_BIOMASA_2026\02_Practica\TP4_Radar_SAR\03_Scripts\01_Pre_procesamiento\BIOMASS_bandaP
echo     python -u buscar_biomass_L2.py
echo.
echo     Solo consulta el catalogo. No descarga y no necesita credenciales.
echo.
echo  Si prefiere entender que pasa, cierre esta ventana y escribalo a
echo  mano. El atajo sirve para repetir, no para aprender.
echo ================================================================
echo.


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

echo.
echo ================================================================
echo  Consulta al catalogo de ESA MAAP  (sin token, solo lectura)
echo  Si en diez segundos no dice nada, es la red: se puede cerrar.
echo ================================================================
echo.
cd /d "%RAIZ%TP4_Radar_SAR\03_Scripts\01_Pre_procesamiento\BIOMASS_bandaP"
python -u buscar_biomass_L2.py
echo.
if errorlevel 2 (
  echo El catalogo no respondio. No es un problema del proyecto.
) else (
  REM  Solo se anuncia el registro SI EXISTE. El 01/08/2026 el .bat lo daba
  REM  por guardado sin comprobarlo, y esa vez el script no habia podido
  REM  abrirlo: el mensaje afirmaba algo falso.
  set "REG=%RAIZ%TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad\CONSULTA_BIOMASS.log"
  if exist "%REG%" (
    echo Registro guardado en %REG%
  ) else (
    echo AVISO: no se pudo escribir el registro. La salida de arriba es la buena.
    echo        Suele pasar si el .log quedo abierto en un editor.
  )
)
echo.
pause
