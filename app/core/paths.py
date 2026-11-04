"""Portable data directory resolution and logging setup."""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path

APP_FOLDER = "InstagramResearchSuite"
SUBDIRS = ("database", "downloads", "cache", "exports", "backups", "logs", "imports")


def app_root() -> Path:
    """Folder beside the .exe when frozen, otherwise the repository root."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def _writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def get_data_directory(override: str | None = None) -> Path:
    """Resolve a writable data directory.

    Order: explicit override → ``IRS_DATA_DIR`` → ``<app>/data`` (portable) →
    ``%LOCALAPPDATA%/InstagramResearchSuite``. Program Files and read-only USB
    drives are handled by the fallback.
    """
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    if os.environ.get("IRS_DATA_DIR"):
        candidates.append(Path(os.environ["IRS_DATA_DIR"]))
    candidates.append(app_root() / "data")
    for cand in candidates:
        if _writable(cand):
            break
    else:
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        cand = base / APP_FOLDER
        cand.mkdir(parents=True, exist_ok=True)
    for sub in SUBDIRS:
        (cand / sub).mkdir(exist_ok=True)
    return cand


def configure_logging(log_path: Path) -> None:
    """Rotating file log. Never log tokens or credentials."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    if any(isinstance(h, logging.handlers.RotatingFileHandler) for h in root.handlers):
        return
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    fh = logging.handlers.RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3,
                                              encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)
    if sys.stderr:
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        root.addHandler(sh)
