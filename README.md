# Instagram Research Suite

A Windows desktop research workspace with an Instagram-inspired browsing UI, local snapshots,
engagement exploration, mentions, account classification, and export tools.

> **Data access notice:** This repository ships with a clearly labelled demo data provider.
> Instagram does not provide unrestricted access to arbitrary accounts' follower/following
> lists, private stories, likes, or comments. Real integrations must use Meta-authorised
> permissions or another lawful, supported source. The application never bypasses login,
> access controls, private-account restrictions, or rate limits.

## Features in this starter release

- Dark dashboard with sidebar navigation and responsive desktop panels.
- Instagram-style feed/profile/story/highlight browsing using demo content.
- Follower and following explorer with search, completeness state, and local snapshots.
- Snapshot history and added/removed comparison.
- Account-type and public/private breakdown; gender is shown as **unknown** unless a
  source explicitly provides authorised aggregate demographic data.
- Post engagement view with demo comments/replies and emoji frequency analysis.
- Mentions and tags timeline (only records supplied by the connected provider).
- CSV export for account lists.
- SQLite persistence, settings, structured logging, and tests.

## Requirements

- Windows 10/11 (64-bit)
- Python 3.11+
- Internet connection only if a future provider integration requires it

## Run from source

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## Build a portable Windows executable

Run on Windows, not Linux/macOS:

```powershell
.\scripts\build_windows.ps1
```

The build creates `dist\InstagramResearchSuite\InstagramResearchSuite.exe` using PyInstaller
one-folder mode. The `data` directory is stored beside the executable in portable mode when
writable; otherwise the app uses the user's local application-data directory.

For a single-file executable, change `--onedir` to `--onefile` in the build script. One-folder
mode is recommended for startup speed, diagnostics, and predictable asset handling.

## GitHub setup

1. Create an empty GitHub repository named `InstagramResearchSuite`.
2. Extract this project.
3. Run:

```powershell
git init
git add .
git commit -m "Initial Instagram Research Suite desktop app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/InstagramResearchSuite.git
git push -u origin main
```

## Provider integration contract

Implement `app/services/provider.py` and provide an implementation of `InstagramDataProvider`.
A provider must report source, retrieval time, completeness, pagination state, and any limitation.
Do not silently label partial results as complete.

## Current release status

This is a functional desktop foundation with local demo data and local snapshot workflows.
It is not an official Instagram client, does not authenticate to Instagram, and does not
promise arbitrary-account or private-account access. Real provider integrations are a
separate, permission-dependent milestone.
