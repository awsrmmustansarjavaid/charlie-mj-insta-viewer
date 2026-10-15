# Development Roadmap

## Phase 0 — Preservation and repository preparation

- Inventory current pages, routes, models and interactions.
- Add purpose comments to source files where the language permits.
- Create documentation and feature preservation checklist.
- Add tests for existing frontend behavior.
- Confirm the mock/demo data boundary.

Exit criteria: current frontend still builds and its existing functionality is documented.

## Phase 1 — Desktop shell

- Add Tauri 2.
- Configure Windows build prerequisites.
- Preserve Vite browser development mode.
- Add typed Tauri command boundary.
- Add portable/user-data path resolution.

Exit criteria: desktop shell launches and can read/write a harmless test setting.

## Phase 2 — Local database

- Add SQLite and migrations.
- Implement repositories.
- Migrate settings, saved items and history.
- Add backup and restore.

Exit criteria: data survives restart and migrations are tested.

## Phase 3 — Provider framework

- Define provider interface.
- Define capability registry.
- Add mock adapter fixtures.
- Add one appropriately authorized provider integration.
- Normalize profile and media records.

Exit criteria: UI accurately displays supported and unsupported operations.

## Phase 4 — Content modules

- Profiles.
- Stories and Story Inspector.
- Mentions with provenance.
- Highlights.
- Posts and carousels.
- Reels and repost records.
- Profile picture history.

Exit criteria: every displayed live item has source and retrieval metadata.

## Phase 5 — Download manager

- Queue and progress.
- Safe filenames and folder structure.
- Retry and cancellation.
- Integrity checks and duplicate detection.
- Saved Library.

Exit criteria: download jobs recover safely from common failures.

## Phase 6 — Monitoring and notifications

- Per-profile schedules.
- Visibility snapshots.
- New-content detection.
- Deduplication.
- Windows notifications.
- Automatic download rules.

Exit criteria: failed checks do not create false visibility changes or duplicate notifications.

## Phase 7 — Activity and reports

- Activity event service.
- Search and filters.
- Daily, weekly and monthly Markdown exports.
- Backup/restore validation.

Exit criteria: reports can be regenerated from the database.

## Phase 8 — Release hardening

- Unit, integration and end-to-end tests.
- Clean Windows packaging tests.
- Portable mode tests.
- Upgrade and migration tests.
- Security review.
- Release notes and checksums.

Exit criteria: documented features work in the packaged build and known limitations are disclosed.
