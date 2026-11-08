from __future__ import annotations

import logging
from typing import Any

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import ConfigError, Settings
from db import clear_user_history, get_user_history, init_database, save_message
from llm import generate_reply


logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user_id = update.effective_user.id
    db_path = context.application.bot_data["chat_db_path"]
    clear_user_history(db_path, user_id)

    greeting = (
        "👋 Привіт! Я — Solura AI Bot з постійною пам'яттю.\n\n"
        "Я запам'ятовую наш діалог у локальній базі даних SQLite. "
        "Щоб почати спочатку — надішли команду /clear 🚀"
    )
    await update.message.reply_text(greeting)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages with full history context."""
    db_path = context.application.bot_data["chat_db_path"]
    settings: Settings = context.application.bot_data["settings"]

    user_id = update.effective_user.id
    user_message = update.message.text

    save_message(db_path, user_id, user_message, "user")
    history = get_user_history(db_path, user_id)

    await update.message.chat.send_action(action="typing")

    try:
        ai_reply = generate_reply(history, settings=settings) or (
            "Вибачте, я отримав порожню відповідь від моделі. "
            "Спробуйте ще раз або трохи перефразуйте запит."
        )

        save_message(db_path, user_id, ai_reply, "model")
        await update.message.reply_text(ai_reply)
    except Exception as exc:  # noqa: BLE001
        logger.error("Помилка при зверненні до Gemini", exc_info=exc)
        await update.message.reply_text(
            "Вибачте, сталася помилка під час звернення до моделі. "
            "Спробуйте, будь ласка, пізніше."
        )


async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear chat history for current user (/clear)."""
    db_path = context.application.bot_data["chat_db_path"]
    user_id = update.effective_user.id

    clear_user_history(db_path, user_id)
    await update.message.reply_text("🗑️ Історію діалогу очищено!")


async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show last N messages for current user (/history)."""
    db_path = context.application.bot_data["chat_db_path"]
    user_id = update.effective_user.id

    history = get_user_history(db_path, user_id, limit=5)
    if not history:
        await update.message.reply_text("📝 Історія діалогу порожня!")
        return

    history_text_lines: list[str] = ["📖 Останні повідомлення:\n"]
    for msg in history:
        role_label = "👤 Ви" if msg["role"] == "user" else "🤖 Бот"
        parts = msg.get("parts") or [""]
        content = parts[0]
        history_text_lines.append(f"{role_label}: {content}\n")

    await update.message.reply_text("".join(history_text_lines))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler for the Telegram application."""
    logger.error("Виняток при обробці оновлення", exc_info=context.error)


def run() -> None:
    """Entry point for running the Telegram bot."""
    try:
        settings = Settings.load()
    except ConfigError as exc:
        print("❌ Configuration error for Solura AI Bot:")
        print(f"   {exc}")
        print("   Make sure you have a .env file based on .env.example.")
        return

    log_level_name = (settings.log_level or "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=log_level,
    )

    logger.info("Starting Solura AI Bot (Telegram)...")

    init_database(settings.chat_db_path)

    application = ApplicationBuilder().token(settings.telegram_token).build()
    application.bot_data["chat_db_path"] = settings.chat_db_path
    application.bot_data["settings"] = settings

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_history))
    application.add_handler(CommandHandler("history", show_history))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)

    print("🤖 Solura AI Bot is running...")
    print(f"💾 Chat history DB: {settings.chat_db_path}")
    application.run_polling()

