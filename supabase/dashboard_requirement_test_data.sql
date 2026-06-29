-- HamsaTech coach dashboard test data.
-- Run this after existing_data_safe_full_setup.sql in Supabase SQL Editor.
-- Safe to rerun: deterministic IDs are upserted, not duplicated.

insert into public.coaches (coach_name, coach_id_text, email, specialization)
values ('HamsaTech Coach', 'C001', 'coach@hamsatech.ai', 'Shooting performance')
on conflict (coach_id_text) do update
set coach_name = excluded.coach_name,
    email = excluded.email,
    specialization = excluded.specialization,
    updated_at = now();

with c001 as (
  select coach_id::text as coach_id
  from public.coaches
  where upper(coach_id_text) = 'C001'
  limit 1
)
insert into public.athletes (
  athlete_id, athlete_name, name, age, gender, academy_id, coach_id,
  contact_number, email, registration_source, onboarding_status,
  profile_completion_status, created_at, updated_at
)
select *
from (
  values
    ('TEST-ATH-001', 'Anaya Rao', 'Anaya Rao', 16, 'Female', '10m Air Rifle', (select coach_id from c001), '9000000001', 'anaya.test@hamsatech.ai', 'dashboard-test', 'ready_to_train', 'complete', now() - interval '3 days', now()),
    ('TEST-ATH-002', 'Kabir Mehta', 'Kabir Mehta', 17, 'Male', '10m Air Pistol', (select coach_id from c001), '9000000002', 'kabir.test@hamsatech.ai', 'dashboard-test', 'ready_to_train', 'complete', now() - interval '10 days', now()),
    ('TEST-ATH-003', 'Mira Sen', 'Mira Sen', 15, 'Female', '10m Air Rifle', (select coach_id from c001), '9000000003', 'mira.test@hamsatech.ai', 'dashboard-test', 'ready_to_train', 'complete', now() - interval '1 day', now()),
    ('TEST-ATH-004', 'Dev Iyer', 'Dev Iyer', 18, 'Male', '50m Rifle', (select coach_id from c001), '9000000004', 'dev.test@hamsatech.ai', 'dashboard-test', 'ready_to_train', 'partial', now() - interval '45 days', now())
) as seed(athlete_id, athlete_name, name, age, gender, academy_id, coach_id, contact_number, email, registration_source, onboarding_status, profile_completion_status, created_at, updated_at)
on conflict (athlete_id) do update
set athlete_name = excluded.athlete_name,
    name = excluded.name,
    age = excluded.age,
    gender = excluded.gender,
    academy_id = excluded.academy_id,
    coach_id = excluded.coach_id,
    contact_number = excluded.contact_number,
    email = excluded.email,
    registration_source = excluded.registration_source,
    onboarding_status = excluded.onboarding_status,
    profile_completion_status = excluded.profile_completion_status,
    updated_at = now();

insert into public.shooting_session_log (
  session_id, athlete_id, coach_id, session_date, start_time, end_time,
  duration_minutes, training_type, location, notes, coach_notes,
  athlete_notes, planned_shots, completed_shots, reflection_submitted,
  created_at, updated_at
)
values
  ('11111111-1111-4111-8111-111111111111', 'TEST-ATH-001', (select coach_id::text from public.coaches where upper(coach_id_text) = 'C001' limit 1), current_date - 1, '06:00', '07:10', 70, 'Shooting', 'Range A', '{"plannedShots":60,"avgHeartRate":72,"peakHeartRate":91}', 'Maintain current pre-shot routine.', 'Felt focused and calm.', 60, 60, true, now() - interval '1 day', now()),
  ('11111111-1111-4111-8111-111111111112', 'TEST-ATH-001', (select coach_id::text from public.coaches where upper(coach_id_text) = 'C001' limit 1), current_date - 5, '06:00', '07:00', 60, 'Shooting', 'Range A', '{"plannedShots":60,"avgHeartRate":74,"peakHeartRate":94}', 'Good hold stability.', 'Strong rhythm.', 60, 60, true, now() - interval '5 days', now()),
  ('22222222-2222-4222-8222-222222222221', 'TEST-ATH-002', (select coach_id::text from public.coaches where upper(coach_id_text) = 'C001' limit 1), current_date - 2, '07:00', '08:00', 60, 'Shooting', 'Range B', '{"plannedShots":50,"avgHeartRate":82,"peakHeartRate":108}', 'Add breathing reset after every ten shots.', 'Good start, lost focus late.', 50, 50, true, now() - interval '2 days', now()),
  ('33333333-3333-4333-8333-333333333331', 'TEST-ATH-003', (select coach_id::text from public.coaches where upper(coach_id_text) = 'C001' limit 1), current_date - 1, '17:00', '18:00', 60, 'Shooting', 'Range A', '{"plannedShots":50,"avgHeartRate":96,"peakHeartRate":132}', 'Reduce load. Recovery session recommended.', 'Tired and distracted.', 50, 42, true, now() - interval '1 day', now()),
  ('44444444-4444-4444-8444-444444444441', 'TEST-ATH-004', (select coach_id::text from public.coaches where upper(coach_id_text) = 'C001' limit 1), current_date - 21, '06:30', '07:15', 45, 'Shooting', 'Range C', '{"plannedShots":40,"avgHeartRate":76,"peakHeartRate":98}', 'Needs schedule confirmation.', 'Returned after break.', 40, 38, false, now() - interval '21 days', now())
