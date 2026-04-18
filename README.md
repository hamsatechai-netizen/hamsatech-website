# HamsaTech

HamsaTech is a Vite/React frontend with a FastAPI backend for student intake, coach review, secure coach-to-student assignment, and Supabase-backed persistence.

## What this repo contains (high level)

- `src/` - React app (UI + routes)
- `public/` - static assets served by Vite (redirects + logo)
- `backend/` - FastAPI API service (auth, intake, coach workflows, Supabase persistence)
- `supabase/` - database schema used by the backend

## Stack

- React 18
- TypeScript
- Vite
- React Router
- Plain CSS
- FastAPI
- Supabase

## Routes

- `/` - landing page
- `/home` - main showcase page
- `/platform` - platform details
- `/usecases` - use cases
- `/howitworks` - process overview
- `/about` - about page
- `/signin` - sign in
- `/signup` - student signup
- `/dashboard` - coach and student dashboard
- `/profile` - account profile
- `/athlete-intake` - student intake form

## Local Development

### 1) Frontend (Vite + React)

```bash
npm install
npm run dev
```

The frontend runs on `http://127.0.0.1:5173` by default.

For local frontend configuration:

```bash
copy .env.example .env
```

Set:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## FastAPI Authentication Service

The backend owns:

- student-only public signup
- coach login and secure assignment approval
- coach-only access to assigned students
- student intake submission
- coach feedback persistence

### Backend setup

### 2) Backend (FastAPI)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

The API runs on `http://127.0.0.1:8000` by default.

You can override those values with environment variables before starting FastAPI:

```bash
set HAMSA_DEFAULT_EMAIL=you@example.com
set HAMSA_DEFAULT_PASSWORD=your-secure-password
```

For backend configuration, copy `backend/.env.example` to `backend/.env` and update the values you need.

### Frontend + backend together

Run the backend first, then start the Vite frontend:

```bash
npm run dev
```

The frontend expects the API URL from `.env` via `VITE_API_BASE_URL`.

## Supabase Intake Storage

The coach-facing athlete intake workflow and app user/session data are stored in Supabase through FastAPI.

### Required environment variables

```bash
set SUPABASE_URL=https://your-project.supabase.co
set SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Supabase table setup

Run the SQL in `supabase/schema.sql` inside the Supabase SQL editor. It creates:

- `Athletes_Master`
- `Family_Details`
- `Athlete_Profile`
- `Sessions_Log`
- `Physiology_Data`
- `Psychology_Questions`
- `Psychology_Responses`
- `Athlete_Lookup`
- `App_Users`
- `App_Sessions`
- `Coach_Feedback`

After applying schema changes, restart FastAPI.

## Current Assignment Flow

1. Student signs up without entering a coach code.
2. Student signs in and requests coach assignment from the dashboard.
3. The request is sent to the main coach profile `coach@hamsatech.ai`.
4. Coach opens `Student Assignment Requests` in the dashboard.
5. Coach enters their coach code and approves the student.
6. Student intake unlocks after approval.

## Quality Checks

```bash
npm run lint
npm run build
```

## Cloudflare Pages Deployment

This project is ready to deploy as a static site on Cloudflare Pages.

Use these settings:

- Framework preset: `Vite`
- Build command: `npm run build`
- Build output directory: `dist`
- Node version: `20` recommended

Because the app uses client-side routing with `BrowserRouter`, the repo includes a `public/_redirects` file so deep links and refreshes resolve back to `index.html` on Cloudflare Pages.

### Branch workflow

Recommended GitHub and Cloudflare setup:

1. Push this repository to GitHub.
2. Use your `development` branch for active development and commits.
3. Connect the GitHub repository to Cloudflare Pages.
4. Configure Cloudflare Pages to build from the branch you want to preview or release.
5. Set the frontend environment variable in Cloudflare Pages:

```bash
VITE_API_BASE_URL=https://your-fastapi-api.example.com
```

6. Make sure the FastAPI backend allows every Cloudflare frontend origin you plan to use:

```bash
HAMSA_FRONTEND_ORIGINS=http://127.0.0.1:5173,http://localhost:5173,https://your-project.pages.dev,https://dev.your-domain.com
```

7. For cross-site auth cookies in production, configure the backend cookie settings:

```bash
HAMSA_COOKIE_SECURE=true
HAMSA_COOKIE_SAMESITE=none
```

## Render Backend Deployment

This repo includes a `render.yaml` blueprint for deploying the FastAPI backend on Render.

### Render setup

1. Push this repository to GitHub.
2. In Render, create a new `Blueprint` deployment from the repository.
3. Select the branch you want to deploy.
4. Render will create the `hamsatech-api` web service using `render.yaml`.
5. Set the secret environment variables in Render:

```bash
HAMSA_DEFAULT_PASSWORD=your-secure-coach-password
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
HAMSA_FRONTEND_ORIGIN=https://your-cloudflare-pages-domain.pages.dev
HAMSA_FRONTEND_ORIGINS=https://your-cloudflare-pages-domain.pages.dev,https://www.your-domain.com
```

If you are using the current Cloudflare Pages preview domain shown in this project, start with:

```bash
HAMSA_FRONTEND_ORIGIN=https://9727d29b.hamsatech-website.pages.dev
HAMSA_FRONTEND_ORIGINS=https://9727d29b.hamsatech-website.pages.dev
```

6. After Render deploys, note the public backend URL, for example:

```bash
https://hamsatech-api.onrender.com
```

7. In Cloudflare Pages, set:

```bash
VITE_API_BASE_URL=https://hamsatech-api.onrender.com
```

8. Redeploy Cloudflare Pages after updating the environment variable.

### Quick production checklist

1. Render backend deploys successfully.
2. Render health check returns `200` at `/api/health`.
3. Cloudflare Pages has `VITE_API_BASE_URL` set to the Render backend URL.
4. Render includes your Pages origin in `HAMSA_FRONTEND_ORIGINS`.
5. Render uses:

```bash
HAMSA_COOKIE_SECURE=true
HAMSA_COOKIE_SAMESITE=none
```

6. After changing env vars, redeploy both Render and Cloudflare Pages.

### Important production note

Cloudflare Pages hosts only the frontend. Signup, signin, assignment, intake, and feedback require the FastAPI backend to be deployed separately over HTTPS.

### Production cookie settings

For Cloudflare Pages frontend plus a separate HTTPS backend, use:

```bash
HAMSA_COOKIE_SECURE=true
HAMSA_COOKIE_SAMESITE=none
```

## Project Structure

```text
public/
  _redirects
  logo-mark-128.png
  logo-mark-256.png
  logo-mark-384.png
