"""Tests for local snapshot persistence."""

from instagram_research_suite.storage.database import Database


def test_snapshot_round_trip(tmp_path):
    """A saved relationship snapshot should preserve metadata and record count."""
    database = Database(tmp_path / "test.sqlite3")
    database.initialize()
    snapshot_id = database.save_snapshot(
        account_handle="sample_user",
        list_type="followers",
        records=[{"username": "example", "is_private": False}],
        source="test-fixture",
        completeness="partial",
    )

    snapshots = database.list_snapshots("sample_user")
    assert snapshot_id == 1
    assert len(snapshots) == 1
    assert snapshots[0]["retrieved_count"] == 1
    assert snapshots[0]["completeness"] == "partial"


def test_invalid_list_type_is_rejected(tmp_path):
    """Reject unexpected relationship list types to keep stored data consistent."""
    database = Database(tmp_path / "test.sqlite3")
    database.initialize()

    try:
        database.save_snapshot("sample_user", "likes", [], completeness="unknown")
    except ValueError as error:
        assert "list_type" in str(error)
    else:
        raise AssertionError("Invalid list type should raise ValueError")