on conflict (session_id) do update
set session_date = excluded.session_date,
    notes = excluded.notes,
    coach_notes = excluded.coach_notes,
    athlete_notes = excluded.athlete_notes,
    planned_shots = excluded.planned_shots,
    completed_shots = excluded.completed_shots,
    reflection_submitted = excluded.reflection_submitted,
    updated_at = now();

insert into public.athlete_physiology (
  physiology_id, athlete_id, session_id, recorded_date, resting_heart_rate,
  avg_heart_rate, min_heart_rate, max_heart_rate, rmssd, hrv_ms,
  hr_std_dev, sleep_hours, recovery_score, stress_score, fatigue_level,
  zone_1_time, zone_2_time, zone_3_time, zone_4_time, zone_5_time,
  stability_score, acc_hold_stability, acc_settle_score, acc_spike_count, remarks
)
values
  ('TEST-PHY-001', 'TEST-ATH-001', '11111111-1111-4111-8111-111111111111', current_date - 1, 58, 72, 55, 91, 72, 72, 5.2, 8.1, 91, 22, 2, 24, 31, 10, 4, 1, 88, 91, 86, 2, '{"mood":"Great","energyLevel":9}'),
  ('TEST-PHY-002', 'TEST-ATH-002', '22222222-2222-4222-8222-222222222221', current_date - 2, 66, 82, 62, 108, 54, 54, 8.4, 7.0, 72, 48, 5, 18, 24, 15, 8, 2, 70, 74, 68, 6, '{"mood":"Good","energyLevel":7}'),
  ('TEST-PHY-003', 'TEST-ATH-003', '33333333-3333-4333-8333-333333333331', current_date - 1, 79, 96, 74, 132, 28, 28, 14.8, 4.8, 34, 86, 9, 8, 14, 22, 14, 8, 42, 45, 40, 14, '{"mood":"Poor","energyLevel":3}'),
  ('TEST-PHY-004', 'TEST-ATH-004', '44444444-4444-4444-8444-444444444441', current_date - 21, 70, 76, 66, 98, 46, 46, 6.2, 6.2, 62, 52, 5, 16, 18, 8, 2, 1, 61, 64, 60, 5, '{"mood":"Okay","energyLevel":5}')
on conflict (physiology_id) do update
set recorded_date = excluded.recorded_date,
    resting_heart_rate = excluded.resting_heart_rate,
    avg_heart_rate = excluded.avg_heart_rate,
    min_heart_rate = excluded.min_heart_rate,
    max_heart_rate = excluded.max_heart_rate,
    rmssd = excluded.rmssd,
    hrv_ms = excluded.hrv_ms,
    sleep_hours = excluded.sleep_hours,
    recovery_score = excluded.recovery_score,
    stress_score = excluded.stress_score,
    fatigue_level = excluded.fatigue_level,
    stability_score = excluded.stability_score,
    acc_hold_stability = excluded.acc_hold_stability,
    acc_settle_score = excluded.acc_settle_score,
    acc_spike_count = excluded.acc_spike_count,
    remarks = excluded.remarks;

