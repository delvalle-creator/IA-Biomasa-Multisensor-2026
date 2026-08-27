@echo off
REM ===================================================================
REM  EJECUTAR_descarga_BIOMASS.bat
REM
REM  DOBLE CLIC. Descarga los productos BIOMASS que caen sobre los dos
REM  recintos, incluidos los de NIVEL 2A publicados el 30/06/2026:
REM  altura de dosel y retrodispersion con el suelo cancelado.
REM
REM  ESTE .bat SI NECESITA TOKEN. La consulta del catalogo es abierta -de
REM  eso se ocupa EJECUTAR_consulta_BIOMASS.bat-, pero la descarga exige
REM  autenticarse ante la ESA.
REM
REM  EL TOKEN NO SE ESCRIBE EN NINGUNA CONSOLA. Se pega en el Bloc de notas
REM  y se guarda como   C:\Temp\Personal\biomass_token.txt
REM  Ese archivo esta FUERA del proyecto, por la regla 8 del README: nunca
REM  se guardan contrasenias ni tokens dentro de 03_Scripts.
REM
REM  Los productos quedan en 00_COMUN\08_Originales_crudos\03_post\BIOMASS_bandaP, que
REM  es donde ya estan los trece de nivel 1. Si un archivo ya esta, no se
REM  vuelve a bajar: se puede cortar y retomar sin perder lo hecho.
REM
REM  SIN REDIRECCION de la salida, por el mismo motivo que el .bat de
REM  consulta: con redireccion la ventana se ve muda y parece colgada.
REM ===================================================================

chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
setlocal
rem El atajo vive en 09_ATAJOS: la raiz del proyecto es la carpeta de arriba.
for %%I in ("%~dp0..") do set "RAIZ=%%~fI\"
set "TOKEN=C:\Temp\Personal\biomass_token.txt"

REM  --- BLOQUE DE ORDENES EQUIVALENTES ---
echo.
echo ================================================================
echo  ESTE .bat EQUIVALE A ESCRIBIR, EN EL MINIFORGE PROMPT:
echo.
echo     conda activate aoi
echo     cd C:\Temp\CURSO_BIOMASA_2026\02_Practica\TP4_Radar_SAR\03_Scripts\01_Pre_procesamiento\BIOMASS_bandaP
echo     python -u descargar_biomass.py
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

REM  El token se comprueba ANTES de salir a la red: si falta, es mejor
REM  decirlo aca que despues de dos minutos de consultas al catalogo.
if not exist "%TOKEN%" (
  echo.
  echo ================================================================
  echo  FALTA EL ARCHIVO DEL TOKEN
  echo ================================================================
  echo  No encontre:
  echo     %TOKEN%
  echo.
  echo  1. Genere el token offline en el portal de ESA MAAP.
  echo  2. Abra el Bloc de notas, pegue el token y guarde el archivo con
  echo     esa ruta exacta. Si queda cortado en varias lineas no importa.
  echo  3. Vuelva a hacer doble clic aca.
  echo.
  echo  El token dura 90 dias. No hace falta escribirlo en la consola.
  echo ================================================================
  echo.
  pause
  exit /b 1
)

echo Token encontrado. No se muestra ni se copia.
echo.
cd /d "%RAIZ%TP4_Radar_SAR\03_Scripts\01_Pre_procesamiento\BIOMASS_bandaP"
python -u descargar_biomass.py
set "SALIO=%errorlevel%"
echo.
REM  Solo se anuncia el final feliz SI el script termino bien. Antes se
REM  anunciaba siempre, y el 02/08/2026 quedo diciendo "Termino. Los
REM  productos quedan en..." justo despues de que el script avisara que no
REM  habia bajado nada. Dos mensajes que se contradicen en la misma
REM  pantalla es peor que ninguno.
if "%SALIO%"=="0" (
  echo ================================================================
  echo  Termino bien. Los productos quedan en
  echo     00_COMUN\08_Originales_crudos\03_post\BIOMASS_bandaP
  echo  Despues:  python TP4_11_inspeccionar_biomass_L2A.py
  echo ================================================================
) else (
  echo ================================================================
  echo  NO SE BAJO NADA. El motivo esta explicado mas arriba.
  echo  Queda registrado en
  echo     TP2_LiDAR_GEDI_ICESat2\05_Resultados\06_Control_calidad\DESCARGA_BIOMASS.log
  echo ================================================================
)
echo.
pause
endlocal
