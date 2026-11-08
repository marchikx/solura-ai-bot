from __future__ import annotations

import sqlite3
from typing import Any, Dict, List


def init_database(db_path: str) -> None:
    """Initialize the SQLite database used for chat history."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            role TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def save_message(db_path: str, user_id: int, message: str, role: str) -> None:
    """Persist a single message to the chat history."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chat_history (user_id, message, role) VALUES (?, ?, ?)",
        (user_id, message, role),
    )

    conn.commit()
    conn.close()


def get_user_history(
    db_path: str, user_id: int, limit: int = 10
) -> List[Dict[str, Any]]:
    """Return recent history for a user in a format suitable for Gemini."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, message
        FROM chat_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (user_id, limit * 2),  # *2 because messages come in user/model pairs
    )

    rows = cursor.fetchall()
    conn.close()

    history: List[Dict[str, Any]] = []
    for role, message in reversed(rows):  # chronological order
        history.append({"role": role, "parts": [message]})

    return history


def clear_user_history(db_path: str, user_id: int) -> None:
    """Delete all messages for a given user."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

