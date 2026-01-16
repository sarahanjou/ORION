# ORION

Agent IA conversationnel vocal pour faciliter la communication entre les équipes de production et de maintenance en industrie.

## Le problème

En atelier de production, les opérateurs doivent garder les mains propres et libres. Quand un incident survit, alerter la maintenance via un clavier ou une souris n'est pas pratique. Orion permet de signaler un besoin par commande vocale, directement depuis l'atelier.

## Comment ça marche

Orion écoute la demande vocale de l'opérateur, identifie les personnes concernées, consulte leurs agendas, planifie l'intervention et envoie automatiquement un email récapitulatif à la maintenance.

**Côté production** : un terminal vocal installé en atelier  
**Côté maintenance** : une app mobile pour consulter les interventions en temps réel

## Architecture

- **Communication vocale** : LiveKit pour l'échange audio en temps réel
- **Raisonnement** : OpenAI Realtime Model pour comprendre l'intention directement depuis la voix
- **Actions** : Google APIs (Gmail, Calendar, People) pour gérer les emails, agendas et contacts
- **Sécurité** : OAuth 2.0 pour l'authentification

## Démarrage rapide

### Prérequis

- Python 3.10+
- Flutter SDK
- Compte LiveKit
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

### Lancer le projet

Le plus simple :
```bash
cd scripts
bash demo.sh
```

Ce script lance automatiquement l'agent Orion et l'application Flutter.

## Configuration

Les variables d'environnement se configurent dans `backend/.env`. Voir [backend/README.md](backend/README.md) pour les détails.

## Structure

```
ORION/
├── frontend/          # Application Flutter (Web, iOS, Android)
├── backend/           # Agent Orion (Python)
│   ├── server/        # Serveur Flask pour tokens LiveKit
│   ├── agent/         # Code source de l'agent
│   └── secrets/       # Configuration OAuth
└── scripts/           # Scripts de lancement
```

## Notes

- Projet développé dans le cadre d'une PeiP 2 à Polytech (septembre-décembre 2025)
- Prototype fonctionnel, prêt pour des améliorations en vue d'une industrialisation
- Matériel : Raspberry Pi Zero 2, écran 7 pouces, système audio mono