insert into public.athlete_scores (
  score_id, athlete_id, score_type, score_value, percentile, category,
  calculated_at, source_data, created_at, updated_at
)
values
  ('TEST-SCORE-001-OVERALL', 'TEST-ATH-001', 'overall', 92, 94, 'Strong', now() - interval '1 day', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-001-READINESS', 'TEST-ATH-001', 'readiness', 88, 90, 'Strong', now() - interval '1 day', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-001-FOCUS', 'TEST-ATH-001', 'focus', 90, 91, 'Strong', now() - interval '1 day', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-001-CONSISTENCY', 'TEST-ATH-001', 'consistency', 86, 88, 'Strong', now() - interval '1 day', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-001-BESTSERIES', 'TEST-ATH-001', 'best_series', 98, 96, 'Strong', now() - interval '1 day', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-002-OVERALL', 'TEST-ATH-002', 'overall', 74, 66, 'Progressing', now() - interval '2 days', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-002-READINESS', 'TEST-ATH-002', 'readiness', 70, 62, 'Progressing', now() - interval '2 days', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-002-FOCUS', 'TEST-ATH-002', 'focus', 64, 58, 'Progressing', now() - interval '2 days', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-002-CONSISTENCY', 'TEST-ATH-002', 'consistency', 76, 70, 'Progressing', now() - interval '2 days', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-002-BESTSERIES', 'TEST-ATH-002', 'best_series', 88, 76, 'Progressing', now() - interval '2 days', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-003-OVERALL', 'TEST-ATH-003', 'overall', 51, 28, 'Needs Attention', now() - interval '1 day', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-003-READINESS', 'TEST-ATH-003', 'readiness', 36, 18, 'Needs Attention', now() - interval '1 day', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-003-FOCUS', 'TEST-ATH-003', 'focus', 42, 24, 'Needs Attention', now() - interval '1 day', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-003-CONSISTENCY', 'TEST-ATH-003', 'consistency', 44, 22, 'Needs Attention', now() - interval '1 day', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-003-BESTSERIES', 'TEST-ATH-003', 'best_series', 68, 36, 'Needs Attention', now() - interval '1 day', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-004-OVERALL', 'TEST-ATH-004', 'overall', 63, 45, 'Stable', now() - interval '21 days', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-004-READINESS', 'TEST-ATH-004', 'readiness', 58, 38, 'Stable', now() - interval '21 days', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-004-FOCUS', 'TEST-ATH-004', 'focus', 57, 37, 'Stable', now() - interval '21 days', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-004-CONSISTENCY', 'TEST-ATH-004', 'consistency', 52, 33, 'Stable', now() - interval '21 days', '{"source":"test data"}', now(), now()),
  ('TEST-SCORE-004-BESTSERIES', 'TEST-ATH-004', 'best_series', 75, 49, 'Stable', now() - interval '21 days', '{"source":"test data"}', now(), now())
on conflict (score_id) do update
set score_value = excluded.score_value,
    percentile = excluded.percentile,
    category = excluded.category,
    calculated_at = excluded.calculated_at,
    source_data = excluded.source_data,
    updated_at = now();

insert into public.training_plans (
  training_plan_id, athlete_id, coach_id, focus_area, recommended_drills,
  session_frequency, recovery_instructions, mental_training_notes,
  coach_recommendation, status, generated_from, updated_at
)
values
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1', 'TEST-ATH-001', (select coach_id from public.coaches where upper(coach_id_text) = 'C001' limit 1), 'Match simulation', 'Final hold stability block', '4 sessions/week', 'Normal recovery', 'Preserve routine', 'Prepare competition simulation.', 'In Progress', '{"source":"test data"}', now()),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2', 'TEST-ATH-002', (select coach_id from public.coaches where upper(coach_id_text) = 'C001' limit 1), 'Focus endurance', '10-shot reset drill', '3 sessions/week', 'Hydration and cooldown', 'Breathing reset', 'Stabilize final series focus.', 'Needs Review', '{"source":"test data"}', now()),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa3', 'TEST-ATH-003', (select coach_id from public.coaches where upper(coach_id_text) = 'C001' limit 1), 'Recovery and regulation', 'Low-load technical session', '2 sessions/week', 'Sleep target 7.5h before next live session', '5-minute breathing protocol', 'Reduce training load and review stress driver.', 'New', '{"source":"test data"}', now()),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa4', 'TEST-ATH-004', (select coach_id from public.coaches where upper(coach_id_text) = 'C001' limit 1), 'Return to rhythm', 'Baseline grouping drill', '2 sessions/week', 'Gradual load increase', 'Reflection after every session', 'Confirm schedule and rebuild consistency.', 'Needs Review', '{"source":"test data"}', now())
on conflict (training_plan_id) do update
set focus_area = excluded.focus_area,
    recommended_drills = excluded.recommended_drills,
    session_frequency = excluded.session_frequency,
    recovery_instructions = excluded.recovery_instructions,
    mental_training_notes = excluded.mental_training_notes,
    coach_recommendation = excluded.coach_recommendation,
    status = excluded.status,
    generated_from = excluded.generated_from,
    updated_at = now();

