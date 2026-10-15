# Security, Privacy and Responsible Data Handling

## 1. Local data

The application is designed to keep profiles, settings, activity records and downloaded files on the user's machine by default. Any external provider connection must be disclosed in the UI and documentation.

## 2. Credentials

- Never request or store an Instagram password.
- Do not extract or persist browser session cookies.
- Store provider credentials using an appropriate OS credential store where possible.
- Never commit secrets to Git.
- Provide `.env.example` with placeholder values only.
- Redact tokens and sensitive URLs from logs.

## 3. Filesystem safety

- Restrict file operations to configured application/download directories.
- Sanitize usernames and filenames.
- Prevent path traversal.
- Write downloads to temporary files before finalizing.
- Confirm destructive file deletion.
- Do not delete user media when clearing database history unless the user explicitly chooses that action.

## 4. External provider use

Review current platform terms, API documentation, provider contracts and applicable law before integrating a source. Respect authentication, access controls, rate limits and provider restrictions. Do not bypass private-account restrictions or anti-abuse controls.

## 5. Metadata integrity

- Preserve provenance for timestamps and mentions.
- Distinguish exact, approximate and unknown values.
- Label OCR or heuristic extraction as inferred.
- Never claim that a profile changed visibility based solely on a failed network request.

## 6. Logs and reports

- Avoid writing secrets to logs.
- Keep generated reports local unless the user exports them.
- Provide controls to clear history and delete local application data.
- Explain the difference between clearing records and deleting downloaded media.

## 7. Backups

- Let users choose backup location.
- Avoid including credentials in plain-text backups.
- Validate backups before restore.
- Warn before overwriting existing data.
