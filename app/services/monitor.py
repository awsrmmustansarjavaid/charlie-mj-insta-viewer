"""Monitoring engine: one idempotent check cycle per profile.

The first cycle records a baseline silently. Later cycles emit events only for
things that were *first detected* since the previous cycle; wording always says
"detected", never that the person performed the action at that moment.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone

from app.data.database import Database
from app.providers.base import Mention, ProviderError, to_dict
from app.providers.registry import ProviderRegistry
from app.services.analytics import extract_mentions
from app.services.snapshots import SnapshotService

log = logging.getLogger(__name__)
MAX_ERRORS_BEFORE_PAUSE = 5


def _h(value: object) -> str:
    """Stable short hash (built-in hash() is randomised per process)."""
    return hashlib.sha1(str(value).encode(), usedforsecurity=False).hexdigest()[:10]


def _notify(db: Database, kind: str, title: str, body: str = "") -> None:
    db.add_notification(kind, title, body)


def run_cycle(db: Database, registry: ProviderRegistry, profile: str) -> list[str]:
    """Run all checks for ``profile``. Returns human-readable change lines."""
    changes: list[str] = []
    prov = registry.active
    snaps = SnapshotService(db, registry)

    # 1. profile fields ---------------------------------------------------------
    info = registry.call("get_profile", profile)
    cur = to_dict(info)
    prev = db.last_profile_snapshot(profile)
    if prev is None:
        db.add_event(profile, "baseline", "Initial profile snapshot saved", f"pbase-{profile}-{cur['bio'][:8]}")
    else:
        labels = {"avatar": "Profile picture", "bio": "Bio", "display_name": "Display name",
                  "visibility": "Account visibility", "external_url": "Link in bio"}
        for key, label in labels.items():
            if prev.get(key) != cur.get(key):
                line = f"{label} change first detected"
                if db.add_event(profile, f"profile_{key}", line, f"p-{profile}-{key}-{_h(cur.get(key))}"):
                    changes.append(f"@{profile}: {line}")
                    _notify(db, "profile_change", f"@{profile}: {label.lower()} changed", line)
        for key, label in (("followers_count", "Follower count"), ("following_count", "Following count")):
            a, b = prev.get(key), cur.get(key)
            if a is not None and b is not None and a != b:
                db.add_event(profile, "count_change", f"{label}: {a} → {b}", f"c-{profile}-{key}-{b}-{a}")
    db.save_profile_snapshot(profile, cur)
    db.upsert_profile(info, prov.name)

    # 2. posts / reels ------------------------------------------------------------
    try:
        posts = registry.call("get_posts", profile, 50)
        first = not db.has_seen_any(profile, "post")
        for p in posts:
            new = db.mark_seen(profile, "post", p.id)
            db.save_post_stats(profile, p.id, p.likes, p.comments_count)
            if new and not first:
                kind = "Reel" if p.kind == "REEL" else "Post"
                if db.add_event(profile, f"new_{kind.lower()}", f"New {kind.lower()} discovered: {p.id}", f"post-{p.id}"):
                    changes.append(f"@{profile}: new {kind.lower()}")
                    _notify(db, f"new_{kind.lower()}", f"@{profile} has a new {kind.lower()}", p.caption[:120])
            for m in extract_mentions(p.caption):
                db.add_mention(profile, Mention("caption", p.owner, m, p.id, p.caption[:140], p.timestamp))
    except ProviderError as exc:
        log.info("posts unavailable for %s: %s", profile, exc)

    # 3. stories ------------------------------------------------------------------
    try:
        stories = registry.call("get_stories", profile)
        first = not db.has_seen_any(profile, "story")
        for s in stories:
            if db.mark_seen(profile, "story", s.id) and not first:
                if db.add_event(profile, "new_story", f"New story discovered ({s.id})", f"story-{s.id}"):
                    changes.append(f"@{profile}: new story")
                    _notify(db, "new_story", f"@{profile} has a new story")
    except ProviderError as exc:
        log.info("stories unavailable for %s: %s", profile, exc)

    # 4. mentions -----------------------------------------------------------------
    try:
        for m in registry.call("get_mentions", profile):
            if db.add_mention(profile, m):
                db.add_event(profile, "mention", f"New {m.source_type} mention by @{m.by_user}",
                             f"mention-{profile}-{m.source_type}-{m.by_user}-{m.ref}")
    except ProviderError as exc:
        log.info("mentions unavailable for %s: %s", profile, exc)

    # 5. follower / following lists (only if the provider can supply them) ---------------
    for list_type in ("followers", "following"):
        try:
            res = snaps.take(profile, list_type)
        except ProviderError:
            continue
        if res.had_previous:
            noun = "follower" if list_type == "followers" else "following"
            if res.added:
                changes.append(f"@{profile}: {len(res.added)} new {noun}(s)")
                _notify(db, f"new_{noun}", f"@{profile}: {len(res.added)} new {noun}(s) detected",
                        ", ".join("@" + u for u in res.added[:8]))
            if res.removed:
                changes.append(f"@{profile}: {len(res.removed)} {noun}(s) gone")
                _notify(db, f"lost_{noun}", f"@{profile}: {len(res.removed)} {noun}(s) no longer listed",
                        ", ".join("@" + u for u in res.removed[:8]))
    return changes


def due_monitors(db: Database, now: datetime | None = None) -> list[str]:
    """Enabled monitors whose next run has arrived, highest priority first."""
    now = now or datetime.now(timezone.utc)
    out = []
    for m in db.list_monitors():
        if not m["enabled"]:
            continue
        if not m["next_run"] or datetime.fromisoformat(m["next_run"]) <= now:
            out.append(m["profile"])
    return out


def run_monitor(db: Database, registry: ProviderRegistry, profile: str) -> tuple[str, list[str]]:
    """Run one monitor with error accounting and auto-pause after repeated failures."""
    row = next((m for m in db.list_monitors() if m["profile"] == profile), None)
    interval = row["interval_minutes"] if row else 60
    errors = row["consecutive_errors"] if row else 0
    nxt = (datetime.now(timezone.utc) + timedelta(minutes=interval)).isoformat(timespec="seconds")
    try:
        changes = run_cycle(db, registry, profile)
        db.update_monitor_run(profile, f"ok · {len(changes)} change(s)", nxt, 0)
        return "ok", changes
    except ProviderError as exc:
        errors += 1
        db.update_monitor_run(profile, f"error: {exc}", nxt, errors)
        if errors >= MAX_ERRORS_BEFORE_PAUSE:
            db.upsert_monitor(profile, interval, False, row["priority"] if row else 5)
            _notify(db, "monitor_failure", f"Monitoring paused for @{profile}",
                    f"{errors} consecutive failures. Last error: {exc}")
        else:
            _notify(db, "monitor_failure", f"Check failed for @{profile}", str(exc))
        return "error", []
