"""Point d'entrée principal de l'agent Orion."""
from __future__ import annotations

import logging
from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai

from orion.prompts.orion import orion_prompt_system
from orion.utils.paths import get_env_path
from orion.app.functions import AssistantFnc

# Configuration des logs : DEBUG pour voir les échanges détaillés
logging.basicConfig(level=logging.DEBUG)

# Charge le fichier d'env via utilitaire
load_dotenv(dotenv_path=str(get_env_path()))
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def entrypoint(ctx: JobContext):
    """Fonction d'entrée principale pour démarrer l'agent."""
    logger.info("=" * 60)
    logger.info("ENTRYPOINT - Job reçu!")
    logger.info(f"   Room: {ctx.room.name}")
    logger.info(f"   Job ID: {getattr(ctx.job, 'job_id', 'N/A')}")
    logger.info("=" * 60)

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    logger.info("Connecté à la room LiveKit")
    logger.info(f"   Participants dans la room: {len(ctx.room.remote_participants)}")
    
    # Logger quand un participant se connecte
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logger.info(f"Participant connecté: {participant.identity}")
        # Compter les publications audio (pas audio_tracks qui n'existe pas)
        audio_pubs = [p for p in participant.track_publications.values() if p.kind == rtc.TrackKind.KIND_AUDIO]
        logger.info(f"   Audio publications: {len(audio_pubs)}")
    
    def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            logger.info(f"Audio track souscrit de {participant.identity} - L'agent peut maintenant entendre!")
    
    def on_track_published(publication: rtc.TrackPublication, participant: rtc.Participant):
        if publication.kind == rtc.TrackKind.KIND_AUDIO:
            logger.info(f"Track audio publié par {participant.identity} - L'agent parle maintenant!")
    
    ctx.room.on("participant_connected", on_participant_connected)
    ctx.room.on("track_subscribed", on_track_subscribed)
    ctx.room.on("track_published", on_track_published)

    fnc_ctx = AssistantFnc()

    model = openai.realtime.RealtimeModel(
        instructions=orion_prompt_system(),
        voice="marin",
        temperature=0.6,
        modalities=["audio", "text"],
    )

    assistant = MultimodalAgent(model=model, fnc_ctx=fnc_ctx)
    assistant.start(ctx.room)

    logger.info("Agent multimodal démarré et prêt à recevoir l'audio")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="orion-assistant",
        )
    )
