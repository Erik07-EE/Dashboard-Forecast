@echo off
chcp 65001 >nul
title Actualizar y publicar Dashboard Forecast
setlocal

REM ================== CONFIGURACION (editar una sola vez) ==================
set "FORECAST=G:\Unidades compartidas\7. Compras y producto\7.3. Compras\7.3.3. Rotación\Forecast\Forecast.xlsm"
set "COSTOS=G:\Unidades compartidas\7. Compras y producto\7.4. Producto\7.4.5. Gestor de precios\Masters\Costos.xlsm"
set "REPO_URL=https://github.com/Erik07-EE/Dashboard-Forecast.git"
set "PAGES_URL=https://erik07-ee.github.io/Dashboard-Forecast/Dashboard_Forecast.html"
REM =========================================================================

cd /d "%~dp0"

echo(
echo  ==================================================
echo    Publicar Dashboard Forecast
echo  ==================================================

REM ---- Detectar Python (py launcher o python real) ----
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY (
  python --version >nul 2>nul && set "PY=python"
)
if not defined PY goto :sin_python

echo(
echo === 1/4  Regenerando el dashboard desde el Forecast + Costos ===
%PY% "scripts\generar_dashboard.py" "%FORECAST%" "Dashboard_Forecast.html" "%COSTOS%"
if errorlevel 1 goto :error_generar

echo(
echo === 2/4  Revisando que los datos esten al dia ===
%PY% "scripts\chequear_actualizacion.py"
if errorlevel 2 goto :preguntar_igual
if errorlevel 1 goto :error_chequeo
goto :mostrar_cambios

:preguntar_igual
echo(
set "RTA2=N"
set /p "RTA2=  Publicar igual? (S/N): "
if /i not "%RTA2%"=="S" goto :cancelado

:mostrar_cambios
echo(
echo === 3/4  Esto es lo que se va a publicar ===
echo(
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 goto :primera_vez
git status --short
echo(
set "RTA=N"
set /p "RTA=  Publicar estos cambios? (S/N): "
if /i not "%RTA%"=="S" goto :cancelado
git remote set-url origin "%REPO_URL%" 2>nul
goto :subir

:primera_vez
echo  Primera vez: preparando la carpeta para publicar...
git init
git branch -M main
git remote add origin "%REPO_URL%"

:subir
echo(
echo === 4/4  Subiendo a GitHub ===
git add -A
git commit -m "Actualiza dashboard %date% %time%"
git push -u origin main
if errorlevel 1 goto :error_subir

echo(
echo  --------------------------------------------------
echo   OK - Dashboard publicado.
echo(
echo   %PAGES_URL%
echo(
echo   Abrilo con Ctrl+F5 para ver la version nueva.
echo   Puede tardar un minuto en actualizarse.
echo  --------------------------------------------------
goto :fin

:cancelado
echo(
echo  Cancelado. No se subio nada a GitHub.
echo  (El dashboard de tu PC si quedo regenerado.)
goto :fin

:sin_python
echo(
echo  ERROR: no se encontro Python en esta PC.
echo  Instalalo desde python.org y tilda "Add python.exe to PATH".
echo  Despues corre:  pip install openpyxl
goto :fin

:error_generar
echo(
echo  --------------------------------------------------
echo   ERROR al generar el dashboard.
echo   Revisa que estas rutas existan y que Drive este andando:
echo     %FORECAST%
echo     %COSTOS%
echo   No se subio nada.
echo  --------------------------------------------------
goto :fin

:error_chequeo
echo(
echo  --------------------------------------------------
echo   ERROR al revisar el dashboard. Mira el detalle arriba.
echo   No se subio nada.
echo  --------------------------------------------------
goto :fin

:error_subir
echo(
echo  --------------------------------------------------
echo   ERROR al publicar. Mira el detalle arriba.
echo   Si se abrio una ventana de GitHub, inicia sesion
echo   con Erik07-EE y volve a correr este archivo.
echo   Los cambios quedaron guardados en tu PC: no se perdio nada.
echo  --------------------------------------------------
goto :fin

:fin
echo(
pause
