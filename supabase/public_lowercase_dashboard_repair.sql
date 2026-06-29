-- Public-schema repair for the current FastAPI backend.
-- Run this in Supabase SQL Editor before dashboard_requirement_test_data.sql.
-- It creates the lowercase public tables that backend/app/main.py queries.

create extension if not exists pgcrypto;

create table if not exists public.coaches (
  coach_id uuid primary key default gen_random_uuid(),
  coach_name text not null,
  coach_id_text text unique,
  email text unique,
  specialization text,
  status text not null default 'active' check (status in ('active', 'inactive')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.athletes (
  athlete_id text primary key,
  athlete_name text,
  name text not null,
  age integer,
  gender text,
  height_cm numeric,
  weight_kg numeric,
  academy_id text,
  coach_id text not null default '',
  contact_number text,
  email text,
  registration_source text default 'website',
  onboarding_status text default 'registered',
  profile_completion_status text default 'partial',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  updated_by text
);

create table if not exists public.athlete_details (
  details_id text primary key,
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  class text,
  school_name text,
  diet_type text,
  outside_food_frequency text,
  sleep_time text,
  wake_time text,
  friend_circle text,
  anger_pattern text,
  sadness_pattern text,
  academic_performance text,
  reason_for_shooting text,
  athlete_goal text
);

create table if not exists public.athlete_family (
  family_id text primary key,
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  mother_name text,
  father_name text,
  mother_occupation text,
  father_occupation text,
  education_level text,
  sibling_details text,
  family_conservative text,
  discipline_level text,
  health_conditions text,
  father_contact_number text,
  mother_contact_number text,
  parent_email text,
  comments text
);

create table if not exists public.shooting_session_log (
  session_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  coach_id text not null default '',
  session_date date not null,
  start_time text,
  end_time text,
  duration_minutes integer,
  training_type text,
  location text,
  notes jsonb,
  session_type text,
  coach_notes text,
  athlete_notes text,
  planned_shots integer,
  completed_shots integer,
  missed_session boolean not null default false,
  reflection_submitted boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.athlete_physiology (
  physiology_id text primary key,
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  session_id uuid references public.shooting_session_log(session_id) on delete cascade,
  recorded_date date not null,
  resting_heart_rate integer,
  avg_heart_rate integer,
  min_heart_rate integer,
  max_heart_rate integer,
  rmssd numeric,
  hrv_ms numeric,
  hr_std_dev numeric,
  sleep_hours numeric,
  recovery_score integer,
  stress_score integer,
  fatigue_level integer,
  zone_1_time integer not null default 0,
  zone_2_time integer not null default 0,
  zone_3_time integer not null default 0,
  zone_4_time integer not null default 0,
  zone_5_time integer not null default 0,
  stability_score numeric,
  acc_hold_stability numeric,
  acc_settle_score numeric,
  acc_spike_count integer,
  remarks jsonb
);

create table if not exists public.psychology_questions (
  question_id text primary key,
  question_text text not null,
  category text not null,
  question_type text not null
);

create table if not exists public.psychology_responses (
  answer_id text primary key,
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  question_id text not null references public.psychology_questions(question_id),
  answer_text text not null,
  answer_score integer,
  recorded_at timestamptz not null default now()
);

create table if not exists public.athlete_scores (
  score_id text primary key,
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  score_type text not null,
  score_value numeric not null,
  percentile numeric,
  category text not null,
  calculated_at timestamptz not null default now(),
  source_data jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.training_plans (
  training_plan_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  coach_id uuid references public.coaches(coach_id),
  focus_area text,
  recommended_drills text,
  session_frequency text,
  recovery_instructions text,
  mental_training_notes text,
  coach_recommendation text,
  status text not null default 'New',
  generated_from jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists public.athlete_insights (
  insight_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  session_id uuid references public.shooting_session_log(session_id) on delete set null,
  title text not null,
  insight_text text not null,
  category text not null,
  score numeric,
  priority text,
  suggested_action text,
  supporting_data jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.coach_feedback (
  feedback_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  athlete_name text,
  athlete_email text,
  coach_email text,
  coach_name text,
  coach_id uuid references public.coaches(coach_id),
  coach_uid text,
  note text,
  recommendation text,
  status text,
  technique_score numeric,
  focus_score numeric,
  breathing_score numeric,
  posture_score numeric,
  coach_observations text,
  coach_notes text,
  strengths text,
  training_plan text,
  exercise_plan text,
  improvement_areas text,
  created_at timestamptz not null default now()
);

create table if not exists public.coach_profiles (
  coach_id text primary key,
  name text not null,
  email text not null unique references public."App_Users"(email) on delete cascade,
  phone text,
  profile_image text,
  specialization text,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.coach_athlete_assignments (
  assignment_id text primary key,
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  coach_email text not null references public."App_Users"(email),
  assigned_by text not null references public."App_Users"(email),
  previous_coach_email text,
  status text not null default 'active',
  created_at timestamptz not null default now()
);

create table if not exists public.coach_assignments (
  assignment_id uuid primary key default gen_random_uuid(),
  coach_id uuid references public.coaches(coach_id),
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.assignment_requests (
  request_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  requesting_coach_id uuid references public.coaches(coach_id),
  assigned_coach_id uuid references public.coaches(coach_id),
  status text not null default 'PENDING',
  notes text,
  requested_at timestamptz not null default now(),
  assigned_at timestamptz
);

create table if not exists public.notifications (
  notification_id uuid primary key default gen_random_uuid(),
  recipient_coach_id uuid references public.coaches(coach_id),
  notification_type text,
  related_athlete_id text references public.athletes(athlete_id),
  related_session_id uuid,
  message text not null,
  is_read boolean not null default false,
  action_url text,
  recipient_email text,
  recipient_role text,
  title text,
  type text,
  entity_id text,
  read_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.feedback_requests (
  request_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references public.athletes(athlete_id) on delete cascade,
  session_id uuid not null,
  coach_id uuid not null references public.coaches(coach_id),
  status text not null default 'PENDING',
  requested_at timestamptz not null default now(),
  completed_at timestamptz,
  feedback_id uuid
);

create table if not exists public.audit_logs (
  audit_id text primary key,
  actor_email text not null,
  action text not null,
  entity_type text not null,
  entity_id text not null,
  metadata jsonb,
  created_at timestamptz not null default now()
);

insert into public.coaches (coach_name, coach_id_text, email, specialization)
values
  ('HamsaTech Coach', 'C001', 'coach@hamsatech.ai', 'Shooting performance'),
  ('HamsaTech Admin', 'C002', 'admin@hamsatech.ai', 'Assignment operations')
on conflict (coach_id_text) do update
set coach_name = excluded.coach_name,
    email = excluded.email,
    specialization = excluded.specialization,
    updated_at = now();

insert into public.coach_profiles (
  coach_id, name, email, specialization, status, created_at, updated_at
)
select
  c.coach_id::text,
  c.coach_name,
  c.email,
  c.specialization,
  coalesce(c.status, 'active'),
  now(),
  now()
from public.coaches c
join public."App_Users" u on lower(u.email) = lower(c.email)
where lower(c.email) in ('coach@hamsatech.ai', 'admin@hamsatech.ai')
on conflict (email) do update
set name = excluded.name,
    specialization = excluded.specialization,
    status = excluded.status,
    updated_at = now();

create index if not exists idx_athletes_coach_id on public.athletes(coach_id);
create index if not exists idx_sessions_athlete_date on public.shooting_session_log(athlete_id, session_date desc);
create index if not exists idx_physiology_athlete_date on public.athlete_physiology(athlete_id, recorded_date desc);
create index if not exists idx_athlete_scores_athlete_id on public.athlete_scores(athlete_id);
create index if not exists idx_athlete_scores_type_calc on public.athlete_scores(athlete_id, score_type, calculated_at desc);
create index if not exists idx_notifications_coach_unread on public.notifications(recipient_coach_id, is_read, created_at desc);
create index if not exists idx_feedback_requests_status on public.feedback_requests(coach_id, status, requested_at desc);
create index if not exists idx_assignment_requests_pending on public.assignment_requests(status, requested_at desc);
create index if not exists idx_assignment_requests_athlete_pending on public.assignment_requests(athlete_id) where status = 'PENDING';

select table_name
from information_schema.tables
where table_schema = 'public'
  and table_name in (
    'coaches', 'athletes', 'coach_profiles', 'assignment_requests',
    'notifications', 'shooting_session_log', 'athlete_scores'
  )
order by table_name;
