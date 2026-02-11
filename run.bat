uv@echo off
REM Ejecutar detector de neumonia - usar despues de haber instalado dependencias
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo Iniciando con .venv...
    .venv\Scripts\python.exe detector_neumonia.py
    goto :eof
)

echo No se encontro entorno virtual con dependencias instaladas.
echo.
echo Ejecuta primero en esta carpeta:
echo   python -m venv .venv
echo   .venv\Scripts\pip install -r requirements.txt
echo.
echo Si falla por "long path", activa rutas largas en Windows:
echo   https://pip.pypa.io/warnings/enable-long-paths
echo O copia el proyecto a una ruta corta (ej: C:\Neumonia) y repite.
pause
