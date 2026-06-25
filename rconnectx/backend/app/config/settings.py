from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "RConnectX API"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    FRONTEND_URL: str = "http://localhost:3000"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nexus"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REFRESH_TOKEN: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = ""

    # Email
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@nexus.dev"

    # External APIs
    GNEWS_API_KEY: str = ""
    DEVTO_API_KEY: str = ""

    # Cloudinary (persistent media storage)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_FOLDER: str = "rconnectx"

    # Push notifications — Web Push API (VAPID). No Firebase.
    VAPID_PUBLIC_KEY: str = ""
    VAPID_PRIVATE_KEY: str = ""
    VAPID_CLAIMS_EMAIL: str = "mailto:admin@rconnectx.com"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def github_redirect_uri(self) -> str:
        """OAuth callback URL sent to GitHub. Must match the GitHub app settings."""
        localhost = "http://localhost:3000/github/callback"
        explicit = (self.GITHUB_REDIRECT_URI or "").strip().rstrip("/")

        if explicit and explicit != localhost.rstrip("/"):
            return explicit

        frontend = (self.FRONTEND_URL or "").strip().rstrip("/")
        if frontend and frontend != "http://localhost:3000":
            return f"{frontend}/github/callback"

        production_origin = self._production_frontend_origin()
        if production_origin:
            return f"{production_origin}/github/callback"

        return localhost

    def _production_frontend_origin(self) -> str | None:
        https_origins = [o.rstrip("/") for o in self.cors_origins_list if o.startswith("https://")]
        if not https_origins:
            return None
        www_origin = next((o for o in https_origins if "://www." in o), None)
        return www_origin or https_origins[0]


@lru_cache
def get_settings() -> Settings:
    return Settings()
