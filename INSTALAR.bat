@echo off
setlocal
cd /d "%~dp0"
echo Instalando Programa Vida y Ministerio...
where py >nul 2>nul
if errorlevel 1 (
  echo No se encontro Python. Instale Python 3.12 o superior desde python.org y marque "Add Python to PATH".
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" py -m venv .venv
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py initialize_vym
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0crear_acceso_directo.ps1"
echo.
echo Instalacion terminada. Se creo un acceso directo en el Escritorio.
pause
