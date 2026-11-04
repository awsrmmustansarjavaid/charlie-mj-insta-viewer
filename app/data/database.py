"""SQLite persistence: snapshots, events, mentions, monitors, settings, downloads."""

from __future__ import annotations

import json
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from app.providers.base import Account

SCHEMA_VERSION = 2

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS profiles (
    username TEXT PRIMARY KEY, display_name TEXT, bio TEXT, followers_count INTEGER,
    following_count INTEGER, posts_count INTEGER, avatar TEXT, account_type TEXT,
    visibility TEXT, verified INTEGER, fetched_at TEXT, provider TEXT,
    notes TEXT DEFAULT '', collection TEXT DEFAULT '', tags TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS profile_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, created_at TEXT NOT NULL,
    data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT, profile TEXT NOT NULL, list_type TEXT NOT NULL,
    created_at TEXT NOT NULL, source TEXT NOT NULL, complete INTEGER NOT NULL,
    expected_count INTEGER, returned_count INTEGER NOT NULL, label TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS snapshot_accounts (
    snapshot_id INTEGER NOT NULL, username TEXT NOT NULL, display_name TEXT,
    account_type TEXT, visibility TEXT, verified INTEGER, followed_at TEXT, profile_url TEXT,
    PRIMARY KEY (snapshot_id, username),
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_snap_profile ON snapshots(profile, list_type, id);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, profile TEXT NOT NULL, kind TEXT NOT NULL,
    detail TEXT NOT NULL, detected_at TEXT NOT NULL, dedupe_key TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, profile TEXT NOT NULL, source_type TEXT NOT NULL,
    by_user TEXT NOT NULL, mentioned_user TEXT NOT NULL, ref TEXT NOT NULL, preview TEXT,
    posted_at TEXT, detected_at TEXT NOT NULL,
    UNIQUE(profile, source_type, by_user, mentioned_user, ref)
);
CREATE TABLE IF NOT EXISTS post_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT, profile TEXT NOT NULL, post_id TEXT NOT NULL,
    taken_at TEXT NOT NULL, likes INTEGER, comments_count INTEGER
);
CREATE TABLE IF NOT EXISTS seen_items (
    profile TEXT NOT NULL, kind TEXT NOT NULL, item_id TEXT NOT NULL, first_seen TEXT NOT NULL,
    PRIMARY KEY (profile, kind, item_id)
);
CREATE TABLE IF NOT EXISTS monitors (
    profile TEXT PRIMARY KEY, interval_minutes INTEGER NOT NULL DEFAULT 60,
    enabled INTEGER NOT NULL DEFAULT 1, priority INTEGER NOT NULL DEFAULT 5,
    last_run TEXT, next_run TEXT, last_status TEXT DEFAULT 'never run',
    consecutive_errors INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, kind TEXT NOT NULL,
    title TEXT NOT NULL, body TEXT, is_read INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT, profile TEXT, item_id TEXT, kind TEXT, path TEXT,
    created_at TEXT NOT NULL, status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT, query TEXT NOT NULL, created_at TEXT NOT NULL
);
"""


def now() -> str:
    """UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    """Owns the SQLite file. A new short-lived connection per operation keeps
    it safe to use from worker threads."""

    def __init__(self, path: Path):
        self.path = Path(path)

    # -- connection -----------------------------------------------------------
    @contextmanager
    def conn(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    # kept for backwards compatibility with the starter release
    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        """Create or migrate the schema."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.conn() as c:
            version = c.execute("PRAGMA user_version").fetchone()[0]
            if version == 1:  # starter-release layout: rebuild snapshot tables
                c.executescript("DROP TABLE IF EXISTS snapshot_accounts; DROP TABLE IF EXISTS snapshots;")
            c.execute("PRAGMA journal_mode = WAL")
            c.executescript(SCHEMA)
            c.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    def integrity_check(self) -> str:
        """Return 'ok' or a description of the problem."""
        with self.conn() as c:
            return str(c.execute("PRAGMA integrity_check").fetchone()[0])

    def vacuum(self) -> None:
        c = sqlite3.connect(self.path)
        try:
            c.execute("VACUUM")
        finally:
            c.close()

    # -- settings -------------------------------------------------------------
    def save_setting(self, key: str, value: object) -> None:
        with self.conn() as c:
            c.execute("INSERT INTO settings(key, value) VALUES(?, ?) "
                      "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, json.dumps(value)))

    def get_setting(self, key: str, default: object = None) -> object:
        with self.conn() as c:
            row = c.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return json.loads(row["value"]) if row else default

    # -- profiles -------------------------------------------------------------
    def upsert_profile(self, info, provider: str) -> None:
        with self.conn() as c:
            c.execute(
                """INSERT INTO profiles(username, display_name, bio, followers_count, following_count,
                posts_count, avatar, account_type, visibility, verified, fetched_at, provider)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(username) DO UPDATE SET display_name=excluded.display_name, bio=excluded.bio,
                followers_count=excluded.followers_count, following_count=excluded.following_count,
                posts_count=excluded.posts_count, avatar=excluded.avatar, account_type=excluded.account_type,
                visibility=excluded.visibility, verified=excluded.verified, fetched_at=excluded.fetched_at,
                provider=excluded.provider""",
                (info.username, info.display_name, info.bio, info.followers_count, info.following_count,
                 info.posts_count, info.avatar, info.account_type, info.visibility,
                 None if info.verified is None else int(info.verified), now(), provider))

    def list_profiles(self) -> list[sqlite3.Row]:
        with self.conn() as c:
            return c.execute("SELECT * FROM profiles ORDER BY username").fetchall()

    def update_profile_meta(self, username: str, notes: str, collection: str, tags: str) -> None:
        with self.conn() as c:
            c.execute("UPDATE profiles SET notes=?, collection=?, tags=? WHERE username=?",
                      (notes, collection, tags, username))

    def delete_profile_data(self, username: str) -> None:
        """Remove every locally stored trace of a profile."""
        with self.conn() as c:
            for table, col in [("snapshots", "profile"), ("events", "profile"), ("mentions", "profile"),
                               ("post_snapshots", "profile"), ("seen_items", "profile"),
                               ("monitors", "profile"), ("downloads", "profile"),
                               ("profile_snapshots", "username"), ("profiles", "username")]:
                c.execute(f"DELETE FROM {table} WHERE {col} = ?", (username,))  # noqa: S608

    def save_profile_snapshot(self, username: str, data: dict) -> None:
        with self.conn() as c:
            c.execute("INSERT INTO profile_snapshots(username, created_at, data) VALUES(?,?,?)",
                      (username, now(), json.dumps(data)))

    def last_profile_snapshot(self, username: str) -> dict | None:
        with self.conn() as c:
            row = c.execute("SELECT data FROM profile_snapshots WHERE username=? ORDER BY id DESC LIMIT 1",
                            (username,)).fetchone()
        return json.loads(row["data"]) if row else None

    # -- snapshots ------------------------------------------------------------
    def save_snapshot(self, profile: str, list_type: str, accounts: list[Account], source: str,
                      complete: bool, expected_count: int | None, label: str = "") -> int:
        with self.conn() as c:
            cur = c.execute(
                """INSERT INTO snapshots(profile, list_type, created_at, source, complete,
                expected_count, returned_count, label) VALUES(?,?,?,?,?,?,?,?)""",
                (profile, list_type, now(), source, int(complete), expected_count, len(accounts), label))
            sid = int(cur.lastrowid)
            c.executemany(
                """INSERT OR REPLACE INTO snapshot_accounts(snapshot_id, username, display_name,
                account_type, visibility, verified, followed_at, profile_url) VALUES(?,?,?,?,?,?,?,?)""",
                [(sid, a.username, a.display_name, a.account_type, a.visibility,
                  None if a.verified is None else int(a.verified), a.followed_at, a.profile_url)
                 for a in accounts])
        return sid

    def list_snapshots(self, profile: str | None = None, list_type: str | None = None) -> list[sqlite3.Row]:
        q, args = "SELECT * FROM snapshots WHERE 1=1", []
        if profile:
            q += " AND profile = ?"
            args.append(profile)
        if list_type:
            q += " AND list_type = ?"
            args.append(list_type)
        with self.conn() as c:
            return c.execute(q + " ORDER BY id DESC", args).fetchall()

    def latest_snapshot(self, profile: str, list_type: str) -> sqlite3.Row | None:
        rows = self.list_snapshots(profile, list_type)
        return rows[0] if rows else None

    def snapshot_accounts(self, snapshot_id: int) -> list[Account]:
        with self.conn() as c:
            rows = c.execute("SELECT * FROM snapshot_accounts WHERE snapshot_id=? ORDER BY username",
                             (snapshot_id,)).fetchall()
        return [Account(r["username"], r["display_name"] or "", r["account_type"] or "Unknown",
                        r["visibility"] or "Unknown", None if r["verified"] is None else bool(r["verified"]),
                        r["followed_at"] or "", r["profile_url"] or "") for r in rows]

    def get_snapshot_usernames(self, snapshot_id: int) -> list[str]:
        with self.conn() as c:
            rows = c.execute("SELECT username FROM snapshot_accounts WHERE snapshot_id=? ORDER BY username",
                             (snapshot_id,)).fetchall()
        return [r["username"] for r in rows]

    def delete_snapshot(self, snapshot_id: int) -> None:
        with self.conn() as c:
            c.execute("DELETE FROM snapshots WHERE id=?", (snapshot_id,))

    # -- events / notifications ---------------------------------------------------
    def add_event(self, profile: str, kind: str, detail: str, dedupe_key: str | None = None) -> bool:
        """Insert an event; returns False when ``dedupe_key`` already exists."""
        with self.conn() as c:
            cur = c.execute("INSERT OR IGNORE INTO events(profile, kind, detail, detected_at, dedupe_key) "
                            "VALUES(?,?,?,?,?)", (profile, kind, detail, now(), dedupe_key))
            return cur.rowcount > 0

    def list_events(self, profile: str | None = None, kind: str | None = None,
                    limit: int = 500) -> list[sqlite3.Row]:
        q, args = "SELECT * FROM events WHERE 1=1", []
        if profile:
            q += " AND profile=?"
            args.append(profile)
        if kind:
            q += " AND kind=?"
            args.append(kind)
        with self.conn() as c:
            return c.execute(q + " ORDER BY id DESC LIMIT ?", [*args, limit]).fetchall()

    def add_notification(self, kind: str, title: str, body: str = "") -> None:
        with self.conn() as c:
            c.execute("INSERT INTO notifications(created_at, kind, title, body) VALUES(?,?,?,?)",
                      (now(), kind, title, body))

    def list_notifications(self, limit: int = 300) -> list[sqlite3.Row]:
        with self.conn() as c:
            return c.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT ?", (limit,)).fetchall()

    def mark_notifications_read(self) -> None:
        with self.conn() as c:
            c.execute("UPDATE notifications SET is_read=1")

    def unread_count(self) -> int:
        with self.conn() as c:
            return int(c.execute("SELECT COUNT(*) FROM notifications WHERE is_read=0").fetchone()[0])

    # -- mentions -------------------------------------------------------------
    def add_mention(self, profile: str, m) -> bool:
        with self.conn() as c:
            cur = c.execute(
                """INSERT OR IGNORE INTO mentions(profile, source_type, by_user, mentioned_user, ref,
                preview, posted_at, detected_at) VALUES(?,?,?,?,?,?,?,?)""",
                (profile, m.source_type, m.by_user, m.mentioned_user, m.ref, m.preview, m.timestamp, now()))
            return cur.rowcount > 0

    def list_mentions(self, profile: str | None = None) -> list[sqlite3.Row]:
        q, args = "SELECT * FROM mentions", []
        if profile:
            q += " WHERE profile=?"
            args.append(profile)
        with self.conn() as c:
            return c.execute(q + " ORDER BY id DESC", args).fetchall()

    # -- seen items / post snapshots ------------------------------------------------
    def mark_seen(self, profile: str, kind: str, item_id: str) -> bool:
        """Return True if the item was newly recorded."""
        with self.conn() as c:
            cur = c.execute("INSERT OR IGNORE INTO seen_items(profile, kind, item_id, first_seen) "
                            "VALUES(?,?,?,?)", (profile, kind, item_id, now()))
            return cur.rowcount > 0

    def has_seen_any(self, profile: str, kind: str) -> bool:
        with self.conn() as c:
            return c.execute("SELECT 1 FROM seen_items WHERE profile=? AND kind=? LIMIT 1",
                             (profile, kind)).fetchone() is not None

    def save_post_stats(self, profile: str, post_id: str, likes: int | None, comments: int | None) -> None:
        with self.conn() as c:
            c.execute("INSERT INTO post_snapshots(profile, post_id, taken_at, likes, comments_count) "
                      "VALUES(?,?,?,?,?)", (profile, post_id, now(), likes, comments))

    def post_history(self, profile: str) -> list[sqlite3.Row]:
        with self.conn() as c:
            return c.execute("SELECT * FROM post_snapshots WHERE profile=? ORDER BY id", (profile,)).fetchall()

    # -- monitors -------------------------------------------------------------
    def upsert_monitor(self, profile: str, interval: int = 60, enabled: bool = True, priority: int = 5) -> None:
        with self.conn() as c:
            c.execute("""INSERT INTO monitors(profile, interval_minutes, enabled, priority) VALUES(?,?,?,?)
                      ON CONFLICT(profile) DO UPDATE SET interval_minutes=excluded.interval_minutes,
                      enabled=excluded.enabled, priority=excluded.priority""",
                      (profile, interval, int(enabled), priority))

    def list_monitors(self) -> list[sqlite3.Row]:
        with self.conn() as c:
            return c.execute("SELECT * FROM monitors ORDER BY priority, profile").fetchall()

    def update_monitor_run(self, profile: str, status: str, next_run: str, errors: int) -> None:
        with self.conn() as c:
            c.execute("UPDATE monitors SET last_run=?, last_status=?, next_run=?, consecutive_errors=? "
                      "WHERE profile=?", (now(), status, next_run, errors, profile))

    def delete_monitor(self, profile: str) -> None:
        with self.conn() as c:
            c.execute("DELETE FROM monitors WHERE profile=?", (profile,))

    # -- downloads / search history -------------------------------------------------
    def add_download(self, profile: str, item_id: str, kind: str, path: str, status: str) -> None:
        with self.conn() as c:
            c.execute("INSERT INTO downloads(profile, item_id, kind, path, created_at, status) "
                      "VALUES(?,?,?,?,?,?)", (profile, item_id, kind, path, now(), status))

    def list_downloads(self) -> list[sqlite3.Row]:
        with self.conn() as c:
            return c.execute("SELECT * FROM downloads ORDER BY id DESC").fetchall()

    def add_search(self, query: str) -> None:
        with self.conn() as c:
            c.execute("INSERT INTO search_history(query, created_at) VALUES(?,?)", (query, now()))

    def list_searches(self, limit: int = 20) -> list[str]:
        with self.conn() as c:
            rows = c.execute("SELECT query FROM search_history GROUP BY query ORDER BY MAX(id) DESC LIMIT ?",
                             (limit,)).fetchall()
        return [r["query"] for r in rows]

    def clear_search_history(self) -> None:
        with self.conn() as c:
            c.execute("DELETE FROM search_history")

    # -- stats ----------------------------------------------------------------
    def stats(self) -> dict[str, int]:
        with self.conn() as c:
            def n(sql: str) -> int:
                return int(c.execute(sql).fetchone()[0])
            return {
                "profiles": n("SELECT COUNT(*) FROM profiles"),
                "monitors": n("SELECT COUNT(*) FROM monitors WHERE enabled=1"),
                "snapshots": n("SELECT COUNT(*) FROM snapshots"),
                "downloads": n("SELECT COUNT(*) FROM downloads WHERE status='ok'"),
                "events": n("SELECT COUNT(*) FROM events"),
                "mentions": n("SELECT COUNT(*) FROM mentions"),
            }

    # -- backup ---------------------------------------------------------------
    def backup_to(self, target: Path) -> Path:
        """Consistent online backup using SQLite's backup API."""
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        src = sqlite3.connect(self.path)
        dst = sqlite3.connect(target)
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()
        return target

    def restore_from(self, source: Path) -> None:
        """Replace the database with a backup after validating it."""
        probe = sqlite3.connect(source)
        try:
            if probe.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Backup file failed the integrity check.")
            probe.execute("SELECT COUNT(*) FROM snapshots")
        except sqlite3.DatabaseError as exc:
            raise ValueError("Not a valid Instagram Research Suite backup.") from exc
        finally:
            probe.close()
        safety = self.path.with_suffix(".before-restore")
        if self.path.exists():
            shutil.copy2(self.path, safety)
        for suffix in ("-wal", "-shm"):
            Path(str(self.path) + suffix).unlink(missing_ok=True)
        shutil.copy2(source, self.path)
        self.initialize()
