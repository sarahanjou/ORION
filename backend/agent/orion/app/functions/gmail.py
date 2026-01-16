"""Fonctions concernant l'API Gmail."""
from __future__ import annotations

import re
import logging
import base64
import urllib.parse
import webbrowser
from typing import Annotated, Optional
from email.mime.text import MIMEText

from orion.services.google.auth import service
from orion.app.functions.base import BaseFunctions, llm

logger = logging.getLogger(__name__)


class GmailFunctions(BaseFunctions):
    """Fonctions pour gérer les emails Gmail."""

    @llm.ai_callable()
    async def create_draft(
        self,
        recipient: Annotated[
            str, 
            llm.TypeInfo(description="The recipient email address")
        ],
        subject: Annotated[
            str, 
            llm.TypeInfo(description="The subject of the email draft")
        ],
        body: Annotated[
            str, 
            llm.TypeInfo(description="The body content of the email draft")
        ],
        open_in_browser: Annotated[
            Optional[bool],
            llm.TypeInfo(description="If true, open Gmail drafts with the created draft filtered")
        ] = True,
    ):
        """
        Creates a draft in gmail.

        Args: 
            recipient (str): The email address of the receiver of the mail.
            subject (str): The subject of the email draft.
            body (str): The body content of the email draft.
        """
        logger.info(f"Creating a draft with these args : recipient={recipient}, subject={subject}")

        try:
            if not body:
                raise ValueError("Le corps du mail (body) ne peut pas être vide ou None.")
        
            message = MIMEText(body, _charset="utf-8")

            message["to"] = recipient
            message["subject"] = subject

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            draft = {"message": {"raw": encoded_message}}

            creating_draft = service['gmail'].users().drafts().create(userId="me", body=draft).execute()

            logger.info(f"Brouillon créé avec l'ID: {creating_draft['id']}")
            if open_in_browser:
                try:
                    # Open Gmail drafts filtered by subject
                    q = urllib.parse.quote(f"subject:{subject} in:drafts")
                    gmail_url = f"https://mail.google.com/mail/u/0/#search/{q}"
                    webbrowser.open(gmail_url)
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir Gmail (drafts): {e}")
            return 'Brouillon créé.'

        except Exception as e:
            logger.error(f"Erreur lors de la création du brouillon : {e}")
            raise

    @llm.ai_callable()
    async def send_draft(
        self,
        recipient: Annotated[
            str,
            llm.TypeInfo(description="The recipient email address")
        ],
        subject: Annotated[
            str, 
            llm.TypeInfo(description="The subject of the email draft")
        ],
        open_in_browser: Annotated[
            Optional[bool],
            llm.TypeInfo(description="If true, open Gmail sent mail filtered by subject")
        ] = True,
    ):
        """
        Sends a draft in gmail knowing the recipient and the subject.

        Args: 
            recipient (str): The email address of the receiver of the mail.
            subject (str): The subject of the email draft.
        """
        logger.info(f"Sending a draft with these args : recipient={recipient}, subject={subject}")

        try:
            drafts_list = service['gmail'].users().drafts().list(userId="me").execute()
            drafts = drafts_list.get("drafts", [])

            if not drafts:
                logger.error("Aucun brouillon trouvé.")
                return "Aucun brouillon trouvé."

            draft_id = None

            for draft in drafts:
                draft_data = service['gmail'].users().drafts().get(userId="me", id=draft["id"]).execute()
                message = draft_data["message"]
                headers = {header["name"]: header["value"] for header in message["payload"]["headers"]}

                found_recipient = headers.get("to", "").strip()
                found_subject = headers.get("subject", "").strip()

                match = re.search(r'<(.*?)>', found_recipient)

                if match:
                    found_recipient = match.group(1)

                if found_recipient == recipient and found_subject == subject:
                    draft_id = draft["id"]
                    break

            if not draft_id:
                logger.error("Aucun brouillon correspondant trouvé.")
                return "Aucun brouillon correspondant trouvé."

            send_response = service['gmail'].users().drafts().send(userId="me", body={"id": draft_id}).execute()

            logger.info(f"Brouillon envoyé avec succès : {send_response}")
            if open_in_browser:
                try:
                    q = urllib.parse.quote(f"subject:{subject} in:sent")
                    gmail_url = f"https://mail.google.com/mail/u/0/#search/{q}"
                    webbrowser.open(gmail_url)
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir Gmail (sent): {e}")
            return 'Brouillon envoyé.'

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du brouillon : {e}")
            return f"Erreur lors de l'envoi du brouillon : {str(e)}"
