@echo off 

color 0B
python --version 3>nul
if %errorlevel% neq 0 (
    echo Es necesario instar Python :(
    %USERPROFILE%
)
color 0A

if not exist subtitulos (
    REM Crear un entorno virtual llamado "subtitulos"
    echo Creando entorno virtual...
    python -m venv subtitulos
)
echo Entorno virtual creado correctamente :)

color 0D
call subtitulos\Scripts\activate
echo Instalando librerias necesarias...
pip install -r requirements.txt
echo Librerias instaladas correctamente :)
cls
echo Todo funciono correctamente :)
color 0E
python Subtitulos.py
