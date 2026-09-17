"""
Central application configuration.

Everything that might change between machines (secrets, database location,
allowed frontend origins) lives here and is read from the .env file.
Nothing sensitive is ever hard-coded in the rest of the codebase.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------------
# Important paths, resolved relative to THIS file so the app works no matter
# which directory you launch it from.
#
#   config.py lives at:  <project>/backend/app/config.py
#   .parent            -> <project>/backend/app
#   .parent.parent     -> <project>/backend
#   .parent.parent.parent -> <project>            (PROJECT_ROOT)
# ---------------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

DATABASE_DIR = PROJECT_ROOT / "database"
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"

# Make sure these exist so nothing crashes on a fresh clone.
for _directory in (DATABASE_DIR, MODELS_DIR, DATA_DIR):
    _directory.mkdir(parents=True, exist_ok=True)

# .as_posix() keeps forward slashes, which SQLAlchemy prefers on Windows too.
DEFAULT_DB_URL = f"sqlite:///{(DATABASE_DIR / 'nutrition.db').as_posix()}"


class Settings(BaseSettings):
    """Application settings, populated from environment variables / .env."""

    # --- General ---
    APP_NAME: str = "AI-Powered Nutrition Intelligence System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # --- Security (Stage 2 uses these) ---
    SECRET_KEY: str = "insecure-development-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # --- Database ---
    DATABASE_URL: str = DEFAULT_DB_URL

    # --- CORS: which frontend origins may call this API ---
    # Stored as one comma-separated string because .env files hold plain text.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unrelated variables in the environment
    )

    @property
    def cors_origin_list(self) -> list[str]:
        """Turn the comma-separated CORS string into a clean Python list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


# A single shared instance imported everywhere else: `from .config import settings`
settings = Settings()