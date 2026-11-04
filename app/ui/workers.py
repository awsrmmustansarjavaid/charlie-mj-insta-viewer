"""Run blocking provider/database work off the UI thread."""

from __future__ import annotations

import logging
import traceback
from typing import Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

log = logging.getLogger(__name__)


class _Signals(QObject):
    done = Signal(object)
    error = Signal(object)
    progress = Signal(int, object)


class _Job(QRunnable):
    def __init__(self, fn: Callable, with_progress: bool):
        super().__init__()
        self.fn, self.with_progress = fn, with_progress
        self.signals = _Signals()

    def run(self) -> None:
        try:
            if self.with_progress:
                result = self.fn(lambda n, total: self.signals.progress.emit(n, total))
            else:
                result = self.fn()
        except Exception as exc:  # noqa: BLE001
            log.warning("background task failed: %s\n%s", exc, traceback.format_exc())
            self.signals.error.emit(exc)
        else:
            self.signals.done.emit(result)


_alive: set[_Job] = set()


def run_async(fn: Callable, on_done: Callable | None = None, on_error: Callable | None = None,
              on_progress: Callable[[int, int | None], None] | None = None) -> None:
    """Run ``fn`` in the thread pool; callbacks fire on the GUI thread.
    If ``on_progress`` is given, ``fn`` receives a ``progress(n, total)`` callable."""
    job = _Job(fn, on_progress is not None)
    _alive.add(job)

    def cleanup(*_):
        _alive.discard(job)

    if on_done:
        job.signals.done.connect(on_done)
    if on_error:
        job.signals.error.connect(on_error)
    if on_progress:
        job.signals.progress.connect(on_progress)
    job.signals.done.connect(cleanup)
    job.signals.error.connect(cleanup)
    QThreadPool.globalInstance().start(job)
