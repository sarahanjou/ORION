#!/usr/bin/env python3
"""
Script pour dispatcher l'agent Orion à une room LiveKit
Utilise l'API LiveKit directement, sans passer par le serveur Flask
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from livekit import api

# Charger les variables d'environnement
# Chercher dans plusieurs emplacements possibles
script_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = os.getcwd()  # Répertoire depuis lequel le script est exécuté

# Calculer le répertoire racine du projet (parent de scripts/)
project_root = os.path.dirname(script_dir)

env_paths = [
    # Depuis le répertoire racine du projet (fichier .env centralisé)
    os.path.join(project_root, "backend/.env"),
    # Depuis le répertoire courant (où le script est exécuté)
    os.path.join(current_dir, "backend/.env"),
    # Depuis le répertoire du script
    os.path.join(script_dir, "../backend/.env"),
    # Chemins relatifs standards
    "backend/.env",
    # Fallback: ancien emplacement pour compatibilité
    os.path.join(project_root, "backend/src/config/.env"),
    "backend/src/config/.env",
    ".env",
]

env_loaded = False
for env_path in env_paths:
    # Essayer le chemin tel quel
    if os.path.exists(env_path):
        load_dotenv(env_path)
        env_loaded = True
        print(f"✅ Variables d'environnement chargées depuis: {os.path.abspath(env_path)}")
        break
    # Essayer avec chemin absolu
    full_path = os.path.abspath(env_path)
    if os.path.exists(full_path) and full_path != env_path:
        load_dotenv(full_path)
        env_loaded = True
        print(f"✅ Variables d'environnement chargées depuis: {full_path}")
        break

if not env_loaded:
    print("⚠️  Aucun fichier .env trouvé, utilisation des variables d'environnement système")
    print(f"   Répertoire courant: {current_dir}")
    print(f"   Répertoire du script: {script_dir}")
    print(f"   Chemins testés:")
    for env_path in env_paths[:6]:  # Afficher les 6 premiers
        tested = os.path.abspath(env_path) if not os.path.isabs(env_path) else env_path
        exists = "✓" if os.path.exists(tested) else "✗"
        print(f"     {exists} {tested}")

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Variable d'environnement manquante: {name}")
    return value

async def dispatch_agent_async(room_name="my-room", agent_name="orion-assistant"):
    """Dispatche l'agent à la room spécifiée (version asynchrone)"""
    try:
        api_key = get_env_var("LIVEKIT_API_KEY")
        api_secret = get_env_var("LIVEKIT_API_SECRET")
        livekit_url = get_env_var("LIVEKIT_URL")
        
        print(f"🔄 Dispatch de l'agent '{agent_name}' vers la room '{room_name}'...")
        print(f"   LiveKit URL: {livekit_url}")
        
        # Initialiser l'API LiveKit
        lkapi = api.LiveKitAPI(
            url=livekit_url,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Créer la requête de dispatch
        dispatch_request = api.CreateAgentDispatchRequest(
            agent_name=agent_name,
            room=room_name
        )
        
        # Dispatcher l'agent
        dispatch = await lkapi.agent_dispatch.create_dispatch(dispatch_request)
        
        print(f"✅ Agent dispatché avec succès!")
        print(f"   Dispatch ID: {dispatch.job_id if hasattr(dispatch, 'job_id') else 'N/A'}")
        
        # Fermer l'API
        await lkapi.aclose()
        
        return True
            
    except Exception as e:
        print(f"❌ Erreur lors du dispatch: {e}")
        import traceback
        traceback.print_exc()
        return False

def dispatch_agent(room_name="my-room", agent_name="orion-assistant"):
    """Wrapper synchrone pour dispatcher l'agent"""
    return asyncio.run(dispatch_agent_async(room_name, agent_name))

if __name__ == "__main__":
    room = sys.argv[1] if len(sys.argv) > 1 else "my-room"
    agent = sys.argv[2] if len(sys.argv) > 2 else "orion-assistant"
    
    success = dispatch_agent(room, agent)
    sys.exit(0 if success else 1)
