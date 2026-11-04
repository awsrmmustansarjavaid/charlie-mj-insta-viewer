# Changelog
## 1.0.1
* Fixed: `.gitignore` pattern `data/` also ignored the `app/data/` source package, so it was missing from git (caused ModuleNotFoundError and ruff I001 errors in CI). Now `/data/` (runtime folder only).
* Fixed: workflows call tools via `python -m` (Windows `ruff: not recognized`); Windows build is gated on lint + tests; added a CI sanity check that source packages are tracked.
* Pinned ruff import classification (`known-first-party = ["app"]`).

## 1.0.0
* Rewrote the starter release into the full suite: provider layer (demo, Graph API, data-export importer), snapshots & diff, monitoring engine, Instagram-style viewers, analytics, mentions, exports, backup, tray, theme engine, 17 pages, CI and Windows build scripts.
* Fixed: portable data directory when running from source; DB schema v2 migration.
