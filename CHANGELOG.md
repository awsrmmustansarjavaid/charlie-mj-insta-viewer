# Changelog
## 1.0.3
* Workflows now use the same file names as the earlier prototype's (`tests.yml` = "Tests and lint", `windows-build.yml` = "Windows build", plus `ci.yml`), so uploading them overwrites the old failing ones. All call tools via `python -m`.
* `pip install -e ".[dev]"` now works (added `dev` extra, explicit package discovery, build-system table).
* Ruff ignores a legacy `src/` folder if one is still present in the repo.

## 1.0.2
* Release candidate: verified from a clean `git clone` (ruff + 41 tests), and verified that a PyInstaller build of the app starts and creates its data folder (Linux). Pinned dev tool versions, added `.gitattributes`, added docs/GITHUB-SETUP.md.

## 1.0.1
* Fixed: `.gitignore` pattern `data/` also ignored the `app/data/` source package, so it was missing from git (caused ModuleNotFoundError and ruff I001 errors in CI). Now `/data/` (runtime folder only).
* Fixed: workflows call tools via `python -m` (Windows `ruff: not recognized`); Windows build is gated on lint + tests; added a CI sanity check that source packages are tracked.
* Pinned ruff import classification (`known-first-party = ["app"]`).

## 1.0.0
* Rewrote the starter release into the full suite: provider layer (demo, Graph API, data-export importer), snapshots & diff, monitoring engine, Instagram-style viewers, analytics, mentions, exports, backup, tray, theme engine, 17 pages, CI and Windows build scripts.
* Fixed: portable data directory when running from source; DB schema v2 migration.
