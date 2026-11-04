"""Small formatting helpers."""

from __future__ import annotations

from datetime import datetime, timezone


def parse_dt(ts: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def ago(ts: str) -> str:
    """'2h', '3d', '5w' style relative time like Instagram."""
    dt = parse_dt(ts)
    if not dt:
        return ""
    secs = max(0, int((datetime.now(timezone.utc) - dt).total_seconds()))
    for unit, size in (("w", 604800), ("d", 86400), ("h", 3600), ("m", 60)):
        if secs >= size:
            return f"{secs // size}{unit}"
    return "now"


def fmt_count(n: int | None) -> str:
    if n is None:
        return "–"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 10_000:
        return f"{n / 1000:.1f}k"
    return f"{n:,}"


def fmt_dt(ts: str) -> str:
    dt = parse_dt(ts)
    return dt.astimezone().strftime("%Y-%m-%d %H:%M") if dt else (ts or "")


def parse_username(text: str) -> str:
    """Accept '@name', 'name' or an instagram.com profile URL."""
    import re

    text = (text or "").strip()
    m = re.search(r"instagram\.com/(?:_u/)?([A-Za-z0-9._]+)", text)
    return (m.group(1) if m else text).strip("/@ ").lower()


def ago_long(ts: str) -> str:
    """'3h ago' or 'just now'."""
    short = ago(ts)
    return "" if not short else ("just now" if short == "now" else f"{short} ago")
