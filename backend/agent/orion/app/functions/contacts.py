"""Fonctions concernant l'API People (Google Contacts)."""
from __future__ import annotations

import logging
import urllib.parse
import webbrowser
from typing import Annotated, Optional

from orion.services.google.auth import service
from orion.app.functions.base import BaseFunctions, llm

logger = logging.getLogger(__name__)


class ContactFunctions(BaseFunctions):
    """Fonctions pour gérer les contacts Google."""

    @llm.ai_callable()
    async def create_contact(
        self,
        first_name: Annotated[
            str,
            llm.TypeInfo(description="First name of the contact to create")
        ],
        last_name: Annotated[
            str,
            llm.TypeInfo(description="Last name of the contact to create")
        ],
        email: Annotated[
            Optional[str],
            llm.TypeInfo(description="Email address of the contact to create (optional)")
        ] = None,
        phone_number: Annotated[
            Optional[str],
            llm.TypeInfo(description="Phone number of the contact to create (optional)")
        ] = None,
        notes: Annotated[
            Optional[str],
            llm.TypeInfo(description="Infos of the contact to create (optional)")
        ] = None,
        open_in_browser: Annotated[
            Optional[bool],
            llm.TypeInfo(description="If true, open Google Contacts in the browser")
        ] = True,
    ):
        """
        Creates a contact in Google Contact knowing the first name and the last name of the contact.

        Args: 
            first_name (str): First name of the contact to create
            last_name (str): Last name of the contact to create
            email (Optional[str]): Email address of the contact to create (optional)
            phone_number (Optional[str]): Phone number of the contact to create (optional)
        """
        logger.info(f"Creating a new contact with the first name : {first_name} and the last name : {last_name}.")

        newcontact_data = {
            "names": [{"givenName": first_name, "familyName": last_name}],
            "emailAddresses": [{"value": email}] if email else [],
            "phoneNumbers": [{"value": phone_number}] if phone_number else [],
            "biographies": [{"value": notes, "contentType": "TEXT_PLAIN"}] if notes else [],
        }

        try:
            create_response = service["people"].people().createContact(body=newcontact_data).execute()
            if open_in_browser:
                try:
                    # Open the specific contact page using the resource name
                    contact_resource_name = create_response.get("resourceName", "")
                    if contact_resource_name:
                        # Remove 'people/' prefix if present
                        contact_id = contact_resource_name.replace("people/", "")
                        contact_url = f"https://contacts.google.com/person/{contact_id}"
                        webbrowser.open(contact_url)
                    else:
                        # Fallback to general contacts page
                        webbrowser.open("https://contacts.google.com/")
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir Google Contacts: {e}")
            return 'Contact créé.'

        except Exception as e:
            logger.error(f"Erreur lors de la création du contact {first_name} {last_name} : {e}")
            return f"Erreur lors de la création du contact {first_name} {last_name} : {str(e)}"

    @llm.ai_callable()
    async def delete_contact(
        self,
        first_name: Annotated[
            str,
            llm.TypeInfo(description="First name of the contact to delete")
        ],
        last_name: Annotated[
            str,
            llm.TypeInfo(description="Last name of the contact to delete")
        ],
        open_in_browser: Annotated[
            Optional[bool],
            llm.TypeInfo(description="If true, open Google Contacts in the browser")
        ] = True,
    ):
        """
        Deletes a contact in Google Contact knowing the first name and the last name of the contact.

        Args: 
            first_name (str): First name of the contact to delete
            last_name (str): Last name of the contact to delete
        """
        logger.info(f"Suppression du contact {first_name} {last_name}.")

        try:
            # On liste tous les contacts pour trouver le bon ID
            list_contacts = service["people"].people().connections().list(
                resourceName="people/me",
                personFields="names"
            ).execute()

            contact_id = None

            if "connections" in list_contacts:
                for contact in list_contacts["connections"]:
                    names = contact.get("names", "")
                    for name in names:
                        if name.get("givenName") == first_name and name.get("familyName") == last_name:
                            contact_id = contact["resourceName"]
                            break
            
            if not contact_id:
                logger.info(f"Aucun contact trouvé avec le nom {first_name} {last_name}.")
                return f"Aucun contact trouvé avec le nom {first_name} {last_name}."

            # Supprimer le contact trouvé
            delete_service = service["people"].people().deleteContact(resourceName=contact_id).execute()
            if open_in_browser:
                try:
                    # Open a search for the deleted contact to show it's no longer there
                    search_query = urllib.parse.quote(f"{first_name} {last_name}")
                    contact_url = f"https://contacts.google.com/search/{search_query}"
                    webbrowser.open(contact_url)
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir Google Contacts: {e}")
            return "Contact Supprimé"

        except Exception as e:
            logger.error(f"Erreur lors de la suppression du contact {first_name} {last_name} : {e}")
            return f"Erreur lors de la suppression du contact {first_name} {last_name} : {str(e)}"

    @llm.ai_callable()
    async def modify_contact(
        self,
        first_name: Annotated[
            str,
            llm.TypeInfo(description="First name of the contact to modify")
        ],
        last_name: Annotated[
            str,
            llm.TypeInfo(description="Last name of the contact to modify")
        ],
        email: Annotated[
            Optional[str],
            llm.TypeInfo(description="Email address of the contact to modify (optional)")
        ] = None,
        phone_number: Annotated[
            Optional[str],
            llm.TypeInfo(description="Phone number of the contact to modify (optional)")
        ] = None,
        notes: Annotated[
            Optional[str],
            llm.TypeInfo(description="Infos of the contact to modify (optional)")
        ] = None,
        open_in_browser: Annotated[
            Optional[bool],
            llm.TypeInfo(description="If true, open Google Contacts in the browser")
        ] = True,
    ):
        """
        Modifies a contact in Google Contact knowing the first name and the last name of the contact.

        Args: 
            first_name (str): First name of the contact to update 
            last_name (str): Last name of the contact to update
            email (Optional[str]): Email address of the contact to update (optional)
            phone_number (Optional[str]): Phone number of the contact to update (optional)
            notes (Optional[str]): Infos of the contact to create (optional)
        """
        logger.info("Modifying the contact.")

        try:
            # Lister tous les contacts
            list_contacts = service["people"].people().connections().list(
                resourceName="people/me",
                personFields="names,emailAddresses,phoneNumbers,biographies"
            ).execute()
            
            contact_id = None
            existing_contact = None

            # Trouver l'ID du contact correspondant et attribuer le bon contact à existing_contact
            if "connections" in list_contacts:
                for contact in list_contacts["connections"]:
                    names = contact.get("names", "")
                    for name in names:
                        if name.get("givenName") == first_name and name.get("familyName") == last_name:
                            contact_id = contact["resourceName"]
                            existing_contact = contact
                            break
            
            # Si aucun identifiant n'est trouvé
            if not contact_id:
                logger.info(f"Aucun contact trouvé avec le nom {first_name} {last_name}.")
                return f"Aucun contact trouvé avec le nom {first_name} {last_name}."
            
            # Implémenter les nouvelles données
            updated_contact_data = {
                "names": existing_contact.get("names", []),  # Garde le nom existant
                "emailAddresses": [{"value": email}] if email else existing_contact.get("emailAddresses", []),
                "phoneNumbers": [{"value": phone_number}] if phone_number else existing_contact.get("phoneNumbers", []),
                "biographies": [{"value": notes, "contentType": "TEXT_PLAIN"}] if notes else existing_contact.get("biographies", []),
            }

            # Envoyer les modifications
            update_service = service["people"].people().updateContact(
                resourceName=contact_id,
                body=updated_contact_data,
                # Spécifie les champs à modifier (names n'est pas à modifier car valeur obligatoire)
                updateMask="emailAddresses,phoneNumbers,biographies"
            ).execute()

            if open_in_browser:
                try:
                    # Open the specific contact page using the resource name
                    # Remove 'people/' prefix if present
                    clean_contact_id = contact_id.replace("people/", "")
                    contact_url = f"https://contacts.google.com/person/{clean_contact_id}"
                    webbrowser.open(contact_url)
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir Google Contacts: {e}")

            return 'Contact modifié.'

        except Exception as e:
            logger.error(f"Erreur lors de la modification du contact : {e}")
            return f"Erreur lors de la modification du contact : {str(e)}"

    @llm.ai_callable()
    async def research_contact(
        self,
        first_name: Annotated[
            Optional[str],
            llm.TypeInfo(description="First name of the contact to research.")
        ] = None,
        last_name: Annotated[
            Optional[str],
            llm.TypeInfo(description="Last name of the contact to research.")
        ] = None,
        nickname: Annotated[
            Optional[str],
            llm.TypeInfo(description="Nickname of the contact to research.")
        ] = None,
        notes: Annotated[
            Optional[str],
            llm.TypeInfo(description="Infos of the contact to research.")
        ] = None,
        open_in_browser: Annotated[
            Optional[bool],
            llm.TypeInfo(description="If true, open Google Contacts search in the browser")
        ] = True,
    ):
        """
        Researches a contact.

        Args: 
            first_name (Optional[str]): First name of the contact to research (optional)
            last_name (Optional[str]): Last name of the contact to research (optional)
            nickname (Optional[str]): Nickname of the contact to research (optional)
            notes (Optional[str]): Infos of the contact to research (optional)
        """
        
        logger.info("Recherche du contact.")

        try: 
            # Lister tous les contacts
            list_contacts = service["people"].people().connections().list(
                resourceName="people/me",
                personFields="names,nicknames,biographies,emailAddresses"
            ).execute()
            
            if "connections" not in list_contacts:
                return "Aucun contact trouvé."
            
            filtered_contacts = []
            
            for contact in list_contacts["connections"]:
                # Liste tous les names, nicknames et biographies des contacts dans 3 tableaux différents
                # Ce sont des listes
                contact_names = contact.get("names", [])
                contact_nicknames = contact.get("nicknames", [])
                contact_biographies = contact.get("biographies", [])

                # On récupère les valeurs individuellement
                # Ce sont des str
                contact_first_name = contact_names[0].get("givenName") if contact_names else None
                contact_last_name = contact_names[0].get("familyName") if contact_names else None
                contact_nickname = contact_nicknames[0].get("value") if contact_nicknames else None
                contact_notes = contact_biographies[0].get("value") if contact_biographies else None

                # Vérifier si le contact correspond aux critères de recherche
                match = True

                # Filtre par prénom (exact, case-insensitive)
                if first_name:
                    if not contact_first_name or contact_first_name.lower() != first_name.lower():
                        match = False

                # Filtre par nom de famille (exact, case-insensitive)
                if last_name:
                    if not contact_last_name or contact_last_name.lower() != last_name.lower():
                        match = False

                # Filtre par surnom (exact, case-insensitive)
                if nickname:
                    if not contact_nickname or contact_nickname.lower() != nickname.lower():
                        match = False

                # Filtre par notes/description (partial match, case-insensitive)
                if notes:
                    if not contact_notes or notes.lower() not in contact_notes.lower():
                        match = False

                # Si le contact correspond, l'ajouter à la liste
                if match:
                    # Extraire les emails du contact
                    contact_emails = contact.get("emailAddresses", [])
                    primary_email = contact_emails[0].get("value") if contact_emails else None

                    filtered_contacts.append({
                        "first_name": contact_first_name,
                        "last_name": contact_last_name,
                        "nickname": contact_nickname,
                        "notes": contact_notes,
                        "email": primary_email,
                        "full_contact": contact
                    })

            # Construire la réponse formatée
            if not filtered_contacts:
                # Construire le message des critères de recherche
                criteria_parts = []
                if first_name:
                    criteria_parts.append(f"first_name='{first_name}'")
                if last_name:
                    criteria_parts.append(f"last_name='{last_name}'")
                if nickname:
                    criteria_parts.append(f"nickname='{nickname}'")
                if notes:
                    criteria_parts.append(f"notes='{notes}'")

                criteria_str = ", ".join(criteria_parts) if criteria_parts else "no criteria"
                return f"No contacts found matching the criteria: {criteria_str}"

            # Formater les résultats
            response = f"Found {len(filtered_contacts)} contact(s)"
            if notes:
                response += f" matching '{notes}'"
            response += ":\n\n"

            for idx, contact_info in enumerate(filtered_contacts, 1):
                full_name_parts = []
                if contact_info["first_name"]:
                    full_name_parts.append(contact_info["first_name"])
                if contact_info["last_name"]:
                    full_name_parts.append(contact_info["last_name"])
                full_name = " ".join(full_name_parts) if full_name_parts else "Unknown"

                response += f"{idx}. {full_name}\n"

                if contact_info["email"]:
                    response += f"   Email: {contact_info['email']}\n"
                else:
                    response += f"   Email: (no email address)\n"

                if contact_info["notes"]:
                    response += f"   Description: {contact_info['notes']}\n"

                if contact_info["nickname"]:
                    response += f"   Nickname: {contact_info['nickname']}\n"

                response += "\n"

            # Si plusieurs contacts, demander à l'utilisateur de choisir
            if len(filtered_contacts) > 1:
                response += "Which contact would you like to use?"

            return response

        except Exception as e:
            logger.error(f"Erreur lors de la recherche du contact : {e}")
            return f"Erreur lors de la recherche du contact : {str(e)}"
