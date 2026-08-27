@echo off
REM ===================================================================
REM  COPIAR_CRUDOS_A_RESPALDO.bat
REM
REM  DOBLE CLIC. Copia TODAS las imagenes crudas descargadas
REM  (00_COMUN\08_Originales_crudos, unos 253 GB) a un disco aparte,
REM  para tenerlas a mano si falla internet durante el curso.
REM
REM  COMO SE USA
REM     1. Conecte el disco externo (o tenga a mano la letra del disco
REM        de destino, por ejemplo E: o F:).
REM     2. Doble clic a este archivo.
REM     3. Escriba la letra del disco cuando la pida y presione Entrar.
REM     4. Espere: puede tardar varias horas la primera vez.
REM
REM  Si la copia se interrumpe (corte de luz, se cerro la ventana),
REM  vuelva a ejecutarlo con el mismo destino: CONTINUA donde quedo,
REM  no arranca de cero. Los originales NO se modifican: solo se leen.
REM ===================================================================

chcp 65001 >nul
setlocal

rem El atajo vive en 02_Practica\09_ATAJOS: la raiz esta dos niveles arriba.
for %%I in ("%~dp0..\..") do set "RAIZ=%%~fI"
set "ORIGEN=%RAIZ%\02_Practica\00_COMUN\08_Originales_crudos"

if not exist "%ORIGEN%" (
  echo.
  echo  NO ENCUENTRO la carpeta de originales:
  echo     %ORIGEN%
  echo  Revise que este atajo siga en 02_Practica\09_ATAJOS.
  pause
  exit /b 1
)

echo.
echo ================================================================
echo  RESPALDO DE LAS IMAGENES CRUDAS DEL CURSO
echo.
echo  Origen: %ORIGEN%
echo.
echo  Escriba la letra del disco de destino y presione Entrar.
echo  Ejemplos:  E:      (disco externo)
echo             D:\RESPALDO_CURSO   (una carpeta en otro disco)
echo ================================================================
set /p "DESTINO=Destino: "

if "%DESTINO%"=="" (
  echo  No escribio nada. No se copio nada.
  pause
  exit /b 1
)

rem Si escribio una sola letra (por ejemplo I), se completa a I:
if "%DESTINO:~1%"=="" set "DESTINO=%DESTINO%:"

rem El destino tiene que existir antes de arrancar.
if not exist "%DESTINO%\" (
  echo.
  echo  NO ENCUENTRO el destino %DESTINO%
  echo  Revise que el disco este conectado y la letra sea la correcta
  echo  ^(la letra se ve en el Explorador de archivos, en "Este equipo"^).
  pause
  exit /b 1
)

set "DEST=%DESTINO%\CRUDOS_CURSO_BIOMASA_2026"

echo.
echo  Se va a copiar a:  %DEST%
echo  Puede tardar VARIAS HORAS. Va a ver pasar cada archivo con su
echo  porcentaje: eso indica que esta trabajando. No apague el equipo.
echo  Cierre esta ventana si no queria hacerlo.
echo.
pause

robocopy "%ORIGEN%" "%DEST%" /E /Z /R:2 /W:5 /NJH /ETA

if errorlevel 8 (
  echo.
  echo  LA COPIA FALLO. Revise el mensaje de arriba y el espacio libre
  echo  del disco de destino ^(hacen falta unos 260 GB libres^).
  pause
  exit /b 1
)

echo.
echo ================================================================
echo  LISTO. Verificacion:
for /f %%A in ('dir "%ORIGEN%" /s /a-d /b 2^>nul ^| find /c /v ""') do set "N_ORI=%%A"
for /f %%A in ('dir "%DEST%" /s /a-d /b 2^>nul ^| find /c /v ""') do set "N_DES=%%A"
echo     Archivos en el origen : %N_ORI%
echo     Archivos en el destino: %N_DES%
echo.
if "%N_ORI%"=="%N_DES%" (
  echo  Las dos cifras COINCIDEN: el respaldo esta completo.
) else (
  echo  Las cifras NO coinciden. Vuelva a ejecutar este atajo con el
  echo  mismo destino: la copia continuara donde quedo.
)
echo ================================================================
pause
exit /b 0
