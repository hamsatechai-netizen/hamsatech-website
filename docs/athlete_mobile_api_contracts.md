# ASTRA Athlete Mobile API Contracts

Scope: Flutter athlete profile/onboarding, home, check-in, and training-session flows from `ASTRA.pdf`.

Constraint: no new migrations or tables. These APIs write to existing tables only.

## Existing Table Mapping

- `athletes`: registration, name, age, gender, academy/discipline, onboarding status.
- `athlete_details`: mobile profile details stored in existing text fields:
  - `academic_performance`: JSON for `averagePracticeScore`, `targetScore`, `experienceLevel`, `yearsShooting`
  - `reason_for_shooting`: JSON for `city`, `discipline`, `academyClub`, `performanceFactors`
  - `athlete_goal`: JSON for `goal30Days`, `goal6Months`
- `shooting_session_log`: mobile training session setup/status.
- `athlete_physiology`: Polar baseline and session heart-rate snapshots.
- `psychology_questions` / `psychology_responses`: daily check-in and session reflection JSON payloads.
- `athlete_scores`: per-series score entries using `score_type = mobile_series`.
- `coach_feedback`: coach messages shown on athlete home/report screens.

## Endpoints

### Register Athlete

`POST /api/mobile/athletes/register`

```json
{
  "fullName": "Alex Rao",
  "email": "alex@example.com",
  "age": 15,
  "gender": "Female",
  "phone": "9999999999",
  "sport": "Air Pistol",
  "focusArea": "Competition focus"
}
```

Response: `201`

```json
{
  "athleteId": "uuid-or-client-id",
  "assignedCoachEmail": "coach@hamsatech.ai",
  "notificationCreated": true,
  "success": true
}
```

### Athlete Profile

`GET /api/mobile/athletes/{athleteId}/profile`

`PUT /api/mobile/athletes/{athleteId}/profile`

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

Response shape:

```json
{
  "profile": {
    "athleteId": "athlete-id",
    "fullName": "Alex Rao",
    "discipline": "Air Pistol",
    "restingHrBaseline": 68,
    "onboardingStatus": "ready_to_train",
    "profileCompletionStatus": "complete"
  }
}
```

### Baseline

`POST /api/mobile/athletes/{athleteId}/baseline`

```json
{
  "restingHrBaseline": 68,
  "hrvBaselineMs": 75,
  "polarLinked": true,
  "polarDeviceId": "polar-device-id"
}
```

Writes a `Recovery` row to `shooting_session_log` and a matching row to `athlete_physiology`.

### Daily Check-In

`POST /api/mobile/athletes/{athleteId}/daily-checkins`

```json
{
  "checkinDate": "2026-05-19",
  "mood": "Good",
  "energyLevel": 5,
  "sleepBand": "7-8h",
  "sleepHours": 7.5,
  "tags": ["Focused", "Calm"],
  "notes": "Ready for training"
}
```

`GET /api/mobile/athletes/{athleteId}/daily-checkins/latest`

### Home Snapshot

`GET /api/mobile/athletes/{athleteId}/home`

Returns profile status, readiness metrics, latest check-in, recent sessions, coach feedback, and recommendations.

### Training Sessions

`POST /api/mobile/athletes/{athleteId}/sessions`

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

`GET /api/mobile/athletes/{athleteId}/sessions?limit=20`

### Series Scores

`POST /api/mobile/athletes/{athleteId}/sessions/{sessionId}/series`

```json
{
  "seriesNumber": 2,
  "shots": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
  "avgHeartRate": 80
}
```

Stores a row in `athlete_scores` with `score_type = mobile_series`.

### Reflection And Summary

`POST /api/mobile/athletes/{athleteId}/sessions/{sessionId}/reflection`

```json
{
  "mood": "Okay",
  "whatWorked": "Breathing was steady",
  "whatDidnt": "Lost focus in series 2",
  "selfRating": 6,
  "fatigueLevel": 7
}
```

`POST /api/mobile/athletes/{athleteId}/sessions/{sessionId}/complete`

```json
{
  "durationSeconds": 3600,
  "avgHeartRate": 77,
  "peakHeartRate": 92,
  "fatigue": "Low",
  "recovery": "Fair"
}
```

`GET /api/mobile/athletes/{athleteId}/sessions/{sessionId}/summary`

Returns total score, average, efficiency, best/worst shot, series breakdown, physiology, reflection, key insight, and recommendations.
