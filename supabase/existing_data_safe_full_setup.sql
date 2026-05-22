-- HamsaTech existing-data-safe full setup.
-- Run this in Supabase SQL Editor.
-- This script is intentionally non-destructive:
-- - no drop table
-- - no truncate
-- - no delete
-- - create table/index/schema only if missing
-- - add columns only if missing
-- - replace triggers only, without touching table data

create extension if not exists pgcrypto;
create schema if not exists hamsatech;

create table if not exists hamsatech."App_Users" (
  email text primary key,
  full_name text not null,
  role text not null check (role in ('coach', 'student')),
  salt text not null,
  password_hash text not null,
  coach_code text unique,
  assignment_status text not null default 'unassigned',
  assigned_coach_email text,
  assigned_coach_name text,
  requested_coach_email text,
  requested_coach_name text,
  requested_coach_code text,
  coach_request_sent_at timestamptz,
  sport text,
  focus_area text,
  date_of_birth date,
  performance_score integer,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table hamsatech."App_Users" add column if not exists assignment_status text not null default 'unassigned';
alter table hamsatech."App_Users" add column if not exists assigned_coach_email text;
alter table hamsatech."App_Users" add column if not exists assigned_coach_name text;
alter table hamsatech."App_Users" add column if not exists requested_coach_email text;
alter table hamsatech."App_Users" add column if not exists requested_coach_name text;
alter table hamsatech."App_Users" add column if not exists requested_coach_code text;
alter table hamsatech."App_Users" add column if not exists coach_request_sent_at timestamptz;
alter table hamsatech."App_Users" add column if not exists sport text;
alter table hamsatech."App_Users" add column if not exists focus_area text;
alter table hamsatech."App_Users" add column if not exists date_of_birth date;
alter table hamsatech."App_Users" add column if not exists performance_score integer;
alter table hamsatech."App_Users" add column if not exists updated_at timestamptz not null default now();

create table if not exists hamsatech."App_Sessions" (
  session_token text primary key,
  user_email text not null references hamsatech."App_Users"(email) on delete cascade,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null
);

create table if not exists hamsatech.coaches (
  coach_id uuid primary key default gen_random_uuid(),
  coach_name text not null,
  coach_id_text text unique,
  email text unique,
  specialization text,
  status text not null default 'active' check (status in ('active', 'inactive')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table hamsatech.coaches add column if not exists coach_id_text text;
alter table hamsatech.coaches add column if not exists email text;
alter table hamsatech.coaches add column if not exists specialization text;
alter table hamsatech.coaches add column if not exists status text not null default 'active';
alter table hamsatech.coaches add column if not exists updated_at timestamptz not null default now();

create table if not exists hamsatech.athletes (
  athlete_id text primary key,
  athlete_name text,
  name text not null,
  age integer,
  gender text check (gender in ('Male', 'Female', 'Other')),
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

alter table hamsatech.athletes add column if not exists athlete_name text;
alter table hamsatech.athletes add column if not exists name text;
alter table hamsatech.athletes add column if not exists age integer;
alter table hamsatech.athletes add column if not exists gender text;
alter table hamsatech.athletes add column if not exists height_cm numeric;
alter table hamsatech.athletes add column if not exists weight_kg numeric;
alter table hamsatech.athletes add column if not exists academy_id text;
alter table hamsatech.athletes add column if not exists coach_id text not null default '';
alter table hamsatech.athletes add column if not exists contact_number text;
alter table hamsatech.athletes add column if not exists email text;
alter table hamsatech.athletes add column if not exists registration_source text default 'website';
alter table hamsatech.athletes add column if not exists onboarding_status text default 'registered';
alter table hamsatech.athletes add column if not exists profile_completion_status text default 'partial';
alter table hamsatech.athletes add column if not exists updated_at timestamptz not null default now();
alter table hamsatech.athletes add column if not exists updated_by text;

create table if not exists hamsatech.athlete_family (
  family_id text primary key,
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  mother_name text,
  father_name text,
  mother_occupation text,
  father_occupation text,
  education_level text,
  sibling_details text,
  family_conservative text check (family_conservative in ('Yes', 'No')),
  discipline_level text,
  health_conditions text,
  father_contact_number text,
  mother_contact_number text,
  parent_email text,
  comments text
);

create table if not exists hamsatech.athlete_details (
  details_id text primary key,
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  class text,
  school_name text,
  diet_type text check (diet_type in ('Veg', 'Non-Veg', 'Mixed')),
  outside_food_frequency text check (outside_food_frequency in ('Rare', 'Weekly', 'Frequent')),
  sleep_time text,
  wake_time text,
  friend_circle text,
  anger_pattern text,
  sadness_pattern text,
  academic_performance text,
  reason_for_shooting text,
  athlete_goal text
);

create table if not exists hamsatech.shooting_session_log (
  session_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  coach_id text not null default '',
  session_date date not null,
  start_time text not null,
  end_time text not null,
  duration_minutes integer not null default 0,
  training_type text not null check (training_type in ('Shooting', 'Fitness', 'Mental', 'Recovery')),
  location text not null,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table hamsatech.shooting_session_log add column if not exists created_at timestamptz not null default now();
alter table hamsatech.shooting_session_log add column if not exists updated_at timestamptz not null default now();
alter table hamsatech.shooting_session_log add column if not exists session_type text;
alter table hamsatech.shooting_session_log add column if not exists coach_notes text;
alter table hamsatech.shooting_session_log add column if not exists athlete_notes text;
alter table hamsatech.shooting_session_log add column if not exists planned_shots integer;
alter table hamsatech.shooting_session_log add column if not exists completed_shots integer;
alter table hamsatech.shooting_session_log add column if not exists missed_session boolean not null default false;
alter table hamsatech.shooting_session_log add column if not exists reflection_submitted boolean not null default false;

create table if not exists hamsatech.athlete_physiology (
  physiology_id text primary key,
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  session_id uuid references hamsatech.shooting_session_log(session_id) on delete cascade,
  recorded_date date not null,
  resting_heart_rate integer,
  avg_heart_rate integer,
  spo2 integer,
  breathing_rate integer,
  sleep_hours numeric,
  recovery_score integer,
  stress_score integer,
  fatigue_level integer,
  remarks text
);

alter table hamsatech.athlete_physiology add column if not exists min_heart_rate integer;
alter table hamsatech.athlete_physiology add column if not exists max_heart_rate integer;
alter table hamsatech.athlete_physiology add column if not exists rmssd numeric;
alter table hamsatech.athlete_physiology add column if not exists hrv_ms numeric;
alter table hamsatech.athlete_physiology add column if not exists hr_std_dev numeric;
alter table hamsatech.athlete_physiology add column if not exists zone_1_time integer not null default 0;
alter table hamsatech.athlete_physiology add column if not exists zone_2_time integer not null default 0;
alter table hamsatech.athlete_physiology add column if not exists zone_3_time integer not null default 0;
alter table hamsatech.athlete_physiology add column if not exists zone_4_time integer not null default 0;
alter table hamsatech.athlete_physiology add column if not exists zone_5_time integer not null default 0;
alter table hamsatech.athlete_physiology add column if not exists stability_score numeric;
alter table hamsatech.athlete_physiology add column if not exists acc_hold_stability numeric;
alter table hamsatech.athlete_physiology add column if not exists acc_settle_score numeric;
alter table hamsatech.athlete_physiology add column if not exists acc_spike_count integer;

create table if not exists hamsatech.psychology_questions (
  question_id text primary key,
  question_text text not null,
  category text not null,
  question_type text not null
);

create table if not exists hamsatech.psychology_responses (
  answer_id text primary key,
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  question_id text not null references hamsatech.psychology_questions(question_id),
  answer_text text not null,
  answer_score integer,
  recorded_at timestamptz not null default now()
);

create table if not exists hamsatech.athlete_scores (
  score_id text primary key,
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  score_type text not null,
  score_value numeric not null,
  percentile numeric,
  category text not null,
  calculated_at timestamptz not null default now(),
  source_data jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists hamsatech.training_plans (
  training_plan_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  coach_id uuid references hamsatech.coaches(coach_id),
  focus_area text,
  recommended_drills text,
  session_frequency text,
  recovery_instructions text,
  mental_training_notes text,
  coach_recommendation text,
  status text not null default 'New' check (status in ('New', 'In Progress', 'Completed', 'Needs Review')),
  generated_from jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists hamsatech.athlete_insights (
  insight_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  session_id uuid references hamsatech.shooting_session_log(session_id) on delete set null,
  title text not null,
  insight_text text not null,
  category text not null,
  score numeric,
  priority text not null default 'Medium' check (priority in ('High', 'Medium', 'Low')),
  suggested_action text,
  supporting_data jsonb,
  created_at timestamptz not null default now()
);

create table if not exists hamsatech.coach_feedback (
  feedback_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  athlete_name text,
  athlete_email text,
  coach_email text,
  coach_name text,
  coach_id uuid references hamsatech.coaches(coach_id),
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

alter table hamsatech.coach_feedback add column if not exists athlete_name text;
alter table hamsatech.coach_feedback add column if not exists athlete_email text;
alter table hamsatech.coach_feedback add column if not exists coach_email text;
alter table hamsatech.coach_feedback add column if not exists coach_name text;
alter table hamsatech.coach_feedback add column if not exists coach_id uuid;
alter table hamsatech.coach_feedback add column if not exists coach_uid text;
alter table hamsatech.coach_feedback add column if not exists note text;
alter table hamsatech.coach_feedback add column if not exists recommendation text;
alter table hamsatech.coach_feedback add column if not exists status text;
alter table hamsatech.coach_feedback add column if not exists technique_score numeric;
alter table hamsatech.coach_feedback add column if not exists focus_score numeric;
alter table hamsatech.coach_feedback add column if not exists breathing_score numeric;
alter table hamsatech.coach_feedback add column if not exists posture_score numeric;
alter table hamsatech.coach_feedback add column if not exists coach_observations text;
alter table hamsatech.coach_feedback add column if not exists coach_notes text;
alter table hamsatech.coach_feedback add column if not exists strengths text;
alter table hamsatech.coach_feedback add column if not exists training_plan text;
alter table hamsatech.coach_feedback add column if not exists exercise_plan text;
alter table hamsatech.coach_feedback add column if not exists improvement_areas text;

create table if not exists hamsatech.coach_profiles (
  coach_id text primary key,
  name text not null,
  email text not null unique references hamsatech."App_Users"(email) on delete cascade,
  phone text,
  profile_image text,
  specialization text,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists hamsatech.coach_athlete_assignments (
  assignment_id text primary key,
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  coach_email text not null references hamsatech."App_Users"(email),
  assigned_by text not null references hamsatech."App_Users"(email),
  previous_coach_email text,
  status text not null default 'active',
  created_at timestamptz not null default now()
);

create table if not exists hamsatech.coach_assignments (
  assignment_id uuid primary key default gen_random_uuid(),
  coach_id uuid references hamsatech.coaches(coach_id),
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists hamsatech.assignment_requests (
  request_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  requesting_coach_id uuid references hamsatech.coaches(coach_id),
  assigned_coach_id uuid references hamsatech.coaches(coach_id),
  status text not null default 'PENDING',
  notes text,
  requested_at timestamptz not null default now(),
  assigned_at timestamptz
);

create table if not exists hamsatech.notifications (
  notification_id uuid primary key default gen_random_uuid(),
  recipient_coach_id uuid references hamsatech.coaches(coach_id),
  notification_type text,
  related_athlete_id text references hamsatech.athletes(athlete_id),
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

alter table hamsatech.notifications add column if not exists recipient_coach_id uuid;
alter table hamsatech.notifications add column if not exists notification_type text;
alter table hamsatech.notifications add column if not exists related_athlete_id text;
alter table hamsatech.notifications add column if not exists related_session_id uuid;
alter table hamsatech.notifications add column if not exists is_read boolean not null default false;
alter table hamsatech.notifications add column if not exists action_url text;
alter table hamsatech.notifications add column if not exists recipient_email text;
alter table hamsatech.notifications add column if not exists recipient_role text;
alter table hamsatech.notifications add column if not exists title text;
alter table hamsatech.notifications add column if not exists type text;
alter table hamsatech.notifications add column if not exists entity_id text;
alter table hamsatech.notifications add column if not exists read_at timestamptz;

create table if not exists hamsatech.feedback_requests (
  request_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references hamsatech.athletes(athlete_id) on delete cascade,
  session_id uuid not null,
  coach_id uuid not null references hamsatech.coaches(coach_id),
  status text not null default 'PENDING',
  requested_at timestamptz not null default now(),
  completed_at timestamptz,
  feedback_id uuid
);

alter table hamsatech.feedback_requests add column if not exists completed_at timestamptz;
alter table hamsatech.feedback_requests add column if not exists feedback_id uuid;

create table if not exists hamsatech.audit_logs (
  audit_id text primary key,
  actor_email text not null,
  action text not null,
  entity_type text not null,
  entity_id text not null,
  metadata jsonb,
  created_at timestamptz not null default now()
);

create table if not exists hamsatech."Athlete_Lookup" (
  athlete_id text primary key references hamsatech.athletes(athlete_id) on delete cascade,
  name text not null
);

create index if not exists idx_app_sessions_user_email on hamsatech."App_Sessions"(user_email);
create index if not exists idx_athletes_coach_id on hamsatech.athletes(coach_id);
create index if not exists idx_sessions_athlete_date on hamsatech.shooting_session_log(athlete_id, session_date desc);
create index if not exists idx_physiology_athlete_date on hamsatech.athlete_physiology(athlete_id, recorded_date desc);
create index if not exists idx_athlete_scores_athlete_id on hamsatech.athlete_scores(athlete_id);
create index if not exists idx_athlete_scores_type_calc on hamsatech.athlete_scores(athlete_id, score_type, calculated_at desc);
create index if not exists idx_psychology_responses_athlete_recorded on hamsatech.psychology_responses(athlete_id, recorded_at desc);
create index if not exists idx_training_plans_athlete_status on hamsatech.training_plans(athlete_id, status, updated_at desc);
create index if not exists idx_athlete_insights_athlete_created on hamsatech.athlete_insights(athlete_id, created_at desc);
create index if not exists idx_athlete_insights_category_created on hamsatech.athlete_insights(category, created_at desc);
create index if not exists idx_notifications_email on hamsatech.notifications(recipient_email);
create index if not exists idx_notifications_coach_unread on hamsatech.notifications(recipient_coach_id, is_read, created_at desc);
create index if not exists idx_feedback_requests_status on hamsatech.feedback_requests(coach_id, status, requested_at desc);
create index if not exists idx_assignment_requests_pending on hamsatech.assignment_requests(status, requested_at desc);
create index if not exists idx_assignment_requests_athlete_pending on hamsatech.assignment_requests(athlete_id) where status = 'PENDING';

-- Security posture for hosted Supabase:
-- The web app talks to the Render FastAPI backend, and the backend uses the
-- Supabase service role. Enabling RLS blocks direct anon/authenticated table
-- access unless explicit policies are added later.
alter table hamsatech."App_Users" enable row level security;
alter table hamsatech."App_Sessions" enable row level security;
alter table hamsatech.coaches enable row level security;
alter table hamsatech.athletes enable row level security;
alter table hamsatech.athlete_family enable row level security;
alter table hamsatech.athlete_details enable row level security;
alter table hamsatech.shooting_session_log enable row level security;
alter table hamsatech.athlete_physiology enable row level security;
alter table hamsatech.psychology_questions enable row level security;
alter table hamsatech.psychology_responses enable row level security;
alter table hamsatech.athlete_scores enable row level security;
alter table hamsatech.training_plans enable row level security;
alter table hamsatech.athlete_insights enable row level security;
alter table hamsatech.coach_feedback enable row level security;
alter table hamsatech.coach_profiles enable row level security;
alter table hamsatech.coach_athlete_assignments enable row level security;
alter table hamsatech.coach_assignments enable row level security;
alter table hamsatech.assignment_requests enable row level security;
alter table hamsatech.notifications enable row level security;
alter table hamsatech.feedback_requests enable row level security;
alter table hamsatech.audit_logs enable row level security;
alter table hamsatech."Athlete_Lookup" enable row level security;

create or replace view hamsatech.athlete_physiology_metrics as
select
  p.physiology_id,
  p.athlete_id,
  p.session_id,
  p.recorded_date,
  p.resting_heart_rate as resting_hr,
  p.avg_heart_rate as avg_hr,
  p.min_heart_rate as min_hr,
  p.max_heart_rate as max_hr,
  coalesce(p.rmssd, p.hrv_ms) as rmssd,
  p.hr_std_dev,
  p.zone_1_time,
  p.zone_2_time,
  p.zone_3_time,
  p.zone_4_time,
  p.zone_5_time,
  p.sleep_hours,
  p.recovery_score,
  p.stress_score,
  least(100, greatest(0, coalesce(p.fatigue_level, 0) * 10))::numeric as fatigue_score,
  round(
    (
      coalesce(p.recovery_score, 50)::numeric
      + (100 - coalesce(p.stress_score, 50))::numeric
      + (100 - least(100, greatest(0, coalesce(p.fatigue_level, 5) * 10)))::numeric
    ) / 3,
    2
  ) as readiness_score,
  p.stability_score,
  p.acc_hold_stability,
  p.acc_settle_score,
  p.acc_spike_count,
  p.remarks
from hamsatech.athlete_physiology p;

create or replace view hamsatech.athlete_psychology_scores as
select
  md5(r.athlete_id || ':' || lower(coalesce(q.category, r.question_id))) as psychology_score_id,
  r.athlete_id,
  lower(coalesce(q.category, r.question_id)) as category,
  round(avg(r.answer_score)::numeric, 2) as score,
  case
    when avg(r.answer_score) >= 8 then 'Strong'
    when avg(r.answer_score) >= 6 then 'Good'
    when avg(r.answer_score) >= 4 then 'Moderate'
    else 'Low'
  end as interpretation,
  jsonb_agg(
    jsonb_build_object(
      'questionId', r.question_id,
      'questionText', q.question_text,
      'answerText', r.answer_text,
      'answerScore', r.answer_score,
      'recordedAt', r.recorded_at
    )
    order by r.recorded_at desc
  ) as input_summary,
  max(r.recorded_at) as calculated_at
from hamsatech.psychology_responses r
left join hamsatech.psychology_questions q on q.question_id = r.question_id
where r.answer_score is not null
group by r.athlete_id, lower(coalesce(q.category, r.question_id));

create or replace view hamsatech.athlete_session_summary as
with session_series as (
  select
    s.session_id,
    s.athlete_id,
    avg(sc.score_value)::numeric as average_series_score,
    max(sc.score_value)::numeric as best_series_score,
    stddev_pop(sc.score_value)::numeric as series_stddev,
    count(sc.score_id) as series_count
  from hamsatech.shooting_session_log s
  left join hamsatech.athlete_scores sc
    on sc.athlete_id = s.athlete_id
   and sc.score_type = 'mobile_series'
   and sc.source_data ->> 'sessionId' = s.session_id::text
  group by s.session_id, s.athlete_id
),
recent_sessions as (
  select
    s.athlete_id,
    count(*) filter (where s.session_date >= current_date - interval '7 days') as sessions_7d,
    count(*) filter (where s.session_date >= current_date - interval '30 days') as sessions_30d
  from hamsatech.shooting_session_log s
  group by s.athlete_id
)
select
  s.session_id,
  s.athlete_id,
  s.coach_id,
  s.session_date,
  s.training_type,
  s.location,
  coalesce(ss.average_series_score, latest_overall.score_value, 0)::numeric as performance_score,
  coalesce(ss.best_series_score, best_series.score_value)::numeric as best_series_score,
  coalesce(pm.readiness_score, latest_readiness.score_value)::numeric as readiness_score,
  coalesce(pm.fatigue_score, 100 - latest_fatigue.score_value)::numeric as fatigue_score,
  coalesce(pm.stress_score, latest_stress.score_value)::numeric as stress_score,
  coalesce(pm.recovery_score, latest_recovery.score_value)::numeric as recovery_score,
  pm.avg_hr,
  pm.min_hr,
  pm.max_hr,
  pm.rmssd,
  coalesce(100 - least(100, coalesce(ss.series_stddev, 0) * 10), latest_consistency.score_value, 50)::numeric as consistency_index,
  coalesce(pm.stability_score, latest_stability.score_value)::numeric as stability_index,
  least(100, coalesce(rs.sessions_30d, 0) * 8)::numeric as training_adherence_score,
  coalesce(rs.sessions_7d, 0) as sessions_7d,
  coalesce(rs.sessions_30d, 0) as sessions_30d,
  tp.focus_area as next_training_focus,
  tp.coach_recommendation as recommendations,
  jsonb_build_object(
    'notes', s.notes,
    'coachNotes', s.coach_notes,
    'athleteNotes', s.athlete_notes,
    'reflectionSubmitted', s.reflection_submitted,
    'seriesCount', ss.series_count
  ) as detailed_analysis,
  s.created_at,
  s.updated_at
from hamsatech.shooting_session_log s
left join session_series ss on ss.session_id = s.session_id
left join hamsatech.athlete_physiology_metrics pm on pm.session_id = s.session_id
left join recent_sessions rs on rs.athlete_id = s.athlete_id
left join lateral (
  select score_value from hamsatech.athlete_scores
  where athlete_id = s.athlete_id and score_type in ('overall', 'performance')
  order by calculated_at desc limit 1
) latest_overall on true
left join lateral (
  select score_value from hamsatech.athlete_scores
  where athlete_id = s.athlete_id and score_type = 'readiness'
  order by calculated_at desc limit 1
) latest_readiness on true
left join lateral (
  select score_value from hamsatech.athlete_scores
  where athlete_id = s.athlete_id and score_type = 'fatigue'
  order by calculated_at desc limit 1
) latest_fatigue on true
left join lateral (
  select score_value from hamsatech.athlete_scores
  where athlete_id = s.athlete_id and score_type = 'stress'
  order by calculated_at desc limit 1
) latest_stress on true
left join lateral (
  select score_value from hamsatech.athlete_scores
  where athlete_id = s.athlete_id and score_type = 'recovery'
  order by calculated_at desc limit 1
) latest_recovery on true
left join lateral (
  select score_value from hamsatech.athlete_scores
  where athlete_id = s.athlete_id and score_type in ('consistency', 'discipline')
  order by calculated_at desc limit 1
) latest_consistency on true
left join lateral (
  select score_value from hamsatech.athlete_scores
  where athlete_id = s.athlete_id and score_type in ('hold_stability', 'stability')
  order by calculated_at desc limit 1
) latest_stability on true
left join lateral (
  select score_value from hamsatech.athlete_scores
  where athlete_id = s.athlete_id and score_type = 'best_series'
  order by calculated_at desc limit 1
) best_series on true
left join lateral (
  select focus_area, coach_recommendation
  from hamsatech.training_plans
  where athlete_id = s.athlete_id and status in ('New', 'In Progress', 'Needs Review')
  order by updated_at desc limit 1
) tp on true;

insert into hamsatech.psychology_questions (question_id, question_text, category, question_type)
values
  ('Q1', 'How stressed do you feel?', 'Stress', 'Scale'),
  ('Q2', 'How focused were you today?', 'Focus', 'Scale'),
  ('Q3', 'What distracted you today?', 'Behavior', 'Text'),
  ('MOBILE_DAILY_CHECKIN', 'Mobile daily athlete check-in', 'Mobile', 'Json'),
  ('MOBILE_SESSION_REFLECTION', 'Mobile training session reflection', 'Mobile', 'Json')
on conflict (question_id) do nothing;

insert into hamsatech.coaches (coach_name, coach_id_text, email, specialization)
values
  ('HamsaTech Coach', 'C001', 'coach@hamsatech.ai', 'Shooting performance'),
  ('HamsaTech Admin', 'C002', 'admin@hamsatech.ai', 'Assignment operations')
on conflict (coach_id_text) do nothing;

create or replace function hamsatech.notify_coach_feedback_request()
returns trigger
language plpgsql
as $$
declare
  v_athlete_name text;
begin
  select coalesce(a.athlete_name, a.name, 'Athlete')
    into v_athlete_name
  from hamsatech.athletes a
  where a.athlete_id = new.athlete_id
  limit 1;

  insert into hamsatech.notifications (
    recipient_coach_id, notification_type, related_athlete_id, related_session_id,
    message, action_url, title, type, entity_id
  ) values (
    new.coach_id,
    'FEEDBACK_REQUEST',
    new.athlete_id,
    new.session_id,
    coalesce(v_athlete_name, 'Athlete') || ' has requested feedback.',
    '/coach/feedback/new?athlete_id=' || new.athlete_id || '&session_id=' || new.session_id || '&request_id=' || new.request_id,
    'Feedback request',
    'feedback_request',
    new.athlete_id
  );

  return new;
end;
$$;

drop trigger if exists trigger_feedback_request_notification on hamsatech.feedback_requests;
create trigger trigger_feedback_request_notification
after insert on hamsatech.feedback_requests
for each row
execute function hamsatech.notify_coach_feedback_request();

create or replace function hamsatech.notify_default_coach_new_registration()
returns trigger
language plpgsql
as $$
declare
  v_default_coach_id uuid;
  v_athlete_name text;
  v_existing_request_id uuid;
  v_request_id uuid;
begin
  select ar.request_id into v_existing_request_id
  from hamsatech.assignment_requests ar
  where ar.athlete_id = new.athlete_id
    and ar.status = 'PENDING'
  order by ar.requested_at desc
  limit 1;

  if v_existing_request_id is not null then
    return new;
  end if;

  select c.coach_id into v_default_coach_id
  from hamsatech.coaches c
  where upper(coalesce(c.coach_id_text, '')) = 'C001'
  order by c.created_at asc
  limit 1;

  if v_default_coach_id is null then
    return new;
  end if;

  select coalesce(a.athlete_name, a.name, 'Athlete')
    into v_athlete_name
  from hamsatech.athletes a
  where a.athlete_id = new.athlete_id
  limit 1;

  insert into hamsatech.assignment_requests (athlete_id, assigned_coach_id, status, notes)
  values (new.athlete_id, v_default_coach_id, 'PENDING', 'Fallback auto-created on athlete profile registration')
  returning request_id into v_request_id;

  insert into hamsatech.notifications (
    recipient_coach_id, notification_type, related_athlete_id,
    message, action_url, title, type, entity_id
  ) values (
    v_default_coach_id,
    'ASSIGNMENT_REQUEST',
    new.athlete_id,
    coalesce(v_athlete_name, 'Athlete') || ' registered and needs coach assignment.',
    '/coach/assignments/pending',
    'New athlete assignment request',
    'ASSIGNMENT_REQUEST',
    v_request_id::text
  );

  return new;
end;
$$;

drop trigger if exists trigger_new_user_assignment_request on hamsatech.athlete_details;
create trigger trigger_new_user_assignment_request
after insert on hamsatech.athlete_details
for each row
execute function hamsatech.notify_default_coach_new_registration();

-- Optional verification:
-- select table_name from information_schema.tables where table_schema = 'hamsatech' order by table_name;
-- select coach_id_text, coach_name, email from hamsatech.coaches order by coach_id_text;
