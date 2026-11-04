"""Background monitoring scheduler (runs checks off the UI thread, one at a time)."""

from __future__ import annotations

import logging

from PySide6.QtCore import QObject, QTimer, Signal

from app.services.monitor import due_monitors, run_monitor
from app.ui.context import AppContext
from app.ui.workers import run_async

log = logging.getLogger(__name__)


class MonitorScheduler(QObject):
    cycle_finished = Signal(str, str, list)  # profile, status, changes
    state_changed = Signal()

    def __init__(self, ctx: AppContext):
        super().__init__()
        self.ctx = ctx
        self.running: str | None = None
        self.timer = QTimer(self)
        self.timer.setInterval(30_000)
        self.timer.timeout.connect(self.tick)
        if self.enabled:
            self.timer.start()

    @property
    def enabled(self) -> bool:
        return bool(self.ctx.db.get_setting("monitoring_enabled", True))

    def set_enabled(self, on: bool) -> None:
        self.ctx.db.save_setting("monitoring_enabled", on)
        self.timer.start() if on else self.timer.stop()
        self.state_changed.emit()

    def tick(self) -> None:
        """Run the next due monitor (never overlapping runs)."""
        if self.running or not self.enabled:
            return
        due = due_monitors(self.ctx.db)
        if due:
            self.run(due[0])

    def run(self, profile: str) -> None:
        if self.running:
            return
        self.running = profile
        self.state_changed.emit()
        db, reg = self.ctx.db, self.ctx.registry

        def done(result):
            status, changes = result
            self.running = None
            self.ctx.invalidate()
            self.cycle_finished.emit(profile, status, changes)
            self.state_changed.emit()

        def failed(exc):
            log.warning("monitor crashed for %s: %s", profile, exc)
            self.running = None
            self.state_changed.emit()

        run_async(lambda: run_monitor(db, reg, profile), done, failed)
