from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Load environment variables from a local .env file if present.
# This is safe in production because real deployments can override
# values via the environment.
load_dotenv()


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    """Typed configuration for the Solura AI Bot."""

    telegram_token: str
    gemini_api_key: str
    gemini_model: str
    chat_db_path: str
    log_level: str

    @classmethod
    def load(cls) -> "Settings":
        """Load settings from environment variables.

        Required:
        - TELEGRAM_TOKEN
        - GEMINI_API_KEY

        Optional:
        - GEMINI_MODEL (default: models/gemini-1.5-flash-latest)
        - CHAT_DB_PATH (default: chat_history.db)
        - LOG_LEVEL (default: INFO)
        """

        def required(name: str) -> str:
            value = os.getenv(name)
            if not value:
                raise ConfigError(
                    f"Environment variable {name} is not set. "
                    "Create a .env file in the project root based on .env.example "
                    "or export the variable in your shell."
                )
            return value

        return cls(
            telegram_token=required("TELEGRAM_TOKEN"),
            gemini_api_key=required("GEMINI_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL", "models/gemini-1.5-flash-latest"),
            chat_db_path=os.getenv("CHAT_DB_PATH", "chat_history.db"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

