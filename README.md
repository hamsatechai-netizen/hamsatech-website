# HamsaTech Repository Documentation

HamsaTech is a Vite React web application with a FastAPI backend and Supabase persistence. The current product is focused on a coach dashboard for shooting athletes, athlete/mobile intake data, coach assignment workflows, feedback requests, notifications, and athlete performance/readiness views.

This README is intended to be the single end-to-end reference for the repository: how it runs, which routes exist, which API operations are available, which database tables are touched, and how the main workflows move from frontend to backend to Supabase.

## Coach and Athlete Performance Monitoring Requirement Coverage

The requested Coach and Athlete Performance Monitoring System is covered in this repository through two main coach-facing screens:

- Operational Coach Dashboard: `/coach/dashboard`, implemented by `src/components/coach/CoachDashboardV1Page.tsx`.
- Athlete Detail Dashboard: `/coach/athletes/:athleteId`, implemented by `src/components/CoachAthleteDetailsPage.tsx`.

The supporting backend is in `backend/app/main.py`, mainly through:

- `GET /api/v1/coaches/{coach_id}/dashboard`
- `GET /api/coach/athletes/{athlete_id}/widget`
- `GET /api/coach/athletes/{athlete_id}/sessions-widget`
- `GET /api/coach/athletes/{athlete_id}/insights-widget`
- `GET /api/coach/athletes/{athlete_id}/profile-widget`
- `POST /api/coach/athletes/{athlete_id}/feedback`

### Requirement Coverage Matrix

| Requirement area | Repo coverage | Where it is implemented |
| --- | --- | --- |
| Team-wide operational dashboard | Covered | `/coach/dashboard`, `CoachDashboardV1Page`, `GET /api/v1/coaches/{coach_id}/dashboard`. |
| Total athletes, active athletes, averages | Covered | Dashboard `totals`, `averageScore`, `averageReadiness`, `averageFatigue`, `averageStress`. |
| Athletes needing attention | Covered | Backend derives `athletesNeedingAttention`; UI shows `Need Attention` tile and risk queue. |
| Search, filter, sort athlete table | Covered | Search by athlete name, filters by gender/status/min score, sort by performance/readiness/fatigue/stress/consistency. |
| Performance/readiness/focus/discipline/stress/HR/HRV/fatigue/recovery/latest session table | Covered | Athlete table columns in `CoachDashboardV1Page`; values produced by `CoachDashboardAthleteRow`. |
| Athlete statuses: Strong, Stable, Needs Attention, At Risk | Covered | Backend `derive_status(...)`; frontend renders status chip. |
| Drill-down to athlete profile | Covered | Athlete table and risk cards link to `/coach/athletes/:athleteId`. |
| Performance vs stress/fatigue/HR/HRV/sleep/readiness/focus/consistency mapping | Covered | Backend `mapping`; frontend `ScatterPlot` cards and heatmap-style overview. |
| Top performers | Covered | Backend `topPerformers`; frontend ranking card. |
| Most disciplined athletes | Covered | Backend `mostDisciplined`; discipline derived from score records or consistency/frequency/recovery signals. |
| Healthy and focused habits | Covered | Backend `healthyFocused`; frontend habit cards show sleep, stress, fatigue, HR/HRV, recovery, focus. |
| Risk/attention queue with reason, severity, suggested action and link | Covered | Backend `risk_reasons_for_row(...)` and `suggested_action_for_reasons(...)`; frontend risk cards. |
| Athlete summary | Covered | Athlete detail summary tiles show name, age/gender, sport, coach, status, scores, latest session and trend. |
| Performance summary | Covered | Athlete detail page shows latest score, 7-day average, best 30-day average, best score, best series, improvement rate, session frequency, best vs latest. |
| Derived score breakdown | Covered | Score cards for performance, readiness, focus, discipline, recovery, fatigue, stress control, mental resilience, consistency, decision making, arousal control, social support. |
| Health and readiness mapping | Covered | Athlete detail mapping cards for fatigue, readiness, focus/consistency, mental load, stress/recovery, HR/HRV, sleep/energy, mood. |
| Training plan | Covered | Athlete detail reads `training_plans` and feedback recommendations; shows focus area, recommendation, plan status, frequency and trend. |
| Insights engine | Covered | Backend reads `athlete_insights` and also creates rule-based insight cards; UI shows title, priority, category, supporting action text. |
| Session history | Covered | Athlete detail session table shows type, score, best series, HR, fatigue, recovery, reflection and coach notes. |
| Coach feedback system | Covered | Coach can add status, note and recommendation; previous feedback history is shown. |
| Data sources listed in requirement | Covered | `athletes`, `shooting_session_log`, `athlete_scores`, `psychology_responses`, `athlete_physiology`, `coach_feedback`, `training_plans`, `athlete_insights`, plus views. |
| Required technical tables/views | Covered | `athletes`, `athlete_session_summary`, `athlete_physiology_metrics`, `athlete_psychology_scores`, `shooting_session_log`, `athlete_insights`, `coach_feedback`. |

### Requirement Flow: Operational Coach Dashboard

1. Coach signs in from `/coach/login`.
2. Frontend calls `POST /api/auth/login`.
3. Backend validates `"App_Users"`, creates `"App_Sessions"`, and sets the `hamsai_session` cookie.
4. Frontend loads `/coach/dashboard`.
5. Dashboard calls `GET /api/coach/profile` to resolve the logged-in coach to a domain `coaches.coach_id`.
6. Dashboard calls `GET /api/v1/coaches/{coach_id}/dashboard`.
7. Backend verifies the coach owns that coach UUID.
8. Backend reads assigned athletes and supporting data from `athletes`, `shooting_session_log`, `athlete_physiology`, `athlete_scores`, `psychology_responses`, `athlete_insights`, and `training_plans`.
9. Backend derives:
   - team totals and averages
   - athlete status
   - trend
   - fatigue burden
   - discipline score
   - risk reasons
   - suggested coach action
   - top performer, disciplined, healthy/focused lists
   - scatter-plot mapping points
10. Frontend renders:
   - Team Summary
   - Athlete Performance Table
   - Score Mapping scatter plots and heatmap-style strips
   - Top Performers
   - Most Disciplined
   - Healthy and Focused Habits
   - Risk / Attention Queue
   - Team Insights Feed

### Requirement Flow: Athlete Detail Dashboard

1. Coach clicks an athlete from the dashboard.
2. Frontend opens `/coach/athletes/:athleteId`.
3. Athlete detail page loads four focused widget endpoints in parallel:
   - `GET /api/coach/athletes/{athlete_id}/widget`
   - `GET /api/coach/athletes/{athlete_id}/sessions-widget`
   - `GET /api/coach/athletes/{athlete_id}/insights-widget`
   - `GET /api/coach/athletes/{athlete_id}/profile-widget`
4. Backend verifies the coach can access that athlete.
5. Backend reads the athlete profile, sessions, scores, physiology, psychology scores, insights, training plan and feedback history.
6. Frontend renders:
   - Athlete Summary
   - Performance Summary
   - Derived Score Breakdown
   - Health and Readiness Mapping
   - Physiology Panel
   - Hold Stability
   - Training Plan
   - Insights
   - Session History
   - Coach Feedback
7. When the coach submits feedback, frontend calls `POST /api/coach/athletes/{athlete_id}/feedback`.
8. Backend inserts a `coach_feedback` row.
9. Athlete detail reloads widget data so the feedback history and recommendation context stay current.

### Data Architecture for This Requirement

The monitoring feature is powered by these tables and views:

| Data source | Used for |
| --- | --- |
| `athletes` | Athlete identity, sport/discipline, coach assignment, onboarding/profile status. |
| `shooting_session_log` | Latest session, session history, training type, reflections/notes, missed/completed session signals. |
| `athlete_scores` | Overall performance, readiness, focus, discipline, consistency, best series, mobile series scores. |
| `athlete_physiology` | HR, HRV/RMSSD, fatigue, recovery, stress, sleep, hold stability and heart-rate zones. |
| `psychology_responses` | Daily check-ins, session reflections, focus/mental readiness inputs. |
| `athlete_session_summary` | Session-level performance/readiness/fatigue/stress/recovery summary view. |
| `athlete_physiology_metrics` | Normalized physiology/readiness metrics view. |
| `athlete_psychology_scores` | Aggregated psychology/focus/support scores view. |
| `training_plans` | Focus area, drills/recommendations, recovery guidance and plan status. |
| `athlete_insights` | Stored insight feed with priority, supporting data and suggested action. |
| `coach_feedback` | Coach notes, recommendations, status and feedback history. |
| `coaches` | Domain coach identity used by dashboard ownership and assignment. |
| `assignment_requests` and `coach_assignments` | New registration assignment queue and coach-athlete ownership. |
| `notifications` | Assignment and feedback notifications for coaches. |

### Derived Metric Logic

The backend derives or aggregates the following metrics in `backend/app/main.py`:

- Overall Performance Score: from `athlete_scores` score types such as `overall` or `performance`, with fallback logic when needed.
- Readiness Score: from `readiness` score records and physiology/recovery inputs.
- Fatigue Score: from fatigue score records and `athlete_physiology.fatigue_level`.
- Recovery Score: from physiology recovery score and recovery score records.
- Stress Control Score: represented through stress score, fatigue burden, recovery and status logic.
- Focus Score: from `focus` or `mental_score` score records and psychology score views.
- Discipline/Consistency Score: from `discipline` or `consistency` score records, with fallback using recent sessions, stress and fatigue.
- Habit/Healthy Focused Signals: sleep, recovery, stress, fatigue, HR/HRV and focus.
- Risk Score/Reasons: from high stress, high fatigue, poor recovery, low readiness, low focus, no recent session and declining performance.
- Improvement Trend: from score/session history.
- Training Adherence Score: in `athlete_session_summary`, based on recent session counts.

Some items are implemented as practical MVP derivations rather than a separate named table column. For example, habit score and stress control are represented through the dashboard's healthy/focused sorting, readiness/fatigue/stress values and risk/status logic.

### Actual Data Needed and Insert Order

The file `supabase/dashboard_requirement_test_data.sql` is only demo/test data. In real usage, data should normally enter through backend APIs so validation, notifications, audit logs and assignment status stay aligned. Direct SQL inserts are useful for migration, admin backfill or demos, but should follow the same order below.

#### Recommended real application flow

1. Create the database structure first.
   - Run `supabase/existing_data_safe_full_setup.sql`.
   - This creates the tables, views, indexes, RLS settings and triggers used by the dashboard.
2. Create coach login users.
   - Backend seed creates the default coach when `HAMSA_DEFAULT_PASSWORD` is set.
   - Admin coach can be created with `HAMSA_ADMIN_PASSWORD`.
   - Extra coaches can be created with `POST /api/admin/coaches`.
