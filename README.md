# Charlie MJ Insta Viewer

An independent, GitHub-Pages-first public-content viewer built with React, TypeScript, Vite and Tailwind CSS.

> **Important:** This repository is a Phase 1 frontend/demo. It uses realistic mock data and does not scrape Instagram, bypass access controls, or expose private content.

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
