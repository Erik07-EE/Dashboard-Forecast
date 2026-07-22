@echo off
chcp 65001 >nul
title Actualizar y publicar Dashboard Forecast
setlocal

REM ================== CONFIGURACION (editar una sola vez) ==================
set "FORECAST=G:\Unidades compartidas\7. Compras y producto\7.3. Compras\7.3.3. Rotación\Forecast\Forecast.xlsm"
set "COSTOS=G:\Unidades compartidas\7. Compras y producto\7.6. Costos\Costos.xlsm"
set "REPO_URL=https://github.com/Erik07-EE/Dashboard-Forecast.git"
set "PAGES_URL=https://erik07-ee.github.io/Dashboard-Forecast/Dashboard_Forecast.html"
REM =========================================================================

cd /d "%~dp0"

REM ---- Detectar Python (py launcher o python real, ignorando el stub de Store) ----
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY (
  python --version >nul 2>nul && set "PY=python"
)

echo(
echo === 1/3  Regenerando dashboard desde el Forecast + Costos ===
if defined PY (
  %PY% "generador\generar_dashboard.py" "%FORECAST%" "Dashboard_Forecast.html" "%COSTOS%"
  if errorlevel 1 (
    echo.
    echo ERROR al generar el dashboard. Revisa las rutas FORECAST y COSTOS arriba.
    pause
    exit /b 1
  )
) else (
  echo ATENCION: no se encontro Python en esta PC.
  echo Se subira la version ACTUAL del dashboard sin regenerar.
  echo Para que se actualice solo, instala Python desde python.org
  echo y tilda "Add python.exe to PATH". Luego corre: pip install openpyxl
)

echo(
echo === 2/3  Preparando publicacion en GitHub ===
if not exist ".git" (
  echo Primera vez: inicializando repositorio git...
  git init
  git branch -M main
  git remote add origin "%REPO_URL%"
) else (
  git remote set-url origin "%REPO_URL%" 2>nul
)

echo(
echo === 3/3  Subiendo a GitHub ===
git add -A
git commit -m "Actualiza dashboard %date% %time%"
git push -u origin main
if errorlevel 1 (
  echo.
  echo ================== ATENCION ==================
  echo El push fallo. Suele ser por login la primera vez.
  echo Si se abrio una ventana de GitHub, inicia sesion con Erik07-EE
  echo y volve a correr este .bat.
  echo ==============================================
  pause
  exit /b 1
)

echo(
echo ================== LISTO ==================
echo Dashboard publicado. Tu URL de GitHub Pages:
echo   %PAGES_URL%
echo (La primera vez, activa Pages en Settings ^> Pages ^> Branch: main / root)
echo ===========================================
pause
