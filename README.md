# Solura AI Bot (Telegram + Gemini)

[![CI](https://github.com/marchikx/solura-ai-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/marchikx/solura-ai-bot/actions/workflows/ci.yml) ![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)

Professional, production-ready Telegram assistant powered by Google Gemini with persistent chat history in SQLite.  
Built as an AI-augmented backend project (Cursor + LLMs) and then refactored and hardened for portfolio use.

## Demo

- **Local preview:** `python test_api.py` (Gemini healthcheck) — console output is the offline demo; Telegram UI requires your BotFather token in `.env`.
- **Screenshot / flow:** `/start` → chat message → SQLite-backed reply with context (see `telegram_bot.py` handlers).

---

## What It Does

- 🔁 **Conversational Telegram bot** – friendly chat interface powered by Gemini (`gemini-1.5-flash` by default).
- 🧠 **Long-term memory** – stores the full dialog in **SQLite** so the model can answer in context.
- 🔐 **Environment-based config** – all secrets (Telegram token, Gemini API key) are taken from `.env`, never hard-coded.
- 🧪 **API healthcheck tools** – simple scripts to verify Gemini connectivity and list available models.
- 🏗️ **Clean, extensible architecture** – separated config, database, LLM client, and Telegram adapter for future channels.

---

## Trade-offs

- **SQLite memory** — simple ops for a portfolio bot; not multi-instance HA without external DB.
- **Gemini via env** — easy swap of model/key; vendor lock-in to Google unless you replace `llm.py`.
- **Long polling Telegram** — no webhook server required locally; production often prefers webhook + HTTPS.

---

## Project Structure

```text
solura_ai_bot/
  bot.py               # Simple entrypoint that runs the Telegram bot
  telegram_bot.py      # Bot engine: handlers, routing, logging, wiring
  config.py            # Typed configuration loaded from .env (with safety checks)
  db.py                # SQLite-based chat history (init, save, fetch, clear)
  llm.py               # Gemini client wrapper and reply generation

  test_api.py          # Minimal Gemini healthcheck (uses same config as the bot)
  list_models.py       # Utility: list available Gemini models for your API key

  .env.example         # Example configuration (copy to .env and edit)
  .gitignore           # Ignores env files, DB, venv, IDE, etc.
  requirements.txt     # Python dependencies
  README.md            # This file
```

This layout makes it easy to:

- Reuse the **core engine** (`config.py`, `db.py`, `llm.py`) across multiple frontends.
- Swap or upgrade LLM providers (Gemini model is configured via env).
- Add additional adapters later (Discord/Slack/web) without touching the core logic.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/solura-ai-bot.git
cd solura-ai-bot
```

### 2. Create a virtual environment & install dependencies

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root based on `.env.example`:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key

GEMINI_MODEL=models/gemini-1.5-flash-latest
CHAT_DB_PATH=chat_history.db
LOG_LEVEL=INFO
```

> `.env` is **ignored by git** and must never be committed.  
> The example file `.env.example` is safe to share.

### 4. Run healthcheck (recommended)

Before running the bot, verify that the Gemini API is reachable and your key works:

```bash
python test_api.py
```

Expected output:

- On success: a ✅ message with the model name and a short text reply.
- On failure: a clear ❌ message explaining what went wrong (missing env vars, network/API error, etc.) instead of a raw traceback.

You can also inspect supported models:

```bash
python list_models.py
```

### 5. Run the Telegram bot

```bash
python bot.py
```

You should see console logs similar to:

```text
🤖 Solura AI Bot is running...
💾 Chat history DB: chat_history.db
```

Open your Telegram bot (configured via BotFather) and start chatting.

---

## Telegram Commands & Behavior

- `/start` – resets your personal history and sends a welcome message.
- `/clear` – clears all stored messages for your Telegram user (full reset).
- `/history` – shows the last messages in the conversation (as seen by the model).
- Plain text – any regular message is passed to Gemini with your **full stored history** as context.

Notes:

- Each user has an isolated history stored in SQLite (`chat_history.db` by default).
- The bot shows Telegram “typing…” while the model generates a response.
- Errors from the LLM are logged and surfaced to the user as a friendly message instead of a crash.

---

## Configuration Details

All configuration is centralized in `config.py` and loaded via the `Settings` dataclass:

- `TELEGRAM_TOKEN` – Telegram bot token (BotFather).
- `GEMINI_API_KEY` – Google Gemini API key.
- `GEMINI_MODEL` – model name, e.g. `models/gemini-1.5-flash-latest`.
- `CHAT_DB_PATH` – path to the SQLite database file (default: `chat_history.db`).
- `LOG_LEVEL` – one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

If a required variable is missing, the bot and helper scripts fail with a **clear configuration error** and instructions to create `.env`, instead of throwing an opaque stack trace.

---

## Safety, Secrets & Production Notes

- `.env`, `Key.env` and any other secret-bearing files are **ignored via `.gitignore`**.
- The SQLite database (`chat_history.db`) is also ignored, so no real user data is ever committed.
- All external tokens and model names are configured via environment variables, so you can:
  - Run locally with `.env`.
  - Deploy to production via Docker/Kubernetes/CI by injecting env vars.

For a portfolio or open-source setup:

- Commit only `.env.example` with placeholder values.
- Never paste real keys into code, README, or commit messages.

---

## AI-Augmented Development Notes

This project was refactored using an AI-augmented workflow (Cursor + LLMs) and then manually reviewed:

- **Architecture first** – split into config, DB, LLM client, and Telegram adapter before touching code.
- **Security by design** – secrets are strictly env-based; local DB and env files are excluded from git.
- **Operational clarity** – dedicated healthcheck script (`test_api.py`) and explicit logging configuration.

The goal is to demonstrate how I combine LLM tooling with traditional backend practices (SQLite schema, error handling, logging) to get both **speed** and **control**.

---

## Roadmap

These are intentional next steps that would turn this into a more full-featured “Solura-style” assistant:

1. **Multi-channel engine**
   - Extract a generic conversation engine and add adapters for:
     - Telegram (current)
     - Discord / Slack
     - Simple web chat (FastAPI + WebSocket)

2. **Knowledge / RAG mode**
   - Allow uploading PDF/Markdown/FAQ files and build a lightweight RAG layer (even via external APIs).
   - Store and query business-specific knowledge so answers are grounded in the client’s docs.

3. **Integrations with CRM / Notion**
   - Log all conversations and qualified leads to Notion, Google Sheets or a lightweight CRM.
   - Mark high-intent contacts for follow-up by a human sales team.

4. **Operator handoff**
   - When the model is uncertain (low score / fallback intents):
     - Ask the user for email/Telegram handle.
     - Create a “ticket” in a table/CRM.
     - Notify the operator (you) via a dedicated Telegram channel.

5. **White-label configuration**
   - Centralize branding in config (`BOT_NAME`, `COMPANY_NAME`, `PRIMARY_LANGUAGE`, etc.).
   - Make it easy to spin up separate, branded bots (per small business) by just changing `.env` or a `config.yaml`.

---

## How to Use This in Your Portfolio

- The repository is structured similarly to my other production-style projects:
  - Clear entrypoint (`bot.py`).
  - Explicit dependencies (`requirements.txt`).
  - Strict secret handling (`.env.example` + `.gitignore`).
  - Minimal but practical tooling (`test_api.py`, `list_models.py`).
- It showcases:
  - Telegram + LLM integration.
  - Persistent memory via SQLite.
  - Clean separation of concerns suitable for extension into a multi-channel AI assistant.

You can point technical leads directly to this repo as a compact but realistic example of how you structure AI-powered backend services.

## Tests

```bash
make verify
```

Offline unit tests cover configuration validation and SQLite history (no Telegram or Gemini API calls).

## License

MIT — see [LICENSE](LICENSE).

