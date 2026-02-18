"""Session management for goopenbot."""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

from .config import get_data_dir

console = Console()


class Session:
    """Represents a conversation session."""

    def __init__(
        self,
        id: str,
        created_at: str,
        updated_at: str,
        messages: list[dict[str, Any]],
        model: str,
    ):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.messages = messages
        self.model = model

    @classmethod
    def create(cls, model: str = "llama3") -> "Session":
        """Create a new session."""
        now = datetime.now().isoformat()
        return cls(
            id=str(uuid.uuid4()),
            created_at=now,
            updated_at=now,
            messages=[],
            model=model,
        )

    @classmethod
    def from_row(cls, row: tuple) -> "Session":
        """Create a session from a database row."""
        return cls(
            id=row[0],
            created_at=row[1],
            updated_at=row[2],
            messages=json.loads(row[3]) if row[3] else [],
            model=row[4],
        )

    def to_row(self) -> tuple:
        """Convert to database row."""
        return (
            self.id,
            self.created_at,
            self.updated_at,
            json.dumps(self.messages),
            self.model,
        )

    def add_message(self, role: str, content: str, tool_calls: Optional[list] = None):
        """Add a message to the session."""
        message: dict[str, Any] = {"role": role, "content": content}
        if tool_calls:
            message["tool_calls"] = tool_calls
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()

    def add_tool_result(self, tool_call_id: str, content: str):
        """Add a tool result message."""
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": content,
            }
        )
        self.updated_at = datetime.now().isoformat()


class SessionStore:
    """SQLite-based session storage."""

    def __init__(self):
        self.db_path = get_data_dir() / "sessions.db"
        self._init_db()

    def _init_db(self):
        """Initialize the database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                messages TEXT,
                model TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    def save(self, session: Session):
        """Save a session to the database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO sessions (id, created_at, updated_at, messages, model)
            VALUES (?, ?, ?, ?, ?)
            """,
            session.to_row(),
        )
        conn.commit()
        conn.close()

    def get(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT id, created_at, updated_at, messages, model FROM sessions WHERE id = ?",
            (session_id,),
        )
        row = cursor.fetchone()
        conn.close()
        return Session.from_row(row) if row else None

    def get_latest(self) -> Optional[Session]:
        """Get the most recent session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT id, created_at, updated_at, messages, model FROM sessions ORDER BY updated_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()
        return Session.from_row(row) if row else None

    def list(self, limit: int = 10) -> list[Session]:
        """List all sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT id, created_at, updated_at, messages, model FROM sessions ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [Session.from_row(row) for row in rows]

    def delete(self, session_id: str):
        """Delete a session."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()
