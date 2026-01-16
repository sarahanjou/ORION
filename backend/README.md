# Orion Agent - Assistant Personnel IA

Orion est un assistant personnel IA développé avec LiveKit et OpenAI, capable de gérer votre calendrier Google, vos emails Gmail et vos contacts.

## 🚀 Installation Rapide

### Prérequis
- Python 3.10 ou supérieur
- Compte Google avec API activées
- Clé API OpenAI
- Compte LiveKit

### Installation
```bash
# 1. Aller dans le dossier backend
cd backend

# 2. Créer un environnement virtuel
python3 -m venv venv

# 3. Activer l'environnement virtuel
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate     # Sur Windows

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Configurer les variables d'environnement
# Créer un fichier .env dans le dossier backend/ avec vos clés API
# Voir la section Configuration ci-dessous pour la liste des variables requises
```

## ⚙️ Configuration

### 1. Variables d'environnement
Créez un fichier `.env` dans le dossier `backend/` et configurez les variables suivantes :

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# LiveKit
LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here

# CORS Configuration (optionnel)
# En développement : laisser vide pour autoriser localhost automatiquement
# En production : spécifier les origines autorisées séparées par des virgules
# Exemple : ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_ORIGINS=

# Google Calendar IDs
PERSO_CALENDAR_ID=your_personal_calendar_id_here
REVISIONS_CALENDAR_ID=your_revisions_calendar_id_here
ANNIVERSAIRES_CALENDAR_ID=your_anniversaires_calendar_id_here
POLYTECH_CALENDAR_ID=your_polytech_calendar_id_here
FAMILLE_CALENDAR_ID=your_famille_calendar_id_here
SPORT_CALENDAR_ID=your_sport_calendar_id_here
```

### 2. Google API Setup
1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez les APIs suivantes :
   - Google Calendar API
   - Gmail API
   - People API
4. Créez des credentials OAuth 2.0
5. Téléchargez le fichier JSON et placez-le dans `secrets/credentials.json`

### 3. Calendriers Google
Créez les calendriers suivants dans Google Calendar et notez leurs IDs :
- Calendrier personnel
- Calendrier révisions
- Calendrier anniversaires
- Calendrier Polytech
- Calendrier famille
- Calendrier sport

## 🎯 Utilisation

### Démarrer l'agent
```bash
# Aller dans le dossier backend
cd backend

# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'agent (méthode simple)
cd agent
python run_agent.py

# Ou en module (recommandé)
python3 -m orion.app.agent dev
```

### Démarrer le serveur Flask
```bash
# Aller dans le dossier backend
cd backend

# Activer l'environnement virtuel
source venv/bin/activate

# Lancer le serveur Flask
python server/server.py
```

### Fonctionnalités
- **Gestion de calendrier** : Ajouter, lister, supprimer des événements
- **Gestion d'emails** : Créer des brouillons, envoyer des emails
- **Gestion de contacts** : Créer, modifier, supprimer des contacts
- **Interface vocale** : Communication naturelle avec Orion

## 🔧 Dépannage

### Problèmes courants
1. **Erreur d'authentification Google** : Vérifiez que `secrets/credentials.json` est présent
2. **Erreur de variables d'environnement** : Vérifiez que le fichier `.env` est correctement configuré
3. **Erreur de dépendances** : Réinstallez avec `pip install -r requirements.txt`

### Logs
Les logs sont affichés dans la console. Pour plus de détails, modifiez le niveau de log dans `agent/orion/app/agent.py`.

## 📝 Notes
- L'agent est configuré pour Sarah Anjou avec des calendriers spécifiques à Polytech
- Les abréviations de cours sont automatiquement appliquées
- L'agent commence toujours par "Oui Sarah ?"

## 📁 Structure du Backend

```
backend/
├── server/        # Serveur Flask pour tokens LiveKit
│   └── server.py
├── agent/         # Agent Orion
│   └── orion/     # Code source de l'agent
├── secrets/       # Fichiers de configuration sensibles
├── requirements.txt
└── Procfile
```
