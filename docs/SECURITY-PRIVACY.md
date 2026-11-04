# Security & privacy
* No Instagram password is ever requested.
* API tokens: Windows Credential Manager (`keyring`); never in SQLite, logs, exports or backups.
* HTTPS only for providers and media downloads; downloads capped at 200 MB; filenames sanitised.
* Everything stays local (SQLite + files in the data folder); nothing is uploaded anywhere except requests to the provider you enable. A third-party provider can see your IP.
* Controls: clear search history, clear image cache, **delete all stored data for a profile**, backups (daily auto, 10 kept), DB integrity check.
* Logs rotate and contain no tokens.
* Gender is never inferred for individuals; sentiment is labelled indicative.
* Replying to comments on a real account asks for confirmation first.
