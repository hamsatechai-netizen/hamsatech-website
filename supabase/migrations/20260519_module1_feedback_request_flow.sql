create extension if not exists pgcrypto;

create table if not exists public.notifications (
  notification_id uuid primary key default gen_random_uuid(),
  recipient_coach_id uuid references public.coaches(coach_id),
  notification_type text,
  related_athlete_id text references public.athletes(athlete_id),
  related_session_id uuid,
  message text not null,
  is_read boolean default false,
  action_url text,
  created_at timestamp with time zone default now(),
  read_at timestamp with time zone,
  recipient_email text,
  recipient_role text,
  title text,
  type text,
  entity_id text
);

create table if not exists public.feedback_requests (
  request_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references public.athletes(athlete_id),
  session_id uuid not null,
  coach_id uuid not null references public.coaches(coach_id),
  status text not null default 'PENDING' check (status in ('PENDING', 'COMPLETED', 'DISMISSED')),
  requested_at timestamp with time zone default now(),
  completed_at timestamp with time zone,
  feedback_id uuid references public.coach_feedback(feedback_id)
);

create index if not exists idx_notifications_coach_unread
  on public.notifications(recipient_coach_id, is_read, created_at desc);

create index if not exists idx_feedback_requests_status
  on public.feedback_requests(coach_id, status, requested_at desc);

create or replace function public.notify_coach_feedback_request()
returns trigger
language plpgsql
as $$
declare
  v_athlete_name text;
begin
  select coalesce(a.athlete_name, a.name, 'Athlete')
    into v_athlete_name
  from public.athletes a
  where a.athlete_id = new.athlete_id
  limit 1;

  insert into public.notifications (
    recipient_coach_id,
    notification_type,
    related_athlete_id,
    related_session_id,
    message,
    action_url,
    title,
    type,
    entity_id
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

drop trigger if exists trigger_feedback_request_notification on public.feedback_requests;
create trigger trigger_feedback_request_notification
after insert on public.feedback_requests
for each row
execute function public.notify_coach_feedback_request();
