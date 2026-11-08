from __future__ import annotations

import os
import tempfile

import db


def test_init_and_history_roundtrip() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "chat.db")
        db.init_database(path)
        db.save_message(path, user_id=42, message="hello", role="user")
        db.save_message(path, user_id=42, message="hi there", role="model")
        history = db.get_user_history(path, user_id=42, limit=5)
        assert len(history) == 2
        by_role = {row["role"]: row["parts"][0] for row in history}
        assert by_role["user"] == "hello"
        assert by_role["model"] == "hi there"


def test_clear_user_history() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "chat.db")
        db.init_database(path)
        db.save_message(path, user_id=7, message="x", role="user")
        db.clear_user_history(path, user_id=7)
        assert db.get_user_history(path, user_id=7, limit=5) == []
