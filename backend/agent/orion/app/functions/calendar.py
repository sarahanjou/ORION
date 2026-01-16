"""Fonctions concernant l'API Google Calendar."""
from __future__ import annotations

import os
import logging
import datetime
import urllib.parse
import webbrowser
from typing import Annotated, Optional

from orion.utils.dates import paris_tz
from orion.services.google.auth import service
from orion.app.functions.base import BaseFunctions, llm

logger = logging.getLogger(__name__)


class CalendarFunctions(BaseFunctions):
    """Fonctions pour gérer les événements Google Calendar."""

    @llm.ai_callable()
    async def add_event(
        self,
        calendar_name: Annotated[
            str, 
            llm.TypeInfo(description="The calendar to add the event to")
        ],
        title: Annotated[
            str, 
            llm.TypeInfo(description="The title of the event")
        ],
        start_time: Annotated[
            str, 
            llm.TypeInfo(description="The start time of the event in HH:MM format")
        ],
        end_time: Annotated[
            str, 
            llm.TypeInfo(description="The end time of the event in HH:MM format")
        ],
        date: Annotated[
            str, 
            llm.TypeInfo(description="The date of the event")
        ],
        open_in_browser: Annotated[
            Optional[bool],
            llm.TypeInfo(description="If true, open the created event in the browser")
        ] = True,
    ):
        """
        Creates an event in Google Calendar.

        Args:
            calendar_name (str): The name of the calendar to add the event to.
            title (str): The title of the event.
            date (str): The date of the event in the format 'YYYY-MM-DD'.
            start_time (str): The start time of the event in the format 'HH:MM'.
            end_time (str): The end time of the event in the format 'HH:MM'.
        """
        logger.info(f"Creating event in calendar: {calendar_name}")
        
        try:
            calendar_id = os.getenv(calendar_name)
            if not calendar_id:
                raise ValueError(f"L'ID pour le calendrier {calendar_name} n'a pas été trouvé.")
            
            if (start_time == "00:00" and end_time == "23:59"):
                event_body = {
                    "summary": title,
                    "start": {"date": date},
                    "end": {"date": date}
                }
            else:
                event_body = {
                    "summary": title,
                    "start": {"dateTime": f"{date}T{start_time}:00", "timeZone": "Europe/Paris"},
                    "end": {"dateTime": f"{date}T{end_time}:00", "timeZone": "Europe/Paris"},
                }

            # Envoyer l'événement à google calendar
            created_event = service['calendar'].events().insert(
                calendarId=calendar_id, 
                body=event_body
            ).execute()
            event_link = created_event.get("htmlLink", "No link available")

            logger.info(f"L'événement a bien été créé ! {event_link}")
            if open_in_browser and isinstance(event_link, str) and event_link.startswith("http"):
                try:
                    webbrowser.open(event_link)
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir le navigateur pour l'événement: {e}")
            return f"L'événement {title} a été créé avec succès : {event_link}"
        
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'événement : {e}")
            return f"Erreur lors de la création de l'événement : {str(e)}"

    @llm.ai_callable()
    async def list_event(
        self,
        calendar_name: Annotated[
            str,
            llm.TypeInfo(description="The calendar to list the events from")
        ],
        date: Annotated[
            str,
            llm.TypeInfo(description="The date of the day of the events to list")
        ],
        open_in_browser: Annotated[
            Optional[bool],
            llm.TypeInfo(description="If true, open the calendar day view in the browser")
        ] = True,
    ):
        """
        Lists the events from a calendar on a specific day.

        Args:
            calendar_name (str): The name of the calendar to list events from.
            date (str): The date of the events to list in the format 'YYYY-MM-DD'.
        """
        try:
            calendar_id = os.getenv(calendar_name)
            if not calendar_id:
                logger.error(f"L'ID pour le calendrier '{calendar_name}' n'a pas été trouvé.")
                raise ValueError(f"L'ID pour le calendrier '{calendar_name}' n'a pas été trouvé.")
            
            date_obj = datetime.datetime.fromisoformat(date).replace(tzinfo=paris_tz)

            start_time = date_obj.replace(hour=0, minute=0, second=1).isoformat()
            end_time = date_obj.replace(hour=23, minute=59, second=59).isoformat()
            
            calendar_results = service['calendar'].events().list(
                calendarId=calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            items = calendar_results.get('items', [])

            logger.info(f"items :: {items}")

            if not items:
                return f"Aucun événement trouvé pour le calendrier {calendar_name} le {date}."

            # Construire une réponse lisible
            response = f"Événements trouvés pour le calendrier {calendar_name} le {date} :\n"
            for event in items:
                event_title = event.get("summary", "Sans titre")

                # Gestion de l'heure de début
                start = event["start"].get("dateTime", event["start"].get("date", "Inconnu"))
                if start.endswith("Z"):
                    start_dt = datetime.datetime.fromisoformat(start.replace("Z", ""))
                    start_dt = start_dt.replace(tzinfo=datetime.timezone.utc).astimezone(paris_tz)
                else:
                    start_dt = datetime.datetime.fromisoformat(start).astimezone(paris_tz)

                # Formatage de l'heure
                formatted_start_time = start_dt.strftime("%H:%M")

                # Gestion de l'heure de fin (si présente)
                end = event["end"].get("dateTime", event["end"].get("date", "Inconnu"))
                if end.endswith("Z"):
                    end_dt = datetime.datetime.fromisoformat(end.replace("Z", ""))
                    end_dt = end_dt.replace(tzinfo=datetime.timezone.utc).astimezone(paris_tz)
                else:
                    end_dt = datetime.datetime.fromisoformat(end).astimezone(paris_tz)

                formatted_end_time = end_dt.strftime("%H:%M")

                response += f"- {event_title} (Début : {formatted_start_time}, Fin : {formatted_end_time})\n"

            # Optionally open the calendar day view
            if open_in_browser:
                try:
                    # Build a link to Google Calendar day view for the specified date and calendar
                    date_obj_url = datetime.datetime.fromisoformat(date)
                    cal_url = (
                        f"https://calendar.google.com/calendar/u/0/r/day/"
                        f"{date_obj_url.year}/{date_obj_url.month:02d}/{date_obj_url.day:02d}?cid="
                        f"{urllib.parse.quote(calendar_id)}"
                    )
                    webbrowser.open(cal_url)
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir la vue jour du calendrier: {e}")

            return response
        
        except Exception as e:
            logger.error(f"Erreur lors du listage des événements : {e}")
            return f"Erreur lors du listage des événements : {str(e)}"

    @llm.ai_callable()
    async def delete_event(
        self,
        calendar_name: Annotated[
            str, 
            llm.TypeInfo(description="The calendar to delete the event from")
        ],
        title: Annotated[
            str, 
            llm.TypeInfo(description="The title of the event to delete")
        ],
        start_time: Annotated[
            str, 
            llm.TypeInfo(description="The start time of the event to delete in HH:MM format")
        ],
        end_time: Annotated[
            str,
            llm.TypeInfo(description="The end time of the event to delete in HH:MM format")
        ],
        date: Annotated[
            str, 
            llm.TypeInfo(description="The date of the event to delete")
        ],
        open_in_browser: Annotated[
            Optional[bool],
            llm.TypeInfo(description="If true, open the calendar day view in the browser")
        ] = True,
    ):
        """
        Deletes an event in Google Calendar.

        Args:
            calendar_name (str): The name of the calendar to delete the event from.
            title (str): The title of the event to delete.
            date (str): The date of the event to delete in the format 'YYYY-MM-DD'.
            start_time (str): The start time of the event to delete in the format 'HH:MM'.
            end_time (str): The end time of the event to delete in the format 'HH:MM'.
        """
        logger.info(f"Deleting event in calendar: {calendar_name}, {title}, {date}, {start_time}, {end_time}")

        try:
            calendar_id = os.getenv(calendar_name)
            logger.info(f"ID du calendrier : {calendar_id}")
            if not calendar_id:
                raise ValueError(f"L'ID pour le calendrier {calendar_name} n'a pas été trouvé.")
            
            date_obj = datetime.datetime.fromisoformat(date).replace(tzinfo=paris_tz)

            start_time_list = date_obj.replace(hour=0, minute=0, second=1).isoformat()
            end_time_list = date_obj.replace(hour=23, minute=59, second=59).isoformat()

            events_result = service['calendar'].events().list(
                calendarId=calendar_id,
                timeMin=start_time_list,
                timeMax=end_time_list,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            logger.info(f"Resultat liste evenement : {events_result}")

            events = events_result.get('items', [])

            logger.info(f"Événements trouvés : {events}")

            if not events:
                return f"Aucun événement trouvé pour le calendrier '{calendar_name}' à la date {date}."

            deleted = False

            for event in events:
                event_start_time = event.get("start", {}).get("dateTime", "").split("T")[1][:5]
                event_end_time = event.get("end", {}).get("dateTime", "").split("T")[1][:5]

                event_id = event.get('id')
                event_title = event.get("summary", "")
                
                if event_title.strip().lower() == title.strip().lower():
                    # Suppression de l'événement
                    service['calendar'].events().delete(calendarId=calendar_id, eventId=event_id).execute()
                    deleted = True
                    logger.info(f"Événement supprimé : {title}")
    
            if deleted:
                if open_in_browser:
                    try:
                        date_obj_url = datetime.datetime.fromisoformat(date)
                        cal_url = (
                            f"https://calendar.google.com/calendar/u/0/r/day/"
                            f"{date_obj_url.year}/{date_obj_url.month:02d}/{date_obj_url.day:02d}?cid="
                            f"{urllib.parse.quote(calendar_id)}"
                        )
                        webbrowser.open(cal_url)
                    except Exception as e:
                        logger.warning(f"Impossible d'ouvrir la vue jour du calendrier: {e}")
                return f"Événement '{title}' supprimé avec succès."
            else:
                return f"L'événement '{title}' n'a pas pu être supprimé."

        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'événement : {e}")
            return f"Erreur lors de la suppression de l'événement : {str(e)}"
