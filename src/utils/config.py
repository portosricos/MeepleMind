import os
from pathlib import Path

# Project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Data directory paths
RAW_DATA_DIR = PROJECT_ROOT / "raw_data"
PROCESSED_DATA_PATH = PROJECT_ROOT / "processed_games.pkl"
ENV_PATH = PROJECT_ROOT / ".env"

def get_bgg_api_token() -> str:
    """Retrieve BGG API Token from environment variables or .env file."""
    token = os.getenv("BGG_API_TOKEN")
    if not token and ENV_PATH.exists():
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("BGG_API_TOKEN="):
                        token = line.split("=", 1)[1].strip()
                        break
        except Exception:
            pass
    return token if token else ""
