import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Application configuration, sourced from the environment where possible."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-local-development-key")
    database_url = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"
    SQLALCHEMY_DATABASE_URI = database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    INCIDENT_RISK_THRESHOLD = int(os.getenv("INCIDENT_RISK_THRESHOLD", "65"))
    MAX_METRICS_PER_SERVER = int(os.getenv("MAX_METRICS_PER_SERVER", "500"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
