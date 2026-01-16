"""Fonctions de planification et consultation de maintenance."""
from __future__ import annotations

import os
import re
import logging
import random
import base64
import datetime
import webbrowser
from typing import Annotated, Optional
from email.mime.text import MIMEText

from orion.utils.dates import paris_tz
from orion.services.google.auth import service
from orion.app.functions.base import BaseFunctions, llm

logger = logging.getLogger(__name__)


class MaintenanceFunctions(BaseFunctions):
    """Fonctions pour gérer la maintenance de production."""

    @llm.ai_callable()
    async def schedule_maintenance(
        self,
        ligne_production: Annotated[
            str,
            llm.TypeInfo(description="Numéro de la ligne de production concernée (1 ou 2)")
        ],
        machine_name: Annotated[
            str,
            llm.TypeInfo(description="Nom ou identifiant de la machine concernée")
        ],
        probleme_description: Annotated[
            str,
            llm.TypeInfo(description="Description détaillée du problème rencontré")
        ],
        urgence: Annotated[
            str,
            llm.TypeInfo(description="Niveau d'urgence: 'urgent', 'moyen', ou 'faible'")
        ],
    ):
        """
        Planifie automatiquement une intervention de maintenance en fonction de l'urgence.
        Vérifie les disponibilités du calendrier maintenance et cale un créneau approprié.

        Args:
            ligne_production (str): Ligne de production (1 ou 2)
            machine_name (str): Nom de la machine
            probleme_description (str): Description du problème
            urgence (str): Niveau d'urgence (urgent/moyen/faible)
        """
        logger.info(f"Planification maintenance : ligne {ligne_production}, machine {machine_name}, urgence {urgence}")

        try:
            # 1. Récupérer l'heure actuelle à Paris
            now_paris = datetime.datetime.now(paris_tz)
            logger.info(f"Heure actuelle Paris : {now_paris}")

            # 2. Calculer les créneaux selon l'urgence
            urgence_lower = urgence.lower()

            if urgence_lower == "urgent" or urgence_lower == "haute":
                # Urgent : entre 5 et 30 minutes
                start_offset_min = 5
                start_offset_max = 30
                duration_hours = 1  # Durée de l'intervention : 1h
            elif urgence_lower == "moyen" or urgence_lower == "moyenne":
                # Moyen : entre 1h et 3h
                start_offset_min = 60
                start_offset_max = 180
                duration_hours = 2  # Durée : 2h
            else:  # faible
                # Faible : entre 5h et le lendemain (24h)
                start_offset_min = 300
                start_offset_max = 1440
                duration_hours = 3  # Durée : 3h

            # 3. Récupérer les calendriers depuis les variables d'environnement
            calendar_maintenance = os.getenv("MAINTENANCE_CALENDAR_ID")
            if ligne_production == "1":
                calendar_ligne = os.getenv("PRODUCTION_LIGNE_1_CALENDAR_ID")
            elif ligne_production == "2":
                calendar_ligne = os.getenv("PRODUCTION_LIGNE_2_CALENDAR_ID")
            else:
                return f"Erreur : ligne de production invalide (doit être 1 ou 2)"

            if not calendar_maintenance or not calendar_ligne:
                return "Erreur : calendriers de production non configurés dans .env"

            # 4. Fonction pour vérifier si un créneau est disponible
            def check_availability(start_time, end_time):
                """Vérifie si le calendrier maintenance est libre dans ce créneau"""
                try:
                    events_result = service['calendar'].events().list(
                        calendarId=calendar_maintenance,
                        timeMin=start_time.isoformat(),
                        timeMax=end_time.isoformat(),
                        singleEvents=True,
                        orderBy="startTime"
                    ).execute()

                    events = events_result.get('items', [])
                    return len(events) == 0  # Disponible si aucun événement
                except Exception as e:
                    logger.error(f"Erreur vérification disponibilité : {e}")
                    return True  # En cas d'erreur, on autorise

            # 5. Trouver le premier créneau disponible
            slot_found = False
            tentative = 0
            max_tentatives = 20

            while not slot_found and tentative < max_tentatives:
                # Calculer un créneau de départ aléatoire dans la plage
                offset_minutes = random.randint(start_offset_min, start_offset_max) + (tentative * 30)

                start_time = now_paris + datetime.timedelta(minutes=offset_minutes)
                end_time = start_time + datetime.timedelta(hours=duration_hours)

                # Arrondir à la demi-heure la plus proche
                start_time = start_time.replace(minute=(start_time.minute // 30) * 30, second=0, microsecond=0)
                end_time = start_time + datetime.timedelta(hours=duration_hours)

                # Vérifier disponibilité
                if check_availability(start_time, end_time):
                    slot_found = True
                    logger.info(f"Créneau trouvé : {start_time} - {end_time}")
                else:
                    logger.info(f"Créneau occupé, tentative suivante...")
                    tentative += 1

            if not slot_found:
                return f"Erreur : impossible de trouver un créneau disponible dans les {max_tentatives} prochaines tentatives"

            # 6. Créer le titre de l'événement
            event_title = f"MAINTENANCE - {probleme_description[:50]} - {machine_name}"

            # 7. Préparer le body de l'événement
            event_description = (
                f"Ligne de production : {ligne_production}\n"
                f"Machine : {machine_name}\n"
                f"Problème : {probleme_description}\n"
                f"Urgence : {urgence}\n"
                f"Signalé le : {now_paris.strftime('%d/%m/%Y à %H:%M')}"
            )

            # 8. Créer l'événement dans le calendrier maintenance
            event_body = {
                "summary": event_title,
                "description": event_description,
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "Europe/Paris"
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "Europe/Paris"
                }
            }

            event_maintenance = service['calendar'].events().insert(
                calendarId=calendar_maintenance,
                body=event_body
            ).execute()
            logger.info(f"Événement créé dans calendrier maintenance : {event_maintenance.get('id')}")

            # Ouvrir l'événement maintenance dans le navigateur
            event_maintenance_link = event_maintenance.get('htmlLink')
            if event_maintenance_link:
                try:
                    webbrowser.open(event_maintenance_link)
                    logger.info(f"Ouverture événement maintenance dans le navigateur")
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir l'événement maintenance : {e}")

            # 9. Créer le même événement dans le calendrier de la ligne de production
            event_ligne = service['calendar'].events().insert(
                calendarId=calendar_ligne,
                body=event_body
            ).execute()
            logger.info(f"Événement créé dans calendrier ligne {ligne_production} : {event_ligne.get('id')}")

            # Ouvrir l'événement de la ligne dans le navigateur
            event_ligne_link = event_ligne.get('htmlLink')
            if event_ligne_link:
                try:
                    webbrowser.open(event_ligne_link)
                    logger.info(f"Ouverture événement ligne {ligne_production} dans le navigateur")
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir l'événement ligne : {e}")

            # 10. Envoyer l'email de maintenance (directement, pas en brouillon)
            email_maintenance_addr = os.getenv("EMAIL_MAINTENANCE", "maintenance@orion.com")

            email_subject = f"[{urgence.upper()}] Maintenance requise - Ligne {ligne_production} - {machine_name}"
            email_body = (
                f"Bonjour,\n\n"
                f"Une intervention de maintenance a été planifiée :\n\n"
                f"Ligne de production : {ligne_production}\n"
                f"Machine : {machine_name}\n"
                f"Problème : {probleme_description}\n"
                f"Urgence : {urgence}\n\n"
                f"Date d'intervention : {start_time.strftime('%d/%m/%Y')}\n"
                f"Heure de début : {start_time.strftime('%H:%M')}\n"
                f"Heure de fin prévue : {end_time.strftime('%H:%M')}\n\n"
                f"Signalé le {now_paris.strftime('%d/%m/%Y à %H:%M')}\n\n"
                f"Cordialement,\n"
                f"Système Orion - Gestion de Production"
            )

            message = MIMEText(email_body, _charset="utf-8")
            message["to"] = email_maintenance_addr
            message["subject"] = email_subject

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            send_message = {"raw": encoded_message}

            # Envoyer directement l'email
            email_sent = service['gmail'].users().messages().send(userId="me", body=send_message).execute()
            logger.info(f"Email envoyé à {email_maintenance_addr} : {email_sent.get('id')}")

            # Ouvrir Gmail dans le navigateur pour voir l'email envoyé
            try:
                gmail_sent_url = f"https://mail.google.com/mail/u/0/#sent/{email_sent.get('id')}"
                webbrowser.open(gmail_sent_url)
                logger.info(f"Ouverture Gmail (email envoyé) dans le navigateur")
            except Exception as e:
                logger.warning(f"Impossible d'ouvrir Gmail : {e}")

            # 11. Retourner la confirmation
            response = (
                f"Maintenance planifiée avec succès !\n\n"
                f"Ligne {ligne_production} - {machine_name}\n"
                f"Problème : {probleme_description}\n"
                f"Urgence : {urgence}\n\n"
                f"Intervention prévue le {start_time.strftime('%d/%m/%Y')} de {start_time.strftime('%H:%M')} à {end_time.strftime('%H:%M')}\n\n"
                f"Email envoyé à {email_maintenance_addr}\n"
                f"Événements créés dans les calendriers (maintenance + ligne {ligne_production})"
            )

            return response

        except Exception as e:
            logger.error(f"Erreur lors de la planification de maintenance : {e}")
            import traceback
            traceback.print_exc()
            return f"Erreur lors de la planification : {str(e)}"

    @llm.ai_callable()
    async def get_maintenance_schedule(
        self,
        nombre_jours: Annotated[
            Optional[int],
            llm.TypeInfo(description="Nombre de jours à consulter dans le futur (par défaut: 7)")
        ] = 7,
    ):
        """
        Récupère les prochaines interventions de maintenance depuis le calendrier maintenance.
        Utile pour que l'équipe de maintenance consulte leur planning.

        Args:
            nombre_jours (int): Nombre de jours à consulter dans le futur
        """
        logger.info(f"Récupération du planning de maintenance (prochains {nombre_jours} jours)")

        try:
            # 1. Récupérer le calendrier maintenance depuis .env
            calendar_maintenance = os.getenv("MAINTENANCE_CALENDAR_ID")

            if not calendar_maintenance:
                return "Erreur : calendrier de maintenance non configuré dans .env"

            # 2. Calculer la période de temps
            now_paris = datetime.datetime.now(paris_tz)
            time_min = now_paris.isoformat()
            time_max = (now_paris + datetime.timedelta(days=nombre_jours)).isoformat()

            # 3. Récupérer les événements du calendrier maintenance
            events_result = service['calendar'].events().list(
                calendarId=calendar_maintenance,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                maxResults=20
            ).execute()

            events = events_result.get('items', [])

            if not events:
                return f"Aucune intervention de maintenance planifiée dans les {nombre_jours} prochains jours."

            # 4. Parser et formater les événements
            interventions = []

            for event in events:
                # Extraire le titre et la description
                title = event.get('summary', 'Sans titre')
                description = event.get('description', '')

                # Extraire les dates/heures
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                # Parser la date/heure
                try:
                    if 'T' in start:  # Format dateTime
                        start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                        end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))

                        # Convertir en heure de Paris si besoin
                        if start_dt.tzinfo is None:
                            start_dt = paris_tz.localize(start_dt)
                        else:
                            start_dt = start_dt.astimezone(paris_tz)

                        if end_dt.tzinfo is None:
                            end_dt = paris_tz.localize(end_dt)
                        else:
                            end_dt = end_dt.astimezone(paris_tz)

                        date_str = start_dt.strftime('%d/%m/%Y')
                        heure_debut = start_dt.strftime('%H:%M')
                        heure_fin = end_dt.strftime('%H:%M')
                    else:  # Format date seule
                        date_str = start
                        heure_debut = "Toute la journée"
                        heure_fin = ""
                except Exception as e:
                    logger.warning(f"Erreur parsing date: {e}")
                    date_str = start
                    heure_debut = "?"
                    heure_fin = "?"

                # Parser la description pour extraire les infos
                # Format : Ligne de production : X, Machine : XXX, Problème : XXX, Urgence : XXX
                ligne = "?"
                machine = "?"
                probleme = "?"
                urgence = "?"

                if description:
                    ligne_match = re.search(r'Ligne de production\s*:\s*(\d+)', description)
                    machine_match = re.search(r'Machine\s*:\s*(.+?)(?:\n|$)', description)
                    probleme_match = re.search(r'Problème\s*:\s*(.+?)(?:\n|$)', description)
                    urgence_match = re.search(r'Urgence\s*:\s*(\w+)', description)

                    if ligne_match:
                        ligne = ligne_match.group(1)
                    if machine_match:
                        machine = machine_match.group(1).strip()
                    if probleme_match:
                        probleme = probleme_match.group(1).strip()
                    if urgence_match:
                        urgence = urgence_match.group(1).strip()

                # Si on ne trouve pas les infos dans la description, essayer de parser le titre
                # Format titre : "MAINTENANCE - [Problème] - [Machine]"
                if machine == "?" and " - " in title:
                    parts = title.split(" - ")
                    if len(parts) >= 3:
                        probleme = parts[1].strip() if probleme == "?" else probleme
                        machine = parts[2].strip()

                interventions.append({
                    'ligne': ligne,
                    'machine': machine,
                    'probleme': probleme,
                    'urgence': urgence,
                    'date': date_str,
                    'heure_debut': heure_debut,
                    'heure_fin': heure_fin,
                    'titre': title
                })

            # 5. Formater la réponse
            response = f"Prochaines interventions de maintenance ({len(interventions)}) :\n\n"

            # Calculer les dates pour "aujourd'hui" et "demain"
            now_paris = datetime.datetime.now(paris_tz)
            aujourd_hui_str = now_paris.strftime('%d/%m/%Y')
            demain_str = (now_paris + datetime.timedelta(days=1)).strftime('%d/%m/%Y')

            for idx, inter in enumerate(interventions, 1):
                response += f"{idx}. Ligne {inter['ligne']} - {inter['machine']}\n"

                if inter['urgence'] != "?":
                    response += f"   Urgence : {inter['urgence']}\n"

                response += f"   Problème : {inter['probleme']}\n"

                # Remplacer la date par "aujourd'hui" ou "demain" si applicable
                date_display = inter['date']
                if inter['date'] == aujourd_hui_str:
                    date_display = "aujourd'hui"
                elif inter['date'] == demain_str:
                    date_display = "demain"

                response += f"   Date : {date_display}\n"

                if inter['heure_fin']:
                    response += f"   Horaire : {inter['heure_debut']} - {inter['heure_fin']}\n"
                else:
                    response += f"   Horaire : {inter['heure_debut']}\n"

                response += "\n"

            return response

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du planning de maintenance : {e}")
            import traceback
            traceback.print_exc()
            return f"Erreur lors de la récupération du planning : {str(e)}"
