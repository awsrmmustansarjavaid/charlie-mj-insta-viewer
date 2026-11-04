"""Fetch, store and compare follower / following snapshots."""

from __future__ import annotations

from dataclasses import dataclass

from app.data.database import Database
from app.providers.base import Account, ProgressFn, RetrievalStatus
from app.providers.registry import ProviderRegistry
from app.services.analytics import compare_usernames


@dataclass
class SnapshotResult:
    snapshot_id: int
    accounts: list[Account]
    status: RetrievalStatus
    added: list[str]
    removed: list[str]
    had_previous: bool


class SnapshotService:
    def __init__(self, db: Database, registry: ProviderRegistry):
        self.db, self.registry = db, registry

    def fetch(self, profile: str, list_type: str, progress: ProgressFn | None = None):
        """Retrieve a list from the active provider (with explicit completeness)."""
        method = "get_followers" if list_type == "followers" else "get_following"
        return self.registry.call(method, profile, progress=progress)

    def save(self, profile: str, list_type: str, accounts: list[Account], status: RetrievalStatus,
             label: str = "") -> SnapshotResult:
        """Persist a snapshot, diff it against the previous one and record events."""
        prev = self.db.latest_snapshot(profile, list_type)
        old = self.db.get_snapshot_usernames(prev["id"]) if prev else []
        sid = self.db.save_snapshot(profile, list_type, accounts, status.source, status.complete,
                                    status.expected_count, label)
        added, removed = compare_usernames(old, [a.username for a in accounts]) if prev else ([], [])
        noun = "follower" if list_type == "followers" else "following"
        if not prev:
            self.db.add_event(profile, "baseline", f"Initial {noun} snapshot saved "
                              f"({len(accounts)} accounts)", f"base-{sid}")
        else:
            for u in added:
                self.db.add_event(profile, f"new_{noun}", f"New {noun} first detected: @{u}", f"n-{noun}-{u}-{sid}")
            for u in removed:
                self.db.add_event(profile, f"lost_{noun}", f"@{u} no longer in {noun} list "
                                  "(first detected missing)", f"l-{noun}-{u}-{sid}")
        return SnapshotResult(sid, accounts, status, added, removed, prev is not None)

    def take(self, profile: str, list_type: str, progress: ProgressFn | None = None,
             label: str = "") -> SnapshotResult:
        accounts, status = self.fetch(profile, list_type, progress)
        return self.save(profile, list_type, accounts, status, label)

    def diff(self, older_id: int, newer_id: int) -> tuple[list[str], list[str]]:
        return compare_usernames(self.db.get_snapshot_usernames(older_id),
                                 self.db.get_snapshot_usernames(newer_id))
