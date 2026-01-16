"""Module combinant toutes les fonctions de l'assistant."""
from orion.app.functions.base import BaseFunctions
from orion.app.functions.calendar import CalendarFunctions
from orion.app.functions.gmail import GmailFunctions
from orion.app.functions.contacts import ContactFunctions
from orion.app.functions.maintenance import MaintenanceFunctions


class AssistantFnc(
    CalendarFunctions,
    GmailFunctions,
    ContactFunctions,
    MaintenanceFunctions
):
    """Classe principale combinant toutes les fonctions de l'assistant."""
    pass
