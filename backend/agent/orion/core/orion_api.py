from openai import OpenAI
import os
from dotenv import load_dotenv
from orion.utils.paths import get_env_path

# Charge les variables d'environnement depuis le fichier .env centralisé
load_dotenv(dotenv_path=str(get_env_path()))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_chatgpt(messages):
    """Envoie une requête à ChatGPT et retourne la réponse."""
    r = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3,
    )
    return r.choices[0].message.content