src/
  components/
  images/
  styles/
  App.tsx
  main.tsx
backend/
  app/
  requirements.txt
supabase/
  schema.sql
```

## File/Folder Guide (what each thing is for)

### Frontend (`src/`)

- `src/main.tsx` - app bootstrap (React root, `BrowserRouter`, `AuthProvider`)
- `src/App.tsx` - route table (React Router) and top-level layout
- `src/components/` - UI components + page components used by routes (ex: `Navigation.tsx`, `SignInPage.tsx`, `DashboardPage.tsx`)
- `src/context/` - React context providers (auth/session state, etc.)
- `src/lib/` - browser-side helpers (storage, API helpers, utilities)
- `src/styles/` - CSS modules used by components/pages
- `src/images/` - image assets used by the React app (keep only assets that are referenced)

#### UI map (routes → components → styles)

- Navbar: `src/components/Navigation.tsx` → `src/styles/Navigation.css`
- Landing: `/` → `src/components/NextPage.tsx` (uses shared styles in `src/App.css` / `src/index.css`)
- Home: `/home` → `src/components/Hero.tsx` + `src/components/FeatureCard.tsx` → `src/styles/Hero.css`, `src/styles/FeatureCard.css`
- About: `/about` → `src/components/AboutPage.tsx` → `src/styles/About.css`
- Auth: `/signin`, `/signup` → `src/components/SignInPage.tsx`, `src/components/SignUpPage.tsx` → `src/styles/Auth.css`
- Dashboard: `/dashboard` → `src/components/DashboardPage.tsx` → `src/styles/Dashboard.css`
- Profile: `/profile` → `src/components/ProfilePage.tsx` → `src/styles/Profile.css`
- Intake: `/athlete-intake` → `src/components/AthleteIntakePage.tsx` → `src/styles/AthleteIntake.css`

### Backend (`backend/`)

- `backend/app/main.py` - FastAPI app + routes (auth, assignment, intake, coach pages data)
- `backend/app/config.py` - environment-driven settings (CORS origins, cookie config, defaults)
- `backend/app/security.py` - password hashing + session helpers
- `backend/app/supabase_client.py` - Supabase admin client helper
- `backend/requirements.txt` - Python dependencies for FastAPI service

### Supabase (`supabase/`)

- `supabase/schema.sql` - creates all required tables (run in Supabase SQL editor)

## Notes

- `dist/` is build output and should not be committed.
- `node_modules/` is ignored.
- `.env` and `backend/.env` should not be committed.
- `.venv/` and `backend/.venv/` should not be committed.
- `.npm-cache/` (local npm cache) should not be committed.
- `vite-dev.err` / `vite-dev.log` are local logs and should not be committed.
- Internal navigation is handled with React Router.
- Safe deployment support files included in the repo:
  - `.env.example`
  - `backend/.env.example`
  - `.nvmrc`
  - `public/_redirects`