3. Create domain coaches.
   - `coaches` must contain the dashboard coach UUIDs.
   - The setup script seeds `C001` and `C002`.
4. Register athletes.
   - Preferred: `POST /api/mobile/athletes/register`.
   - This writes `"App_Users"`, `athletes`, `assignment_requests`, `notifications`, `audit_logs`, and a baseline score sync where possible.
5. Complete athlete profile/onboarding.
   - Preferred: `PUT /api/mobile/athletes/{athlete_id}/profile`.
   - This writes `athlete_details` and updates `athletes`.
6. Coach reviews pending assignments.
   - Frontend tab: `/coach/assignments/pending`.
   - APIs: `GET /api/v1/coaches/{coach_id}/pending_assignments`, then `POST /api/v1/assignments/assign`.
   - Assignment updates `athletes.coach_id`, writes `coach_assignments`, updates `assignment_requests`, updates matching `"App_Users"` assignment fields and writes `audit_logs`.
7. Athlete training/check-in data starts flowing.
   - Daily check-in: `POST /api/mobile/athletes/{athlete_id}/daily-checkins`.
   - Training session: `POST /api/mobile/athletes/{athlete_id}/sessions`.
   - Series scores: `POST /api/mobile/athletes/{athlete_id}/sessions/{session_id}/series`.
   - Reflection: `POST /api/mobile/athletes/{athlete_id}/sessions/{session_id}/reflection`.
   - Completion: `POST /api/mobile/athletes/{athlete_id}/sessions/{session_id}/complete`.
8. Add training plans and insights.
   - Current repo reads `training_plans` and `athlete_insights`.
   - These can be generated by an admin/service job or inserted by a future coach planning API.
9. Coach feedback is added.
   - Direct feedback: `POST /api/coach/athletes/{athlete_id}/feedback`.
   - Feedback request flow: `POST /api/v1/feedback_requests`, then `POST /api/v1/coach_feedback`.
10. Dashboard and notification tabs now have live data.
   - Dashboard reads assigned athletes, session logs, physiology, scores, insights, plans and feedback.
   - Notifications reads `notifications` filtered by `recipient_coach_id`.

#### Minimum tables needed for each screen/tab

| Screen/tab | Required minimum data | Optional/enhanced data |
| --- | --- | --- |
| Coach login | `"App_Users"` with `role = coach`, `"App_Sessions"` created on login | `coach_profiles` for phone/image/specialization. |
| Operational dashboard | `coaches`, `athletes` with `coach_id` matching `coaches.coach_id` | `shooting_session_log`, `athlete_scores`, `athlete_physiology`, `psychology_responses`, `training_plans`, `athlete_insights`, `coach_feedback`. |
| Athlete performance table | `athletes`, latest `shooting_session_log`, latest `athlete_scores` | `athlete_physiology` for HR/HRV/stress/fatigue/recovery. |
| Score mapping | `athletes`, `athlete_scores`, `athlete_physiology` | `psychology_responses` and score rows for focus/consistency. |
| Risk queue | `athletes`, `athlete_scores`, `athlete_physiology`, recent `shooting_session_log` | `athlete_insights` for richer recommendations. |
| Athlete detail dashboard | `athletes`, `shooting_session_log`, `athlete_scores` | `athlete_physiology`, `athlete_psychology_scores`, `training_plans`, `athlete_insights`, `coach_feedback`. |
| Assignments tab | `assignment_requests` with `status = PENDING`, `athletes`, `coaches` | `notifications` with `notification_type = ASSIGNMENT_REQUEST`. |
| Notifications tab/bell | `notifications.recipient_coach_id`, `message`, `notification_type`, `is_read` | `related_athlete_id`, `related_session_id`, `action_url`, linked `feedback_requests`. |
| Feedback request tab | `feedback_requests`, `notifications`, assigned `athletes` | Existing session and score data to help coach review context. |

#### Direct SQL insert order for real/backfill data

Use API flows where possible. If direct SQL is required, insert in this order to satisfy dependencies and make dashboards useful:

1. `"App_Users"`: coach app accounts for login.
2. `coaches`: domain coach records used by dashboard UUIDs.
3. `coach_profiles`: optional, but useful for profile display and coach mapping.
4. `athletes`: master athlete record. For dashboard visibility, `athletes.coach_id` must equal the target `coaches.coach_id::text`, or the athlete must have a pending assignment request for that coach.
5. `athlete_details`: profile/onboarding details. Inserts here may trigger fallback assignment-request creation if the trigger is installed.
6. `athlete_family`: optional family information.
7. `shooting_session_log`: training sessions.
8. `athlete_physiology`: HR, HRV, sleep, recovery, stress, fatigue and hold stability linked to sessions.
9. `psychology_questions`: should already be seeded by setup.
10. `psychology_responses`: daily check-ins, reflections and psychology answers.
11. `athlete_scores`: performance/readiness/focus/consistency/best-series scores.
12. `training_plans`: current plan and recommendation context.
13. `athlete_insights`: insight feed and risk/supporting action data.
14. `coach_feedback`: coach notes and recommendations.
15. `assignment_requests`: pending assignment queue items.
16. `coach_assignments`: assignment history after approval.
17. `notifications`: assignment, feedback and activity messages.
18. `audit_logs`: optional but recommended for assignment/admin traceability.

#### Minimal SQL skeleton for one assigned dashboard athlete

This is the smallest practical direct-SQL pattern for a real assigned athlete to appear in the operational dashboard with useful metrics. Replace IDs, names and dates with real values.

```sql
-- 1. Domain coach. The setup script already creates C001, but this is the pattern.
insert into public.coaches (coach_name, coach_id_text, email, specialization)
values ('HamsaTech Coach', 'C001', 'coach@hamsatech.ai', 'Shooting performance')
on conflict (coach_id_text) do update
set coach_name = excluded.coach_name,
    email = excluded.email,
    specialization = excluded.specialization,
    updated_at = now();

-- 2. Athlete assigned to that coach.
insert into public.athletes (
  athlete_id, athlete_name, name, age, gender, academy_id, coach_id,
  contact_number, email, registration_source, onboarding_status,
  profile_completion_status, created_at, updated_at
)
select
  'ATH-REAL-001',
  'Real Athlete',
  'Real Athlete',
  16,
  'Female',
  '10m Air Rifle',
  c.coach_id::text,
  '9999999999',
  'athlete@example.com',
  'mobile_app',
  'ready_to_train',
  'complete',
  now(),
  now()
from public.coaches c
where upper(c.coach_id_text) = 'C001'
on conflict (athlete_id) do update
set athlete_name = excluded.athlete_name,
    name = excluded.name,
    coach_id = excluded.coach_id,
    updated_at = now();

-- 3. Latest training session.
insert into public.shooting_session_log (
  session_id, athlete_id, coach_id, session_date, start_time, end_time,
  duration_minutes, training_type, location, notes, coach_notes,
  athlete_notes, planned_shots, completed_shots, reflection_submitted
)
select
  gen_random_uuid(),
  'ATH-REAL-001',
  c.coach_id::text,
  current_date,
  '06:00',
  '07:00',
  60,
  'Shooting',
  'Range A',
  '{"plannedShots":60,"avgHeartRate":78}',
  'Maintain pre-shot routine.',
  'Felt calm.',
  60,
  58,
  true
from public.coaches c
where upper(c.coach_id_text) = 'C001'
returning session_id;

-- 4. Physiology for the session. Use the returned session_id.
insert into public.athlete_physiology (
  physiology_id, athlete_id, session_id, recorded_date, resting_heart_rate,
  avg_heart_rate, min_heart_rate, max_heart_rate, rmssd, hrv_ms,
  hr_std_dev, sleep_hours, recovery_score, stress_score, fatigue_level,
  stability_score, acc_hold_stability, acc_settle_score, acc_spike_count, remarks
)
values (
  'PHY-REAL-001', 'ATH-REAL-001', 'PASTE-SESSION-UUID-HERE', current_date,
  62, 78, 58, 96, 65, 65, 6.1, 7.5, 82, 32, 3,
  84, 86, 82, 3, '{"mood":"Good","energyLevel":8}'
);

-- 5. Score records used by dashboard rankings and mappings.
insert into public.athlete_scores (
  score_id, athlete_id, score_type, score_value, percentile, category,
  calculated_at, source_data, created_at, updated_at
)
values
  ('SCORE-REAL-001-OVERALL', 'ATH-REAL-001', 'overall', 84, 80, 'Strong', now(), '{"source":"live"}', now(), now()),
  ('SCORE-REAL-001-READINESS', 'ATH-REAL-001', 'readiness', 82, 78, 'Strong', now(), '{"source":"live"}', now(), now()),
  ('SCORE-REAL-001-FOCUS', 'ATH-REAL-001', 'focus', 79, 74, 'Good', now(), '{"source":"live"}', now(), now()),
  ('SCORE-REAL-001-CONSISTENCY', 'ATH-REAL-001', 'consistency', 76, 70, 'Good', now(), '{"source":"live"}', now(), now()),
  ('SCORE-REAL-001-BESTSERIES', 'ATH-REAL-001', 'best_series', 96, 90, 'Strong', now(), '{"source":"live"}', now(), now())
on conflict (score_id) do update
set score_value = excluded.score_value,
    category = excluded.category,
    calculated_at = excluded.calculated_at,
    source_data = excluded.source_data,
    updated_at = now();
```

#### Minimal SQL skeleton for assignment and notification tabs

For an unassigned athlete to appear in `/coach/assignments/pending`, create the athlete first with an empty `coach_id`, then create `assignment_requests` and `notifications`.

```sql
with target_coach as (
  select coach_id
  from public.coaches
  where upper(coach_id_text) = 'C001'
  limit 1
),
new_request as (
  insert into public.assignment_requests (
    athlete_id, assigned_coach_id, status, notes, requested_at
  )
  select
    'ATH-REAL-001',
    coach_id,
    'PENDING',
    'New athlete needs coach assignment.',
    now()
  from target_coach
  returning request_id, athlete_id, assigned_coach_id
)
insert into public.notifications (
  recipient_coach_id, notification_type, related_athlete_id,
  message, action_url, title, type, entity_id, is_read, created_at
)
select
  assigned_coach_id,
  'ASSIGNMENT_REQUEST',
  athlete_id,
  'Real Athlete registered and needs coach assignment.',
  '/coach/assignments/pending',
  'New athlete assignment request',
  'ASSIGNMENT_REQUEST',
  request_id::text,
  false,
  now()
from new_request;
```

When the coach assigns from the UI, the backend updates the assignment correctly. If doing it manually, the equivalent data changes are:

