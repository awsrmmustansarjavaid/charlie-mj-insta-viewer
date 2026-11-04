# Feature master list

Status: ✅ implemented & tested · 🟡 implemented, depends on source/permissions · ⛔ not provided (and why)

## Your five requirements
| Feature | Status | Notes |
|---|---|---|
| Full followers list, completeness shown | ✅ / 🟡 | ✅ from data export or demo; ⛔ via Graph API (Meta exposes counts only) |
| Full following list | ✅ / 🟡 | same |
| Snapshots, history, compare any two | ✅ | stored in SQLite; diff = added / removed |
| Mutuals, not-following-back, fans you don't follow | ✅ | derived from the two latest snapshots |
| Account type / public vs private / verified counts | 🟡 | only what the source labels; else Unknown |
| Girl/boy counts | 🟡 | aggregate from Instagram Insights (own account); individual gender is never inferred |
| Comments + nested replies, reply to comment | 🟡 | demo ✅; Graph API for your own media |
| Heart / thumbs-up / other emoji counts | ✅ | counted from comment text (not reaction buttons — Instagram exposes none) |
| Mentions in captions / comments / tags | ✅ / 🟡 | story mentions need webhooks via the official API |
| Instagram-style feed, profile, highlights, stories, posts, reels | ✅ | demo data; real media for own/Business accounts via Graph API |

## Website-tool features (from the research documents)
| Capability seen on the 16 sites | Status |
|---|---|
| Profile viewer, profile picture viewer / download | ✅ |
| Story viewer & downloader, highlights viewer & downloader | ✅ demo · 🟡 own stories (API) · ⛔ highlights via API |
| Post / carousel / reel viewing and downloading | ✅ (HTTPS only, 200 MB cap, duplicate detection) |
| New follower / new following / unfollower tracking | ✅ via snapshots (reported as "first detected") |
| Profile change detection (picture, bio, name, link, visibility, counts) | ✅ |
| New post / reel / story detection | ✅ |
| Engagement, posting-pattern, hashtag analytics, profile comparison | ✅ |
| Export CSV / Excel / PDF / HTML / JSON / Markdown, backup & restore | ✅ |
| Anonymous viewing of *any* account's stories/lists via scrapers | ⛔ no compliant official source; see below |
| Last seen / online status | ⛔ not exposed by Instagram |
| Account creation date, registration email / phone / location | ⛔ private |
| Who viewed / liked a post or story | ⛔ not exposed for other users |
| Story replies / private DMs | ⛔ private |

## Why ⛔ items are not built
They are either not exposed by any legitimate Instagram interface or can only be obtained by scraping that violates Instagram's Terms and risks account bans and privacy harm. The provider interface (docs/PROVIDERS.md) lets you add a source **you are authorised to use**.

## Beyond the original lists
Command palette (Ctrl+K), provider health & capability matrix, silent baseline + idempotent change detection, auto-pause after 5 failures, event de-duplication, wallpaper/glass/minimal card styles, reduced-motion option, tray monitoring, daily auto-backup, integrity check, per-profile data deletion, local favourites.
