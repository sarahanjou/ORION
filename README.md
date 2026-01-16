# ORION

Projet d'assistant personnel IA développé avec Flutter (frontend) et Python (backend), utilisant LiveKit pour la communication vocale en temps réel.

## 📁 Structure du Projet

```
ORION/
├── frontend/          # Application Flutter (Web, iOS, Android)
├── backend/           # Serveur Python avec agent Orion
│   ├── server/        # Serveur Flask pour tokens LiveKit
│   │   └── server.py
│   ├── agent/         # Code source de l'agent Orion
│   │   └── orion/
│   └── secrets/       # Fichiers de configuration sensibles
├── scripts/           # Scripts de lancement et utilitaires
├── docs/              # Documentation
└── README.md          # Ce fichier
```

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.10+
- Flutter SDK
- Compte LiveKit
- Clés API OpenAI et Google

### Installation

1. **Backend (Agent Orion)**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
pip install -r requirements.txt
```

2. **Frontend (Flutter)**
```bash
cd frontend
flutter pub get
```

### Lancement

**Option 1 : Script automatique (recommandé)**
```bash
cd scripts
bash demo.sh
```

**Option 2 : Lancement manuel**

1. Démarrer l'agent Orion :
```bash
cd scripts
bash launch_orion.sh
```

2. Dans un autre terminal, lancer l'application Flutter :
```bash
cd frontend
flutter clean
flutter pub get
flutter run -d chrome
```

## 📚 Documentation

- [Documentation du backend](backend/README.md)
- [Diagnostics LiveKit](docs/DIAGNOSTIC_LIVEKIT.md)
- [Solution appliquée](docs/SOLUTION_APPLIQUEE.md)

## 🛠️ Scripts Disponibles

- `demo.sh` : Lance l'agent et l'application Flutter automatiquement
- `launch_orion.sh` : Lance uniquement l'agent Orion (macOS/Linux)
- `launch_orion.bat` : Lance uniquement l'agent Orion (Windows)
- `dispatch_agent.py` : Script Python pour dispatcher l'agent à une room LiveKit

## ⚙️ Configuration

Les variables d'environnement doivent être configurées dans :
- `backend/.env` (fichier centralisé pour le serveur Flask et l'agent Orion)

Voir [backend/README.md](backend/README.md) pour plus de détails.

## 📝 Notes

- Le serveur Flask est déployé sur Render pour la production
- L'agent Orion gère les calendriers Google, Gmail et les contacts
- L'interface vocale utilise LiveKit pour la communication en temps réel
