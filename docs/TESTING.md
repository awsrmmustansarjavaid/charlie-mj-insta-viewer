# Testing
`pytest` runs 41 tests: analytics (emoji, groups, relationships, no gender inference), database (snapshots, backup/restore, dedupe, deletion), providers (export parsing incl. zips and multiple layouts, Graph API with mocked HTTP, HTTPS enforcement), monitoring (baseline, idempotency, auto-pause, no demo fallback) and offscreen UI smoke tests (all 17 pages, 587-row followers table, filtering, post/story viewers, reply round-trip, theme switch).
`python scripts/screenshots.py OUT_DIR` renders the key screens headlessly.
Manual checklist before release: build exe on Windows, open every page, import a real export zip, run a monitor, restore a backup, test tray/notifications.
