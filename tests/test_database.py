"""Persistence tests for snapshots and settings."""

from pathlib import Path

from app.data.database import Database
from app.services.provider import Account
from instagram_research_suite.storage.database import Database as LegacyDatabase


def test_legacy_import_path_points_to_supported_database() -> None:
    """Keep the historical package import compatible."""
    assert LegacyDatabase is Database


def test_database_initializes_and_persists_snapshot(tmp_path: Path) -> None:
    """Create a snapshot and verify its metadata and account rows."""
    database = Database(tmp_path / "test.sqlite3")
    database.initialize()

    snapshot_id = database.save_snapshot(
        profile="sample_profile",
        list_type="followers",
        accounts=[Account(username="alice", display_name="Alice")],
        source="unit test",
        complete=True,
        expected_count=1,
    )

    snapshots = database.list_snapshots()
    assert len(snapshots) == 1
    assert snapshots[0]["id"] == snapshot_id
    assert snapshots[0]["returned_count"] == 1
    assert snapshots[0]["complete"] == 1
    assert database.get_snapshot_usernames(snapshot_id) == ["alice"]


def test_settings_round_trip(tmp_path: Path) -> None:
    """Persist JSON-compatible settings."""
    database = Database(tmp_path / "settings.sqlite3")
    database.initialize()
    database.save_setting("page_size", 50)
    assert database.get_setting("page_size") == 50
    assert database.get_setting("missing", "fallback") == "fallback"