```sql
update public.athletes
set coach_id = (
  select coach_id::text from public.coaches where upper(coach_id_text) = 'C001' limit 1
),
updated_at = now()
where athlete_id = 'ATH-REAL-001';

update public.assignment_requests
set status = 'ASSIGNED',
    assigned_at = now()
where athlete_id = 'ATH-REAL-001'
  and status = 'PENDING';

insert into public.coach_assignments (coach_id, athlete_id, is_active)
select coach_id, 'ATH-REAL-001', true
from public.coaches
where upper(coach_id_text) = 'C001';
```

#### Notification rows used by the bell

The coach notification bell reads:

- `notifications.recipient_coach_id`
- `notifications.notification_type`
- `notifications.related_athlete_id`
- `notifications.related_session_id`
- `notifications.message`
- `notifications.action_url`
- `notifications.created_at`
- `notifications.is_read`

Useful notification types:

- `ASSIGNMENT_REQUEST`: opens `/coach/assignments/pending`.
- `FEEDBACK_REQUEST`: opens `/coach/feedback/new?...`.
- `DAILY_CHECKIN`, `TRAINING_SESSION_STARTED`, `TRAINING_SESSION_COMPLETED`, `SESSION_REFLECTION`: activity notifications from mobile flows.

For feedback request notifications, prefer the API:

```text
POST /api/v1/feedback_requests
```

That inserts `feedback_requests`; the Supabase trigger then inserts a matching `notifications` row.

## Stack

- Frontend: React 18, TypeScript, Vite, React Router, plain CSS.
- Backend: FastAPI, Pydantic v2, Uvicorn.
- Database: Supabase Postgres through the Python Supabase client.
- Auth/session model: backend-managed password hashes and HTTP-only cookie sessions.
- Deployment: Cloudflare Pages for frontend, Render for backend.

## Repository Structure

```text
.
  public/                         Static assets and Cloudflare _redirects
  src/                            React frontend
    components/                   Page and UI components
    components/coach/             Coach dashboard, notifications, assignment and feedback pages
    context/AuthContext.tsx        Browser auth state wrapper
    lib/authApi.ts                 Frontend API client and TypeScript response types
    lib/profileStorage.ts         Local browser profile display preferences
    styles/                       Page/component CSS
    App.tsx                       React route table
    main.tsx                      React bootstrap
  backend/
    app/main.py                   FastAPI app, all API routes, workflow logic
    app/config.py                 Environment settings, CORS and cookie settings
    app/security.py               Password hashing and session token helpers
    app/supabase_client.py        Supabase admin client factory
    requirements.txt              Python dependencies
  supabase/
    existing_data_safe_full_setup.sql       Recommended current setup script
    public_lowercase_dashboard_repair.sql   Repair/setup for current lowercase public tables
    schema.sql                            Older uppercase schema baseline
    migrations/                           Feature migrations for dashboard modules
    dashboard_requirement_test_data.sql    Test/demo data for dashboard requirements
  docs/
    coach_system_backend_logic.md
    athlete_mobile_api_contracts.md
```

## Local Setup

### Frontend

```bash
npm install
copy .env.example .env
npm run dev
```

Default frontend URL:

```text
http://127.0.0.1:5173
```

Frontend environment:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

If `VITE_API_BASE_URL` is missing in a browser deployment, `src/lib/authApi.ts` falls back to:

- `http://127.0.0.1:8000` on `localhost` or `127.0.0.1`.
- `https://hamsatech-api.onrender.com` on Cloudflare Pages domains and other hosted domains.

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
copy backend\.env.example backend\.env
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Default backend URL:

```text
http://127.0.0.1:8000
```

