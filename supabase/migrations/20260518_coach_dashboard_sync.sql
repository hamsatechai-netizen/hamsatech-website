alter table public."Athletes" add column if not exists registration_source text default 'website';
alter table public."Athletes" add column if not exists onboarding_status text default 'registered';
alter table public."Athletes" add column if not exists profile_completion_status text default 'partial';
alter table public."Athletes" add column if not exists updated_at timestamptz not null default now();

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
  athlete_id text not null references public."Athletes"(athlete_id) on delete cascade,
  coach_email text not null references public."App_Users"(email),
  assigned_by text not null references public."App_Users"(email),
  previous_coach_email text,
  status text not null default 'active' check (status in ('active', 'inactive')),
  created_at timestamptz not null default now()
);

create table if not exists public."Athlete_Scores" (
  score_id text primary key,
  athlete_id text not null references public."Athletes"(athlete_id) on delete cascade,
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

create index if not exists idx_athletes_coach_id on public."Athletes"(coach_id);
create index if not exists idx_athlete_scores_athlete_id on public."Athlete_Scores"(athlete_id);
create index if not exists idx_notifications_recipient_email on public."Notifications"(recipient_email);
create index if not exists idx_assignments_athlete_id on public."Coach_Athlete_Assignments"(athlete_id);
