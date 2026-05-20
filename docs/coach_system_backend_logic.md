# HamsaTech Coach System: Backend Logic and Generation Scripts

## Scope
This document explains:
- backend API logic used by coach flows (Module 1, 2, 3)
- DB migrations/triggers that generate notifications and workflow records
- how frontend pages consume these APIs

Codebase root: `D:/hamsa_code/hamsatech-website`

---

## 1) Backend Architecture

Backend is a single FastAPI app in:
- `D:/hamsa_code/hamsatech-website/backend/app/main.py`

Core patterns:
- Cookie session auth (`App_Sessions`) for web/API requests
- Role checks via helper functions:
  - `ensure_coach_user(...)`
  - `get_authenticated_user(...)`
- Supabase client access:
  - `ensure_supabase()`
- Coach-to-domain mapping:
  - `resolve_dashboard_coach_key(...)`
  - maps App user (email/coachCode) to domain `hamsatech.coaches.coach_id` UUID

Safe query pattern:
- `safe_table_rows(table_name, query_builder)` returns `[]` on failures for optional/non-critical reads

---

## 2) Database Scripts (Migrations)

### Module 1 migration
File:
- `D:/hamsa_code/hamsatech-website/supabase/migrations/20260519_module1_feedback_request_flow.sql`

Creates:
- `hamsatech.notifications`
- `hamsatech.feedback_requests`
- indexes:
  - `idx_notifications_coach_unread`
  - `idx_feedback_requests_status`

Trigger logic:
- function `hamsatech.notify_coach_feedback_request()`
- trigger `trigger_feedback_request_notification`
- behavior: on `feedback_requests` insert, auto-inserts a coach notification.

### Module 2 migration
File:
- `D:/hamsa_code/hamsatech-website/supabase/migrations/20260519_module2_assignment_flow.sql`

Creates:
- `hamsatech.assignment_requests`
- index:
  - `idx_assignment_requests_pending`

Trigger logic:
- function `hamsatech.notify_default_coach_new_registration()`
- trigger `trigger_new_user_assignment_request` on `hamsatech.athlete_details`
- behavior:
  - creates pending assignment request
  - creates `NEW_USER_REGISTRATION` notification for default coach (`C001` fallback first coach).

---

## 3) Module 1: Session Feedback Request Flow

## DB write flow
1. Client calls `POST /api/v1/feedback_requests`
2. Backend validates athlete exists and belongs to target coach
3. Backend inserts row in `feedback_requests`
4. DB trigger auto-creates row in `notifications`

## Endpoints
- `POST /api/v1/feedback_requests`
  - input: `athleteId, sessionId, coachId`
  - output: `requestId, status=PENDING`

- `GET /api/v1/coaches/{coach_id}/notifications`
  - params: `unreadOnly`, `limit`
  - output: notifications + unread count

- `PATCH /api/v1/notifications/{notification_id}/mark_read`
  - marks one notification read

- `POST /api/v1/coach_feedback`
  - input: `requestId, athleteId, note, recommendation, status`
  - behavior:
    - inserts into `coach_feedback`
    - updates matching `feedback_requests` row to `COMPLETED`

Frontend consumers:
- notification widget:
  - `src/components/coach/NotificationBell.tsx`
- feedback form page:
  - `src/components/coach/CoachFeedbackRequestPage.tsx`

---

## 4) Module 2: New User Assignment Flow

## DB write flow
1. Athlete profile insert in `hamsatech.athlete_details`
2. DB trigger creates:
   - pending row in `assignment_requests`
   - `NEW_USER_REGISTRATION` row in `notifications`

## Endpoints
- `GET /api/v1/coaches/available`
  - returns coach list for assignment dropdown

- `GET /api/v1/coaches/{coach_id}/pending_assignments`
  - returns pending assignment queue for coach

- `POST /api/v1/assignments/assign`
  - updates athlete `coach_id`
  - writes assignment to `coach_assignments` (best effort insert)
  - marks `assignment_requests` row `ASSIGNED`
  - writes audit log

- `GET /api/v1/athletes/{athlete_id}/assignment_status`
  - mobile/web status polling endpoint

Frontend consumer:
- `src/components/coach/PendingAssignmentsPage.tsx`

---

## 5) Module 3: Coach Dashboard (Read-Only Views)

## Main endpoint
- `GET /api/v1/coaches/{coach_id}/dashboard`

Logic:
1. Verify coach session + coach UUID ownership
2. Reuse `list_coach_athletes(... include_pending=false ...)`
3. Build derived metrics:
   - total athletes
   - average score
   - score distribution
   - alerts
4. Apply optional filters:
   - `gender`
   - `minScore`
   - `maxScore`

## Athlete full profile endpoint
- `GET /api/v1/athletes/{athlete_id}/full_profile`

Logic:
1. Reuses existing athlete detail endpoint
2. Reuses feedback listing endpoint
3. Returns combined payload with `feedbackHistory`

Frontend consumer:
- dashboard page:
  - `src/components/coach/CoachDashboardV1Page.tsx`
- athlete detail page:
  - `src/components/CoachAthleteDetailsPage.tsx`

---

## 6) Frontend API Client Layer

File:
- `D:/hamsa_code/hamsatech-website/src/lib/authApi.ts`

Module 1 methods:
- `createFeedbackRequest(...)`
- `getCoachNotificationsV1(...)`
- `markCoachNotificationRead(...)`
- `createCoachFeedbackV1(...)`

Module 2 methods:
- `getPendingAssignments(...)`
- `getAvailableCoaches(...)`
- `assignAthlete(...)`

Module 3 methods:
- `getCoachDashboardV1(...)`
- `getAthleteFullProfileV1(...)`

All methods use shared `request<T>(path, init)` with cookie credentials.

---

## 7) Security and Access Rules in Code

- Coach-only endpoints call `ensure_coach_user(...)`
- Coach resource ownership is enforced using `ensure_coach_owns_coach_id(...)`
- Athlete access in detail/feedback paths checks assigned `coach_id`
- Assignment writes create audit entries through `write_audit_log(...)`

---

## 8) Operational Notes

- Migrations must be applied in Supabase before API endpoints are used.
- Current UI and APIs assume schema `hamsatech`.
- Notification dropdown polls every 30 seconds (MVP strategy).
- Existing coach/athlete mapping depends on `resolve_dashboard_coach_key(...)`.

---

## 9) Quick File Map

- Backend API + logic:
  - `D:/hamsa_code/hamsatech-website/backend/app/main.py`

- DB migrations:
  - `D:/hamsa_code/hamsatech-website/supabase/migrations/20260519_module1_feedback_request_flow.sql`
  - `D:/hamsa_code/hamsatech-website/supabase/migrations/20260519_module2_assignment_flow.sql`

- Coach UI:
  - `D:/hamsa_code/hamsatech-website/src/components/coach/CoachDashboardV1Page.tsx`
  - `D:/hamsa_code/hamsatech-website/src/components/coach/NotificationBell.tsx`
  - `D:/hamsa_code/hamsatech-website/src/components/coach/CoachFeedbackRequestPage.tsx`
  - `D:/hamsa_code/hamsatech-website/src/components/coach/PendingAssignmentsPage.tsx`

- Athlete detail UI:
  - `D:/hamsa_code/hamsatech-website/src/components/CoachAthleteDetailsPage.tsx`
