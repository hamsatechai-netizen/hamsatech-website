# HamsaTech

HamsaTech is a Vite/React frontend with a FastAPI backend for student intake, coach review, secure coach-to-student assignment, and Supabase-backed persistence.

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

This repo includes a [`render.yaml`](c:/Users/hp/Desktop/HamsAi/render.yaml) blueprint for deploying the FastAPI backend on Render.

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
src/
  components/
  images/
  styles/
  App.tsx
  main.tsx
```

## Notes

- `dist/` is build output and should not be committed.
- `node_modules/` is ignored.
- `.env` and `backend/.env` should not be committed.
- `.venv/` and `backend/.venv/` should not be committed.
- Internal navigation is handled with React Router.
- Safe deployment support files included in the repo:
  - `.env.example`
  - `backend/.env.example`
  - `.nvmrc`
  - `public/_redirects`
