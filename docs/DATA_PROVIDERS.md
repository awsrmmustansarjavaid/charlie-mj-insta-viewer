# Data Providers and Integration Strategy

## 1. Purpose

This document defines how the application connects to external data sources without coupling the UI to one provider.

## 2. Provider interface

Every provider adapter should:
- Declare its name and version.
- Declare supported operations and limitations.
- Validate configuration.
- Normalize results into application models.
- Return structured errors.
- Report retrieval timestamps and data provenance.
- Respect documented permissions, terms and rate limits.

## 3. Capability registry

Use a capability registry per operation. Example states:
- supported
- partial
- authorization_required
- unavailable
- temporarily_unavailable

A provider supporting profile lookup does not imply it supports Stories, Story timestamps, mentions, Highlights, repost records or follower lists.

## 4. Data provenance

For each normalized record, retain:
- provider identifier
- provider record ID
- retrieved_at
- source URL, if safe and useful
- original publication time, if supplied
- timestamp precision
- metadata fields supplied by the source

Do not fabricate timestamps or mention relationships. Do not label a timestamp derived from first detection as the original publication time.

## 5. Official API and third-party providers

The official Instagram APIs have account eligibility, permission and endpoint limitations. They are not a universal public-profile scraping API. Review current Meta developer documentation and terms before implementing an integration.

A third-party provider must be evaluated for:
- documented authorization and lawful data access.
- explicit feature coverage.
- data freshness and timestamp semantics.
- mention metadata provenance.
- pagination and retention.
- rate limits and quotas.
- security and credential handling.
- service availability and pricing.
- contractual and platform-policy compatibility.

Do not implement private-account bypasses, credential/session-cookie extraction, anti-bot evasion or rate-limit circumvention.

## 6. Mock provider

Keep a mock provider for:
- UI development.
- automated tests.
- offline demonstrations.
- reproducible fixtures for timestamp and mention UI.

Every mock record must be visibly identified as sample/demo data. The UI must not mix mock and live records without a clear provider/source label.

## 7. Provider failure behavior

A timeout, authorization failure or provider outage must not be interpreted as a profile becoming private or deleted. Preserve the last known state and record the failed check separately.

## 8. Integration acceptance checklist

- [ ] Provider capabilities are declared.
- [ ] Terms and permissions have been reviewed.
- [ ] Credentials are stored securely.
- [ ] Rate limits are enforced.
- [ ] Errors are typed and retryable where appropriate.
- [ ] Timestamps have source and precision fields.
- [ ] Mention records have source provenance.
- [ ] Unsupported operations are clearly surfaced.
- [ ] Automated tests use fixtures and do not depend on live accounts.
