"""Small SQLite repository for locally collected, permitted research snapshots."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from platformdirs import user_data_dir


class Database:
    """Manage the app database without storing Instagram passwords or session cookies."""

    def __init__(self, database_path: Path | None = None) -> None:
        # Keep writable data outside the installation directory for portable/locked installs.
        base_dir = Path(user_data_dir("InstagramResearchSuite", "IRS"))
        self.path = database_path or (base_dir / "research.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        """Return a configured SQLite connection with foreign keys enabled."""
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        """Create the version-one schema when the database is first opened."""
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_handle TEXT NOT NULL,
                    list_type TEXT NOT NULL CHECK(list_type IN ('followers', 'following')),
                    captured_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    completeness TEXT NOT NULL,
                    expected_count INTEGER,
                    retrieved_count INTEGER NOT NULL,
                    records_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_snapshots_account
                    ON snapshots(account_handle, list_type, captured_at);
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def save_snapshot(
        self,
        account_handle: str,
        list_type: str,
        records: list[dict[str, Any]],
        source: str = "manual-import",
        expected_count: int | None = None,
        completeness: str = "unknown",
    ) -> int:
        """Persist a snapshot and return its new ID; never label partial data as complete."""
        if list_type not in {"followers", "following"}:
            raise ValueError("list_type must be 'followers' or 'following'")
        if completeness not in {"complete", "partial", "unknown", "unavailable"}:
            raise ValueError("Unsupported completeness status")

        captured_at = datetime.now(UTC).isoformat()
        with self.connect() as connection:
            cursor = connection.execute(
                """INSERT INTO snapshots
                   (account_handle, list_type, captured_at, source, completeness,
                    expected_count, retrieved_count, records_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    account_handle.lstrip("@"), list_type, captured_at, source,
                    completeness, expected_count, len(records),
                    json.dumps(records, ensure_ascii=False),
                ),
            )
            return int(cursor.lastrowid)

    def list_snapshots(self, account_handle: str | None = None) -> list[dict[str, Any]]:
        """Return snapshot metadata, newest first, without loading all record payloads."""
        query = "SELECT * FROM snapshots"
        parameters: tuple[str, ...] = ()
        if account_handle:
            query += " WHERE account_handle = ?"
            parameters = (account_handle.lstrip("@"),)
        query += " ORDER BY captured_at DESC"
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(query, parameters).fetchall()]
