# Legacy Frontend README

The original README from the uploaded frontend project has been replaced at the repository root by the new documentation hub. The previous content is retained below for reference.

---

# Charlie MJ Insta Viewer

An independent, GitHub-Pages-first public-content viewer built with React, TypeScript, Vite and Tailwind CSS.

> **Important:** This repository is a Phase 1 frontend/demo. It uses realistic mock data and does not scrape Instagram, bypass access controls, or expose private content.
>

## 🚀 Live Demo

👉 **[Click here to view the live demo](https://awsrmmustansarjavaid.github.io/)**

The application is deployed as a static frontend using GitHub Pages.

## ✨ Features

- 🔎 **Profile Search**
  - Search mock public profiles by username.
  - Profile overview with bio, avatar, and follower/following counts.
  - Verified badge support.

- 📖 **Stories**
  - Story viewer and story ring UI.
  - Story inspector with detailed metadata.
  - Story calendar view.
  - Timestamps, location, music, and mentions when available.

- 🖼️ **Posts & Reels**
  - Browse posts grid with captions and engagement counts.
  - Dedicated reels feed with view counts.
  - Repost view showing original creator and source link.
  - Comment explorer with nested reply threads.

- 📅 **Content Timeline**
  - Unified chronological feed combining stories, posts, and reels.

- ⭐ **Highlights**
  - Highlight collection previews on profile.

- 💾 **Saved Library**
  - Save items locally to the browser.
  - Browse and remove saved items.
  - Backed by browser localStorage — no server required.

- 🕘 **Search History**
  - Automatically stores recently searched usernames.
  - One-click clear history.
  - Fully local, never transmitted anywhere.

- ⚙️ **Settings**
  - App preferences (dark mode, language, API base URL).
  - Local storage-based configuration.

- 📄 **Info Pages**
  - About, Privacy, and Terms pages describing the demo's scope and data handling.

- 📱 **Responsive UI**
  - Desktop, tablet, and mobile-friendly layouts.
  - Instagram-inspired look with independent branding — not affiliated with Meta/Instagram.

- 🌐 **GitHub Pages Deployment**
  - Fully static frontend, no backend required.
  - Automated build & deploy via GitHub Actions.

- 🧩 **API-Ready Architecture**
  - Data access abstracted behind a service layer (`src/services/api.ts`).
  - Currently backed by a mock data provider (`src/data/mockData.ts`).
  - Structured so a real/legitimate data source could be swapped in later.

- 📦 **PWA Foundation**
  - Web app manifest included (`manifest.webmanifest`).
  - Installable-app groundwork — no offline/service-worker support yet.

> ⚠️ **Note:** This is a demo project using **mock/sample data only**. It does not fetch or display real Instagram accounts, and is not affiliated with or endorsed by Instagram or Meta.

## What is included

- Responsive Instagram-inspired UI without copying Instagram branding.
- Profile search and profile pages.
- Stories, Story Viewer and Story Inspector.
- Story timeline and calendar-style views.
- Posts, reels, reposts, highlights and comments.
- Saved library and search history using browser storage.
- Settings, About, Privacy and Terms screens.
- API adapter layer ready for a legitimate external data provider.
- PWA manifest.
- GitHub Actions deployment to GitHub Pages.
- Mock data so the project works immediately without a backend.

## Architecture

```text
Browser
  |
  +--> React + TypeScript + Vite
  |       |
  |       +--> Local storage (saved items, history, settings)
  |       |
  |       +--> API adapter
  |                |
  |                +--> Mock provider (default)
  |                +--> Future legitimate API/backend
  |
  +--> GitHub Pages
```

GitHub Pages hosts the static frontend. It does not provide a server-side runtime. If live data is added later, the frontend should call a legitimate HTTPS API or a separately hosted backend.

## Run locally

Requirements:

- Node.js 20+
- npm 10+

```bash
git clone https://github.com/YOUR_USERNAME/charlie-mj-insta-viewer.git
cd charlie-mj-insta-viewer
npm install
npm run dev
```

Open the local URL printed by Vite.

## Build

```bash
npm run build
npm run preview
```

## GitHub Pages

1. Create a repository named `charlie-mj-insta-viewer`.
2. Push this project to the `main` branch.
3. Open **Settings → Pages**.
4. Set the source to **GitHub Actions**.
5. The workflow in `.github/workflows/deploy.yml` builds and publishes the `dist/` directory.
6. The Vite base path is already configured for `/charlie-mj-insta-viewer/`.

If you choose another repository name, update `base` in `vite.config.ts` and `start_url` in `public/manifest.webmanifest`.

## Project structure

```text
charlie-mj-insta-viewer/
├── .github/workflows/deploy.yml
├── public/
│   ├── favicon.svg
│   ├── manifest.webmanifest
│   └── robots.txt
├── src/
│   ├── components/
│   ├── data/
│   ├── pages/
│   ├── services/
│   ├── store/
│   ├── types/
│   ├── utils/
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── tsconfig*.json
└── vite.config.ts
```

## Data and privacy model

The demo intentionally separates UI behavior from the data provider.

- Exact timestamps are shown only when the data object contains an exact timestamp.
- An expired Story cannot be magically recovered if the application never legitimately observed or retained it.
- The archive concept is for metadata captured while content was legitimately available.
- Download actions are demo placeholders; a production provider must only return media the user is permitted to receive.
- No Instagram login credentials are requested.
- No secrets belong in frontend environment variables.

## Future live-data integration

Implement a provider behind `src/services/api.ts` and map external responses into the internal types under `src/types/`.

Recommended flow:

```text
GitHub Pages
   |
   v
api.ts
   |
   v
Legitimate data API
   |
   v
Publicly accessible content
```

Do not put private API credentials, cookies, session tokens or scraping credentials into the browser bundle.

## License

Add the license you want to use before publishing the repository.

## Disclaimer

Charlie MJ Insta is an independent project and is not affiliated with, sponsored by, or endorsed by Instagram or Meta.
