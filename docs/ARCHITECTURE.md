# Architecture

```
UI (PySide6)  ──►  AppContext  ──►  ProviderRegistry ──► Provider (demo | graph | your own)
   pages/                │                 │
   viewers               ├─► Services (analytics, snapshots, monitor, exporter, downloader)
   scheduler             └─► Database (SQLite, WAL)
```
* **Provider contract** (`app/providers/base.py`): every source subclasses `Provider`, implements only what it truly supports and raises `ProviderError(status)` otherwise. Statuses drive the UI chips.
* **Registry**: active provider first, then other *enabled real* providers; **demo is never an implicit fallback**.
* **Services are Qt-free**, so they are unit-tested without a display.
* **Workers** (`ui/workers.py`) run provider calls in a thread pool; callbacks return on the GUI thread. SQLite uses a short-lived connection per operation (thread-safe).
* **Monitoring**: `services/monitor.run_cycle` is idempotent. First run = silent baseline; later runs emit events only for items not in `seen_items`/previous snapshot; events carry a `dedupe_key`. `MonitorScheduler` ticks every 30 s, runs one profile at a time (no overlap), pauses a monitor after 5 consecutive failures.
* **Honest time semantics**: all change events mean "first detected by this app", never "the person did this at".
