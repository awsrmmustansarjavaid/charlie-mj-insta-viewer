"""Save media to disk. Local/generated media is rendered by the UI layer; remote
URLs are fetched over HTTPS only, with a size cap and de-duplication."""

from __future__ import annotations

import hashlib
import re
import urllib.request
from pathlib import Path

MAX_BYTES = 200 * 1024 * 1024


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._")[:80] or "item"


def target_path(downloads: Path, profile: str, item_id: str, ext: str) -> Path:
    folder = downloads / safe_name(profile)
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{safe_name(item_id)}{ext}"


def fetch_url(url: str, dest: Path) -> Path:
    """Download an HTTPS URL to ``dest`` (refuses non-HTTPS and oversize files)."""
    if not url.lower().startswith("https://"):
        raise ValueError("Only HTTPS media URLs can be downloaded.")
    req = urllib.request.Request(url, headers={"User-Agent": "InstagramResearchSuite/1.0"})  # noqa: S310
    with urllib.request.urlopen(req, timeout=40) as resp, open(dest, "wb") as out:  # noqa: S310
        size = 0
        while chunk := resp.read(1 << 16):
            size += len(chunk)
            if size > MAX_BYTES:
                out.close()
                dest.unlink(missing_ok=True)
                raise ValueError("File exceeds the 200 MB safety limit.")
            out.write(chunk)
    return dest


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_duplicate(path: Path) -> Path | None:
    """Return an existing identical file in the same folder, if any."""
    digest = file_hash(path)
    for other in path.parent.iterdir():
        if other != path and other.is_file() and other.stat().st_size == path.stat().st_size:
            if file_hash(other) == digest:
                return other
    return None
