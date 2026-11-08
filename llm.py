from __future__ import annotations

from typing import Any, Dict, List

import google.generativeai as genai

from config import Settings


_configured = False


def _configure_client(settings: Settings) -> None:
    """Configure the Gemini client once per process."""
    global _configured
    if not _configured:
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True


def get_model(settings: Settings) -> genai.GenerativeModel:
    """Return an initialized GenerativeModel instance."""
    _configure_client(settings)
    return genai.GenerativeModel(settings.gemini_model)


def generate_reply(history: List[Dict[str, Any]], settings: Settings) -> str:
    """Generate a reply from Gemini based on the full chat history."""
    model = get_model(settings)
    response = model.generate_content(history)
    text = getattr(response, "text", "") or ""
    return text.strip()

