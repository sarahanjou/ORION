# ORION

Agent IA conversationnel vocal conçu pour fluidifier la communication entre les équipes de production et de maintenance en environnement industriel.

## Le problème

En atelier, les opérateurs doivent garder les mains libres et propres (port de gants, manipulation de pièces). En cas d'incident, l'utilisation d'un clavier ou d'une souris pour saisir un ticket de maintenance est inadaptée. Orion permet de signaler une anomalie par simple commande vocale.

## Fonctionnement

Orion écoute la demande vocale de l'opérateur, identifie les personnes concernées, consulte leurs agendas, planifie l'intervention et envoie automatiquement un email récapitulatif à la maintenance.

**Côté production** : un terminal vocal installé en atelier  
**Côté maintenance** : une app mobile pour consulter les interventions en temps réel

## Architecture

- **Communication vocale** : LiveKit pour l'échange audio en temps réel
- **Raisonnement** : OpenAI Realtime Model pour comprendre l'intention directement depuis la voix
- **Prise de décision** : Google APIs (Gmail, Calendar, People) pour gérer les emails, agendas et contacts
- **Sécurisation des échanges** : OAuth 2.0 pour l'authentification

## Démarrage rapide

### Prérequis

- Python 3.10+
- Flutter SDK
- API LiveKit
- Clés API OpenAI et Google

### Installation

**Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend**
```bash
cd frontend
flutter pub get
```

### Lancement du projet

```bash
cd scripts
bash demo.sh
```

## Configuration

Les variables d'environnement doivent être renseignées dans le fichier backend/.env.