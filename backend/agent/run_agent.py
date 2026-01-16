from orion.app.agent import entrypoint
from livekit.agents import cli, WorkerOptions

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
