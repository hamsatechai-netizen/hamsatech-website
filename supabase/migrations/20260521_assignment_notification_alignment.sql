create index if not exists idx_assignment_requests_athlete_pending
  on public.assignment_requests(athlete_id)
  where status = 'PENDING';

alter table public.notifications add column if not exists recipient_email text;
alter table public.notifications add column if not exists recipient_role text;
alter table public.notifications add column if not exists title text;
alter table public.notifications add column if not exists type text;
alter table public.notifications add column if not exists entity_id text;
alter table public.notifications add column if not exists read_at timestamp with time zone;

create or replace function public.notify_default_coach_new_registration()
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
  from public.assignment_requests ar
  where ar.athlete_id = new.athlete_id
    and ar.status = 'PENDING'
  order by ar.requested_at desc
  limit 1;

  if v_existing_request_id is not null then
    return new;
  end if;

  select c.coach_id into v_default_coach_id
  from public.coaches c
  where upper(coalesce(c.coach_id_text, '')) = 'C001'
  order by c.created_at asc
  limit 1;

  if v_default_coach_id is null then
    select c.coach_id into v_default_coach_id
    from public.coaches c
    order by c.created_at asc
    limit 1;
  end if;

  if v_default_coach_id is null then
    return new;
  end if;

  select coalesce(a.athlete_name, a.name, 'Athlete')
    into v_athlete_name
  from public.athletes a
  where a.athlete_id = new.athlete_id
  limit 1;

  insert into public.assignment_requests (
    athlete_id,
    assigned_coach_id,
    status,
    notes
  ) values (
    new.athlete_id,
    v_default_coach_id,
    'PENDING',
    'Fallback auto-created on athlete profile registration'
  )
  returning request_id into v_request_id;

  insert into public.notifications (
    recipient_coach_id,
    notification_type,
    related_athlete_id,
    message,
    action_url,
    title,
    type,
    entity_id
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
