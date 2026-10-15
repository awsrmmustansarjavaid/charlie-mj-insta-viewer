# Local Database and Data Model

## 1. Database choice

SQLite is the proposed local database because it is embedded, portable and suitable for a single-user desktop application. The database should be accessed through Rust repository/service modules rather than directly from React components.

## 2. Proposed entities

### profiles
- id
- username (normalized and unique)
- display_name
- bio
- avatar_reference
- last_known_visibility
- monitoring_enabled
- created_at
- updated_at

### profile_snapshots
- id
- profile_id
- observed_at
- visibility
- follower_count (nullable)
- following_count (nullable)
- post_count (nullable)
- avatar_reference (nullable)
- source_id

### media_items
- id
- profile_id
- provider_id
- provider_media_id
- category
- media_type
- caption
- published_at (nullable)
- published_at_precision
- first_detected_at
- metadata_source
- original_url (nullable)
- unique provider/media identity constraint

### mentions
- id
- media_item_id
- mentioned_username
- mention_type
- source_id
- detected_at
- provenance

### downloads
- id
- media_item_id
- destination_path
- filename
- file_size
- checksum
- status
- queued_at
- completed_at

### monitoring_jobs
- id
- profile_id
- schedule_definition
- next_run_at
- last_run_at
- status
- retry_count

### activity_events
- id
- event_type
- profile_id (nullable)
- media_item_id (nullable)
- created_at
- details_json

### notifications
- id
- event_id
- category
- created_at
- read_at (nullable)
- delivery_status

### app_settings
- key
- value_json
- updated_at

## 3. Timestamp storage

Store machine timestamps in UTC using an unambiguous ISO-8601 representation or integer epoch convention chosen consistently by the implementation. Preserve source timezone/offset and precision separately when available. Convert to the user's selected timezone only for display.

## 4. Migrations

- Version every schema migration.
- Apply migrations transactionally.
- Back up before destructive migrations.
- Test migration from every supported prior schema version.
- Never silently discard unknown user data.

## 5. Indexes and constraints

Recommended indexes:
- normalized profile username.
- provider ID + provider media ID.
- media category + published_at.
- profile_id + first_detected_at.
- activity created_at + event_type.
- monitoring next_run_at + status.

Use foreign keys and uniqueness constraints to prevent duplicate profile and media records.

## 6. Markdown reports

SQLite is the authoritative source. Markdown files are generated reports and may be regenerated. A report export failure must not delete or corrupt underlying activity events.
