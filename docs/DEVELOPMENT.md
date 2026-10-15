# Development Guide and Current Status

## 1. Current repository status

The source imported into this repository is the existing React/Vite web demonstration. It contains mock data and browser-local storage. It does not yet contain a Tauri shell, Rust services, SQLite database, live provider, monitoring bot or production downloader.

Do not describe the current repository as a finished Windows application until those systems exist and have passed tests.

## 2. Prerequisites for the current frontend

- Git
- Node.js LTS
- npm

Check versions:

```powershell
node --version
npm --version
git --version
```

## 3. Run the current frontend

From the repository root:

```powershell
npm install
npm run dev
```

Vite prints a local development URL. Open that URL in a browser.

## 4. Build the current frontend

```powershell
npm run build
npm run preview
```

The production web build is written to `dist/`. This is a web frontend build, not a Windows EXE.

## 5. Desktop implementation prerequisites

When the Tauri desktop layer is added, install the documented Rust toolchain and Windows build prerequisites for the selected Tauri release. Follow the official Tauri Windows setup guide linked from the root README.

The desktop scripts must be added to `package.json` only when `src-tauri/` and the Tauri dependencies are actually committed.

Expected future commands (not available in the current prototype until configured):

```powershell
npm run tauri:dev
npm run tauri:build
```

## 6. Recommended implementation order

1. Create a preservation inventory for existing pages, routes, models and behavior.
2. Add automated tests around the current frontend behavior.
3. Introduce typed service boundaries and provider capability declarations.
4. Add the Tauri shell without removing the browser development workflow.
5. Add SQLite migrations and repositories.
6. Add filesystem and portable-path services.
7. Implement one provider adapter with documented permissions and capabilities.
8. Implement normalized profile/content models.
9. Implement download queue and safe file handling.
10. Implement scheduler, deduplication and notifications.
11. Implement Markdown reports and backup/restore.
12. Package and test on clean Windows machines.

## 7. Branch and commit strategy

Suggested branches:
- `main`: stable releases.
- `develop`: integration branch.
- `feature/tauri-shell`
- `feature/sqlite-storage`
- `feature/provider-interface`
- `feature/download-manager`
- `feature/monitoring`
- `feature/activity-reports`

Use small commits with one clear purpose. Keep the original frontend usable during migration.

## 8. Pull request checklist

- [ ] Existing features remain functional.
- [ ] New code has purpose and logic comments.
- [ ] No secrets, local databases or downloaded media are committed.
- [ ] Provider capability and provenance are handled.
- [ ] Errors are surfaced and logged safely.
- [ ] Tests are added or updated.
- [ ] Documentation is updated.
- [ ] Build succeeds.
- [ ] Portable data paths are tested if relevant.

## 9. Definition of done

A feature is not complete merely because a button or screen exists. It is complete when the user action is connected to a working service, success and failure states are handled, data persists correctly, tests cover the behavior, and the documentation matches actual implementation.
