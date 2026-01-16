"""Classe de base pour toutes les fonctions de l'assistant."""
from livekit.agents import llm
import logging

logger = logging.getLogger(__name__)

# Réexporter llm pour faciliter les imports dans les modules enfants
__all__ = ['BaseFunctions', 'llm']


class BaseFunctions(llm.FunctionContext):
    """Classe de base pour toutes les fonctions de l'assistant."""
    pass
