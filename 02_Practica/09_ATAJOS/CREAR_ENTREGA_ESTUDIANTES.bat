@echo off
REM ===================================================================
REM  CREAR_ENTREGA_ESTUDIANTES.bat
REM
REM  DOBLE CLIC. Arma la carpeta que se copia al estudiante.
REM
REM  Deja el resultado en la raiz del curso, en _ENTREGA_ESTUDIANTES.
REM  No modifica nada: solo copia. Se puede volver a correr las veces
REM  que haga falta; sincroniza lo que cambio y deja el resto igual.
REM
REM  QUE SE COPIA
REM     las presentaciones en PDF, la guia completa en PDF, los
REM     programas, los grafos de SNAP, los recortes de trabajo, los
REM     resultados, la bibliografia en formato de cita y los atajos.
REM
REM  QUE NO SE COPIA, y por que
REM     08_Originales_crudos  las imagenes crudas: 253 GB, no viajan. El
REM                           estudiante trabaja sobre 02_Subsets_SNAP_QGIS,
REM                           que SI se copia, porque es sobre eso que se
REM                           trabaja en clase
REM     *.docx            NINGUN Word viaja: el estudiante recibe PDF
REM     *.pptx            idem con las presentaciones
REM     *.original_*      versiones viejas de scripts, respaldadas antes
REM     *.previo          de una correccion; no son material del curso
REM     _fuente           la carpeta de originales de la guia
REM     02_Fuentes_pptx   los .pptx del docente
REM     01_Articulos      PDF de terceros cuya licencia no permite
REM                       redistribuirlos; van los .ris y los DOI
REM     99_PRIVADO_...    material del docente
REM ===================================================================

chcp 65001 >nul
setlocal

rem El atajo vive en 02_Practica\09_ATAJOS: la raiz esta dos niveles arriba.
for %%I in ("%~dp0..\..") do set "RAIZ=%%~fI"
set "DEST=%RAIZ%\_ENTREGA_ESTUDIANTES"

echo.
echo ================================================================
echo  ORIGEN : %RAIZ%
echo  DESTINO: %DEST%
echo ================================================================
echo.
echo  Se va a armar la carpeta de entrega. Puede tardar unos minutos
echo  la primera vez. Cierre esta ventana si no queria hacerlo.
echo.
pause

robocopy "%RAIZ%" "%DEST%" /E /R:1 /W:1 ^
  /XD "99_PRIVADO_NO_DISTRIBUIR" "08_Originales_crudos" "02_Fuentes_pptx" ^
      "_fuente" "__pycache__" "01_Articulos" "_ENTREGA_ESTUDIANTES" ^
  /XF "*.pyc" "*.log" "*.docx" "*.pptx" "*.original_*" "*.previo" ^
  /NFL /NDL /NJH

if errorlevel 8 (
  echo.
  echo  LA COPIA FALLO. Revise el mensaje de arriba.
  pause
  exit /b 1
)

echo.
echo ================================================================
echo  LISTO. La carpeta quedo en:
echo     %DEST%
echo.
for /f "tokens=3" %%A in ('dir "%DEST%" /s /-c ^| findstr /C:"bytes"') do set "TAM=%%A"
echo  Tamano aproximado: %TAM% bytes
echo.
echo  Antes de entregarla, compruebe dos cosas:
echo     1. que la guia completa este en PDF dentro de
echo        02_Practica\00_Guia_teorica_practica
echo     2. que las presentaciones esten en PDF dentro de
echo        01_Teoria\01_Presentaciones_pdf
echo ================================================================
pause
exit /b 0
