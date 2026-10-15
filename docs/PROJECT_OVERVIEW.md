# Project Overview

## 1. What is Charlie MJ Insta Viewer & Downloader?

Charlie MJ Insta Viewer & Downloader is the planned Windows desktop evolution of the existing Charlie MJ Insta Viewer frontend demonstration. The long-term product is intended to provide one local-first workspace for managing supported public Instagram profile information and media workflows.

The project brings together profile discovery, Story inspection, available Story metadata, media viewing, downloads, monitoring schedules, notifications, saved media, and Markdown activity reports.

**Current repository status:** The imported React/Vite application is a frontend demonstration backed by mock data and browser `localStorage`. It is not yet the completed Windows desktop application. A real provider integration, Tauri/Rust desktop shell, SQLite database, monitoring worker, and download engine are future implementation work.

## 2. Why this project is being built

The project is motivated by the desire to consolidate repetitive manual profile checks and media organization into one Windows application. Instead of repeatedly opening several independent websites, the intended application will provide one place to:

- Maintain a list of profiles to check.
- Review content returned by a supported provider.
- Inspect publication metadata when the provider exposes it.
- Organize downloaded media locally.
- Receive configurable notifications about newly detected content.
- Keep searchable activity and export reports.

## 3. Product goals

- Reuse and preserve useful parts of the existing React frontend.
- Build a desktop-first interface with a configurable grid layout.
- Keep application records and user preferences local by default.
- Make provider integrations replaceable.
- Clearly distinguish live provider data from mock/demo data.
- Make timestamps and mention metadata provenance visible.
- Provide reliable download queues and recovery behavior.
- Produce portable Windows distribution packages after desktop implementation.

## 4. Planned feature groups

### Profile management
- Username and supported profile URL input.
- Multiple saved profile records.
- Notes, tags, favorites and monitoring preferences.
- Profile status snapshots when supported.

### Content viewing
- Stories and Story Inspector.
- Story calendar.
- Highlights and Highlight media.
- Posts and carousels.
- Reels.
- Repost records when a provider exposes them.
- Profile-picture previews.

### Story metadata
- Original publication timestamp when supplied by the source.
- First-detected timestamp recorded by the application.
- Download timestamp recorded locally.
- Mention and tag metadata when supplied in structured form.
- Explicit unavailable/unknown states instead of fabricated values.

### Monitoring and notifications
- Per-profile schedules.
- Visibility-state change history where observable.
- New-content detection based on stable provider identifiers.
- Duplicate-notification prevention.
- Windows and in-app notifications.
- Quiet hours, retries and rate-limit-aware backoff.

### Download and library
- Centralized download queue.
- Category-specific directories.
- Configurable Windows-safe filenames.
- Progress, retry and failure history.
- Local media library, collections and duplicate detection.

### Activity and reports
- Structured SQLite activity events.
- Daily, weekly, monthly and custom Markdown reports.
- Search, filter and export functions.
- Backup and restore.

## 5. Non-goals and boundaries

- The app is not an official Instagram or Meta product.
- The project does not promise access to every Instagram feature or every public account.
- It does not bypass private-account restrictions, authentication controls, rate limits or provider restrictions.
- It does not promise exact Story timestamps or mention metadata unless the connected source actually supplies them.
- It does not claim that the current mock frontend retrieves live Instagram data.

## 6. Product principles

1. **Preserve existing functionality:** document current behavior before refactoring.
2. **Additive migration:** replace components only when the replacement is tested and equivalent behavior is retained.
3. **Provider independence:** UI components must not depend on one provider's response format.
4. **Provenance:** record where metadata came from and when it was observed.
5. **Local-first:** keep user settings, history and downloaded media on the user's device unless an explicitly configured service requires otherwise.
6. **Honest capability reporting:** unsupported features must be visibly marked unsupported.
7. **Reliability:** failed jobs must remain inspectable and retryable.

## 7. Project identity

- **Name:** Charlie MJ Insta Viewer & Downloader
- **Short name:** Charlie MJ Insta Viewer
- **Target platform:** Windows desktop
- **Planned desktop framework:** Tauri 2
- **Frontend:** React and TypeScript
- **Backend/runtime:** Rust
- **Local database:** SQLite
- **Styling:** Tailwind CSS
- **Current prototype tooling:** Vite

## 8. Current status

The repository currently contains a React/Vite frontend demonstration, mock content data, local browser storage, a provider-shaped API adapter, and GitHub Pages deployment configuration. The desktop architecture and feature descriptions in this documentation are the target design, not proof that those systems have already been implemented.

See [Development Status](DEVELOPMENT.md), [Architecture](ARCHITECTURE.md), and [Roadmap](ROADMAP.md).
