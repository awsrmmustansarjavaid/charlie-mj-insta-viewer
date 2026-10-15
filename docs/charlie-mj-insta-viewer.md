# charlie-mj-insta-viewer

# Project Name: Charlie MJ Insta Viewer & Downloader

Windows Desktop Application

Portable EXE

Local-First Architecture

[Social Media Automation for AI Agents | Posta](https://images.openai.com/static-rsc-4/w4MnU5mqhYEpuLg9g6qNNcY73K8UVsnyhnorJODK9Y8N8_V7TzsFEUnY-ZViPQlRwzftBZlphRbgZEi2Uqp6mWAM9RMshUwAsHhfLdItqVpp_wNHXj59CY9LjI9U41kCoC6K9suWhXdUFpHTDkhduYf13I3AK0SA0CnmljkUxoE?purpose=inline)

[getposta.app](https://getposta.app/)

## 1. Project Vision and Main Objective

Charlie MJ Insta Viewer & Downloader will be a Windows-based desktop application that combines the most useful functionality of StorySaver, InSnoop, AnonyIG, Pixnoy, and your existing Charlie MJ Insta Viewer web application.

The objective is to develop a complete, standalone application that lets you:

- Search and monitor multiple Instagram usernames.
- View available public profiles and their information.
- Check Stories, Highlights, Posts, Reels and reposts.
- Inspect Story timestamps and available mention information.
- Download available profile pictures, Stories, Highlights, Posts, Reels and repost media.
- Automatically monitor configured profiles on a schedule.
- Receive Windows desktop notifications when new content is detected.
- Maintain a local library of downloaded media.
- Keep activity records and generate Markdown reports.
- Manage everything through one modern desktop interface.
- Operate without opening multiple third-party websites every day.

The application should be designed as a personal productivity and media-management tool rather than simply wrapping your existing website inside an EXE.

## 2. Review of Your Existing Demo Application

I inspected the uploaded ZIP source code, including its React components, pages, data models, storage system, mock provider and project configuration.

Your GitHub project:

[Charlie MJ Insta Viewer – GitHub Repository](https://github.com/awsrmmustansarjavaid/charlie-mj-insta-viewer)

### 2.1 Existing technology and architecture

Your current project uses:

- React.
- TypeScript.
- Vite.
- Tailwind CSS.
- React Router.
- Lucide React icons.
- Browser localStorage.
- A provider-based data access architecture.
- GitHub Actions for deployment.
- PWA manifest groundwork.

### 2.2 Existing features that should be preserved

Your existing application already provides a useful frontend foundation.

- Home dashboard.
- Profile search.
- Profile information and statistics.
- Story viewer.
- Story Inspector.
- Story calendar groundwork.
- Story metadata fields.
- Exact timestamp field.
- Mentioned-user metadata.
- Location metadata.
- Music metadata.
- Story archive status.
- Posts and carousel data models.
- Reels.
- Reposts with original creator and source URL.
- Comment explorer data models.
- Saved Library.
- Search History.
- Dark mode.
- Settings.
- About, Privacy and Terms pages.
- Provider abstraction through `src/services/api.ts`.

### 2.3 Important technical discovery

Your existing project is still a frontend demonstration.

The most important finding is that:

- `src/data/mockData.ts` contains demonstration profiles and media.
- `src/services/api.ts` currently uses `mockProvider`.
- Profile, Story, Post and Reel data are not being retrieved from a live Instagram data source.
- Your sample Story timestamps and mentions are predefined values, not timestamps or mentions independently retrieved from Instagram.
- Your browser storage currently uses localStorage.
- Your settings contain a future API URL field, but it does not establish a functioning backend.

However, there is an important architectural advantage: your existing DataProvider abstraction makes it possible to introduce a real backend without rebuilding the entire frontend from scratch.

### 2.4 How to migrate the existing project

I recommend keeping your current frontend as the UI foundation and gradually introducing desktop functionality.

- Preserve existing React components wherever practical.
- Preserve existing profile, Story, Post, Reel and Repost models.
- Extend models rather than replacing them unnecessarily.
- Replace the mock provider with a backend-connected provider.
- Introduce a desktop database instead of relying exclusively on localStorage.
- Add a background monitoring service.
- Introduce a dedicated download manager.
- Add Windows notification integration.
- Preserve your current Saved Library and Search History functionality.
- Keep existing navigation and visual identity while expanding the application.

Important development principle: New functionality must be additive. Existing working features should not be removed or unnecessarily rewritten during migration.

## 3. Final Application Architecture

I recommend building the desktop application using a modular architecture rather than putting everything into one large application file.

### 3.1 Recommended technology stack

[Tauri: Building Tiny, Fast, and Secure Native Apps | by asierr.dev | Medium](https://images.openai.com/static-rsc-4/616asBoUMuVihwE4xwNEttfdUjBZ2BY0eEnChoAyjdMU5AaVsN_AI8qjpC7Z-GBwBREMKO4__NnM4B2rOITE4_-StDCtJCN7EOIN9O0E4nyDLApu7jlXEHCbiZg0rvZBIZFJKqMGORuom_KUZdrvPL9yX2VFX0kZ6hghR3ynq1g?purpose=inline)

Tauri 2 + Rust

Desktop application framework and native Windows integration

Recommended

[React + TypeScript: Smarter State Management with useState and readonly - DEV Community](https://images.openai.com/static-rsc-4/cacXJztmtcgtvVsBKfWaXGT7KjINjxpaLYcQHFnN8yvF8coav1A9NP8Fy844rX8KvbfkRo7YNvD2DU57pGHVGqyAeUhLrZKdAx6B_0Ixc48wK26uoOcqG7S1C0IGjRV1RUkFgLwE6t6zXRtjAqKUHicH7jxl72Wea9x0ZTdO2t8?purpose=inline)

React + TypeScript

Frontend, dashboard, grid layouts and interactive components

[Free Download SQLite Logo in Vector Formats](https://images.openai.com/static-rsc-4/4xTVn01t1WPxD08-pKJLia1IP4Eg27txL8vqYML4j7hKw2D3oT7c_-pyHXrtJPFliXkMD5H44EGTY8hwILOMR7btgsWrcwdGnmNQUuhlfNLAs4_ujaKWtnUJKdymevunuvjz7kto60B5tNh8kr9s34pMZsPEAlwZ43A_ChinDr4?purpose=inline)

SQLite

Local database for profiles, monitoring, settings and history

[Building a cross platform Rust CI/CD pipeline with GitHub Actions](https://images.openai.com/static-rsc-4/AIBv059WEUbUQJJxX5ILTs3wLPBOexEPkq12X3rnJVCz1eIfqPv5RGBKMJpBeqo2114TUE1XKqSk0_7AdyS6Blj7aWXxQiWHjYypGEmZTSBw8wvpEwji9k8kUvworAhMgY_SCXFUxg3_xJb8gIqgJ7ED9Yhyu_AA2vinS71MhOE?purpose=inline)

Rust background services

Scheduling, downloads, file operations and application lifecycle

Additional technologies:

- Vite for frontend development and production builds.
- Tailwind CSS for styling.
- Lucide React for icons.
- TanStack Query for backend data synchronization.
- SQLite migrations for database version management.
- Windows native notifications through Tauri plugins or native integration.
- Rust asynchronous networking for downloads and scheduled tasks.
- FFmpeg integration as an optional media utility for inspecting supported video files.
- Markdown generation for activity reports.
- ZIP generation for bulk download archives.

### 3.2 Why I recommend Tauri instead of Electron

- Smaller application footprint.
- Lower memory consumption in typical desktop configurations.
- Native Windows functionality.
- Rust-based backend.
- Existing React frontend can be reused.
- Suitable for a local-first application.
- Can package the application for Windows.
- Supports communication between the React frontend and native backend.

Electron remains a valid alternative, but Tauri is my first recommendation for this particular project.

### 3.3 Portable EXE requirements

The application should support:

- Portable Windows executable distribution.
- No mandatory installation wizard.
- Customizable application data directory.
- Portable database storage.
- Portable settings.
- Portable activity logs.
- Portable download directory.
- Automatic creation of required directories.
- No dependency on browser localStorage.
- Graceful shutdown and database recovery.
- Application updates without losing user data.

I recommend offering two distribution formats:

- `Charlie-MJ-Insta-Viewer-Portable.zip`
- `Charlie-MJ-Insta-Viewer-Setup.exe`

The portable distribution should have a structure similar to:

```
Charlie-MJ-Insta-Viewer/
│
├── Charlie-MJ-Insta-Viewer.exe
│
├── data/
│   ├── database/
│   │   └── insta-viewer.db
│   │
│   ├── settings/
│   │   └── app-settings.json
│   │
│   ├── cache/
│   │
│   └── thumbnails/
│
├── Downloads/
│   ├── Instagram Profiles/
│   ├── Instagram Stories/
│   ├── Instagram Highlights/
│   ├── Instagram Posts/
│   ├── Instagram Reels/
│   └── Instagram Reposts/
│
├── activity/
│   ├── daily/
│   ├── weekly/
│   ├── monthly/
│   └── all-activity.md
│
├── backups/
│
└── logs/
```

The application should also offer a setting to store all application data alongside the EXE or in the Windows user data directory.

Important: A portable package does not necessarily mean a completely dependency-free single EXE. WebView2 and native runtime requirements must be handled during packaging and tested on clean Windows installations.

# 4. Complete Application Feature Set

## 4.1 Home Dashboard

[Dashboard UI Design for Modern Digital Services by khushboo kumari on Dribbble](https://images.openai.com/static-rsc-4/Sfl27kEZvZhjg503MJTngAiWzcsYoR9m_zMftCyqEqqvoTqcmoRU0O_imjCTHWPiCflPJm2sO83spa5WrmvFgYdQ521k_w6B61TMfQBh4ZRlqjhUFs2y3M8ykzpRkR2dUYkljaeUikZHj_S9ALhUmU1TpcBU7Ekimc7Yb3L8hzk?purpose=inline)

[dribbble.com](https://dribbble.com/shots/26325444-Dashboard-UI-Design-for-Modern-Digital-Services)

The dashboard should provide an overview of everything happening inside the application.

- Total monitored Instagram profiles.
- Currently available profiles.
- Profiles with unavailable or restricted status.
- Profiles that recently changed availability status.
- Profiles with newly detected Stories.
- Newly detected Posts.
- Newly detected Reels.
- Newly detected reposts.
- Newly detected Highlights when available.
- Total downloaded media.
- Total downloaded storage size.
- Active download tasks.
- Failed download tasks.
- Pending monitoring tasks.
- Last successful monitoring time.
- Next scheduled monitoring time.
- Recent notifications.
- Recent application activity.

### Dashboard widgets

- Monitored Profiles.
- New Stories.
- New Posts.
- New Reels.
- New Reposts.
- Recent Downloads.
- Recent Activity.
- Monitoring Status.
- Upcoming Scheduled Checks.
- Storage Usage.

### Dashboard quick actions

- Add Instagram Profile.
- Start Monitoring.
- Pause All Monitoring.
- Open Download Manager.
- Open Saved Library.
- Generate Activity Report.
- Open Settings.

## 4.2 Instagram Profile Management

This should be one of the application's primary modules.

### Profile Search

- Search using Instagram username.
- Search using a complete Instagram profile URL.
- Automatically extract usernames from pasted URLs.
- Remove unnecessary `@` characters.
- Validate usernames.
- Show search progress.
- Display profile loading errors.
- Retry unsuccessful searches.
- Avoid creating duplicate profile records.

### Profile Information

Display available information:

- Username.
- Display name.
- Biography.
- Profile picture.
- Full-size profile picture.
- Verified badge, when available.
- Followers count.
- Following count.
- Total posts count.
- Account visibility status.
- Profile URL.
- Last checked timestamp.
- Last detected activity.
- First added date.

### Profile Management

- Add multiple usernames.
- Remove usernames.
- Edit monitored profiles.
- Add profile notes.
- Add profile tags.
- Mark profiles as favorites.
- Enable or disable individual monitoring.
- Pause monitoring temporarily.
- Set individual checking schedules.
- View profile monitoring history.
- Open a profile's complete content timeline.

### Suggested profile categories

- Favorites.
- Frequently Monitored.
- Recently Added.
- Monitoring Enabled.
- Monitoring Paused.
- Recently Updated.
- Unavailable Profiles.

## 4.3 Advanced Instagram Story Viewer

[Anonymous Instagram Story Viewer – Watch and Download Stories Online](https://images.openai.com/static-rsc-4/Uv-7V-qZ2eUT_tEIycALeFwz0OW6iC_4kD6kkVn6Uy4mnO2xa-gAZmF1AKsvvacf3JbrbhPYLELOTwxNrMwS_DpgroPCld0QkWC2FUcwVvVCIHNljdPW2h34gQdAzcdBc3qos0npxZ6YQzQnt6STlOipFJ2j8OtfwPE3LOVKnSo?purpose=inline)

[BBB 24: conheça app usado para descobrir participantes do reality](https://images.openai.com/static-rsc-4/7YTzmA3o1yo2tTMU-cdtnhYDmuY_dK2ZX1Gyp2HzIIlnS6b-MDqsji4QFFcaR2xhWlfb0IlAxJDzxlsd0F3oGO7WGTj5PGyNCXqRei_psIQAtHU-dk0JazPXOu1Cwj-DNgGRI11F_YYPvCtCYJnnYZ2wAXv_zb7tHjfRANF50Ho?purpose=inline)

[Social Media Scheduling Tool UK | AI-Powered Posting Platform | Puurfect Post](https://images.openai.com/static-rsc-4/0meCQvcRzyIFgoRg0JFHq_Sl3uMggXBR8U35el-2PCJNVJqymyjKhJ0bsFl6_IlH-TQ17zMzec0C-4dirbo-5GYtLmdTJYpLDMgGrRolvfTQHGrVl-eB54mydyrQ9oYW1TvoaoBltaZz5NWGubOu58bviZqJGUVWoZbKhTuN5SY?purpose=inline)

This should be one of the most important modules because of your interest in InSnoop's timestamp and mention functionality.

### Story Viewing

- View available public Stories.
- Story image preview.
- Story video playback.
- Sequential Story navigation.
- Previous and Next controls.
- Story progress indicator.
- Pause and resume video.
- Full-screen Story viewing.
- Story thumbnails.
- Story grid view.
- Individual Story download.
- Multi-Story download.
- Save Story to Library.

### Story Metadata Inspector

Every Story should have a dedicated inspection panel.

Display the following whenever the source actually provides the information:

- Instagram username.
- Story media ID.
- Actual publication timestamp.
- Publication date.
- Publication time.
- Time zone.
- Detection timestamp.
- Time between publication and detection.
- Story expiration estimate.
- Media type.
- Original media dimensions, when available.
- Tagged usernames.
- Mentioned usernames.
- Location.
- Music information.
- External link information.
- Original media URL, when available.
- Download status.

### Exact Story Timestamp System

I recommend separating three different timestamps:

- Original publication time: When Instagram or an authorized provider says the Story was published.
- First detection time: When your application first discovered the Story.
- Download time: When the application saved the media locally.

For example:

```
Instagram Username: example_user

Story Published:
14 October 2026

Original Time:
08:42:17 AM

First Detected:
14 October 2026

Detection Time:
08:45:03 AM

Download Time:
14 October 2026

Download Time:
08:47:21 AM
```

This distinction is essential. If the source provides only an approximate age, the application must not present an estimated timestamp as an exact publication time.

### Story Mention Detection

This feature should receive its own dedicated system.

- Extract available structured mention metadata.
- Display mentioned Instagram usernames.
- Display tagged users where available.
- Identify multiple mentions.
- Link mentioned usernames to their profile records.
- Show the original Story associated with each mention.
- Display the timestamp associated with the Story.
- Maintain a searchable mention history.
- Filter Stories by mentioned username.
- Notify when a new Story containing a detected mention appears.
- Allow the user to open the Story Inspector directly from the notification.

### Mention Search Examples

- Show all Stories mentioning `@username`.
- Show all Stories mentioning a particular person.
- Show Stories containing multiple mentions.
- Show Stories with no detected mentions.
- Show mentions detected during a selected date range.

Important technical limitation: Your frontend already has `postedAt`, `exactTimeAvailable` and `mentions` fields, which are excellent data-model foundations. However, they do not themselves retrieve this information. The actual timestamp and mention extraction must be supported by the authorized data source. If metadata is unavailable, the application should explicitly display `Unavailable` rather than fabricate it.

## 4.4 Instagram Story Calendar

This is an excellent feature to expand from your existing frontend.

[Starvy - AI SaaS Dashboard by Illiyin Studio on Dribbble](https://images.openai.com/static-rsc-4/xeBPfdCOf8KG6VZx6jScCI8oJBIUmIlCkHZ8iIYcwDYZNDvTmlgRd3OFTkpkunLjj17p8jZCKRTR-6GWx-wAvqJiizx9DuHtum14TMho-I4yXrijnZPQf6V5nGJRiTJIsSEgpVgyEwC7FHrIucBwsEBl01tglVoVQt9UlrauTnY?purpose=inline)

[dribbble.com](https://dribbble.com/shots/25651012-Starvy-AI-SaaS-Dashboard)

- Monthly calendar.
- Weekly calendar.
- Daily timeline.
- Display Stories by publication date.
- Display multiple Stories on the same day.
- Different indicators for photos and videos.
- Mention indicators.
- New Story indicators.
- Downloaded Story indicators.
- Click a calendar event to open Story Inspector.
- Filter by Instagram username.
- Filter by mentioned user.
- Filter by date.
- Search historical Story records.

Additional functionality:

- Compare activity between different days.
- Identify frequently active profiles.
- View Story publishing patterns.
- Display daily Story counts.
- Display weekly Story counts.
- Export calendar data to Markdown or CSV.

## 4.5 Instagram Highlights Viewer

[Instagram Highlight Viewer â€“ Watch Highlights Anonymously - Stories Watch](https://images.openai.com/static-rsc-4/pMZHM7oTgdIQSYAEJvPTco8lGOWn4iZym0QHaiRkTXchV1OgqX2gcxP2Zr0nHfEA5u_xdKStQf-Q1gW6ikJiH9ns_ZOl1y2hVzKf-VeT9CSMVuGGSwzHZed6GzseFyo04HJFABPNKsq6y6H7VsKC1bg__Gpw4NqWvDpU8pLVDm4?purpose=inline)

[storieswatch.com](https://www.storieswatch.com/blog/instagram-highlight-viewer-watch-highlights-anonymously)

- Display available public Highlight collections.
- Highlight cover images.
- Highlight names.
- Highlight media counts, when available.
- Open individual Highlight collections.
- Browse photos and videos.
- Previous and Next navigation.
- Full-screen viewer.
- View individual Highlight Stories.
- Inspect available metadata.
- Download individual Highlight media.
- Download complete available collections.
- Save Highlights to the local library.
- Search Highlights.
- Sort by available collection information.

### Highlight Metadata

- Original creator.
- Highlight title.
- Media ID.
- Story timestamp, if available.
- Detection timestamp.
- Mention information, if available.
- Media type.
- Download status.

## 4.6 Instagram Posts Viewer

[Instagram Redesign - Desktop - Dark | Diseño de sitios web, Diseño de paginas web, Portafolio de diseño web](https://images.openai.com/static-rsc-4/AIHKadG-S4A6j2oFZmqsaoPgU3expbhf_xvYZny_eYPnvJqIENoi33-rxYsHznwFrnhHSe2pHtW-MOSosjeCm8D0CB8h-8cqmSNYr6znvF8j0fgm3fq1PLmTFDmkJAXQQguMA0U7kwJrrXzNJbkRPRNOpWfnwWLTndnf3jlvcdY?purpose=inline)

[pinterest.com](https://www.pinterest.com/pin/instagram-redesign-desktop-dark--626141154432195315/)

- Display available public posts.
- Grid-based post gallery.
- Single-photo posts.
- Video posts.
- Carousel posts.
- Multiple images inside one carousel.
- Post captions.
- Publication timestamps.
- Like counts, where available.
- Comment counts, where available.
- Post thumbnails.
- Full-resolution preview when available.
- Original post URL.
- Post detail inspector.
- Individual media downloads.
- Complete carousel downloads.
- Multi-select downloads.
- Save posts to the local library.

### Advanced Post Features

- Filter image posts.
- Filter video posts.
- Filter carousel posts.
- Sort newest to oldest.
- Sort oldest to newest.
- Search post captions.
- Filter by publication date.
- Filter downloaded and undownloaded posts.
- Display original creator information.

## 4.7 Instagram Reels Viewer

[CampusReels | Victor Timi](https://images.openai.com/static-rsc-4/r170u7R3TymMrJFxxLocS-YWmZgNQE-sGj-Ybm2o1mlrfGthbtsfZiqWDlk7w9j2K8f0R0IQt0LaVqYvjrnSTXwozZNLZ_QkIYnTHqDSuA0cYnVQr465JecYCznu8DmY6xGabKTzzDNOlPy0GRwza9kNkv4Kv_dnON5lM2WQsTw?purpose=inline)

[victortimi.com](https://www.victortimi.com/projects/campusreels)

- Dedicated Reels section.
- Reels grid.
- Video thumbnails.
- Embedded video player.
- Caption information.
- Publication timestamp, when available.
- View counts, when available.
- Original creator information.
- Full-screen playback.
- Individual Reel downloads.
- Multi-select Reel downloads.
- Save Reels to Library.
- Search Reels.
- Sort by available publication information.

### Video Player Features

- Play and pause.
- Volume control.
- Playback speed.
- Full-screen mode.
- Seek bar.
- Video duration.
- Previous and Next Reel.
- Picture-in-picture where supported.

## 4.8 Instagram Repost Viewer

Your existing frontend already includes a Repost data model, so this should remain an independent module.

[Social Media Dashboard UI by George Chichua on Dribbble](https://images.openai.com/static-rsc-4/Z1Y1m0i8rdkqRsN3BAq884o76iKF_DztMpdcVxulqLg5k9iPJSV4P4pqh56yPKBdzQPVgttQUluQCSTHIiKVKdzguQGOH4AbzYsg18Td4uXltTKDBKUEmxMddrrAYlXdh77SPYVeu35b42CNDzhf3ql8sdrBGJBW6ueI3cbIKio?purpose=inline)

[dribbble.com](https://dribbble.com/shots/23594402-Social-Media-Dashboard-UI)

- Display available repost records.
- Identify the account that reposted the content.
- Display original creator.
- Display original media.
- Display original post URL.
- Display repost timestamp, when available.
- Display original publication timestamp, when available.
- Preview reposted photos and videos.
- Open the original content.
- Download supported repost media.
- Save repost records.
- Filter by original creator.
- Search repost history.

### Repost Identification

Store the following information:

- Reposting username.
- Original creator username.
- Original media ID.
- Original post URL.
- Repost publication time, if supplied.
- First detection time.
- Original media type.
- Download information.

Do not treat an ordinary Reel shared through an external link as a confirmed native Instagram repost. Keep those classifications separate.

## 4.9 Instagram Profile Picture Downloader

[We Are Dcoded](https://images.openai.com/static-rsc-4/9Avq2DLWJzFJXyiM4JlxukEAYbIVF8qO3HRMedmWEv7ZtYUJY-p67555xEGGZAYk9epD7El3x3Nr3RuVdYBgZtPevKszf9COtO-j5qhsUONg4EMceR_88wlq1m7ZALV3VkK0UqRWDkDRthmU4qLiu2m4F2_duXMfUNPaKyi2YCs?purpose=inline)

[wearedcoded.com](https://www.wearedcoded.com/)

- Profile picture preview.
- Full-size image viewer.
- Zoom.
- Original available image resolution.
- Image dimensions.
- Download profile picture.
- Save profile pictures in JPG, PNG or WebP where supported.
- Replace older profile picture snapshots with new versions.
- Maintain historical profile picture versions.
- Compare previously saved profile pictures.
- Display the date each version was first detected.

This last feature is a useful addition: you could maintain a local history of profile picture changes for each monitored username.

# 5. Automatic Profile Monitoring Bot

Core Productivity Feature

This is probably the most important additional system to develop because it will replace your daily manual routine of opening StorySaver, InSnoop, AnonyIG and Pixnoy.

[GYB Agent - Growth Your Business with AI Agents](https://images.openai.com/static-rsc-4/JK1Bc7jfLSzMWKNAlsdvEYeWCvlCnmBEDY2zuZliyl7rkZjbs0lIhfvFntAoGMoqXHYZRehDMpW7UqMHzeZQRvz-wUERz4ujZIDVrZJ8-joKeLAuuqckm0hknprQxuBiPyVCzyLONR9jm2kZr9ARgG-1Gg8dHrNMaXR0-VI3H_Q?purpose=inline)

[gybagent.com](https://gybagent.com/)

## 5.1 Multi-Profile Monitoring

- Add multiple Instagram usernames.
- Monitor each username independently.
- Enable or disable monitoring for individual profiles.
- Monitor all configured profiles.
- Pause all monitoring.
- Resume monitoring.
- Remove profiles from monitoring.
- Set different schedules for different profiles.
- View the last successful check.
- View the next scheduled check.
- View individual monitoring status.
- Retry unsuccessful checks.

## 5.2 Automatic Profile Availability Monitoring

You specifically want to detect when an account changes from private to public.

Introduce a dedicated feature called:

Profile Visibility Monitor

Functionalities:

- Periodically check the availability and visibility status of configured profiles through a supported data provider.
- Record the last observed visibility state.
- Detect transitions between observed states.
- Identify when a previously inaccessible profile becomes publicly accessible.
- Record the first time the application detects the change.
- Display a visibility change timeline.
- Send a Windows notification when a monitored profile becomes publicly accessible.
- Automatically initiate a content check after the profile becomes accessible.
- Identify newly available Stories, Posts, Reels and other supported content.
- Notify you when new content is discovered.
- Allow individual profiles to have different visibility-monitoring settings.

### Example monitoring timeline

```
Profile: @example_user

Previous Status:
Unavailable / Private

New Status:
Publicly Accessible

Detected:
15 October 2026
08:35 AM

Next Action:
Check available public content

Result:
2 New Stories Detected
1 New Post Detected
```

The application should distinguish private, unavailable, deleted, blocked, rate-limited and temporary provider failures. A failed request must never automatically be classified as a private account.

## 5.3 Monitoring Scheduler

You should have complete control over how frequently the bot checks profiles.

Suggested intervals:

- Every 5 minutes.
- Every 10 minutes.
- Every 15 minutes.
- Every 30 minutes.
- Every hour.
- Every 3 hours.
- Every 6 hours.
- Every 12 hours.
- Once per day.
- Custom schedule.

Also include:

- Specific days of the week.
- Start and end times.
- Time-zone selection.
- Individual profile schedules.
- Global monitoring schedule.
- Monitoring pause periods.
- Quiet hours.
- Maximum concurrent jobs.
- Automatic retry policy.
- Exponential backoff for temporary failures.
- Randomized scheduling within a user-defined window to avoid synchronized request bursts.
- Rate-limit awareness.

My recommendation: Make the checking interval configurable, but never promise that a profile can be checked successfully at every selected interval. Actual checking depends on provider availability, access restrictions and permitted request limits.

## 5.4 Automatic New Content Detection

The bot should maintain a record of previously discovered media.

For each monitored username:

- Retrieve currently available content through the configured provider.
- Compare content IDs against the local database.
- Identify newly discovered Stories.
- Identify newly discovered Highlights or Highlight media.
- Identify new Posts.
- Identify new Reels.
- Identify supported repost records.
- Identify profile picture changes.
- Identify changes in available profile information.
- Record first detection timestamps.
- Prevent duplicate notifications.
- Add new items to the activity timeline.
- Offer automatic downloading if enabled.

### Duplicate Detection

Use multiple identification methods:

- Provider media ID.
- Original content URL.
- Media type.
- Username.
- File checksum for downloaded files.
- Perceptual image hash as an additional duplicate-detection method.

The system should not assume that two media items are duplicates merely because they have identical captions.

## 5.5 Automatic Download Bot

Add a separate setting for automatic downloads.

For each monitored profile, let the user select:

- Automatically download new Stories.
- Automatically download new Highlight media when detected.
- Automatically download new Posts.
- Automatically download new Reels.
- Automatically download new Repost media.
- Automatically save updated profile pictures.
- Download only photos.
- Download only videos.
- Download all supported media.
- Ignore already downloaded items.
- Save everything into the configured category directories.

Also include:

- Automatic filename generation.
- Download progress.
- Download failure retry.
- Duplicate prevention.
- Disk space monitoring.
- Download queue management.
- Automatic activity logging.

### 5.6 Bot Control Panel

Create a dedicated interface for controlling the automation system.

- Start Bot.
- Pause Bot.
- Resume Bot.
- Stop Bot.
- Start monitoring for selected profiles.
- Start monitoring for all profiles.
- View running tasks.
- View pending tasks.
- View failed tasks.
- View completed tasks.
- View next execution time.
- View last execution time.
- View bot logs.
- Clear completed task history.
- Retry failed tasks.

The bot should be able to continue running when the main application window is minimized.

For reliability, I recommend a background process managed by the desktop application, with an optional Windows startup setting. Closing the application should stop monitoring unless you explicitly configure a separate background mode.

# 6. Windows Notification System

[Windows 11 Is Officially Out with Centered Start Menu](https://images.openai.com/static-rsc-4/JFiuq46Jk_OU3nM1VsRmNTaJBZEuZaNZKjANp2o5nFu0w02vRNVsiAZtgJrC16TpOURbr5MO70VCa6KDjN3FAM2qa-n3gBvw6rSBlj85i5nDN5iQiSpLWZEV6DM_xNmvL2PKVIYSTTf0zqVouW733J0t-AX_lUPnBZ3yQEuvizI?purpose=inline)

[wccftech.com](https://wccftech.com/windows-11-is-officially-out-with-centered-start-menu/)

You specifically requested two kinds of notifications:

- Notifications when new Instagram content is detected.
- Notifications whenever you click buttons inside the application.

I recommend implementing both through a unified notification service.

## 6.1 Instagram Activity Notifications

Display a Windows desktop popup when:

- A monitored profile becomes publicly accessible.
- A new Story is detected.
- A new Story contains a detected mention.
- A new Post is detected.
- A new Reel is detected.
- A new Repost is detected.
- A new Highlight item is detected.
- A profile picture changes.
- A monitoring task fails.
- A download finishes.
- A download fails.

### Example Story Notification

Charlie MJ Insta Viewer

Just now

[刘悦](https://images.openai.com/static-rsc-4/veUH2oO1fTTRzJ63HsU2V1DlWIBra7d1U_ezDHy9t3L5_o0QtcdzUIuYCxB4qGeMmxAVBrew6-RoMduo_RcRVZzHapyN1jE7X6PQ-0J9_Zgr2qFo8FJ9IPRGYIMSY5W7BCZ3jGcy4jH-0PfVrd7dPSknHTrIf4w6WtrpnRrT2-Q?purpose=inline)

New Instagram Story

@example_user shared a new Story.

Detected: 08:45 AM · 1 new Story

New content

Story detected

Open Story · View Profile · Download

## 6.2 Button Interaction Notifications

You also want a popup whenever you click a button.

Implement a configurable toast notification system.

Examples:

- Profile added successfully.
- Profile removed successfully.
- Monitoring started.
- Monitoring paused.
- Monitoring stopped.
- Story downloaded successfully.
- Post saved successfully.
- Settings updated.
- Activity report generated.
- Search completed.
- History cleared.

Use different notification styles:

- Success.
- Information.
- Warning.
- Error.
- Progress.

### Notification Settings

- Enable or disable button notifications.
- Enable or disable Instagram activity notifications.
- Enable or disable download notifications.
- Configure notification duration.
- Enable or disable notification sounds.
- Enable or disable notification previews.
- Configure quiet hours.
- Configure notification categories.

Important: Avoid displaying success messages before an operation actually completes. For example, show `Download started` when the queue accepts a job and `Download completed` only after the file is successfully saved.

# 7. Built-in Advanced Downloader

Core Module

[Kick Video Downloader - Kick Stream Replay MP4 Saver | DownForge](https://images.openai.com/static-rsc-4/nAEP8QHDSeXFeLTx0ONQPpfZMFIMNjlwDgvbB_6OMRa7dqeRqu37m86JzWf7oIqKl_CPt9XQh8ieKCJdPlo2R3DBlJegnnDVKEnyYxz6tqCk6XlnXl0X1_sj0Cn6bY9a1vImVRZKDJ0Ye8cSnkJ6kaQ0qUDIYXFnTGvDx3i1Kt8?purpose=inline)

[downforge.com](https://www.downforge.com/en/download/kick-video-downloader)

This should be an independent downloading engine, not a collection of individual download buttons with separate implementations.

## 7.1 Supported Download Categories

- Instagram Profile Pictures.
- Instagram Stories.
- Instagram Highlight Stories.
- Instagram Highlight Covers.
- Instagram Posts.
- Instagram Carousel Posts.
- Instagram Reels.
- Instagram Reposts.

## 7.2 Download Functionality

- Download individual media.
- Download multiple selected items.
- Download complete available Story collections.
- Download available Highlight collections.
- Download complete carousel media.
- Download multiple Reels.
- Download profile pictures.
- Automatic downloads through the monitoring bot.
- Manual downloads through media viewers.
- Download by supported Instagram URL.
- Download from selected media cards.

## 7.3 Download Manager

Include a dedicated Download Manager tab.

- Download queue.
- Active downloads.
- Completed downloads.
- Failed downloads.
- Paused downloads.
- Pending downloads.
- Download progress percentage.
- Download speed.
- File size.
- Estimated remaining time, when calculable.
- Cancel download.
- Pause download where supported.
- Resume interrupted downloads where supported.
- Retry failed downloads.
- Open containing folder.
- Open downloaded file.
- Copy file path.
- Clear completed entries.
- Remove failed entries.

## 7.4 Automatic Filename System

This is a requirement I would treat as mandatory.

Your requested filename pattern:

```
InstagramUsername-InstagramCategory-Day-Month-Year_Time_AM/PM
```

I recommend using a consistent and Windows-compatible format.

### Final naming convention

```
{username}-{category}-{day}-{month}-{year}_{hour}-{minute}_{AM/PM}.{extension}
```

Examples:

```
example_user-instagram-profile-2-October-2026_10-05_AM.jpg

example_user-instagram-story-2-October-2026_10-05_AM.mp4

example_user-instagram-highlight-story-2-October-2026_10-05_AM.jpg

example_user-instagram-highlight-cover-2-October-2026_10-05_AM.jpg

example_user-instagram-post-2-October-2026_10-05_AM.jpg

example_user-instagram-reel-2-October-2026_10-05_AM.mp4

example_user-instagram-repost-2-October-2026_10-05_AM.mp4
```

### Filename rules

- First part: Instagram username.
- Second part: Content category.
- Third part: Date.
- Fourth part: Time.
- Last part: Correct file extension.
- Use lowercase category names.
- Replace invalid Windows filename characters.
- Preserve original media extensions where practical.
- Handle duplicate filenames automatically.
- Maintain the original filename in metadata when available.

### Important timestamp setting

Provide two filename timestamp options:

- Download timestamp.
- Original publication timestamp, when reliably available.

Default should be download timestamp because it is always known locally.

## 7.5 Download Folder Structure

```
Downloads/
│
├── Instagram Profiles/
│   └── example_user/
│
├── Instagram Stories/
│   └── example_user/
│
├── Instagram Highlights/
│   └── example_user/
│       ├── Covers/
│       └── Stories/
│
├── Instagram Posts/
│   └── example_user/
│       ├── Images/
│       ├── Videos/
│       └── Carousels/
│
├── Instagram Reels/
│   └── example_user/
│
└── Instagram Reposts/
    └── example_user/
```

## 7.6 Additional Downloader Features

- Custom download locations.
- Category-specific folders.
- Username-specific folders.
- Automatic folder creation.
- Preserve original available resolution.
- File integrity checks.
- Duplicate detection.
- Download queue priorities.
- Maximum simultaneous downloads.
- Disk space warnings.
- Failed download reports.
- Download history.
- Export download history.
- Bulk ZIP archives.
- Automatic cleanup of temporary files.

# 8. Saved Media Library

[CatchBan - 创作者素材工作台](https://images.openai.com/static-rsc-4/xukr0_qkgj8uVEVhqWOXfjeLFnEz3JDGxplGf5oSORwQVPLM6ZYWl6r7llN2us8uA7v7ll95Aj4nnHVOA-snloTIpYrhZcGTrX4IIXZ0OIJPfTVATaORxOkbswc10JgyfaE35MjmYVxev8o8FhVRtdWthUXQWSsYJK16RauD2Hw?purpose=inline)

[catchban.com](https://catchban.com/)

Create a dedicated library for everything you save.

### Library categories

- All Media.
- Profile Pictures.
- Stories.
- Highlight Stories.
- Highlight Covers.
- Posts.
- Carousels.
- Reels.
- Reposts.

### Library functionality

- Grid view.
- List view.
- Thumbnail previews.
- Media playback.
- Image zoom.
- Search by username.
- Search by filename.
- Filter by category.
- Filter by date.
- Sort newest first.
- Sort oldest first.
- Sort by file size.
- Filter downloaded media.
- Select multiple files.
- Delete selected files.
- Open containing folder.
- Copy file location.
- View file metadata.
- View original publication date.
- View download date.
- View associated Instagram profile.
- Add personal notes.
- Add favorites.
- Create custom collections.

### Additional recommendation: Media Collections

Allow the user to create collections such as:

- Favorite Stories.
- Important Posts.
- Reels Collection.
- Profile References.
- Research Collection.
- Temporary Downloads.

This will make the application more useful as a long-term media archive.

# 9. Activity and History Management

[Clouisle - Enterprise AI Platform V0.2.9 Public Beta | Clouisle](https://images.openai.com/static-rsc-4/mIgt2qT7a0DzW6sCEk7ldSl8IRiX1q3iMF_z0LDNriuXtthSxZ2KZoDNNXfLxD-91srhfuPxsyYzm4qQnmWoi3URvfNWCChytaa4Xar79oRvpYZRnUFAyuJxRnmX9wTgg8rXD6t8ATD2cXbXANfN-Wb4rLyv121zkyIvT-QxLs0?purpose=inline)

[clouisle.asia](https://clouisle.asia/en)

This is another feature I strongly recommend implementing as an independent module.

## 9.1 Activity Tab

Every meaningful operation should generate an activity event.

Examples:

- Profile added.
- Profile removed.
- Profile searched.
- Profile visibility changed.
- Monitoring started.
- Monitoring stopped.
- Story detected.
- Story mention detected.
- New Post detected.
- New Reel detected.
- Repost detected.
- Profile picture changed.
- Media downloaded.
- Download failed.
- File deleted.
- Settings changed.
- History cleared.
- Activity report generated.

## 9.2 Activity Categories

- Profile Activity.
- Story Activity.
- Mention Activity.
- Post Activity.
- Reel Activity.
- Repost Activity.
- Download Activity.
- Bot Activity.
- Notification Activity.
- Settings Activity.
- Application Activity.

## 9.3 Markdown Activity Logs

All activity should be recorded in Markdown files inside the `activity/` directory.

Recommended structure:

```
activity/
│
├── daily/
│   ├── 2026-10-14.md
│   └── 2026-10-15.md
│
├── weekly/
│   ├── 2026-W42.md
│   └── 2026-W43.md
│
├── monthly/
│   ├── 2026-10.md
│   └── 2026-11.md
│
├── profiles/
│   ├── example_user.md
│   └── another_user.md
│
├── downloads/
│   └── download-history.md
│
└── all-activity.md
```

### 9.4 Example Daily Activity Report

```
# Charlie MJ Insta Viewer
## Daily Activity Report

Date: 15 October 2026

### Profile Monitoring

- Profiles monitored: 12
- Profiles successfully checked: 10
- Profiles unavailable: 2
- Visibility changes detected: 1

### New Content

- Stories detected: 5
- Posts detected: 2
- Reels detected: 3
- Reposts detected: 1
- New Highlight items: 0

### Story Mentions

- Stories with detected mentions: 2
- Unique mentioned usernames: 3

### Downloads

- Profile pictures: 1
- Stories: 5
- Posts: 2
- Reels: 3
- Reposts: 1

### Errors

- Failed monitoring tasks: 2
- Failed downloads: 0

### Detailed Timeline

08:35 AM - Profile became publicly accessible.
08:45 AM - New Story detected.
08:47 AM - Story downloaded.
09:10 AM - New Reel detected.
09:12 AM - Reel downloaded.

### Summary

Monitoring and downloading activities
for the selected date.
```

The report above is a format example, not actual retrieved data.

## 9.5 Activity Report Generator

Provide report generation options:

- Generate today's report.
- Generate yesterday's report.
- Generate a specific date's report.
- Generate weekly reports.
- Generate monthly reports.
- Generate custom date-range reports.
- Generate reports for individual profiles.
- Generate download-only reports.
- Generate monitoring-only reports.
- Generate mention-only reports.
- Generate complete application reports.

### Export formats

- Markdown (`.md`).
- Plain text (`.txt`).
- JSON (`.json`).
- CSV (`.csv`).
- PDF (`.pdf`).

### History Management

- Search activity.
- Filter by date.
- Filter by username.
- Filter by activity category.
- Clear selected history.
- Clear all history.
- Archive older logs.
- Export selected records.
- Open Markdown files directly.
- Restore historical records from backups where available.

Important implementation detail: SQLite should be the authoritative activity record. Markdown files should be generated from database events. This prevents losing activity when a Markdown export fails or the application closes unexpectedly.

# 10. Followers and Following Viewer

You also requested the ability to view followers and following lists.

I recommend including a dedicated section:

Followers & Following Explorer

Potential functionality:

- Display follower information when available through an authorized source.
- Display following information when available.
- Search usernames within an available list.
- Search profile names.
- Sort alphabetically.
- Open associated profiles.
- Compare previously saved snapshots.
- Detect changes between available snapshots.
- Export available lists to CSV or JSON.

One important technical distinction: follower and following counts are not the same as access to the actual lists. The official Instagram API does not provide a general-purpose endpoint for retrieving arbitrary users' complete follower and following lists. Therefore, this module should support actual lists only where an authorized provider makes them available.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.postman.com\&sz=32)

Postman API Network

+1



# 11. Advanced Search and Discovery

I recommend making Search a standalone module rather than limiting it to a username input.

### Search functionality

- Username search.
- Profile URL search.
- Post URL search.
- Reel URL search.
- Story URL search, where supported.
- Search downloaded media.
- Search Story mentions.
- Search activity logs.
- Search saved profiles.
- Search media captions.
- Search filenames.

### Advanced filters

- Username.
- Content category.
- Publication date.
- Detection date.
- Download date.
- Media type.
- Mentioned username.
- Download status.
- Profile availability.
- Monitoring status.

### Quick Search

Add a global search bar that can search:

- Profiles.
- Stories.
- Posts.
- Reels.
- Reposts.
- Downloaded files.
- Activity records.

# 12. Advanced Features I Recommend Adding

These additions can make the project considerably more useful than simply combining the four websites.

## 12.1 Profile Activity Intelligence

- Display each profile's daily activity.
- Calculate available Story counts per day.
- Display publishing frequency.
- Display active and inactive periods.
- Show historical visibility changes.
- Display first and last detected activity.
- Identify profiles that frequently publish Stories.
- Compare activity across monitored profiles.

## 12.2 Story Mention Intelligence

- Dedicated mention dashboard.
- Search all detected mentions.
- Group Stories by mentioned username.
- Display when each mention was first detected.
- Display which monitored profile mentioned someone.
- Track mention history.
- Export mention history.
- Notification for newly detected mentions.

This should be a major differentiating feature of your application.

## 12.3 Profile Change Tracker

Maintain historical snapshots of available profile information.

- Username changes, if identifiable.
- Display name changes.
- Biography changes.
- Profile picture changes.
- Follower count changes.
- Following count changes.
- Post count changes.
- Visibility status changes.

Display a timeline of changes.

## 12.4 Automatic Story Expiration Tracker

- Record the first detection of each Story.
- Display estimated expiration.
- Display remaining estimated availability.
- Highlight Stories approaching expiration.
- Prioritize downloading newly discovered Stories.
- Notify when a detected Story is approaching expiration.

The expiration estimate should be based on the actual publication timestamp where available, not simply the time of discovery.

## 12.5 Smart Monitoring Priorities

Allow profiles to have different priorities.

- High Priority.
- Normal Priority.
- Low Priority.
- Monitoring Paused.

High-priority profiles can receive more frequent checks within the provider's permitted limits.

## 12.6 Media Comparison System

- Compare two profile pictures.
- Compare two downloaded images.
- Compare older and newer profile pictures.
- Compare available media versions.
- Detect visually similar images.
- Identify duplicate downloads.
- Display image dimensions and file sizes.

## 12.7 Smart Download Rules

Allow custom rules such as:

- Download every new Story.
- Download only video Stories.
- Download Stories containing detected mentions.
- Download only Posts from selected profiles.
- Download Reels automatically.
- Ignore duplicate media.
- Save only media above a selected resolution.
- Use different folders for different profiles.

## 12.8 Backup and Restore

- Backup SQLite database.
- Backup settings.
- Backup monitored profile lists.
- Backup saved metadata.
- Backup activity records.
- Export monitoring configurations.
- Restore previous backups.
- Schedule automatic backups.
- Configure backup location.
- Retain multiple backup versions.

## 12.9 Application Maintenance

- Clear temporary cache.
- Clear thumbnail cache.
- Remove orphaned database records.
- Detect missing downloaded files.
- Check database integrity.
- Display application version.
- Check for application updates.
- Export diagnostic logs.
- Restore default settings.

## 12.10 Keyboard Shortcuts

- `Ctrl + K`: Global Search.
- `Ctrl + D`: Open Downloads.
- `Ctrl + H`: Activity History.
- `Ctrl + P`: Add Profile.
- `Ctrl + ,`: Settings.
- `Ctrl + R`: Refresh Current View.
- `Ctrl + Shift + M`: Start/Pause Monitoring.
- `Esc`: Close dialogs or viewers.

Make shortcuts configurable.

# 13. Backend Architecture and Data Provider Strategy

This is the most important engineering decision in the project.

You need a real data-retrieval layer. The frontend alone cannot provide live Instagram content.

## 13.1 Provider-Based Architecture

Your current project already has:

```
src/services/api.ts
```

Preserve this architectural idea and expand it into a provider system.

Recommended structure:

```
src/
│
├── services/
│   ├── api.ts
│   ├── providers/
│   │   ├── provider-interface.ts
│   │   ├── official-provider.ts
│   │   ├── authorized-provider.ts
│   │   └── mock-provider.ts
│   │
│   ├── profile-service.ts
│   ├── story-service.ts
│   ├── post-service.ts
│   ├── reel-service.ts
│   ├── repost-service.ts
│   ├── mention-service.ts
│   ├── monitoring-service.ts
│   ├── download-service.ts
│   ├── notification-service.ts
│   └── activity-service.ts
│
├── desktop/
│   ├── commands/
│   ├── scheduler/
│   ├── downloader/
│   ├── notifications/
│   ├── database/
│   └── filesystem/
│
└── components/
```

### Provider interface

Each provider should implement clearly defined operations.

- Search profile.
- Retrieve profile details.
- Retrieve available Stories.
- Retrieve Story metadata.
- Retrieve available Highlights.
- Retrieve Posts.
- Retrieve Reels.
- Retrieve supported repost records.
- Retrieve available mention information.
- Retrieve available follower/following information.
- Retrieve downloadable media URLs.

Not every provider will support every operation.

Therefore, every provider should advertise its capabilities.

For example:

```
Provider: Authorized Provider A

Capabilities:

Profile Information: Supported
Public Posts: Supported
Stories: Not Supported
Story Timestamps: Provider Dependent
Story Mentions: Not Supported
Highlights: Not Supported
Reels: Supported
Reposts: Not Supported
Followers Lists: Not Supported
```

This prevents the application from showing buttons for functionality that its active provider cannot actually perform.

## 13.2 Important Instagram API Limitations

There is one major technical reality that must be addressed before development.

The official Instagram Platform API primarily supports Instagram Business and Creator accounts and their authorized integrations. Its capabilities are not equivalent to the third-party public-profile viewer websites.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.postman.com\&sz=32)

Postman API Network

+1



In particular:

- The official API is not a general-purpose interface for downloading arbitrary users' Stories.
- Arbitrary personal-account access is not supported through the official API.
- Complete arbitrary followers/following lists are not generally available.
- Story mention information is not universally available for unrelated profiles.
- Story timestamps cannot be assumed to be accessible for every account.
- Public profile discovery has eligibility and permission restrictions.

Meta's automated data collection rules also impose restrictions on automated collection without express written permission.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://vorplabs.com\&sz=32)

Vorp Labs

+1



Consequently, the application should use an approved provider or another source with appropriate authorization for each capability. Do not design the architecture around bypassing access controls, extracting private session cookies or evading rate limits.

### My recommended provider strategy

Layer 1 — Official Instagram API

- Integrate supported professional-account features.
- Support authorized account connections.
- Retrieve information permitted by granted permissions.
- Implement official authentication and token management.

Layer 2 — Authorized external data provider

- Allow integration with a legitimate provider that explicitly supports the required public-content functionality.
- Require documented API capabilities.
- Support API keys stored securely.
- Display unsupported operations clearly.
- Provide provider health checks.
- Implement rate-limit handling.
- Support provider replacement without changing the frontend.

Layer 3 — Local demonstration provider

- Keep mock data available for development.
- Allow frontend functionality to be tested without external services.
- Provide predictable sample timestamps and mentions.
- Never confuse sample records with real Instagram data.

### 13.3 Provider Capability Matrix

For every feature, the application should maintain a capability state:

- Supported.
- Partially Supported.
- Unavailable.
- Requires Authorization.
- Temporarily Unavailable.

This is particularly important for Story timestamps, Story mentions, Highlights, reposts and follower lists.

# 14. Database Architecture

I recommend SQLite as the main local database.

It will store application records even when the application is closed.

### Recommended database entities

\- `profiles`

- Instagram username.
- Display name.
- Biography.
- Avatar URL.
- Visibility status.
- Last checked.
- Monitoring status.

\- `stories`

- Story ID.
- Profile ID.
- Publication timestamp.
- First detection timestamp.
- Mention information.
- Media URL.
- Media type.
- Download status.

\- `highlights`

- Highlight ID.
- Profile ID.
- Highlight title.
- Cover image.
- Media count.

\- `posts`

- Post ID.
- Profile ID.
- Caption.
- Publication timestamp.
- Engagement information.
- Media information.

\- `reels`

- Reel ID.
- Profile ID.
- Caption.
- Publication timestamp.
- Media information.

\- `reposts`

- Repost ID.
- Original creator.
- Reposting profile.
- Original media ID.
- Repost timestamp.

\- `mentions`

- Story ID.
- Mentioned username.
- Detection timestamp.
- Source metadata.

\- `downloads`

- Download ID.
- Profile ID.
- Media category.
- File location.
- Filename.
- File size.
- Download timestamp.
- Download status.

\- `monitoring_jobs`

- Job ID.
- Profile ID.
- Schedule.
- Last execution.
- Next execution.
- Job status.

\- `activity_logs`

- Activity ID.
- Activity category.
- Description.
- Profile ID.
- Timestamp.
- Associated media ID.

\- `notifications`

- Notification ID.
- Notification category.
- Description.
- Created timestamp.
- Read status.

\- `settings`

- Application preferences.
- Download settings.
- Notification settings.
- Monitoring configuration.
- Provider configuration.

\- `profile_snapshots`

- Profile ID.
- Snapshot timestamp.
- Visibility.
- Available profile statistics.
- Avatar reference.

### Database requirements

- Automatic database creation.
- Database migrations.
- Indexed username and media ID fields.
- Foreign key relationships.
- Transaction-based updates.
- Database backup.
- Database restoration.
- Duplicate record prevention.
- Database integrity checks.
- Safe application shutdown.

# 15. Recommended Frontend Design and Layout

My strongest recommendation is a modern dark desktop application with a left sidebar, top navigation, dashboard cards and responsive grid-based content galleries.

Do not make it look like a website squeezed into a desktop window.

It should feel like a dedicated Windows productivity application.

## 15.1 Overall Visual Direction

[Purple Dashboard App Design](https://images.openai.com/static-rsc-4/uw7H8GPiqbpizzWLxA-_HcJca38jOcbgLBhpVJqCok7_jM3tZgYZFPMxUXpen66sXO3vp1ZbT-S6m6Ab3lyxCcnRcVJaw2cdm9z3aE-sZF4v1cjYqRstadX-v4m0608USFzTVqjpZUf9pJg62xG0VSu7AgQeUhcure6BVz35X-U?purpose=inline)

[Xerintel - Desarrollo web](https://images.openai.com/static-rsc-4/BuXP804R36ryduFYjLPbDSA8gwtDg7WhIvFEl_446xLASbBUO1VvSccNG0jHHuk-8w1GnpNoKEWcaraFOKXzyuec_Tu6b133j7C-6CVdpP7382Wkdus_7TEBLe_a-LiXP4TV02ibGe7PIuHHMQN-E-4HacMJUQy5CoiEx0KtgaU?purpose=inline)

[IDM Internet Download Manager UI Redesign by UI/UX monster for Mimadesign on Dribbble](https://images.openai.com/static-rsc-4/TBr53OVjdCNkGydNWwj_d1W5JYvhmIocOyyOTiQuwQys5zC2pFGjS2qeN0G-h5BfbT6WpcPrlEqyax62Gw_YehRZ3AY8b-sTBQ0a_RrWLzb3_bINzClYDIf0NR0Doz7WcQKvkW5hirvd2dhNPh-6M-utZ8KPXR5SRl_7KMU3gHo?purpose=inline)

14

### Design characteristics

- Dark background.
- Charcoal and deep-black surfaces.
- Purple and violet accent colors.
- Subtle gradients.
- Rounded cards.
- Modern typography.
- Lucide icons.
- Smooth transitions.
- Grid-based layouts.
- Consistent spacing.
- Minimal visual clutter.
- Responsive desktop layouts.
- Light theme as an optional setting.

Suggested design palette:

- Main background: `#09090F`
- Sidebar: `#101019`
- Cards: `#171723`
- Secondary surfaces: `#202031`
- Primary accent: `#8B5CF6`
- Secondary accent: `#A78BFA`
- Success: `#22C55E`
- Warning: `#F59E0B`
- Error: `#EF4444`
- Main text: `#F5F5FA`
- Secondary text: `#A1A1B2`

## 15.2 Main Application Layout

[Freelance platform dashboard by Bogdan Falin for QClay on Dribbble](https://images.openai.com/static-rsc-4/6wacCPPNOkPcam9pEtr4OmVbhGIgVaadMutVI4GmZZ31Fw3S_1kEQw1413Y8FD9Z4x1TPDCuffUa-K8gnzRrrqOGx_0i5_LFU_ZTxU3UKx_9iRxw-vcBq7Zww5u7kuAdXVj5maAKdSMDK7iSHcUwPAVlUy2sTAa6C-Hj-hH1xg4?purpose=inline)

[dribbble.com](https://dribbble.com/shots/21072206-Freelance-platform-dashboard)

I recommend dividing the application into four major areas.

1\. Left Sidebar

Permanent navigation.

2\. Top Navigation Bar

Global search, notifications, monitoring status and profile menu.

3\. Main Content Area

Grid-based dashboard, profile galleries, viewers and other modules.

4\. Optional Right Inspector Panel

Display selected media metadata, timestamps, mentions and download information.

## 15.3 Final Sidebar Navigation

I recommend this navigation structure:

```
CHARLIE MJ
INSTA VIEWER

MAIN
├── Dashboard
├── Profile Search
├── Monitored Profiles
└── Favorites

INSTAGRAM CONTENT
├── Stories
├── Story Calendar
├── Story Inspector
├── Highlights
├── Posts
├── Reels
├── Reposts
├── Profile Pictures
└── Followers & Following

AUTOMATION
├── Monitoring Bot
├── Monitoring Schedule
├── Visibility Tracker
├── Mention Tracker
└── Notifications

MEDIA MANAGEMENT
├── Download Manager
├── Saved Library
├── Collections
└── Download History

ACTIVITY
├── Activity Timeline
├── Search History
├── Daily Reports
├── Weekly Reports
└── Monthly Reports

APPLICATION
├── Settings
├── Backup & Restore
├── About
└── Help & Information
```

## 15.4 Top Navigation Bar

Include:

- Global search.
- Monitoring indicator.
- Bot status.
- Notification bell.
- Active download indicator.
- Quick Add Profile button.
- Application settings shortcut.
- Minimize and window controls.

## 15.5 Grid Design System

Since you specifically want grid layouts, I recommend making the grid system reusable throughout the application.

### Profile Grid

[Browse thousands of Redesign Social Media images for design inspiration | Dribbble](https://images.openai.com/static-rsc-4/fjAxRefVoB8ZMYZWwXKuhKIqMisy6VHeIipuRlQGKooRlVjc8h85IGgNL60sQUzcxLebp08a7x7blQLKiENgiL5YJsC5YQSMsaczHKF3Er0Wj7MtjZzk1_acYwA6Py0TGBnY_jMT9iqy5Gj-vndjZ9pXPz4jYgQOu-O1HvMzVe4?purpose=inline)

[dribbble.com](https://dribbble.com/search/redesign-social-media)

Each profile card should contain:

- Profile picture.
- Username.
- Display name.
- Visibility status.
- Followers count, if available.
- Monitoring status.
- New Story indicator.
- Last detected activity.
- Quick actions.

### Story Grid

[Instagram Story Viewer | Anonymous Instagram Viewer Online](https://images.openai.com/static-rsc-4/U2gqP699LGqEtxq9uwgI3-z2hUQhCNzu1oI4-KK7B6G_4dJFr5rxi04RlTunFs-_-dWq92L_haHj1L0Mk_R12ixAZ8lmmdjJLcWiqyyBRRx5E4OfoJN-XkGkxWMW6t6DgpJd2NsrLNTWsQp50WzhLcsUhEUcVQ36sWtFXKEGVuU?purpose=inline)

[anonyigpro.com](https://anonyigpro.com/)

Each Story card should contain:

- Story thumbnail.
- Username.
- Publication timestamp.
- Mention indicator.
- Photo or video indicator.
- Download status.
- Download button.
- Story Inspector shortcut.

### Post and Reel Grid

- Three to five columns depending on available window width.
- Responsive thumbnail sizes.
- Consistent aspect ratios.
- Hover actions.
- Download icon.
- Save icon.
- Media type indicator.
- Publication information.

### Grid Customization

- Compact grid.
- Standard grid.
- Large grid.
- List view.
- Adjustable column count.
- Adjustable card spacing.
- Sort options.
- Filter options.

## 15.6 Dedicated Story Inspector Layout

This deserves a particularly good interface.

[브런치](https://images.openai.com/static-rsc-4/m-_vJM07IVeGGH4SxlmzAshFV3sBLRCX2-x3qwmC8sa-jn7AArGDiDApJd2_C18JFeqXjGxiar3ebnYSiwS-9hlCqsrYRIR_ZUKaWzQ6As0cJUsRPQFQXB20cOrksDdJKhycHsnV9PbgcvloKSWCYcwqodLD7wZ4K0-vDhLOYYU?purpose=inline)

[brunch.co.kr](https://brunch.co.kr/%40timeismoney/23)

Recommended structure:

- Left side: Large Story media viewer.
- Right side: Story metadata panel.
- Top: Username and profile picture.
- Middle: Publication date and exact time, when supplied.
- Below: Mentioned usernames.
- Below: Location and music information.
- Bottom: Download, Save and Open Original actions.

This will make your Story Inspector one of the most useful sections in the application.

# 16. Settings Module

Settings should be comprehensive and divided into separate categories.

## General Settings

- Application name.
- Application language.
- Theme selection.
- Default startup page.
- Startup behavior.
- Minimize to tray.
- Close-to-tray behavior.
- Confirm before deleting records.
- Automatic update checking.

## Monitoring Settings

- Enable monitoring.
- Default monitoring interval.
- Maximum concurrent jobs.
- Automatic retries.
- Quiet hours.
- Global monitoring schedule.
- Individual profile schedules.
- Start monitoring when application launches.
- Start background monitoring.
- Pause monitoring when internet is unavailable.

## Downloader Settings

- Default download directory.
- Automatic folder creation.
- Filename format.
- Filename timestamp source.
- Maximum simultaneous downloads.
- Automatic downloads.
- Download categories.
- Duplicate detection.
- Automatic retry.
- Preserve available media quality.
- Disk space warning threshold.

## Notification Settings

- Desktop notifications.
- In-app notifications.
- Button feedback notifications.
- Story notifications.
- Mention notifications.
- Profile visibility notifications.
- Download notifications.
- Error notifications.
- Sound settings.
- Notification duration.
- Quiet hours.

## Appearance Settings

- Dark theme.
- Light theme.
- Accent colors.
- Sidebar size.
- Grid size.
- Card appearance.
- Thumbnail quality.
- Animation settings.
- Compact mode.

## Storage Settings

- Database location.
- Cache location.
- Download location.
- Activity directory.
- Backup directory.
- Maximum cache size.
- Automatic cache cleanup.
- Automatic backup schedule.

## Provider Settings

- Active provider.
- Provider connection status.
- API endpoint where applicable.
- Provider capabilities.
- Authentication status.
- Connection testing.
- Request limits.
- Provider error history.

## Privacy and Security

- Protect locally stored credentials.
- Windows Credential Manager integration where appropriate.
- Clear search history.
- Clear monitoring history.
- Clear activity history.
- Delete database.
- Export application data.
- Secure backup options.

# 17. Error Handling and Reliability

I strongly recommend treating reliability as a separate development requirement.

### Profile errors

- Username not found.
- Profile unavailable.
- Private profile.
- Deleted profile.
- Provider timeout.
- Temporary network failure.
- Provider rate limit.
- Unsupported profile type.

### Content errors

- No Stories available.
- No Posts available.
- No Reels available.
- Story expired.
- Media unavailable.
- Missing metadata.
- Unsupported media type.

### Download errors

- Download interrupted.
- Invalid media URL.
- Network timeout.
- Insufficient disk space.
- File permission denied.
- Duplicate filename.
- Invalid media file.
- Provider download restriction.

### Recovery functionality

- Automatic retry where appropriate.
- Resume supported interrupted downloads.
- Record error details.
- Maintain failed task history.
- Provide manual retry buttons.
- Never silently discard failed jobs.

# 18. Security, Privacy and Data Ownership

- Do not request Instagram passwords.
- Do not store Instagram session cookies.
- Store authorized provider credentials securely.
- Keep personal monitoring information local.
- Do not upload local activity reports automatically.
- Do not transmit downloaded files to external services.
- Make external provider requests transparent.
- Provide a complete history-clearing option.
- Provide an option to delete the local database.
- Provide a local backup and restore mechanism.
- Do not collect unnecessary telemetry.
- Make external connections configurable.

# 19. Development Roadmap

I recommend developing this project in carefully separated phases.

Do not attempt to build all modules simultaneously. First establish the desktop foundation, then the data provider, and then the automation and downloading systems.

## Development phases

1. Phase 1 — Project Foundation
   - Set up Tauri.
   - Integrate the existing React frontend.
   - Configure Rust backend.
   - Create portable Windows packaging.
   - Establish application directories.
   - Implement SQLite.
2. Phase 2 — Frontend Migration
   - Preserve existing dashboard.
   - Preserve profile search.
   - Preserve Story viewer.
   - Preserve Story Inspector.
   - Preserve Posts, Reels and Reposts.
   - Implement desktop navigation.
   - Implement grid layouts.
3. Phase 3 — Data Provider Integration
   - Provider interface.
   - Official API integration where supported.
   - Authorized provider integration.
   - Capability detection.
   - Error handling.
   - Real metadata normalization.
4. Phase 4 — Content Management
   - Profile management.
   - Stories.
   - Story timestamps.
   - Mention tracking.
   - Highlights.
   - Posts.
   - Reels.
   - Reposts.
   - Profile pictures.
5. Phase 5 — Download Engine
   - Download manager.
   - Media downloads.
   - Filename generation.
   - Custom folders.
   - Download queues.
   - Duplicate detection.
   - Saved Library.
6. Phase 6 — Monitoring Bot
   - Multi-profile monitoring.
   - Visibility monitoring.
   - Scheduling.
   - New-content detection.
   - Automatic downloads.
   - Monitoring history.
7. Phase 7 — Notifications
   - Windows toast notifications.
   - In-app notifications.
   - Button feedback.
   - Story notifications.
   - Mention notifications.
   - Download notifications.
8. Phase 8 — Activity Management
   - Activity database.
   - Markdown generation.
   - Daily reports.
   - Weekly reports.
   - Monthly reports.
   - Search and filtering.
9. Phase 9 — Advanced Features
   - Story calendar.
   - Profile change tracking.
   - Mention intelligence.
   - Media collections.
   - Media comparison.
   - Advanced search.
   - Backup and restore.
10. Phase 10 — Testing and Release
    - Integration testing.
    - Database testing.
    - Download testing.
    - Scheduler testing.
    - Notification testing.
    - Portable EXE testing.
    - Clean Windows installation testing.
    - Final release.

# 20. Suggested Project Directory Structure

This is how I recommend organizing the complete source repository.

```
charlie-mj-insta-viewer/
│
├── src/
│   ├── app/
│   ├── components/
│   │   ├── layout/
│   │   ├── dashboard/
│   │   ├── profiles/
│   │   ├── stories/
│   │   ├── posts/
│   │   ├── reels/
│   │   ├── reposts/
│   │   ├── downloads/
│   │   ├── monitoring/
│   │   ├── notifications/
│   │   └── common/
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Profiles.tsx
│   │   ├── ProfileDetails.tsx
│   │   ├── Stories.tsx
│   │   ├── StoryCalendar.tsx
│   │   ├── StoryInspector.tsx
│   │   ├── Highlights.tsx
│   │   ├── Posts.tsx
│   │   ├── Reels.tsx
│   │   ├── Reposts.tsx
│   │   ├── FollowersFollowing.tsx
│   │   ├── Downloads.tsx
│   │   ├── Library.tsx
│   │   ├── Monitoring.tsx
│   │   ├── Activity.tsx
│   │   └── Settings.tsx
│   │
│   ├── services/
│   │   ├── providers/
│   │   ├── profiles/
│   │   ├── stories/
│   │   ├── mentions/
│   │   ├── posts/
│   │   ├── reels/
│   │   ├── reposts/
│   │   ├── downloader/
│   │   ├── monitoring/
│   │   ├── notifications/
│   │   ├── activity/
│   │   └── reports/
│   │
│   ├── hooks/
│   ├── store/
│   ├── types/
│   ├── utils/
│   └── styles/
│
├── src-tauri/
│   ├── src/
│   │   ├── main.rs
│   │   ├── commands/
│   │   ├── database/
│   │   ├── downloader/
│   │   ├── scheduler/
│   │   ├── notifications/
│   │   ├── filesystem/
│   │   └── providers/
│   │
│   ├── capabilities/
│   ├── icons/
│   ├── migrations/
│   └── tauri.conf.json
│
├── public/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/
│   ├── architecture.md
│   ├── database.md
│   ├── providers.md
│   ├── monitoring.md
│   └── development.md
│
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

This is a proposed target structure. Existing source files should be migrated incrementally rather than deleted simply to match the proposed structure.

# 21. Additional Features for Future Versions

After the first stable release, consider these enhancements.

### Version 2.0

- Multiple provider support.
- Advanced profile analytics.
- Advanced Story analytics.
- Historical profile comparison.
- Advanced mention reports.
- Automatic media classification.
- AI-generated media descriptions.
- Local AI integration through Ollama.
- OCR for visible text inside downloaded Stories.
- Smart media tagging.
- Natural-language search across activity records.

### Version 3.0

- Advanced media library.
- Local AI-powered content organization.
- Similarity-based media discovery.
- Advanced reporting dashboard.
- Media metadata extraction.
- More customizable automation rules.
- Additional export formats.
- Plugin-based provider architecture.

These should remain optional enhancements and should not delay the initial working release.

# 22. Critical Development Decisions

Before starting implementation, I would establish the following requirements as non-negotiable.

- Existing functionality preservation: Do not remove working functionality from the current web application.
- Additive development: Introduce new features through modular services.
- Desktop-first: Design for Windows desktop rather than simply embedding the existing website.
- Local-first: Store application data, history, settings and downloaded media locally.
- Provider independence: Never tightly couple the UI to a particular external data provider.
- Capability awareness: Never display unsupported provider functionality as if it were operational.
- Background monitoring: Keep monitoring separate from the frontend rendering process.
- Download reliability: Use a centralized queue and download service.
- Timestamp accuracy: Distinguish original publication time from detection time.
- Mention accuracy: Distinguish actual structured mention metadata from OCR guesses.
- No duplicate records: Maintain stable media identifiers and database uniqueness constraints.
- Recoverability: Provide backups, retries and error reporting.
- Portable operation: Ensure database and configuration paths work independently of installation location.
- Privacy: Keep local data under the user's control.
- Testing: Every new module must have independent tests.

## 23. Most Important Technical Reality Before Development

There is one issue I want to make particularly clear because it affects the feasibility of your entire project.

Your desired application is technically achievable as a desktop framework, with local storage, grid viewers, a downloader, scheduling, notifications, reporting and automation.

However, the ability to retrieve all the live content advertised by the four websites is a separate challenge from building the application itself.

The official Instagram API does not provide all the access needed for your requested combination of arbitrary public-account Stories, exact Story timestamps, Story mentions, reposts and follower lists.

For example, the official API supports certain professional-account integrations, but it is not a replacement for every third-party viewer feature.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.postman.com\&sz=32)

Postman API Network

+2



Therefore, I recommend building the complete application framework first and making each external data capability replaceable.

This allows you to complete and test:

- The Windows application.
- All navigation.
- The dashboard.
- The profile manager.
- The Story Inspector.
- The media gallery.
- The download engine.
- The monitoring scheduler.
- The Windows notification system.
- The Markdown activity system.
- The database.
- The settings.

Then each live Instagram capability can be integrated and tested independently against a legitimate provider.

This is much safer than building the whole project around one fragile data-retrieval method.

# 24. My Final Recommendations: What Should Be Prioritized?

Although the project contains many features, I would prioritize the following ten systems.

## Priority features

P1

Multi-profile monitoring bot

P1

Profile visibility change detection

P1

New Story detection and notifications

P1

Story timestamp and mention inspector

P1

Centralized downloader

P2

Complete media library

P2

Markdown activity and reporting

P2

Story calendar and historical tracking

P2

Profile change intelligence

P3

Advanced media search and organization

# 25. Final Project Definition

# Charlie MJ Insta Viewer & Downloader

Independent Windows desktop application

[Top Social Media Management Tools for Small Businesses | iOLab Digital](https://images.openai.com/static-rsc-4/A2ouVybcZoDUOwVi289K2j2mtG8yxzUoJgNdsaBH15OgX8uK2JuIzAY1VCmFJqxR7fMnW6-80UYVpjqwWT3xchjVerIx2RFOwkAnLgj8yzEC-et0gIVzcS1-dzkCy5dbfM6rywau3r5x_L-d3JIEnwxR-YB_pUUEXd24OsK1ri0?purpose=inline)

[iolab.co](https://iolab.co/blog/top-social-media-management-tools)

Project objective

A standalone, portable Windows application for discovering, viewing, monitoring, organizing and downloading available Instagram public-content media through supported data providers.

Core systems

- Profile search and management.
- Stories, timestamps and mention inspection.
- Highlights, Posts, Reels and Reposts.
- HD profile picture viewing.
- Multi-profile monitoring bot.
- Profile visibility tracking.
- Automatic new-content detection.
- Windows notifications.
- Built-in media downloader.
- Saved media library.
- Activity and Markdown reports.
- Advanced search and filters.
- Backup and restore.
- Comprehensive settings.

Technology

- Tauri 2.
- React.
- TypeScript.
- Rust.
- SQLite.
- Tailwind CSS.

Distribution

- Portable Windows EXE.
- Optional Windows installer.
- Local-first storage.
- No mandatory remote application backend.

## 26. My Suggested Next Development Step

I would not immediately start writing the entire application. First, establish a proper technical implementation specification so that the development process does not damage your existing frontend.

I recommend dividing the next stage into three deliverables:

1\. Complete Architecture Specification: Final technology choices, application architecture, provider interfaces, database schema, service boundaries and directory structure.

2\. Frontend Design Specification: Every page, sidebar item, dashboard widget, grid card, modal, inspector, notification and settings screen.

3\. Implementation Specification: Detailed development instructions, phased implementation, acceptance criteria, testing requirements and rules protecting all existing functionality.

One additional recommendation: create a permanent `FEATURE-PRESERVATION.md` file in your GitHub repository. It should document every existing feature, its current implementation location and its expected behavior. Every development phase should verify this document before merging changes.

My strongest recommendation: Build this as a modular desktop application with your existing React frontend as its foundation, Tauri/Rust as its desktop and background engine, SQLite as its local database, and a replaceable provider architecture. That gives you a solid foundation to expand the project without repeatedly rebuilding it.
---


-------
# Complete Features and Functionalities of Your 4 Favourite Instagram Story Viewer Websites

The four websites you mentioned are:

1. StorySaver
2. InSnoop
3. AnonyIG
4. Pixnoy

These websites belong to the Instagram anonymous-viewing and media-downloading category. Their main purpose is to let visitors access publicly available Instagram content through a browser, often without logging into an Instagram account.

Below is a structured feature breakdown that you can use as a reference for documenting their functionality or planning a similar application.

## 1. StorySaver — Instagram Story Viewer & Downloader

[Top 4 Free Instagram Story Downloaders (No Login Needed) | Toolsmart Blog](https://images.openai.com/static-rsc-4/Imq2y1hPltv68TylIHo16O2TJIV6AfjSI3VSyCBpFmA7VsDorB5lBiUH2Uf2sct3CLOF2qHjIqyyzZQcWdZvhE_6GqGsdNy74QTPkupDFqIsnJqFPGtyTyXl1xWl13kCX-O0zwpiePGm2FLh_L54E7lqyrJSLn2eWPtdvyUTQr0?purpose=inline)

Website: [storiesaver.com](https://storiesaver.com/)

Main purpose: View and download Instagram Stories, Highlights, Reels, posts and profile pictures.

Story downloading focused

### A. Profile Viewing

- Search Instagram profiles using usernames.
- Search using complete Instagram profile URLs.
- View public profile information.
- Display profile picture in full resolution.
- View profile biography.
- Display follower and following counts.
- Access public profile content.

### B. Instagram Stories

- View active Instagram Stories anonymously.
- View photos and videos.
- Browse multiple stories in sequence.
- Play story videos directly in the browser.
- Download individual stories.
- Save stories before they expire.
- Support story images and video files.

### C. Instagram Highlights

- View all available public Highlights.
- Display Highlight cover images.
- Open individual Highlight collections.
- Browse stories inside each collection.
- Download individual Highlight stories.
- Access older stories preserved in Highlights.

### D. Instagram Posts

- Browse recent public Instagram posts.
- View photos and videos.
- View carousel posts.
- Display post captions.
- Display likes and comments information.
- Download individual post media.
- Save carousel slides separately.

### E. Instagram Reels

- Dedicated Reels section.
- Browse recent public Reels.
- Play Reels inside the website.
- Download individual Reels.
- Save videos in MP4 format.

### F. Profile Picture Downloader

- View full-size Instagram profile pictures.
- Open profile pictures separately.
- Download original available profile images.
- Save profile pictures without cropping.

### G. Downloading System

- Individual download buttons.
- JPG/JPEG image downloads.
- WebP image support where available.
- MP4 video downloads.
- No additional watermark.
- Original available media resolution.
- Direct browser downloads.

### H. Privacy and Accessibility

- No Instagram login required.
- No registration required.
- Anonymous public-content browsing.
- No Instagram password collection.
- Browser-based functionality.
- Desktop and mobile compatibility.
- Search history kept locally in the browser according to the site's description.

Source:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://storiesaver.com\&sz=32)

Storiesaver

+1



## 2. InSnoop — Anonymous Instagram Story Viewer

[What Is Insnoop? Complete Guide to Anonymous Instagram Story Viewing](https://images.openai.com/static-rsc-4/J4BxI1USrvbrG3fL7hSS2Qm8GsD3db27pEsw6QBM4AITlwIINPmPuZRQFQnW_KtVyBBJYbj7tdL7SKtUstJtQ3HJAPo84lE5yb6Fl-pukwON9P3lpYJi9EwFQ6EpMbSFgoR0a4mJxK3yOUjLjVnreRiCw_ZN4nZ9V1z8W0rQgDI?purpose=inline)

Website: [insnoop.io](https://insnoop.io/)

Main purpose: Anonymous Instagram Story and Highlight viewing and downloading.

Anonymous viewing focused

### A. Anonymous Story Viewing

- View public Instagram Stories without logging in.
- Watch stories without using your personal Instagram account.
- Browse stories without intentionally registering a view under your Instagram identity.
- View stories from public profiles.
- Access stories through username searches.
- Search using Instagram profile information.

### B. Story Downloading

- Download Instagram Stories.
- Save story photos.
- Save story videos.
- Download media in available HD quality.
- Save videos in MP4 format.
- Save images in image formats.
- Access media for offline viewing.

### C. Instagram Highlights

- Browse public Instagram Highlights.
- View saved Highlight collections.
- Watch individual Highlight stories.
- Download Highlight photos.
- Download Highlight videos.
- Access older publicly available Highlight content.

### D. Profile Search

- Search using Instagram usernames.
- Paste Instagram profile URLs.
- Retrieve publicly accessible account content.
- Load available active stories.
- Display search results through a browser interface.

### E. Media Viewer

- Watch stories directly in the browser.
- View media without installing an application.
- Access content through a simple interface.
- Use the browser to view and download content.

### F. Privacy Features

- No Instagram login.
- No account registration.
- No email verification.
- No Instagram password required.
- Anonymous browsing.
- Server-side retrieval of public content.

### G. Cross-Platform Compatibility

- Desktop browsers.
- Android browsers.
- iPhone and iPad browsers.
- Tablet compatibility.
- No software installation.
- Browser-based access.

### H. Performance and Interface

- Simple search interface.
- Fast profile lookup.
- Minimal navigation.
- Content-focused layout.
- Direct access to Stories and Highlights.

Main strength: InSnoop concentrates on anonymous Story viewing and saving, rather than presenting itself primarily as a complete Instagram media management platform.

Source:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://insnoop.io\&sz=32)

Anonymous Instagram Story Viewer

+1



## 3. AnonyIG — Anonymous Instagram Profile Viewer

[Best 10 Instagram Story Viewers to Watch IG Anonymously in 2026](https://images.openai.com/static-rsc-4/3mPfiCRsEhvBj2y9Ptq_afc9JK9T6kv8ZG35wkochSullHEYW_N-GyTJTSyG3FONBT1EDAUvyETXml0A8SfveA6_Xnc8iMEz1XonACKoPkSfrkU7PY2CY4yPhXvAnIbyfdGpgvglqFGVk9ZnFZ-1xH4zTEruBslQODNDyVVP3uY?purpose=inline)

Website: [anonyig.com](https://anonyig.com/)

Main purpose: All-in-one anonymous Instagram profile, Story, Reel, Highlight and post viewer.

All-in-one viewer

### A. Complete Instagram Profile Viewer

- Search Instagram profiles.
- Browse public profiles anonymously.
- Search by username.
- Search using Instagram profile URLs.
- View public profile information.
- View account biography.
- View follower counts.
- View following counts.
- Browse profile publishing history.
- Access available public content.

### B. Instagram Story Viewer

- Watch public Instagram Stories anonymously.
- Browse active stories.
- View photo stories.
- Play video stories.
- Download individual stories.
- Save stories before expiration.
- Access available stories without an Instagram account.

### C. Instagram Highlights Viewer

- View public Highlight collections.
- Browse individual Highlight albums.
- View Highlight covers.
- Play individual Highlight stories.
- Download Highlight images.
- Download Highlight videos.
- Access older Highlight collections.

### D. Instagram Posts Viewer

- Browse public Instagram posts.
- View individual photos.
- Watch video posts.
- View carousel posts.
- Display post captions.
- Display likes information.
- Display comments information.
- Download individual posts.
- Save available post media.

### E. Instagram Reels Viewer

- Browse public Reels.
- Watch Reels directly in the browser.
- View short-form video content.
- Download Reels.
- Save videos for offline viewing.
- Access publicly available IGTV content where supported.

### F. Instagram DP Viewer

- View Instagram profile pictures in full size.
- Open profile images separately.
- Zoom into profile pictures.
- Download profile pictures.
- Access higher-resolution images where available.
- View profile pictures without logging in.

### G. Media Downloading System

- Download public photos.
- Download public videos.
- Download Stories.
- Download Highlights.
- Download Reels.
- Download profile pictures.
- Save content directly to devices.
- Download media without adding a watermark.
- Access available original-quality files.

### H. Privacy and Security

- No Instagram login required.
- No account registration.
- No email verification.
- Anonymous browsing.
- HTTPS connections.
- No Instagram password required.
- Public-content-only access.
- Privacy-oriented browsing.

### I. Interface and Accessibility

- Simple username search.
- Profile URL support.
- Browser-based operation.
- Mobile-friendly layout.
- Desktop compatibility.
- Multiple language support.
- No application installation.
- Free access according to the site's published offering.

### J. Additional Capabilities

- Public profile research.
- Competitor content research.
- Influencer content monitoring.
- Social media inspiration collection.
- Public visual-content archiving.
- Reference material collection.

Main strength: AnonyIG combines profile exploration, full-size DP viewing, Stories, Highlights, Reels and post downloading in one place.

Source:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://anonyig.com\&sz=32)

AnonyIG

+2



## 4. Pixnoy — Instagram Viewer & Downloader

[Cyber Detective💙💛 (@cyb_detective) on X](https://images.openai.com/static-rsc-4/rGdGR3H6RKIhObLLiN4RKgvJ-vzt0Y3szwwVzWpfolZFdpOARt-683wPlB4K4tmTZPwAiYzKXXtg-wYmAOzdINfEN6D7o5nJDIzEQQdp4cL8u2_Jq_EjjPf2hhQu8FSfRELwQw95zFsIwGoYo9afPiYSKU3NE9ROWHIDltRrFT4?purpose=inline)

Website: [pixnoy.com](https://www.pixnoy.com/)

Main purpose: Browse public Instagram profiles and download photos, videos, Reels and Stories.

Profile and media focused

### A. Instagram Profile Viewer

- Search public Instagram profiles.
- Search using usernames.
- Search using Instagram post links.
- Browse profile information.
- View profile biography.
- View follower counts.
- View following counts.
- Explore available public profile content.
- Browse profiles without an Instagram account.

### B. Anonymous Instagram Browsing

- View public profiles anonymously.
- Browse photos without logging in.
- Watch public Reels.
- Browse available Stories.
- Access public Highlights.
- Use the service without registration.
- Browse from a regular web browser.

### C. Instagram Photo Downloader

- Download Instagram photos.
- Save images in available HD quality.
- Download individual images.
- Save photos without additional watermarks.
- Preserve available original image quality.
- Download media directly to your device.

### D. Instagram Video Downloader

- Download Instagram videos.
- Save public video posts.
- Download Reels.
- Save videos in MP4 format where available.
- Access videos for offline playback.
- Download available original-quality media.

### E. Instagram Story Viewer

- View public Instagram Stories.
- Watch active stories.
- Browse story photos.
- Play story videos.
- Download individual Stories.
- Access content without Instagram login.

### F. Instagram Highlights

- Browse public Highlights.
- Open individual Highlight collections.
- View Highlight stories.
- Download individual stories.
- Access saved stories beyond the original 24-hour period, as long as they remain in Highlights.

### G. Instagram Link Downloader

- Paste Instagram post URLs.
- Load content using direct links.
- Retrieve public media.
- Preview content before downloading.
- Download photos and videos through a simplified workflow.

### H. Media Quality and Downloading

- HD media downloads.
- No additional watermark.
- No unnecessary media compression according to its published claims.
- Direct download functionality.
- Support for available photo and video formats.

### I. Privacy and Accessibility

- No Instagram login.
- No registration.
- No subscription required according to the published offering.
- Mobile browser compatibility.
- Desktop browser compatibility.
- Tablet compatibility.
- No application installation.
- Public-content-only access.

### J. Content Discovery and Inspiration

- Browse travel and photography content.
- Explore food and lifestyle profiles.
- Explore fashion and beauty content.
- Explore fitness and motivational content.
- Collect publicly available visual references.

Main strength: Pixnoy offers a combination of profile browsing, link-based media retrieval and downloading of public Instagram photos and videos.

Source:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.pixnoy.com\&sz=32)

Pixnoy

+1



# 5. Combined Feature Comparison

Here is a comparison of the four websites based on their published features.

| Feature                 | StorySaver | InSnoop       | AnonyIG | Pixnoy        |
| ----------------------- | ---------- | ------------- | ------- | ------------- |
| Anonymous viewing       | Yes        | Yes           | Yes     | Yes           |
| No login required       | Yes        | Yes           | Yes     | Yes           |
| Profile viewer          | Yes        | Basic         | Yes     | Yes           |
| Story viewer            | Yes        | Yes           | Yes     | Yes           |
| Story downloader        | Yes        | Yes           | Yes     | Yes           |
| Highlights viewer       | Yes        | Yes           | Yes     | Yes           |
| Highlights downloader   | Yes        | Yes           | Yes     | Yes           |
| Posts viewer            | Yes        | Not prominent | Yes     | Yes           |
| Posts downloader        | Yes        | Not prominent | Yes     | Yes           |
| Reels viewer            | Yes        | Not prominent | Yes     | Yes           |
| Reels downloader        | Yes        | Not prominent | Yes     | Yes           |
| Full-size DP viewer     | Yes        | Not prominent | Yes     | Not prominent |
| Carousel support        | Yes        | Not specified | Yes     | Not specified |
| Username search         | Yes        | Yes           | Yes     | Yes           |
| Profile URL search      | Yes        | Yes           | Yes     | Yes           |
| Browser-based           | Yes        | Yes           | Yes     | Yes           |
| Mobile support          | Yes        | Yes           | Yes     | Yes           |
| No additional watermark | Yes        | Not specified | Yes     | Yes           |

Not prominent / not specified means the feature was not clearly established in the reviewed website descriptions; it does not necessarily mean the feature is unavailable.

# 6. Combined Master Feature List

If you want to study all four websites as a single product concept, the following is the consolidated functionality list.

Master feature inventory

### 1. Instagram Profile Management and Viewing

- Username-based profile search.
- Profile URL search.
- Profile information viewer.
- Full-size profile picture viewer.
- Biography viewer.
- Followers and following information.
- Public profile browsing.
- Recent post browsing.
- Profile content navigation.

### 2. Instagram Stories System

- Anonymous Story viewer.
- Active Story detection.
- Photo Story viewer.
- Video Story viewer.
- Story navigation.
- Story playback.
- Individual Story downloads.
- Story media preview.
- Story expiration awareness.

### 3. Instagram Highlights System

- Highlight collection viewer.
- Highlight cover previews.
- Individual Highlight viewer.
- Highlight navigation.
- Highlight media downloads.
- Historical public Highlight access.

### 4. Instagram Posts System

- Photo post viewer.
- Video post viewer.
- Carousel viewer.
- Caption display.
- Likes information.
- Comments information.
- Individual media downloads.
- Multi-image post support.

### 5. Instagram Reels System

- Reels viewer.
- Reels playback.
- Reels downloader.
- Video preview.
- MP4 downloads.
- Offline viewing.

### 6. Instagram DP System

- Full-size profile picture viewer.
- Profile picture zoom.
- HD image preview.
- Profile picture downloading.

### 7. Universal Downloading System

- Individual image downloads.
- Individual video downloads.
- Story downloads.
- Highlight downloads.
- Reel downloads.
- Post downloads.
- Profile picture downloads.
- Carousel downloads.
- Original available resolution.
- Watermark-free downloads.

### 8. Search and Navigation System

- Username search.
- Profile URL search.
- Post URL search.
- Search input validation.
- Automatic username extraction from URLs.
- Search result display.
- Loading indicators.
- Error handling.
- Empty-result messages.
- Retry functionality.

### 9. Privacy and Security

- No Instagram authentication required.
- No Instagram password collection.
- Anonymous public-content access.
- HTTPS connections.
- No unnecessary user registration.
- Privacy-conscious server requests.
- Public/private profile access restrictions.
- Clear privacy policy.

### 10. User Interface and Experience

- Responsive design.
- Mobile-first interface.
- Desktop compatibility.
- Tablet compatibility.
- Media thumbnails.
- Content preview.
- Tab-based navigation.
- Separate Stories, Posts, Reels and Highlights sections.
- Simple download buttons.
- Fast-loading interface.
- Browser-based operation.

### 11. Additional Useful Features to Consider

These are potential additions to the combined concept, not claims that all four websites currently offer them.

- Download queue.
- Multiple media selection.
- Bulk download.
- ZIP archive generation.
- Download progress indicators.
- Recently searched profiles.
- Favorite profiles.
- Local search history.
- Media gallery.
- Download history.
- Dark and light themes.
- Multi-language interface.
- Copy media links.
- Share downloaded media.
- Profile comparison.
- Media filtering.
- Sort by newest and oldest.
- Custom download folders.
- Duplicate media detection.

# 7. Official Website Links

| Website    | Official link                               |
| ---------- | ------------------------------------------- |
| StorySaver | [Open StorySaver](https://storiesaver.com/) |
| InSnoop    | [Open InSnoop](https://insnoop.io/)         |
| AnonyIG    | [Open AnonyIG](https://anonyig.com/)        |
| Pixnoy     | [Open Pixnoy](https://www.pixnoy.com/)      |

Important: These are independent third-party services, not official Instagram products. Their advertised capabilities can change, and actual availability depends on Instagram's access restrictions and the services' data providers. Public profile content is the appropriate scope; private-account restrictions should not be bypassed. Downloaded content remains subject to its creator's copyright.
---
