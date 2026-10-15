# Feature Catalogue

This document is the feature inventory and acceptance reference for the planned application.

## 1. Dashboard

- Profile count and monitoring status.
- New content counts.
- Download totals and active queue.
- Recent activity and notifications.
- Last and next monitoring runs.
- Storage usage and quick actions.

Acceptance: all dashboard metrics must be calculated from local records or clearly labeled provider data; demo fixture values must be labeled as demo.

## 2. Profile manager

- Add by username or supported profile URL.
- Normalize usernames and avoid duplicates.
- Edit notes, tags, favorites and schedule.
- Pause or resume monitoring.
- Remove a profile without silently deleting its downloaded files.
- Show latest known profile snapshot and last check.

Acceptance: profile records remain after application restart and are not duplicated by equivalent URL/username input.

## 3. Stories and Story Inspector

- Photo and video preview.
- Sequential navigation and full-screen view.
- Metadata panel.
- Story calendar.
- Mention filters when structured mention data exists.
- Save and download actions.

Acceptance: published, detected and downloaded times are stored separately. Missing publication timestamps display as unavailable. No timestamp may be synthesized from detection time.

## 4. Highlights

- Collection cover and title.
- Available media list.
- Media viewer.
- Metadata and download state.
- Search and filtering.

Acceptance: only collections and items returned by the provider are shown as live data.

## 5. Posts and carousels

- Image, video and carousel cards.
- Caption and available engagement metadata.
- Media preview and original link.
- Individual and multi-item download.

Acceptance: carousel slides preserve their order and association with the parent post.

## 6. Reels and reposts

- Reels gallery and player.
- Available caption, creator and publication information.
- Repost record with original creator/source attribution.
- Clear distinction between a native repost record and a normal shared link.

Acceptance: repost classification is based on provider metadata, not merely a guessed relationship.

## 7. Profile pictures

- Preview, zoom and download.
- Available resolution information.
- Optional local snapshots to compare changes.

Acceptance: the app describes an image as the highest available source resolution only when that is known.

## 8. Followers and following

- Display lists only if the connected provider is authorized and capable of returning them.
- Search and sort returned entries.
- Export returned data.
- Compare snapshots only when comparable snapshots exist.

Acceptance: counts must not be represented as full lists. Unsupported list retrieval must be shown as unavailable.

## 9. Monitoring bot

- Multiple profiles.
- Per-profile and global schedules.
- Start, pause, resume and stop.
- New-content detection using stable provider IDs.
- Visibility state snapshots where observable.
- Retry and backoff.
- Automatic download rules.

Acceptance: temporary provider/network failures do not become false private/public transitions. Repeated checks do not create duplicate media or notifications.

## 10. Notifications

- New content.
- Visibility state change.
- Mention metadata detected.
- Download completion/failure.
- Monitoring errors.
- In-app button feedback.

Acceptance: success notifications appear only after the operation succeeds. Progress notifications use a separate status.

## 11. Downloader

- Queue, progress, pause/cancel where supported.
- Retry failed downloads.
- Category-specific directories.
- Safe filenames.
- Duplicate detection.
- Open file/folder.
- Download history.

Suggested filename:
`{username}-{category}-{DD-Month-YYYY}_{hh-mm}_{AM/PM}.{extension}`

Use the local download time by default. Allow original publication time only when it is reliably supplied. Resolve filename collisions with a stable suffix.

## 12. Saved Library

- Grid/list view.
- Category and date filters.
- Search by username and filename.
- Favorites and collections.
- Metadata and file location.
- Multi-select and deletion.

Acceptance: deleting a database reference and deleting the actual file must be separate, explicit actions.

## 13. Activity and reports

- Structured activity records.
- Search and filters.
- Daily, weekly, monthly and custom reports.
- Per-profile reports.
- Markdown, JSON and CSV export; PDF may be added later.

Acceptance: SQLite is the authoritative activity store. Markdown reports are generated views and can be regenerated.

## 14. Settings and maintenance

- Appearance and language.
- Provider configuration.
- Monitoring schedules.
- Notification preferences.
- Download naming and paths.
- Storage, cache and backup.
- Export, restore and clear-history controls.

Acceptance: settings are validated, persisted and migrated safely between versions.
