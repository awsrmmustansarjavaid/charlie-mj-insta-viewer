from app.providers.demo import DemoProvider
from app.services.monitor import due_monitors, run_cycle, run_monitor
from app.services.snapshots import SnapshotService


def test_first_cycle_is_silent_baseline(db, registry):
    changes = run_cycle(db, registry, "travel.diary")
    assert changes == []
    kinds = {e["kind"] for e in db.list_events("travel.diary")}
    assert "baseline" in kinds and "new_post" not in kinds


def test_second_cycle_detects_changes_once(db, registry):
    run_cycle(db, registry, "travel.diary")
    db.save_setting("demo_epoch", 2)
    registry.reload()
    changes = run_cycle(db, registry, "travel.diary")
    text = " ".join(changes)
    assert "new follower" in text and "follower(s) gone" in text and "Bio change" in text
    assert "new post" in text or "new reel" in text
    assert run_cycle(db, registry, "travel.diary") == []  # idempotent: nothing new on re-run


def test_snapshot_diff_service(db, registry):
    svc = SnapshotService(db, registry)
    first = svc.take("travel.diary", "followers")
    assert not first.had_previous and len(first.accounts) == 587
    registry.providers["demo"] = DemoProvider(1)
    second = svc.take("travel.diary", "followers")
    assert len(second.added) == 5 and len(second.removed) == 3
    assert svc.diff(first.snapshot_id, second.snapshot_id) == (second.added, second.removed)


def test_monitor_pauses_after_repeated_errors(db, registry):
    db.save_setting("active_provider", "graph")  # unconfigured -> PERMISSION errors
    db.upsert_monitor("x", 5)
    for _ in range(5):
        status, _ = run_monitor(db, registry, "x")
        assert status == "error"
    assert db.list_monitors()[0]["enabled"] == 0
    assert any("paused" in n["title"] for n in db.list_notifications())


def test_no_silent_demo_fallback(db, registry):
    db.save_setting("active_provider", "graph")
    assert [p.name for p in registry.order()] == ["graph"]


def test_due_monitors(db):
    db.upsert_monitor("a", 10)
    assert due_monitors(db) == ["a"]
