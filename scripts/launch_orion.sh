#!/bin/bash

echo "=============================="
echo "   Orion - Lancement serveur"
echo "=============================="

# Dossier du script (scripts/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Dossier racine du projet (parent de scripts/)
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
echo "Dossier projet : $BASE_DIR"

# Chemins
VENV_DIR="$BASE_DIR/backend/venv"
SRC_DIR="$BASE_DIR/backend/agent"

if [ ! -d "$SRC_DIR" ]; then
    echo "ERREUR : Le dossier agent est introuvable."
    exit 1
fi

# Détection du système d'exploitation
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    VENV_PYTHON="$VENV_DIR/Scripts/python"
    VENV_PYTHON_EXE="$VENV_DIR/Scripts/python.exe"
else
    VENV_PYTHON="$VENV_DIR/bin/python"
    VENV_PYTHON_EXE="$VENV_DIR/bin/python"
fi

# Vérifier si l'environnement virtuel existe et est valide
NEED_NEW_VENV=false

if [ ! -f "$VENV_PYTHON" ] && [ ! -f "$VENV_PYTHON_EXE" ]; then
    NEED_NEW_VENV=true
    echo "L'environnement virtuel n'existe pas ou n'est pas compatible avec ce système."
else
    # Tester si le venv fonctionne
    if [ -f "$VENV_PYTHON" ]; then
        TEST_CMD="$VENV_PYTHON"
    else
        TEST_CMD="$VENV_PYTHON_EXE"
    fi
    
    # Tester si Python fonctionne
    if ! "$TEST_CMD" --version &> /dev/null; then
        NEED_NEW_VENV=true
        echo "L'environnement virtuel existant semble corrompu."
        echo "Suppression de l'ancien environnement virtuel..."
        rm -rf "$VENV_DIR"
    fi
fi

if [ "$NEED_NEW_VENV" = true ]; then
    echo "Création d'un nouvel environnement virtuel..."
    
    # Vérifier que Python est installé
    if ! command -v python3 &> /dev/null; then
        echo "ERREUR : Python3 n'est pas installé ou n'est pas dans le PATH."
        exit 1
    fi
    
    # Créer l'environnement virtuel
    python3 -m venv "$VENV_DIR"
    
    if [ $? -ne 0 ]; then
        echo "ERREUR : Impossible de créer l'environnement virtuel."
        exit 1
    fi
    
    echo "Environnement virtuel créé avec succès."
fi

# Utiliser le bon chemin selon le système
if [ -f "$VENV_PYTHON" ]; then
    PYTHON_CMD="$VENV_PYTHON"
elif [ -f "$VENV_PYTHON_EXE" ]; then
    PYTHON_CMD="$VENV_PYTHON_EXE"
else
    echo "ERREUR : Impossible de trouver l'exécutable Python dans l'environnement virtuel."
    exit 1
fi

cd "$SRC_DIR"
echo "Dossier agent : $(pwd)"

echo "Mise à jour de pip..."
"$PYTHON_CMD" -m pip install --upgrade pip

echo "Installation des dépendances..."
"$PYTHON_CMD" -m pip install -r "$BASE_DIR/backend/requirements.txt"

echo "Lancement de Orion Agent en mode dev..."
"$PYTHON_CMD" -m orion.app.agent dev
