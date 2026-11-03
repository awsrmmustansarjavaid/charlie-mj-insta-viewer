"""Shared application utilities."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path


APP_FOLDER = "InstagramResearchSuite"


def get_data_directory() -> Path:
    """Return a writable portable data path, falling back to user app data."""
    executable_dir = Path(sys.executable).resolve().parent
    source_dir = Path(__file__).resolve().parents[1]
    candidates = [executable_dir / "data", source_dir / "data"]

    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write_test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return candidate
        except OSError:
            continue

    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    fallback = base / APP_FOLDER
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def configure_logging(log_path: Path) -> None:
    """Configure rotating-friendly basic logging without recording credentials."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
