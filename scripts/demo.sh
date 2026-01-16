#!/bin/bash

# Script de déploiement rapide - Tout doit être déjà installé
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PYTHON="$BASE_DIR/backend/venv/bin/python"
SRC_DIR="$BASE_DIR/backend/agent"
SERVER_DIR="$BASE_DIR/backend"
APP_DIR="$BASE_DIR/frontend"
AGENT_LOG="$SCRIPT_DIR/agent.log"

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "Arrêt des services..."
    kill $AGENT_PID $FLUTTER_PID $SERVER_PID 2>/dev/null
    # Tuer aussi les processus Chrome liés à Flutter
    pkill -f "chrome.*flutter" 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "=============================="
echo "   Lancement d'Orion"
echo "=============================="
echo ""

# Option : Lancer le serveur Flask local pour le dispatch de l'agent
USE_LOCAL_SERVER="${USE_LOCAL_SERVER:-false}"

if [ "$USE_LOCAL_SERVER" = "true" ]; then
    echo "Lancement du serveur Flask local"
    cd "$SERVER_DIR"
    if [ ! -f "$VENV_PYTHON" ]; then
        echo "Erreur: venv non trouvé"
        echo "   Créez un venv et installez les dépendances dans $BASE_DIR/backend"
        exit 1
    fi
    # Utiliser le venv du projet
    SERVER_PYTHON="$VENV_PYTHON"
    "$SERVER_PYTHON" "$SERVER_DIR/server/server.py" > /tmp/flask_server.log 2>&1 &
    SERVER_PID=$!
    echo "Serveur Flask lancé (PID: $SERVER_PID) sur http://localhost:5000"
    sleep 2
else
    echo "Utilisation du serveur distant pour dispatcher l'agent"
    echo "IMPORTANT: Assurez-vous que l'endpoint /dispatchAgent est déployé sur Render"
    echo "   Pour utiliser le serveur local: USE_LOCAL_SERVER=true bash demo.sh"
fi

# Démarrer l'agent Orion avec logs visibles
cd "$SRC_DIR"
echo ""
echo "=============================="
echo "   Logs de l'agent Orion"
echo "=============================="
echo ""
"$VENV_PYTHON" -m orion.app.agent dev 2>&1 | tee "$AGENT_LOG" &
AGENT_PID=$!

# Attendre que l'agent démarre
echo "Démarrage de l'agent Orion..."
sleep 2

# Lancer l'application Flutter AVANT de dispatcher l'agent
cd "$APP_DIR"
echo ""
echo "Démarrage de l'application Flutter..."
echo "L'application va s'ouvrir dans votre navigateur."
echo ""

# Vérifier que Flutter est installé
if ! command -v flutter &> /dev/null; then
    echo "Erreur: Flutter n'est pas installé ou n'est pas dans le PATH"
    exit 1
fi

# Nettoyage et récupération des dépendances à chaque lancement
echo "Nettoyage de Flutter (flutter clean)..."
flutter clean > /dev/null 2>&1

echo "Récupération des dépendances (flutter pub get)..."
flutter pub get > /dev/null 2>&1

# Lancer Flutter avec une meilleure gestion des erreurs
echo "Lancement de Flutter..."
echo "Note: L'application va se compiler et s'ouvrir dans Chrome"
echo "      Cela peut prendre 10-20 secondes..."
echo ""

# Lancer Flutter en arrière-plan mais attendre qu'il soit prêt
# IMPORTANT : ne pas forcer de port, on laisse Flutter choisir
nohup flutter run -d chrome > /tmp/flutter_app.log 2>&1 &
FLUTTER_PID=$!

# Attendre que Flutter compile et démarre (peut prendre du temps)
echo "Attente de la compilation Flutter..."
for i in {1..30}; do
    sleep 1
    # Vérifier si Flutter a démarré en cherchant dans les logs
    if grep -q "Flutter run key commands" /tmp/flutter_app.log 2>/dev/null; then
        echo "Flutter a démarré avec succès!"
        break
    fi
    # Vérifier si le processus est toujours actif
    if ! ps -p $FLUTTER_PID > /dev/null 2>&1; then
        echo "Flutter s'est arrêté. Erreurs:"
        tail -30 /tmp/flutter_app.log
        echo ""
        echo "Essayez de lancer manuellement:"
        echo "  cd $APP_DIR && flutter run -d chrome"
        break
    fi
    if [ $i -eq 10 ] || [ $i -eq 20 ]; then
        echo "   Compilation en cours... (${i}s)"
    fi
done

if ps -p $FLUTTER_PID > /dev/null 2>&1; then
    echo "Flutter est en cours d'exécution (PID: $FLUTTER_PID)"
    # Essayer de récupérer l'URL exacte du serveur Flutter dans les logs
    FLUTTER_URL=$(grep -o 'http://localhost:[0-9]*' /tmp/flutter_app.log | head -1)
    if [ -n "$FLUTTER_URL" ]; then
        echo "   L'application devrait s'ouvrir dans Chrome sur : $FLUTTER_URL"
        echo "   Si ce n'est pas le cas, ouvrez cette URL manuellement."
    else
        echo "   L'application devrait s'ouvrir dans Chrome."
    fi
fi

# Attendre que Flutter se connecte à la room LiveKit
echo ""
echo "Attente de la connexion de l'application à LiveKit (10 secondes)..."
sleep 10

# Dispatcher l'agent à la room APRÈS que le client soit connecté
echo ""
echo "Dispatch de l'agent à la room..."
cd "$SCRIPT_DIR"
if [ -f "$SCRIPT_DIR/dispatch_agent.py" ]; then
    # Utiliser le venv du projet pour exécuter le script
    if [ -f "$VENV_PYTHON" ]; then
        "$VENV_PYTHON" "$SCRIPT_DIR/dispatch_agent.py" "my-room" "orion-assistant" 2>&1 | head -5
        DISPATCH_EXIT=$?
        if [ $DISPATCH_EXIT -eq 0 ]; then
            echo "Agent dispatché avec succès à la room!"
        else
            echo "Le dispatch a retourné un code d'erreur $DISPATCH_EXIT"
        fi
    else
        python3 "$SCRIPT_DIR/dispatch_agent.py" "my-room" "orion-assistant" 2>&1 | head -5
    fi
else
    echo "Script dispatch_agent.py non trouvé, l'agent ne sera pas dispatché automatiquement"
fi
sleep 2

# Attendre que l'utilisateur arrête avec Ctrl+C
echo ""
echo "Tous les services sont lancés!"
echo "   - Agent Orion: dispatché à la room"
echo "   - Application Flutter: connectée à LiveKit"
echo ""
echo "Vous pouvez maintenant parler à Orion dans l'application Chrome."
echo "Appuyez sur Ctrl+C pour arrêter tous les services."
echo ""
wait $AGENT_PID

# Nettoyage à l'arrêt
cleanup
