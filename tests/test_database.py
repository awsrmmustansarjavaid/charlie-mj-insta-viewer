from app.providers.base import Account


def test_snapshot_roundtrip_and_completeness(db):
    sid = db.save_snapshot("me", "followers", [Account("a"), Account("b", verified=True)],
                           "src", True, 2)
    accs = db.snapshot_accounts(sid)
    assert [a.username for a in accs] == ["a", "b"] and accs[1].verified is True and accs[0].verified is None
    assert db.list_snapshots("me")[0]["complete"] == 1


def test_settings_default(db):
    assert db.get_setting("x", 5) == 5
    db.save_setting("x", {"a": 1})
    assert db.get_setting("x") == {"a": 1}


def test_event_dedupe(db):
    assert db.add_event("me", "k", "d", "key") is True
    assert db.add_event("me", "k", "d", "key") is False


def test_backup_restore(db, tmp_path):
    db.save_setting("a", 1)
    b = db.backup_to(tmp_path / "bk.sqlite3")
    db.save_setting("a", 2)
    db.restore_from(b)
    assert db.get_setting("a") == 1


def test_restore_rejects_garbage(db, tmp_path):
    bad = tmp_path / "bad.sqlite3"
    bad.write_bytes(b"not a database")
    import pytest
    with pytest.raises(ValueError):
        db.restore_from(bad)


def test_delete_profile_data(db):
    db.save_snapshot("x", "followers", [Account("a")], "s", True, 1)
    db.add_event("x", "k", "d")
    db.delete_profile_data("x")
    assert not db.list_snapshots("x") and not db.list_events("x")
