import os
import base64
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

from livekit.api import AccessToken, VideoGrants

app = Flask(__name__)

# Configuration CORS sécurisée
# En développement : autorise localhost avec n'importe quel port
# En production : utilise la variable d'environnement ALLOWED_ORIGINS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins:
    # Production : utiliser les origines spécifiées dans .env
    origins_list = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
else:
    # Développement : autoriser localhost avec tous les ports
    origins_list = [
        "http://localhost:*",
        "http://127.0.0.1:*",
        "http://localhost",
        "http://127.0.0.1"
    ]

CORS(app, resources={r"/*": {"origins": origins_list}})

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing environment variable: {name}")
    return value

@app.route("/getToken")
def get_token():
    api_key = get_env_var("LIVEKIT_API_KEY")
    api_secret = get_env_var("LIVEKIT_API_SECRET")

    token = (
        AccessToken(api_key, api_secret)
        .with_identity("identity")
        .with_name("mobile-app")
        .with_grants(VideoGrants(room_join=True, room="my-room"))
        .to_jwt()
    )

    return jsonify({"token": token})

@app.route("/dispatchAgent")
def dispatch_agent():
    """Crée un job pour dispatcher l'agent Orion à la room"""
    try:
        api_key = get_env_var("LIVEKIT_API_KEY")
        api_secret = get_env_var("LIVEKIT_API_SECRET")
        livekit_url = get_env_var("LIVEKIT_URL")
        
        # Utiliser l'API REST LiveKit directement (plus simple pour Flask synchrone)
        # Convertir wss:// en https:// pour l'API REST
        api_base_url = livekit_url.replace("wss://", "https://").replace("ws://", "http://")
        
        # Endpoint pour dispatcher un agent
        dispatch_url = f"{api_base_url}/twirp/livekit.AgentDispatchService/DispatchAgent"
        
        # Authentification Basic (API Key:Secret encodé en base64)
        auth_string = f"{api_key}:{api_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json"
        }
        
        # Payload pour dispatcher l'agent
        payload = {
            "agent_name": "orion-assistant",
            "room": "my-room"
        }
        
        # Faire la requête POST
        response = requests.post(dispatch_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return jsonify({
                "success": True,
                "message": "Agent dispatched successfully to room my-room"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"LiveKit API error: {response.status_code} - {response.text}"
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("Flask server started (local mode)")
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),  # Render injecte PORT automatiquement
        debug=False
    )