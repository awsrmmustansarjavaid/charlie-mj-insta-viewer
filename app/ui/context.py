"""Shared application context passed to every page."""

from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap

from app.data.database import Database
from app.providers.registry import ProviderRegistry
from app.services.snapshots import SnapshotService
from app.ui.media import ImageCache
from app.ui.theme import Theme


class AppContext(QObject):
    profile_changed = Signal(str)
    data_changed = Signal()
    theme_changed = Signal()
    navigate = Signal(str)          # page key
    open_profile = Signal(str)      # username
    toast = Signal(str, str)        # title, body

    def __init__(self, db: Database, data_dir: Path):
        super().__init__()
        self.db, self.data_dir = db, data_dir
        self.registry = ProviderRegistry(db)
        self.snapshots = SnapshotService(db, self.registry)
        self.images = ImageCache(data_dir / "cache")
        self.theme = Theme.from_dict(db.get_setting("theme"))
        self._cache: dict[tuple, tuple[float, object]] = {}

    # -- current profile ------------------------------------------------------
    @property
    def profile(self) -> str:
        return str(self.db.get_setting("current_profile", "travel.diary"))

    def set_profile(self, username: str) -> None:
        username = username.strip().lstrip("@")
        if username:
            self.db.save_setting("current_profile", username)
            self.db.add_search(username)
            self.profile_changed.emit(username)

    # -- provider convenience ---------------------------------------------------
    @property
    def provider_label(self) -> str:
        return self.registry.active.label

    @property
    def is_demo(self) -> bool:
        return self.registry.active_name == "demo"

    def pix(self, src: str, w: int, h: int, on_ready=None) -> QPixmap:
        return self.images.resolve(src, w, h, on_ready)

    def save_theme(self) -> None:
        self.db.save_setting("theme", self.theme.to_dict())
        self.theme_changed.emit()

    # -- cached provider access (call from worker threads) ----------------------
    def fetch(self, method: str, *args, ttl: int = 90, **kwargs):
        """Provider call with a short-lived cache so pages don't refetch."""
        key = (self.registry.active_name, method, args)
        hit = self._cache.get(key)
        if hit and time.time() - hit[0] < ttl:
            return hit[1]
        value = self.registry.call(method, *args, **kwargs)
        self._cache[key] = (time.time(), value)
        return value

    def invalidate(self) -> None:
        """Drop cached provider data (after switching provider or demo epoch)."""
        self._cache.clear()
        self.registry.reload()
        self.data_changed.emit()
