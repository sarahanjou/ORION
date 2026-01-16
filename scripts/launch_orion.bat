@echo off
echo ================================
echo   Orion - Lancement du serveur
echo ================================

REM Détecter le dossier du script (scripts/)
set SCRIPT_DIR=%~dp0
REM Détecter le dossier racine du projet (parent de scripts/)
set BASE_DIR=%SCRIPT_DIR%..
REM Normaliser le chemin (enlever le \ final)
set BASE_DIR=%BASE_DIR:~0,-1%
echo Dossier projet : %BASE_DIR%

REM Définir les chemins
set VENV_PYTHON=%BASE_DIR%\backend\venv\Scripts\python.exe
set SRC_DIR=%BASE_DIR%\backend\agent

IF NOT EXIST "%SRC_DIR%" (
    echo ERREUR : Le dossier agent est introuvable.
    pause
    exit /b 1
)

cd "%SRC_DIR%"
echo Dossier agent : %cd%

echo Mise à jour de pip...
"%VENV_PYTHON%" -m pip install --upgrade pip

echo Installation des dépendances...
"%VENV_PYTHON%" -m pip install -r "%BASE_DIR%\backend\requirements.txt"

echo Lancement de Orion Agent en mode dev...
"%VENV_PYTHON%" -m orion.app.agent dev

pause
