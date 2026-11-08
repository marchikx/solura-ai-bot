from __future__ import annotations

import sys

import google.generativeai as genai

from config import ConfigError, Settings


def main() -> int:
    """Minimal healthcheck for the Gemini API configuration."""
    try:
        settings = Settings.load()
    except ConfigError as exc:
        print("❌ Configuration error for Solura AI Bot:")
        print(f"   {exc}")
        print("   Make sure you have a .env file based on .env.example.")
        return 1

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        response = model.generate_content(
            "Healthcheck: please respond with a short greeting."
        )
        text = getattr(response, "text", "") or ""
        print("✅ Gemini API is reachable.")
        print(f"   Model: {settings.gemini_model}")
        print(f"   Response: {text.strip() or '<empty response>'}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print("❌ Gemini API test failed:")
        print(f"   {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())