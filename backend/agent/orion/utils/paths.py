from pathlib import Path
import os


def find_project_root(start: Path | None = None) -> Path:
    env_root = os.getenv("ORION_PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()

    if start is None:
        start = Path.cwd()
    cur = start.resolve()

    while cur.parent != cur:
        if (cur / ".root").exists():
            return cur
        # Repo-specific fallback: treat agent as root
        if (cur / "agent").exists():
            return (cur / "agent").resolve()
        cur = cur.parent

    # Last resort: assume this file lives under agent/orion/utils/paths.py
    return Path(__file__).resolve().parents[2]


def get_project_root() -> Path:
    if not hasattr(get_project_root, "_cache"):
        get_project_root._cache = find_project_root()
    return get_project_root._cache


def path_in_project(*parts: str) -> Path:
    return get_project_root().joinpath(*parts)


def get_env_path() -> Path:
    """
    Retourne le chemin du fichier .env centralisé.
    Cherche d'abord dans backend/.env, puis dans config/.env pour compatibilité.
    """
    # Chercher dans le répertoire backend (racine du projet backend)
    # Si ce fichier est dans backend/agent/orion/utils/paths.py:
    # parents[0] = utils/, parents[1] = orion/, parents[2] = agent/, parents[3] = backend/
    backend_root = Path(__file__).resolve().parents[3]
    backend_env = backend_root / ".env"
    if backend_env.exists():
        return backend_env
    
    # Dernier recours: retourner le chemin backend/.env même s'il n'existe pas
    return backend_env


def get_secrets_dir() -> Path:
    """Retourne le répertoire des secrets (backend/secrets/)."""
    # Utiliser la variable d'environnement si définie
    env_secrets_dir = os.getenv("ORION_SECRETS_DIR")
    if env_secrets_dir:
        return Path(env_secrets_dir).resolve()
    
    # Sinon, chercher dans backend/secrets/ (pas dans agent/secrets/)
    # Si ce fichier est dans backend/agent/orion/utils/paths.py:
    # parents[0] = utils/, parents[1] = orion/, parents[2] = agent/, parents[3] = backend/
    backend_root = Path(__file__).resolve().parents[3]
    secrets_dir = backend_root / "secrets"
    return secrets_dir


def get_credentials_path() -> Path:
    return Path(os.getenv("GOOGLE_CREDENTIALS_PATH", get_secrets_dir() / "credentials.json"))


def get_token_path() -> Path:
    return Path(os.getenv("GOOGLE_TOKEN_PATH", get_secrets_dir() / "token.json"))