insert into public.athlete_insights (
  insight_id, athlete_id, session_id, title, insight_text, category,
  score, priority, suggested_action, supporting_data, created_at
)
values
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1', 'TEST-ATH-001', '11111111-1111-4111-8111-111111111111', 'Healthy high performer', 'Performance stays high while fatigue and stress remain low.', 'coach_performance', 92, 'Low', 'Preserve routine and increase match simulation difficulty.', '{"performance":92,"fatigue":20,"stress":22}', now()),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2', 'TEST-ATH-003', '33333333-3333-4333-8333-333333333331', 'Fatigue is driving risk', 'Performance drops when fatigue and stress are elevated.', 'coach_risk', 86, 'High', 'Reduce load and run a stress regulation check-in today.', '{"performance":51,"fatigue":90,"stress":86}', now()),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb3', 'TEST-ATH-004', '44444444-4444-4444-8444-444444444441', 'No recent activity', 'Athlete has not logged a current-week training session.', 'coach_activity', 75, 'Medium', 'Contact athlete and confirm next planned session.', '{"daysSinceSession":21}', now())
on conflict (insight_id) do update
set title = excluded.title,
    insight_text = excluded.insight_text,
    category = excluded.category,
    score = excluded.score,
    priority = excluded.priority,
    suggested_action = excluded.suggested_action,
    supporting_data = excluded.supporting_data,
    created_at = excluded.created_at;

insert into public.coach_feedback (
  feedback_id, athlete_id, athlete_name, athlete_email, coach_email, coach_name,
  coach_id, note, recommendation, status, training_plan, created_at
)
values
  ('cccccccc-cccc-4ccc-8ccc-ccccccccccc1', 'TEST-ATH-003', 'Mira Sen', 'mira.test@hamsatech.ai', 'coach@hamsatech.ai', 'HamsaTech Coach', (select coach_id from public.coaches where upper(coach_id_text) = 'C001' limit 1), 'Fatigue is too high for normal load.', 'Run recovery session and breathing drill before next live firing.', 'Needs Attention', 'Recovery and regulation block.', now() - interval '1 hour')
on conflict (feedback_id) do update
set note = excluded.note,
    recommendation = excluded.recommendation,
    status = excluded.status,
    training_plan = excluded.training_plan,
    created_at = excluded.created_at;

insert into public.assignment_requests (
  request_id, athlete_id, requesting_coach_id, assigned_coach_id, status, notes, requested_at
)
values
  ('dddddddd-dddd-4ddd-8ddd-ddddddddddd1', 'TEST-ATH-002', null, (select coach_id from public.coaches where upper(coach_id_text) = 'C001' limit 1), 'PENDING', 'Dashboard test pending assignment for Kabir Mehta.', now() - interval '45 minutes'),
  ('dddddddd-dddd-4ddd-8ddd-ddddddddddd2', 'TEST-ATH-004', null, (select coach_id from public.coaches where upper(coach_id_text) = 'C001' limit 1), 'PENDING', 'Dashboard test pending assignment for Dev Iyer.', now() - interval '25 minutes')
on conflict (request_id) do update
set assigned_coach_id = excluded.assigned_coach_id,
    status = excluded.status,
    notes = excluded.notes,
    requested_at = excluded.requested_at,
    assigned_at = null;

select
  a.athlete_id,
  a.athlete_name,
  a.coach_id,
  s.session_date,
  p.recovery_score,
  p.stress_score,
  p.fatigue_level
from public.athletes a
left join public.shooting_session_log s on s.athlete_id = a.athlete_id
left join public.athlete_physiology p on p.session_id = s.session_id
where a.athlete_id like 'TEST-ATH-%'
order by a.athlete_id, s.session_date desc;
