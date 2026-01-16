# Backend ORION

La partie backend, également appelée le cerveau d'Orion, orchestre l'intelligence artificielle, le flux audio en temps réel et les outils collaboratifs pour automatiser la maintenance industrielle.

## Fonctionnalités

Orion planifie automatiquement les interventions de maintenance depuis les demandes vocales des opérateurs. Lorsqu'un incident est signalé, l'agent crée des événements dans les calendriers Google (maintenance et ligne de production concernée) selon le niveau d'urgence. Il vérifie les disponibilités du calendrier maintenance pour trouver le premier créneau libre, puis envoie un email récapitulatif à l'équipe de maintenance via l'API Gmail. L'agent peut également consulter le planning des prochaines interventions pour les techniciens. L'ensemble du traitement s'effectue via LiveKit pour la communication audio temps réel et OpenAI Realtime Model pour l'analyse directe de la voix, sans étape de transcription intermédiaire.

## Choix techniques

- **LiveKit Agents SDK** : Architecture agentique via le SDK LiveKit Agents. Les fonctions sont exposées au modèle via le décorateur `@llm.ai_callable()` et héritent de `llm.FunctionContext`. Lorsque le modèle identifie un besoin nécessitant une action externe, il invoque automatiquement ces fonctions asynchrones. Contrairement à une fonction classique qui bloque l'exécution, une fonction asynchrone permet à Orion de lancer une tâche en arrière-plan (comme l'envoi d'un mail) tout en poursuivant l'échange avec l'utilisateur. Les paramètres sont typés avec `Annotated` et `llm.TypeInfo` pour guider le modèle dans l'appel des fonctions.

- **OpenAI Realtime Model** : Compréhension vocale directe sans étape de transcription intermédiaire. Le modèle analyse directement l'intention de l'opérateur à partir du signal vocal, minimisant la latence.

- **Google Calendar API** : Synchronisation des équipes maintenance/production, vérification des disponibilités pour trouver le premier créneau libre, traçabilité des arrêts de production.

- **Gmail API** : Notifications immédiates et historisation des interventions. Chaque demande génère un email avec tous les détails (ligne, machine, problème, urgence, horaire).

- **Google People API** : Identification des contacts pour la coordination. Permet à Orion d'identifier le destinataire à partir d'un nom, prénom ou description, sans que l'utilisateur ait à dicter l'adresse e-mail complète.

- **OAuth 2.0** : Sécurisation des échanges via des jetons d'accès à durée limitée. Orion agit au nom de l'utilisateur avec des permissions définies, sans manipuler directement les identifiants.

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
