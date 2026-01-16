# Backend ORION

Backend Python : serveur Flask pour tokens LiveKit + agent vocal qui planifie automatiquement les interventions de maintenance depuis les demandes vocales des opérateurs.

## Fonctionnalités

- **Planification automatique** : Crée des événements dans Google Calendar (maintenance + ligne de production) selon l'urgence
- **Notifications** : Envoie des emails Gmail à l'équipe de maintenance avec les détails de l'intervention
- **Consultation planning** : Récupère les prochaines interventions depuis le calendrier maintenance
- **Communication vocale** : Traite les demandes vocales via LiveKit et OpenAI Realtime Model

## Choix techniques

- **Google Calendar** : Synchronisation des équipes maintenance/production, vérification disponibilités, traçabilité
- **Gmail API** : Notifications immédiates et historisation des interventions
- **Google People API** : Identification des contacts pour la coordination
- **LiveKit** : Communication audio temps réel entre opérateur et agent
- **OpenAI Realtime Model** : Compréhension vocale directe (pas de transcription)

## Installation

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Créez `backend/.env` :

```env
OPENAI_API_KEY=your_key
LIVEKIT_URL=wss://your-url.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
MAINTENANCE_CALENDAR_ID=your_calendar_id
PRODUCTION_LIGNE_1_CALENDAR_ID=your_calendar_id
PRODUCTION_LIGNE_2_CALENDAR_ID=your_calendar_id
EMAIL_MAINTENANCE=maintenance@company.com
ALLOWED_ORIGINS=
```

**Google OAuth** : Placez `credentials.json` dans `secrets/`. Au premier lancement, l'authentification Google créera `secrets/token.json`.

## Lancement

**Serveur Flask** :
```bash
python server/server.py
```

**Agent Orion** :
```bash
cd agent
python run_agent.py
```

## Déploiement usine

Le serveur Flask est déployé sur Render (voir `Procfile`). Pour la production :

1. Configurez les variables d'environnement sur Render
2. Déployez le serveur Flask (génère les tokens LiveKit)
3. Lancez l'agent Orion sur une machine dédiée ou un serveur
4. Configurez les calendriers Google (maintenance, ligne 1, ligne 2)
5. Testez la connexion LiveKit depuis le frontend

## Structure

```
backend/
├── server/server.py          # Flask : /getToken, /dispatchAgent
├── agent/orion/
│   ├── app/agent.py          # Point d'entrée agent
│   ├── app/functions/
│   │   ├── maintenance.py    # Planification interventions
│   │   ├── calendar.py       # Gestion calendriers
│   │   ├── gmail.py          # Envoi emails
│   │   └── contacts.py       # Gestion contacts
│   └── services/google/      # Authentification OAuth
└── secrets/                  # credentials.json, token.json
```
