"""Import complete follower/following lists from your own Instagram data export.

Instagram lets every account owner download their data (Accounts Center →
*Your information and permissions* → *Download your information*, format
JSON). That archive contains the full ``followers_1.json`` / ``following.json``
lists, including the time each connection was created. This is the
authoritative, fully lawful way to obtain a complete 587-of-587 list.

Also accepted: a plain CSV/JSON/TXT of usernames, and ``recently_unfollowed``
files from the export.
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from app.providers.base import Account, RetrievalStatus, utcnow

_USER_RE = re.compile(r"instagram\.com/(?:_u/)?([A-Za-z0-9._]+)/?")


def _ts(value: object) -> str:
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).isoformat(timespec="seconds")
    except (TypeError, ValueError, OSError):
        return ""


def _from_entry(entry: dict) -> Account | None:
    """Parse one ``string_list_data`` style entry."""
    data = (entry.get("string_list_data") or [{}])[0]
    name = data.get("value") or entry.get("title") or ""
    if not name and data.get("href"):
        match = _USER_RE.search(data["href"])
        name = match.group(1) if match else ""
    name = str(name).strip().lstrip("@")
    if not name:
        return None
    return Account(username=name, followed_at=_ts(data.get("timestamp")),
                   profile_url=data.get("href") or "")


def _walk(obj: object) -> list[Account]:
    """Find account entries in the several layouts Instagram has used."""
    found: list[Account] = []
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict) and "string_list_data" in item:
                acc = _from_entry(item)
                if acc:
                    found.append(acc)
            elif isinstance(item, (dict, list)):
                found.extend(_walk(item))
            elif isinstance(item, str) and item.strip():
                found.append(Account(username=item.strip().lstrip("@")))
    elif isinstance(obj, dict):
        for value in obj.values():
            if isinstance(value, (dict, list)):
                found.extend(_walk(value))
    return found


def _dedupe(accounts: list[Account]) -> list[Account]:
    seen: dict[str, Account] = {}
    for acc in accounts:
        seen.setdefault(acc.username.lower(), acc)
    return sorted(seen.values(), key=lambda a: a.username.lower())


def parse_json_bytes(raw: bytes) -> list[Account]:
    """Parse an Instagram export JSON file."""
    return _dedupe(_walk(json.loads(raw.decode("utf-8-sig"))))


def parse_text(text: str) -> list[Account]:
    """Parse CSV (header ``username``) or one-username-per-line text."""
    text = text.strip()
    if not text:
        return []
    if text[0] in "[{":
        return _dedupe(_walk(json.loads(text)))
    rows = list(csv.reader(io.StringIO(text)))
    header = [c.strip().lower() for c in rows[0]] if rows else []
    if "username" in header:
        idx = header.index("username")
        disp = header.index("display_name") if "display_name" in header else None
        out = [Account(username=r[idx].strip().lstrip("@"),
                       display_name=r[disp].strip() if disp is not None and len(r) > disp else "")
               for r in rows[1:] if len(r) > idx and r[idx].strip()]
        return _dedupe(out)
    return _dedupe([Account(username=line.strip().lstrip("@")) for line in text.splitlines() if line.strip()])


def _names_in_zip(zf: zipfile.ZipFile, pattern: str) -> list[str]:
    rx = re.compile(pattern, re.I)
    return sorted(n for n in zf.namelist() if rx.search(n.replace("\\", "/")))


def load_export(path: str | Path, list_type: str) -> tuple[list[Account], RetrievalStatus]:
    """Load followers or following from a zip, JSON, CSV or TXT file.

    ``list_type`` is ``"followers"`` or ``"following"``. For a zip, all matching
    files (``followers_1.json``, ``followers_2.json`` …) are merged.
    """
    path = Path(path)
    accounts: list[Account] = []
    if path.suffix.lower() == ".zip":
        pattern = r"(^|/)followers_\d+\.json$" if list_type == "followers" else r"(^|/)following\.json$"
        with zipfile.ZipFile(path) as zf:
            names = _names_in_zip(zf, pattern)
            if not names:
                raise ValueError(f"No {list_type} file found in the archive. Expected "
                                 f"{'followers_1.json' if list_type == 'followers' else 'following.json'}.")
            for name in names:
                accounts.extend(parse_json_bytes(zf.read(name)))
    elif path.suffix.lower() == ".json":
        accounts = parse_json_bytes(path.read_bytes())
    else:
        accounts = parse_text(path.read_text(encoding="utf-8-sig"))
    accounts = _dedupe(accounts)
    status = RetrievalStatus(
        source=f"Instagram data export ({path.name})", retrieved_at=utcnow(),
        returned_count=len(accounts), expected_count=len(accounts), complete=bool(accounts),
        message=(f"Imported {len(accounts)} {list_type} from your own export file. "
                 "Completeness reflects the export, as of the day it was generated."),
        availability="AVAILABLE" if accounts else "PROVIDER UNAVAILABLE")
    return accounts, status


def load_recently_unfollowed(path: str | Path) -> list[Account]:
    """Read ``recently_unfollowed_profiles.json`` from an export zip or file."""
    path = Path(path)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = _names_in_zip(zf, r"recently_unfollowed.*\.json$")
            out: list[Account] = []
            for n in names:
                out.extend(parse_json_bytes(zf.read(n)))
            return _dedupe(out)
    return parse_json_bytes(path.read_bytes())
