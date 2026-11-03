# Architecture

- `app/ui`: PySide6 presentation layer. UI widgets do not perform network requests.
- `app/services`: provider contract and deterministic analytics.
- `app/data`: SQLite persistence and snapshot history.
- `app/utils.py`: writable portable data path and logging.
- `main.py`: composition root.

## Provider boundary

Implement `InstagramDataProvider` for any authorised source. Provider responses should
include a `RetrievalStatus` with `source`, `retrieved_at`, `returned_count`,
`expected_count`, `complete`, and a human-readable `message`.

Keep API tokens out of source code, logs, exports and settings JSON. Prefer Windows
Credential Manager or another OS-backed secret store for future credentials.