Required backend/Supabase variables:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_SCHEMA=public
HAMSA_DEFAULT_EMAIL=coach@hamsatech.ai
HAMSA_DEFAULT_PASSWORD=replace-with-secure-coach-password
HAMSA_DEFAULT_FULL_NAME=HamsaTech Coach
HAMSA_DEFAULT_COACH_CODE=HAMSA-COACH-001
HAMSA_FRONTEND_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
HAMSA_COOKIE_SECURE=false
HAMSA_COOKIE_SAMESITE=lax
```

Optional seed accounts:

```bash
HAMSA_ADMIN_PASSWORD=replace-with-secure-admin-password
HAMSA_DEMO_STUDENT_PASSWORD=replace-with-secure-student-password
HAMSA_ENABLE_STARTUP_TEST_MAPPER=false
```

### Quality Checks

```bash
npm run lint
npm run build
```

## Frontend Routes

All frontend routes are defined in `src/App.tsx`.

| Route | Component | Purpose |
| --- | --- | --- |
| `/` | `HomePage` | Public homepage and product overview. |
| `/home` | redirect to `/` | Legacy alias. |
| `/platform` | `PlatformPage` | Platform details. |
| `/usecases` | `UseCasesPage` | Use cases. |
| `/howitworks` | `HowItWorksPage` | Process overview. |
| `/about` | `AboutPage` | About page. |
| `/signin` | `CoachLoginPage` | Coach sign-in alias. |
| `/signup` | redirect to `/coach/login` | Legacy alias. |
| `/signout` | `SignOutPage` | Calls logout and clears frontend auth state. |
| `/dashboard` | `DashboardRoute` | Role-aware redirect; coaches go to `/coach/dashboard`, others go to login. |
| `/coach/login` | `CoachLoginPage` | Coach-only login page. |
| `/coach/dashboard` | `CoachDashboardV1Page` | Operational coach dashboard. |
| `/coach/feedback/new` | `CoachFeedbackRequestPage` | Feedback request completion page. |
| `/coach/assignments/pending` | `PendingAssignmentsPage` | Assignment request queue. |
| `/coach/athletes/:athleteId` | `CoachAthleteDetailsPage` | Athlete detail dashboard and feedback form. |
| `/profile` | `ProfilePage` | Coach/student display profile and coach profile updates. |

Global frontend elements:

- `Navigation`: top nav, coach links, profile menu, notification bell for coaches.
- `Footer`: page footer.
- `ScrollNavigator`: scroll behavior helper.
- `SaarthiBot`: floating Saarthi assistant widget.
- `AppSplash` and `PageLoader`: loading states.

## Frontend API Client

All browser API calls go through `src/lib/authApi.ts`.

Important behavior:

- Every request sends `credentials: 'include'` so the HTTP-only `hamsai_session` cookie is included.
- JSON requests send `Content-Type: application/json`.
- Network calls retry with delays of `800ms`, `1600ms`, `3200ms`, and `5000ms`.
- Non-2xx responses are converted to friendly errors using the backend `detail` field.

## Backend Architecture

The backend is a single FastAPI app in `backend/app/main.py`.

Core helpers:

- `ensure_supabase()`: creates/returns the Supabase admin client.
- `ensure_seed_data()`: creates configured coach/admin/demo users on startup/login.
- `get_user_from_session()`: reads `hamsai_session`, validates `App_Sessions`, and loads `App_Users`.
- `ensure_coach_user()`: requires a logged-in coach.
- `ensure_admin_user()`: requires the admin email `admin@hamsatech.ai`.
- `resolve_dashboard_coach_key()`: maps the logged-in app user to the domain `coaches.coach_id`.
- `ensure_coach_owns_coach_id()`: prevents a coach from querying another coach's dashboard UUID.
- `coach_can_access_athlete()`: checks whether a coach can access an athlete.
- `create_notification()`: writes notification rows.
- `write_audit_log()`: writes audit entries.
- `sync_latest_overall_score()`: keeps latest score data aligned after intake/mobile updates.

Security model:

- Passwords are hashed with PBKDF2-HMAC-SHA256 and a per-user salt in `backend/app/security.py`.
- Sessions are random tokens stored in `"App_Sessions"`.
- The browser only receives an HTTP-only cookie named `hamsai_session`.
- Coach-only routes reject non-coaches with `403`.
- Most athlete data routes verify coach ownership or coach assignment before returning data.
- Supabase is accessed server-side with a service-role key; frontend does not talk directly to Supabase.

## Database Setup

For the current backend, use:

```sql
supabase/existing_data_safe_full_setup.sql
```

This script is the safest current setup because it is non-destructive:

- Creates tables if missing.
- Adds missing columns.
- Creates indexes.
- Enables RLS on the known tables.
- Creates the current views.
- Seeds default psychology questions and default domain coaches.
- Creates notification triggers for feedback requests and new athlete registrations.

If a database already exists but dashboard lowercase tables are missing, run:

```sql
supabase/public_lowercase_dashboard_repair.sql
```

Older baseline file:

```sql
supabase/schema.sql
```

`schema.sql` contains the earlier uppercase table set. The current backend mostly uses lowercase public tables for domain data, while auth still uses uppercase `"App_Users"` and `"App_Sessions"`.

## Current Table Map

`backend/app/main.py` maps current domain table names through `APP_TABLES`:

| Backend key | Current Supabase table | Main usage |
| --- | --- | --- |
| `athletes` | `public.athletes` | Athlete master rows, mobile registration, coach assignment ownership. |
| `athlete_details` | `public.athlete_details` | Athlete profile/onboarding details, mobile profile JSON fields. |
| `athlete_family` | `public.athlete_family` | Family details for full intake/profile. |
| `athlete_physiology` | `public.athlete_physiology` | Heart rate, HRV, sleep, recovery, stress, fatigue, hold stability. |
| `shooting_session_log` | `public.shooting_session_log` | Training/session records, mobile session lifecycle. |
| `psychology_questions` | `public.psychology_questions` | Seeded question definitions. |
| `psychology_responses` | `public.psychology_responses` | Intake answers, mobile daily check-ins, session reflections. |
| `coach_feedback` | `public.coach_feedback` | Coach feedback history and feedback request completion. |
| `coach_profiles` | `public.coach_profiles` | Website coach profile data linked to `"App_Users"`. |
| `coach_assignments` | `public.coach_athlete_assignments` | App-user style coach-athlete assignment history. |
| `athlete_scores` | `public.athlete_scores` | Performance, readiness, mobile series and derived score records. |
| `notifications` | `public.notifications` | Coach notification feed and general app notifications. |
| `audit_logs` | `public.audit_logs` | Assignment/intake/admin audit records. |

Additional current lowercase tables:

| Table | Main usage |
| --- | --- |
| `public.coaches` | Domain coach UUIDs used by dashboard module, assignment requests and notifications. |
| `public.coach_assignments` | Domain coach UUID to athlete assignment records. |
| `public.assignment_requests` | Pending/assigned/rejected athlete assignment workflow. |
| `public.feedback_requests` | Pending/completed coach feedback request workflow. |
| `public.training_plans` | Training plan/recommendation inputs used by widgets and views. |
| `public.athlete_insights` | Insight cards and recommendations shown to coaches. |

Auth/legacy-support tables:

| Table | Main usage |
| --- | --- |
| `public."App_Users"` | Login accounts, roles, coach codes, assignment status, student profile metadata. |
| `public."App_Sessions"` | Persistent HTTP-only session tokens. |
| `public."Athlete_Lookup"` | Name lookup compatibility for some intake/feedback flows. |

Views created by the full setup script:

| View | Main usage |
| --- | --- |
| `public.athlete_physiology_metrics` | Normalized physiology metrics such as resting HR, HRV, fatigue score and readiness score. |
| `public.athlete_psychology_scores` | Aggregated psychology score categories from responses. |
| `public.athlete_session_summary` | Session-level score/readiness/performance summary. |

## Database Columns by Functional Area

### Auth and Sessions

`"App_Users"` stores:

- `email`, `full_name`, `role`.
- `salt`, `password_hash`.
- `coach_code` for coaches.
- `assignment_status`, `assigned_coach_email`, `assigned_coach_name`.
- `requested_coach_email`, `requested_coach_name`, `requested_coach_code`, `coach_request_sent_at`.
- `sport`, `focus_area`, `date_of_birth`, `performance_score`.

`"App_Sessions"` stores:

- `session_token`, `user_email`, `created_at`, `expires_at`.

### Athlete Profile and Intake

`athletes` stores master identity and ownership:

- `athlete_id`, `athlete_name`, `name`, `age`, `gender`.
- `height_cm`, `weight_kg`, `academy_id`, `coach_id`.
- `contact_number`, `email`.
- `registration_source`, `onboarding_status`, `profile_completion_status`.
- `created_at`, `updated_at`, `updated_by`.

`athlete_details` stores profile and mobile onboarding:

- `details_id`, `athlete_id`.
- `class`, `school_name`, `diet_type`, `outside_food_frequency`.
- `sleep_time`, `wake_time`, `friend_circle`.
- `anger_pattern`, `sadness_pattern`, `academic_performance`.
- `reason_for_shooting`, `athlete_goal`.

Mobile profile JSON is packed into existing text columns:

- `academic_performance`: average practice score, target score, experience level, years shooting.
- `reason_for_shooting`: city, discipline, academy/club, performance factors.
- `athlete_goal`: 30-day and 6-month goals.

`athlete_family` stores:

- Parent names, occupations, contacts, parent email.
- Education, siblings, conservativeness, discipline, health conditions, comments.

### Sessions, Physiology, Psychology and Scores

`shooting_session_log` stores:

- `session_id`, `athlete_id`, `coach_id`.
- `session_date`, `start_time`, `end_time`, `duration_minutes`.
- `training_type`, `location`, `notes`.
- Mobile fields: `session_type`, `coach_notes`, `athlete_notes`, `planned_shots`, `completed_shots`, `missed_session`, `reflection_submitted`.

`athlete_physiology` stores:

- `physiology_id`, `athlete_id`, `session_id`, `recorded_date`.
- Heart metrics: `resting_heart_rate`, `avg_heart_rate`, `min_heart_rate`, `max_heart_rate`, `rmssd`, `hrv_ms`, `hr_std_dev`.
- Sleep/readiness metrics: `sleep_hours`, `recovery_score`, `stress_score`, `fatigue_level`.
- HR zones: `zone_1_time` to `zone_5_time`.
- Shooting stability metrics: `stability_score`, `acc_hold_stability`, `acc_settle_score`, `acc_spike_count`.
- `remarks` for JSON/text metadata.

`psychology_questions` stores:

- `question_id`, `question_text`, `category`, `question_type`.

Seeded questions:

- `Q1`: stress scale.
- `Q2`: focus scale.
- `Q3`: distraction text.
- `MOBILE_DAILY_CHECKIN`: mobile daily check-in JSON.
- `MOBILE_SESSION_REFLECTION`: mobile session reflection JSON.

`psychology_responses` stores:

- `answer_id`, `athlete_id`, `question_id`.
- `answer_text`, `answer_score`, `recorded_at`.

`athlete_scores` stores:

- `score_id`, `athlete_id`, `score_type`, `score_value`.
- `percentile`, `category`, `calculated_at`.
- `source_data` JSON, `created_at`, `updated_at`.

Common score types include:

- `overall`, `performance`, `readiness`, `fatigue`, `stress`, `recovery`.
- `consistency`, `discipline`, `focus`.
- `mobile_series`.
- `best_series`, `hold_stability`, `stability`.

### Coach, Assignment, Feedback and Notifications

`coaches` stores domain coach identities:

- `coach_id` UUID, `coach_name`, `coach_id_text`, `email`, `specialization`, `status`.

Default seeded domain coaches:

- `C001`, `coach@hamsatech.ai`, `HamsaTech Coach`.
- `C002`, `admin@hamsatech.ai`, `HamsaTech Admin`.

`coach_profiles` stores website profile metadata:

- `coach_id`, `name`, `email`, `phone`, `profile_image`, `specialization`, `status`.
- Used by `/profile` and dashboard coach UUID resolution.

`assignment_requests` stores:

- `request_id`, `athlete_id`, `requesting_coach_id`, `assigned_coach_id`.
- `status`: `PENDING`, `ASSIGNED`, or `REJECTED`.
- `notes`, `requested_at`, `assigned_at`.

`coach_assignments` stores domain assignment history:

- `assignment_id`, `coach_id`, `athlete_id`, `is_active`, `created_at`.

`coach_athlete_assignments` stores app-user assignment history:

- `assignment_id`, `athlete_id`, `coach_email`, `assigned_by`, `previous_coach_email`, `status`, `created_at`.

`feedback_requests` stores:

- `request_id`, `athlete_id`, `session_id`, `coach_id`.
- `status`: `PENDING`, `COMPLETED`, or `DISMISSED`.
- `requested_at`, `completed_at`, `feedback_id`.

`coach_feedback` stores:

- Common fields: `feedback_id`, `athlete_id`, `athlete_name`, `athlete_email`, `coach_email`, `coach_name`, `coach_id`, `coach_uid`.
- Simple feedback fields: `note`, `recommendation`, `status`.
- Detailed coach fields: `technique_score`, `focus_score`, `breathing_score`, `posture_score`, `coach_observations`, `coach_notes`, `strengths`, `training_plan`, `exercise_plan`, `improvement_areas`.
- `created_at`.

`notifications` stores:

- UUID/domain fields: `notification_id`, `recipient_coach_id`, `notification_type`, `related_athlete_id`, `related_session_id`.
- Generic app fields: `recipient_email`, `recipient_role`, `title`, `message`, `type`, `entity_id`.
- State fields: `is_read`, `read_at`, `action_url`, `created_at`.

`audit_logs` stores:

- `audit_id`, `actor_email`, `action`, `entity_type`, `entity_id`, `metadata`, `created_at`.

## Backend API Reference

All responses are JSON. Authenticated web routes use the `hamsai_session` cookie.

### Health

#### `GET /api/health`

Checks that the API process is running.

Response:

```json
{
  "success": true
}
```

### Auth

#### `POST /api/auth/login`

Logs in an existing coach/student account.

Request:

```json
{
  "email": "coach@hamsatech.ai",
  "password": "your-password"
}
```

Response:

```json
{
  "user": {
    "email": "coach@hamsatech.ai",
    "fullName": "HamsaTech Coach",
    "role": "coach",
    "coachCode": "HAMSA-COACH-001",
    "assignmentStatus": "unassigned",
    "assignedCoachCode": null,
    "assignedCoachEmail": null,
    "assignedCoachName": null,
    "requestedCoachCode": null,
    "requestedCoachEmail": null,
    "requestedCoachName": null,
    "sport": null,
    "focusArea": null,
    "dateOfBirth": null,
    "performanceScore": null
  }
}
```

Side effects:

- Calls seed refresh best-effort.
- Verifies password against `"App_Users"`.
- Inserts a row into `"App_Sessions"`.
- Sets HTTP-only `hamsai_session` cookie.

Common errors:

- `401`: no account or invalid password.
- `503`: Supabase/auth tables unavailable.

#### `GET /api/auth/me`

Returns the current cookie-authenticated user.

Response:

```json
{
  "user": {
    "email": "coach@hamsatech.ai",
    "fullName": "HamsaTech Coach",
    "role": "coach",
    "assignmentStatus": "unassigned"
  }
}
```

#### `POST /api/auth/signup`

Creates a student account and logs the student in.

Request:

```json
{
  "fullName": "Alex Rao",
  "email": "alex@example.com",
  "password": "secure-password",
  "role": "student",
  "sport": "Air Pistol",
  "focusArea": "Competition focus",
  "dateOfBirth": "2011-04-15"
}
```

Response:

```json
{
  "user": {
    "email": "alex@example.com",
    "fullName": "Alex Rao",
    "role": "student",
    "assignmentStatus": "unassigned",
    "sport": "Air Pistol",
    "focusArea": "Competition focus",
    "dateOfBirth": "2011-04-15",
    "performanceScore": 72
  }
}
```

Side effects:

- Inserts/upserts `"App_Users"`.
- Creates `"App_Sessions"`.
- Sets `hamsai_session`.

#### `POST /api/auth/logout`

Logs out the current user.

Response:

```json
{
  "success": true
}
```

Side effects:

- Deletes the current `"App_Sessions"` row if present.
- Clears `hamsai_session`.

### Student and Legacy Assignment APIs

#### `GET /api/students`

Coach-only. Returns app-user students assigned to the logged-in coach email.

Response:

```json
{
  "students": [
    {
      "email": "alex@example.com",
      "fullName": "Alex Rao",
      "assignedCoachEmail": "coach@hamsatech.ai",
      "assignedCoachName": "HamsaTech Coach",
      "sport": "Air Pistol",
      "focusArea": "Competition focus",
      "dateOfBirth": "2011-04-15",
      "performanceScore": 72
    }
  ]
}
```

Tables read:

- `"App_Users"`.

#### `POST /api/student/coach-request`

Student-only. Requests assignment to the primary/default coach.

Response:

```json
{
  "user": {
    "email": "alex@example.com",
    "fullName": "Alex Rao",
    "role": "student",
    "assignmentStatus": "pending",
    "requestedCoachEmail": "coach@hamsatech.ai",
    "requestedCoachName": "HamsaTech Coach",
    "requestedCoachCode": "HAMSA-COACH-001"
  }
}
```

Tables updated:

- `"App_Users"`.

#### `GET /api/coach/assignment-requests`

Coach-only. Lists pending student account assignment requests for the logged-in coach email.

Response:

```json
{
  "requests": [
    {
      "email": "alex@example.com",
      "fullName": "Alex Rao",
      "sport": "Air Pistol",
      "focusArea": "Competition focus",
      "requestedCoachCode": "HAMSA-COACH-001",
      "requestedCoachName": "HamsaTech Coach",
      "requestedAt": "2026-05-24T10:30:00+00:00",
      "assignmentStatus": "pending"
    }
  ]
}
```

Tables read:

- `"App_Users"`.

#### `POST /api/coach/assignment-requests/{student_email}/approve`

Coach-only. Approves a legacy student account assignment request.

Request:

```json
{
  "coachCode": "HAMSA-COACH-001"
}
```

Response:

```json
{
  "success": true
}
```

Tables updated:

- `"App_Users"`.

### Coach Profile and Admin APIs

#### `GET /api/coach/profile`

Coach-only. Returns the logged-in coach profile and creates/aligns it if needed.

Response:

```json
{
  "profile": {
    "coachId": "domain-or-profile-coach-id",
    "name": "HamsaTech Coach",
    "email": "coach@hamsatech.ai",
    "phone": null,
    "profileImage": null,
    "specialization": "Shooting performance",
    "status": "active",
    "assignedAthletes": 4,
    "createdAt": "2026-05-24T10:00:00+00:00",
    "updatedAt": "2026-05-24T10:00:00+00:00"
  }
}
```

Tables read/written:

- `coach_profiles`.
- `coaches`.
- `athletes`.

#### `PATCH /api/coach/profile`

Coach-only. Updates coach display/profile fields.

Request:

```json
{
  "name": "Coach Priya",
  "phone": "+91 9999999999",
  "profileImage": "data:image/png;base64,...",
  "specialization": "10m Air Rifle",
  "status": "active"
}
```

Response:

```json
{
  "profile": {
    "coachId": "coach-id",
    "name": "Coach Priya",
    "email": "coach@hamsatech.ai",
    "phone": "+91 9999999999",
    "profileImage": "data:image/png;base64,...",
    "specialization": "10m Air Rifle",
    "status": "active",
    "assignedAthletes": 4
  }
}
```

Tables updated:

- `coach_profiles`.

#### `GET /api/admin/coaches`

Admin-only. Lists coach profiles.

Response:

```json
{
  "coaches": [
    {
      "coachId": "coach-id",
      "name": "HamsaTech Coach",
      "email": "coach@hamsatech.ai",
      "status": "active",
      "assignedAthletes": 4
    }
  ]
}
```

#### `POST /api/admin/coaches`

Admin-only. Creates a coach app user and coach profile.

Request:

```json
{
  "name": "Coach Priya",
  "email": "priya@example.com",
  "phone": "+91 9999999999",
  "profileImage": null,
  "specialization": "Air Pistol",
  "status": "active",
  "password": "secure-password",
  "coachCode": "COACH-PRIYA"
}
```

Response:

```json
{
  "profile": {
    "coachId": "coach-id",
    "name": "Coach Priya",
    "email": "priya@example.com",
    "status": "active",
    "assignedAthletes": 0
  }
}
```

Tables written:

- `"App_Users"`.
- `coach_profiles`.

#### `PATCH /api/admin/coaches/{coach_email}`

Admin-only. Updates a coach profile.

Request:

```json
{
  "name": "Coach Priya S",
  "specialization": "Rifle and Pistol",
  "status": "active"
}
```

Response:

```json
{
  "profile": {
    "coachId": "coach-id",
    "name": "Coach Priya S",
    "email": "priya@example.com",
    "specialization": "Rifle and Pistol",
    "status": "active"
  }
}
```

#### `POST /api/admin/assignments`

Admin-only. Assigns/reassigns an athlete to a coach email in the app-user assignment model.

Request:

```json
{
  "athleteId": "athlete-id",
  "coachEmail": "coach@hamsatech.ai"
}
```

Response:

```json
{
  "success": true
}
```

Tables updated/written:

- `athletes`.
- `coach_athlete_assignments`.
- `audit_logs`.

### Intake APIs

#### `GET /api/intake/questions`

Returns seeded psychology questions.

Response:

```json
{
  "questions": [
    {
      "questionId": "Q1",
      "questionText": "How stressed do you feel?",
      "category": "Stress",
      "questionType": "Scale"
    }
  ]
}
```

Tables read/written:

- Seeds and reads `psychology_questions`.

#### `POST /api/intake/submit`

Authenticated student. Submits a full athlete intake for a student who has an assigned coach.

Request:

```json
{
  "athleteMaster": {
    "age": 15,
    "gender": "Female",
    "heightCm": 162,
    "weightKg": 51,
    "academyId": "Air Pistol",
    "contactNumber": "9999999999"
  },
  "familyDetails": {
    "motherName": "Parent One",
    "fatherName": "Parent Two",
    "motherOccupation": "Teacher",
    "fatherOccupation": "Engineer",
    "educationLevel": "Class 10",
    "siblingDetails": "One sibling",
    "familyConservative": "No",
    "disciplineLevel": "High",
    "healthConditions": "None",
    "fatherContactNumber": "9999999998",
    "motherContactNumber": "9999999997",
    "parentEmail": "parent@example.com",
    "comments": "Supportive family"
  },
  "athleteProfile": {
    "class": "10",
    "schoolName": "Hamsa School",
    "dietType": "Veg",
    "outsideFoodFrequency": "Rare",
    "sleepTime": "22:00",
    "wakeTime": "05:30",
    "friendCircle": "Small",
    "angerPattern": "Rare",
    "sadnessPattern": "Rare",
    "academicPerformance": "Good",
    "reasonForShooting": "Discipline and focus",
    "athleteGoal": "State finals"
  },
  "sessionsLog": {
    "sessionDate": "2026-05-24",
    "startTime": "07:00",
    "endTime": "08:00",
    "durationMinutes": 60,
    "trainingType": "Shooting",
    "location": "Range",
    "notes": "Baseline session"
  },
  "physiologyData": {
    "recordedDate": "2026-05-24",
    "restingHeartRate": 68,
    "avgHeartRate": 82,
    "spo2": 98,
    "breathingRate": 12,
    "sleepHours": 7.5,
    "recoveryScore": 74,
    "stressScore": 35,
    "fatigueLevel": 3,
    "remarks": "Normal"
  },
  "psychologyResponses": [
    {
      "questionId": "Q1",
      "answerText": "Moderate",
      "answerScore": 5
    }
  ]
}
```

Response:

```json
{
  "athleteId": "generated-athlete-id",
  "sessionId": "generated-session-id",
  "success": true
}
```

Tables written:

- `athletes`.
- `athlete_family`.
- `athlete_details`.
- `shooting_session_log`.
- `athlete_physiology`.
- `psychology_responses`.
- `"Athlete_Lookup"`.
- `athlete_scores` through score sync when available.
- `notifications`.
- `audit_logs`.

### General Notifications

#### `GET /api/notifications`

Authenticated. Returns generic notifications for the current user's email.

Response:

```json
{
  "notifications": [
    {
      "notificationId": "notification-id",
      "recipientEmail": "coach@hamsatech.ai",
      "recipientRole": "coach",
      "title": "New intake submitted",
      "message": "Alex Rao submitted a new athlete intake.",
      "type": "intake_submitted",
      "entityId": "athlete-id",
      "readAt": null,
      "createdAt": "2026-05-24T10:00:00+00:00"
    }
  ]
}
```

Tables read:

- `notifications`.

#### `POST /api/notifications/{notification_id}/read`

Authenticated. Marks a generic notification as read.

Response:

```json
{
  "success": true
}
```

Tables updated:

- `notifications`.

### Coach Dashboard and Athlete APIs

#### `GET /api/coach/athletes`

Coach-only. Lists athletes visible to the logged-in coach.

Query params:

- `search`: optional name/email/academy search.
- `athleteIds`: optional comma-separated filter.
- `includePending`: optional boolean to include pending assignment rows.

Response:

```json
{
  "athletes": [
    {
      "athleteId": "athlete-id",
      "name": "Alex Rao",
      "age": 15,
      "gender": "Female",
      "academyId": "Air Pistol",
      "coachId": "coach-id-or-email",
      "email": "alex@example.com",
      "contactNumber": "9999999999",
      "createdAt": "2026-05-24T10:00:00+00:00",
      "latestSessionDate": "2026-05-24",
      "latestTrainingType": "Shooting",
      "latestRecoveryScore": 74,
      "latestStressScore": 35,
      "latestFatigueLevel": 3,
      "latestSleepHours": 7.5,
      "overallScore": 72
    }
  ]
}
```

Tables read:

- `athletes`.
- `shooting_session_log`.
- `athlete_physiology`.
- `athlete_scores`.
- `assignment_requests` when pending inclusion is needed.

#### `GET /api/coach/dashboard-summary`

Coach-only. Older summary endpoint used by earlier dashboard UI.

Response:

```json
{
  "summary": {
    "totalAssignedAthletes": 4,
    "newRegistrations": 1,
    "activeAthletes": 3,
    "inactiveAthletes": 1,
    "averageScore": 72.5,
    "highestPerforming": [],
    "lowestPerforming": [],
    "scoreDistribution": {
      "Strong": 1,
      "Good": 2,
      "Needs Attention": 1
    },
    "recentActivity": [],
    "alerts": []
  }
}
```

Tables read:

- `athletes`.
- `shooting_session_log`.
- `athlete_scores`.
- `notifications`.

#### `GET /api/coach/athletes/{athlete_id}`

Coach-only. Returns full athlete detail payload.

Response:

```json
{
  "athlete": {
    "athleteMaster": {},
    "familyDetails": {},
    "athleteProfile": {},
    "scores": [],
    "sessionsLog": [],
    "physiologyData": [],
    "psychologyResponses": []
  }
}
```

Tables read:

- `athletes`.
- `athlete_family`.
- `athlete_details`.
- `shooting_session_log`.
- `athlete_physiology`.
- `psychology_responses`.
- `psychology_questions`.
- `athlete_scores`.

#### `GET /api/coach/athletes/{athlete_id}/home`

Coach-only. Returns the same kind of mobile home snapshot but protected for coach access.

Response:

```json
{
  "home": {
    "athleteId": "athlete-id",
    "displayName": "Alex Rao",
    "onboardingStatus": "ready_to_train",
    "profileCompletionStatus": "complete",
    "polar": {
      "linked": true,
      "deviceId": "polar-device-id"
    },
    "metrics": {
      "readiness": 74,
      "sleepHours": 7.5,
      "restingHr": 68,
      "hrvMs": 75
    },
    "dailyCheckin": {},
    "recommendations": []
  }
}
```

#### `GET /api/coach/athletes/{athlete_id}/widget`

Coach-only. Returns compact score/readiness/fatigue widget data.

Response:

```json
{
  "widget": {
    "athleteId": "athlete-id",
    "readiness": 74,
    "performance": 72,
    "fatigue": 30,
    "nextFocus": "Breathing stability"
  }
}
```

#### `GET /api/coach/athletes/{athlete_id}/sessions-widget`

Coach-only. Returns last session and session history summary for the athlete page.

Response:

```json
{
  "widget": {
    "athleteId": "athlete-id",
    "lastSession": {
      "sessionId": "session-id",
      "sessionDate": "2026-05-24",
      "performance": 72,
      "readiness": 74,
      "holdStability": 80,
      "mentalScore": 7,
      "fatigue": 30,
      "summaryTitle": "Stable session"
    },
    "history": []
  }
}
```

Tables/views read:

- `shooting_session_log`.
- `athlete_session_summary`.
- `athlete_scores`.
- `athlete_physiology`.
- `psychology_responses`.

#### `GET /api/coach/athletes/{athlete_id}/insights-widget`

Coach-only. Returns psychology/insight/recommendation and feedback history information.

Response:

```json
{
  "widget": {
    "athleteId": "athlete-id",
    "scores": {
      "social": 7,
      "arousal": 6,
      "decision": 8,
      "focus": 7
    },
    "recommendation": "Reduce load and review breathing drills.",
    "insights": [],
    "feedbackHistory": []
  }
}
```

Tables/views read:

- `athlete_psychology_scores`.
- `athlete_insights`.
- `coach_feedback`.
- `training_plans`.

#### `GET /api/coach/athletes/{athlete_id}/profile-widget`

Coach-only. Returns the main profile widget used by the athlete detail dashboard.

Response:

```json
{
  "widget": {
    "athleteId": "athlete-id",
    "name": "Alex Rao",
    "initials": "AR",
    "coachId": "coach-id",
    "coachName": "HamsaTech Coach",
    "age": 15,
    "gender": "Female",
    "sport": "Air Pistol",
    "currentStatus": "Stable",
    "latestSessionDate": "2026-05-24",
    "scores": {},
    "psychology": {},
    "physiology": {},
    "holdStability": {},
    "trainingPlan": "Focus on shot routine.",
    "trainingPlanStatus": "Needs Review",
    "feedbackHistory": []
  }
}
```

Tables/views read:

- `athletes`.
- `coaches`.
- `shooting_session_log`.
- `athlete_scores`.
- `athlete_physiology`.
- `athlete_psychology_scores`.
- `training_plans`.
- `coach_feedback`.

#### `GET /api/coach/athletes/{athlete_id}/scores`

Coach-only. Lists score rows for one athlete.

Response:

```json
{
  "scores": [
    {
      "scoreId": "score-id",
      "athleteId": "athlete-id",
      "scoreType": "overall",
      "scoreValue": 72,
      "percentile": null,
      "category": "Good",
      "calculatedAt": "2026-05-24T10:00:00+00:00",
      "sourceData": {},
      "createdAt": "2026-05-24T10:00:00+00:00",
      "updatedAt": "2026-05-24T10:00:00+00:00"
    }
  ]
}
```

Tables read:

- `athlete_scores`.

#### `GET /api/coach/athletes/{athlete_id}/feedback`

Coach-only. Lists coach feedback for one athlete.

Response:

```json
{
  "feedback": [
    {
      "feedbackId": "feedback-id",
      "athleteId": "athlete-id",
      "athleteName": "Alex Rao",
      "athleteEmail": "alex@example.com",
      "coachEmail": "coach@hamsatech.ai",
      "coachName": "HamsaTech Coach",
      "note": "Good focus today.",
      "recommendation": "Repeat breathing drill.",
      "status": "Progressing",
      "createdAt": "2026-05-24T10:00:00+00:00"
    }
  ]
}
```

Tables read:

- `coach_feedback`.
- `athletes`.

#### `POST /api/coach/athletes/{athlete_id}/feedback`

Coach-only. Creates direct feedback from the athlete detail page.

Request:

```json
{
  "note": "Good focus today.",
  "recommendation": "Repeat breathing drill.",
  "status": "Progressing"
}
```

Response:

```json
{
  "feedback": {
    "feedbackId": "feedback-id",
    "athleteId": "athlete-id",
    "athleteName": "Alex Rao",
    "athleteEmail": "alex@example.com",
    "coachEmail": "coach@hamsatech.ai",
    "coachName": "HamsaTech Coach",
    "note": "Good focus today.",
    "recommendation": "Repeat breathing drill.",
    "status": "Progressing",
    "createdAt": "2026-05-24T10:00:00+00:00"
  }
}
```

Tables written:

- `coach_feedback`.

#### `GET /api/student/feedback`

Student-only. Lists feedback for the current student's email/athlete rows.

Response:

```json
{
  "feedback": []
}
```

Tables read:

- `coach_feedback`.
- `athletes`.

### V1 Coach Workflow APIs

These APIs power the current coach dashboard modules.

#### `POST /api/v1/feedback_requests`

Creates a feedback request for an athlete/session/coach.

Request:

```json
{
  "athleteId": "athlete-id",
  "sessionId": "session-id",
  "coachId": "coach-uuid"
}
```

Response:

```json
{
  "requestId": "request-uuid",
  "status": "PENDING",
  "message": "Feedback request created."
}
```

Tables read/written:

- Reads `athletes` and validates coach access.
- Inserts `feedback_requests`.
- Database trigger inserts `notifications`.

#### `GET /api/v1/coaches/{coach_id}/notifications`

Coach-only. Lists domain notifications for a coach UUID.

Query params:

- `unreadOnly`: optional boolean.
- `limit`: optional integer.

Response:

```json
{
  "notifications": [
    {
      "notificationId": "notification-uuid",
      "type": "FEEDBACK_REQUEST",
      "athleteId": "athlete-id",
      "athleteName": "Alex Rao",
      "sessionId": "session-id",
      "requestId": "request-uuid",
      "message": "Alex Rao has requested feedback.",
      "actionUrl": "/coach/feedback/new?athlete_id=athlete-id&session_id=session-id&request_id=request-uuid",
      "createdAt": "2026-05-24T10:00:00+00:00",
      "isRead": false
    }
  ],
  "unreadCount": 1
}
```

Tables read:

- `notifications`.
- `athletes`.

#### `PATCH /api/v1/notifications/{notification_id}/mark_read`

Coach-only. Marks a V1 notification as read.

Response:

```json
{
  "notificationId": "notification-uuid",
  "isRead": true,
  "readAt": "2026-05-24T10:05:00+00:00"
}
```

Tables updated:

- `notifications`.

#### `POST /api/v1/coach_feedback`

Coach-only. Completes a feedback request and writes coach feedback.

Request:

```json
{
  "requestId": "request-uuid",
  "athleteId": "athlete-id",
  "note": "Good rhythm in the final series.",
  "recommendation": "Keep the same pre-shot routine.",
  "status": "Strong"
}
```

Response:

```json
{
  "feedback": {
    "feedbackId": "feedback-id",
    "athleteId": "athlete-id",
    "athleteName": "Alex Rao",
    "athleteEmail": "alex@example.com",
    "coachEmail": "coach@hamsatech.ai",
    "coachName": "HamsaTech Coach",
    "note": "Good rhythm in the final series.",
    "recommendation": "Keep the same pre-shot routine.",
    "status": "Strong",
    "createdAt": "2026-05-24T10:00:00+00:00"
  }
}
```

Tables written/updated:

- Inserts `coach_feedback`.
- Updates `feedback_requests.status` to `COMPLETED`.
- Sets `feedback_requests.completed_at`.
- Stores `feedback_requests.feedback_id`.

#### `GET /api/v1/coaches/available`

Coach-only. Lists active domain coaches for assignment dropdowns.

Response:

```json
{
  "coaches": [
    {
      "coachId": "coach-uuid",
      "coachName": "HamsaTech Coach",
      "coachIdText": "C001",
      "specialization": "Shooting performance"
    }
  ]
}
```

Tables read:

- `coaches`.

#### `GET /api/v1/coaches/{coach_id}/pending_assignments`

Coach-only. Lists pending assignment requests for a coach UUID.

Response:

```json
{
  "requests": [
    {
      "requestId": "request-uuid",
      "athleteId": "athlete-id",
      "athleteName": "Alex Rao",
      "assignedCoachId": "coach-uuid",
      "status": "PENDING",
      "notes": "Fallback auto-created on athlete profile registration",
      "requestedAt": "2026-05-24T10:00:00+00:00"
    }
  ]
}
```

Tables read:

- `assignment_requests`.
- `athletes`.

#### `POST /api/v1/assignments/assign`

Coach-only. Assigns an athlete to a selected coach.

Request:

```json
{
  "requestId": "request-uuid",
  "athleteId": "athlete-id",
  "assignedCoachId": "coach-uuid",
  "notes": "Assigned from pending assignments page"
}
```

Response:

```json
{
  "success": true,
  "assignmentId": "assignment-id"
}
```

Tables updated/written:

- Updates `athletes.coach_id`.
- Inserts best-effort `coach_assignments`.
- Updates `assignment_requests.status` to `ASSIGNED`.
- Sets `assignment_requests.assigned_at`.
- Writes `audit_logs`.
- May create/read `notifications` depending on workflow path.

#### `GET /api/v1/athletes/{athlete_id}/assignment_status`

Returns assignment status for an athlete. Useful for mobile polling.

Response:

```json
{
  "athleteId": "athlete-id",
  "status": "ASSIGNED",
  "assignedCoachId": "coach-uuid",
  "assignedCoachName": "HamsaTech Coach",
  "requestedAt": "2026-05-24T10:00:00+00:00",
  "assignedAt": "2026-05-24T10:10:00+00:00"
}
```

Tables read:

- `assignment_requests`.
- `coaches`.
- `athletes`.

#### `GET /api/v1/coaches/{coach_id}/dashboard`

Coach-only. Main operational dashboard endpoint.

Query params:

- `gender`: optional filter.
- `minScore`: optional numeric filter.
- `maxScore`: optional numeric filter.

Response:

```json
{
  "dashboard": {
    "coachId": "coach-uuid",
    "totals": {
      "totalAssignedAthletes": 4,
      "activeAthletes": 3,
      "inactiveAthletes": 1,
      "newRegistrations": 1,
      "athletesNeedingAttention": 1,
      "topPerformers": 2,
      "mostDisciplined": 2
    },
    "averageScore": 72.5,
    "averageReadiness": 76,
    "averageFatigue": 32,
    "averageStress": 38,
    "scoreDistribution": {
      "Strong": 1,
      "Stable": 2,
      "Needs Attention": 1,
      "At Risk": 0
    },
    "athletes": [],
    "topPerformers": [],
    "mostDisciplined": [],
    "healthyFocused": [],
    "riskQueue": [],
    "mapping": {
      "performanceVsFatigue": [],
      "performanceVsStress": [],
      "performanceVsHeartRate": [],
      "performanceVsHrv": [],
      "performanceVsSleep": [],
      "readinessVsPerformance": [],
      "focusVsConsistency": []
    },
    "insights": [],
    "alerts": []
  }
}
```

Main calculations:

- Score category from score value.
- Athlete status from performance/readiness/fatigue/stress/sleep.
- Trend from score history.
- Risk reasons from fatigue, stress, sleep, recovery and recent activity.
- Suggested coach action from risk reasons.

Tables/views read:

- `athletes`.
- `shooting_session_log`.
- `athlete_physiology`.
- `athlete_scores`.
- `psychology_responses`.
- `athlete_insights`.
- `training_plans`.
- Assignment tables as needed for coach ownership.

#### `GET /api/v1/athletes/{athlete_id}/full_profile`

Coach-only. Combines full athlete detail with feedback history.

Response:

```json
{
  "athlete": {
    "athleteMaster": {},
    "familyDetails": {},
    "athleteProfile": {},
    "scores": [],
    "sessionsLog": [],
    "physiologyData": [],
    "psychologyResponses": [],
    "feedbackHistory": []
  }
}
```

Tables read:

- Same as `/api/coach/athletes/{athlete_id}`.
- Plus `coach_feedback`.

### Mobile Athlete APIs

These endpoints support athlete mobile onboarding, check-in and training-session flows. They do not require the browser cookie session; the athlete is identified by `athlete_id`.

#### `POST /api/mobile/athletes/register`

Creates or updates a mobile athlete registration.

Request:

```json
{
  "athleteId": "optional-client-id",
  "fullName": "Alex Rao",
  "email": "alex@example.com",
  "age": 15,
  "gender": "Female",
  "phone": "9999999999",
  "sport": "Air Pistol",
  "focusArea": "Competition focus",
  "coachId": "optional-coach-uuid",
  "coachCode": "C001"
}
```

Response:

```json
{
  "athleteId": "athlete-id",
  "assignedCoachEmail": "coach@hamsatech.ai",
  "notificationCreated": true,
  "success": true
}
```

Tables written:

- `athletes`.
- `assignment_requests`.
- `notifications`.
- `"Athlete_Lookup"`.

Assignment behavior:

- If a target coach is supplied/resolved, an assignment request is created.
- If not, fallback default coach `C001` is used when available.
- New registration notifications are sent to the target/default coach.

#### `GET /api/mobile/athletes/{athlete_id}/profile`

Returns the athlete profile.

Response:

```json
{
  "profile": {
    "athleteId": "athlete-id",
    "fullName": "Alex Rao",
    "email": "alex@example.com",
    "age": 15,
    "gender": "Female",
    "city": "Hyderabad",
    "discipline": "Air Pistol",
    "experienceLevel": "Beginner",
    "yearsShooting": 1,
    "academyClub": "Hamsa Academy",
    "averagePracticeScore": 150,
    "targetScore": 580,
    "performanceFactors": ["Nervousness"],
    "goal30Days": "Reach 560",
    "goal6Months": "Qualify for state finals",
    "restingHrBaseline": 68,
    "hrvBaselineMs": 75,
    "polarLinked": true,
    "polarDeviceId": "polar-device-id",
    "onboardingStatus": "ready_to_train",
    "profileCompletionStatus": "complete"
  }
}
```

Tables read:

- `athletes`.
- `athlete_details`.
- `athlete_physiology`.

#### `PUT /api/mobile/athletes/{athlete_id}/profile`

Creates or updates profile details.

Request:

```json
{
  "fullName": "Alex Rao",
  "age": 15,
  "gender": "Female",
  "city": "Hyderabad",
  "discipline": "Air Pistol",
  "experienceLevel": "Beginner",
  "yearsShooting": 1,
  "academyClub": "Hamsa Academy",
  "averagePracticeScore": 150,
  "targetScore": 580,
  "performanceFactors": ["Nervousness in competition", "Poor sleep"],
  "goal30Days": "Reach 560 in training",
  "goal6Months": "Qualify for state finals"
}
```

Response:

```json
{
  "profile": {
    "athleteId": "athlete-id",
    "fullName": "Alex Rao",
    "discipline": "Air Pistol",
    "onboardingStatus": "profile_created",
    "profileCompletionStatus": "complete"
  }
}
```

Tables updated/written:

- `athletes`.
- `athlete_details`.
- May trigger database assignment notification if `athlete_details` insert fires the trigger.

#### `POST /api/mobile/athletes/{athlete_id}/baseline`

Stores Polar/baseline physiology information.

Request:

```json
{
  "restingHrBaseline": 68,
  "hrvBaselineMs": 75,
  "polarLinked": true,
  "polarDeviceId": "polar-device-id"
}
```

Response:

```json
{
  "profile": {
    "athleteId": "athlete-id",
    "restingHrBaseline": 68,
    "hrvBaselineMs": 75,
    "polarLinked": true,
    "polarDeviceId": "polar-device-id",
    "onboardingStatus": "ready_to_train",
    "profileCompletionStatus": "complete"
  }
}
```

Tables written:

- `shooting_session_log` with `training_type = Recovery`.
- `athlete_physiology`.
- `athletes` onboarding/profile status.

#### `POST /api/mobile/athletes/{athlete_id}/daily-checkins`

Stores daily athlete check-in as a psychology response.

Request:

```json
{
  "checkinDate": "2026-05-24",
  "mood": "Good",
  "energyLevel": 5,
  "sleepBand": "7-8h",
  "sleepHours": 7.5,
  "tags": ["Focused", "Calm"],
  "notes": "Ready for training"
}
```

Response:

```json
{
  "checkin": {
    "answerId": "answer-id",
    "athleteId": "athlete-id",
    "checkinDate": "2026-05-24",
    "mood": "Good",
    "energyLevel": 5,
    "sleepBand": "7-8h",
    "sleepHours": 7.5,
    "tags": ["Focused", "Calm"],
    "notes": "Ready for training",
    "recordedAt": "2026-05-24T10:00:00+00:00"
  }
}
```

Tables written:

- `psychology_questions` seed.
- `psychology_responses` with `question_id = MOBILE_DAILY_CHECKIN`.
- `notifications` to coach.

#### `GET /api/mobile/athletes/{athlete_id}/daily-checkins/latest`

Returns the latest daily check-in.

Response:

```json
{
  "checkin": {
    "answerId": "answer-id",
    "athleteId": "athlete-id",
    "mood": "Good",
    "energyLevel": 5,
    "sleepBand": "7-8h",
    "sleepHours": 7.5
  }
}
```

Tables read:

- `psychology_responses`.

#### `GET /api/mobile/athletes/{athlete_id}/home`

Returns the mobile home snapshot.

Response:

```json
{
  "home": {
    "athleteId": "athlete-id",
    "displayName": "Alex Rao",
    "onboardingStatus": "ready_to_train",
    "profileCompletionStatus": "complete",
    "polar": {
      "linked": true,
      "deviceId": "polar-device-id"
    },
    "metrics": {
      "readiness": 74,
      "sleepHours": 7.5,
      "restingHr": 68,
      "hrvMs": 75
    },
    "dailyCheckin": {},
    "recentSessions": [],
    "coachFeedback": [],
    "recommendations": []
  }
}
```

Tables read:

- `athletes`.
- `athlete_details`.
- `athlete_physiology`.
- `psychology_responses`.
- `shooting_session_log`.
- `athlete_scores`.
- `coach_feedback`.
- `training_plans`.

#### `POST /api/mobile/athletes/{athlete_id}/sessions`

Creates a mobile training session.

Request:

```json
{
  "rangeType": "Paper",
  "sessionType": "Scoring",
  "plannedShots": 60,
  "discipline": "Air Pistol",
  "intention": "Stay composed on trigger",
  "visualization": "Clean 10, steady breath",
  "bodyScanCompleted": true,
  "startNow": true
}
```

Response:

```json
{
  "session": {
    "sessionId": "session-id",
    "athleteId": "athlete-id",
    "sessionDate": "2026-05-24",
    "trainingType": "Shooting",
    "rangeType": "Paper",
    "sessionType": "Scoring",
    "plannedShots": 60,
    "status": "LIVE"
  }
}
```

Tables written:

- `shooting_session_log`.
- `notifications` to coach.

#### `GET /api/mobile/athletes/{athlete_id}/sessions?limit=20`

Lists mobile training sessions.

Response:

```json
{
  "sessions": [
    {
      "sessionId": "session-id",
      "athleteId": "athlete-id",
      "sessionDate": "2026-05-24",
      "trainingType": "Shooting",
      "status": "COMPLETED"
    }
  ]
}
```

Tables read:

- `shooting_session_log`.

#### `POST /api/mobile/athletes/{athlete_id}/sessions/{session_id}/series`

Stores one series of shot scores.

Request:

```json
{
  "seriesNumber": 2,
  "shots": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
  "avgHeartRate": 80
}
```

Response:

```json
{
  "series": {
    "scoreId": "score-id",
    "sessionId": "session-id",
    "seriesNumber": 2,
    "shots": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
    "total": 60,
    "avgHeartRate": 80
  },
  "summary": {}
}
```

Tables written:

- `athlete_scores` with `score_type = mobile_series` and `source_data.sessionId`.

#### `POST /api/mobile/athletes/{athlete_id}/sessions/{session_id}/reflection`

Stores post-session reflection.

Request:

```json
{
  "mood": "Okay",
  "whatWorked": "Breathing was steady",
  "whatDidnt": "Lost focus in series 2",
  "voiceNoteUrl": null,
  "selfRating": 6,
  "fatigueLevel": 7
}
```

Response:

```json
{
  "reflection": {
    "answerId": "answer-id",
    "sessionId": "session-id",
    "mood": "Okay",
    "whatWorked": "Breathing was steady",
    "whatDidnt": "Lost focus in series 2",
    "selfRating": 6,
    "fatigueLevel": 7
  },
  "summary": {}
}
```

Tables written:

- `psychology_questions` seed.
- `psychology_responses` with `question_id = MOBILE_SESSION_REFLECTION`.
- `notifications` to coach.

#### `POST /api/mobile/athletes/{athlete_id}/sessions/{session_id}/complete`

Completes a mobile training session.

Request:

```json
{
  "durationSeconds": 3600,
  "avgHeartRate": 77,
  "peakHeartRate": 92,
  "fatigue": "Low",
  "recovery": "Fair"
}
```

Response:

```json
{
  "summary": {
    "sessionId": "session-id",
    "totalScore": 540,
    "averageShot": 9,
    "efficiency": 90,
    "bestShot": 10,
    "worstShot": 7,
    "series": [],
    "physiology": {},
    "reflection": {},
    "keyInsight": "Stable rhythm with manageable fatigue.",
    "recommendations": []
  }
}
```

Tables updated/written:

- Updates `shooting_session_log`.
- Inserts `athlete_physiology` when heart-rate payload is present.
- Sends coach notification.

#### `GET /api/mobile/athletes/{athlete_id}/sessions/{session_id}/summary`

Returns session summary.

Response:

```json
{
  "summary": {
    "sessionId": "session-id",
    "totalScore": 540,
    "averageShot": 9,
    "series": [],
    "physiology": {},
    "reflection": {},
    "recommendations": []
  }
}
```

Tables read:

- `shooting_session_log`.
- `athlete_scores`.
- `athlete_physiology`.
- `psychology_responses`.

## End-to-End Functional Workflows

### 1. Coach Login and Dashboard Load

1. Coach enters credentials on `/coach/login`.
2. Frontend calls `POST /api/auth/login`.
3. Backend reads `"App_Users"`, verifies password and writes `"App_Sessions"`.
4. Browser receives `hamsai_session`.
5. Navigation/AuthContext calls `GET /api/auth/me`.
6. `/dashboard` redirects coach to `/coach/dashboard`.
7. Dashboard page calls `GET /api/coach/profile`.
8. Backend resolves/creates `coach_profiles` and maps to domain `coaches.coach_id`.
9. Dashboard page calls `GET /api/v1/coaches/{coach_id}/dashboard`.
10. Backend reads athlete/session/score/physiology/psychology/insight/training-plan data and returns the dashboard model.

### 2. Mobile Athlete Registration to Pending Assignment

1. Mobile app calls `POST /api/mobile/athletes/register`.
2. Backend upserts `athletes`.
3. Backend resolves target coach by `coachId`, `coachCode`, default `C001`, or fallback coach.
4. Backend creates `assignment_requests` with `PENDING`.
5. Backend creates a `notifications` row for the coach.
6. Coach notification bell reads `GET /api/v1/coaches/{coach_id}/notifications`.
7. Coach opens `/coach/assignments/pending`.
8. Frontend calls `GET /api/v1/coaches/{coach_id}/pending_assignments`.
9. Coach selects a coach and clicks assign.
10. Frontend calls `POST /api/v1/assignments/assign`.
11. Backend updates `athletes.coach_id`, writes `coach_assignments`, marks `assignment_requests` as `ASSIGNED`, and writes `audit_logs`.

### 3. Athlete Profile Completion

1. Mobile app calls `PUT /api/mobile/athletes/{athlete_id}/profile`.
2. Backend updates `athletes` master fields and upserts `athlete_details`.
3. Mobile app calls `POST /api/mobile/athletes/{athlete_id}/baseline`.
4. Backend inserts a recovery session in `shooting_session_log`.
5. Backend inserts baseline metrics in `athlete_physiology`.
6. Backend updates onboarding/profile status on `athletes`.
7. Coach dashboard and athlete profile widgets can now show profile, Polar/baseline and readiness data.

### 4. Daily Check-In

1. Mobile app calls `POST /api/mobile/athletes/{athlete_id}/daily-checkins`.
2. Backend ensures mobile psychology questions exist.
3. Backend inserts `psychology_responses` with `question_id = MOBILE_DAILY_CHECKIN`.
4. Backend notifies the assigned coach through `notifications`.
5. Mobile home and coach athlete home read the latest check-in from `psychology_responses`.

### 5. Training Session, Series, Reflection and Summary

1. Mobile app calls `POST /api/mobile/athletes/{athlete_id}/sessions`.
2. Backend inserts `shooting_session_log` and notifies the coach.
3. Mobile app calls `POST /api/mobile/athletes/{athlete_id}/sessions/{session_id}/series` for each series.
4. Backend inserts `athlete_scores` rows with `score_type = mobile_series`.
5. Mobile app calls `POST /api/mobile/athletes/{athlete_id}/sessions/{session_id}/reflection`.
6. Backend inserts `psychology_responses` with `question_id = MOBILE_SESSION_REFLECTION`.
7. Mobile app calls `POST /api/mobile/athletes/{athlete_id}/sessions/{session_id}/complete`.
8. Backend updates `shooting_session_log`, may insert `athlete_physiology`, and notifies the coach.
9. Summary reads session, score, physiology and reflection rows.
10. Coach dashboard and athlete detail widgets use this data in rankings, risk queue, charts and session history.

### 6. Feedback Request and Completion

1. A client calls `POST /api/v1/feedback_requests`.
2. Backend validates coach/athlete access and inserts `feedback_requests`.
3. Supabase trigger `notify_coach_feedback_request` inserts `notifications`.
4. Notification bell calls `GET /api/v1/coaches/{coach_id}/notifications`.
5. Coach opens `/coach/feedback/new?...`.
6. Coach submits the feedback form.
7. Frontend calls `POST /api/v1/coach_feedback`.
8. Backend inserts `coach_feedback`.
9. Backend marks the `feedback_requests` row `COMPLETED`.
10. Frontend marks notification read with `PATCH /api/v1/notifications/{notification_id}/mark_read`.

### 7. Direct Coach Feedback From Athlete Detail

1. Coach opens `/coach/athletes/{athleteId}`.
2. Page loads profile, sessions, insights and feedback widgets.
3. Coach submits the feedback form.
4. Frontend calls `POST /api/coach/athletes/{athlete_id}/feedback`.
5. Backend inserts `coach_feedback`.
6. Feedback appears in the athlete detail history and mobile/athlete home views.

### 8. Full Student Intake

1. Student logs in with an assigned coach.
2. Frontend/mobile calls `GET /api/intake/questions`.
3. Student submits `POST /api/intake/submit`.
4. Backend creates master, family, profile, session, physiology and psychology rows.
5. Backend writes `"Athlete_Lookup"`.
6. Backend syncs latest score when possible.
7. Backend notifies assigned coach and writes an audit log.

## Supabase Triggers

### Feedback Request Notification

Defined in:

- `supabase/existing_data_safe_full_setup.sql`
- `supabase/migrations/20260519_module1_feedback_request_flow.sql`

Trigger:

```text
trigger_feedback_request_notification
```

Behavior:

- Fires after insert on `feedback_requests`.
- Looks up athlete name.
- Inserts a `notifications` row with `notification_type = FEEDBACK_REQUEST`.
- Sets action URL to `/coach/feedback/new?...`.

### New User Assignment Request Notification

Defined in:

- `supabase/existing_data_safe_full_setup.sql`
- `supabase/migrations/20260519_module2_assignment_flow.sql`
- `supabase/migrations/20260521_assignment_notification_alignment.sql`

Trigger:

```text
trigger_new_user_assignment_request
```

Behavior:

- Fires after insert on `athlete_details`.
- Checks if a pending assignment request already exists.
- Finds default coach `C001`.
- Inserts `assignment_requests` row with `PENDING`.
- Inserts `notifications` row with `notification_type = ASSIGNMENT_REQUEST`.

## Frontend Page to API Map

| Page/component | Main API calls |
| --- | --- |
| `CoachLoginPage` | `POST /api/auth/login`, `GET /api/auth/me`. |
| `SignOutPage` | `POST /api/auth/logout`. |
| `Navigation` | Auth context, local profile storage, coach notification UI. |
| `NotificationBell` | `GET /api/coach/profile`, `GET /api/v1/coaches/{coach_id}/notifications`, `PATCH /api/v1/notifications/{id}/mark_read`. |
| `CoachDashboardV1Page` | `GET /api/coach/profile`, `GET /api/v1/coaches/{coach_id}/dashboard`. |
| `PendingAssignmentsPage` | `GET /api/coach/profile`, `GET /api/v1/coaches/{coach_id}/pending_assignments`, `GET /api/v1/coaches/available`, `POST /api/v1/assignments/assign`. |
| `CoachFeedbackRequestPage` | `POST /api/v1/coach_feedback`, `PATCH /api/v1/notifications/{id}/mark_read`. |
| `CoachAthleteDetailsPage` | `GET /api/coach/athletes/{id}/widget`, `/sessions-widget`, `/insights-widget`, `/profile-widget`, `POST /api/coach/athletes/{id}/feedback`. |
| `ProfilePage` | `GET /api/coach/profile`, `PATCH /api/coach/profile`, local profile display storage. |

## Deployment

### Cloudflare Pages Frontend

Use:

```text
Framework preset: Vite
Build command: npm run build
Build output directory: dist
Node version: 20 recommended
```

Required Pages environment variable:

```bash
VITE_API_BASE_URL=https://hamsatech-api.onrender.com
```

The repo includes:

```text
public/_redirects
```

This makes React Router deep links work on Cloudflare Pages by routing all frontend paths back to `index.html`.

### Render Backend

The repo includes:

```text
render.yaml
```

Set these secret environment variables in Render:

```bash
HAMSA_DEFAULT_PASSWORD=your-secure-coach-password
HAMSA_ADMIN_PASSWORD=your-secure-admin-password
HAMSA_DEMO_STUDENT_PASSWORD=optional-demo-student-password
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_SCHEMA=public
HAMSA_FRONTEND_ORIGIN=https://your-cloudflare-pages-domain.pages.dev
HAMSA_FRONTEND_ORIGINS=https://your-cloudflare-pages-domain.pages.dev,https://www.your-domain.com
HAMSA_COOKIE_SECURE=true
HAMSA_COOKIE_SAMESITE=none
```

Production checklist:

1. Run `supabase/existing_data_safe_full_setup.sql` in Supabase.
2. Deploy backend on Render.
3. Confirm `GET /api/health` returns `{"success": true}`.
4. Set Cloudflare `VITE_API_BASE_URL` to the Render URL.
5. Include every Cloudflare/custom domain origin in `HAMSA_FRONTEND_ORIGINS`.
6. Use `HAMSA_COOKIE_SECURE=true` and `HAMSA_COOKIE_SAMESITE=none` for cross-site production cookies.
7. Redeploy Render and Cloudflare after environment changes.

## Important Operational Notes

- The frontend cannot complete login, dashboard, assignment, athlete detail or feedback workflows unless the FastAPI backend is deployed and reachable.
- The backend requires Supabase service-role access. Do not expose the service-role key to the frontend.
- Current domain data should use lowercase public tables from `existing_data_safe_full_setup.sql`.
- `"App_Users"` and `"App_Sessions"` remain uppercase because they are the current app auth tables.
- `dist/`, `node_modules/`, `.venv/`, `.npm-cache/`, `.env`, and `backend/.env` are local/generated and should not be committed.
- Local logs such as `vite-dev.log`, `vite-dev.err`, `backend-uvicorn.log`, and `backend-uvicorn.err.log` are not part of application behavior.

## Useful Files

- Frontend routes: `src/App.tsx`.
- Frontend API contracts: `src/lib/authApi.ts`.
- Auth state: `src/context/AuthContext.tsx`.
- Backend API: `backend/app/main.py`.
- Backend settings: `backend/app/config.py`.
- Password/session helpers: `backend/app/security.py`.
- Supabase client: `backend/app/supabase_client.py`.
- Current database setup: `supabase/existing_data_safe_full_setup.sql`.
- Dashboard repair setup: `supabase/public_lowercase_dashboard_repair.sql`.
- Test data: `supabase/dashboard_requirement_test_data.sql`.
- Additional backend flow notes: `docs/coach_system_backend_logic.md`.
- Mobile API contract notes: `docs/athlete_mobile_api_contracts.md`.
