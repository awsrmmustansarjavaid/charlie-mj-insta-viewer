# Feature Roadmap

## Implemented in the starter release
- Dark desktop shell and navigation.
- Dashboard, profile, Instagram-style feed mock, story/highlight mock.
- Demo follower and following lists (587 records each).
- Completeness/source labels.
- Local SQLite snapshots and latest-snapshot comparison.
- Provider-supplied account type and visibility counts.
- Demo comment/reply and emoji-analysis screen.
- Mentions timeline mock.
- CSV export.
- Pytest coverage for core analytics.

## Next milestones
1. **Provider research and authorisation:** select a supported data source, document scopes,
   terms, account eligibility, pagination, quotas and failure states.
2. **Live profile/content integration:** map provider records to the provider contract.
3. **Live follower/following collection:** only where the chosen source permits it; persist
   cursor/page state and mark partial responses accurately.
4. **Stories, highlights and mentions:** integrate only endpoints/events available to the
   authorised account and provider.
5. **Engagement integration:** comments/replies and media insights only within granted scopes.
6. **Production UI polish:** real media thumbnails, video playback, virtualised tables,
   accessibility, localisation and light theme.
7. **Release engineering:** Windows signing, versioning, crash diagnostics, backup/restore,
   installer option and clean-machine testing.

## Data integrity rules
- Never fabricate a complete result from a partial provider response.
- Store provider, retrieval timestamp, expected count (if known), returned count and status.
- Distinguish first detected from actual change time.
- Do not infer gender or sensitive attributes from usernames, photos or names.
- Respect platform permissions, terms, rate limits and private-account boundaries.
