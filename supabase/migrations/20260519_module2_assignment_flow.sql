create table if not exists hamsatech.assignment_requests (
  request_id uuid primary key default gen_random_uuid(),
  athlete_id text not null references hamsatech.athletes(athlete_id),
  requesting_coach_id uuid references hamsatech.coaches(coach_id),
  assigned_coach_id uuid references hamsatech.coaches(coach_id),
  status text not null default 'PENDING' check (status in ('PENDING', 'ASSIGNED', 'REJECTED')),
  notes text,
  requested_at timestamp with time zone default now(),
  assigned_at timestamp with time zone
);

create index if not exists idx_assignment_requests_pending
  on hamsatech.assignment_requests(status, requested_at desc);

create or replace function hamsatech.notify_default_coach_new_registration()
returns trigger
language plpgsql
as $$
declare
  v_default_coach_id uuid;
  v_athlete_name text;
begin
  select c.coach_id into v_default_coach_id
  from hamsatech.coaches c
  where upper(coalesce(c.coach_id_text, '')) = 'C001'
  order by c.created_at asc
  limit 1;

  if v_default_coach_id is null then
    select c.coach_id into v_default_coach_id
    from hamsatech.coaches c
    order by c.created_at asc
    limit 1;
  end if;

  if v_default_coach_id is null then
    return new;
  end if;

  select coalesce(a.athlete_name, a.name, 'Athlete')
    into v_athlete_name
  from hamsatech.athletes a
  where a.athlete_id = new.athlete_id
  limit 1;

  insert into hamsatech.assignment_requests (
    athlete_id,
    assigned_coach_id,
    status,
    notes
  ) values (
    new.athlete_id,
    v_default_coach_id,
    'PENDING',
    'Auto-created on athlete profile registration'
  )
  on conflict do nothing;

  insert into hamsatech.notifications (
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
    'NEW_USER_REGISTRATION',
    new.athlete_id,
    coalesce(v_athlete_name, 'Athlete') || ' registered and needs coach assignment.',
    '/coach/assignments/pending',
    'New athlete registration',
    'new_user_registration',
    new.athlete_id
  );

  return new;
end;
$$;

drop trigger if exists trigger_new_user_assignment_request on hamsatech.athlete_details;
create trigger trigger_new_user_assignment_request
after insert on hamsatech.athlete_details
for each row
execute function hamsatech.notify_default_coach_new_registration();
