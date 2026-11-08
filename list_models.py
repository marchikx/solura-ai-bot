from __future__ import annotations

import google.generativeai as genai

from config import ConfigError, Settings


def main() -> None:
    """Utility script to list available Gemini models for this API key."""
    try:
        settings = Settings.load()
    except ConfigError as exc:
        print("❌ Configuration error for Solura AI Bot:")
        print(f"   {exc}")
        print("   Make sure you have a .env file based on .env.example.")
        return

    try:
        genai.configure(api_key=settings.gemini_api_key)

        print("Доступні моделі Gemini (що підтримують generateContent):")
        for model in genai.list_models():
            if "generateContent" in getattr(
                model, "supported_generation_methods", []
            ):
                print(f"- {model.name}")
    except Exception as exc:  # noqa: BLE001
        print("❌ Помилка при отриманні списку моделей:")
        print(f"   {exc}")


if __name__ == "__main__":
    main()