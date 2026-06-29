create extension if not exists pgcrypto;

-- 1️⃣ App Users (no dependencies)
create table if not exists public."App_Users" (
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

alter table public."App_Users" add column if not exists assignment_status text not null default 'unassigned';
alter table public."App_Users" add column if not exists requested_coach_email text;
alter table public."App_Users" add column if not exists requested_coach_name text;
alter table public."App_Users" add column if not exists requested_coach_code text;
alter table public."App_Users" add column if not exists coach_request_sent_at timestamptz;

update public."App_Users"
set assignment_status = case
  when assigned_coach_email is not null then 'assigned'
  when requested_coach_email is not null then 'pending'
  else 'unassigned'
end
where assignment_status is null or assignment_status = '';

-- 2️⃣ Athletes Master (parent table)
create table if not exists public."Athletes_Master" (
  athlete_id text primary key,
  name text not null,
  age integer not null,
  gender text not null check (gender in ('Male', 'Female', 'Other')),
  height_cm numeric not null,
  weight_kg numeric not null,
  academy_id text not null,
  coach_id text not null,
  contact_number text not null,
  email text not null,
  created_at timestamptz not null default now(),
  updated_by text
);

alter table public."Athletes_Master" add column if not exists registration_source text default 'website';
alter table public."Athletes_Master" add column if not exists onboarding_status text default 'registered';
alter table public."Athletes_Master" add column if not exists profile_completion_status text default 'partial';
alter table public."Athletes_Master" add column if not exists updated_at timestamptz not null default now();

-- 3️⃣ App Sessions (depends on App_Users)
create table if not exists public."App_Sessions" (
  session_token text primary key,
  user_email text not null references public."App_Users"(email) on delete cascade,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null
);

-- 4️⃣ Coach Feedback (depends on App_Users + Athletes_Master)
create table if not exists public."Coach_Feedback" (
  feedback_id text primary key,
  athlete_id text not null references public."Athletes_Master"(athlete_id) on delete cascade,
  athlete_name text not null,
  athlete_email text not null,
  coach_email text not null references public."App_Users"(email),
  coach_name text not null,
  note text not null,
  recommendation text not null,
  status text not null check (status in ('Needs Attention', 'Progressing', 'Strong')),
  created_at timestamptz not null default now()
);

create table if not exists public."Coach_Profiles" (
  coach_id text primary key,
  name text not null,
  email text not null unique references public."App_Users"(email) on delete cascade,
  phone text,
  profile_image text,
  specialization text,
  status text not null default 'active' check (status in ('active', 'inactive')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public."Coach_Athlete_Assignments" (
  assignment_id text primary key,
  athlete_id text not null references public."Athletes_Master"(athlete_id) on delete cascade,
  coach_email text not null references public."App_Users"(email),
  assigned_by text not null references public."App_Users"(email),
  previous_coach_email text,
  status text not null default 'active' check (status in ('active', 'inactive')),
  created_at timestamptz not null default now()
);

create table if not exists public."Athlete_Scores" (
  score_id text primary key,
  athlete_id text not null references public."Athletes_Master"(athlete_id) on delete cascade,
  score_type text not null,
  score_value numeric not null,
  percentile numeric,
  category text not null,
  calculated_at timestamptz not null default now(),
  source_data jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public."Notifications" (
  notification_id text primary key,
  recipient_email text not null,
  recipient_role text not null,
  title text not null,
  message text not null,
  type text not null,
  entity_id text,
  read_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public."Audit_Logs" (
  audit_id text primary key,
  actor_email text not null,
  action text not null,
  entity_type text not null,
  entity_id text not null,
  metadata jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_athletes_master_coach_id on public."Athletes_Master"(coach_id);
create index if not exists idx_athlete_scores_athlete_id on public."Athlete_Scores"(athlete_id);
create index if not exists idx_notifications_recipient_email on public."Notifications"(recipient_email);
create index if not exists idx_assignments_athlete_id on public."Coach_Athlete_Assignments"(athlete_id);

-- 5️⃣ Family Details (depends on Athletes_Master)
create table if not exists public."Family_Details" (
  family_id text primary key,
  athlete_id text not null references public."Athletes_Master"(athlete_id) on delete cascade,
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

-- 6️⃣ Athlete Profile (depends on Athletes_Master)
create table if not exists public."Athlete_Profile" (
  details_id text primary key,
  athlete_id text not null references public."Athletes_Master"(athlete_id) on delete cascade,
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

-- 7️⃣ Sessions Log (depends on Athletes_Master)
create table if not exists public."Sessions_Log" (
  session_id text primary key,
  athlete_id text not null references public."Athletes_Master"(athlete_id) on delete cascade,
  coach_id text not null,
  session_date date not null,
  start_time text not null,
  end_time text not null,
  duration_minutes integer not null,
  training_type text not null check (training_type in ('Shooting', 'Fitness', 'Mental', 'Recovery')),
  location text not null,
  notes text
);

-- 8️⃣ Physiology Data (depends on Athletes_Master + Sessions_Log)
create table if not exists public."Physiology_Data" (
  physiology_id text primary key,
  athlete_id text not null references public."Athletes_Master"(athlete_id) on delete cascade,
  session_id text not null references public."Sessions_Log"(session_id) on delete cascade,
  recorded_date date not null,
  resting_heart_rate integer not null check (resting_heart_rate between 40 and 200),
  avg_heart_rate integer not null check (avg_heart_rate between 40 and 200),
  spo2 integer not null check (spo2 between 80 and 100),
  breathing_rate integer,
  sleep_hours numeric not null check (sleep_hours between 0 and 12),
  recovery_score integer,
  stress_score integer,
  fatigue_level integer,
  remarks text
);

-- 9️⃣ Psychology Questions (independent)
create table if not exists public."Psychology_Questions" (
  question_id text primary key,
  question_text text not null,
  category text not null,
  question_type text not null
);

-- 🔟 Psychology Responses (depends on Athletes_Master + Psychology_Questions)
create table if not exists public."Psychology_Responses" (
  answer_id text primary key,
  athlete_id text not null references public."Athletes_Master"(athlete_id) on delete cascade,
  question_id text not null references public."Psychology_Questions"(question_id),
  answer_text text not null,
  answer_score integer check (answer_score between 1 and 10),
  recorded_at timestamptz not null default now()
);

-- 1️⃣1️⃣ Athlete Lookup (depends on Athletes_Master)
create table if not exists public."Athlete_Lookup" (
  athlete_id text primary key references public."Athletes_Master"(athlete_id) on delete cascade,
  name text not null
);

-- 1️⃣2️⃣ Seed Data
insert into public."Psychology_Questions" (question_id, question_text, category, question_type)
values
  ('Q1', 'How stressed do you feel?', 'Stress', 'Scale'),
  ('Q2', 'How focused were you today?', 'Focus', 'Scale'),
  ('Q3', 'What distracted you today?', 'Behavior', 'Text')
on conflict (question_id) do update
set
  question_text = excluded.question_text,
  category = excluded.category,
  question_type = excluded.question_type;
