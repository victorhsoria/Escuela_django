@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Primero ejecute INSTALAR.bat
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m waitress --listen=127.0.0.1:8000 vym_project.wsgi:application
