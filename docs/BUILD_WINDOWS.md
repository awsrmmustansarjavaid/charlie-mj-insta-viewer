# Windows Build and Portable Packaging

## 1. Important distinction

The current project can build a static web frontend with Vite. It cannot yet produce the planned Tauri Windows application because the Tauri project, Rust commands, native plugins and desktop build scripts have not been added.

## 2. Current web build

```powershell
npm install
npm run build
```

Output: `dist/`.

This output is for web hosting and is not a portable Windows executable.

## 3. Planned desktop build

After Tauri 2 is integrated and configured:

```powershell
npm install
npm run tauri:dev
npm run tauri:build
```

The exact output location and package format depend on the Tauri configuration and Windows bundler settings. Confirm the generated artifacts from the build output rather than assuming a fixed path.

## 4. Portable distribution design

Plan to publish:
- A portable archive containing the executable and required runtime files.
- An installer package for users who prefer installation.

A portable package should support:
- Portable data stored beside the executable, when the folder is writable.
- A fallback to the Windows user data directory.
- Clear indication of the active data location.
- Database migrations and backups.
- No hardcoded developer-machine paths.

Do not promise a single-file, dependency-free EXE until tested. Windows WebView2 and native runtime requirements must be documented and validated.

## 5. Release validation

Test on a clean Windows environment:
- First launch and data-directory creation.
- Launch from a path containing spaces.
- Launch from a non-system drive.
- Read-only folder fallback.
- Database creation and migration.
- Download path permissions.
- Notification permission and delivery.
- App close/reopen while downloads are pending.
- Backup and restore.
- Upgrade from a previous release.
- Missing provider configuration.
- Network unavailable behavior.

## 6. Release artifacts

Recommended names:
- `Charlie-MJ-Insta-Viewer-Portable-vX.Y.Z.zip`
- `Charlie-MJ-Insta-Viewer-Setup-vX.Y.Z.exe`

Publish checksums and release notes. Do not include personal databases, downloaded media, API keys or local activity logs in release archives.
