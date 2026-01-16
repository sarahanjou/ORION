import os.path
import os
from orion.utils.paths import get_credentials_path, get_token_path
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

#If you modify these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar",
          "https://mail.google.com/",
          "https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.modify",
          "https://www.googleapis.com/auth/contacts",
]

# Construire les chemins absolus pour token.json et credentials.json via utils (surcharges env supportées)
token_path = str(get_token_path())
credentials_path = str(get_credentials_path())

def authenticate_google_api():

    creds = None

    # Vérifier si le fichier token.json existe
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    #If there is no valid token, he creates a new one
    if not creds or not creds.valid:

        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

        except RefreshError:
            print("Le jeton est invalide ou expiré. Suppression du jeton et redémarrage du flux d'authentification.")
            if os.path.exists(token_path):
                os.remove(token_path)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Sauvegarder le nouveau token dans token.json
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    
    # Création des différents services
    try:
        services = {
            "gmail": build("gmail", "v1", credentials=creds),
            "calendar": build("calendar", "v3", credentials=creds),
            "people": build("people", "v1", credentials=creds)
        }
        logging.info("Authentification réussie pour les différents services.")
        return services
    except HttpError as error:
        logging.error(f"Erreur lors de la connexion aux APIs : {error}")
        return None

service = authenticate_google_api()

if service:
    gmail_service = service["gmail"]
    calendar_service = service["calendar"]
    people_service = service["people"]
    logging.info("Les différents services sont prêts à être utilisés.")

else:
    logging.error("L'authentification a échoué.")