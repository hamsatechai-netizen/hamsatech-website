from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import json
import logging
import os
import re
import secrets
import json
import logging
import re
from uuid import uuid4
from typing import Annotated, Any
from typing import Literal

from fastapi import Cookie, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field
from twilio.rest import Client as TwilioClient

from .config import settings
from .security import (
    UserRecord,
    generate_salt,
    generate_session_token,
    hash_password,
    verify_password,
)
from .supabase_client import get_supabase_admin_client


logger = logging.getLogger(__name__)

UUID_LIKE_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


logger = logging.getLogger(__name__)

UUID_LIKE_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


app = FastAPI(title="HamsaTech Auth API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_origin_regex=settings.normalized_frontend_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_PSYCHOLOGY_QUESTIONS = [
    {
        "question_id": "Q1",
        "question_text": "How stressed do you feel?",
        "category": "Stress",
        "question_type": "Scale",
    },
    {
        "question_id": "Q2",
        "question_text": "How focused were you today?",
        "category": "Focus",
        "question_type": "Scale",
    },
    {
        "question_id": "Q3",
        "question_text": "What distracted you today?",
        "category": "Behavior",
        "question_type": "Text",
    },
]

MOBILE_PSYCHOLOGY_QUESTIONS = [
    {
        "question_id": "MOBILE_DAILY_CHECKIN",
        "question_text": "Mobile daily athlete check-in",
        "category": "Mobile",
        "question_type": "Json",
    },
    {
        "question_id": "MOBILE_SESSION_REFLECTION",
        "question_text": "Mobile training session reflection",
        "category": "Mobile",
        "question_type": "Json",
    },
]


APP_TABLES = {
    "athletes": "athletes",
    "athlete_details": "athlete_details",
    "athlete_family": "athlete_family",
    "athlete_physiology": "athlete_physiology",
    "shooting_session_log": "shooting_session_log",
    "psychology_questions": "psychology_questions",
    "psychology_responses": "psychology_responses",
    "coach_feedback": "coach_feedback",
    "coach_profiles": "coach_profiles",
    "coach_assignments": "coach_athlete_assignments",
    "athlete_scores": "athlete_scores",
    "notifications": "notifications",
    "audit_logs": "audit_logs",
}

ADMIN_EMAIL = "admin@hamsatech.ai"

MOBILE_PSYCHOLOGY_QUESTIONS = [
    {
        "question_id": "MOBILE_DAILY_CHECKIN",
        "question_text": "Mobile daily athlete check-in",
        "category": "Mobile",
        "question_type": "Json",
    },
    {
        "question_id": "MOBILE_SESSION_REFLECTION",
        "question_text": "Mobile training session reflection",
        "category": "Mobile",
        "question_type": "Json",
    },
]


APP_TABLES = {
    "athletes": "athletes",
    "athlete_details": "athlete_details",
    "athlete_family": "athlete_family",
    "athlete_physiology": "athlete_physiology",
    "shooting_session_log": "shooting_session_log",
    "psychology_questions": "psychology_questions",
    "psychology_responses": "psychology_responses",
    "coach_feedback": "coach_feedback",
    "coach_profiles": "coach_profiles",
    "coach_assignments": "coach_athlete_assignments",
    "athlete_scores": "athlete_scores",
    "notifications": "notifications",
    "audit_logs": "audit_logs",
}

ADMIN_EMAIL = "admin@hamsatech.ai"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class SignUpRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=80, alias="fullName")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["student"] = "student"
    sport: str | None = Field(default=None, min_length=2, max_length=50)
    focus_area: str | None = Field(default=None, min_length=2, max_length=80, alias="focusArea")
    date_of_birth: date | None = Field(default=None, alias="dateOfBirth")


class AuthenticatedUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    full_name: str = Field(alias="fullName")
    role: Literal["coach", "student"]
    coach_code: str | None = Field(default=None, alias="coachCode")
    assignment_status: Literal["unassigned", "pending", "assigned"] = Field(
        default="unassigned",
        alias="assignmentStatus",
    )
    assigned_coach_code: str | None = Field(default=None, alias="assignedCoachCode")
    assigned_coach_email: str | None = Field(default=None, alias="assignedCoachEmail")
    assigned_coach_name: str | None = Field(default=None, alias="assignedCoachName")
    requested_coach_code: str | None = Field(default=None, alias="requestedCoachCode")
    requested_coach_email: str | None = Field(default=None, alias="requestedCoachEmail")
    requested_coach_name: str | None = Field(default=None, alias="requestedCoachName")
    sport: str | None = None
    focus_area: str | None = Field(default=None, alias="focusArea")
    date_of_birth: date | None = Field(default=None, alias="dateOfBirth")
    performance_score: int | None = Field(default=None, alias="performanceScore")


class StudentProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    full_name: str = Field(alias="fullName")
    assigned_coach_email: str | None = Field(default=None, alias="assignedCoachEmail")
    assigned_coach_name: str | None = Field(default=None, alias="assignedCoachName")
    sport: str
    focus_area: str = Field(alias="focusArea")
    date_of_birth: date = Field(alias="dateOfBirth")
    performance_score: int = Field(alias="performanceScore")


class AuthResponse(BaseModel):
    user: AuthenticatedUser


class StudentsResponse(BaseModel):
    students: list[StudentProfile]


class CoachAssignmentRequestRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    full_name: str = Field(alias="fullName")
    sport: str
    focus_area: str = Field(alias="focusArea")
    requested_coach_code: str = Field(alias="requestedCoachCode")
    requested_coach_name: str = Field(alias="requestedCoachName")
    requested_at: str | None = Field(default=None, alias="requestedAt")
    assignment_status: Literal["pending"] = Field(alias="assignmentStatus")


class CoachAssignmentRequestsResponse(BaseModel):
    requests: list[CoachAssignmentRequestRecord]


class CoachAssignmentApprovalInput(BaseModel):
    coach_code: str = Field(alias="coachCode", min_length=4, max_length=80)


class CoachAthleteListItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    athlete_id: str = Field(alias="athleteId")
    name: str
    age: int | None = None
    gender: str | None = None
    academy_id: str | None = Field(default=None, alias="academyId")
    coach_id: str | None = Field(default=None, alias="coachId")
    email: str | None = None
    contact_number: str | None = Field(default=None, alias="contactNumber")
    created_at: str | None = Field(default=None, alias="createdAt")
    latest_session_date: str | None = Field(default=None, alias="latestSessionDate")
    latest_training_type: str | None = Field(default=None, alias="latestTrainingType")
    latest_recovery_score: float | None = Field(default=None, alias="latestRecoveryScore")
    latest_stress_score: float | None = Field(default=None, alias="latestStressScore")
    latest_fatigue_level: int | None = Field(default=None, alias="latestFatigueLevel")
    latest_sleep_hours: float | None = Field(default=None, alias="latestSleepHours")
    overall_score: float | None = Field(default=None, alias="overallScore")
    age: int | None = None
    gender: str | None = None
    academy_id: str | None = Field(default=None, alias="academyId")
    coach_id: str | None = Field(default=None, alias="coachId")
    email: str | None = None
    contact_number: str | None = Field(default=None, alias="contactNumber")
    created_at: str | None = Field(default=None, alias="createdAt")
    latest_session_date: str | None = Field(default=None, alias="latestSessionDate")
    latest_training_type: str | None = Field(default=None, alias="latestTrainingType")
    latest_recovery_score: float | None = Field(default=None, alias="latestRecoveryScore")
    latest_stress_score: float | None = Field(default=None, alias="latestStressScore")
    latest_fatigue_level: int | None = Field(default=None, alias="latestFatigueLevel")
    latest_sleep_hours: float | None = Field(default=None, alias="latestSleepHours")
    overall_score: float | None = Field(default=None, alias="overallScore")


class CoachAthleteListResponse(BaseModel):
    athletes: list[CoachAthleteListItem]


class CoachAthleteDetailResponse(BaseModel):
    athlete: dict[str, Any]

class CoachAthleteWidgetResponse(BaseModel):
    widget: dict[str, Any]

class CoachAthleteSessionsWidgetResponse(BaseModel):
    widget: dict[str, Any]

class CoachAthleteInsightsWidgetResponse(BaseModel):
    widget: dict[str, Any]


class CoachAthleteProfileWidgetResponse(BaseModel):
    widget: dict[str, Any]

class CoachAthleteWidgetResponse(BaseModel):
    widget: dict[str, Any]

class CoachAthleteSessionsWidgetResponse(BaseModel):
    widget: dict[str, Any]

class CoachAthleteInsightsWidgetResponse(BaseModel):
    widget: dict[str, Any]


class CoachAthleteProfileWidgetResponse(BaseModel):
    widget: dict[str, Any]


class StatusResponse(BaseModel):
    success: bool


class CoachFeedbackInput(BaseModel):
    note: str = Field(min_length=2, max_length=500)
    recommendation: str = Field(min_length=2, max_length=500)
    status: Literal["Needs Attention", "Progressing", "Strong"] = "Progressing"


class CoachFeedbackRecord(BaseModel):
    feedback_id: str = Field(alias="feedbackId")
    athlete_id: str = Field(alias="athleteId")
    athlete_name: str = Field(alias="athleteName")
    athlete_email: str = Field(alias="athleteEmail")
    coach_email: str = Field(alias="coachEmail")
    athlete_email: str = Field(alias="athleteEmail")
    coach_email: str = Field(alias="coachEmail")
    coach_name: str = Field(alias="coachName")
    note: str
    recommendation: str
    status: Literal["Needs Attention", "Progressing", "Strong"]
    created_at: str = Field(alias="createdAt")


class CoachFeedbackResponse(BaseModel):
    feedback: CoachFeedbackRecord


class CoachFeedbackListResponse(BaseModel):
    feedback: list[CoachFeedbackRecord]


class CoachProfileRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    coach_id: str = Field(alias="coachId")
    name: str
    email: str
    phone: str | None = None
    profile_image: str | None = Field(default=None, alias="profileImage")
    specialization: str | None = None
    status: Literal["active", "inactive"] = "active"
    assigned_athletes: int = Field(default=0, alias="assignedAthletes")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class CoachProfileResponse(BaseModel):
    profile: CoachProfileRecord


class CoachProfilesResponse(BaseModel):
    coaches: list[CoachProfileRecord]


class CoachProfileInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    profile_image: str | None = Field(default=None, alias="profileImage", max_length=500)
    specialization: str | None = Field(default=None, max_length=120)
    status: Literal["active", "inactive"] = "active"
    password: str | None = Field(default=None, min_length=8, max_length=128)
    coach_code: str | None = Field(default=None, alias="coachCode", min_length=4, max_length=80)


class CoachProfileUpdateInput(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    profile_image: str | None = Field(default=None, alias="profileImage", max_length=500)
    specialization: str | None = Field(default=None, max_length=120)
    status: Literal["active", "inactive"] | None = None


class AssignmentInput(BaseModel):
    athlete_id: str = Field(alias="athleteId", min_length=1)
    coach_email: EmailStr = Field(alias="coachEmail")


class AthleteScoreRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    score_id: str = Field(alias="scoreId")
    athlete_id: str = Field(alias="athleteId")
    score_type: str = Field(alias="scoreType")
    score_value: float = Field(alias="scoreValue")
    percentile: float | None = None
    category: str
    calculated_at: str = Field(alias="calculatedAt")
    source_data: dict[str, Any] | None = Field(default=None, alias="sourceData")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class AthleteScoresResponse(BaseModel):
    scores: list[AthleteScoreRecord]


class NotificationRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    notification_id: str = Field(alias="notificationId")
    recipient_email: str = Field(alias="recipientEmail")
    recipient_role: str = Field(alias="recipientRole")
    title: str
    message: str
    type: str
    entity_id: str | None = Field(default=None, alias="entityId")
    read_at: str | None = Field(default=None, alias="readAt")
    created_at: str = Field(alias="createdAt")


class NotificationsResponse(BaseModel):
    notifications: list[NotificationRecord]


class FeedbackRequestCreateInput(BaseModel):
    athlete_id: str = Field(alias="athleteId", min_length=1)
    session_id: str = Field(alias="sessionId", min_length=1)
    coach_id: str = Field(alias="coachId", min_length=1)


class FeedbackRequestCreateResponse(BaseModel):
    request_id: str = Field(alias="requestId")
    status: Literal["PENDING"]
    message: str


class CoachNotificationItem(BaseModel):
    notification_id: str = Field(alias="notificationId")
    type: str
    athlete_id: str | None = Field(default=None, alias="athleteId")
    athlete_name: str | None = Field(default=None, alias="athleteName")
    session_id: str | None = Field(default=None, alias="sessionId")
    request_id: str | None = Field(default=None, alias="requestId")
    message: str
    action_url: str | None = Field(default=None, alias="actionUrl")
    created_at: str = Field(alias="createdAt")
    is_read: bool = Field(alias="isRead")


class CoachNotificationsResponse(BaseModel):
    notifications: list[CoachNotificationItem]
    unread_count: int = Field(alias="unreadCount")


class NotificationMarkReadResponse(BaseModel):
    notification_id: str = Field(alias="notificationId")
    is_read: bool = Field(alias="isRead")
    read_at: str | None = Field(default=None, alias="readAt")


class V1CoachFeedbackInput(BaseModel):
    request_id: str = Field(alias="requestId", min_length=1)
    athlete_id: str = Field(alias="athleteId", min_length=1)
    note: str = Field(min_length=2, max_length=500)
    recommendation: str = Field(min_length=2, max_length=500)
    status: Literal["Needs Attention", "Progressing", "Strong"] = "Progressing"


class PendingAssignmentItem(BaseModel):
    request_id: str = Field(alias="requestId")
    athlete_id: str = Field(alias="athleteId")
    athlete_name: str = Field(alias="athleteName")
    assigned_coach_id: str | None = Field(default=None, alias="assignedCoachId")
    status: Literal["PENDING", "ASSIGNED", "REJECTED"]
    notes: str | None = None
    requested_at: str | None = Field(default=None, alias="requestedAt")


class PendingAssignmentsResponse(BaseModel):
    requests: list[PendingAssignmentItem]


class AssignAthleteInput(BaseModel):
    request_id: str = Field(alias="requestId", min_length=1)
    athlete_id: str = Field(alias="athleteId", min_length=1)
    assigned_coach_id: str = Field(alias="assignedCoachId", min_length=1)
    notes: str | None = Field(default=None, max_length=500)


class AssignAthleteResponse(BaseModel):
    success: bool
    assignment_id: str = Field(alias="assignmentId")


class CoachOptionItem(BaseModel):
    coach_id: str = Field(alias="coachId")
    coach_name: str = Field(alias="coachName")
    coach_id_text: str | None = Field(default=None, alias="coachIdText")
    specialization: str | None = None


class CoachOptionsResponse(BaseModel):
    coaches: list[CoachOptionItem]


class AthleteAssignmentStatusResponse(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    status: Literal["PENDING", "ASSIGNED", "REJECTED", "UNASSIGNED"]
    assigned_coach_id: str | None = Field(default=None, alias="assignedCoachId")
    assigned_coach_name: str | None = Field(default=None, alias="assignedCoachName")
    requested_at: str | None = Field(default=None, alias="requestedAt")
    assigned_at: str | None = Field(default=None, alias="assignedAt")


class CoachDashboardAthleteRow(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    athlete_name: str = Field(alias="athleteName")
    sport: str | None = None
    discipline: str | None = None
    gender: str | None = None
    age: int | None = None
    score: float | None = None
    readiness_score: float | None = Field(default=None, alias="readinessScore")
    focus_score: float | None = Field(default=None, alias="focusScore")
    discipline_score: float | None = Field(default=None, alias="disciplineScore")
    score_category: str = Field(alias="scoreCategory")
    status: Literal["Strong", "Stable", "Needs Attention", "At Risk"] = "Stable"
    trend: Literal["Improving", "Declining", "Stable"] = "Stable"
    latest_stress: float | None = Field(default=None, alias="latestStress")
    resting_hr: float | None = Field(default=None, alias="restingHr")
    hrv_indicator: float | None = Field(default=None, alias="hrvIndicator")
    fatigue_score: float | None = Field(default=None, alias="fatigueScore")
    latest_recovery: float | None = Field(default=None, alias="latestRecovery")
    sleep_hours: float | None = Field(default=None, alias="sleepHours")
    last_session_date: str | None = Field(default=None, alias="lastSessionDate")
    risk_score: float = Field(default=0, alias="riskScore")
    risk_reasons: list[str] = Field(default_factory=list, alias="riskReasons")
    suggested_action: str | None = Field(default=None, alias="suggestedAction")


class CoachDashboardRiskItem(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    athlete_name: str = Field(alias="athleteName")
    severity: Literal["High", "Medium", "Low"]
    reasons: list[str]
    suggested_action: str = Field(alias="suggestedAction")


class CoachDashboardInsightItem(BaseModel):
    title: str
    insight_text: str = Field(alias="insightText")
    category: str
    score: float | None = None
    priority: Literal["High", "Medium", "Low"] = "Medium"


class CoachDashboardScatterPoint(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    athlete_name: str = Field(alias="athleteName")
    performance: float | None = None
    stress: float | None = None
    fatigue: float | None = None
    readiness: float | None = None
    sleep: float | None = None
    resting_hr: float | None = Field(default=None, alias="restingHr")
    hrv_indicator: float | None = Field(default=None, alias="hrvIndicator")
    focus: float | None = None
    consistency: float | None = None


class CoachDashboardV1Payload(BaseModel):
    coach_id: str = Field(alias="coachId")
    totals: dict[str, float | int | None]
    average_score: float | None = Field(default=None, alias="averageScore")
    average_readiness: float | None = Field(default=None, alias="averageReadiness")
    average_fatigue: float | None = Field(default=None, alias="averageFatigue")
    average_stress: float | None = Field(default=None, alias="averageStress")
    score_distribution: dict[str, int] = Field(alias="scoreDistribution")
    athletes: list[CoachDashboardAthleteRow]
    top_performers: list[CoachDashboardAthleteRow] = Field(default_factory=list, alias="topPerformers")
    most_disciplined: list[CoachDashboardAthleteRow] = Field(default_factory=list, alias="mostDisciplined")
    healthy_focused: list[CoachDashboardAthleteRow] = Field(default_factory=list, alias="healthyFocused")
    risk_queue: list[CoachDashboardRiskItem] = Field(default_factory=list, alias="riskQueue")
    mapping: dict[str, list[CoachDashboardScatterPoint]] = Field(default_factory=dict)
    insights: list[CoachDashboardInsightItem] = Field(default_factory=list)
    alerts: list[str]


class CoachDashboardV1Response(BaseModel):
    dashboard: CoachDashboardV1Payload


class AthleteFullProfileV1Response(BaseModel):
    athlete: dict[str, Any]


class CoachDashboardSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_assigned_athletes: int = Field(alias="totalAssignedAthletes")
    new_registrations: int = Field(alias="newRegistrations")
    active_athletes: int = Field(alias="activeAthletes")
    inactive_athletes: int = Field(alias="inactiveAthletes")
    average_score: float | None = Field(default=None, alias="averageScore")
    highest_performing: list[CoachAthleteListItem] = Field(alias="highestPerforming")
    lowest_performing: list[CoachAthleteListItem] = Field(alias="lowestPerforming")
    score_distribution: dict[str, int] = Field(alias="scoreDistribution")
    recent_activity: list[NotificationRecord] = Field(alias="recentActivity")
    alerts: list[str]


class CoachDashboardSummaryResponse(BaseModel):
    summary: CoachDashboardSummary


class MobileAthleteRegistrationInput(BaseModel):
    athlete_id: str | None = Field(default=None, alias="athleteId")
    full_name: str = Field(alias="fullName", min_length=2, max_length=100)
    email: EmailStr
    age: int = Field(ge=5, le=80)
    gender: Literal["Male", "Female", "Other"]
    phone: str = Field(min_length=7, max_length=20)
    sport: str | None = Field(default=None, max_length=50)
    focus_area: str | None = Field(default=None, alias="focusArea", max_length=80)
    assigned_coach_email: EmailStr | None = Field(default=None, alias="assignedCoachEmail")
    assigned_coach_id: str | None = Field(default=None, alias="assignedCoachId", min_length=1, max_length=80)
    selected_coach_id: str | None = Field(default=None, alias="selectedCoachId", min_length=1, max_length=80)
    profile_completion_status: Literal["incomplete", "partial", "complete"] = Field(default="partial", alias="profileCompletionStatus")


class MobileAthleteRegistrationResponse(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    assigned_coach_email: str | None = Field(default=None, alias="assignedCoachEmail")
    notification_created: bool = Field(alias="notificationCreated")
    success: bool


class MobileAthleteProfileUpsertInput(BaseModel):
    full_name: str | None = Field(default=None, alias="fullName", min_length=2, max_length=100)
    age: int | None = Field(default=None, ge=5, le=80)
    gender: Literal["Male", "Female", "Other"] | None = None
    city: str | None = Field(default=None, min_length=2, max_length=80)
    discipline: str | None = Field(default=None, min_length=2, max_length=80)
    experience_level: Literal["Beginner", "Intermediate", "Advanced"] | None = Field(default=None, alias="experienceLevel")
    years_shooting: int | None = Field(default=None, alias="yearsShooting", ge=0, le=80)
    academy_club: str | None = Field(default=None, alias="academyClub", max_length=120)
    average_practice_score: float | None = Field(default=None, alias="averagePracticeScore", ge=0)
    target_score: float | None = Field(default=None, alias="targetScore", ge=0)
    performance_factors: list[str] | None = Field(default=None, alias="performanceFactors")
    goal_30_days: str | None = Field(default=None, alias="goal30Days", max_length=500)
    goal_6_months: str | None = Field(default=None, alias="goal6Months", max_length=500)
    polar_linked: bool | None = Field(default=None, alias="polarLinked")
    polar_device_id: str | None = Field(default=None, alias="polarDeviceId", max_length=120)


class MobileAthleteProfileRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    athlete_id: str = Field(alias="athleteId")
    full_name: str | None = Field(default=None, alias="fullName")
    age: int | None = None
    gender: str | None = None
    city: str | None = None
    discipline: str | None = None
    experience_level: str | None = Field(default=None, alias="experienceLevel")
    years_shooting: int | None = Field(default=None, alias="yearsShooting")
    academy_club: str | None = Field(default=None, alias="academyClub")
    average_practice_score: float | None = Field(default=None, alias="averagePracticeScore")
    target_score: float | None = Field(default=None, alias="targetScore")
    performance_factors: list[str] = Field(default_factory=list, alias="performanceFactors")
    goal_30_days: str | None = Field(default=None, alias="goal30Days")
    goal_6_months: str | None = Field(default=None, alias="goal6Months")
    polar_linked: bool = Field(default=False, alias="polarLinked")
    polar_device_id: str | None = Field(default=None, alias="polarDeviceId")
    resting_hr_baseline: int | None = Field(default=None, alias="restingHrBaseline")
    hrv_baseline_ms: int | None = Field(default=None, alias="hrvBaselineMs")
    onboarding_status: str = Field(alias="onboardingStatus")
    profile_completion_status: str = Field(alias="profileCompletionStatus")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class MobileAthleteProfileResponse(BaseModel):
    profile: MobileAthleteProfileRecord


class MobileBaselineInput(BaseModel):
    resting_hr_baseline: int = Field(alias="restingHrBaseline", ge=30, le=220)
    hrv_baseline_ms: int | None = Field(default=None, alias="hrvBaselineMs", ge=1, le=300)
    polar_linked: bool = Field(default=True, alias="polarLinked")
    polar_device_id: str | None = Field(default=None, alias="polarDeviceId", max_length=120)


class MobileDailyCheckinInput(BaseModel):
    checkin_date: date | None = Field(default=None, alias="checkinDate")
    mood: Literal["Trouble", "Poor", "Okay", "Good", "Great"]
    energy_level: int = Field(alias="energyLevel", ge=1, le=10)
    sleep_band: Literal["<5h", "5-6h", "6-7h", "7-8h", "8h+"] | None = Field(default=None, alias="sleepBand")
    sleep_hours: float | None = Field(default=None, alias="sleepHours", ge=0, le=14)
    tags: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=500)


class MobileDailyCheckinRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    checkin_id: str = Field(alias="checkinId")
    athlete_id: str = Field(alias="athleteId")
    checkin_date: date = Field(alias="checkinDate")
    mood: str
    energy_level: int = Field(alias="energyLevel")
    sleep_band: str | None = Field(default=None, alias="sleepBand")
    sleep_hours: float | None = Field(default=None, alias="sleepHours")
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class MobileDailyCheckinResponse(BaseModel):
    checkin: MobileDailyCheckinRecord


class MobileAthleteHomeResponse(BaseModel):
    home: dict[str, Any]


class MobileTrainingSessionCreateInput(BaseModel):
    range_type: Literal["Paper", "Electronic"] = Field(alias="rangeType")
    session_type: Literal["Scoring", "Grouping", "Dry Fire"] = Field(alias="sessionType")
    planned_shots: int = Field(alias="plannedShots", ge=1, le=300)
    discipline: str | None = Field(default=None, max_length=80)
    intention: str | None = Field(default=None, max_length=500)
    visualization: str | None = Field(default=None, max_length=500)
    body_scan_completed: bool = Field(default=False, alias="bodyScanCompleted")
    start_now: bool = Field(default=False, alias="startNow")


class MobileTrainingSeriesInput(BaseModel):
    series_number: int = Field(alias="seriesNumber", ge=1, le=30)
    shots: list[Any] = Field(min_length=1, max_length=30)
    avg_heart_rate: float | None = Field(default=None, alias="avgHeartRate", ge=30, le=220)


class MobileSessionCompleteInput(BaseModel):
    duration_seconds: int | None = Field(default=None, alias="durationSeconds", ge=0)
    avg_heart_rate: float | None = Field(default=None, alias="avgHeartRate", ge=30, le=220)
    peak_heart_rate: float | None = Field(default=None, alias="peakHeartRate", ge=30, le=240)
    fatigue: str | None = Field(default=None, max_length=40)
    recovery: str | None = Field(default=None, max_length=40)


class MobileSessionReflectionInput(BaseModel):
    mood: Literal["Trouble", "Poor", "Okay", "Good", "Great"]
    what_worked: str | None = Field(default=None, alias="whatWorked", max_length=1000)
    what_didnt: str | None = Field(default=None, alias="whatDidnt", max_length=1000)
    voice_note_url: str | None = Field(default=None, alias="voiceNoteUrl", max_length=500)
    self_rating: int | None = Field(default=None, alias="selfRating", ge=1, le=10)
    fatigue_level: int | None = Field(default=None, alias="fatigueLevel", ge=1, le=10)


class MobileTrainingSessionResponse(BaseModel):
    session: dict[str, Any]


class MobileTrainingSessionsResponse(BaseModel):
    sessions: list[dict[str, Any]]


class MobileTrainingSeriesResponse(BaseModel):
    series: dict[str, Any]
    summary: dict[str, Any]


class MobileSessionReflectionResponse(BaseModel):
    reflection: dict[str, Any]
    summary: dict[str, Any]


class MobileSessionSummaryResponse(BaseModel):
    summary: dict[str, Any]


class CoachProfileRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    coach_id: str = Field(alias="coachId")
    name: str
    email: str
    phone: str | None = None
    profile_image: str | None = Field(default=None, alias="profileImage")
    specialization: str | None = None
    status: Literal["active", "inactive"] = "active"
    assigned_athletes: int = Field(default=0, alias="assignedAthletes")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class CoachProfileResponse(BaseModel):
    profile: CoachProfileRecord


class CoachProfilesResponse(BaseModel):
    coaches: list[CoachProfileRecord]


class CoachProfileInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    profile_image: str | None = Field(default=None, alias="profileImage", max_length=500)
    specialization: str | None = Field(default=None, max_length=120)
    status: Literal["active", "inactive"] = "active"
    password: str | None = Field(default=None, min_length=8, max_length=128)
    coach_code: str | None = Field(default=None, alias="coachCode", min_length=4, max_length=80)


class CoachProfileUpdateInput(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    profile_image: str | None = Field(default=None, alias="profileImage", max_length=500)
    specialization: str | None = Field(default=None, max_length=120)
    status: Literal["active", "inactive"] | None = None


class AssignmentInput(BaseModel):
    athlete_id: str = Field(alias="athleteId", min_length=1)
    coach_email: EmailStr = Field(alias="coachEmail")


class AthleteScoreRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    score_id: str = Field(alias="scoreId")
    athlete_id: str = Field(alias="athleteId")
    score_type: str = Field(alias="scoreType")
    score_value: float = Field(alias="scoreValue")
    percentile: float | None = None
    category: str
    calculated_at: str = Field(alias="calculatedAt")
    source_data: dict[str, Any] | None = Field(default=None, alias="sourceData")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class AthleteScoresResponse(BaseModel):
    scores: list[AthleteScoreRecord]


class NotificationRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    notification_id: str = Field(alias="notificationId")
    recipient_email: str = Field(alias="recipientEmail")
    recipient_role: str = Field(alias="recipientRole")
    title: str
    message: str
    type: str
    entity_id: str | None = Field(default=None, alias="entityId")
    read_at: str | None = Field(default=None, alias="readAt")
    created_at: str = Field(alias="createdAt")


class NotificationsResponse(BaseModel):
    notifications: list[NotificationRecord]


class FeedbackRequestCreateInput(BaseModel):
    athlete_id: str = Field(alias="athleteId", min_length=1)
    session_id: str = Field(alias="sessionId", min_length=1)
    coach_id: str = Field(alias="coachId", min_length=1)


class FeedbackRequestCreateResponse(BaseModel):
    request_id: str = Field(alias="requestId")
    status: Literal["PENDING"]
    message: str


class CoachNotificationItem(BaseModel):
    notification_id: str = Field(alias="notificationId")
    type: str
    athlete_id: str | None = Field(default=None, alias="athleteId")
    athlete_name: str | None = Field(default=None, alias="athleteName")
    session_id: str | None = Field(default=None, alias="sessionId")
    request_id: str | None = Field(default=None, alias="requestId")
    message: str
    action_url: str | None = Field(default=None, alias="actionUrl")
    created_at: str = Field(alias="createdAt")
    is_read: bool = Field(alias="isRead")


class CoachNotificationsResponse(BaseModel):
    notifications: list[CoachNotificationItem]
    unread_count: int = Field(alias="unreadCount")


class NotificationMarkReadResponse(BaseModel):
    notification_id: str = Field(alias="notificationId")
    is_read: bool = Field(alias="isRead")
    read_at: str | None = Field(default=None, alias="readAt")


class V1CoachFeedbackInput(BaseModel):
    request_id: str = Field(alias="requestId", min_length=1)
    athlete_id: str = Field(alias="athleteId", min_length=1)
    note: str = Field(min_length=2, max_length=500)
    recommendation: str = Field(min_length=2, max_length=500)
    status: Literal["Needs Attention", "Progressing", "Strong"] = "Progressing"


class PendingAssignmentItem(BaseModel):
    request_id: str = Field(alias="requestId")
    athlete_id: str = Field(alias="athleteId")
    athlete_name: str = Field(alias="athleteName")
    assigned_coach_id: str | None = Field(default=None, alias="assignedCoachId")
    status: Literal["PENDING", "ASSIGNED", "REJECTED"]
    notes: str | None = None
    requested_at: str | None = Field(default=None, alias="requestedAt")


class PendingAssignmentsResponse(BaseModel):
    requests: list[PendingAssignmentItem]


class AssignAthleteInput(BaseModel):
    request_id: str = Field(alias="requestId", min_length=1)
    athlete_id: str = Field(alias="athleteId", min_length=1)
    assigned_coach_id: str = Field(alias="assignedCoachId", min_length=1)
    notes: str | None = Field(default=None, max_length=500)


class AssignAthleteResponse(BaseModel):
    success: bool
    assignment_id: str = Field(alias="assignmentId")


class CoachOptionItem(BaseModel):
    coach_id: str = Field(alias="coachId")
    coach_name: str = Field(alias="coachName")
    coach_id_text: str | None = Field(default=None, alias="coachIdText")
    specialization: str | None = None


class CoachOptionsResponse(BaseModel):
    coaches: list[CoachOptionItem]


class AthleteAssignmentStatusResponse(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    status: Literal["PENDING", "ASSIGNED", "REJECTED", "UNASSIGNED"]
    assigned_coach_id: str | None = Field(default=None, alias="assignedCoachId")
    assigned_coach_name: str | None = Field(default=None, alias="assignedCoachName")
    requested_at: str | None = Field(default=None, alias="requestedAt")
    assigned_at: str | None = Field(default=None, alias="assignedAt")


class CoachDashboardAthleteRow(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    athlete_name: str = Field(alias="athleteName")
    sport: str | None = None
    discipline: str | None = None
    gender: str | None = None
    age: int | None = None
    score: float | None = None
    readiness_score: float | None = Field(default=None, alias="readinessScore")
    focus_score: float | None = Field(default=None, alias="focusScore")
    discipline_score: float | None = Field(default=None, alias="disciplineScore")
    score_category: str = Field(alias="scoreCategory")
    status: Literal["Strong", "Stable", "Needs Attention", "At Risk"] = "Stable"
    trend: Literal["Improving", "Declining", "Stable"] = "Stable"
    latest_stress: float | None = Field(default=None, alias="latestStress")
    resting_hr: float | None = Field(default=None, alias="restingHr")
    hrv_indicator: float | None = Field(default=None, alias="hrvIndicator")
    fatigue_score: float | None = Field(default=None, alias="fatigueScore")
    latest_recovery: float | None = Field(default=None, alias="latestRecovery")
    sleep_hours: float | None = Field(default=None, alias="sleepHours")
    last_session_date: str | None = Field(default=None, alias="lastSessionDate")
    risk_score: float = Field(default=0, alias="riskScore")
    risk_reasons: list[str] = Field(default_factory=list, alias="riskReasons")
    suggested_action: str | None = Field(default=None, alias="suggestedAction")


class CoachDashboardRiskItem(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    athlete_name: str = Field(alias="athleteName")
    severity: Literal["High", "Medium", "Low"]
    reasons: list[str]
    suggested_action: str = Field(alias="suggestedAction")


class CoachDashboardInsightItem(BaseModel):
    title: str
    insight_text: str = Field(alias="insightText")
    category: str
    score: float | None = None
    priority: Literal["High", "Medium", "Low"] = "Medium"


class CoachDashboardScatterPoint(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    athlete_name: str = Field(alias="athleteName")
    performance: float | None = None
    stress: float | None = None
    fatigue: float | None = None
    readiness: float | None = None
    sleep: float | None = None
    resting_hr: float | None = Field(default=None, alias="restingHr")
    hrv_indicator: float | None = Field(default=None, alias="hrvIndicator")
    focus: float | None = None
    consistency: float | None = None


class CoachDashboardV1Payload(BaseModel):
    coach_id: str = Field(alias="coachId")
    totals: dict[str, float | int | None]
    average_score: float | None = Field(default=None, alias="averageScore")
    average_readiness: float | None = Field(default=None, alias="averageReadiness")
    average_fatigue: float | None = Field(default=None, alias="averageFatigue")
    average_stress: float | None = Field(default=None, alias="averageStress")
    score_distribution: dict[str, int] = Field(alias="scoreDistribution")
    athletes: list[CoachDashboardAthleteRow]
    top_performers: list[CoachDashboardAthleteRow] = Field(default_factory=list, alias="topPerformers")
    most_disciplined: list[CoachDashboardAthleteRow] = Field(default_factory=list, alias="mostDisciplined")
    healthy_focused: list[CoachDashboardAthleteRow] = Field(default_factory=list, alias="healthyFocused")
    risk_queue: list[CoachDashboardRiskItem] = Field(default_factory=list, alias="riskQueue")
    mapping: dict[str, list[CoachDashboardScatterPoint]] = Field(default_factory=dict)
    insights: list[CoachDashboardInsightItem] = Field(default_factory=list)
    alerts: list[str]


class CoachDashboardV1Response(BaseModel):
    dashboard: CoachDashboardV1Payload


class AthleteFullProfileV1Response(BaseModel):
    athlete: dict[str, Any]


class CoachDashboardSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_assigned_athletes: int = Field(alias="totalAssignedAthletes")
    new_registrations: int = Field(alias="newRegistrations")
    active_athletes: int = Field(alias="activeAthletes")
    inactive_athletes: int = Field(alias="inactiveAthletes")
    average_score: float | None = Field(default=None, alias="averageScore")
    highest_performing: list[CoachAthleteListItem] = Field(alias="highestPerforming")
    lowest_performing: list[CoachAthleteListItem] = Field(alias="lowestPerforming")
    score_distribution: dict[str, int] = Field(alias="scoreDistribution")
    recent_activity: list[NotificationRecord] = Field(alias="recentActivity")
    alerts: list[str]


class CoachDashboardSummaryResponse(BaseModel):
    summary: CoachDashboardSummary


class MobileAthleteRegistrationInput(BaseModel):
    athlete_id: str | None = Field(default=None, alias="athleteId")
    full_name: str = Field(alias="fullName", min_length=2, max_length=100)
    email: EmailStr
    age: int = Field(ge=5, le=80)
    gender: Literal["Male", "Female", "Other"]
    phone: str = Field(min_length=7, max_length=20)
    sport: str | None = Field(default=None, max_length=50)
    focus_area: str | None = Field(default=None, alias="focusArea", max_length=80)
    assigned_coach_email: EmailStr | None = Field(default=None, alias="assignedCoachEmail")
    assigned_coach_id: str | None = Field(default=None, alias="assignedCoachId", min_length=1, max_length=80)
    selected_coach_id: str | None = Field(default=None, alias="selectedCoachId", min_length=1, max_length=80)
    profile_completion_status: Literal["incomplete", "partial", "complete"] = Field(default="partial", alias="profileCompletionStatus")


class MobileAthleteRegistrationResponse(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    assigned_coach_email: str | None = Field(default=None, alias="assignedCoachEmail")
    notification_created: bool = Field(alias="notificationCreated")
    success: bool


class MobileAthleteProfileUpsertInput(BaseModel):
    full_name: str | None = Field(default=None, alias="fullName", min_length=2, max_length=100)
    age: int | None = Field(default=None, ge=5, le=80)
    gender: Literal["Male", "Female", "Other"] | None = None
    city: str | None = Field(default=None, min_length=2, max_length=80)
    discipline: str | None = Field(default=None, min_length=2, max_length=80)
    experience_level: Literal["Beginner", "Intermediate", "Advanced"] | None = Field(default=None, alias="experienceLevel")
    years_shooting: int | None = Field(default=None, alias="yearsShooting", ge=0, le=80)
    academy_club: str | None = Field(default=None, alias="academyClub", max_length=120)
    average_practice_score: float | None = Field(default=None, alias="averagePracticeScore", ge=0)
    target_score: float | None = Field(default=None, alias="targetScore", ge=0)
    performance_factors: list[str] | None = Field(default=None, alias="performanceFactors")
    goal_30_days: str | None = Field(default=None, alias="goal30Days", max_length=500)
    goal_6_months: str | None = Field(default=None, alias="goal6Months", max_length=500)
    polar_linked: bool | None = Field(default=None, alias="polarLinked")
    polar_device_id: str | None = Field(default=None, alias="polarDeviceId", max_length=120)


class MobileAthleteProfileRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    athlete_id: str = Field(alias="athleteId")
    full_name: str | None = Field(default=None, alias="fullName")
    age: int | None = None
    gender: str | None = None
    city: str | None = None
    discipline: str | None = None
    experience_level: str | None = Field(default=None, alias="experienceLevel")
    years_shooting: int | None = Field(default=None, alias="yearsShooting")
    academy_club: str | None = Field(default=None, alias="academyClub")
    average_practice_score: float | None = Field(default=None, alias="averagePracticeScore")
    target_score: float | None = Field(default=None, alias="targetScore")
    performance_factors: list[str] = Field(default_factory=list, alias="performanceFactors")
    goal_30_days: str | None = Field(default=None, alias="goal30Days")
    goal_6_months: str | None = Field(default=None, alias="goal6Months")
    polar_linked: bool = Field(default=False, alias="polarLinked")
    polar_device_id: str | None = Field(default=None, alias="polarDeviceId")
    resting_hr_baseline: int | None = Field(default=None, alias="restingHrBaseline")
    hrv_baseline_ms: int | None = Field(default=None, alias="hrvBaselineMs")
    onboarding_status: str = Field(alias="onboardingStatus")
    profile_completion_status: str = Field(alias="profileCompletionStatus")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class MobileAthleteProfileResponse(BaseModel):
    profile: MobileAthleteProfileRecord


class MobileBaselineInput(BaseModel):
    resting_hr_baseline: int = Field(alias="restingHrBaseline", ge=30, le=220)
    hrv_baseline_ms: int | None = Field(default=None, alias="hrvBaselineMs", ge=1, le=300)
    polar_linked: bool = Field(default=True, alias="polarLinked")
    polar_device_id: str | None = Field(default=None, alias="polarDeviceId", max_length=120)


class MobileDailyCheckinInput(BaseModel):
    checkin_date: date | None = Field(default=None, alias="checkinDate")
    mood: Literal["Trouble", "Poor", "Okay", "Good", "Great"]
    energy_level: int = Field(alias="energyLevel", ge=1, le=10)
    sleep_band: Literal["<5h", "5-6h", "6-7h", "7-8h", "8h+"] | None = Field(default=None, alias="sleepBand")
    sleep_hours: float | None = Field(default=None, alias="sleepHours", ge=0, le=14)
    tags: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=500)


class MobileDailyCheckinRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    checkin_id: str = Field(alias="checkinId")
    athlete_id: str = Field(alias="athleteId")
    checkin_date: date = Field(alias="checkinDate")
    mood: str
    energy_level: int = Field(alias="energyLevel")
    sleep_band: str | None = Field(default=None, alias="sleepBand")
    sleep_hours: float | None = Field(default=None, alias="sleepHours")
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class MobileDailyCheckinResponse(BaseModel):
    checkin: MobileDailyCheckinRecord


class MobileAthleteHomeResponse(BaseModel):
    home: dict[str, Any]


class MobileTrainingSessionCreateInput(BaseModel):
    range_type: Literal["Paper", "Electronic"] = Field(alias="rangeType")
    session_type: Literal["Scoring", "Grouping", "Dry Fire"] = Field(alias="sessionType")
    planned_shots: int = Field(alias="plannedShots", ge=1, le=300)
    discipline: str | None = Field(default=None, max_length=80)
    intention: str | None = Field(default=None, max_length=500)
    visualization: str | None = Field(default=None, max_length=500)
    body_scan_completed: bool = Field(default=False, alias="bodyScanCompleted")
    start_now: bool = Field(default=False, alias="startNow")


class MobileTrainingSeriesInput(BaseModel):
    series_number: int = Field(alias="seriesNumber", ge=1, le=30)
    shots: list[Any] = Field(min_length=1, max_length=30)
    avg_heart_rate: float | None = Field(default=None, alias="avgHeartRate", ge=30, le=220)


class MobileSessionCompleteInput(BaseModel):
    duration_seconds: int | None = Field(default=None, alias="durationSeconds", ge=0)
    avg_heart_rate: float | None = Field(default=None, alias="avgHeartRate", ge=30, le=220)
    peak_heart_rate: float | None = Field(default=None, alias="peakHeartRate", ge=30, le=240)
    fatigue: str | None = Field(default=None, max_length=40)
    recovery: str | None = Field(default=None, max_length=40)


class MobileSessionReflectionInput(BaseModel):
    mood: Literal["Trouble", "Poor", "Okay", "Good", "Great"]
    what_worked: str | None = Field(default=None, alias="whatWorked", max_length=1000)
    what_didnt: str | None = Field(default=None, alias="whatDidnt", max_length=1000)
    voice_note_url: str | None = Field(default=None, alias="voiceNoteUrl", max_length=500)
    self_rating: int | None = Field(default=None, alias="selfRating", ge=1, le=10)
    fatigue_level: int | None = Field(default=None, alias="fatigueLevel", ge=1, le=10)


class MobileTrainingSessionResponse(BaseModel):
    session: dict[str, Any]


class MobileTrainingSessionsResponse(BaseModel):
    sessions: list[dict[str, Any]]


class MobileTrainingSeriesResponse(BaseModel):
    series: dict[str, Any]
    summary: dict[str, Any]


class MobileSessionReflectionResponse(BaseModel):
    reflection: dict[str, Any]
    summary: dict[str, Any]


class MobileSessionSummaryResponse(BaseModel):
    summary: dict[str, Any]


class AthleteMasterInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=5, le=80)
    gender: Literal["Male", "Female", "Other"]
    height_cm: float = Field(alias="heightCm", gt=0, le=260)
    weight_kg: float = Field(alias="weightKg", gt=0, le=300)
    academy_id: str = Field(alias="academyId", min_length=1, max_length=50)
    coach_id: str = Field(alias="coachId", min_length=1, max_length=80)
    contact_number: str = Field(alias="contactNumber", min_length=7, max_length=20)
    email: EmailStr


class FamilyDetailsInput(BaseModel):
    mother_name: str = Field(alias="motherName", min_length=2, max_length=100)
    father_name: str = Field(alias="fatherName", min_length=2, max_length=100)
    mother_occupation: str = Field(alias="motherOccupation", min_length=2, max_length=100)
    father_occupation: str = Field(alias="fatherOccupation", min_length=2, max_length=100)
    education_level: str = Field(alias="educationLevel", min_length=2, max_length=100)
    sibling_details: str = Field(alias="siblingDetails", min_length=2, max_length=250)
    family_conservative: Literal["Yes", "No"] = Field(alias="familyConservative")
    discipline_level: str = Field(alias="disciplineLevel", min_length=2, max_length=100)
    health_conditions: str = Field(alias="healthConditions", min_length=2, max_length=250)
    father_contact_number: str = Field(alias="fatherContactNumber", min_length=7, max_length=20)
    mother_contact_number: str = Field(alias="motherContactNumber", min_length=7, max_length=20)
    parent_email: EmailStr = Field(alias="parentEmail")
    comments: str = Field(min_length=2, max_length=500)


class AthleteProfileInput(BaseModel):
    athlete_class: str = Field(alias="class", min_length=1, max_length=30)
    school_name: str = Field(alias="schoolName", min_length=2, max_length=150)
    diet_type: Literal["Veg", "Non-Veg", "Mixed"] = Field(alias="dietType")
    outside_food_frequency: Literal["Rare", "Weekly", "Frequent"] = Field(alias="outsideFoodFrequency")
    sleep_time: str = Field(alias="sleepTime", min_length=1, max_length=10)
    wake_time: str = Field(alias="wakeTime", min_length=1, max_length=10)
    friend_circle: str = Field(alias="friendCircle", min_length=2, max_length=250)
    anger_pattern: str = Field(alias="angerPattern", min_length=2, max_length=250)
    sadness_pattern: str = Field(alias="sadnessPattern", min_length=2, max_length=250)
    academic_performance: str = Field(alias="academicPerformance", min_length=2, max_length=100)
    reason_for_shooting: str = Field(alias="reasonForShooting", min_length=2, max_length=250)
    athlete_goal: str = Field(alias="athleteGoal", min_length=2, max_length=250)


class SessionLogInput(BaseModel):
    coach_id: str = Field(alias="coachId", min_length=1, max_length=80)
    session_date: date = Field(alias="sessionDate")
    start_time: str = Field(alias="startTime", min_length=1, max_length=10)
    end_time: str = Field(alias="endTime", min_length=1, max_length=10)
    training_type: Literal["Shooting", "Fitness", "Mental", "Recovery"] = Field(alias="trainingType")
    location: str = Field(min_length=2, max_length=120)
    notes: str = Field(min_length=2, max_length=500)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration_minutes(self) -> int:
        start = datetime.strptime(self.start_time, "%H:%M")
        end = datetime.strptime(self.end_time, "%H:%M")
        minutes = int((end - start).total_seconds() // 60)
        if minutes <= 0:
            raise ValueError("End time must be after start time.")
        return minutes


class PhysiologyDataInput(BaseModel):
    recorded_date: date = Field(alias="recordedDate")
    resting_heart_rate: int = Field(alias="restingHeartRate", ge=40, le=200)
    avg_heart_rate: int = Field(alias="avgHeartRate", ge=40, le=200)
    spo2: int = Field(ge=80, le=100)
    breathing_rate: int = Field(alias="breathingRate", ge=1, le=60)
    sleep_hours: float = Field(alias="sleepHours", ge=0, le=12)
    recovery_score: int = Field(alias="recoveryScore", ge=0, le=100)
    stress_score: int = Field(alias="stressScore", ge=0, le=100)
    fatigue_level: int = Field(alias="fatigueLevel", ge=0, le=10)
    remarks: str = Field(min_length=2, max_length=500)


class PsychologyAnswerInput(BaseModel):
    question_id: str = Field(alias="questionId", min_length=1, max_length=20)
    answer_text: str = Field(alias="answerText", min_length=1, max_length=500)
    answer_score: int | None = Field(default=None, alias="answerScore", ge=1, le=10)


class PsychologyQuestionRecord(BaseModel):
    question_id: str = Field(alias="questionId")
    question_text: str = Field(alias="questionText")
    category: str
    question_type: str = Field(alias="questionType")


class PsychologyQuestionsResponse(BaseModel):
    questions: list[PsychologyQuestionRecord]


class AthleteIntakeRequest(BaseModel):
    athlete_master: AthleteMasterInput = Field(alias="athleteMaster")
    family_details: FamilyDetailsInput = Field(alias="familyDetails")
    athlete_profile: AthleteProfileInput = Field(alias="athleteProfile")
    sessions_log: SessionLogInput = Field(alias="sessionsLog")
    physiology_data: PhysiologyDataInput = Field(alias="physiologyData")
    psychology_responses: list[PsychologyAnswerInput] = Field(alias="psychologyResponses", min_length=1)


class AthleteIntakeResponse(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    session_id: str = Field(alias="sessionId")
    success: bool


class PhoneOtpSendRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20)


class PhoneOtpSendResponse(BaseModel):
    success: bool
    message: str


class PhoneOtpVerifyRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20)
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class PhoneOtpVerifyResponse(BaseModel):
    athlete_id: str = Field(alias="athleteId")
    success: bool


def create_user_record(
    *,
    email: str,
    full_name: str,
    password: str,
    role: Literal["coach", "student"],
    coach_code: str | None = None,
    assignment_status: Literal["unassigned", "pending", "assigned"] | None = None,
    assigned_coach_email: str | None = None,
    assigned_coach_name: str | None = None,
    requested_coach_email: str | None = None,
    requested_coach_name: str | None = None,
    requested_coach_code: str | None = None,
    coach_request_sent_at: str | None = None,
    sport: str | None = None,
    focus_area: str | None = None,
    date_of_birth: str | None = None,
    performance_score: int | None = None,
) -> UserRecord:
    salt = generate_salt()
    return UserRecord(
        email=email.lower(),
        full_name=full_name,
        role=role,
        salt=salt,
        password_hash=hash_password(password, salt),
        coach_code=coach_code,
        assignment_status=assignment_status or ("assigned" if assigned_coach_email else "unassigned"),
        assigned_coach_email=assigned_coach_email,
        assigned_coach_name=assigned_coach_name,
        requested_coach_email=requested_coach_email,
        requested_coach_name=requested_coach_name,
        requested_coach_code=requested_coach_code,
        coach_request_sent_at=coach_request_sent_at,
        sport=sport,
        focus_area=focus_area,
        date_of_birth=date_of_birth,
        performance_score=performance_score,
    )


def serialize_user_row(row: dict[str, Any]) -> UserRecord:
    assignment_status = row.get("assignment_status")
    if assignment_status not in {"unassigned", "pending", "assigned"}:
        assignment_status = "assigned" if row.get("assigned_coach_email") else "pending" if row.get("requested_coach_email") else "unassigned"

    return UserRecord(
        email=row["email"],
        full_name=row["full_name"],
        role=row["role"],
        salt=row["salt"],
        password_hash=row["password_hash"],
        coach_code=row.get("coach_code"),
        assignment_status=assignment_status,
        assigned_coach_email=row.get("assigned_coach_email"),
        assigned_coach_name=row.get("assigned_coach_name"),
        requested_coach_email=row.get("requested_coach_email"),
        requested_coach_name=row.get("requested_coach_name"),
        requested_coach_code=row.get("requested_coach_code"),
        coach_request_sent_at=(
            str(row["coach_request_sent_at"]) if row.get("coach_request_sent_at") else None
        ),
        sport=row.get("sport"),
        focus_area=row.get("focus_area"),
        date_of_birth=(str(row["date_of_birth"]) if row.get("date_of_birth") else None),
        performance_score=row.get("performance_score"),
    )


def to_user_row(user: UserRecord) -> dict[str, Any]:
    return {
        "email": user.email.lower(),
        "full_name": user.full_name,
        "role": user.role,
        "salt": user.salt,
        "password_hash": user.password_hash,
        "coach_code": user.coach_code,
        "assignment_status": user.assignment_status,
        "assigned_coach_email": user.assigned_coach_email,
        "assigned_coach_name": user.assigned_coach_name,
        "requested_coach_email": user.requested_coach_email,
        "requested_coach_name": user.requested_coach_name,
        "requested_coach_code": user.requested_coach_code,
        "coach_request_sent_at": user.coach_request_sent_at,
        "sport": user.sport,
        "focus_area": user.focus_area,
        "date_of_birth": user.date_of_birth,
        "performance_score": user.performance_score,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_seed_users() -> list[UserRecord]:
    users: list[UserRecord] = []
    if settings.default_password:
        users.append(
            create_user_record(
                email=settings.default_email.lower(),
                full_name=settings.default_full_name,
                password=settings.default_password,
                role="coach",
                coach_code=settings.default_coach_code,
            )
        )
    if settings.admin_password:
        users.append(
            create_user_record(
                email=ADMIN_EMAIL,
                full_name="HamsaTech Admin",
                password=settings.admin_password,
                role="coach",
                coach_code="ADMIN-COACH-001",
            )
        )
    if settings.demo_student_password:
        demo_students = [
            ("ava.student@hamsatech.ai", "Ava Martinez", "Air Rifle", "Footwork and recovery", "2008-04-14", 91),
            ("leo.student@hamsatech.ai", "Leo Jackson", "Air Pistol", "Endurance pacing", "2006-09-02", 88),
            ("maya.student@hamsatech.ai", "Maya Chen", "Air Rifle", "Vertical leap and mobility", "2007-01-27", 94),
        ]
        users.extend(
            create_user_record(
                email=email,
                full_name=full_name,
                password=settings.demo_student_password,
                role="student",
                assigned_coach_email=settings.default_email.lower(),
                assigned_coach_name=settings.default_full_name,
                sport=sport,
                focus_area=focus_area,
                date_of_birth=date_of_birth,
                performance_score=performance_score,
            )
            for email, full_name, sport, focus_area, date_of_birth, performance_score in demo_students
        )
    return users
def build_seed_users() -> list[UserRecord]:
    users: list[UserRecord] = []
    if settings.default_password:
        users.append(
            create_user_record(
                email=settings.default_email.lower(),
                full_name=settings.default_full_name,
                password=settings.default_password,
                role="coach",
                coach_code=settings.default_coach_code,
            )
        )
    if settings.admin_password:
        users.append(
            create_user_record(
                email=ADMIN_EMAIL,
                full_name="HamsaTech Admin",
                password=settings.admin_password,
                role="coach",
                coach_code="ADMIN-COACH-001",
            )
        )
    if settings.demo_student_password:
        demo_students = [
            ("ava.student@hamsatech.ai", "Ava Martinez", "Air Rifle", "Footwork and recovery", "2008-04-14", 91),
            ("leo.student@hamsatech.ai", "Leo Jackson", "Air Pistol", "Endurance pacing", "2006-09-02", 88),
            ("maya.student@hamsatech.ai", "Maya Chen", "Air Rifle", "Vertical leap and mobility", "2007-01-27", 94),
        ]
        users.extend(
            create_user_record(
                email=email,
                full_name=full_name,
                password=settings.demo_student_password,
                role="student",
                assigned_coach_email=settings.default_email.lower(),
                assigned_coach_name=settings.default_full_name,
                sport=sport,
                focus_area=focus_area,
                date_of_birth=date_of_birth,
                performance_score=performance_score,
            )
            for email, full_name, sport, focus_area, date_of_birth, performance_score in demo_students
        )
    return users


def to_public_user(user: UserRecord) -> AuthenticatedUser:
    assigned_coach_code: str | None = None
    if user.role == "student" and user.assigned_coach_email:
        assigned_coach = get_user_by_email(user.assigned_coach_email)
        assigned_coach_code = assigned_coach.coach_code if assigned_coach else None

    return AuthenticatedUser(
        email=user.email,
        fullName=user.full_name,
        role=user.role,
        coachCode=user.coach_code,
        assignmentStatus=user.assignment_status,
        assignedCoachCode=assigned_coach_code,
        assignedCoachEmail=user.assigned_coach_email,
        assignedCoachName=user.assigned_coach_name,
        requestedCoachCode=user.requested_coach_code,
        requestedCoachEmail=user.requested_coach_email,
        requestedCoachName=user.requested_coach_name,
        sport=user.sport,
        focusArea=user.focus_area,
        dateOfBirth=user.date_of_birth,
        performanceScore=user.performance_score,
    )


def to_student_profile(user: UserRecord) -> StudentProfile:
    return StudentProfile(
        email=user.email,
        fullName=user.full_name,
        assignedCoachEmail=user.assigned_coach_email,
        assignedCoachName=user.assigned_coach_name,
        sport=user.sport or "General Training",
        focusArea=user.focus_area or "Performance consistency",
        dateOfBirth=user.date_of_birth or "2007-01-01",
        performanceScore=user.performance_score or 85,
    )


def to_assignment_request_record(user: UserRecord) -> CoachAssignmentRequestRecord:
    return CoachAssignmentRequestRecord(
        email=user.email,
        fullName=user.full_name,
        sport=user.sport or "General Training",
        focusArea=user.focus_area or "Performance consistency",
        requestedCoachCode=user.requested_coach_code or "",
        requestedCoachName=user.requested_coach_name or "Requested Coach",
        requestedAt=user.coach_request_sent_at,
        assignmentStatus="pending",
    )


def get_user_by_email(email: str) -> UserRecord | None:
    supabase = ensure_supabase()
    result = supabase.table("App_Users").select("*").eq("email", email.lower()).limit(1).execute()
    row = (result.data or [None])[0]
    return serialize_user_row(row) if row else None


def upsert_user(user: UserRecord) -> UserRecord:
    supabase = ensure_supabase()
    supabase.table("App_Users").upsert(to_user_row(user), on_conflict="email").execute()
    stored_user = get_user_by_email(user.email)
    if not stored_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to persist app user.",
        )
    return stored_user


def ensure_seed_data() -> None:
    supabase = ensure_supabase()
    rows = [to_user_row(user) for user in build_seed_users()]
    if not rows:
        return
    rows = [to_user_row(user) for user in build_seed_users()]
    if not rows:
        return
    supabase.table("App_Users").upsert(rows, on_conflict="email").execute()


def assign_existing_records_to_default_coach_for_testing() -> None:
    # Temporary local/testing mapper: split existing athletes across first two domain coaches.
    supabase = ensure_supabase()
    coaches = [row.get("coach_id") for row in get_domain_coaches() if row.get("coach_id")]
    if not coaches:
        return
    if len(coaches) == 1:
        coaches = [coaches[0], coaches[0]]

    try:
        athlete_rows = supabase.table(APP_TABLES["athletes"]).select("*").execute().data or []
        athlete_rows.sort(key=lambda row: str(row.get("athlete_id") or ""))
        for idx, athlete in enumerate(athlete_rows):
            assigned_coach_id = coaches[idx % 2]
            supabase.table(APP_TABLES["athletes"]).update(
                {
                    "coach_id": assigned_coach_id,
                    "updated_by": "temporary-default-coach-mapper",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            ).eq("athlete_id", athlete["athlete_id"]).execute()
    except Exception:
        return


def get_default_domain_coach_id() -> str | None:
    try:
        supabase = ensure_supabase()
        rows = safe_table_rows(
            "coaches",
            supabase.table("coaches").select("coach_id,coach_id_text,created_at").order("created_at"),
        )
        if not rows:
            return None
        preferred = next((row for row in rows if str(row.get("coach_id_text") or "").upper() == "C001"), None)
        return str((preferred or rows[0]).get("coach_id") or "")
    except Exception:
        return None


def get_domain_coaches() -> list[dict[str, Any]]:
    supabase = ensure_supabase()
    rows = safe_table_rows(
        "coaches",
        supabase.table("coaches").select("coach_id,coach_name,coach_id_text,created_at").order("created_at"),
    )
    return rows


def get_secondary_domain_coach_id() -> str | None:
    rows = get_domain_coaches()
    if len(rows) < 2:
        return rows[0].get("coach_id") if rows else None
    preferred = next((row for row in rows if str(row.get("coach_id_text") or "").upper() == "C002"), None)
    return str((preferred or rows[1]).get("coach_id") or "")


def resolve_dashboard_coach_key(coach_user: UserRecord) -> str | None:
    # App_Users identifies coach by email, while athletes table uses domain coach UUID.
    email = coach_user.email.lower()
    if email == ADMIN_EMAIL:
        return get_secondary_domain_coach_id()
    if coach_user.email.lower() == settings.default_email.lower():
        return get_default_domain_coach_id()
    code = (coach_user.coach_code or "").upper().strip()
    suffix = code.split("-")[-1] if code else ""
    if suffix.isdigit():
        target = f"C{int(suffix):03d}"
        rows = get_domain_coaches()
        match = next((row for row in rows if str(row.get("coach_id_text") or "").upper() == target), None)
        if match:
            return str(match.get("coach_id") or "")
    return None


def ensure_coach_owns_coach_id(coach_user: UserRecord, coach_id: str) -> str:
    mapped = resolve_dashboard_coach_key(coach_user)
    if not mapped or str(mapped) != str(coach_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own coach notifications and feedback requests.",
        )
    return mapped


def resolve_domain_coach_id_for_email(email: str | None) -> str | None:
    if not email:
        return None
    coach = get_user_by_email(email.lower())
    if coach and coach.role == "coach":
        return resolve_dashboard_coach_key(coach)
    if email.lower() == settings.default_email.lower():
        return get_default_domain_coach_id()
    if email.lower() == ADMIN_EMAIL:
        return get_secondary_domain_coach_id()
    return None


def get_domain_coach_email(coach_id: str | None) -> str | None:
    if not coach_id:
        return None
    if str(coach_id) == str(get_default_domain_coach_id()):
        return settings.default_email.lower()
    if str(coach_id) == str(get_secondary_domain_coach_id()):
        return ADMIN_EMAIL
    return None


def get_assignment_target_for_registration(payload: MobileAthleteRegistrationInput) -> tuple[str | None, str | None]:
    selected_coach_id = payload.selected_coach_id or payload.assigned_coach_id
    if selected_coach_id:
        return selected_coach_id, get_domain_coach_email(selected_coach_id)
    if payload.assigned_coach_email:
        coach_id = resolve_domain_coach_id_for_email(payload.assigned_coach_email)
        if coach_id:
            return coach_id, payload.assigned_coach_email.lower()
    default_coach_id = get_default_domain_coach_id()
    return default_coach_id, settings.default_email.lower() if default_coach_id else None


def create_assignment_request_for_athlete(
    *,
    athlete_id: str,
    athlete_name: str,
    target_coach_id: str | None,
    target_coach_email: str | None,
    notes: str,
) -> str | None:
    if not target_coach_id:
        return None
    supabase = ensure_supabase()
    existing = safe_table_rows(
        "assignment_requests",
        supabase.table("assignment_requests")
        .select("request_id")
        .eq("athlete_id", athlete_id)
        .eq("status", "PENDING")
        .limit(1),
    )
    if existing:
        return str(existing[0].get("request_id") or "")

    request_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("assignment_requests").insert(
        {
            "request_id": request_id,
            "athlete_id": athlete_id,
            "assigned_coach_id": target_coach_id,
            "status": "PENDING",
            "notes": notes,
            "requested_at": now,
        }
    ).execute()
    create_notification(
        recipient_email=target_coach_email or settings.default_email.lower(),
        recipient_role="coach",
        recipient_coach_id=target_coach_id,
        title="New athlete assignment request",
        message=f"{athlete_name} registered and needs coach assignment.",
        notification_type="ASSIGNMENT_REQUEST",
        entity_id=request_id,
        related_athlete_id=athlete_id,
        action_url="/coach/assignments/pending",
    )
    return request_id


def get_pending_or_assigned_coach_for_athlete(athlete_row: dict[str, Any]) -> str | None:
    assigned_coach_id = str(athlete_row.get("coach_id") or "").strip()
    if assigned_coach_id:
        return assigned_coach_id
    supabase = ensure_supabase()
    rows = safe_table_rows(
        "assignment_requests",
        supabase.table("assignment_requests")
        .select("assigned_coach_id")
        .eq("athlete_id", athlete_row.get("athlete_id"))
        .eq("status", "PENDING")
        .order("requested_at", desc=True)
        .limit(1),
    )
    if rows and rows[0].get("assigned_coach_id"):
        return str(rows[0].get("assigned_coach_id"))
    return None


def notify_coach_of_athlete_activity(
    *,
    athlete_row: dict[str, Any],
    title: str,
    message: str,
    notification_type: str,
    related_session_id: str | None = None,
    action_url: str | None = None,
) -> None:
    coach_id = get_pending_or_assigned_coach_for_athlete(athlete_row)
    if not coach_id:
        return
    create_notification(
        recipient_email=get_domain_coach_email(coach_id) or settings.default_email.lower(),
        recipient_role="coach",
        recipient_coach_id=coach_id,
        title=title,
        message=message,
        notification_type=notification_type,
        entity_id=str(athlete_row.get("athlete_id") or ""),
        related_athlete_id=str(athlete_row.get("athlete_id") or ""),
        related_session_id=related_session_id,
        action_url=action_url,
    )


def assign_existing_records_to_default_coach_for_testing() -> None:
    # Temporary local/testing mapper: split existing athletes across first two domain coaches.
    supabase = ensure_supabase()
    coaches = [row.get("coach_id") for row in get_domain_coaches() if row.get("coach_id")]
    if not coaches:
        return
    if len(coaches) == 1:
        coaches = [coaches[0], coaches[0]]

    try:
        athlete_rows = supabase.table(APP_TABLES["athletes"]).select("*").execute().data or []
        athlete_rows.sort(key=lambda row: str(row.get("athlete_id") or ""))
        for idx, athlete in enumerate(athlete_rows):
            assigned_coach_id = coaches[idx % 2]
            supabase.table(APP_TABLES["athletes"]).update(
                {
                    "coach_id": assigned_coach_id,
                    "updated_by": "temporary-default-coach-mapper",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            ).eq("athlete_id", athlete["athlete_id"]).execute()
    except Exception:
        return


def get_default_domain_coach_id() -> str | None:
    try:
        supabase = ensure_supabase()
        rows = safe_table_rows(
            "coaches",
            supabase.table("coaches").select("coach_id,coach_id_text,created_at").order("created_at"),
        )
        if not rows:
            return None
        preferred = next((row for row in rows if str(row.get("coach_id_text") or "").upper() == "C001"), None)
        return str((preferred or rows[0]).get("coach_id") or "")
    except Exception:
        return None


def get_domain_coaches() -> list[dict[str, Any]]:
    supabase = ensure_supabase()
    rows = safe_table_rows(
        "coaches",
        supabase.table("coaches").select("coach_id,coach_name,coach_id_text,created_at").order("created_at"),
    )
    return rows


def get_secondary_domain_coach_id() -> str | None:
    rows = get_domain_coaches()
    if len(rows) < 2:
        return rows[0].get("coach_id") if rows else None
    preferred = next((row for row in rows if str(row.get("coach_id_text") or "").upper() == "C002"), None)
    return str((preferred or rows[1]).get("coach_id") or "")


def resolve_dashboard_coach_key(coach_user: UserRecord) -> str | None:
    # App_Users identifies coach by email, while athletes table uses domain coach UUID.
    email = coach_user.email.lower()
    if email == ADMIN_EMAIL:
        return get_secondary_domain_coach_id()
    if coach_user.email.lower() == settings.default_email.lower():
        return get_default_domain_coach_id()
    code = (coach_user.coach_code or "").upper().strip()
    suffix = code.split("-")[-1] if code else ""
    if suffix.isdigit():
        target = f"C{int(suffix):03d}"
        rows = get_domain_coaches()
        match = next((row for row in rows if str(row.get("coach_id_text") or "").upper() == target), None)
        if match:
            return str(match.get("coach_id") or "")
    return None


def ensure_coach_owns_coach_id(coach_user: UserRecord, coach_id: str) -> str:
    mapped = resolve_dashboard_coach_key(coach_user)
    if not mapped or str(mapped) != str(coach_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own coach notifications and feedback requests.",
        )
    return mapped


def resolve_domain_coach_id_for_email(email: str | None) -> str | None:
    if not email:
        return None
    coach = get_user_by_email(email.lower())
    if coach and coach.role == "coach":
        return resolve_dashboard_coach_key(coach)
    if email.lower() == settings.default_email.lower():
        return get_default_domain_coach_id()
    if email.lower() == ADMIN_EMAIL:
        return get_secondary_domain_coach_id()
    return None


def get_domain_coach_email(coach_id: str | None) -> str | None:
    if not coach_id:
        return None
    if str(coach_id) == str(get_default_domain_coach_id()):
        return settings.default_email.lower()
    if str(coach_id) == str(get_secondary_domain_coach_id()):
        return ADMIN_EMAIL
    return None


def get_assignment_target_for_registration(payload: MobileAthleteRegistrationInput) -> tuple[str | None, str | None]:
    selected_coach_id = payload.selected_coach_id or payload.assigned_coach_id
    if selected_coach_id:
        return selected_coach_id, get_domain_coach_email(selected_coach_id)
    if payload.assigned_coach_email:
        coach_id = resolve_domain_coach_id_for_email(payload.assigned_coach_email)
        if coach_id:
            return coach_id, payload.assigned_coach_email.lower()
    default_coach_id = get_default_domain_coach_id()
    return default_coach_id, settings.default_email.lower() if default_coach_id else None


def create_assignment_request_for_athlete(
    *,
    athlete_id: str,
    athlete_name: str,
    target_coach_id: str | None,
    target_coach_email: str | None,
    notes: str,
) -> str | None:
    if not target_coach_id:
        return None
    supabase = ensure_supabase()
    existing = safe_table_rows(
        "assignment_requests",
        supabase.table("assignment_requests")
        .select("request_id")
        .eq("athlete_id", athlete_id)
        .eq("status", "PENDING")
        .limit(1),
    )
    if existing:
        return str(existing[0].get("request_id") or "")

    request_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("assignment_requests").insert(
        {
            "request_id": request_id,
            "athlete_id": athlete_id,
            "assigned_coach_id": target_coach_id,
            "status": "PENDING",
            "notes": notes,
            "requested_at": now,
        }
    ).execute()
    create_notification(
        recipient_email=target_coach_email or settings.default_email.lower(),
        recipient_role="coach",
        recipient_coach_id=target_coach_id,
        title="New athlete assignment request",
        message=f"{athlete_name} registered and needs coach assignment.",
        notification_type="ASSIGNMENT_REQUEST",
        entity_id=request_id,
        related_athlete_id=athlete_id,
        action_url="/coach/assignments/pending",
    )
    return request_id


def get_pending_or_assigned_coach_for_athlete(athlete_row: dict[str, Any]) -> str | None:
    assigned_coach_id = str(athlete_row.get("coach_id") or "").strip()
    if assigned_coach_id:
        return assigned_coach_id
    supabase = ensure_supabase()
    rows = safe_table_rows(
        "assignment_requests",
        supabase.table("assignment_requests")
        .select("assigned_coach_id")
        .eq("athlete_id", athlete_row.get("athlete_id"))
        .eq("status", "PENDING")
        .order("requested_at", desc=True)
        .limit(1),
    )
    if rows and rows[0].get("assigned_coach_id"):
        return str(rows[0].get("assigned_coach_id"))
    return None


def notify_coach_of_athlete_activity(
    *,
    athlete_row: dict[str, Any],
    title: str,
    message: str,
    notification_type: str,
    related_session_id: str | None = None,
    action_url: str | None = None,
) -> None:
    coach_id = get_pending_or_assigned_coach_for_athlete(athlete_row)
    if not coach_id:
        return
    create_notification(
        recipient_email=get_domain_coach_email(coach_id) or settings.default_email.lower(),
        recipient_role="coach",
        recipient_coach_id=coach_id,
        title=title,
        message=message,
        notification_type=notification_type,
        entity_id=str(athlete_row.get("athlete_id") or ""),
        related_athlete_id=str(athlete_row.get("athlete_id") or ""),
        related_session_id=related_session_id,
        action_url=action_url,
    )


def get_next_student_score() -> int:
    supabase = ensure_supabase()
    result = (
        supabase.table("App_Users")
        .select("performance_score")
        .eq("role", "student")
        .order("performance_score", desc=True)
        .limit(1)
        .execute()
    )
    top_row = (result.data or [None])[0]
    top_score = top_row.get("performance_score") if top_row else None
    return max(86, (top_score or 84) + 2)


def create_persistent_session(user_email: str) -> str:
    supabase = ensure_supabase()
    session_token = generate_session_token()
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=8)).isoformat()
    supabase.table("App_Sessions").insert(
        {
            "session_token": session_token,
            "user_email": user_email.lower(),
            "expires_at": expires_at,
        }
    ).execute()
    return session_token


def delete_persistent_session(session_token: str) -> None:
    supabase = ensure_supabase()
    supabase.table("App_Sessions").delete().eq("session_token", session_token).execute()


def list_students_for_coach(coach_email: str) -> list[UserRecord]:
    supabase = ensure_supabase()
    response = (
        supabase.table("App_Users")
        .select("*")
        .eq("role", "student")
        .eq("assigned_coach_email", coach_email.lower())
        .order("full_name")
        .execute()
    )
    return [serialize_user_row(row) for row in response.data or []]


def list_assignment_requests_for_coach(coach_email: str) -> list[UserRecord]:
    supabase = ensure_supabase()
    response = (
        supabase.table("App_Users")
        .select("*")
        .eq("role", "student")
        .eq("assignment_status", "pending")
        .eq("requested_coach_email", coach_email.lower())
        .order("coach_request_sent_at")
        .execute()
    )
    return [serialize_user_row(row) for row in response.data or []]


def get_primary_coach() -> UserRecord:
    coach = get_user_by_email(settings.default_email.lower())
    if coach and coach.role == "coach":
        return coach

    supabase = ensure_supabase()
    response = (
        supabase.table("App_Users")
        .select("*")
        .eq("role", "coach")
        .order("full_name")
        .limit(1)
        .execute()
    )
    coach_row = (response.data or [None])[0]
    primary_coach = serialize_user_row(coach_row) if coach_row else None
    if not primary_coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active coach profile is available yet.",
        )
    return primary_coach


def find_coach_by_code(coach_code: str) -> UserRecord:
    normalized_code = coach_code.strip().upper()
    supabase = ensure_supabase()
    response = (
        supabase.table("App_Users")
        .select("*")
        .eq("role", "coach")
        .eq("coach_code", normalized_code)
        .limit(1)
        .execute()
    )
    coach_row = (response.data or [None])[0]
    coach = serialize_user_row(coach_row) if coach_row else None
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach code not found. Please use a valid coach assignment code.",
        )
    return coach


def get_user_from_session(session_token: str | None) -> UserRecord:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    supabase = ensure_supabase()
    session_result = (
        supabase.table("App_Sessions")
        .select("session_token,user_email,expires_at")
        .eq("session_token", session_token)
        .limit(1)
        .execute()
    )
    session_row = (session_result.data or [None])[0]
    if not session_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    expires_at = datetime.fromisoformat(str(session_row["expires_at"]).replace("Z", "+00:00"))
    if expires_at < datetime.now(timezone.utc):
        delete_persistent_session(session_token)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    user = get_user_by_email(session_row["user_email"])

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return user


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.session_cookie_name,
        httponly=True,
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
    )


def ensure_coach_user(session_token: str | None) -> UserRecord:
    user = get_user_from_session(session_token)
    if user.role != "coach":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coaches can access assigned athlete records.",
        )
    return user


def get_authenticated_user(session_token: str | None) -> UserRecord:
    return get_user_from_session(session_token)


def ensure_supabase() -> Any:
    return get_supabase_admin_client()


def is_uuid_like(value: str) -> bool:
    return bool(UUID_LIKE_RE.match((value or "").strip()))


def supabase_error_code(exception: Exception) -> str | None:
    if isinstance(exception.args, tuple) and exception.args:
        payload = exception.args[0]
        if isinstance(payload, dict):
            code = payload.get("code")
            return str(code) if code else None
    return None


def resolve_athlete_row_by_identifier(supabase: Any, athlete_identifier: str) -> dict[str, Any] | None:
    identifier = (athlete_identifier or "").strip()
    if not identifier:
        return None

    candidates = ["athlete_id"]
    if not is_uuid_like(identifier):
        candidates.extend(["athlete_id_text", "athlete_code"])

    for column in candidates:
        try:
            result = supabase.table(APP_TABLES["athletes"]).select("*").eq(column, identifier).limit(1).execute()
            row = (result.data or [None])[0]
            if row:
                return row
        except Exception as exception:
            code = supabase_error_code(exception)
            message = str(exception)
            # If the backend schema uses UUID athlete ids, trying to filter by a non-UUID value
            # can trigger a Postgres cast error (22P02). In that case, keep trying alternative columns.
            if code == "22P02" or "invalid input syntax for type uuid" in message:
                continue
            continue

    return None


def coach_can_access_athlete(*, supabase: Any, coach_id: str | None, athlete_row: dict[str, Any]) -> bool:
    if not coach_id:
        return False

    athlete_coach_id = str(athlete_row.get("coach_id") or "")
    if athlete_coach_id and athlete_coach_id == str(coach_id):
        return True

    athlete_id = str(athlete_row.get("athlete_id") or "")
    if not athlete_id:
        return False

    # If the athlete is not assigned yet, allow access when there's a pending assignment request
    # for this coach (default coach flow).
    rows = safe_table_rows(
        "assignment_requests",
        supabase.table("assignment_requests")
        .select("request_id")
        .eq("athlete_id", athlete_id)
        .eq("status", "PENDING")
        .eq("assigned_coach_id", str(coach_id))
        .limit(1),
    )
    return bool(rows)


def is_admin_user(user: UserRecord) -> bool:
    return user.email.lower() == ADMIN_EMAIL


def ensure_admin_user(session_token: str | None) -> UserRecord:
    user = get_user_from_session(session_token)
    if not is_admin_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can manage coach profiles and assignments.",
        )
    return user


def safe_table_rows(table_name: str, query_builder: Any) -> list[dict[str, Any]]:
    try:
        response = query_builder.execute()
        return response.data or []
    except Exception:
        return []


def create_notification(
    *,
    recipient_email: str,
    recipient_role: str,
    title: str,
    message: str,
    notification_type: str,
    entity_id: str | None = None,
    recipient_coach_id: str | None = None,
    related_athlete_id: str | None = None,
    related_session_id: str | None = None,
    action_url: str | None = None,
) -> bool:
    try:
        supabase = ensure_supabase()
        now = datetime.now(timezone.utc).isoformat()
        row = {
            "notification_id": str(uuid4()),
            "recipient_email": recipient_email.lower(),
            "recipient_role": recipient_role,
            "title": title,
            "message": message,
            "type": notification_type,
            "entity_id": entity_id,
            "created_at": now,
        }
        if not recipient_coach_id and recipient_role == "coach":
            recipient_coach_id = resolve_domain_coach_id_for_email(recipient_email)
        enriched_row = {
            **row,
            "recipient_coach_id": recipient_coach_id,
            "notification_type": notification_type.upper(),
            "related_athlete_id": related_athlete_id or entity_id,
            "related_session_id": related_session_id,
            "action_url": action_url,
            "is_read": False,
        }
        try:
            supabase.table(APP_TABLES["notifications"]).insert(enriched_row).execute()
        except Exception:
            supabase.table(APP_TABLES["notifications"]).insert(row).execute()
        return True
    except Exception:
        return False


def write_audit_log(
    *,
    actor_email: str,
    action: str,
    entity_type: str,
    entity_id: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    try:
        supabase = ensure_supabase()
        supabase.table(APP_TABLES["audit_logs"]).insert(
            {
                "audit_id": str(uuid4()),
                "actor_email": actor_email.lower(),
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()
    except Exception:
        return


def ensure_coach_profile(user: UserRecord) -> CoachProfileRecord:
    supabase = ensure_supabase()
    coach_key = resolve_dashboard_coach_key(user)
    assigned_rows = safe_table_rows(
        APP_TABLES["athletes"],
        (supabase.table(APP_TABLES["athletes"]).select("athlete_id").eq("coach_id", coach_key) if coach_key else supabase.table(APP_TABLES["athletes"]).select("athlete_id").eq("coach_id", "__unmapped__")),
    )
    assigned_count = len(assigned_rows)
    domain_rows = get_domain_coaches()
    domain_row = next((row for row in domain_rows if str(row.get("coach_id") or "") == str(coach_key or "")), None)
    rows = safe_table_rows(
        APP_TABLES["coach_profiles"],
        supabase.table(APP_TABLES["coach_profiles"]).select("*").eq("email", user.email.lower()).limit(1),
    )
    row = rows[0] if rows else {}
    if not row:
        row = {
            "coach_id": coach_key or user.email.lower(),
            "name": (domain_row or {}).get("coach_name") or user.full_name,
            "email": user.email.lower(),
            "status": "active",
            "created_at": None,
            "updated_at": None,
        }

    # Dashboard endpoints are keyed by the domain coaches.coach_id UUID, not the
    # legacy coach_profiles.coach_id text value.
    resolved_coach_id = coach_key or row.get("coach_id") or user.email.lower()
    return CoachProfileRecord(
        coachId=str(resolved_coach_id),
        name=str(row.get("name") or (domain_row or {}).get("coach_name") or user.full_name),
        email=str(row.get("email") or user.email.lower()),
        phone=row.get("phone"),
        profileImage=row.get("profile_image"),
        specialization=row.get("specialization"),
        status=row.get("status") if row.get("status") in {"active", "inactive"} else "active",
        assignedAthletes=assigned_count,
        createdAt=str(row.get("created_at")) if row.get("created_at") else None,
        updatedAt=str(row.get("updated_at")) if row.get("updated_at") else None,
    )


def score_category(value: float) -> str:
    if value >= 80:
        return "Strong"
    if value >= 60:
        return "Progressing"
    return "Needs Attention"


def build_score_record(
    *,
    athlete_id: str,
    score_type: str,
    score_value: float,
    calculated_at: str,
    source_data: dict[str, Any] | None = None,
) -> AthleteScoreRecord:
    return AthleteScoreRecord(
        scoreId=f"{athlete_id}-{score_type}-{calculated_at}",
        athleteId=athlete_id,
        scoreType=score_type,
        scoreValue=round(score_value, 2),
        percentile=round(score_value, 2),
        category=score_category(score_value),
        calculatedAt=calculated_at,
        sourceData=source_data or {},
        createdAt=calculated_at,
        updatedAt=calculated_at,
    )


def fallback_scores_for_athlete(athlete_row: dict[str, Any]) -> list[AthleteScoreRecord]:
    athlete_id = str(athlete_row["athlete_id"])
    created_at = str(athlete_row.get("created_at") or datetime.now(timezone.utc).isoformat())
    email = str(athlete_row.get("email") or "").lower()
    app_user = get_user_by_email(email) if email else None
    base_score = float(app_user.performance_score if app_user and app_user.performance_score is not None else 75)

    latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [athlete_id], "recorded_date").get(athlete_id)
    scores = [
        build_score_record(
            athlete_id=athlete_id,
            score_type="overall",
            score_value=base_score,
            calculated_at=created_at,
            source_data={"source": "App_Users.performance_score"},
        )
    ]
    if latest_physiology:
        recovery = row_float(latest_physiology.get("recovery_score"), base_score)
        stress_control = 100 - row_float(latest_physiology.get("stress_score"), 50)
        fatigue = max(0, 100 - row_float(latest_physiology.get("fatigue_level"), 5) * 10)
        readiness = round((recovery + stress_control + fatigue) / 3, 2)
        calculated_at = str(latest_physiology.get("recorded_date") or latest_physiology.get("created_at") or created_at)
        scores.extend(
            [
                build_score_record(
                    athlete_id=athlete_id,
                    score_type="recovery",
                    score_value=recovery,
                    calculated_at=calculated_at,
                    source_data={"source": "Physiology_Data.recovery_score"},
                ),
                build_score_record(
                    athlete_id=athlete_id,
                    score_type="readiness",
                    score_value=readiness,
                    calculated_at=calculated_at,
                    source_data={"source": "Physiology_Data"},
                ),
                build_score_record(
                    athlete_id=athlete_id,
                    score_type="fatigue",
                    score_value=fatigue,
                    calculated_at=calculated_at,
                    source_data={"source": "Physiology_Data.fatigue_level"},
                ),
            ]
        )
    return scores


def get_scores_for_athlete(athlete_row: dict[str, Any]) -> list[AthleteScoreRecord]:
    supabase = ensure_supabase()
    athlete_id = str(athlete_row["athlete_id"])
    rows = safe_table_rows(
        APP_TABLES["athlete_scores"],
        supabase.table(APP_TABLES["athlete_scores"]).select("*").eq("athlete_id", athlete_id).order("calculated_at", desc=True),
    )
    if rows:
        scores = [
            AthleteScoreRecord(
                scoreId=str(row.get("score_id") or ""),
                athleteId=str(row.get("athlete_id") or ""),
                scoreType=str(row.get("score_type") or "overall"),
                scoreValue=row_float(row.get("score_value")),
                percentile=row_float(row.get("percentile")) if row.get("percentile") is not None else None,
                category=str(row.get("category") or score_category(row_float(row.get("score_value")))),
                calculatedAt=str(row.get("calculated_at") or row.get("created_at") or ""),
                sourceData=row.get("source_data") if isinstance(row.get("source_data"), dict) else {},
                createdAt=str(row.get("created_at")) if row.get("created_at") else None,
                updatedAt=str(row.get("updated_at")) if row.get("updated_at") else None,
            )
            for row in rows
        ]
        score_types = {score.score_type for score in scores}
        if "fatigue" not in score_types:
            athlete_id = str(athlete_row["athlete_id"])
            created_at = str(athlete_row.get("created_at") or datetime.now(timezone.utc).isoformat())
            latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [athlete_id], "recorded_date").get(athlete_id)
            if latest_physiology:
                fatigue = max(0, 100 - row_float(latest_physiology.get("fatigue_level"), 5) * 10)
                calculated_at = str(latest_physiology.get("recorded_date") or latest_physiology.get("created_at") or created_at)
                scores.append(
                    build_score_record(
                        athlete_id=athlete_id,
                        score_type="fatigue",
                        score_value=fatigue,
                        calculated_at=calculated_at,
                        source_data={"source": "Physiology_Data.fatigue_level"},
                    )
                )
        return scores
    return fallback_scores_for_athlete(athlete_row)


def sync_latest_overall_score(athlete_row: dict[str, Any]) -> None:
    scores = get_scores_for_athlete(athlete_row)
    overall = next((item for item in scores if item.score_type == "overall"), scores[0] if scores else None)
    if not overall:
        return
    try:
        supabase = ensure_supabase()
        supabase.table(APP_TABLES["athlete_scores"]).upsert(
            {
                "score_id": overall.score_id,
                "athlete_id": overall.athlete_id,
                "score_type": overall.score_type,
                "score_value": overall.score_value,
                "percentile": overall.percentile,
                "category": overall.category,
                "calculated_at": overall.calculated_at,
                "source_data": overall.source_data,
                "created_at": overall.created_at,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="score_id",
        ).execute()
    except Exception:
        return


def is_uuid_like(value: str) -> bool:
    return bool(UUID_LIKE_RE.match((value or "").strip()))


def supabase_error_code(exception: Exception) -> str | None:
    if isinstance(exception.args, tuple) and exception.args:
        payload = exception.args[0]
        if isinstance(payload, dict):
            code = payload.get("code")
            return str(code) if code else None
    return None


def resolve_athlete_row_by_identifier(supabase: Any, athlete_identifier: str) -> dict[str, Any] | None:
    identifier = (athlete_identifier or "").strip()
    if not identifier:
        return None

    candidates = ["athlete_id"]
    if not is_uuid_like(identifier):
        candidates.extend(["athlete_id_text", "athlete_code"])

    for column in candidates:
        try:
            result = supabase.table(APP_TABLES["athletes"]).select("*").eq(column, identifier).limit(1).execute()
            row = (result.data or [None])[0]
            if row:
                return row
        except Exception as exception:
            code = supabase_error_code(exception)
            message = str(exception)
            # If the backend schema uses UUID athlete ids, trying to filter by a non-UUID value
            # can trigger a Postgres cast error (22P02). In that case, keep trying alternative columns.
            if code == "22P02" or "invalid input syntax for type uuid" in message:
                continue
            continue

    return None


def coach_can_access_athlete(*, supabase: Any, coach_id: str | None, athlete_row: dict[str, Any]) -> bool:
    if not coach_id:
        return False

    athlete_coach_id = str(athlete_row.get("coach_id") or "")
    if athlete_coach_id and athlete_coach_id == str(coach_id):
        return True

    athlete_id = str(athlete_row.get("athlete_id") or "")
    if not athlete_id:
        return False

    # If the athlete is not assigned yet, allow access when there's a pending assignment request
    # for this coach (default coach flow).
    rows = safe_table_rows(
        "assignment_requests",
        supabase.table("assignment_requests")
        .select("request_id")
        .eq("athlete_id", athlete_id)
        .eq("status", "PENDING")
        .eq("assigned_coach_id", str(coach_id))
        .limit(1),
    )
    return bool(rows)


def is_admin_user(user: UserRecord) -> bool:
    return user.email.lower() == ADMIN_EMAIL


def ensure_admin_user(session_token: str | None) -> UserRecord:
    user = get_user_from_session(session_token)
    if not is_admin_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can manage coach profiles and assignments.",
        )
    return user


def safe_table_rows(table_name: str, query_builder: Any) -> list[dict[str, Any]]:
    try:
        response = query_builder.execute()
        return response.data or []
    except Exception:
        return []


def create_notification(
    *,
    recipient_email: str,
    recipient_role: str,
    title: str,
    message: str,
    notification_type: str,
    entity_id: str | None = None,
    recipient_coach_id: str | None = None,
    related_athlete_id: str | None = None,
    related_session_id: str | None = None,
    action_url: str | None = None,
) -> bool:
    try:
        supabase = ensure_supabase()
        now = datetime.now(timezone.utc).isoformat()
        row = {
            "notification_id": str(uuid4()),
            "recipient_email": recipient_email.lower(),
            "recipient_role": recipient_role,
            "title": title,
            "message": message,
            "type": notification_type,
            "entity_id": entity_id,
            "created_at": now,
        }
        if not recipient_coach_id and recipient_role == "coach":
            recipient_coach_id = resolve_domain_coach_id_for_email(recipient_email)
        enriched_row = {
            **row,
            "recipient_coach_id": recipient_coach_id,
            "notification_type": notification_type.upper(),
            "related_athlete_id": related_athlete_id or entity_id,
            "related_session_id": related_session_id,
            "action_url": action_url,
            "is_read": False,
        }
        try:
            supabase.table(APP_TABLES["notifications"]).insert(enriched_row).execute()
        except Exception:
            supabase.table(APP_TABLES["notifications"]).insert(row).execute()
        return True
    except Exception:
        return False


def write_audit_log(
    *,
    actor_email: str,
    action: str,
    entity_type: str,
    entity_id: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    try:
        supabase = ensure_supabase()
        supabase.table(APP_TABLES["audit_logs"]).insert(
            {
                "audit_id": str(uuid4()),
                "actor_email": actor_email.lower(),
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()
    except Exception:
        return


def ensure_coach_profile(user: UserRecord) -> CoachProfileRecord:
    supabase = ensure_supabase()
    coach_key = resolve_dashboard_coach_key(user)
    assigned_rows = safe_table_rows(
        APP_TABLES["athletes"],
        (supabase.table(APP_TABLES["athletes"]).select("athlete_id").eq("coach_id", coach_key) if coach_key else supabase.table(APP_TABLES["athletes"]).select("athlete_id").eq("coach_id", "__unmapped__")),
    )
    assigned_count = len(assigned_rows)
    domain_rows = get_domain_coaches()
    domain_row = next((row for row in domain_rows if str(row.get("coach_id") or "") == str(coach_key or "")), None)
    rows = safe_table_rows(
        APP_TABLES["coach_profiles"],
        supabase.table(APP_TABLES["coach_profiles"]).select("*").eq("email", user.email.lower()).limit(1),
    )
    row = rows[0] if rows else {}
    if not row:
        row = {
            "coach_id": coach_key or user.email.lower(),
            "name": (domain_row or {}).get("coach_name") or user.full_name,
            "email": user.email.lower(),
            "status": "active",
            "created_at": None,
            "updated_at": None,
        }

    # Dashboard endpoints are keyed by the domain coaches.coach_id UUID, not the
    # legacy coach_profiles.coach_id text value.
    resolved_coach_id = coach_key or row.get("coach_id") or user.email.lower()
    return CoachProfileRecord(
        coachId=str(resolved_coach_id),
        name=str(row.get("name") or (domain_row or {}).get("coach_name") or user.full_name),
        email=str(row.get("email") or user.email.lower()),
        phone=row.get("phone"),
        profileImage=row.get("profile_image"),
        specialization=row.get("specialization"),
        status=row.get("status") if row.get("status") in {"active", "inactive"} else "active",
        assignedAthletes=assigned_count,
        createdAt=str(row.get("created_at")) if row.get("created_at") else None,
        updatedAt=str(row.get("updated_at")) if row.get("updated_at") else None,
    )


def score_category(value: float) -> str:
    if value >= 80:
        return "Strong"
    if value >= 60:
        return "Progressing"
    return "Needs Attention"


def build_score_record(
    *,
    athlete_id: str,
    score_type: str,
    score_value: float,
    calculated_at: str,
    source_data: dict[str, Any] | None = None,
) -> AthleteScoreRecord:
    return AthleteScoreRecord(
        scoreId=f"{athlete_id}-{score_type}-{calculated_at}",
        athleteId=athlete_id,
        scoreType=score_type,
        scoreValue=round(score_value, 2),
        percentile=round(score_value, 2),
        category=score_category(score_value),
        calculatedAt=calculated_at,
        sourceData=source_data or {},
        createdAt=calculated_at,
        updatedAt=calculated_at,
    )


def fallback_scores_for_athlete(athlete_row: dict[str, Any]) -> list[AthleteScoreRecord]:
    athlete_id = str(athlete_row["athlete_id"])
    created_at = str(athlete_row.get("created_at") or datetime.now(timezone.utc).isoformat())
    email = str(athlete_row.get("email") or "").lower()
    app_user = get_user_by_email(email) if email else None
    base_score = float(app_user.performance_score if app_user and app_user.performance_score is not None else 75)

    latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [athlete_id], "recorded_date").get(athlete_id)
    scores = [
        build_score_record(
            athlete_id=athlete_id,
            score_type="overall",
            score_value=base_score,
            calculated_at=created_at,
            source_data={"source": "App_Users.performance_score"},
        )
    ]
    if latest_physiology:
        recovery = row_float(latest_physiology.get("recovery_score"), base_score)
        stress_control = 100 - row_float(latest_physiology.get("stress_score"), 50)
        fatigue = max(0, 100 - row_float(latest_physiology.get("fatigue_level"), 5) * 10)
        readiness = round((recovery + stress_control + fatigue) / 3, 2)
        calculated_at = str(latest_physiology.get("recorded_date") or latest_physiology.get("created_at") or created_at)
        scores.extend(
            [
                build_score_record(
                    athlete_id=athlete_id,
                    score_type="recovery",
                    score_value=recovery,
                    calculated_at=calculated_at,
                    source_data={"source": "Physiology_Data.recovery_score"},
                ),
                build_score_record(
                    athlete_id=athlete_id,
                    score_type="readiness",
                    score_value=readiness,
                    calculated_at=calculated_at,
                    source_data={"source": "Physiology_Data"},
                ),
                build_score_record(
                    athlete_id=athlete_id,
                    score_type="fatigue",
                    score_value=fatigue,
                    calculated_at=calculated_at,
                    source_data={"source": "Physiology_Data.fatigue_level"},
                ),
            ]
        )
    return scores


def get_scores_for_athlete(athlete_row: dict[str, Any]) -> list[AthleteScoreRecord]:
    supabase = ensure_supabase()
    athlete_id = str(athlete_row["athlete_id"])
    rows = safe_table_rows(
        APP_TABLES["athlete_scores"],
        supabase.table(APP_TABLES["athlete_scores"]).select("*").eq("athlete_id", athlete_id).order("calculated_at", desc=True),
    )
    if rows:
        scores = [
            AthleteScoreRecord(
                scoreId=str(row.get("score_id") or ""),
                athleteId=str(row.get("athlete_id") or ""),
                scoreType=str(row.get("score_type") or "overall"),
                scoreValue=row_float(row.get("score_value")),
                percentile=row_float(row.get("percentile")) if row.get("percentile") is not None else None,
                category=str(row.get("category") or score_category(row_float(row.get("score_value")))),
                calculatedAt=str(row.get("calculated_at") or row.get("created_at") or ""),
                sourceData=row.get("source_data") if isinstance(row.get("source_data"), dict) else {},
                createdAt=str(row.get("created_at")) if row.get("created_at") else None,
                updatedAt=str(row.get("updated_at")) if row.get("updated_at") else None,
            )
            for row in rows
        ]
        score_types = {score.score_type for score in scores}
        if "fatigue" not in score_types:
            athlete_id = str(athlete_row["athlete_id"])
            created_at = str(athlete_row.get("created_at") or datetime.now(timezone.utc).isoformat())
            latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [athlete_id], "recorded_date").get(athlete_id)
            if latest_physiology:
                fatigue = max(0, 100 - row_float(latest_physiology.get("fatigue_level"), 5) * 10)
                calculated_at = str(latest_physiology.get("recorded_date") or latest_physiology.get("created_at") or created_at)
                scores.append(
                    build_score_record(
                        athlete_id=athlete_id,
                        score_type="fatigue",
                        score_value=fatigue,
                        calculated_at=calculated_at,
                        source_data={"source": "Physiology_Data.fatigue_level"},
                    )
                )
        return scores
    return fallback_scores_for_athlete(athlete_row)


def sync_latest_overall_score(athlete_row: dict[str, Any]) -> None:
    scores = get_scores_for_athlete(athlete_row)
    overall = next((item for item in scores if item.score_type == "overall"), scores[0] if scores else None)
    if not overall:
        return
    try:
        supabase = ensure_supabase()
        supabase.table(APP_TABLES["athlete_scores"]).upsert(
            {
                "score_id": overall.score_id,
                "athlete_id": overall.athlete_id,
                "score_type": overall.score_type,
                "score_value": overall.score_value,
                "percentile": overall.percentile,
                "category": overall.category,
                "calculated_at": overall.calculated_at,
                "source_data": overall.source_data,
                "created_at": overall.created_at,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="score_id",
        ).execute()
    except Exception:
        return


def ensure_assigned_coach_for_student(user: UserRecord) -> UserRecord:
    if user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only student accounts can use this flow.",
        )

    assigned_email = (user.assigned_coach_email or "").lower()
    coach = get_user_by_email(assigned_email)
    if not coach or coach.role != "coach":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This student account is not mapped to an active coach yet.",
        )
    return coach


def request_coach_assignment_for_student(user: UserRecord) -> UserRecord:
    if user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only student accounts can request a coach assignment.",
        )
    if user.assignment_status == "assigned" and user.assigned_coach_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This student account is already assigned to a coach.",
        )

    coach = get_primary_coach()
    updated_user = UserRecord(
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        salt=user.salt,
        password_hash=user.password_hash,
        coach_code=user.coach_code,
        assignment_status="pending",
        assigned_coach_email=None,
        assigned_coach_name=None,
        requested_coach_email=coach.email,
        requested_coach_name=coach.full_name,
        requested_coach_code=coach.coach_code,
        coach_request_sent_at=datetime.now(timezone.utc).isoformat(),
        sport=user.sport,
        focus_area=user.focus_area,
        date_of_birth=user.date_of_birth,
        performance_score=user.performance_score,
    )
    return upsert_user(updated_user)


def approve_assignment_request_for_coach(
    coach_user: UserRecord,
    student_email: str,
    coach_code: str,
) -> UserRecord:
    student = get_user_by_email(student_email.lower())
    if not student or student.role != "student":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student request not found.")
    if student.assignment_status != "pending" or student.requested_coach_email != coach_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending assignment request was found for this student.",
        )
    if (coach_user.coach_code or "").upper() != coach_code.strip().upper():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The coach code does not match your coach profile.",
        )

    approved_student = UserRecord(
        email=student.email,
        full_name=student.full_name,
        role=student.role,
        salt=student.salt,
        password_hash=student.password_hash,
        coach_code=student.coach_code,
        assignment_status="assigned",
        assigned_coach_email=coach_user.email.lower(),
        assigned_coach_name=coach_user.full_name,
        requested_coach_email=None,
        requested_coach_name=None,
        requested_coach_code=None,
        coach_request_sent_at=None,
        sport=student.sport,
        focus_area=student.focus_area,
        date_of_birth=student.date_of_birth,
        performance_score=student.performance_score,
    )
    return upsert_user(approved_student)


def serialize_feedback_item(item: dict[str, Any]) -> CoachFeedbackRecord:
    return CoachFeedbackRecord(
        feedbackId=item["feedbackId"],
        athleteId=item["athleteId"],
        athleteName=item["athleteName"],
        athleteEmail=item["athleteEmail"],
        coachEmail=item["coachEmail"],
        coachName=item["coachName"],
        note=item["note"],
        recommendation=item["recommendation"],
        status=item["status"],
        createdAt=item["createdAt"],
    )


def serialize_athlete_master(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "athleteId": row["athlete_id"],
        "name": row.get("athlete_name") or row.get("name") or "Unnamed athlete",
        "age": row.get("age"),
        "gender": row.get("gender") or "Not provided",
        "heightCm": row.get("height_cm"),
        "weightKg": row.get("weight_kg"),
        "academyId": str(row.get("academy_id") or ""),
        "coachId": str(row.get("coach_id") or ""),
        "contactNumber": row.get("contact_number") or "",
        "email": row.get("email") or "",
        "name": row.get("athlete_name") or row.get("name") or "Unnamed athlete",
        "age": row.get("age"),
        "gender": row.get("gender") or "Not provided",
        "heightCm": row.get("height_cm"),
        "weightKg": row.get("weight_kg"),
        "academyId": str(row.get("academy_id") or ""),
        "coachId": str(row.get("coach_id") or ""),
        "contactNumber": row.get("contact_number") or "",
        "email": row.get("email") or "",
        "createdAt": row["created_at"],
        "updatedBy": row.get("updated_by"),
    }


def get_latest_rows_by_athlete(
    table_name: str,
    athlete_ids: list[str],
    order_column: str,
) -> dict[str, dict[str, Any]]:
    if not athlete_ids:
        return {}

    supabase = ensure_supabase()
    response = (
        supabase.table(table_name)
        .select("*")
        .in_("athlete_id", athlete_ids)
        .order(order_column, desc=True)
        .execute()
    )

    latest_rows: dict[str, dict[str, Any]] = {}
    for row in response.data or []:
        athlete_id = row.get("athlete_id")
        if athlete_id and athlete_id not in latest_rows:
            latest_rows[athlete_id] = row

    return latest_rows


def get_latest_rows_by_athlete(
    table_name: str,
    athlete_ids: list[str],
    order_column: str,
) -> dict[str, dict[str, Any]]:
    if not athlete_ids:
        return {}

    supabase = ensure_supabase()
    response = (
        supabase.table(table_name)
        .select("*")
        .in_("athlete_id", athlete_ids)
        .order(order_column, desc=True)
        .execute()
    )

    latest_rows: dict[str, dict[str, Any]] = {}
    for row in response.data or []:
        athlete_id = row.get("athlete_id")
        if athlete_id and athlete_id not in latest_rows:
            latest_rows[athlete_id] = row

    return latest_rows


def serialize_family_details(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    conservative = row.get("family_conservative")
    return {
        "motherName": row["mother_name"],
        "fatherName": row["father_name"],
        "motherOccupation": row["mother_occupation"],
        "fatherOccupation": row["father_occupation"],
        "educationLevel": row["education_level"],
        "siblingDetails": row["sibling_details"],
        "familyConservative": conservative if conservative in {"Yes", "No"} else "Yes" if conservative is True else "No" if conservative is False else "Not provided",
        "disciplineLevel": row["discipline_level"],
        "healthConditions": row["health_conditions"],
        "fatherContactNumber": row["father_contact_number"],
        "motherContactNumber": row["mother_contact_number"],
        "parentEmail": row["parent_email"],
        "comments": row["comments"],
    }


def serialize_athlete_profile(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        "class": row["class"],
        "schoolName": row["school_name"],
        "dietType": row["diet_type"],
        "outsideFoodFrequency": row["outside_food_frequency"],
        "sleepTime": row["sleep_time"],
        "wakeTime": row["wake_time"],
        "friendCircle": row["friend_circle"],
        "angerPattern": row["anger_pattern"],
        "sadnessPattern": row["sadness_pattern"],
        "academicPerformance": row["academic_performance"],
        "reasonForShooting": row["reason_for_shooting"],
        "athleteGoal": row["athlete_goal"],
    }


def row_number(value: Any, fallback: int = 0) -> int:
    if value is None:
        return fallback
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def row_float(value: Any, fallback: float = 0) -> float:
    if value is None:
        return fallback
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def get_single_athlete_related_row(
    table_name: str,
    athlete_id: str,
    *,
    text_column: str = "athlete_id",
) -> dict[str, Any] | None:
    supabase = ensure_supabase()
    response = supabase.table(table_name).select("*").eq(text_column, athlete_id).limit(1).execute()
    return (response.data or [None])[0]


def serialize_shooting_session(row: dict[str, Any]) -> dict[str, Any]:
    duration = row.get("session_duration_min") or row.get("duration_minutes") or 0
    return {
        "sessionId": str(row.get("session_id") or ""),
        "coachId": str(row.get("coach_id") or ""),
        "sessionDate": row.get("session_date") or row.get("created_at"),
        "startTime": row.get("start_time") or "",
        "endTime": row.get("end_time") or "",
        "durationMinutes": row_number(duration),
        "trainingType": row.get("training_type") or "Shooting",
        "location": row.get("location") or row.get("session_type") or "Training",
        "notes": row.get("notes") or row.get("coach_notes") or row.get("athlete_notes") or "",
    }


def serialize_app_physiology(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "physiologyId": str(row.get("physiology_id") or ""),
        "sessionId": str(row.get("session_id") or ""),
        "recordedDate": row.get("recorded_date") or row.get("created_at"),
        "restingHeartRate": row_number(row.get("resting_heart_rate")),
        "avgHeartRate": row_number(row.get("avg_heart_rate")),
        "spo2": row_number(row.get("spo2")),
        "breathingRate": row_number(row.get("breathing_rate")),
        "sleepHours": row_float(row.get("sleep_hours")),
        "recoveryScore": row_number(row.get("recovery_score")),
        "stressScore": row_number(row.get("stress_score")),
        "fatigueLevel": row_number(row.get("fatigue_level")),
        "remarks": row.get("remarks") or "",
    }


def normalize_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)] if str(value).strip() else []


def parse_json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip():
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def compact_json(value: dict[str, Any]) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True)


def ensure_mobile_athlete_row(athlete_id: str) -> dict[str, Any]:
    supabase = ensure_supabase()
    response = supabase.table(APP_TABLES["athletes"]).select("*").eq("athlete_id", athlete_id).limit(1).execute()
    athlete_row = (response.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    return athlete_row


def get_mobile_profile_row(athlete_id: str) -> dict[str, Any] | None:
    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["athlete_details"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .limit(1)
        .execute()
    )
    return (response.data or [None])[0]


def get_mobile_baseline_row(athlete_id: str) -> dict[str, Any] | None:
    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["athlete_physiology"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .order("recorded_date", desc=True)
        .limit(1)
        .execute()
    )
    return (response.data or [None])[0]


def compute_mobile_profile_status(profile: dict[str, Any], resting_hr: int | None = None) -> tuple[str, str]:
    required_values = [
        profile.get("full_name"),
        profile.get("age"),
        profile.get("gender"),
        profile.get("discipline"),
        profile.get("average_practice_score"),
        profile.get("target_score"),
    ]
    has_goal = bool(profile.get("goal_30_days") or profile.get("goal_6_months"))
    is_complete = all(value is not None and value != "" for value in required_values) and has_goal
    completion = "complete" if is_complete else "partial"
    if not is_complete:
        return "profile_started", completion
    if profile.get("polar_linked") and not resting_hr:
        return "baseline_pending", completion
    return "ready_to_train", completion


def serialize_mobile_profile(
    profile_row: dict[str, Any] | None,
    athlete_row: dict[str, Any],
) -> MobileAthleteProfileRecord:
    row = profile_row or {}
    performance = parse_json_object(row.get("academic_performance"))
    shooting = parse_json_object(row.get("reason_for_shooting"))
    goals = parse_json_object(row.get("athlete_goal"))
    baseline = get_mobile_baseline_row(str(athlete_row["athlete_id"]))
    resting_hr = row_number((baseline or {}).get("resting_heart_rate"), fallback=None)  # type: ignore[arg-type]
    hrv = parse_json_object((baseline or {}).get("remarks")).get("hrvBaselineMs")
    profile_data = {
        "full_name": athlete_row.get("name") or athlete_row.get("athlete_name"),
        "age": athlete_row.get("age"),
        "gender": athlete_row.get("gender"),
        "discipline": shooting.get("discipline") or athlete_row.get("academy_id"),
        "average_practice_score": performance.get("averagePracticeScore"),
        "target_score": performance.get("targetScore"),
        "goal_30_days": goals.get("goal30Days") or row.get("athlete_goal"),
        "goal_6_months": goals.get("goal6Months"),
        "polar_linked": bool(resting_hr),
    }
    onboarding_status, completion_status = compute_mobile_profile_status(profile_data, resting_hr)
    return MobileAthleteProfileRecord(
        athleteId=str(athlete_row["athlete_id"]),
        fullName=profile_data["full_name"],
        age=row_number(athlete_row.get("age"), fallback=None),  # type: ignore[arg-type]
        gender=athlete_row.get("gender"),
        city=shooting.get("city"),
        discipline=profile_data["discipline"],
        experienceLevel=performance.get("experienceLevel"),
        yearsShooting=row_number(performance.get("yearsShooting"), fallback=None),  # type: ignore[arg-type]
        academyClub=shooting.get("academyClub") or athlete_row.get("academy_id"),
        averagePracticeScore=row_float(performance.get("averagePracticeScore"), fallback=None),  # type: ignore[arg-type]
        targetScore=row_float(performance.get("targetScore"), fallback=None),  # type: ignore[arg-type]
        performanceFactors=normalize_text_list(shooting.get("performanceFactors")),
        goal30Days=goals.get("goal30Days") or row.get("athlete_goal"),
        goal6Months=goals.get("goal6Months"),
        polarLinked=bool(resting_hr),
        polarDeviceId=None,
        restingHrBaseline=resting_hr,
        hrvBaselineMs=row_number(hrv, fallback=None),  # type: ignore[arg-type]
        onboardingStatus=athlete_row.get("onboarding_status") or onboarding_status,
        profileCompletionStatus=athlete_row.get("profile_completion_status") or completion_status,
        createdAt=row.get("created_at") or athlete_row.get("created_at"),
        updatedAt=row.get("updated_at") or athlete_row.get("updated_at"),
    )


def serialize_mobile_checkin(row: dict[str, Any]) -> MobileDailyCheckinRecord:
    payload = parse_json_object(row.get("answer_text"))
    recorded_at = row.get("recorded_at") or row.get("created_at") or datetime.now(timezone.utc).isoformat()
    recorded_date = payload.get("checkinDate") or str(recorded_at)[:10]
    return MobileDailyCheckinRecord(
        checkinId=str(row.get("answer_id") or ""),
        athleteId=str(row.get("athlete_id") or ""),
        checkinDate=recorded_date,
        mood=payload.get("mood") or "Okay",
        energyLevel=row_number(payload.get("energyLevel") or row.get("answer_score"), fallback=5),
        sleepBand=payload.get("sleepBand"),
        sleepHours=row_float(payload.get("sleepHours"), fallback=None),  # type: ignore[arg-type]
        tags=normalize_text_list(payload.get("tags")),
        notes=payload.get("notes"),
        createdAt=recorded_at,
        updatedAt=recorded_at,
    )


def sleep_band_to_hours(sleep_band: str | None) -> float | None:
    return {
        "<5h": 4.5,
        "5-6h": 5.5,
        "6-7h": 6.5,
        "7-8h": 7.5,
        "8h+": 8.0,
    }.get(sleep_band or "")


def calculate_readiness(profile: MobileAthleteProfileRecord, checkin: MobileDailyCheckinRecord | None) -> int:
    if not checkin:
        return 60 if profile.resting_hr_baseline else 50
    mood_score = {"Trouble": 1, "Poor": 2, "Okay": 3, "Good": 4, "Great": 5}.get(checkin.mood, 3)
    sleep_hours = checkin.sleep_hours or sleep_band_to_hours(checkin.sleep_band) or 6
    readiness = 30 + (checkin.energy_level * 4) + (mood_score * 6) + min(sleep_hours, 8) * 2
    return max(0, min(100, round(readiness)))


def normalize_shot_score(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized == "X":
            return 0.0
        if normalized.startswith("<"):
            return 4.9
        value = normalized
    try:
        score = float(value)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Shot scores must be numeric, '<5', or 'X'.")
    if score < 0 or score > 10.9:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Shot scores must be between 0 and 10.9.")
    return score


def serialize_mobile_session(row: dict[str, Any]) -> dict[str, Any]:
    notes = parse_json_object(row.get("notes"))
    return {
        "sessionId": str(row.get("session_id") or ""),
        "athleteId": str(row.get("athlete_id") or ""),
        "rangeType": notes.get("rangeType") or row.get("location"),
        "sessionType": notes.get("sessionType") or row.get("training_type"),
        "plannedShots": row_number(notes.get("plannedShots")),
        "discipline": notes.get("discipline"),
        "intention": notes.get("intention"),
        "visualization": notes.get("visualization"),
        "bodyScanCompleted": bool(notes.get("bodyScanCompleted")),
        "status": notes.get("status") or "LIVE",
        "startedAt": row.get("session_date"),
        "endedAt": notes.get("endedAt"),
        "durationSeconds": row_number(row.get("duration_minutes")) * 60,
        "avgHeartRate": row_float(notes.get("avgHeartRate"), fallback=None),  # type: ignore[arg-type]
        "peakHeartRate": row_float(notes.get("peakHeartRate"), fallback=None),  # type: ignore[arg-type]
        "fatigue": notes.get("fatigue"),
        "recovery": notes.get("recovery"),
        "createdAt": row.get("created_at"),
        "updatedAt": row.get("updated_at") or row.get("created_at"),
    }


def serialize_mobile_series(row: dict[str, Any]) -> dict[str, Any]:
    source = parse_json_object(row.get("source_data"))
    shots = source.get("shots") or []
    if not isinstance(shots, list):
        shots = []
    return {
        "seriesId": str(row.get("score_id") or ""),
        "sessionId": str(source.get("sessionId") or ""),
        "athleteId": str(row.get("athlete_id") or ""),
        "seriesNumber": row_number(source.get("seriesNumber")),
        "shots": shots,
        "total": row_float(row.get("score_value")),
        "avgHeartRate": row_float(source.get("avgHeartRate"), fallback=None),  # type: ignore[arg-type]
        "createdAt": row.get("created_at"),
        "updatedAt": row.get("updated_at"),
    }


def serialize_mobile_reflection(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    payload = parse_json_object(row.get("answer_text"))
    return {
        "reflectionId": str(row.get("answer_id") or ""),
        "sessionId": str(payload.get("sessionId") or ""),
        "athleteId": str(row.get("athlete_id") or ""),
        "mood": payload.get("mood"),
        "whatWorked": payload.get("whatWorked"),
        "whatDidnt": payload.get("whatDidnt"),
        "voiceNoteUrl": payload.get("voiceNoteUrl"),
        "selfRating": row_number(payload.get("selfRating"), fallback=None),  # type: ignore[arg-type]
        "fatigueLevel": row_number(payload.get("fatigueLevel"), fallback=None),  # type: ignore[arg-type]
        "createdAt": row.get("recorded_at") or row.get("created_at"),
        "updatedAt": row.get("recorded_at") or row.get("created_at"),
    }


def ensure_mobile_session_row(athlete_id: str, session_id: str) -> dict[str, Any]:
    ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["shooting_session_log"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("session_id", session_id)
        .limit(1)
        .execute()
    )
    session_row = (response.data or [None])[0]
    if not session_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found.")
    return session_row


def list_mobile_session_series(session_id: str) -> list[dict[str, Any]]:
    supabase = ensure_supabase()
    session_row = (
        supabase.table(APP_TABLES["shooting_session_log"])
        .select("athlete_id")
        .eq("session_id", session_id)
        .limit(1)
        .execute()
    )
    athlete_id = ((session_row.data or [{}])[0]).get("athlete_id")
    if not athlete_id:
        return []
    rows = safe_table_rows(
        APP_TABLES["athlete_scores"],
        supabase.table(APP_TABLES["athlete_scores"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("score_type", "mobile_series")
        .order("created_at"),
    )
    series = [
        serialize_mobile_series(row)
        for row in rows
        if parse_json_object(row.get("source_data")).get("sessionId") == session_id
    ]
    return sorted(series, key=lambda item: item.get("seriesNumber") or 0)


def get_mobile_session_reflection(session_id: str) -> dict[str, Any] | None:
    supabase = ensure_supabase()
    session_row = (
        supabase.table(APP_TABLES["shooting_session_log"])
        .select("athlete_id")
        .eq("session_id", session_id)
        .limit(1)
        .execute()
    )
    athlete_id = ((session_row.data or [{}])[0]).get("athlete_id")
    if not athlete_id:
        return None
    rows = safe_table_rows(
        APP_TABLES["psychology_responses"],
        supabase.table(APP_TABLES["psychology_responses"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("question_id", "MOBILE_SESSION_REFLECTION")
        .order("recorded_at", desc=True),
    )
    for row in rows:
        if parse_json_object(row.get("answer_text")).get("sessionId") == session_id:
            return serialize_mobile_reflection(row)
    return None


def build_mobile_session_summary(session_row: dict[str, Any]) -> dict[str, Any]:
    session = serialize_mobile_session(session_row)
    series = list_mobile_session_series(session["sessionId"])
    all_scores = [normalize_shot_score(score) for item in series for score in item["shots"]]
    total = round(sum(all_scores), 1)
    planned_shots = max(session.get("plannedShots") or len(all_scores), 1)
    average = round(total / len(all_scores), 1) if all_scores else 0
    max_total = planned_shots * 10
    efficiency = round((total / max_total) * 100) if max_total else 0
    best_series = max(series, key=lambda item: item["total"], default=None)
    worst_series = min(series, key=lambda item: item["total"], default=None)
    avg_hr_values = [item["avgHeartRate"] for item in series if item.get("avgHeartRate") is not None]
    avg_hr = round(sum(avg_hr_values) / len(avg_hr_values)) if avg_hr_values else session.get("avgHeartRate")
    key_insight = (
        "Solid baseline performance"
        if efficiency >= 60
        else "Build consistency before increasing load"
    )
    recommendations = [
        "Review your shot sequence for the lowest scoring series",
        "Log your session reflection in journal",
    ]
    if avg_hr and session.get("peakHeartRate") and session["peakHeartRate"] - avg_hr > 15:
        recommendations.insert(0, "Complete a 5-minute breathing cool-down")

    return {
        "session": session,
        "series": series,
        "score": {
            "total": total,
            "maxTotal": max_total,
            "averagePerShot": average,
            "efficiencyPercent": efficiency,
            "bestShot": max(all_scores) if all_scores else None,
            "worstShot": min(all_scores) if all_scores else None,
            "bestSeries": best_series,
            "worstSeries": worst_series,
        },
        "physiology": {
            "avgHeartRate": avg_hr,
            "peakHeartRate": session.get("peakHeartRate"),
            "fatigue": session.get("fatigue"),
            "recovery": session.get("recovery"),
        },
        "mentalState": {
            "reflection": get_mobile_session_reflection(session["sessionId"]),
        },
        "keyInsight": {
            "title": key_insight,
            "message": "Use this as your reference point and look for stable scores across every series.",
        },
        "recommendations": recommendations,
    }


def serialize_app_feedback(row: dict[str, Any], athlete_lookup: dict[str, dict[str, Any]] | None = None) -> CoachFeedbackRecord:
    athlete = (athlete_lookup or {}).get(str(row.get("athlete_id"))) or {}
    technique = row_number(row.get("technique_score"), 0)
    focus = row_number(row.get("focus_score"), 0)
    average = round((technique + focus + row_number(row.get("breathing_score"), 0) + row_number(row.get("posture_score"), 0)) / 4)
    status_label: Literal["Needs Attention", "Progressing", "Strong"] = (
        "Strong" if average >= 8 else "Progressing" if average >= 5 else "Needs Attention"
    )
    return CoachFeedbackRecord(
        feedbackId=str(row.get("feedback_id") or ""),
        athleteId=str(row.get("athlete_id") or ""),
        athleteName=athlete.get("athlete_name") or "Athlete",
        athleteEmail=athlete.get("email") or "",
        coachEmail=str(row.get("coach_uid") or row.get("coach_id") or ""),
        coachName="Coach",
        note=row.get("coach_observations") or row.get("coach_notes") or row.get("strengths") or "",
        recommendation=row.get("training_plan") or row.get("exercise_plan") or row.get("improvement_areas") or "",
        status=status_label,
        createdAt=str(row.get("created_at") or ""),
    )


def row_number(value: Any, fallback: int = 0) -> int:
    if value is None:
        return fallback
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def row_float(value: Any, fallback: float = 0) -> float:
    if value is None:
        return fallback
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def get_single_athlete_related_row(
    table_name: str,
    athlete_id: str,
    *,
    text_column: str = "athlete_id",
) -> dict[str, Any] | None:
    supabase = ensure_supabase()
    response = supabase.table(table_name).select("*").eq(text_column, athlete_id).limit(1).execute()
    return (response.data or [None])[0]


def serialize_shooting_session(row: dict[str, Any]) -> dict[str, Any]:
    duration = row.get("session_duration_min") or row.get("duration_minutes") or 0
    return {
        "sessionId": str(row.get("session_id") or ""),
        "coachId": str(row.get("coach_id") or ""),
        "sessionDate": row.get("session_date") or row.get("created_at"),
        "startTime": row.get("start_time") or "",
        "endTime": row.get("end_time") or "",
        "durationMinutes": row_number(duration),
        "trainingType": row.get("training_type") or "Shooting",
        "location": row.get("location") or row.get("session_type") or "Training",
        "notes": row.get("notes") or row.get("coach_notes") or row.get("athlete_notes") or "",
    }


def serialize_app_physiology(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "physiologyId": str(row.get("physiology_id") or ""),
        "sessionId": str(row.get("session_id") or ""),
        "recordedDate": row.get("recorded_date") or row.get("created_at"),
        "restingHeartRate": row_number(row.get("resting_heart_rate")),
        "avgHeartRate": row_number(row.get("avg_heart_rate")),
        "spo2": row_number(row.get("spo2")),
        "breathingRate": row_number(row.get("breathing_rate")),
        "sleepHours": row_float(row.get("sleep_hours")),
        "recoveryScore": row_number(row.get("recovery_score")),
        "stressScore": row_number(row.get("stress_score")),
        "fatigueLevel": row_number(row.get("fatigue_level")),
        "remarks": row.get("remarks") or "",
    }


def normalize_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)] if str(value).strip() else []


def parse_json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip():
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def compact_json(value: dict[str, Any]) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True)


def ensure_mobile_athlete_row(athlete_id: str) -> dict[str, Any]:
    supabase = ensure_supabase()
    response = supabase.table(APP_TABLES["athletes"]).select("*").eq("athlete_id", athlete_id).limit(1).execute()
    athlete_row = (response.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    return athlete_row


def get_mobile_profile_row(athlete_id: str) -> dict[str, Any] | None:
    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["athlete_details"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .limit(1)
        .execute()
    )
    return (response.data or [None])[0]


def get_mobile_baseline_row(athlete_id: str) -> dict[str, Any] | None:
    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["athlete_physiology"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .order("recorded_date", desc=True)
        .limit(1)
        .execute()
    )
    return (response.data or [None])[0]


def compute_mobile_profile_status(profile: dict[str, Any], resting_hr: int | None = None) -> tuple[str, str]:
    required_values = [
        profile.get("full_name"),
        profile.get("age"),
        profile.get("gender"),
        profile.get("discipline"),
        profile.get("average_practice_score"),
        profile.get("target_score"),
    ]
    has_goal = bool(profile.get("goal_30_days") or profile.get("goal_6_months"))
    is_complete = all(value is not None and value != "" for value in required_values) and has_goal
    completion = "complete" if is_complete else "partial"
    if not is_complete:
        return "profile_started", completion
    if profile.get("polar_linked") and not resting_hr:
        return "baseline_pending", completion
    return "ready_to_train", completion


def serialize_mobile_profile(
    profile_row: dict[str, Any] | None,
    athlete_row: dict[str, Any],
) -> MobileAthleteProfileRecord:
    row = profile_row or {}
    performance = parse_json_object(row.get("academic_performance"))
    shooting = parse_json_object(row.get("reason_for_shooting"))
    goals = parse_json_object(row.get("athlete_goal"))
    baseline = get_mobile_baseline_row(str(athlete_row["athlete_id"]))
    resting_hr = row_number((baseline or {}).get("resting_heart_rate"), fallback=None)  # type: ignore[arg-type]
    hrv = parse_json_object((baseline or {}).get("remarks")).get("hrvBaselineMs")
    profile_data = {
        "full_name": athlete_row.get("name") or athlete_row.get("athlete_name"),
        "age": athlete_row.get("age"),
        "gender": athlete_row.get("gender"),
        "discipline": shooting.get("discipline") or athlete_row.get("academy_id"),
        "average_practice_score": performance.get("averagePracticeScore"),
        "target_score": performance.get("targetScore"),
        "goal_30_days": goals.get("goal30Days") or row.get("athlete_goal"),
        "goal_6_months": goals.get("goal6Months"),
        "polar_linked": bool(resting_hr),
    }
    onboarding_status, completion_status = compute_mobile_profile_status(profile_data, resting_hr)
    return MobileAthleteProfileRecord(
        athleteId=str(athlete_row["athlete_id"]),
        fullName=profile_data["full_name"],
        age=row_number(athlete_row.get("age"), fallback=None),  # type: ignore[arg-type]
        gender=athlete_row.get("gender"),
        city=shooting.get("city"),
        discipline=profile_data["discipline"],
        experienceLevel=performance.get("experienceLevel"),
        yearsShooting=row_number(performance.get("yearsShooting"), fallback=None),  # type: ignore[arg-type]
        academyClub=shooting.get("academyClub") or athlete_row.get("academy_id"),
        averagePracticeScore=row_float(performance.get("averagePracticeScore"), fallback=None),  # type: ignore[arg-type]
        targetScore=row_float(performance.get("targetScore"), fallback=None),  # type: ignore[arg-type]
        performanceFactors=normalize_text_list(shooting.get("performanceFactors")),
        goal30Days=goals.get("goal30Days") or row.get("athlete_goal"),
        goal6Months=goals.get("goal6Months"),
        polarLinked=bool(resting_hr),
        polarDeviceId=None,
        restingHrBaseline=resting_hr,
        hrvBaselineMs=row_number(hrv, fallback=None),  # type: ignore[arg-type]
        onboardingStatus=athlete_row.get("onboarding_status") or onboarding_status,
        profileCompletionStatus=athlete_row.get("profile_completion_status") or completion_status,
        createdAt=row.get("created_at") or athlete_row.get("created_at"),
        updatedAt=row.get("updated_at") or athlete_row.get("updated_at"),
    )


def serialize_mobile_checkin(row: dict[str, Any]) -> MobileDailyCheckinRecord:
    payload = parse_json_object(row.get("answer_text"))
    recorded_at = row.get("recorded_at") or row.get("created_at") or datetime.now(timezone.utc).isoformat()
    recorded_date = payload.get("checkinDate") or str(recorded_at)[:10]
    return MobileDailyCheckinRecord(
        checkinId=str(row.get("answer_id") or ""),
        athleteId=str(row.get("athlete_id") or ""),
        checkinDate=recorded_date,
        mood=payload.get("mood") or "Okay",
        energyLevel=row_number(payload.get("energyLevel") or row.get("answer_score"), fallback=5),
        sleepBand=payload.get("sleepBand"),
        sleepHours=row_float(payload.get("sleepHours"), fallback=None),  # type: ignore[arg-type]
        tags=normalize_text_list(payload.get("tags")),
        notes=payload.get("notes"),
        createdAt=recorded_at,
        updatedAt=recorded_at,
    )


def sleep_band_to_hours(sleep_band: str | None) -> float | None:
    return {
        "<5h": 4.5,
        "5-6h": 5.5,
        "6-7h": 6.5,
        "7-8h": 7.5,
        "8h+": 8.0,
    }.get(sleep_band or "")


def calculate_readiness(profile: MobileAthleteProfileRecord, checkin: MobileDailyCheckinRecord | None) -> int:
    if not checkin:
        return 60 if profile.resting_hr_baseline else 50
    mood_score = {"Trouble": 1, "Poor": 2, "Okay": 3, "Good": 4, "Great": 5}.get(checkin.mood, 3)
    sleep_hours = checkin.sleep_hours or sleep_band_to_hours(checkin.sleep_band) or 6
    readiness = 30 + (checkin.energy_level * 4) + (mood_score * 6) + min(sleep_hours, 8) * 2
    return max(0, min(100, round(readiness)))


def normalize_shot_score(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized == "X":
            return 0.0
        if normalized.startswith("<"):
            return 4.9
        value = normalized
    try:
        score = float(value)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Shot scores must be numeric, '<5', or 'X'.")
    if score < 0 or score > 10.9:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Shot scores must be between 0 and 10.9.")
    return score


def serialize_mobile_session(row: dict[str, Any]) -> dict[str, Any]:
    notes = parse_json_object(row.get("notes"))
    return {
        "sessionId": str(row.get("session_id") or ""),
        "athleteId": str(row.get("athlete_id") or ""),
        "rangeType": notes.get("rangeType") or row.get("location"),
        "sessionType": notes.get("sessionType") or row.get("training_type"),
        "plannedShots": row_number(notes.get("plannedShots")),
        "discipline": notes.get("discipline"),
        "intention": notes.get("intention"),
        "visualization": notes.get("visualization"),
        "bodyScanCompleted": bool(notes.get("bodyScanCompleted")),
        "status": notes.get("status") or "LIVE",
        "startedAt": row.get("session_date"),
        "endedAt": notes.get("endedAt"),
        "durationSeconds": row_number(row.get("duration_minutes")) * 60,
        "avgHeartRate": row_float(notes.get("avgHeartRate"), fallback=None),  # type: ignore[arg-type]
        "peakHeartRate": row_float(notes.get("peakHeartRate"), fallback=None),  # type: ignore[arg-type]
        "fatigue": notes.get("fatigue"),
        "recovery": notes.get("recovery"),
        "createdAt": row.get("created_at"),
        "updatedAt": row.get("updated_at") or row.get("created_at"),
    }


def serialize_mobile_series(row: dict[str, Any]) -> dict[str, Any]:
    source = parse_json_object(row.get("source_data"))
    shots = source.get("shots") or []
    if not isinstance(shots, list):
        shots = []
    return {
        "seriesId": str(row.get("score_id") or ""),
        "sessionId": str(source.get("sessionId") or ""),
        "athleteId": str(row.get("athlete_id") or ""),
        "seriesNumber": row_number(source.get("seriesNumber")),
        "shots": shots,
        "total": row_float(row.get("score_value")),
        "avgHeartRate": row_float(source.get("avgHeartRate"), fallback=None),  # type: ignore[arg-type]
        "createdAt": row.get("created_at"),
        "updatedAt": row.get("updated_at"),
    }


def serialize_mobile_reflection(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    payload = parse_json_object(row.get("answer_text"))
    return {
        "reflectionId": str(row.get("answer_id") or ""),
        "sessionId": str(payload.get("sessionId") or ""),
        "athleteId": str(row.get("athlete_id") or ""),
        "mood": payload.get("mood"),
        "whatWorked": payload.get("whatWorked"),
        "whatDidnt": payload.get("whatDidnt"),
        "voiceNoteUrl": payload.get("voiceNoteUrl"),
        "selfRating": row_number(payload.get("selfRating"), fallback=None),  # type: ignore[arg-type]
        "fatigueLevel": row_number(payload.get("fatigueLevel"), fallback=None),  # type: ignore[arg-type]
        "createdAt": row.get("recorded_at") or row.get("created_at"),
        "updatedAt": row.get("recorded_at") or row.get("created_at"),
    }


def ensure_mobile_session_row(athlete_id: str, session_id: str) -> dict[str, Any]:
    ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["shooting_session_log"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("session_id", session_id)
        .limit(1)
        .execute()
    )
    session_row = (response.data or [None])[0]
    if not session_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found.")
    return session_row


def list_mobile_session_series(session_id: str) -> list[dict[str, Any]]:
    supabase = ensure_supabase()
    session_row = (
        supabase.table(APP_TABLES["shooting_session_log"])
        .select("athlete_id")
        .eq("session_id", session_id)
        .limit(1)
        .execute()
    )
    athlete_id = ((session_row.data or [{}])[0]).get("athlete_id")
    if not athlete_id:
        return []
    rows = safe_table_rows(
        APP_TABLES["athlete_scores"],
        supabase.table(APP_TABLES["athlete_scores"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("score_type", "mobile_series")
        .order("created_at"),
    )
    series = [
        serialize_mobile_series(row)
        for row in rows
        if parse_json_object(row.get("source_data")).get("sessionId") == session_id
    ]
    return sorted(series, key=lambda item: item.get("seriesNumber") or 0)


def get_mobile_session_reflection(session_id: str) -> dict[str, Any] | None:
    supabase = ensure_supabase()
    session_row = (
        supabase.table(APP_TABLES["shooting_session_log"])
        .select("athlete_id")
        .eq("session_id", session_id)
        .limit(1)
        .execute()
    )
    athlete_id = ((session_row.data or [{}])[0]).get("athlete_id")
    if not athlete_id:
        return None
    rows = safe_table_rows(
        APP_TABLES["psychology_responses"],
        supabase.table(APP_TABLES["psychology_responses"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("question_id", "MOBILE_SESSION_REFLECTION")
        .order("recorded_at", desc=True),
    )
    for row in rows:
        if parse_json_object(row.get("answer_text")).get("sessionId") == session_id:
            return serialize_mobile_reflection(row)
    return None


def build_mobile_session_summary(session_row: dict[str, Any]) -> dict[str, Any]:
    session = serialize_mobile_session(session_row)
    series = list_mobile_session_series(session["sessionId"])
    all_scores = [normalize_shot_score(score) for item in series for score in item["shots"]]
    total = round(sum(all_scores), 1)
    planned_shots = max(session.get("plannedShots") or len(all_scores), 1)
    average = round(total / len(all_scores), 1) if all_scores else 0
    max_total = planned_shots * 10
    efficiency = round((total / max_total) * 100) if max_total else 0
    best_series = max(series, key=lambda item: item["total"], default=None)
    worst_series = min(series, key=lambda item: item["total"], default=None)
    avg_hr_values = [item["avgHeartRate"] for item in series if item.get("avgHeartRate") is not None]
    avg_hr = round(sum(avg_hr_values) / len(avg_hr_values)) if avg_hr_values else session.get("avgHeartRate")
    key_insight = (
        "Solid baseline performance"
        if efficiency >= 60
        else "Build consistency before increasing load"
    )
    recommendations = [
        "Review your shot sequence for the lowest scoring series",
        "Log your session reflection in journal",
    ]
    if avg_hr and session.get("peakHeartRate") and session["peakHeartRate"] - avg_hr > 15:
        recommendations.insert(0, "Complete a 5-minute breathing cool-down")

    return {
        "session": session,
        "series": series,
        "score": {
            "total": total,
            "maxTotal": max_total,
            "averagePerShot": average,
            "efficiencyPercent": efficiency,
            "bestShot": max(all_scores) if all_scores else None,
            "worstShot": min(all_scores) if all_scores else None,
            "bestSeries": best_series,
            "worstSeries": worst_series,
        },
        "physiology": {
            "avgHeartRate": avg_hr,
            "peakHeartRate": session.get("peakHeartRate"),
            "fatigue": session.get("fatigue"),
            "recovery": session.get("recovery"),
        },
        "mentalState": {
            "reflection": get_mobile_session_reflection(session["sessionId"]),
        },
        "keyInsight": {
            "title": key_insight,
            "message": "Use this as your reference point and look for stable scores across every series.",
        },
        "recommendations": recommendations,
    }


def serialize_app_feedback(row: dict[str, Any], athlete_lookup: dict[str, dict[str, Any]] | None = None) -> CoachFeedbackRecord:
    athlete = (athlete_lookup or {}).get(str(row.get("athlete_id"))) or {}
    technique = row_number(row.get("technique_score"), 0)
    focus = row_number(row.get("focus_score"), 0)
    average = round((technique + focus + row_number(row.get("breathing_score"), 0) + row_number(row.get("posture_score"), 0)) / 4)
    status_label: Literal["Needs Attention", "Progressing", "Strong"] = (
        "Strong" if average >= 8 else "Progressing" if average >= 5 else "Needs Attention"
    )
    return CoachFeedbackRecord(
        feedbackId=str(row.get("feedback_id") or ""),
        athleteId=str(row.get("athlete_id") or ""),
        athleteName=athlete.get("athlete_name") or "Athlete",
        athleteEmail=athlete.get("email") or "",
        coachEmail=str(row.get("coach_uid") or row.get("coach_id") or ""),
        coachName="Coach",
        note=row.get("coach_observations") or row.get("coach_notes") or row.get("strengths") or "",
        recommendation=row.get("training_plan") or row.get("exercise_plan") or row.get("improvement_areas") or "",
        status=status_label,
        createdAt=str(row.get("created_at") or ""),
    )


def seed_psychology_questions() -> None:
    try:
        supabase = get_supabase_admin_client()
        try:
            supabase.table(APP_TABLES["psychology_questions"]).upsert(
                DEFAULT_PSYCHOLOGY_QUESTIONS + MOBILE_PSYCHOLOGY_QUESTIONS,
                on_conflict="question_id",
            ).execute()
        except Exception:
            supabase.table("Psychology_Questions").upsert(
                DEFAULT_PSYCHOLOGY_QUESTIONS + MOBILE_PSYCHOLOGY_QUESTIONS,
                on_conflict="question_id",
            ).execute()
    except HTTPException as exception:
        try:
            supabase.table(APP_TABLES["psychology_questions"]).upsert(
                DEFAULT_PSYCHOLOGY_QUESTIONS + MOBILE_PSYCHOLOGY_QUESTIONS,
                on_conflict="question_id",
            ).execute()
        except Exception:
            supabase.table("Psychology_Questions").upsert(
                DEFAULT_PSYCHOLOGY_QUESTIONS + MOBILE_PSYCHOLOGY_QUESTIONS,
                on_conflict="question_id",
            ).execute()
    except HTTPException as exception:
        # Keep intake usable even before Supabase is configured.
        logger.warning("Skipping psychology question seed because Supabase is not configured: %s", exception.detail)
        return
    except Exception as exception:
        logger.warning("Skipping psychology question seed because Supabase is unavailable: %s", exception)
        return


@app.on_event("startup")
def seed_application_data() -> None:
    try:
        ensure_seed_data()
        if settings.enable_startup_test_mapper:
            assign_existing_records_to_default_coach_for_testing()
        seed_psychology_questions()
    except HTTPException as exception:
        # Allow the API to boot even before local env vars are configured.
        logger.warning("Skipping startup seed because Supabase is not configured: %s", exception.detail)
        return
    except Exception as exception:
        logger.warning("Skipping startup seed because Supabase is unavailable: %s", exception)
        return


@app.get("/api/health")
def healthcheck() -> StatusResponse:
    return StatusResponse(success=True)


@app.get("/api/intake/questions", response_model=PsychologyQuestionsResponse)
def get_psychology_questions(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> PsychologyQuestionsResponse:
    get_authenticated_user(session_token)
    seed_psychology_questions()

    questions = [
        PsychologyQuestionRecord(
            questionId=item["question_id"],
            questionText=item["question_text"],
            category=item["category"],
            questionType=item["question_type"],
        )
        for item in DEFAULT_PSYCHOLOGY_QUESTIONS
    ]
    return PsychologyQuestionsResponse(questions=questions)


@app.get("/api/coach/profile", response_model=CoachProfileResponse)
def get_coach_profile(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachProfileResponse:
    coach_user = ensure_coach_user(session_token)
    return CoachProfileResponse(profile=ensure_coach_profile(coach_user))


@app.patch("/api/coach/profile", response_model=CoachProfileResponse)
def update_coach_profile(
    payload: CoachProfileUpdateInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachProfileResponse:
    coach_user = ensure_coach_user(session_token)
    now = datetime.now(timezone.utc).isoformat()
    update_row = {
        "coach_id": coach_user.email.lower(),
        "email": coach_user.email.lower(),
        "name": payload.name or coach_user.full_name,
        "phone": payload.phone,
        "profile_image": payload.profile_image,
        "specialization": payload.specialization,
        "status": payload.status or "active",
        "updated_at": now,
    }
    try:
        supabase = ensure_supabase()
        existing = safe_table_rows(
            APP_TABLES["coach_profiles"],
            supabase.table(APP_TABLES["coach_profiles"]).select("created_at").eq("email", coach_user.email.lower()).limit(1),
        )
        if not existing:
            update_row["created_at"] = now
        supabase.table(APP_TABLES["coach_profiles"]).upsert(update_row, on_conflict="email").execute()
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to update coach profile: {exception}",
        ) from exception

    return CoachProfileResponse(profile=ensure_coach_profile(coach_user))


@app.get("/api/admin/coaches", response_model=CoachProfilesResponse)
def list_coach_profiles(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachProfilesResponse:
    ensure_admin_user(session_token)
    supabase = ensure_supabase()
    coach_rows = safe_table_rows(
        "App_Users",
        supabase.table("App_Users").select("*").eq("role", "coach").order("full_name"),
    )
    coaches = [ensure_coach_profile(serialize_user_row(row)) for row in coach_rows]
    return CoachProfilesResponse(coaches=coaches)


@app.post("/api/admin/coaches", response_model=CoachProfileResponse, status_code=status.HTTP_201_CREATED)
def create_coach_profile(
    payload: CoachProfileInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachProfileResponse:
    admin_user = ensure_admin_user(session_token)
    email = payload.email.lower()
    existing = get_user_by_email(email)
    if existing and existing.role != "coach":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A non-coach account already uses this email.")
    if not existing and not payload.password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password is required when creating a new coach.")

    coach_user = existing or upsert_user(
        create_user_record(
            email=email,
            full_name=payload.name,
            password=payload.password,
            role="coach",
            coach_code=(payload.coach_code or f"COACH-{uuid4().hex[:8]}").upper(),
        )
    )

    now = datetime.now(timezone.utc).isoformat()
    try:
        supabase = ensure_supabase()
        supabase.table(APP_TABLES["coach_profiles"]).upsert(
            {
                "coach_id": email,
                "name": payload.name,
                "email": email,
                "phone": payload.phone,
                "profile_image": payload.profile_image,
                "specialization": payload.specialization,
                "status": payload.status,
                "created_at": now,
                "updated_at": now,
            },
            on_conflict="email",
        ).execute()
        write_audit_log(
            actor_email=admin_user.email,
            action="coach_profile_created",
            entity_type="coach",
            entity_id=email,
            metadata={"status": payload.status},
        )
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to create coach profile: {exception}") from exception

    return CoachProfileResponse(profile=ensure_coach_profile(coach_user))


@app.patch("/api/admin/coaches/{coach_email}", response_model=CoachProfileResponse)
def admin_update_coach_profile(
    coach_email: str,
    payload: CoachProfileUpdateInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachProfileResponse:
    admin_user = ensure_admin_user(session_token)
    coach_user = get_user_by_email(coach_email.lower())
    if not coach_user or coach_user.role != "coach":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach profile not found.")

    now = datetime.now(timezone.utc).isoformat()
    try:
        supabase = ensure_supabase()
        current = ensure_coach_profile(coach_user)
        supabase.table(APP_TABLES["coach_profiles"]).upsert(
            {
                "coach_id": coach_user.email.lower(),
                "name": payload.name or current.name,
                "email": coach_user.email.lower(),
                "phone": payload.phone if payload.phone is not None else current.phone,
                "profile_image": payload.profile_image if payload.profile_image is not None else current.profile_image,
                "specialization": payload.specialization if payload.specialization is not None else current.specialization,
                "status": payload.status or current.status,
                "updated_at": now,
            },
            on_conflict="email",
        ).execute()
        write_audit_log(
            actor_email=admin_user.email,
            action="coach_profile_updated",
            entity_type="coach",
            entity_id=coach_user.email,
            metadata=payload.model_dump(exclude_none=True, by_alias=True),
        )
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to update coach profile: {exception}") from exception

    return CoachProfileResponse(profile=ensure_coach_profile(coach_user))


@app.post("/api/admin/assignments", response_model=StatusResponse)
def assign_athlete_to_coach(
    payload: AssignmentInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> StatusResponse:
    admin_user = ensure_admin_user(session_token)
    coach = get_user_by_email(payload.coach_email.lower())
    if not coach or coach.role != "coach":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found.")
    coach_key = resolve_dashboard_coach_key(coach)
    if not coach_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This coach is not mapped to a domain coach UUID.")

    supabase = ensure_supabase()
    athlete_result = supabase.table(APP_TABLES["athletes"]).select("*").eq("athlete_id", payload.athlete_id).limit(1).execute()
    athlete_row = (athlete_result.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")

    previous_coach = athlete_row.get("coach_id")
    now = datetime.now(timezone.utc).isoformat()
    supabase.table(APP_TABLES["athletes"]).update({"coach_id": coach_key, "updated_by": admin_user.email}).eq("athlete_id", payload.athlete_id).execute()
    if athlete_row.get("email"):
        student = get_user_by_email(str(athlete_row["email"]).lower())
        if student and student.role == "student":
            upsert_user(
                UserRecord(
                    email=student.email,
                    full_name=student.full_name,
                    role=student.role,
                    salt=student.salt,
                    password_hash=student.password_hash,
                    coach_code=student.coach_code,
                    assignment_status="assigned",
                    assigned_coach_email=coach.email.lower(),
                    assigned_coach_name=coach.full_name,
                    sport=student.sport,
                    focus_area=student.focus_area,
                    date_of_birth=student.date_of_birth,
                    performance_score=student.performance_score,
                )
            )
    try:
        supabase.table(APP_TABLES["coach_assignments"]).insert(
            {
                "assignment_id": str(uuid4()),
                "athlete_id": payload.athlete_id,
                "coach_email": coach.email.lower(),
                "assigned_by": admin_user.email,
                "previous_coach_email": previous_coach,
                "status": "active",
                "created_at": now,
            }
        ).execute()
    except Exception:
        pass

    create_notification(
        recipient_email=coach.email,
        recipient_role="coach",
        title="Athlete assigned",
        message=f"{athlete_row.get('name') or 'An athlete'} is now assigned to your dashboard.",
        notification_type="assignment",
        entity_id=payload.athlete_id,
    )
    write_audit_log(
        actor_email=admin_user.email,
        action="athlete_assigned",
        entity_type="athlete",
        entity_id=payload.athlete_id,
        metadata={"coachEmail": coach.email, "previousCoachEmail": previous_coach},
    )
    return StatusResponse(success=True)


@app.get("/api/notifications", response_model=NotificationsResponse)
def list_notifications(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> NotificationsResponse:
    user = get_authenticated_user(session_token)
    supabase = ensure_supabase()
    query = supabase.table(APP_TABLES["notifications"]).select("*").order("created_at", desc=True).limit(20)
    coach_key = resolve_dashboard_coach_key(user) if user.role == "coach" else None
    if coach_key:
        query = query.or_(f"recipient_email.eq.{user.email.lower()},recipient_coach_id.eq.{coach_key}")
    else:
        query = query.eq("recipient_email", user.email.lower())
    rows = safe_table_rows(
        APP_TABLES["notifications"],
        query,
    )
    notifications = [
        NotificationRecord(
            notificationId=str(row.get("notification_id") or ""),
            recipientEmail=str(row.get("recipient_email") or ""),
            recipientRole=str(row.get("recipient_role") or ""),
            title=str(row.get("title") or ""),
            message=str(row.get("message") or ""),
            type=str(row.get("type") or "info"),
            entityId=row.get("entity_id"),
            readAt=str(row.get("read_at")) if row.get("read_at") else None,
            createdAt=str(row.get("created_at") or ""),
        )
        for row in rows
    ]
    return NotificationsResponse(notifications=notifications)


@app.post("/api/v1/feedback_requests", response_model=FeedbackRequestCreateResponse, status_code=status.HTTP_201_CREATED)
def create_feedback_request_v1(
    payload: FeedbackRequestCreateInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> FeedbackRequestCreateResponse:
    user = get_authenticated_user(session_token)
    if user.role not in {"student", "coach"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only signed-in users can request feedback.")

    supabase = ensure_supabase()
    athlete = (
        supabase.table(APP_TABLES["athletes"])
        .select("athlete_id,coach_id")
        .eq("athlete_id", payload.athlete_id)
        .limit(1)
        .execute()
    )
    athlete_row = (athlete.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if str(athlete_row.get("coach_id") or "") != payload.coach_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Athlete is not assigned to the requested coach.")

    request_row = {
        "request_id": str(uuid4()),
        "athlete_id": payload.athlete_id,
        "session_id": payload.session_id,
        "coach_id": payload.coach_id,
        "status": "PENDING",
        "requested_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table("feedback_requests").insert(request_row).execute()
    return FeedbackRequestCreateResponse(
        requestId=request_row["request_id"],
        status="PENDING",
        message="Feedback request sent to coach",
    )


@app.get("/api/v1/coaches/{coach_id}/notifications", response_model=CoachNotificationsResponse)
def list_coach_notifications_v1(
    coach_id: str,
    unread_only: bool = Query(default=True, alias="unreadOnly"),
    limit: int = Query(default=20, ge=1, le=100),
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachNotificationsResponse:
    coach_user = ensure_coach_user(session_token)
    ensure_coach_owns_coach_id(coach_user, coach_id)
    supabase = ensure_supabase()

    query = (
        supabase.table("notifications")
        .select("notification_id,notification_type,related_athlete_id,related_session_id,message,action_url,created_at,is_read")
        .eq("recipient_coach_id", coach_id)
        .order("created_at", desc=True)
        .limit(limit)
    )
    if unread_only:
        query = query.eq("is_read", False)
    rows = safe_table_rows("notifications", query)

    athlete_ids = [str(row.get("related_athlete_id")) for row in rows if row.get("related_athlete_id")]
    athlete_names: dict[str, str] = {}
    if athlete_ids:
        athlete_rows = safe_table_rows(
            APP_TABLES["athletes"],
            supabase.table(APP_TABLES["athletes"]).select("athlete_id,athlete_name,name").in_("athlete_id", athlete_ids),
        )
        athlete_names = {
            str(row.get("athlete_id")): str(row.get("athlete_name") or row.get("name") or "Athlete")
            for row in athlete_rows
        }

    request_rows = safe_table_rows(
        "feedback_requests",
        supabase.table("feedback_requests").select("request_id,session_id").in_("session_id", [row.get("related_session_id") for row in rows if row.get("related_session_id")]),
    ) if rows else []
    request_by_session = {str(row.get("session_id")): str(row.get("request_id")) for row in request_rows if row.get("session_id")}

    items = [
        CoachNotificationItem(
            notificationId=str(row.get("notification_id") or ""),
            type=str(row.get("notification_type") or "INFO"),
            athleteId=str(row.get("related_athlete_id")) if row.get("related_athlete_id") else None,
            athleteName=athlete_names.get(str(row.get("related_athlete_id"))),
            sessionId=str(row.get("related_session_id")) if row.get("related_session_id") else None,
            requestId=request_by_session.get(str(row.get("related_session_id"))),
            message=str(row.get("message") or ""),
            actionUrl=row.get("action_url"),
            createdAt=str(row.get("created_at") or datetime.now(timezone.utc).isoformat()),
            isRead=bool(row.get("is_read")),
        )
        for row in rows
    ]

    unread_rows = safe_table_rows(
        "notifications",
        supabase.table("notifications").select("notification_id").eq("recipient_coach_id", coach_id).eq("is_read", False),
    )
    return CoachNotificationsResponse(notifications=items, unreadCount=len(unread_rows))


@app.patch("/api/v1/notifications/{notification_id}/mark_read", response_model=NotificationMarkReadResponse)
def mark_notification_read_v1(
    notification_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> NotificationMarkReadResponse:
    coach_user = ensure_coach_user(session_token)
    coach_id = resolve_dashboard_coach_key(coach_user)
    if not coach_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coach mapping not found.")
    supabase = ensure_supabase()
    updated = (
        supabase.table("notifications")
        .update({"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()})
        .eq("notification_id", notification_id)
        .eq("recipient_coach_id", coach_id)
        .execute()
    )
    row = (updated.data or [None])[0]
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    return NotificationMarkReadResponse(
        notificationId=str(row.get("notification_id") or notification_id),
        isRead=bool(row.get("is_read")),
        readAt=str(row.get("read_at")) if row.get("read_at") else None,
    )


@app.get("/api/v1/coaches/available", response_model=CoachOptionsResponse)
def list_available_coaches_v1(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachOptionsResponse:
    _ = ensure_coach_user(session_token)
    supabase = ensure_supabase()
    rows = safe_table_rows(
        "coaches",
        supabase.table("coaches").select("coach_id,coach_name,coach_id_text,specialization").order("coach_name"),
    )
    coaches = [
        CoachOptionItem(
            coachId=str(row.get("coach_id") or ""),
            coachName=str(row.get("coach_name") or "Coach"),
            coachIdText=row.get("coach_id_text"),
            specialization=row.get("specialization"),
        )
        for row in rows
    ]
    return CoachOptionsResponse(coaches=coaches)


@app.get("/api/v1/coaches/{coach_id}/pending_assignments", response_model=PendingAssignmentsResponse)
def list_pending_assignments_v1(
    coach_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> PendingAssignmentsResponse:
    coach_user = ensure_coach_user(session_token)
    ensure_coach_owns_coach_id(coach_user, coach_id)
    supabase = ensure_supabase()
    rows = safe_table_rows(
        "assignment_requests",
        supabase.table("assignment_requests")
        .select("request_id,athlete_id,assigned_coach_id,status,notes,requested_at")
        .eq("status", "PENDING")
        .or_(f"assigned_coach_id.eq.{coach_id},assigned_coach_id.is.null")
        .order("requested_at", desc=True),
    )
    athlete_ids = [str(row.get("athlete_id")) for row in rows if row.get("athlete_id")]
    athlete_rows = safe_table_rows(
        APP_TABLES["athletes"],
        supabase.table(APP_TABLES["athletes"]).select("athlete_id,athlete_name,name").in_("athlete_id", athlete_ids),
    ) if athlete_ids else []
    athlete_name_map = {
        str(row.get("athlete_id")): str(row.get("athlete_name") or row.get("name") or "Athlete")
        for row in athlete_rows
    }
    requests = [
        PendingAssignmentItem(
            requestId=str(row.get("request_id") or ""),
            athleteId=str(row.get("athlete_id") or ""),
            athleteName=athlete_name_map.get(str(row.get("athlete_id")), "Athlete"),
            assignedCoachId=str(row.get("assigned_coach_id")) if row.get("assigned_coach_id") else None,
            status=str(row.get("status") or "PENDING"),
            notes=row.get("notes"),
            requestedAt=str(row.get("requested_at")) if row.get("requested_at") else None,
        )
        for row in rows
    ]
    return PendingAssignmentsResponse(requests=requests)


@app.post("/api/v1/assignments/assign", response_model=AssignAthleteResponse)
def assign_athlete_v1(
    payload: AssignAthleteInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AssignAthleteResponse:
    coach_user = ensure_coach_user(session_token)
    requestor_coach_id = resolve_dashboard_coach_key(coach_user)
    if not requestor_coach_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coach mapping not found.")
    supabase = ensure_supabase()

    athlete_row_result = (
        supabase.table(APP_TABLES["athletes"])
        .select("athlete_id,email,name,athlete_name")
        .eq("athlete_id", payload.athlete_id)
        .limit(1)
        .execute()
    )
    athlete_row = (athlete_row_result.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")

    assignment_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    try:
        request_rows = safe_table_rows(
            "assignment_requests",
            supabase.table("assignment_requests")
            .select("request_id,assigned_coach_id,status")
            .eq("request_id", payload.request_id)
            .limit(1),
        )
        request_row = request_rows[0] if request_rows else None
        if not request_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment request not found.")
        if request_row.get("status") != "PENDING":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignment request is not pending.")
        target_coach_id = str(request_row.get("assigned_coach_id") or "")
        if target_coach_id and target_coach_id != str(requestor_coach_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This assignment request belongs to another coach.")

        supabase.table(APP_TABLES["athletes"]).update({"coach_id": payload.assigned_coach_id}).eq("athlete_id", payload.athlete_id).execute()
        safe_table_rows(
            "coach_assignments",
            supabase.table("coach_assignments").insert(
                {
                    "assignment_id": assignment_id,
                    "coach_id": payload.assigned_coach_id,
                    "athlete_id": payload.athlete_id,
                    "is_active": True,
                }
            ),
        )
        supabase.table("assignment_requests").update(
            {
                "requesting_coach_id": requestor_coach_id,
                "assigned_coach_id": payload.assigned_coach_id,
                "status": "ASSIGNED",
                "notes": payload.notes,
                "assigned_at": now,
            }
        ).eq("request_id", payload.request_id).execute()
        athlete_email = str(athlete_row.get("email") or "").lower()
        assigned_coach_name = None
        coach_rows = safe_table_rows(
            "coaches",
            supabase.table("coaches").select("coach_name").eq("coach_id", payload.assigned_coach_id).limit(1),
        )
        if coach_rows:
            assigned_coach_name = str(coach_rows[0].get("coach_name") or "Coach")
        if athlete_email:
            supabase.table("App_Users").update(
                {
                    "assignment_status": "assigned",
                    "assigned_coach_email": get_domain_coach_email(payload.assigned_coach_id),
                    "assigned_coach_name": assigned_coach_name,
                    "updated_at": now,
                }
            ).eq("email", athlete_email).execute()
            create_notification(
                recipient_email=athlete_email,
                recipient_role="student",
                title="Coach assigned",
                message=f"You have been assigned to {assigned_coach_name or 'your coach'}.",
                notification_type="ASSIGNED_TO_COACH",
                entity_id=payload.athlete_id,
                related_athlete_id=payload.athlete_id,
            )
    except Exception as exception:
        if isinstance(exception, HTTPException):
            raise exception
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to assign athlete: {exception}") from exception

    write_audit_log(
        actor_email=coach_user.email,
        action="athlete_assigned_v1",
        entity_type="assignment_request",
        entity_id=payload.request_id,
        metadata={"athleteId": payload.athlete_id, "assignedCoachId": payload.assigned_coach_id},
    )
    return AssignAthleteResponse(success=True, assignmentId=assignment_id)


@app.get("/api/v1/athletes/{athlete_id}/assignment_status", response_model=AthleteAssignmentStatusResponse)
def get_athlete_assignment_status_v1(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AthleteAssignmentStatusResponse:
    _ = get_authenticated_user(session_token)
    supabase = ensure_supabase()
    rows = safe_table_rows(
        "assignment_requests",
        supabase.table("assignment_requests")
        .select("athlete_id,assigned_coach_id,status,requested_at,assigned_at")
        .eq("athlete_id", athlete_id)
        .order("requested_at", desc=True)
        .limit(1),
    )
    row = rows[0] if rows else None
    if not row:
        return AthleteAssignmentStatusResponse(
            athleteId=athlete_id,
            status="UNASSIGNED",
            assignedCoachId=None,
            assignedCoachName=None,
            requestedAt=None,
            assignedAt=None,
        )

    coach_name = None
    assigned_coach_id = row.get("assigned_coach_id")
    if assigned_coach_id:
        coach_rows = safe_table_rows(
            "coaches",
            supabase.table("coaches").select("coach_name").eq("coach_id", assigned_coach_id).limit(1),
        )
        coach_name = str(coach_rows[0].get("coach_name")) if coach_rows else None

    return AthleteAssignmentStatusResponse(
        athleteId=str(row.get("athlete_id") or athlete_id),
        status=str(row.get("status") or "UNASSIGNED"),
        assignedCoachId=str(assigned_coach_id) if assigned_coach_id else None,
        assignedCoachName=coach_name,
        requestedAt=str(row.get("requested_at")) if row.get("requested_at") else None,
        assignedAt=str(row.get("assigned_at")) if row.get("assigned_at") else None,
    )


def average_metric(values: list[float | None]) -> float | None:
    real_values = [value for value in values if isinstance(value, (int, float))]
    return round(sum(real_values) / len(real_values), 2) if real_values else None


def score_lookup_for_row(athlete_row: dict[str, Any]) -> dict[str, float]:
    values: dict[str, float] = {}
    for score in get_scores_for_athlete(athlete_row):
        current = values.get(score.score_type)
        if current is None:
            values[score.score_type] = round(float(score.score_value), 2)
    return values


def score_value(values: dict[str, float], *keys: str) -> float | None:
    for key in keys:
        value = values.get(key)
        if value is not None:
            return round(float(value), 2)
    return None


def fatigue_burden_from_inputs(score_values: dict[str, float], physiology_row: dict[str, Any] | None = None) -> float | None:
    physiology_row = physiology_row or {}
    if physiology_row.get("fatigue_level") is not None:
        return round(min(100, max(0, row_float(physiology_row.get("fatigue_level"), 0) * 10)), 2)
    fatigue_control = score_value(score_values, "fatigue")
    if fatigue_control is None:
        return None
    return round(min(100, max(0, 100 - fatigue_control)), 2)


def is_recent_date(value: str | None, days: int = 7) -> bool:
    if not value:
        return False
    try:
        normalized = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed >= datetime.now(timezone.utc) - timedelta(days=days)
    except ValueError:
        return False


def derive_status(
    *,
    performance: float | None,
    readiness: float | None,
    stress: float | None,
    fatigue: float | None,
    recovery: float | None,
) -> Literal["Strong", "Stable", "Needs Attention", "At Risk"]:
    if (stress is not None and stress >= 80) or (fatigue is not None and fatigue >= 80) or (recovery is not None and recovery < 35):
        return "At Risk"
    if (performance is not None and performance < 60) or (readiness is not None and readiness < 50):
        return "Needs Attention"
    if (performance is not None and performance >= 80) and (readiness is None or readiness >= 70) and (stress is None or stress < 65):
        return "Strong"
    return "Stable"


def derive_trend(history_values: list[float]) -> Literal["Improving", "Declining", "Stable"]:
    if len(history_values) < 2:
        return "Stable"
    delta = history_values[0] - history_values[-1]
    if delta >= 5:
        return "Improving"
    if delta <= -5:
        return "Declining"
    return "Stable"


def risk_reasons_for_row(
    *,
    performance: float | None,
    readiness: float | None,
    focus: float | None,
    stress: float | None,
    fatigue: float | None,
    recovery: float | None,
    sleep_hours: float | None,
    last_session_date: str | None,
    trend: str,
) -> list[str]:
    reasons: list[str] = []
    if stress is not None and stress >= 70:
        reasons.append("High stress")
    if fatigue is not None and fatigue >= 70:
        reasons.append("High fatigue")
    if recovery is not None and recovery < 50:
        reasons.append("Low recovery")
    if readiness is not None and readiness < 55:
        reasons.append("Low readiness")
    if focus is not None and focus < 55:
        reasons.append("Low focus")
    if performance is not None and performance < 60:
        reasons.append("Low performance")
    if sleep_hours is not None and sleep_hours < 6:
        reasons.append("Poor sleep")
    if trend == "Declining":
        reasons.append("Declining trend")
    if not is_recent_date(last_session_date):
        reasons.append("No recent activity")
    return reasons


def suggested_action_for_reasons(reasons: list[str]) -> str:
    reason_text = " ".join(reasons).lower()
    if "stress" in reason_text or "focus" in reason_text:
        return "Schedule a short regulation check-in and add a breathing/focus drill before the next session."
    if "fatigue" in reason_text or "recovery" in reason_text or "sleep" in reason_text:
        return "Reduce load for the next session and review sleep, recovery, and hydration habits."
    if "performance" in reason_text or "declining" in reason_text:
        return "Review recent session data and assign one technical correction for the next practice."
    if "activity" in reason_text:
        return "Contact the athlete and confirm the next planned training session."
    return "Review the athlete detail dashboard and add coach feedback."


@app.get("/api/v1/coaches/{coach_id}/dashboard", response_model=CoachDashboardV1Response)
def get_coach_dashboard_v1(
    coach_id: str,
    gender: str | None = Query(default=None),
    min_score: float | None = Query(default=None, alias="minScore"),
    max_score: float | None = Query(default=None, alias="maxScore"),
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachDashboardV1Response:
    coach_user = ensure_coach_user(session_token)
    ensure_coach_owns_coach_id(coach_user, coach_id)
    supabase = ensure_supabase()
    athletes = list_coach_athletes(search="", athlete_ids="", include_pending=True, session_token=session_token).athletes

    rows: list[CoachDashboardAthleteRow] = []
    for athlete in athletes:
        athlete_row = resolve_athlete_row_by_identifier(supabase, athlete.athlete_id) or {"athlete_id": athlete.athlete_id}
        score_map = score_lookup_for_row(athlete_row)
        latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [athlete.athlete_id], "recorded_date").get(athlete.athlete_id) or {}
        session_rows = safe_table_rows(
            APP_TABLES["shooting_session_log"],
            supabase.table(APP_TABLES["shooting_session_log"])
            .select("*")
            .eq("athlete_id", athlete.athlete_id)
            .order("session_date", desc=True)
            .limit(5),
        )

        history_scores: list[float] = []
        for session_row in session_rows[:5]:
            try:
                summary = build_mobile_session_summary(session_row)
                value = row_float(summary.get("score", {}).get("efficiencyPercent"), fallback=None)  # type: ignore[arg-type]
                if value is not None:
                    history_scores.append(value)
            except Exception:
                continue

        score = athlete.overall_score or score_value(score_map, "overall", "performance")
        readiness = score_value(score_map, "readiness")
        focus = score_value(score_map, "focus", "mental_score")
        fatigue = fatigue_burden_from_inputs(score_map, latest_physiology)
        recovery = athlete.latest_recovery_score or score_value(score_map, "recovery")
        stress = athlete.latest_stress_score or score_value(score_map, "stress")
        sleep_hours = row_float(latest_physiology.get("sleep_hours"), fallback=None)  # type: ignore[arg-type]
        resting_hr = row_float(latest_physiology.get("resting_heart_rate") or latest_physiology.get("resting_hr"), fallback=None)  # type: ignore[arg-type]
        hrv = row_float(latest_physiology.get("rmssd") or latest_physiology.get("hrv") or latest_physiology.get("hrv_ms"), fallback=None)  # type: ignore[arg-type]
        session_count = len(session_rows)
        discipline = score_value(score_map, "discipline", "consistency")
        if discipline is None:
            discipline_parts = [
                min(100, session_count * 18),
                recovery,
                (100 - stress) if stress is not None else None,
                (100 - fatigue) if fatigue is not None else None,
            ]
            discipline = average_metric(discipline_parts)
        trend = derive_trend(history_scores or ([score] if score is not None else []))
        status_value = derive_status(
            performance=score,
            readiness=readiness,
            stress=stress,
            fatigue=fatigue,
            recovery=recovery,
        )
        reasons = risk_reasons_for_row(
            performance=score,
            readiness=readiness,
            focus=focus,
            stress=stress,
            fatigue=fatigue,
            recovery=recovery,
            sleep_hours=sleep_hours,
            last_session_date=athlete.latest_session_date,
            trend=trend,
        )
        category = "Pending" if score is None else ("Strong" if score >= 80 else "Stable" if score >= 60 else "Needs Attention")
        row = CoachDashboardAthleteRow(
            athleteId=athlete.athlete_id,
            athleteName=athlete.name,
            sport=athlete.latest_training_type or "Shooting",
            discipline=athlete.academy_id or "Performance",
            gender=athlete.gender,
            age=athlete.age,
            score=score,
            readinessScore=readiness,
            focusScore=focus,
            disciplineScore=discipline,
            scoreCategory=category,
            status=status_value,
            trend=trend,
            latestStress=stress,
            restingHr=resting_hr,
            hrvIndicator=hrv,
            fatigueScore=fatigue,
            latestRecovery=recovery,
            sleepHours=sleep_hours,
            lastSessionDate=athlete.latest_session_date,
            riskScore=min(100, len(reasons) * 18),
            riskReasons=reasons,
            suggestedAction=suggested_action_for_reasons(reasons) if reasons else None,
        )
        rows.append(row)

    if gender:
        rows = [row for row in rows if (row.gender or "").lower() == gender.lower()]
    if min_score is not None:
        rows = [row for row in rows if row.score is not None and row.score >= min_score]
    if max_score is not None:
        rows = [row for row in rows if row.score is not None and row.score <= max_score]

    scores = [row.score for row in rows if row.score is not None]
    distribution = {
        "strong": len([value for value in scores if value >= 80]),
        "progressing": len([value for value in scores if 60 <= value < 80]),
        "needsAttention": len([value for value in scores if value < 60]),
        "pending": len([row for row in rows if row.score is None]),
    }
    risk_queue = [
        CoachDashboardRiskItem(
            athleteId=row.athlete_id,
            athleteName=row.athlete_name,
            severity="High" if row.risk_score >= 54 else "Medium" if row.risk_score >= 18 else "Low",
            reasons=row.risk_reasons,
            suggestedAction=row.suggested_action or "Review athlete detail dashboard.",
        )
        for row in sorted(rows, key=lambda item: item.risk_score, reverse=True)
        if row.risk_reasons
    ][:8]
    alerts = [f"{item.athlete_name}: {', '.join(item.reasons[:2])}" for item in risk_queue]
    top_performers = sorted(rows, key=lambda row: (row.score or -1, row.latest_recovery or -1), reverse=True)[:5]
    most_disciplined = sorted(rows, key=lambda row: (row.discipline_score or -1, row.score or -1), reverse=True)[:5]
    healthy_focused = sorted(
        rows,
        key=lambda row: (
            row.latest_recovery or -1,
            row.focus_score or -1,
            -(row.latest_stress or 100),
            -(row.fatigue_score or 100),
        ),
        reverse=True,
    )[:5]
    mapping_points = [
        CoachDashboardScatterPoint(
            athleteId=row.athlete_id,
            athleteName=row.athlete_name,
            performance=row.score,
            stress=row.latest_stress,
            fatigue=row.fatigue_score,
            readiness=row.readiness_score,
            sleep=row.sleep_hours,
            restingHr=row.resting_hr,
            hrvIndicator=row.hrv_indicator,
            focus=row.focus_score,
            consistency=row.discipline_score,
        )
        for row in rows
    ]
    insights = [
        CoachDashboardInsightItem(
            title="Attention queue",
            insightText=f"{len(risk_queue)} athletes need coach review today.",
            category="risk",
            score=float(len(risk_queue)),
            priority="High" if len(risk_queue) >= 3 else "Medium" if risk_queue else "Low",
        ),
        CoachDashboardInsightItem(
            title="Performance baseline",
            insightText="Team average performance is stable." if scores and average_metric(scores) and average_metric(scores) >= 60 else "Team performance needs a baseline review.",
            category="performance",
            score=average_metric(scores),
            priority="Medium",
        ),
    ]
    insight_rows = safe_table_rows(
        "athlete_insights",
        supabase.table("athlete_insights")
        .select("title,insight_text,category,score,priority,created_at")
        .in_("athlete_id", [row.athlete_id for row in rows])
        .order("created_at", desc=True)
        .limit(6),
    )
    insights.extend(
        [
            CoachDashboardInsightItem(
                title=str(row.get("title") or "Coach insight"),
                insightText=str(row.get("insight_text") or ""),
                category=str(row.get("category") or "insight"),
                score=row_float(row.get("score"), fallback=None),  # type: ignore[arg-type]
                priority=row.get("priority") if row.get("priority") in {"High", "Medium", "Low"} else "Medium",
            )
            for row in insight_rows
            if row.get("insight_text")
        ]
    )

    payload = CoachDashboardV1Payload(
        coachId=coach_id,
        totals={
            "totalAssignedAthletes": len(rows),
            "activeAthletes": len([row for row in rows if is_recent_date(row.last_session_date)]),
            "inactiveAthletes": len([row for row in rows if not is_recent_date(row.last_session_date)]),
            "newRegistrations": len([athlete for athlete in athletes if is_recent_date(athlete.created_at)]),
            "athletesNeedingAttention": len([row for row in rows if row.status in {"Needs Attention", "At Risk"}]),
            "topPerformers": len([row for row in rows if row.status == "Strong"]),
            "mostDisciplined": len([row for row in rows if (row.discipline_score or 0) >= 75]),
        },
        averageScore=round(sum(scores) / len(scores), 2) if scores else None,
        averageReadiness=average_metric([row.readiness_score for row in rows]),
        averageFatigue=average_metric([row.fatigue_score for row in rows]),
        averageStress=average_metric([row.latest_stress for row in rows]),
        scoreDistribution=distribution,
        athletes=rows,
        topPerformers=top_performers,
        mostDisciplined=most_disciplined,
        healthyFocused=healthy_focused,
        riskQueue=risk_queue,
        mapping={
            "performanceVsFatigue": mapping_points,
            "performanceVsStress": mapping_points,
            "performanceVsHeartRate": mapping_points,
            "performanceVsHrv": mapping_points,
            "performanceVsSleep": mapping_points,
            "readinessVsPerformance": mapping_points,
            "focusVsConsistency": mapping_points,
        },
        insights=insights,
        alerts=alerts,
    )
    return CoachDashboardV1Response(dashboard=payload)


@app.get("/api/v1/athletes/{athlete_id}/full_profile", response_model=AthleteFullProfileV1Response)
def get_athlete_full_profile_v1(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AthleteFullProfileV1Response:
    detail = get_coach_athlete_detail(athlete_id=athlete_id, session_token=session_token).athlete
    feedback = list_coach_athlete_feedback(athlete_id=athlete_id, session_token=session_token).feedback
    detail["feedbackHistory"] = [item.model_dump(by_alias=True) for item in feedback]
    return AthleteFullProfileV1Response(athlete=detail)


@app.post("/api/v1/coach_feedback", response_model=CoachFeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_coach_feedback_v1(
    payload: V1CoachFeedbackInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachFeedbackResponse:
    coach_user = ensure_coach_user(session_token)
    coach_id = resolve_dashboard_coach_key(coach_user)
    if not coach_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coach mapping not found.")

    supabase = ensure_supabase()
    request_row_result = (
        supabase.table("feedback_requests")
        .select("*")
        .eq("request_id", payload.request_id)
        .eq("coach_id", coach_id)
        .limit(1)
        .execute()
    )
    request_row = (request_row_result.data or [None])[0]
    if not request_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback request not found.")
    if str(request_row.get("status") or "").upper() != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback request is not pending.")

    athlete_result = (
        supabase.table(APP_TABLES["athletes"])
        .select("*")
        .eq("athlete_id", payload.athlete_id)
        .limit(1)
        .execute()
    )
    athlete_row = (athlete_result.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if str(athlete_row.get("coach_id") or "") != str(coach_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Athlete is not assigned to this coach.")

    feedback_id = str(uuid4())
    feedback_item = {
        "feedback_id": feedback_id,
        "athlete_id": athlete_row["athlete_id"],
        "athlete_name": athlete_row.get("athlete_name") or athlete_row.get("name") or "Athlete",
        "athlete_email": athlete_row.get("email") or "",
        "coach_email": coach_user.email,
        "coach_name": coach_user.full_name,
        "note": payload.note,
        "recommendation": payload.recommendation,
        "status": payload.status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table(APP_TABLES["coach_feedback"]).insert(feedback_item).execute()
    supabase.table("feedback_requests").update(
        {
            "status": "COMPLETED",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "feedback_id": feedback_id,
        }
    ).eq("request_id", payload.request_id).execute()

    return CoachFeedbackResponse(
        feedback=serialize_feedback_item(
            {
                "feedbackId": feedback_item["feedback_id"],
                "athleteId": feedback_item["athlete_id"],
                "athleteName": feedback_item["athlete_name"],
                "athleteEmail": feedback_item["athlete_email"],
                "coachEmail": feedback_item["coach_email"],
                "coachName": feedback_item["coach_name"],
                "note": feedback_item["note"],
                "recommendation": feedback_item["recommendation"],
                "status": feedback_item["status"],
                "createdAt": feedback_item["created_at"],
            }
        )
    )


@app.post("/api/notifications/{notification_id}/read", response_model=StatusResponse)
def mark_notification_read(
    notification_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> StatusResponse:
    user = get_authenticated_user(session_token)
    try:
        supabase = ensure_supabase()
        update = {"read_at": datetime.now(timezone.utc).isoformat(), "is_read": True}
        query = supabase.table(APP_TABLES["notifications"]).update(update).eq("notification_id", notification_id)
        coach_key = resolve_dashboard_coach_key(user) if user.role == "coach" else None
        if coach_key:
            query = query.or_(f"recipient_email.eq.{user.email.lower()},recipient_coach_id.eq.{coach_key}")
        else:
            query = query.eq("recipient_email", user.email.lower())
        query.execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to update notification: {exception}") from exception
    return StatusResponse(success=True)


@app.get("/api/coach/profile", response_model=CoachProfileResponse)
def get_coach_profile(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachProfileResponse:
    coach_user = ensure_coach_user(session_token)
    return CoachProfileResponse(profile=ensure_coach_profile(coach_user))


@app.patch("/api/coach/profile", response_model=CoachProfileResponse)
def update_coach_profile(
    payload: CoachProfileUpdateInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachProfileResponse:
    coach_user = ensure_coach_user(session_token)
    now = datetime.now(timezone.utc).isoformat()
    update_row = {
        "coach_id": coach_user.email.lower(),
        "email": coach_user.email.lower(),
        "name": payload.name or coach_user.full_name,
        "phone": payload.phone,
        "profile_image": payload.profile_image,
        "specialization": payload.specialization,
        "status": payload.status or "active",
        "updated_at": now,
    }
    try:
        supabase = ensure_supabase()
        existing = safe_table_rows(
            APP_TABLES["coach_profiles"],
            supabase.table(APP_TABLES["coach_profiles"]).select("created_at").eq("email", coach_user.email.lower()).limit(1),
        )
        if not existing:
            update_row["created_at"] = now
        supabase.table(APP_TABLES["coach_profiles"]).upsert(update_row, on_conflict="email").execute()
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to update coach profile: {exception}",
        ) from exception

    return CoachProfileResponse(profile=ensure_coach_profile(coach_user))


@app.get("/api/admin/coaches", response_model=CoachProfilesResponse)
def list_coach_profiles(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachProfilesResponse:
    ensure_admin_user(session_token)
    supabase = ensure_supabase()
    coach_rows = safe_table_rows(
        "App_Users",
        supabase.table("App_Users").select("*").eq("role", "coach").order("full_name"),
    )
    coaches = [ensure_coach_profile(serialize_user_row(row)) for row in coach_rows]
    return CoachProfilesResponse(coaches=coaches)


@app.post("/api/admin/coaches", response_model=CoachProfileResponse, status_code=status.HTTP_201_CREATED)
def create_coach_profile(
    payload: CoachProfileInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachProfileResponse:
    admin_user = ensure_admin_user(session_token)
    email = payload.email.lower()
    existing = get_user_by_email(email)
    if existing and existing.role != "coach":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A non-coach account already uses this email.")
    if not existing and not payload.password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password is required when creating a new coach.")

    coach_user = existing or upsert_user(
        create_user_record(
            email=email,
            full_name=payload.name,
            password=payload.password,
            role="coach",
            coach_code=(payload.coach_code or f"COACH-{uuid4().hex[:8]}").upper(),
        )
    )

    now = datetime.now(timezone.utc).isoformat()
    try:
        supabase = ensure_supabase()
        supabase.table(APP_TABLES["coach_profiles"]).upsert(
            {
                "coach_id": email,
                "name": payload.name,
                "email": email,
                "phone": payload.phone,
                "profile_image": payload.profile_image,
                "specialization": payload.specialization,
                "status": payload.status,
                "created_at": now,
                "updated_at": now,
            },
            on_conflict="email",
        ).execute()
        write_audit_log(
            actor_email=admin_user.email,
            action="coach_profile_created",
            entity_type="coach",
            entity_id=email,
            metadata={"status": payload.status},
        )
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to create coach profile: {exception}") from exception

    return CoachProfileResponse(profile=ensure_coach_profile(coach_user))


@app.patch("/api/admin/coaches/{coach_email}", response_model=CoachProfileResponse)
def admin_update_coach_profile(
    coach_email: str,
    payload: CoachProfileUpdateInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachProfileResponse:
    admin_user = ensure_admin_user(session_token)
    coach_user = get_user_by_email(coach_email.lower())
    if not coach_user or coach_user.role != "coach":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach profile not found.")

    now = datetime.now(timezone.utc).isoformat()
    try:
        supabase = ensure_supabase()
        current = ensure_coach_profile(coach_user)
        supabase.table(APP_TABLES["coach_profiles"]).upsert(
            {
                "coach_id": coach_user.email.lower(),
                "name": payload.name or current.name,
                "email": coach_user.email.lower(),
                "phone": payload.phone if payload.phone is not None else current.phone,
                "profile_image": payload.profile_image if payload.profile_image is not None else current.profile_image,
                "specialization": payload.specialization if payload.specialization is not None else current.specialization,
                "status": payload.status or current.status,
                "updated_at": now,
            },
            on_conflict="email",
        ).execute()
        write_audit_log(
            actor_email=admin_user.email,
            action="coach_profile_updated",
            entity_type="coach",
            entity_id=coach_user.email,
            metadata=payload.model_dump(exclude_none=True, by_alias=True),
        )
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to update coach profile: {exception}") from exception

    return CoachProfileResponse(profile=ensure_coach_profile(coach_user))


@app.post("/api/admin/assignments", response_model=StatusResponse)
def assign_athlete_to_coach(
    payload: AssignmentInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> StatusResponse:
    admin_user = ensure_admin_user(session_token)
    coach = get_user_by_email(payload.coach_email.lower())
    if not coach or coach.role != "coach":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found.")
    coach_key = resolve_dashboard_coach_key(coach)
    if not coach_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This coach is not mapped to a domain coach UUID.")

    supabase = ensure_supabase()
    athlete_result = supabase.table(APP_TABLES["athletes"]).select("*").eq("athlete_id", payload.athlete_id).limit(1).execute()
    athlete_row = (athlete_result.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")

    previous_coach = athlete_row.get("coach_id")
    now = datetime.now(timezone.utc).isoformat()
    supabase.table(APP_TABLES["athletes"]).update({"coach_id": coach_key, "updated_by": admin_user.email}).eq("athlete_id", payload.athlete_id).execute()
    if athlete_row.get("email"):
        student = get_user_by_email(str(athlete_row["email"]).lower())
        if student and student.role == "student":
            upsert_user(
                UserRecord(
                    email=student.email,
                    full_name=student.full_name,
                    role=student.role,
                    salt=student.salt,
                    password_hash=student.password_hash,
                    coach_code=student.coach_code,
                    assignment_status="assigned",
                    assigned_coach_email=coach.email.lower(),
                    assigned_coach_name=coach.full_name,
                    sport=student.sport,
                    focus_area=student.focus_area,
                    date_of_birth=student.date_of_birth,
                    performance_score=student.performance_score,
                )
            )
    try:
        supabase.table(APP_TABLES["coach_assignments"]).insert(
            {
                "assignment_id": str(uuid4()),
                "athlete_id": payload.athlete_id,
                "coach_email": coach.email.lower(),
                "assigned_by": admin_user.email,
                "previous_coach_email": previous_coach,
                "status": "active",
                "created_at": now,
            }
        ).execute()
    except Exception:
        pass

    create_notification(
        recipient_email=coach.email,
        recipient_role="coach",
        title="Athlete assigned",
        message=f"{athlete_row.get('name') or 'An athlete'} is now assigned to your dashboard.",
        notification_type="assignment",
        entity_id=payload.athlete_id,
    )
    write_audit_log(
        actor_email=admin_user.email,
        action="athlete_assigned",
        entity_type="athlete",
        entity_id=payload.athlete_id,
        metadata={"coachEmail": coach.email, "previousCoachEmail": previous_coach},
    )
    return StatusResponse(success=True)


@app.get("/api/notifications", response_model=NotificationsResponse)
def list_notifications(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> NotificationsResponse:
    user = get_authenticated_user(session_token)
    supabase = ensure_supabase()
    query = supabase.table(APP_TABLES["notifications"]).select("*").order("created_at", desc=True).limit(20)
    coach_key = resolve_dashboard_coach_key(user) if user.role == "coach" else None
    if coach_key:
        query = query.or_(f"recipient_email.eq.{user.email.lower()},recipient_coach_id.eq.{coach_key}")
    else:
        query = query.eq("recipient_email", user.email.lower())
    rows = safe_table_rows(
        APP_TABLES["notifications"],
        query,
    )
    notifications = [
        NotificationRecord(
            notificationId=str(row.get("notification_id") or ""),
            recipientEmail=str(row.get("recipient_email") or ""),
            recipientRole=str(row.get("recipient_role") or ""),
            title=str(row.get("title") or ""),
            message=str(row.get("message") or ""),
            type=str(row.get("type") or "info"),
            entityId=row.get("entity_id"),
            readAt=str(row.get("read_at")) if row.get("read_at") else None,
            createdAt=str(row.get("created_at") or ""),
        )
        for row in rows
    ]
    return NotificationsResponse(notifications=notifications)


@app.post("/api/v1/feedback_requests", response_model=FeedbackRequestCreateResponse, status_code=status.HTTP_201_CREATED)
def create_feedback_request_v1(
    payload: FeedbackRequestCreateInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> FeedbackRequestCreateResponse:
    user = get_authenticated_user(session_token)
    if user.role not in {"student", "coach"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only signed-in users can request feedback.")

    supabase = ensure_supabase()
    athlete = (
        supabase.table(APP_TABLES["athletes"])
        .select("athlete_id,coach_id")
        .eq("athlete_id", payload.athlete_id)
        .limit(1)
        .execute()
    )
    athlete_row = (athlete.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if str(athlete_row.get("coach_id") or "") != payload.coach_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Athlete is not assigned to the requested coach.")

    request_row = {
        "request_id": str(uuid4()),
        "athlete_id": payload.athlete_id,
        "session_id": payload.session_id,
        "coach_id": payload.coach_id,
        "status": "PENDING",
        "requested_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table("feedback_requests").insert(request_row).execute()
    return FeedbackRequestCreateResponse(
        requestId=request_row["request_id"],
        status="PENDING",
        message="Feedback request sent to coach",
    )


@app.get("/api/v1/coaches/{coach_id}/notifications", response_model=CoachNotificationsResponse)
def list_coach_notifications_v1(
    coach_id: str,
    unread_only: bool = Query(default=True, alias="unreadOnly"),
    limit: int = Query(default=20, ge=1, le=100),
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachNotificationsResponse:
    coach_user = ensure_coach_user(session_token)
    ensure_coach_owns_coach_id(coach_user, coach_id)
    supabase = ensure_supabase()

    query = (
        supabase.table("notifications")
        .select("notification_id,notification_type,related_athlete_id,related_session_id,message,action_url,created_at,is_read")
        .eq("recipient_coach_id", coach_id)
        .order("created_at", desc=True)
        .limit(limit)
    )
    if unread_only:
        query = query.eq("is_read", False)
    rows = safe_table_rows("notifications", query)

    athlete_ids = [str(row.get("related_athlete_id")) for row in rows if row.get("related_athlete_id")]
    athlete_names: dict[str, str] = {}
    if athlete_ids:
        athlete_rows = safe_table_rows(
            APP_TABLES["athletes"],
            supabase.table(APP_TABLES["athletes"]).select("athlete_id,athlete_name,name").in_("athlete_id", athlete_ids),
        )
        athlete_names = {
            str(row.get("athlete_id")): str(row.get("athlete_name") or row.get("name") or "Athlete")
            for row in athlete_rows
        }

    request_rows = safe_table_rows(
        "feedback_requests",
        supabase.table("feedback_requests").select("request_id,session_id").in_("session_id", [row.get("related_session_id") for row in rows if row.get("related_session_id")]),
    ) if rows else []
    request_by_session = {str(row.get("session_id")): str(row.get("request_id")) for row in request_rows if row.get("session_id")}

    items = [
        CoachNotificationItem(
            notificationId=str(row.get("notification_id") or ""),
            type=str(row.get("notification_type") or "INFO"),
            athleteId=str(row.get("related_athlete_id")) if row.get("related_athlete_id") else None,
            athleteName=athlete_names.get(str(row.get("related_athlete_id"))),
            sessionId=str(row.get("related_session_id")) if row.get("related_session_id") else None,
            requestId=request_by_session.get(str(row.get("related_session_id"))),
            message=str(row.get("message") or ""),
            actionUrl=row.get("action_url"),
            createdAt=str(row.get("created_at") or datetime.now(timezone.utc).isoformat()),
            isRead=bool(row.get("is_read")),
        )
        for row in rows
    ]

    unread_rows = safe_table_rows(
        "notifications",
        supabase.table("notifications").select("notification_id").eq("recipient_coach_id", coach_id).eq("is_read", False),
    )
    return CoachNotificationsResponse(notifications=items, unreadCount=len(unread_rows))


@app.patch("/api/v1/notifications/{notification_id}/mark_read", response_model=NotificationMarkReadResponse)
def mark_notification_read_v1(
    notification_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> NotificationMarkReadResponse:
    coach_user = ensure_coach_user(session_token)
    coach_id = resolve_dashboard_coach_key(coach_user)
    if not coach_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coach mapping not found.")
    supabase = ensure_supabase()
    updated = (
        supabase.table("notifications")
        .update({"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()})
        .eq("notification_id", notification_id)
        .eq("recipient_coach_id", coach_id)
        .execute()
    )
    row = (updated.data or [None])[0]
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    return NotificationMarkReadResponse(
        notificationId=str(row.get("notification_id") or notification_id),
        isRead=bool(row.get("is_read")),
        readAt=str(row.get("read_at")) if row.get("read_at") else None,
    )


@app.get("/api/v1/coaches/available", response_model=CoachOptionsResponse)
def list_available_coaches_v1(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachOptionsResponse:
    _ = ensure_coach_user(session_token)
    supabase = ensure_supabase()
    rows = safe_table_rows(
        "coaches",
        supabase.table("coaches").select("coach_id,coach_name,coach_id_text,specialization").order("coach_name"),
    )
    coaches = [
        CoachOptionItem(
            coachId=str(row.get("coach_id") or ""),
            coachName=str(row.get("coach_name") or "Coach"),
            coachIdText=row.get("coach_id_text"),
            specialization=row.get("specialization"),
        )
        for row in rows
    ]
    return CoachOptionsResponse(coaches=coaches)


@app.get("/api/v1/coaches/{coach_id}/pending_assignments", response_model=PendingAssignmentsResponse)
def list_pending_assignments_v1(
    coach_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> PendingAssignmentsResponse:
    coach_user = ensure_coach_user(session_token)
    ensure_coach_owns_coach_id(coach_user, coach_id)
    supabase = ensure_supabase()
    rows = safe_table_rows(
        "assignment_requests",
        supabase.table("assignment_requests")
        .select("request_id,athlete_id,assigned_coach_id,status,notes,requested_at")
        .eq("status", "PENDING")
        .or_(f"assigned_coach_id.eq.{coach_id},assigned_coach_id.is.null")
        .order("requested_at", desc=True),
    )
    athlete_ids = [str(row.get("athlete_id")) for row in rows if row.get("athlete_id")]
    athlete_rows = safe_table_rows(
        APP_TABLES["athletes"],
        supabase.table(APP_TABLES["athletes"]).select("athlete_id,athlete_name,name").in_("athlete_id", athlete_ids),
    ) if athlete_ids else []
    athlete_name_map = {
        str(row.get("athlete_id")): str(row.get("athlete_name") or row.get("name") or "Athlete")
        for row in athlete_rows
    }
    requests = [
        PendingAssignmentItem(
            requestId=str(row.get("request_id") or ""),
            athleteId=str(row.get("athlete_id") or ""),
            athleteName=athlete_name_map.get(str(row.get("athlete_id")), "Athlete"),
            assignedCoachId=str(row.get("assigned_coach_id")) if row.get("assigned_coach_id") else None,
            status=str(row.get("status") or "PENDING"),
            notes=row.get("notes"),
            requestedAt=str(row.get("requested_at")) if row.get("requested_at") else None,
        )
        for row in rows
    ]
    return PendingAssignmentsResponse(requests=requests)


@app.post("/api/v1/assignments/assign", response_model=AssignAthleteResponse)
def assign_athlete_v1(
    payload: AssignAthleteInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AssignAthleteResponse:
    coach_user = ensure_coach_user(session_token)
    requestor_coach_id = resolve_dashboard_coach_key(coach_user)
    if not requestor_coach_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coach mapping not found.")
    supabase = ensure_supabase()

    athlete_row_result = (
        supabase.table(APP_TABLES["athletes"])
        .select("athlete_id,email,name,athlete_name")
        .eq("athlete_id", payload.athlete_id)
        .limit(1)
        .execute()
    )
    athlete_row = (athlete_row_result.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")

    assignment_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    try:
        request_rows = safe_table_rows(
            "assignment_requests",
            supabase.table("assignment_requests")
            .select("request_id,assigned_coach_id,status")
            .eq("request_id", payload.request_id)
            .limit(1),
        )
        request_row = request_rows[0] if request_rows else None
        if not request_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment request not found.")
        if request_row.get("status") != "PENDING":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignment request is not pending.")
        target_coach_id = str(request_row.get("assigned_coach_id") or "")
        if target_coach_id and target_coach_id != str(requestor_coach_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This assignment request belongs to another coach.")

        supabase.table(APP_TABLES["athletes"]).update({"coach_id": payload.assigned_coach_id}).eq("athlete_id", payload.athlete_id).execute()
        safe_table_rows(
            "coach_assignments",
            supabase.table("coach_assignments").insert(
                {
                    "assignment_id": assignment_id,
                    "coach_id": payload.assigned_coach_id,
                    "athlete_id": payload.athlete_id,
                    "is_active": True,
                }
            ),
        )
        supabase.table("assignment_requests").update(
            {
                "requesting_coach_id": requestor_coach_id,
                "assigned_coach_id": payload.assigned_coach_id,
                "status": "ASSIGNED",
                "notes": payload.notes,
                "assigned_at": now,
            }
        ).eq("request_id", payload.request_id).execute()
        athlete_email = str(athlete_row.get("email") or "").lower()
        assigned_coach_name = None
        coach_rows = safe_table_rows(
            "coaches",
            supabase.table("coaches").select("coach_name").eq("coach_id", payload.assigned_coach_id).limit(1),
        )
        if coach_rows:
            assigned_coach_name = str(coach_rows[0].get("coach_name") or "Coach")
        if athlete_email:
            supabase.table("App_Users").update(
                {
                    "assignment_status": "assigned",
                    "assigned_coach_email": get_domain_coach_email(payload.assigned_coach_id),
                    "assigned_coach_name": assigned_coach_name,
                    "updated_at": now,
                }
            ).eq("email", athlete_email).execute()
            create_notification(
                recipient_email=athlete_email,
                recipient_role="student",
                title="Coach assigned",
                message=f"You have been assigned to {assigned_coach_name or 'your coach'}.",
                notification_type="ASSIGNED_TO_COACH",
                entity_id=payload.athlete_id,
                related_athlete_id=payload.athlete_id,
            )
    except Exception as exception:
        if isinstance(exception, HTTPException):
            raise exception
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to assign athlete: {exception}") from exception

    write_audit_log(
        actor_email=coach_user.email,
        action="athlete_assigned_v1",
        entity_type="assignment_request",
        entity_id=payload.request_id,
        metadata={"athleteId": payload.athlete_id, "assignedCoachId": payload.assigned_coach_id},
    )
    return AssignAthleteResponse(success=True, assignmentId=assignment_id)


@app.get("/api/v1/athletes/{athlete_id}/assignment_status", response_model=AthleteAssignmentStatusResponse)
def get_athlete_assignment_status_v1(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AthleteAssignmentStatusResponse:
    _ = get_authenticated_user(session_token)
    supabase = ensure_supabase()
    rows = safe_table_rows(
        "assignment_requests",
        supabase.table("assignment_requests")
        .select("athlete_id,assigned_coach_id,status,requested_at,assigned_at")
        .eq("athlete_id", athlete_id)
        .order("requested_at", desc=True)
        .limit(1),
    )
    row = rows[0] if rows else None
    if not row:
        return AthleteAssignmentStatusResponse(
            athleteId=athlete_id,
            status="UNASSIGNED",
            assignedCoachId=None,
            assignedCoachName=None,
            requestedAt=None,
            assignedAt=None,
        )

    coach_name = None
    assigned_coach_id = row.get("assigned_coach_id")
    if assigned_coach_id:
        coach_rows = safe_table_rows(
            "coaches",
            supabase.table("coaches").select("coach_name").eq("coach_id", assigned_coach_id).limit(1),
        )
        coach_name = str(coach_rows[0].get("coach_name")) if coach_rows else None

    return AthleteAssignmentStatusResponse(
        athleteId=str(row.get("athlete_id") or athlete_id),
        status=str(row.get("status") or "UNASSIGNED"),
        assignedCoachId=str(assigned_coach_id) if assigned_coach_id else None,
        assignedCoachName=coach_name,
        requestedAt=str(row.get("requested_at")) if row.get("requested_at") else None,
        assignedAt=str(row.get("assigned_at")) if row.get("assigned_at") else None,
    )


def average_metric(values: list[float | None]) -> float | None:
    real_values = [value for value in values if isinstance(value, (int, float))]
    return round(sum(real_values) / len(real_values), 2) if real_values else None


def score_lookup_for_row(athlete_row: dict[str, Any]) -> dict[str, float]:
    values: dict[str, float] = {}
    for score in get_scores_for_athlete(athlete_row):
        current = values.get(score.score_type)
        if current is None:
            values[score.score_type] = round(float(score.score_value), 2)
    return values


def score_value(values: dict[str, float], *keys: str) -> float | None:
    for key in keys:
        value = values.get(key)
        if value is not None:
            return round(float(value), 2)
    return None


def fatigue_burden_from_inputs(score_values: dict[str, float], physiology_row: dict[str, Any] | None = None) -> float | None:
    physiology_row = physiology_row or {}
    if physiology_row.get("fatigue_level") is not None:
        return round(min(100, max(0, row_float(physiology_row.get("fatigue_level"), 0) * 10)), 2)
    fatigue_control = score_value(score_values, "fatigue")
    if fatigue_control is None:
        return None
    return round(min(100, max(0, 100 - fatigue_control)), 2)


def is_recent_date(value: str | None, days: int = 7) -> bool:
    if not value:
        return False
    try:
        normalized = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed >= datetime.now(timezone.utc) - timedelta(days=days)
    except ValueError:
        return False


def derive_status(
    *,
    performance: float | None,
    readiness: float | None,
    stress: float | None,
    fatigue: float | None,
    recovery: float | None,
) -> Literal["Strong", "Stable", "Needs Attention", "At Risk"]:
    if (stress is not None and stress >= 80) or (fatigue is not None and fatigue >= 80) or (recovery is not None and recovery < 35):
        return "At Risk"
    if (performance is not None and performance < 60) or (readiness is not None and readiness < 50):
        return "Needs Attention"
    if (performance is not None and performance >= 80) and (readiness is None or readiness >= 70) and (stress is None or stress < 65):
        return "Strong"
    return "Stable"


def derive_trend(history_values: list[float]) -> Literal["Improving", "Declining", "Stable"]:
    if len(history_values) < 2:
        return "Stable"
    delta = history_values[0] - history_values[-1]
    if delta >= 5:
        return "Improving"
    if delta <= -5:
        return "Declining"
    return "Stable"


def risk_reasons_for_row(
    *,
    performance: float | None,
    readiness: float | None,
    focus: float | None,
    stress: float | None,
    fatigue: float | None,
    recovery: float | None,
    sleep_hours: float | None,
    last_session_date: str | None,
    trend: str,
) -> list[str]:
    reasons: list[str] = []
    if stress is not None and stress >= 70:
        reasons.append("High stress")
    if fatigue is not None and fatigue >= 70:
        reasons.append("High fatigue")
    if recovery is not None and recovery < 50:
        reasons.append("Low recovery")
    if readiness is not None and readiness < 55:
        reasons.append("Low readiness")
    if focus is not None and focus < 55:
        reasons.append("Low focus")
    if performance is not None and performance < 60:
        reasons.append("Low performance")
    if sleep_hours is not None and sleep_hours < 6:
        reasons.append("Poor sleep")
    if trend == "Declining":
        reasons.append("Declining trend")
    if not is_recent_date(last_session_date):
        reasons.append("No recent activity")
    return reasons


def suggested_action_for_reasons(reasons: list[str]) -> str:
    reason_text = " ".join(reasons).lower()
    if "stress" in reason_text or "focus" in reason_text:
        return "Schedule a short regulation check-in and add a breathing/focus drill before the next session."
    if "fatigue" in reason_text or "recovery" in reason_text or "sleep" in reason_text:
        return "Reduce load for the next session and review sleep, recovery, and hydration habits."
    if "performance" in reason_text or "declining" in reason_text:
        return "Review recent session data and assign one technical correction for the next practice."
    if "activity" in reason_text:
        return "Contact the athlete and confirm the next planned training session."
    return "Review the athlete detail dashboard and add coach feedback."


@app.get("/api/v1/coaches/{coach_id}/dashboard", response_model=CoachDashboardV1Response)
def get_coach_dashboard_v1(
    coach_id: str,
    gender: str | None = Query(default=None),
    min_score: float | None = Query(default=None, alias="minScore"),
    max_score: float | None = Query(default=None, alias="maxScore"),
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachDashboardV1Response:
    coach_user = ensure_coach_user(session_token)
    ensure_coach_owns_coach_id(coach_user, coach_id)
    supabase = ensure_supabase()
    athletes = list_coach_athletes(search="", athlete_ids="", include_pending=True, session_token=session_token).athletes

    rows: list[CoachDashboardAthleteRow] = []
    for athlete in athletes:
        athlete_row = resolve_athlete_row_by_identifier(supabase, athlete.athlete_id) or {"athlete_id": athlete.athlete_id}
        score_map = score_lookup_for_row(athlete_row)
        latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [athlete.athlete_id], "recorded_date").get(athlete.athlete_id) or {}
        session_rows = safe_table_rows(
            APP_TABLES["shooting_session_log"],
            supabase.table(APP_TABLES["shooting_session_log"])
            .select("*")
            .eq("athlete_id", athlete.athlete_id)
            .order("session_date", desc=True)
            .limit(5),
        )

        history_scores: list[float] = []
        for session_row in session_rows[:5]:
            try:
                summary = build_mobile_session_summary(session_row)
                value = row_float(summary.get("score", {}).get("efficiencyPercent"), fallback=None)  # type: ignore[arg-type]
                if value is not None:
                    history_scores.append(value)
            except Exception:
                continue

        score = athlete.overall_score or score_value(score_map, "overall", "performance")
        readiness = score_value(score_map, "readiness")
        focus = score_value(score_map, "focus", "mental_score")
        fatigue = fatigue_burden_from_inputs(score_map, latest_physiology)
        recovery = athlete.latest_recovery_score or score_value(score_map, "recovery")
        stress = athlete.latest_stress_score or score_value(score_map, "stress")
        sleep_hours = row_float(latest_physiology.get("sleep_hours"), fallback=None)  # type: ignore[arg-type]
        resting_hr = row_float(latest_physiology.get("resting_heart_rate") or latest_physiology.get("resting_hr"), fallback=None)  # type: ignore[arg-type]
        hrv = row_float(latest_physiology.get("rmssd") or latest_physiology.get("hrv") or latest_physiology.get("hrv_ms"), fallback=None)  # type: ignore[arg-type]
        session_count = len(session_rows)
        discipline = score_value(score_map, "discipline", "consistency")
        if discipline is None:
            discipline_parts = [
                min(100, session_count * 18),
                recovery,
                (100 - stress) if stress is not None else None,
                (100 - fatigue) if fatigue is not None else None,
            ]
            discipline = average_metric(discipline_parts)
        trend = derive_trend(history_scores or ([score] if score is not None else []))
        status_value = derive_status(
            performance=score,
            readiness=readiness,
            stress=stress,
            fatigue=fatigue,
            recovery=recovery,
        )
        reasons = risk_reasons_for_row(
            performance=score,
            readiness=readiness,
            focus=focus,
            stress=stress,
            fatigue=fatigue,
            recovery=recovery,
            sleep_hours=sleep_hours,
            last_session_date=athlete.latest_session_date,
            trend=trend,
        )
        category = "Pending" if score is None else ("Strong" if score >= 80 else "Stable" if score >= 60 else "Needs Attention")
        row = CoachDashboardAthleteRow(
            athleteId=athlete.athlete_id,
            athleteName=athlete.name,
            sport=athlete.latest_training_type or "Shooting",
            discipline=athlete.academy_id or "Performance",
            gender=athlete.gender,
            age=athlete.age,
            score=score,
            readinessScore=readiness,
            focusScore=focus,
            disciplineScore=discipline,
            scoreCategory=category,
            status=status_value,
            trend=trend,
            latestStress=stress,
            restingHr=resting_hr,
            hrvIndicator=hrv,
            fatigueScore=fatigue,
            latestRecovery=recovery,
            sleepHours=sleep_hours,
            lastSessionDate=athlete.latest_session_date,
            riskScore=min(100, len(reasons) * 18),
            riskReasons=reasons,
            suggestedAction=suggested_action_for_reasons(reasons) if reasons else None,
        )
        rows.append(row)

    if gender:
        rows = [row for row in rows if (row.gender or "").lower() == gender.lower()]
    if min_score is not None:
        rows = [row for row in rows if row.score is not None and row.score >= min_score]
    if max_score is not None:
        rows = [row for row in rows if row.score is not None and row.score <= max_score]

    scores = [row.score for row in rows if row.score is not None]
    distribution = {
        "strong": len([value for value in scores if value >= 80]),
        "progressing": len([value for value in scores if 60 <= value < 80]),
        "needsAttention": len([value for value in scores if value < 60]),
        "pending": len([row for row in rows if row.score is None]),
    }
    risk_queue = [
        CoachDashboardRiskItem(
            athleteId=row.athlete_id,
            athleteName=row.athlete_name,
            severity="High" if row.risk_score >= 54 else "Medium" if row.risk_score >= 18 else "Low",
            reasons=row.risk_reasons,
            suggestedAction=row.suggested_action or "Review athlete detail dashboard.",
        )
        for row in sorted(rows, key=lambda item: item.risk_score, reverse=True)
        if row.risk_reasons
    ][:8]
    alerts = [f"{item.athlete_name}: {', '.join(item.reasons[:2])}" for item in risk_queue]
    top_performers = sorted(rows, key=lambda row: (row.score or -1, row.latest_recovery or -1), reverse=True)[:5]
    most_disciplined = sorted(rows, key=lambda row: (row.discipline_score or -1, row.score or -1), reverse=True)[:5]
    healthy_focused = sorted(
        rows,
        key=lambda row: (
            row.latest_recovery or -1,
            row.focus_score or -1,
            -(row.latest_stress or 100),
            -(row.fatigue_score or 100),
        ),
        reverse=True,
    )[:5]
    mapping_points = [
        CoachDashboardScatterPoint(
            athleteId=row.athlete_id,
            athleteName=row.athlete_name,
            performance=row.score,
            stress=row.latest_stress,
            fatigue=row.fatigue_score,
            readiness=row.readiness_score,
            sleep=row.sleep_hours,
            restingHr=row.resting_hr,
            hrvIndicator=row.hrv_indicator,
            focus=row.focus_score,
            consistency=row.discipline_score,
        )
        for row in rows
    ]
    insights = [
        CoachDashboardInsightItem(
            title="Attention queue",
            insightText=f"{len(risk_queue)} athletes need coach review today.",
            category="risk",
            score=float(len(risk_queue)),
            priority="High" if len(risk_queue) >= 3 else "Medium" if risk_queue else "Low",
        ),
        CoachDashboardInsightItem(
            title="Performance baseline",
            insightText="Team average performance is stable." if scores and average_metric(scores) and average_metric(scores) >= 60 else "Team performance needs a baseline review.",
            category="performance",
            score=average_metric(scores),
            priority="Medium",
        ),
    ]
    insight_rows = safe_table_rows(
        "athlete_insights",
        supabase.table("athlete_insights")
        .select("title,insight_text,category,score,priority,created_at")
        .in_("athlete_id", [row.athlete_id for row in rows])
        .order("created_at", desc=True)
        .limit(6),
    )
    insights.extend(
        [
            CoachDashboardInsightItem(
                title=str(row.get("title") or "Coach insight"),
                insightText=str(row.get("insight_text") or ""),
                category=str(row.get("category") or "insight"),
                score=row_float(row.get("score"), fallback=None),  # type: ignore[arg-type]
                priority=row.get("priority") if row.get("priority") in {"High", "Medium", "Low"} else "Medium",
            )
            for row in insight_rows
            if row.get("insight_text")
        ]
    )

    payload = CoachDashboardV1Payload(
        coachId=coach_id,
        totals={
            "totalAssignedAthletes": len(rows),
            "activeAthletes": len([row for row in rows if is_recent_date(row.last_session_date)]),
            "inactiveAthletes": len([row for row in rows if not is_recent_date(row.last_session_date)]),
            "newRegistrations": len([athlete for athlete in athletes if is_recent_date(athlete.created_at)]),
            "athletesNeedingAttention": len([row for row in rows if row.status in {"Needs Attention", "At Risk"}]),
            "topPerformers": len([row for row in rows if row.status == "Strong"]),
            "mostDisciplined": len([row for row in rows if (row.discipline_score or 0) >= 75]),
        },
        averageScore=round(sum(scores) / len(scores), 2) if scores else None,
        averageReadiness=average_metric([row.readiness_score for row in rows]),
        averageFatigue=average_metric([row.fatigue_score for row in rows]),
        averageStress=average_metric([row.latest_stress for row in rows]),
        scoreDistribution=distribution,
        athletes=rows,
        topPerformers=top_performers,
        mostDisciplined=most_disciplined,
        healthyFocused=healthy_focused,
        riskQueue=risk_queue,
        mapping={
            "performanceVsFatigue": mapping_points,
            "performanceVsStress": mapping_points,
            "performanceVsHeartRate": mapping_points,
            "performanceVsHrv": mapping_points,
            "performanceVsSleep": mapping_points,
            "readinessVsPerformance": mapping_points,
            "focusVsConsistency": mapping_points,
        },
        insights=insights,
        alerts=alerts,
    )
    return CoachDashboardV1Response(dashboard=payload)


@app.get("/api/v1/athletes/{athlete_id}/full_profile", response_model=AthleteFullProfileV1Response)
def get_athlete_full_profile_v1(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AthleteFullProfileV1Response:
    detail = get_coach_athlete_detail(athlete_id=athlete_id, session_token=session_token).athlete
    feedback = list_coach_athlete_feedback(athlete_id=athlete_id, session_token=session_token).feedback
    detail["feedbackHistory"] = [item.model_dump(by_alias=True) for item in feedback]
    return AthleteFullProfileV1Response(athlete=detail)


@app.post("/api/v1/coach_feedback", response_model=CoachFeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_coach_feedback_v1(
    payload: V1CoachFeedbackInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachFeedbackResponse:
    coach_user = ensure_coach_user(session_token)
    coach_id = resolve_dashboard_coach_key(coach_user)
    if not coach_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Coach mapping not found.")

    supabase = ensure_supabase()
    request_row_result = (
        supabase.table("feedback_requests")
        .select("*")
        .eq("request_id", payload.request_id)
        .eq("coach_id", coach_id)
        .limit(1)
        .execute()
    )
    request_row = (request_row_result.data or [None])[0]
    if not request_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback request not found.")
    if str(request_row.get("status") or "").upper() != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback request is not pending.")

    athlete_result = (
        supabase.table(APP_TABLES["athletes"])
        .select("*")
        .eq("athlete_id", payload.athlete_id)
        .limit(1)
        .execute()
    )
    athlete_row = (athlete_result.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if str(athlete_row.get("coach_id") or "") != str(coach_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Athlete is not assigned to this coach.")

    feedback_id = str(uuid4())
    feedback_item = {
        "feedback_id": feedback_id,
        "athlete_id": athlete_row["athlete_id"],
        "athlete_name": athlete_row.get("athlete_name") or athlete_row.get("name") or "Athlete",
        "athlete_email": athlete_row.get("email") or "",
        "coach_email": coach_user.email,
        "coach_name": coach_user.full_name,
        "note": payload.note,
        "recommendation": payload.recommendation,
        "status": payload.status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table(APP_TABLES["coach_feedback"]).insert(feedback_item).execute()
    supabase.table("feedback_requests").update(
        {
            "status": "COMPLETED",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "feedback_id": feedback_id,
        }
    ).eq("request_id", payload.request_id).execute()

    return CoachFeedbackResponse(
        feedback=serialize_feedback_item(
            {
                "feedbackId": feedback_item["feedback_id"],
                "athleteId": feedback_item["athlete_id"],
                "athleteName": feedback_item["athlete_name"],
                "athleteEmail": feedback_item["athlete_email"],
                "coachEmail": feedback_item["coach_email"],
                "coachName": feedback_item["coach_name"],
                "note": feedback_item["note"],
                "recommendation": feedback_item["recommendation"],
                "status": feedback_item["status"],
                "createdAt": feedback_item["created_at"],
            }
        )
    )


@app.post("/api/notifications/{notification_id}/read", response_model=StatusResponse)
def mark_notification_read(
    notification_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> StatusResponse:
    user = get_authenticated_user(session_token)
    try:
        supabase = ensure_supabase()
        update = {"read_at": datetime.now(timezone.utc).isoformat(), "is_read": True}
        query = supabase.table(APP_TABLES["notifications"]).update(update).eq("notification_id", notification_id)
        coach_key = resolve_dashboard_coach_key(user) if user.role == "coach" else None
        if coach_key:
            query = query.or_(f"recipient_email.eq.{user.email.lower()},recipient_coach_id.eq.{coach_key}")
        else:
            query = query.eq("recipient_email", user.email.lower())
        query.execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to update notification: {exception}") from exception
    return StatusResponse(success=True)


@app.get("/api/coach/athletes", response_model=CoachAthleteListResponse)
def list_coach_athletes(
    search: str = Query(default="", max_length=100),
    athlete_ids: str = Query(default="", alias="athleteIds", max_length=1000),
    include_pending: bool = Query(default=False, alias="includePending"),
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteListResponse:
    coach_user = ensure_coach_user(session_token)
    supabase = ensure_supabase()
    coach_key = resolve_dashboard_coach_key(coach_user)
    query = supabase.table(APP_TABLES["athletes"]).select("*")
    if coach_key:
        query = query.eq("coach_id", coach_key)
    else:
        # No mapping between App_Users coach and domain coaches table yet.
        query = query.eq("coach_id", "__unmapped__")

    try:
        response = query.execute()
        rows = response.data or []
        if search.strip():
            term = search.strip().lower()
            rows = [
                row for row in rows
                if term in str(row.get("athlete_name") or row.get("name") or "").lower()
            ]
        athlete_ids_param = athlete_ids if isinstance(athlete_ids, str) else ""
        requested_ids = {value.strip() for value in athlete_ids_param.split(",") if value.strip()}
        if requested_ids:
            rows = [row for row in rows if str(row.get("athlete_id") or "") in requested_ids]
        rows.sort(key=lambda row: str(row.get("athlete_name") or row.get("name") or ""))
        athlete_ids = [row["athlete_id"] for row in rows]
        latest_sessions = get_latest_rows_by_athlete(APP_TABLES["shooting_session_log"], athlete_ids, "session_date")
        latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], athlete_ids, "recorded_date")
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load athletes: {exception}",
        ) from exception

    athletes: list[CoachAthleteListItem] = []
    for row in rows:
        scores = get_scores_for_athlete(row)
        overall = next((item for item in scores if item.score_type == "overall"), scores[0] if scores else None)
        overall_score = overall.score_value if overall else None
        include_pending_flag = include_pending if isinstance(include_pending, bool) else False
        if not include_pending_flag and overall_score is None:
            continue
        athletes.append(
            CoachAthleteListItem(
                athleteId=row["athlete_id"],
                name=row.get("athlete_name") or row.get("name") or "Unnamed athlete",
                age=row.get("age"),
                gender=row.get("gender"),
                academyId=str(row.get("academy_id") or ""),
                coachId=str(row.get("coach_id") or ""),
                email=row.get("email") or "",
                contactNumber=row.get("contact_number") or "",
                createdAt=row.get("created_at"),
                latestSessionDate=(latest_sessions.get(row["athlete_id"]) or {}).get("session_date"),
                latestTrainingType=(latest_sessions.get(row["athlete_id"]) or {}).get("training_type") or "Shooting",
                latestRecoveryScore=(latest_physiology.get(row["athlete_id"]) or {}).get("recovery_score"),
                latestStressScore=(latest_physiology.get(row["athlete_id"]) or {}).get("stress_score"),
                latestFatigueLevel=(latest_physiology.get(row["athlete_id"]) or {}).get("fatigue_level"),
                latestSleepHours=(latest_physiology.get(row["athlete_id"]) or {}).get("sleep_hours"),
                overallScore=overall_score,
            )
        )
    athletes: list[CoachAthleteListItem] = []
    for row in rows:
        scores = get_scores_for_athlete(row)
        overall = next((item for item in scores if item.score_type == "overall"), scores[0] if scores else None)
        overall_score = overall.score_value if overall else None
        include_pending_flag = include_pending if isinstance(include_pending, bool) else False
        if not include_pending_flag and overall_score is None:
            continue
        athletes.append(
            CoachAthleteListItem(
                athleteId=row["athlete_id"],
                name=row.get("athlete_name") or row.get("name") or "Unnamed athlete",
                age=row.get("age"),
                gender=row.get("gender"),
                academyId=str(row.get("academy_id") or ""),
                coachId=str(row.get("coach_id") or ""),
                email=row.get("email") or "",
                contactNumber=row.get("contact_number") or "",
                createdAt=row.get("created_at"),
                latestSessionDate=(latest_sessions.get(row["athlete_id"]) or {}).get("session_date"),
                latestTrainingType=(latest_sessions.get(row["athlete_id"]) or {}).get("training_type") or "Shooting",
                latestRecoveryScore=(latest_physiology.get(row["athlete_id"]) or {}).get("recovery_score"),
                latestStressScore=(latest_physiology.get(row["athlete_id"]) or {}).get("stress_score"),
                latestFatigueLevel=(latest_physiology.get(row["athlete_id"]) or {}).get("fatigue_level"),
                latestSleepHours=(latest_physiology.get(row["athlete_id"]) or {}).get("sleep_hours"),
                overallScore=overall_score,
            )
        )
    return CoachAthleteListResponse(athletes=athletes)


@app.get("/api/coach/dashboard-summary", response_model=CoachDashboardSummaryResponse)
def get_coach_dashboard_summary(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachDashboardSummaryResponse:
    coach_user = ensure_coach_user(session_token)
    athletes = list_coach_athletes(
        search="",
        athlete_ids="",
        include_pending=False,
        session_token=session_token,
    ).athletes
    scores_by_athlete: dict[str, float] = {}
    supabase = ensure_supabase()
    coach_key = resolve_dashboard_coach_key(coach_user)
    athlete_rows = safe_table_rows(
        APP_TABLES["athletes"],
        (supabase.table(APP_TABLES["athletes"]).select("*").eq("coach_id", coach_key) if coach_key else supabase.table(APP_TABLES["athletes"]).select("*").eq("coach_id", "__unmapped__")),
    )
    for row in athlete_rows:
        scores = get_scores_for_athlete(row)
        overall = next((item for item in scores if item.score_type == "overall"), scores[0] if scores else None)
        if overall:
            scores_by_athlete[str(row["athlete_id"])] = overall.score_value

    sorted_athletes = sorted(
        athletes,
        key=lambda athlete: scores_by_athlete.get(athlete.athlete_id, -1),
        reverse=True,
    )
    score_values = list(scores_by_athlete.values())
    average_score = round(sum(score_values) / len(score_values), 2) if score_values else None
    distribution = {
        "strong": len([score for score in score_values if score >= 80]),
        "progressing": len([score for score in score_values if 60 <= score < 80]),
        "needsAttention": len([score for score in score_values if score < 60]),
        "pending": max(0, len(athletes) - len(score_values)),
    }
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_registrations = 0
    for athlete in athletes:
        if not athlete.created_at:
            continue
        try:
            created_at = datetime.fromisoformat(str(athlete.created_at).replace("Z", "+00:00"))
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if created_at >= seven_days_ago:
                new_registrations += 1
        except ValueError:
            continue

    notifications = list_notifications(session_token=session_token).notifications[:8]
    alerts = [
        f"{athlete.name} needs attention"
        for athlete in athletes
        if scores_by_athlete.get(athlete.athlete_id, 100) < 60
    ][:5]
    high_stress = [athlete.name for athlete in athletes if (athlete.latest_stress_score or 0) >= 65][:5]
    alerts.extend([f"{name} has elevated stress" for name in high_stress])

    return CoachDashboardSummaryResponse(
        summary=CoachDashboardSummary(
            totalAssignedAthletes=len(athletes),
            newRegistrations=new_registrations,
            activeAthletes=len([athlete for athlete in athletes if is_recent_date(athlete.latest_session_date)]),
            inactiveAthletes=len([athlete for athlete in athletes if not is_recent_date(athlete.latest_session_date)]),
            averageScore=average_score,
            highestPerforming=sorted_athletes[:5],
            lowestPerforming=list(reversed(sorted_athletes[-5:])),
            scoreDistribution=distribution,
            recentActivity=notifications,
            alerts=alerts[:8],
        )
    )


@app.get("/api/coach/dashboard-summary", response_model=CoachDashboardSummaryResponse)
def get_coach_dashboard_summary(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachDashboardSummaryResponse:
    coach_user = ensure_coach_user(session_token)
    athletes = list_coach_athletes(
        search="",
        athlete_ids="",
        include_pending=False,
        session_token=session_token,
    ).athletes
    scores_by_athlete: dict[str, float] = {}
    supabase = ensure_supabase()
    coach_key = resolve_dashboard_coach_key(coach_user)
    athlete_rows = safe_table_rows(
        APP_TABLES["athletes"],
        (supabase.table(APP_TABLES["athletes"]).select("*").eq("coach_id", coach_key) if coach_key else supabase.table(APP_TABLES["athletes"]).select("*").eq("coach_id", "__unmapped__")),
    )
    for row in athlete_rows:
        scores = get_scores_for_athlete(row)
        overall = next((item for item in scores if item.score_type == "overall"), scores[0] if scores else None)
        if overall:
            scores_by_athlete[str(row["athlete_id"])] = overall.score_value

    sorted_athletes = sorted(
        athletes,
        key=lambda athlete: scores_by_athlete.get(athlete.athlete_id, -1),
        reverse=True,
    )
    score_values = list(scores_by_athlete.values())
    average_score = round(sum(score_values) / len(score_values), 2) if score_values else None
    distribution = {
        "strong": len([score for score in score_values if score >= 80]),
        "progressing": len([score for score in score_values if 60 <= score < 80]),
        "needsAttention": len([score for score in score_values if score < 60]),
        "pending": max(0, len(athletes) - len(score_values)),
    }
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_registrations = 0
    for athlete in athletes:
        if not athlete.created_at:
            continue
        try:
            created_at = datetime.fromisoformat(str(athlete.created_at).replace("Z", "+00:00"))
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if created_at >= seven_days_ago:
                new_registrations += 1
        except ValueError:
            continue

    notifications = list_notifications(session_token=session_token).notifications[:8]
    alerts = [
        f"{athlete.name} needs attention"
        for athlete in athletes
        if scores_by_athlete.get(athlete.athlete_id, 100) < 60
    ][:5]
    high_stress = [athlete.name for athlete in athletes if (athlete.latest_stress_score or 0) >= 65][:5]
    alerts.extend([f"{name} has elevated stress" for name in high_stress])

    return CoachDashboardSummaryResponse(
        summary=CoachDashboardSummary(
            totalAssignedAthletes=len(athletes),
            newRegistrations=new_registrations,
            activeAthletes=len([athlete for athlete in athletes if is_recent_date(athlete.latest_session_date)]),
            inactiveAthletes=len([athlete for athlete in athletes if not is_recent_date(athlete.latest_session_date)]),
            averageScore=average_score,
            highestPerforming=sorted_athletes[:5],
            lowestPerforming=list(reversed(sorted_athletes[-5:])),
            scoreDistribution=distribution,
            recentActivity=notifications,
            alerts=alerts[:8],
        )
    )


@app.get("/api/coach/athletes/{athlete_id}", response_model=CoachAthleteDetailResponse)
def get_coach_athlete_detail(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteDetailResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access athletes assigned to you.",
        )

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    family_rows = safe_table_rows(
        APP_TABLES["athlete_family"],
        supabase.table(APP_TABLES["athlete_family"]).select("*").eq("athlete_id", canonical_athlete_id).limit(1),
    )
    profile_rows = safe_table_rows(
        APP_TABLES["athlete_details"],
        supabase.table(APP_TABLES["athlete_details"]).select("*").eq("athlete_id", canonical_athlete_id).limit(1),
    )
    session_rows = safe_table_rows(
        APP_TABLES["shooting_session_log"],
        supabase.table(APP_TABLES["shooting_session_log"]).select("*").eq("athlete_id", canonical_athlete_id).order("session_date", desc=True),
    )
    physiology_rows = safe_table_rows(
        APP_TABLES["athlete_physiology"],
        supabase.table(APP_TABLES["athlete_physiology"]).select("*").eq("athlete_id", canonical_athlete_id).order("recorded_date", desc=True),
    )
    psychology_rows = safe_table_rows(
        APP_TABLES["psychology_responses"],
        supabase.table(APP_TABLES["psychology_responses"]).select("*").eq("athlete_id", canonical_athlete_id),
    )
    question_rows = safe_table_rows(
        APP_TABLES["psychology_questions"],
        supabase.table(APP_TABLES["psychology_questions"]).select("*"),
    )

    question_lookup = {
        item.get("question_id"): item
        for item in question_rows
    }
    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access athletes assigned to you.",
        )

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    family_rows = safe_table_rows(
        APP_TABLES["athlete_family"],
        supabase.table(APP_TABLES["athlete_family"]).select("*").eq("athlete_id", canonical_athlete_id).limit(1),
    )
    profile_rows = safe_table_rows(
        APP_TABLES["athlete_details"],
        supabase.table(APP_TABLES["athlete_details"]).select("*").eq("athlete_id", canonical_athlete_id).limit(1),
    )
    session_rows = safe_table_rows(
        APP_TABLES["shooting_session_log"],
        supabase.table(APP_TABLES["shooting_session_log"]).select("*").eq("athlete_id", canonical_athlete_id).order("session_date", desc=True),
    )
    physiology_rows = safe_table_rows(
        APP_TABLES["athlete_physiology"],
        supabase.table(APP_TABLES["athlete_physiology"]).select("*").eq("athlete_id", canonical_athlete_id).order("recorded_date", desc=True),
    )
    psychology_rows = safe_table_rows(
        APP_TABLES["psychology_responses"],
        supabase.table(APP_TABLES["psychology_responses"]).select("*").eq("athlete_id", canonical_athlete_id),
    )
    question_rows = safe_table_rows(
        APP_TABLES["psychology_questions"],
        supabase.table(APP_TABLES["psychology_questions"]).select("*"),
    )

    question_lookup = {
        item.get("question_id"): item
        for item in question_rows
    }

    athlete = {
        "athleteMaster": serialize_athlete_master(athlete_row),
        "familyDetails": serialize_family_details((family_rows or [None])[0]),
        "athleteProfile": serialize_athlete_profile((profile_rows or [None])[0]),
        "scores": [score.model_dump(by_alias=True) for score in get_scores_for_athlete(athlete_row)],
        "sessionsLog": [
            serialize_shooting_session(row)
            for row in session_rows
        ],
        "physiologyData": [
            serialize_app_physiology(row)
            for row in physiology_rows
        ],
        "psychologyResponses": [
            {
                "answerId": str(row.get("answer_id") or row.get("id") or f"{athlete_id}-{row.get('question_id')}"),
                "questionId": str(row.get("question_id") or ""),
                "questionText": question_lookup.get(row.get("question_id"), {}).get("question_text", f"Question {row.get('question_id')}"),
                "category": question_lookup.get(row.get("question_id"), {}).get("category", "Psychology"),
                "questionType": "Text",
                "answerText": row.get("answer_text") or row.get("chosen_option") or "",
                "answerScore": row.get("answer_score"),
                "recordedAt": row.get("recorded_at") or row.get("created_at") or athlete_row.get("created_at"),
            }
            for row in psychology_rows
        ],
    }
    return CoachAthleteDetailResponse(athlete=athlete)


@app.get("/api/coach/athletes/{athlete_id}/home", response_model=MobileAthleteHomeResponse)
def get_coach_athlete_home(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> MobileAthleteHomeResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access athletes assigned to you.")

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    return get_mobile_athlete_home(athlete_id=canonical_athlete_id)


@app.get("/api/coach/athletes/{athlete_id}/widget", response_model=CoachAthleteWidgetResponse)
def get_coach_athlete_widget(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteWidgetResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access athletes assigned to you.")

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    scores = get_scores_for_athlete(athlete_row)
    score_by_type = {score.score_type: score for score in scores}
    score_map = {score.score_type: round(float(score.score_value), 2) for score in scores}
    latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [canonical_athlete_id], "recorded_date").get(canonical_athlete_id) or {}
    fatigue_burden = fatigue_burden_from_inputs(score_map, latest_physiology)
    home = get_mobile_athlete_home(athlete_id=canonical_athlete_id).home
    recommendations = home.get("recommendations") if isinstance(home, dict) else None

    next_focus = None
    if isinstance(recommendations, list) and recommendations:
        first = str(recommendations[0])
        lowered = first.lower()
        if "breathing" in lowered or "cool-down" in lowered or "cool down" in lowered:
            next_focus = "Hold"
        elif "check-in" in lowered or "checkin" in lowered:
            next_focus = "Settle"
        elif "training" in lowered or "session" in lowered:
            next_focus = "Shoot"
        else:
            next_focus = first.split(".")[0][:24]

    widget = {
        "athleteId": canonical_athlete_id,
        "readiness": score_by_type.get("readiness").score_value if score_by_type.get("readiness") else None,
        "performance": score_by_type.get("overall").score_value if score_by_type.get("overall") else None,
        "fatigue": fatigue_burden,
        "nextFocus": next_focus,
    }
    return CoachAthleteWidgetResponse(widget=widget)


@app.get("/api/coach/athletes/{athlete_id}/sessions-widget", response_model=CoachAthleteSessionsWidgetResponse)
def get_coach_athlete_sessions_widget(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteSessionsWidgetResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access athletes assigned to you.")

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)

    # Use existing mobile session summary computation (derived from scoring series + session logs).
    session_rows = safe_table_rows(
        APP_TABLES["shooting_session_log"],
        supabase.table(APP_TABLES["shooting_session_log"]).select("*").eq("athlete_id", canonical_athlete_id).order("session_date", desc=True).limit(3),
    )
    latest_session = session_rows[0] if session_rows else None
    latest_summary = None
    if latest_session and latest_session.get("session_id"):
        try:
            latest_summary = build_mobile_session_summary(latest_session)
        except Exception:
            latest_summary = None

    scores = get_scores_for_athlete(athlete_row)
    score_by_type = {score.score_type: score for score in scores}
    score_map = {score.score_type: round(float(score.score_value), 2) for score in scores}
    latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [canonical_athlete_id], "recorded_date").get(canonical_athlete_id) or {}
    fatigue_burden = fatigue_burden_from_inputs(score_map, latest_physiology)

    def session_date(row: dict[str, Any]) -> str | None:
        value = row.get("session_date") or row.get("created_at")
        return str(value) if value else None

    history: list[dict[str, Any]] = []
    for row in session_rows[:2]:
        row_summary = None
        try:
            row_summary = build_mobile_session_summary(row)
        except Exception:
            row_summary = None
        row_score = (row_summary or {}).get("score", {}) if isinstance(row_summary, dict) else {}
        row_physiology = (row_summary or {}).get("physiology", {}) if isinstance(row_summary, dict) else {}
        row_reflection = ((row_summary or {}).get("mentalState", {}) or {}).get("reflection") if isinstance(row_summary, dict) else None
        history.append(
            {
                "sessionId": str(row.get("session_id") or ""),
                "sessionDate": session_date(row),
                "trainingType": row.get("training_type") or row.get("session_type") or "Shooting",
                # Keep these aligned to the Sessions mock: "Score", "Ready", "Fatigue"
                "performance": row_score.get("averagePerShot") or (score_by_type.get("overall").score_value if score_by_type.get("overall") else None),
                "readiness": score_by_type.get("readiness").score_value if score_by_type.get("readiness") else None,
                "bestSeries": (row_score.get("bestSeries") or {}).get("total") if isinstance(row_score.get("bestSeries"), dict) else None,
                "avgHr": row_physiology.get("avgHeartRate"),
                "fatigue": fatigue_burden,
                "recovery": latest_physiology.get("recovery_score"),
                "reflection": (row_reflection or {}).get("whatWorked") if isinstance(row_reflection, dict) else row.get("athlete_notes") or row.get("notes"),
                "coachNotes": row.get("coach_notes") or "",
            }
        )

    widget = {
        "athleteId": canonical_athlete_id,
        "lastSession": {
            "sessionId": str((latest_session or {}).get("session_id") or ""),
            "sessionDate": session_date(latest_session or {}),
            "performance": (latest_summary or {}).get("score", {}).get("averagePerShot") if isinstance(latest_summary, dict) else None,
            "readiness": score_by_type.get("readiness").score_value if score_by_type.get("readiness") else None,
            "holdStability": score_by_type.get("hold_stability").score_value if score_by_type.get("hold_stability") else None,
            "mentalScore": score_by_type.get("mental_score").score_value if score_by_type.get("mental_score") else None,
            "fatigue": fatigue_burden,
            "summaryTitle": (latest_summary or {}).get("keyInsight", {}).get("title") if isinstance(latest_summary, dict) else None,
        },
        "history": history,
    }
    return CoachAthleteSessionsWidgetResponse(widget=widget)


def list_coach_feedback_rows(*, supabase: Any, athlete_id: str, limit: int = 20) -> list[dict[str, Any]]:
    return safe_table_rows(
        APP_TABLES["coach_feedback"],
        supabase.table(APP_TABLES["coach_feedback"]).select("*").eq("athlete_id", athlete_id).order("created_at", desc=True).limit(limit),
    )


@app.get("/api/coach/athletes/{athlete_id}/insights-widget", response_model=CoachAthleteInsightsWidgetResponse)
def get_coach_athlete_insights_widget(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteInsightsWidgetResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access athletes assigned to you.")

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    scores = get_scores_for_athlete(athlete_row)
    score_by_type = {score.score_type: score for score in scores}

    feedback_rows = list_coach_feedback_rows(supabase=supabase, athlete_id=canonical_athlete_id, limit=20)
    feedback_history = [
        {
            "createdAt": str(row.get("created_at") or ""),
            "status": row.get("status"),
            "note": row.get("note") or row.get("coach_observations") or "",
            "trainingPlan": row.get("recommendation") or row.get("training_plan") or "",
        }
        for row in feedback_rows
    ]
    latest_training_plan = feedback_history[0]["trainingPlan"] if feedback_history else None

    # Use mobile recommendations when no coach plan exists.
    home = get_mobile_athlete_home(athlete_id=canonical_athlete_id).home
    recommendations = home.get("recommendations") if isinstance(home, dict) else None
    fallback_plan = None
    if isinstance(recommendations, list) and recommendations:
        fallback_plan = " / ".join([str(item) for item in recommendations[:2]])
    insight_rows = safe_table_rows(
        "athlete_insights",
        supabase.table("athlete_insights")
        .select("title,insight_text,category,score,priority,suggested_action,supporting_data,created_at")
        .eq("athlete_id", canonical_athlete_id)
        .order("created_at", desc=True)
        .limit(20),
    )
    insight_history = [
        {
            "title": str(row.get("title") or "Insight"),
            "insightText": str(row.get("insight_text") or ""),
            "category": str(row.get("category") or "coach"),
            "score": row_float(row.get("score"), fallback=None),  # type: ignore[arg-type]
            "priority": row.get("priority") if row.get("priority") in {"High", "Medium", "Low"} else "Medium",
            "suggestedAction": row.get("suggested_action") or "",
            "supportingData": row.get("supporting_data") if isinstance(row.get("supporting_data"), dict) else {},
            "createdAt": str(row.get("created_at") or ""),
        }
        for row in insight_rows
    ]

    widget = {
        "athleteId": canonical_athlete_id,
        "scores": {
            "social": score_by_type.get("social").score_value if score_by_type.get("social") else None,
            "arousal": score_by_type.get("arousal").score_value if score_by_type.get("arousal") else None,
            "decision": score_by_type.get("decision").score_value if score_by_type.get("decision") else None,
            "focus": score_by_type.get("focus").score_value if score_by_type.get("focus") else None,
        },
        "recommendation": latest_training_plan or fallback_plan,
        "feedbackHistory": feedback_history,
        "insights": insight_history,
    }
    return CoachAthleteInsightsWidgetResponse(widget=widget)


@app.get("/api/coach/athletes/{athlete_id}/profile-widget", response_model=CoachAthleteProfileWidgetResponse)
def get_coach_athlete_profile_widget(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteProfileWidgetResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access athletes assigned to you.")

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    name = str(athlete_row.get("athlete_name") or athlete_row.get("name") or "Athlete")
    initials = "".join([part[:1].upper() for part in name.split()[:2]]) or "A"

    scores = get_scores_for_athlete(athlete_row)
    score_by_type = {score.score_type: score for score in scores}

    session_rows = safe_table_rows(
        APP_TABLES["shooting_session_log"],
        supabase.table(APP_TABLES["shooting_session_log"]).select("*").eq("athlete_id", canonical_athlete_id).order("session_date", desc=True).limit(30),
    )
    latest_session = session_rows[0] if session_rows else None
    latest_summary = None
    if latest_session:
        try:
            latest_summary = build_mobile_session_summary(latest_session)
        except Exception:
            latest_summary = None

    last_session_avg = None
    best_series_total = None
    if isinstance(latest_summary, dict):
        last_session_avg = latest_summary.get("score", {}).get("averagePerShot")
        best_series = latest_summary.get("score", {}).get("bestSeries")
        if isinstance(best_series, dict):
            best_series_total = best_series.get("total")
    latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [canonical_athlete_id], "recorded_date").get(canonical_athlete_id) or {}
    latest_physiology_fatigue = fatigue_burden_from_inputs({score.score_type: score.score_value for score in scores}, latest_physiology)
    performance_values: list[float] = []
    for row in session_rows:
        try:
            summary = build_mobile_session_summary(row)
            value = row_float(summary.get("score", {}).get("averagePerShot"), fallback=None)  # type: ignore[arg-type]
            if value is not None:
                performance_values.append(value)
        except Exception:
            continue
    fallback_overall = score_by_type.get("overall").score_value if score_by_type.get("overall") else None
    if not performance_values and fallback_overall is not None:
        performance_values = [fallback_overall]
    avg_7d_values = [
        value
        for index, value in enumerate(performance_values)
        if index < len([row for row in session_rows if is_recent_date(str(row.get("session_date") or row.get("created_at")), days=7)])
    ]
    best_score = max(performance_values) if performance_values else None
    latest_score = performance_values[0] if performance_values else last_session_avg
    oldest_score = performance_values[-1] if performance_values else None
    improvement_rate = round(latest_score - oldest_score, 2) if latest_score is not None and oldest_score is not None and len(performance_values) > 1 else None

    feedback_rows = list_coach_feedback_rows(supabase=supabase, athlete_id=canonical_athlete_id, limit=50)
    feedback_history = [
        {
            "createdAt": str(row.get("created_at") or ""),
            "status": row.get("status"),
            "note": row.get("note") or "",
            "trainingPlan": row.get("recommendation") or "",
        }
        for row in feedback_rows
    ]
    latest_training_plan = feedback_history[0]["trainingPlan"] if feedback_history else None
    training_plan_rows = safe_table_rows(
        "training_plans",
        supabase.table("training_plans")
        .select("*")
        .eq("athlete_id", canonical_athlete_id)
        .order("updated_at", desc=True)
        .limit(1),
    )
    training_plan_row = training_plan_rows[0] if training_plan_rows else {}
    persisted_training_plan = " / ".join(
        [
            str(value)
            for value in [
                training_plan_row.get("focus_area"),
                training_plan_row.get("recommended_drills"),
                training_plan_row.get("recovery_instructions"),
                training_plan_row.get("mental_training_notes"),
                training_plan_row.get("coach_recommendation"),
            ]
            if value
        ]
    )
    latest_session_date = str(latest_session.get("session_date") or latest_session.get("created_at")) if latest_session else None

    widget = {
        "athleteId": canonical_athlete_id,
        "name": name,
        "initials": initials,
        "coachId": str(athlete_row.get("coach_id") or ""),
        "coachName": coach_user.full_name,
        "age": athlete_row.get("age"),
        "gender": athlete_row.get("gender"),
        "sport": athlete_row.get("academy_id") or (latest_session or {}).get("training_type") or "Shooting",
        "currentStatus": "Needs Review" if latest_training_plan else "Stable",
        "latestSessionDate": latest_session_date,
        "scores": {
            "bestAvg30d": score_by_type.get("best_avg_30d").score_value if score_by_type.get("best_avg_30d") else average_metric(performance_values),
            "avg7d": average_metric(avg_7d_values),
            "periodAvg": score_by_type.get("period_avg").score_value if score_by_type.get("period_avg") else average_metric(performance_values),
            "bestScore": best_score,
            "bestSeries": score_by_type.get("best_series").score_value if score_by_type.get("best_series") else best_series_total,
            "lastSession": score_by_type.get("last_session_avg").score_value if score_by_type.get("last_session_avg") else last_session_avg,
            "improvementRate": improvement_rate,
        },
        "psychology": {
            "social": score_by_type.get("social").score_value if score_by_type.get("social") else None,
            "arousal": score_by_type.get("arousal").score_value if score_by_type.get("arousal") else None,
            "decision": score_by_type.get("decision").score_value if score_by_type.get("decision") else None,
            "focus": score_by_type.get("focus").score_value if score_by_type.get("focus") else None,
            "recovery": score_by_type.get("recovery").score_value if score_by_type.get("recovery") else None,
        },
        "trainingPlan": persisted_training_plan or latest_training_plan,
        "trainingPlanStatus": training_plan_row.get("status") or ("In Progress" if latest_training_plan else "Needs Review"),
        "physiology": {
            "stress": latest_physiology.get("stress_score"),
            "restingHr": latest_physiology.get("resting_heart_rate") or latest_physiology.get("resting_hr"),
            "avgHr": latest_physiology.get("avg_heart_rate"),
            "minHr": latest_physiology.get("min_heart_rate"),
            "maxHr": latest_physiology.get("max_heart_rate"),
            "hrv": latest_physiology.get("rmssd") or latest_physiology.get("hrv") or latest_physiology.get("hrv_ms"),
            "hrStdDev": latest_physiology.get("hr_std_dev"),
            "sleepHours": latest_physiology.get("sleep_hours"),
            "recovery": latest_physiology.get("recovery_score"),
            "fatigue": latest_physiology_fatigue,
            "energyLevel": parse_json_object(latest_physiology.get("remarks")).get("energyLevel"),
            "mood": parse_json_object(latest_physiology.get("remarks")).get("mood"),
            "zones": [
                latest_physiology.get("zone_1_time") or 0,
                latest_physiology.get("zone_2_time") or 0,
                latest_physiology.get("zone_3_time") or 0,
                latest_physiology.get("zone_4_time") or 0,
                latest_physiology.get("zone_5_time") or 0,
            ],
        },
        "holdStability": {
            "stabilityScore": latest_physiology.get("stability_score") or score_by_type.get("hold_stability").score_value if score_by_type.get("hold_stability") else latest_physiology.get("stability_score"),
            "holdStability": latest_physiology.get("acc_hold_stability"),
            "settleScore": latest_physiology.get("acc_settle_score"),
            "spikeCount": latest_physiology.get("acc_spike_count"),
        },
        "feedbackHistory": feedback_history,
    }
    return CoachAthleteProfileWidgetResponse(widget=widget)


@app.get("/api/coach/athletes/{athlete_id}/scores", response_model=AthleteScoresResponse)
def list_coach_athlete_scores(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AthleteScoresResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()
    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access scores for assigned athletes.")
    return AthleteScoresResponse(scores=get_scores_for_athlete(athlete_row))


@app.get("/api/coach/athletes/{athlete_id}/home", response_model=MobileAthleteHomeResponse)
def get_coach_athlete_home(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> MobileAthleteHomeResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access athletes assigned to you.")

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    return get_mobile_athlete_home(athlete_id=canonical_athlete_id)


@app.get("/api/coach/athletes/{athlete_id}/widget", response_model=CoachAthleteWidgetResponse)
def get_coach_athlete_widget(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteWidgetResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access athletes assigned to you.")

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    scores = get_scores_for_athlete(athlete_row)
    score_by_type = {score.score_type: score for score in scores}
    score_map = {score.score_type: round(float(score.score_value), 2) for score in scores}
    latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [canonical_athlete_id], "recorded_date").get(canonical_athlete_id) or {}
    fatigue_burden = fatigue_burden_from_inputs(score_map, latest_physiology)
    home = get_mobile_athlete_home(athlete_id=canonical_athlete_id).home
    recommendations = home.get("recommendations") if isinstance(home, dict) else None

    next_focus = None
    if isinstance(recommendations, list) and recommendations:
        first = str(recommendations[0])
        lowered = first.lower()
        if "breathing" in lowered or "cool-down" in lowered or "cool down" in lowered:
            next_focus = "Hold"
        elif "check-in" in lowered or "checkin" in lowered:
            next_focus = "Settle"
        elif "training" in lowered or "session" in lowered:
            next_focus = "Shoot"
        else:
            next_focus = first.split(".")[0][:24]

    widget = {
        "athleteId": canonical_athlete_id,
        "readiness": score_by_type.get("readiness").score_value if score_by_type.get("readiness") else None,
        "performance": score_by_type.get("overall").score_value if score_by_type.get("overall") else None,
        "fatigue": fatigue_burden,
        "nextFocus": next_focus,
    }
    return CoachAthleteWidgetResponse(widget=widget)


@app.get("/api/coach/athletes/{athlete_id}/sessions-widget", response_model=CoachAthleteSessionsWidgetResponse)
def get_coach_athlete_sessions_widget(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteSessionsWidgetResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access athletes assigned to you.")

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)

    # Use existing mobile session summary computation (derived from scoring series + session logs).
    session_rows = safe_table_rows(
        APP_TABLES["shooting_session_log"],
        supabase.table(APP_TABLES["shooting_session_log"]).select("*").eq("athlete_id", canonical_athlete_id).order("session_date", desc=True).limit(3),
    )
    latest_session = session_rows[0] if session_rows else None
    latest_summary = None
    if latest_session and latest_session.get("session_id"):
        try:
            latest_summary = build_mobile_session_summary(latest_session)
        except Exception:
            latest_summary = None

    scores = get_scores_for_athlete(athlete_row)
    score_by_type = {score.score_type: score for score in scores}
    score_map = {score.score_type: round(float(score.score_value), 2) for score in scores}
    latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [canonical_athlete_id], "recorded_date").get(canonical_athlete_id) or {}
    fatigue_burden = fatigue_burden_from_inputs(score_map, latest_physiology)

    def session_date(row: dict[str, Any]) -> str | None:
        value = row.get("session_date") or row.get("created_at")
        return str(value) if value else None

    history: list[dict[str, Any]] = []
    for row in session_rows[:2]:
        row_summary = None
        try:
            row_summary = build_mobile_session_summary(row)
        except Exception:
            row_summary = None
        row_score = (row_summary or {}).get("score", {}) if isinstance(row_summary, dict) else {}
        row_physiology = (row_summary or {}).get("physiology", {}) if isinstance(row_summary, dict) else {}
        row_reflection = ((row_summary or {}).get("mentalState", {}) or {}).get("reflection") if isinstance(row_summary, dict) else None
        history.append(
            {
                "sessionId": str(row.get("session_id") or ""),
                "sessionDate": session_date(row),
                "trainingType": row.get("training_type") or row.get("session_type") or "Shooting",
                # Keep these aligned to the Sessions mock: "Score", "Ready", "Fatigue"
                "performance": row_score.get("averagePerShot") or (score_by_type.get("overall").score_value if score_by_type.get("overall") else None),
                "readiness": score_by_type.get("readiness").score_value if score_by_type.get("readiness") else None,
                "bestSeries": (row_score.get("bestSeries") or {}).get("total") if isinstance(row_score.get("bestSeries"), dict) else None,
                "avgHr": row_physiology.get("avgHeartRate"),
                "fatigue": fatigue_burden,
                "recovery": latest_physiology.get("recovery_score"),
                "reflection": (row_reflection or {}).get("whatWorked") if isinstance(row_reflection, dict) else row.get("athlete_notes") or row.get("notes"),
                "coachNotes": row.get("coach_notes") or "",
            }
        )

    widget = {
        "athleteId": canonical_athlete_id,
        "lastSession": {
            "sessionId": str((latest_session or {}).get("session_id") or ""),
            "sessionDate": session_date(latest_session or {}),
            "performance": (latest_summary or {}).get("score", {}).get("averagePerShot") if isinstance(latest_summary, dict) else None,
            "readiness": score_by_type.get("readiness").score_value if score_by_type.get("readiness") else None,
            "holdStability": score_by_type.get("hold_stability").score_value if score_by_type.get("hold_stability") else None,
            "mentalScore": score_by_type.get("mental_score").score_value if score_by_type.get("mental_score") else None,
            "fatigue": fatigue_burden,
            "summaryTitle": (latest_summary or {}).get("keyInsight", {}).get("title") if isinstance(latest_summary, dict) else None,
        },
        "history": history,
    }
    return CoachAthleteSessionsWidgetResponse(widget=widget)


def list_coach_feedback_rows(*, supabase: Any, athlete_id: str, limit: int = 20) -> list[dict[str, Any]]:
    return safe_table_rows(
        APP_TABLES["coach_feedback"],
        supabase.table(APP_TABLES["coach_feedback"]).select("*").eq("athlete_id", athlete_id).order("created_at", desc=True).limit(limit),
    )


@app.get("/api/coach/athletes/{athlete_id}/insights-widget", response_model=CoachAthleteInsightsWidgetResponse)
def get_coach_athlete_insights_widget(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteInsightsWidgetResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access athletes assigned to you.")

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    scores = get_scores_for_athlete(athlete_row)
    score_by_type = {score.score_type: score for score in scores}

    feedback_rows = list_coach_feedback_rows(supabase=supabase, athlete_id=canonical_athlete_id, limit=20)
    feedback_history = [
        {
            "createdAt": str(row.get("created_at") or ""),
            "status": row.get("status"),
            "note": row.get("note") or row.get("coach_observations") or "",
            "trainingPlan": row.get("recommendation") or row.get("training_plan") or "",
        }
        for row in feedback_rows
    ]
    latest_training_plan = feedback_history[0]["trainingPlan"] if feedback_history else None

    # Use mobile recommendations when no coach plan exists.
    home = get_mobile_athlete_home(athlete_id=canonical_athlete_id).home
    recommendations = home.get("recommendations") if isinstance(home, dict) else None
    fallback_plan = None
    if isinstance(recommendations, list) and recommendations:
        fallback_plan = " / ".join([str(item) for item in recommendations[:2]])
    insight_rows = safe_table_rows(
        "athlete_insights",
        supabase.table("athlete_insights")
        .select("title,insight_text,category,score,priority,suggested_action,supporting_data,created_at")
        .eq("athlete_id", canonical_athlete_id)
        .order("created_at", desc=True)
        .limit(20),
    )
    insight_history = [
        {
            "title": str(row.get("title") or "Insight"),
            "insightText": str(row.get("insight_text") or ""),
            "category": str(row.get("category") or "coach"),
            "score": row_float(row.get("score"), fallback=None),  # type: ignore[arg-type]
            "priority": row.get("priority") if row.get("priority") in {"High", "Medium", "Low"} else "Medium",
            "suggestedAction": row.get("suggested_action") or "",
            "supportingData": row.get("supporting_data") if isinstance(row.get("supporting_data"), dict) else {},
            "createdAt": str(row.get("created_at") or ""),
        }
        for row in insight_rows
    ]

    widget = {
        "athleteId": canonical_athlete_id,
        "scores": {
            "social": score_by_type.get("social").score_value if score_by_type.get("social") else None,
            "arousal": score_by_type.get("arousal").score_value if score_by_type.get("arousal") else None,
            "decision": score_by_type.get("decision").score_value if score_by_type.get("decision") else None,
            "focus": score_by_type.get("focus").score_value if score_by_type.get("focus") else None,
        },
        "recommendation": latest_training_plan or fallback_plan,
        "feedbackHistory": feedback_history,
        "insights": insight_history,
    }
    return CoachAthleteInsightsWidgetResponse(widget=widget)


@app.get("/api/coach/athletes/{athlete_id}/profile-widget", response_model=CoachAthleteProfileWidgetResponse)
def get_coach_athlete_profile_widget(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteProfileWidgetResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access athletes assigned to you.")

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    name = str(athlete_row.get("athlete_name") or athlete_row.get("name") or "Athlete")
    initials = "".join([part[:1].upper() for part in name.split()[:2]]) or "A"

    scores = get_scores_for_athlete(athlete_row)
    score_by_type = {score.score_type: score for score in scores}

    session_rows = safe_table_rows(
        APP_TABLES["shooting_session_log"],
        supabase.table(APP_TABLES["shooting_session_log"]).select("*").eq("athlete_id", canonical_athlete_id).order("session_date", desc=True).limit(30),
    )
    latest_session = session_rows[0] if session_rows else None
    latest_summary = None
    if latest_session:
        try:
            latest_summary = build_mobile_session_summary(latest_session)
        except Exception:
            latest_summary = None

    last_session_avg = None
    best_series_total = None
    if isinstance(latest_summary, dict):
        last_session_avg = latest_summary.get("score", {}).get("averagePerShot")
        best_series = latest_summary.get("score", {}).get("bestSeries")
        if isinstance(best_series, dict):
            best_series_total = best_series.get("total")
    latest_physiology = get_latest_rows_by_athlete(APP_TABLES["athlete_physiology"], [canonical_athlete_id], "recorded_date").get(canonical_athlete_id) or {}
    latest_physiology_fatigue = fatigue_burden_from_inputs({score.score_type: score.score_value for score in scores}, latest_physiology)
    performance_values: list[float] = []
    for row in session_rows:
        try:
            summary = build_mobile_session_summary(row)
            value = row_float(summary.get("score", {}).get("averagePerShot"), fallback=None)  # type: ignore[arg-type]
            if value is not None:
                performance_values.append(value)
        except Exception:
            continue
    fallback_overall = score_by_type.get("overall").score_value if score_by_type.get("overall") else None
    if not performance_values and fallback_overall is not None:
        performance_values = [fallback_overall]
    avg_7d_values = [
        value
        for index, value in enumerate(performance_values)
        if index < len([row for row in session_rows if is_recent_date(str(row.get("session_date") or row.get("created_at")), days=7)])
    ]
    best_score = max(performance_values) if performance_values else None
    latest_score = performance_values[0] if performance_values else last_session_avg
    oldest_score = performance_values[-1] if performance_values else None
    improvement_rate = round(latest_score - oldest_score, 2) if latest_score is not None and oldest_score is not None and len(performance_values) > 1 else None

    feedback_rows = list_coach_feedback_rows(supabase=supabase, athlete_id=canonical_athlete_id, limit=50)
    feedback_history = [
        {
            "createdAt": str(row.get("created_at") or ""),
            "status": row.get("status"),
            "note": row.get("note") or "",
            "trainingPlan": row.get("recommendation") or "",
        }
        for row in feedback_rows
    ]
    latest_training_plan = feedback_history[0]["trainingPlan"] if feedback_history else None
    training_plan_rows = safe_table_rows(
        "training_plans",
        supabase.table("training_plans")
        .select("*")
        .eq("athlete_id", canonical_athlete_id)
        .order("updated_at", desc=True)
        .limit(1),
    )
    training_plan_row = training_plan_rows[0] if training_plan_rows else {}
    persisted_training_plan = " / ".join(
        [
            str(value)
            for value in [
                training_plan_row.get("focus_area"),
                training_plan_row.get("recommended_drills"),
                training_plan_row.get("recovery_instructions"),
                training_plan_row.get("mental_training_notes"),
                training_plan_row.get("coach_recommendation"),
            ]
            if value
        ]
    )
    latest_session_date = str(latest_session.get("session_date") or latest_session.get("created_at")) if latest_session else None

    widget = {
        "athleteId": canonical_athlete_id,
        "name": name,
        "initials": initials,
        "coachId": str(athlete_row.get("coach_id") or ""),
        "coachName": coach_user.full_name,
        "age": athlete_row.get("age"),
        "gender": athlete_row.get("gender"),
        "sport": athlete_row.get("academy_id") or (latest_session or {}).get("training_type") or "Shooting",
        "currentStatus": "Needs Review" if latest_training_plan else "Stable",
        "latestSessionDate": latest_session_date,
        "scores": {
            "bestAvg30d": score_by_type.get("best_avg_30d").score_value if score_by_type.get("best_avg_30d") else average_metric(performance_values),
            "avg7d": average_metric(avg_7d_values),
            "periodAvg": score_by_type.get("period_avg").score_value if score_by_type.get("period_avg") else average_metric(performance_values),
            "bestScore": best_score,
            "bestSeries": score_by_type.get("best_series").score_value if score_by_type.get("best_series") else best_series_total,
            "lastSession": score_by_type.get("last_session_avg").score_value if score_by_type.get("last_session_avg") else last_session_avg,
            "improvementRate": improvement_rate,
        },
        "psychology": {
            "social": score_by_type.get("social").score_value if score_by_type.get("social") else None,
            "arousal": score_by_type.get("arousal").score_value if score_by_type.get("arousal") else None,
            "decision": score_by_type.get("decision").score_value if score_by_type.get("decision") else None,
            "focus": score_by_type.get("focus").score_value if score_by_type.get("focus") else None,
            "recovery": score_by_type.get("recovery").score_value if score_by_type.get("recovery") else None,
        },
        "trainingPlan": persisted_training_plan or latest_training_plan,
        "trainingPlanStatus": training_plan_row.get("status") or ("In Progress" if latest_training_plan else "Needs Review"),
        "physiology": {
            "stress": latest_physiology.get("stress_score"),
            "restingHr": latest_physiology.get("resting_heart_rate") or latest_physiology.get("resting_hr"),
            "avgHr": latest_physiology.get("avg_heart_rate"),
            "minHr": latest_physiology.get("min_heart_rate"),
            "maxHr": latest_physiology.get("max_heart_rate"),
            "hrv": latest_physiology.get("rmssd") or latest_physiology.get("hrv") or latest_physiology.get("hrv_ms"),
            "hrStdDev": latest_physiology.get("hr_std_dev"),
            "sleepHours": latest_physiology.get("sleep_hours"),
            "recovery": latest_physiology.get("recovery_score"),
            "fatigue": latest_physiology_fatigue,
            "energyLevel": parse_json_object(latest_physiology.get("remarks")).get("energyLevel"),
            "mood": parse_json_object(latest_physiology.get("remarks")).get("mood"),
            "zones": [
                latest_physiology.get("zone_1_time") or 0,
                latest_physiology.get("zone_2_time") or 0,
                latest_physiology.get("zone_3_time") or 0,
                latest_physiology.get("zone_4_time") or 0,
                latest_physiology.get("zone_5_time") or 0,
            ],
        },
        "holdStability": {
            "stabilityScore": latest_physiology.get("stability_score") or score_by_type.get("hold_stability").score_value if score_by_type.get("hold_stability") else latest_physiology.get("stability_score"),
            "holdStability": latest_physiology.get("acc_hold_stability"),
            "settleScore": latest_physiology.get("acc_settle_score"),
            "spikeCount": latest_physiology.get("acc_spike_count"),
        },
        "feedbackHistory": feedback_history,
    }
    return CoachAthleteProfileWidgetResponse(widget=widget)


@app.get("/api/coach/athletes/{athlete_id}/scores", response_model=AthleteScoresResponse)
def list_coach_athlete_scores(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AthleteScoresResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()
    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access scores for assigned athletes.")
    return AthleteScoresResponse(scores=get_scores_for_athlete(athlete_row))


@app.get("/api/coach/athletes/{athlete_id}/feedback", response_model=CoachFeedbackListResponse)
def list_coach_athlete_feedback(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachFeedbackListResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()
    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access feedback for athletes assigned to you.",
        )

    response = (
        supabase.table(APP_TABLES["coach_feedback"])
        .select("*")
        .eq("athlete_id", str(athlete_row.get("athlete_id") or athlete_id))
        .order("created_at", desc=True)
        .execute()
    )
    feedback = [serialize_feedback_item(
        {
            "feedbackId": item["feedback_id"],
            "athleteId": item["athlete_id"],
            "athleteName": item["athlete_name"],
            "athleteEmail": item["athlete_email"],
            "coachEmail": item["coach_email"],
            "coachName": item["coach_name"],
            "note": item["note"],
            "recommendation": item["recommendation"],
            "status": item["status"],
            "createdAt": item["created_at"],
        }
    ) for item in response.data or []]
    feedback.sort(key=lambda item: item.created_at, reverse=True)
    return CoachFeedbackListResponse(feedback=feedback)


@app.post("/api/coach/athletes/{athlete_id}/feedback", response_model=CoachFeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_coach_athlete_feedback(
    athlete_id: str,
    payload: CoachFeedbackInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachFeedbackResponse:
    coach_user = ensure_coach_user(session_token)
    coach_key = resolve_dashboard_coach_key(coach_user)
    supabase = ensure_supabase()

    athlete_row = resolve_athlete_row_by_identifier(supabase, athlete_id)
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if not coach_can_access_athlete(supabase=supabase, coach_id=coach_key, athlete_row=athlete_row):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only leave feedback for athletes assigned to you.",
        )

    canonical_athlete_id = str(athlete_row.get("athlete_id") or athlete_id)
    feedback_item = {
        "feedback_id": str(uuid4()),
        "athlete_id": canonical_athlete_id,
        "athlete_name": athlete_row.get("athlete_name") or athlete_row.get("name") or "Athlete",
        "athlete_email": athlete_row.get("email") or "",
        "coach_email": coach_user.email,
        "coach_name": coach_user.full_name,
        "note": payload.note,
        "recommendation": payload.recommendation,
        "status": payload.status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table(APP_TABLES["coach_feedback"]).insert(feedback_item).execute()
    return CoachFeedbackResponse(
        feedback=serialize_feedback_item(
            {
                "feedbackId": feedback_item["feedback_id"],
                "athleteId": feedback_item["athlete_id"],
                "athleteName": feedback_item["athlete_name"],
                "athleteEmail": feedback_item["athlete_email"],
                "coachEmail": feedback_item["coach_email"],
                "coachName": feedback_item["coach_name"],
                "note": feedback_item["note"],
                "recommendation": feedback_item["recommendation"],
                "status": feedback_item["status"],
                "createdAt": feedback_item["created_at"],
            }
        )
    )


@app.get("/api/student/feedback", response_model=CoachFeedbackListResponse)
def list_student_feedback(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachFeedbackListResponse:
    user = get_authenticated_user(session_token)
    if user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only student accounts can access this feedback feed.",
        )

    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["coach_feedback"])
        .select("*")
        .eq("athlete_email", user.email.lower())
        .order("created_at", desc=True)
        .execute()
    )
    feedback = [serialize_feedback_item(
        {
            "feedbackId": item["feedback_id"],
            "athleteId": item["athlete_id"],
            "athleteName": item["athlete_name"],
            "athleteEmail": item["athlete_email"],
            "coachEmail": item["coach_email"],
            "coachName": item["coach_name"],
            "note": item["note"],
            "recommendation": item["recommendation"],
            "status": item["status"],
            "createdAt": item["created_at"],
        }
    ) for item in response.data or []]
    feedback.sort(key=lambda item: item.created_at, reverse=True)
    return CoachFeedbackListResponse(feedback=feedback)


@app.post("/api/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignUpRequest, response: Response) -> AuthResponse:
    ensure_seed_data()
    email = payload.email.lower()

    if get_user_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    if payload.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public signup is available for student accounts only.",
        )

    assigned_coach = get_primary_coach()
    user = create_user_record(
        email=email,
        full_name=payload.full_name,
        password=payload.password,
        role="student",
        assignment_status="assigned",
        assigned_coach_email=assigned_coach.email.lower(),
        assigned_coach_name=assigned_coach.full_name,
        sport=payload.sport,
        focus_area=payload.focus_area,
        date_of_birth=payload.date_of_birth.isoformat() if payload.date_of_birth else None,
        performance_score=get_next_student_score(),
    )
    stored_user = upsert_user(user)
    session_token = create_persistent_session(stored_user.email)

    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_token,
        httponly=True,
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
        max_age=60 * 60 * 8,
    )

    return AuthResponse(user=to_public_user(stored_user))


@app.post("/api/student/coach-request", response_model=AuthResponse)
def create_student_coach_request(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AuthResponse:
    user = get_authenticated_user(session_token)
    updated_user = request_coach_assignment_for_student(user)
    return AuthResponse(user=to_public_user(updated_user))


@app.post("/api/mobile/athletes/register", response_model=MobileAthleteRegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_mobile_athlete(payload: MobileAthleteRegistrationInput) -> MobileAthleteRegistrationResponse:
    ensure_seed_data()
    supabase = ensure_supabase()
    email = payload.email.lower()
    target_coach_id, target_coach_email = get_assignment_target_for_registration(payload)
    target_coach_user = get_user_by_email(target_coach_email) if target_coach_email else None
    target_coach_name = target_coach_user.full_name if target_coach_user else "HamsaTech Coach"

    user = get_user_by_email(email)
    if not user:
        user = upsert_user(
            create_user_record(
                email=email,
                full_name=payload.full_name,
                password=f"Mobile{uuid4().hex[:10]}!",
                role="student",
                assignment_status="pending",
                assigned_coach_email=None,
                assigned_coach_name=None,
                requested_coach_email=target_coach_email,
                requested_coach_name=target_coach_name,
                requested_coach_code=None,
                coach_request_sent_at=datetime.now(timezone.utc).isoformat(),
                sport=payload.sport,
                focus_area=payload.focus_area,
                performance_score=get_next_student_score(),
            )
        )
    athlete_id = payload.athlete_id or str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    athlete_row = {
        "athlete_id": athlete_id,
        "name": payload.full_name,
        "age": payload.age,
        "gender": payload.gender,
        "height_cm": 1,
        "weight_kg": 1,
        "academy_id": payload.sport or "Mobile",
        "coach_id": "",
        "contact_number": payload.phone,
        "email": email,
        "created_at": now,
        "updated_by": "mobile-app",
        "registration_source": "mobile_app",
        "onboarding_status": "registered",
        "profile_completion_status": payload.profile_completion_status,
        "updated_at": now,
    }
    try:
        supabase.table(APP_TABLES["athletes"]).upsert(athlete_row, on_conflict="athlete_id").execute()
    except Exception as exception:
        legacy_row = {
            key: athlete_row[key]
            for key in (
                "athlete_id",
                "name",
                "age",
                "gender",
                "height_cm",
                "weight_kg",
                "academy_id",
                "coach_id",
                "contact_number",
                "email",
                "created_at",
                "updated_by",
            )
        }
        try:
            supabase.table(APP_TABLES["athletes"]).upsert(legacy_row, on_conflict="athlete_id").execute()
            athlete_row = legacy_row
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save mobile registration: {exception}") from exception

    request_id = create_assignment_request_for_athlete(
        athlete_id=athlete_id,
        athlete_name=payload.full_name,
        target_coach_id=target_coach_id,
        target_coach_email=target_coach_email,
        notes="Auto-created from mobile athlete registration",
    )
    write_audit_log(
        actor_email=email,
        action="mobile_athlete_registered",
        entity_type="athlete",
        entity_id=athlete_id,
        metadata={"targetCoachId": target_coach_id, "targetCoachEmail": target_coach_email, "assignmentRequestId": request_id},
    )
    sync_latest_overall_score(athlete_row)
    return MobileAthleteRegistrationResponse(
        athleteId=athlete_id,
        assignedCoachEmail=target_coach_email,
        notificationCreated=bool(request_id),
        success=True,
    )


@app.get("/api/mobile/athletes/{athlete_id}/profile", response_model=MobileAthleteProfileResponse)
def get_mobile_athlete_profile(athlete_id: str) -> MobileAthleteProfileResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    profile_row = get_mobile_profile_row(athlete_id)
    return MobileAthleteProfileResponse(profile=serialize_mobile_profile(profile_row, athlete_row))


@app.put("/api/mobile/athletes/{athlete_id}/profile", response_model=MobileAthleteProfileResponse)
def upsert_mobile_athlete_profile(
    athlete_id: str,
    payload: MobileAthleteProfileUpsertInput,
) -> MobileAthleteProfileResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    existing_profile = get_mobile_profile_row(athlete_id) or {}
    performance = parse_json_object(existing_profile.get("academic_performance"))
    shooting = parse_json_object(existing_profile.get("reason_for_shooting"))
    goals = parse_json_object(existing_profile.get("athlete_goal"))
    athlete_update: dict[str, Any] = {"updated_by": "mobile-app"}

    if payload.performance_factors is not None and len(normalize_text_list(payload.performance_factors)) > 3:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Select up to 3 performance factors.")
    if payload.full_name is not None:
        athlete_update["name"] = payload.full_name
    if payload.age is not None:
        athlete_update["age"] = payload.age
    if payload.gender is not None:
        athlete_update["gender"] = payload.gender
    if payload.city is not None:
        shooting["city"] = payload.city
    if payload.discipline is not None:
        shooting["discipline"] = payload.discipline
        athlete_update["academy_id"] = payload.discipline
    if payload.experience_level is not None:
        performance["experienceLevel"] = payload.experience_level
    if payload.years_shooting is not None:
        performance["yearsShooting"] = payload.years_shooting
    if payload.academy_club is not None:
        shooting["academyClub"] = payload.academy_club
        if payload.academy_club.strip():
            athlete_update["academy_id"] = payload.academy_club
    if payload.average_practice_score is not None:
        performance["averagePracticeScore"] = payload.average_practice_score
    if payload.target_score is not None:
        performance["targetScore"] = payload.target_score
    if payload.performance_factors is not None:
        shooting["performanceFactors"] = normalize_text_list(payload.performance_factors)
    if payload.goal_30_days is not None:
        goals["goal30Days"] = payload.goal_30_days
    if payload.goal_6_months is not None:
        goals["goal6Months"] = payload.goal_6_months

    profile_status_data = {
        "full_name": athlete_update.get("name") or athlete_row.get("name") or athlete_row.get("athlete_name"),
        "age": athlete_update.get("age") or athlete_row.get("age"),
        "gender": athlete_update.get("gender") or athlete_row.get("gender"),
        "discipline": shooting.get("discipline") or athlete_update.get("academy_id") or athlete_row.get("academy_id"),
        "average_practice_score": performance.get("averagePracticeScore"),
        "target_score": performance.get("targetScore"),
        "goal_30_days": goals.get("goal30Days"),
        "goal_6_months": goals.get("goal6Months"),
    }
    baseline = get_mobile_baseline_row(athlete_id)
    onboarding_status, completion_status = compute_mobile_profile_status(
        profile_status_data,
        row_number((baseline or {}).get("resting_heart_rate"), fallback=None),  # type: ignore[arg-type]
    )
    athlete_update["onboarding_status"] = onboarding_status
    athlete_update["profile_completion_status"] = completion_status
    athlete_update["updated_at"] = datetime.now(timezone.utc).isoformat()

    profile_payload = {
        "details_id": existing_profile.get("details_id") or str(uuid4()),
        "athlete_id": athlete_id,
        "class": existing_profile.get("class") or "Mobile",
        "school_name": existing_profile.get("school_name") or shooting.get("city") or "Not provided",
        "diet_type": existing_profile.get("diet_type") or "Mixed",
        "outside_food_frequency": existing_profile.get("outside_food_frequency") or "Rare",
        "sleep_time": existing_profile.get("sleep_time") or "22:00",
        "wake_time": existing_profile.get("wake_time") or "06:00",
        "friend_circle": existing_profile.get("friend_circle") or "Not provided",
        "anger_pattern": existing_profile.get("anger_pattern") or "Not provided",
        "sadness_pattern": existing_profile.get("sadness_pattern") or "Not provided",
        "academic_performance": compact_json(performance),
        "reason_for_shooting": compact_json(shooting),
        "athlete_goal": compact_json(goals),
    }

    try:
        if existing_profile:
            supabase.table(APP_TABLES["athlete_details"]).update(profile_payload).eq("athlete_id", athlete_id).execute()
        else:
            supabase.table(APP_TABLES["athlete_details"]).insert(profile_payload).execute()
        try:
            supabase.table(APP_TABLES["athletes"]).update(athlete_update).eq("athlete_id", athlete_id).execute()
        except Exception:
            legacy_update = {
                key: value
                for key, value in athlete_update.items()
                if key not in {"onboarding_status", "profile_completion_status", "updated_at"}
            }
            if legacy_update:
                supabase.table(APP_TABLES["athletes"]).update(legacy_update).eq("athlete_id", athlete_id).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save athlete profile: {exception}") from exception

    write_audit_log(
        actor_email=str(athlete_row.get("email") or ""),
        action="mobile_athlete_profile_saved",
        entity_type="athlete",
        entity_id=athlete_id,
        metadata={"profileCompletionStatus": completion_status, "onboardingStatus": onboarding_status},
    )
    updated_athlete_row = ensure_mobile_athlete_row(athlete_id)
    return MobileAthleteProfileResponse(profile=serialize_mobile_profile(get_mobile_profile_row(athlete_id), updated_athlete_row))


@app.post("/api/mobile/athletes/{athlete_id}/baseline", response_model=MobileAthleteProfileResponse)
def save_mobile_athlete_baseline(
    athlete_id: str,
    payload: MobileBaselineInput,
) -> MobileAthleteProfileResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    now = datetime.now(timezone.utc)
    session_id = str(uuid4())
    session_row = {
        "session_id": session_id,
        "athlete_id": athlete_id,
        "coach_id": str(athlete_row.get("coach_id") or ""),
        "session_date": now.date().isoformat(),
        "start_time": now.strftime("%H:%M"),
        "end_time": now.strftime("%H:%M"),
        "duration_minutes": 0,
        "training_type": "Recovery",
        "location": "Polar baseline",
        "notes": compact_json({"source": "mobile_baseline", "polarLinked": payload.polar_linked}),
    }
    physiology_row = {
        "physiology_id": str(uuid4()),
        "athlete_id": athlete_id,
        "session_id": session_id,
        "recorded_date": now.date().isoformat(),
        "resting_heart_rate": payload.resting_hr_baseline,
        "avg_heart_rate": payload.resting_hr_baseline,
        "spo2": 98,
        "breathing_rate": 12,
        "sleep_hours": 0,
        "recovery_score": 50,
        "stress_score": 50,
        "fatigue_level": 0,
        "remarks": compact_json({"source": "mobile_baseline", "hrvBaselineMs": payload.hrv_baseline_ms}),
    }
    profile = serialize_mobile_profile(get_mobile_profile_row(athlete_id), athlete_row)
    onboarding_status = "ready_to_train" if profile.profile_completion_status == "complete" else profile.onboarding_status

    try:
        supabase.table(APP_TABLES["shooting_session_log"]).insert(session_row).execute()
        supabase.table(APP_TABLES["athlete_physiology"]).insert(physiology_row).execute()
        try:
            supabase.table(APP_TABLES["athletes"]).update(
                {
                    "onboarding_status": onboarding_status,
                    "profile_completion_status": profile.profile_completion_status,
                    "updated_at": now.isoformat(),
                    "updated_by": "mobile-app",
                }
            ).eq("athlete_id", athlete_id).execute()
        except Exception:
            supabase.table(APP_TABLES["athletes"]).update({"updated_by": "mobile-app"}).eq("athlete_id", athlete_id).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save baseline: {exception}") from exception

    write_audit_log(
        actor_email=str(athlete_row.get("email") or ""),
        action="mobile_athlete_baseline_saved",
        entity_type="athlete",
        entity_id=athlete_id,
        metadata={"restingHrBaseline": payload.resting_hr_baseline},
    )
    return MobileAthleteProfileResponse(profile=serialize_mobile_profile(get_mobile_profile_row(athlete_id), ensure_mobile_athlete_row(athlete_id)))


@app.post("/api/mobile/athletes/{athlete_id}/daily-checkins", response_model=MobileDailyCheckinResponse, status_code=status.HTTP_201_CREATED)
def save_mobile_daily_checkin(
    athlete_id: str,
    payload: MobileDailyCheckinInput,
) -> MobileDailyCheckinResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    seed_psychology_questions()
    supabase = ensure_supabase()
    now = datetime.now(timezone.utc).isoformat()
    checkin_payload = {
        "checkinDate": (payload.checkin_date or date.today()).isoformat(),
        "mood": payload.mood,
        "energyLevel": payload.energy_level,
        "sleepBand": payload.sleep_band,
        "sleepHours": payload.sleep_hours,
        "tags": normalize_text_list(payload.tags),
        "notes": payload.notes,
    }
    row = {
        "answer_id": str(uuid4()),
        "athlete_id": athlete_id,
        "question_id": "MOBILE_DAILY_CHECKIN",
        "answer_text": compact_json(checkin_payload),
        "answer_score": payload.energy_level,
        "recorded_at": now,
    }
    try:
        supabase.table(APP_TABLES["psychology_responses"]).insert(row).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save daily check-in: {exception}") from exception

    notify_coach_of_athlete_activity(
        athlete_row=athlete_row,
        title="Daily check-in submitted",
        message=f"{athlete_row.get('name') or athlete_row.get('athlete_name') or 'Athlete'} submitted a daily check-in.",
        notification_type="DAILY_CHECKIN",
        action_url=f"/coach/athletes/{athlete_id}",
    )
    return MobileDailyCheckinResponse(checkin=serialize_mobile_checkin(row))


@app.get("/api/mobile/athletes/{athlete_id}/daily-checkins/latest", response_model=MobileDailyCheckinResponse)
def get_mobile_latest_daily_checkin(athlete_id: str) -> MobileDailyCheckinResponse:
    ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["psychology_responses"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("question_id", "MOBILE_DAILY_CHECKIN")
        .order("recorded_at", desc=True)
        .limit(1)
        .execute()
    )
    row = (response.data or [None])[0]
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No check-in found.")
    return MobileDailyCheckinResponse(checkin=serialize_mobile_checkin(row))


@app.get("/api/mobile/athletes/{athlete_id}/home", response_model=MobileAthleteHomeResponse)
def get_mobile_athlete_home(athlete_id: str) -> MobileAthleteHomeResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    profile = serialize_mobile_profile(get_mobile_profile_row(athlete_id), athlete_row)
    checkin_rows = safe_table_rows(
        APP_TABLES["psychology_responses"],
        supabase.table(APP_TABLES["psychology_responses"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("question_id", "MOBILE_DAILY_CHECKIN")
        .order("recorded_at", desc=True)
        .limit(1),
    )
    latest_checkin = serialize_mobile_checkin(checkin_rows[0]) if checkin_rows else None
    session_rows = safe_table_rows(
        APP_TABLES["shooting_session_log"],
        supabase.table(APP_TABLES["shooting_session_log"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .order("session_date", desc=True)
        .limit(3),
    )
    feedback_rows = safe_table_rows(
        APP_TABLES["coach_feedback"],
        supabase.table(APP_TABLES["coach_feedback"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .order("created_at", desc=True)
        .limit(3),
    )
    readiness = calculate_readiness(profile, latest_checkin)
    sleep_hours = latest_checkin.sleep_hours if latest_checkin else None
    if sleep_hours is None and latest_checkin:
        sleep_hours = sleep_band_to_hours(latest_checkin.sleep_band)
    recommendations = ["Start today's check-in"] if not latest_checkin else ["Start training session"]
    if readiness < 60:
        recommendations.insert(0, "Complete a breathing cool-down before shooting")

    return MobileAthleteHomeResponse(
        home={
            "athleteId": athlete_id,
            "displayName": profile.full_name or athlete_row.get("name") or "Athlete",
            "profileCompletionStatus": profile.profile_completion_status,
            "onboardingStatus": profile.onboarding_status,
            "polar": {
                "linked": profile.polar_linked,
                "deviceId": profile.polar_device_id,
            },
            "metrics": {
                "readiness": readiness,
                "sleepHours": sleep_hours,
                "restingHr": profile.resting_hr_baseline,
                "hrvMs": profile.hrv_baseline_ms,
            },
            "dailyCheckin": latest_checkin.model_dump(by_alias=True) if latest_checkin else None,
            "recentSessions": [serialize_mobile_session(row) for row in session_rows],
            "coachFeedback": [
                {
                    "feedbackId": str(row.get("feedback_id") or ""),
                    "coachName": row.get("coach_name") or "Coach",
                    "note": row.get("note") or row.get("coach_observations") or "",
                    "recommendation": row.get("recommendation"),
                    "status": row.get("status"),
                    "createdAt": row.get("created_at"),
                }
                for row in feedback_rows
            ],
            "recommendations": recommendations,
        }
    )


@app.post("/api/mobile/athletes/{athlete_id}/sessions", response_model=MobileTrainingSessionResponse, status_code=status.HTTP_201_CREATED)
def create_mobile_training_session(
    athlete_id: str,
    payload: MobileTrainingSessionCreateInput,
) -> MobileTrainingSessionResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    session_id = str(uuid4())
    start_time = datetime.now(timezone.utc)
    notes = {
        "source": "mobile_training_session",
        "rangeType": payload.range_type,
        "sessionType": payload.session_type,
        "plannedShots": payload.planned_shots,
        "discipline": payload.discipline or athlete_row.get("academy_id"),
        "intention": payload.intention,
        "visualization": payload.visualization,
        "bodyScanCompleted": payload.body_scan_completed,
        "status": "LIVE" if payload.start_now else "SETUP",
    }
    row = {
        "session_id": session_id,
        "athlete_id": athlete_id,
        "coach_id": str(athlete_row.get("coach_id") or ""),
        "session_date": start_time.date().isoformat(),
        "start_time": start_time.strftime("%H:%M"),
        "end_time": start_time.strftime("%H:%M"),
        "duration_minutes": 0,
        "training_type": "Mental" if payload.session_type == "Dry Fire" else "Shooting",
        "location": payload.range_type,
        "notes": compact_json(notes),
    }
    try:
        supabase.table(APP_TABLES["shooting_session_log"]).insert(row).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to create training session: {exception}") from exception
    notify_coach_of_athlete_activity(
        athlete_row=athlete_row,
        title="Training session started",
        message=f"{athlete_row.get('name') or athlete_row.get('athlete_name') or 'Athlete'} started a training session.",
        notification_type="TRAINING_SESSION_STARTED",
        related_session_id=session_id,
        action_url=f"/coach/athletes/{athlete_id}",
    )
    return MobileTrainingSessionResponse(session=serialize_mobile_session(row))


@app.get("/api/mobile/athletes/{athlete_id}/sessions", response_model=MobileTrainingSessionsResponse)
def list_mobile_training_sessions(
    athlete_id: str,
    limit: int = Query(default=20, ge=1, le=100),
) -> MobileTrainingSessionsResponse:
    ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["shooting_session_log"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .order("session_date", desc=True)
        .limit(limit)
        .execute()
    )
    return MobileTrainingSessionsResponse(sessions=[serialize_mobile_session(row) for row in response.data or []])


@app.post("/api/mobile/athletes/{athlete_id}/sessions/{session_id}/series", response_model=MobileTrainingSeriesResponse)
def save_mobile_training_series(
    athlete_id: str,
    session_id: str,
    payload: MobileTrainingSeriesInput,
) -> MobileTrainingSeriesResponse:
    session_row = ensure_mobile_session_row(athlete_id, session_id)
    supabase = ensure_supabase()
    now = datetime.now(timezone.utc).isoformat()
    numeric_scores = [normalize_shot_score(score) for score in payload.shots]
    row = {
        "score_id": str(uuid4()),
        "athlete_id": athlete_id,
        "score_type": "mobile_series",
        "score_value": round(sum(numeric_scores), 1),
        "percentile": None,
        "category": f"Series {payload.series_number}",
        "calculated_at": now,
        "source_data": {
            "sessionId": session_id,
            "seriesNumber": payload.series_number,
            "shots": payload.shots,
            "avgHeartRate": payload.avg_heart_rate,
        },
        "created_at": now,
        "updated_at": now,
    }
    try:
        supabase.table(APP_TABLES["athlete_scores"]).insert(row).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save series: {exception}") from exception

    return MobileTrainingSeriesResponse(
        series=serialize_mobile_series(row),
        summary=build_mobile_session_summary(session_row),
    )


@app.post("/api/mobile/athletes/{athlete_id}/sessions/{session_id}/reflection", response_model=MobileSessionReflectionResponse)
def save_mobile_session_reflection(
    athlete_id: str,
    session_id: str,
    payload: MobileSessionReflectionInput,
) -> MobileSessionReflectionResponse:
    session_row = ensure_mobile_session_row(athlete_id, session_id)
    seed_psychology_questions()
    supabase = ensure_supabase()
    now = datetime.now(timezone.utc).isoformat()
    reflection_payload = {
        "sessionId": session_id,
        "mood": payload.mood,
        "whatWorked": payload.what_worked,
        "whatDidnt": payload.what_didnt,
        "voiceNoteUrl": payload.voice_note_url,
        "selfRating": payload.self_rating,
        "fatigueLevel": payload.fatigue_level,
    }
    row = {
        "answer_id": str(uuid4()),
        "athlete_id": athlete_id,
        "question_id": "MOBILE_SESSION_REFLECTION",
        "answer_text": compact_json(reflection_payload),
        "answer_score": payload.self_rating,
        "recorded_at": now,
    }
    try:
        supabase.table(APP_TABLES["psychology_responses"]).insert(row).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save reflection: {exception}") from exception

    athlete_row = ensure_mobile_athlete_row(athlete_id)
    notify_coach_of_athlete_activity(
        athlete_row=athlete_row,
        title="Session reflection submitted",
        message=f"{athlete_row.get('name') or athlete_row.get('athlete_name') or 'Athlete'} submitted a session reflection.",
        notification_type="SESSION_REFLECTION",
        related_session_id=session_id,
        action_url=f"/coach/athletes/{athlete_id}",
    )
    return MobileSessionReflectionResponse(
        reflection=serialize_mobile_reflection(row) or {},
        summary=build_mobile_session_summary(session_row),
    )


@app.post("/api/mobile/athletes/{athlete_id}/sessions/{session_id}/complete", response_model=MobileSessionSummaryResponse)
def complete_mobile_training_session(
    athlete_id: str,
    session_id: str,
    payload: MobileSessionCompleteInput,
) -> MobileSessionSummaryResponse:
    supabase = ensure_supabase()
    session_row = ensure_mobile_session_row(athlete_id, session_id)
    now = datetime.now(timezone.utc)
    notes = parse_json_object(session_row.get("notes"))
    notes.update(
        {
            "status": "COMPLETED",
            "endedAt": now.isoformat(),
            "durationSeconds": payload.duration_seconds,
            "avgHeartRate": payload.avg_heart_rate,
            "peakHeartRate": payload.peak_heart_rate,
            "fatigue": payload.fatigue,
            "recovery": payload.recovery,
        }
    )
    update_row = {
        "end_time": now.strftime("%H:%M"),
        "duration_minutes": round((payload.duration_seconds or 0) / 60),
        "notes": compact_json(notes),
    }
    physiology_row = None
    if payload.avg_heart_rate:
        physiology_row = {
            "physiology_id": str(uuid4()),
            "athlete_id": athlete_id,
            "session_id": session_id,
            "recorded_date": now.date().isoformat(),
            "resting_heart_rate": round(payload.avg_heart_rate),
            "avg_heart_rate": round(payload.avg_heart_rate),
            "spo2": 98,
            "breathing_rate": 12,
            "sleep_hours": 0,
            "recovery_score": 50,
            "stress_score": 50,
            "fatigue_level": 5,
            "remarks": compact_json({"peakHeartRate": payload.peak_heart_rate, "fatigue": payload.fatigue, "recovery": payload.recovery}),
        }
    try:
        response = (
            supabase.table(APP_TABLES["shooting_session_log"])
            .update(update_row)
            .eq("athlete_id", athlete_id)
            .eq("session_id", session_id)
            .execute()
        )
        if physiology_row:
            supabase.table(APP_TABLES["athlete_physiology"]).insert(physiology_row).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to complete session: {exception}") from exception

    session_row = (response.data or [None])[0] or ensure_mobile_session_row(athlete_id, session_id)
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    notify_coach_of_athlete_activity(
        athlete_row=athlete_row,
        title="Training session completed",
        message=f"{athlete_row.get('name') or athlete_row.get('athlete_name') or 'Athlete'} completed a training session.",
        notification_type="TRAINING_SESSION_COMPLETED",
        related_session_id=session_id,
        action_url=f"/coach/athletes/{athlete_id}",
    )
    return MobileSessionSummaryResponse(summary=build_mobile_session_summary(session_row))


@app.get("/api/mobile/athletes/{athlete_id}/sessions/{session_id}/summary", response_model=MobileSessionSummaryResponse)
def get_mobile_training_session_summary(
    athlete_id: str,
    session_id: str,
) -> MobileSessionSummaryResponse:
    session_row = ensure_mobile_session_row(athlete_id, session_id)
    return MobileSessionSummaryResponse(summary=build_mobile_session_summary(session_row))


@app.post("/api/mobile/athletes/register", response_model=MobileAthleteRegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_mobile_athlete(payload: MobileAthleteRegistrationInput) -> MobileAthleteRegistrationResponse:
    ensure_seed_data()
    supabase = ensure_supabase()
    email = payload.email.lower()
    target_coach_id, target_coach_email = get_assignment_target_for_registration(payload)
    target_coach_user = get_user_by_email(target_coach_email) if target_coach_email else None
    target_coach_name = target_coach_user.full_name if target_coach_user else "HamsaTech Coach"

    user = get_user_by_email(email)
    if not user:
        user = upsert_user(
            create_user_record(
                email=email,
                full_name=payload.full_name,
                password=f"Mobile{uuid4().hex[:10]}!",
                role="student",
                assignment_status="pending",
                assigned_coach_email=None,
                assigned_coach_name=None,
                requested_coach_email=target_coach_email,
                requested_coach_name=target_coach_name,
                requested_coach_code=None,
                coach_request_sent_at=datetime.now(timezone.utc).isoformat(),
                sport=payload.sport,
                focus_area=payload.focus_area,
                performance_score=get_next_student_score(),
            )
        )
    athlete_id = payload.athlete_id or str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    athlete_row = {
        "athlete_id": athlete_id,
        "name": payload.full_name,
        "age": payload.age,
        "gender": payload.gender,
        "height_cm": 1,
        "weight_kg": 1,
        "academy_id": payload.sport or "Mobile",
        "coach_id": "",
        "contact_number": payload.phone,
        "email": email,
        "created_at": now,
        "updated_by": "mobile-app",
        "registration_source": "mobile_app",
        "onboarding_status": "registered",
        "profile_completion_status": payload.profile_completion_status,
        "updated_at": now,
    }
    try:
        supabase.table(APP_TABLES["athletes"]).upsert(athlete_row, on_conflict="athlete_id").execute()
    except Exception as exception:
        legacy_row = {
            key: athlete_row[key]
            for key in (
                "athlete_id",
                "name",
                "age",
                "gender",
                "height_cm",
                "weight_kg",
                "academy_id",
                "coach_id",
                "contact_number",
                "email",
                "created_at",
                "updated_by",
            )
        }
        try:
            supabase.table(APP_TABLES["athletes"]).upsert(legacy_row, on_conflict="athlete_id").execute()
            athlete_row = legacy_row
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save mobile registration: {exception}") from exception

    request_id = create_assignment_request_for_athlete(
        athlete_id=athlete_id,
        athlete_name=payload.full_name,
        target_coach_id=target_coach_id,
        target_coach_email=target_coach_email,
        notes="Auto-created from mobile athlete registration",
    )
    write_audit_log(
        actor_email=email,
        action="mobile_athlete_registered",
        entity_type="athlete",
        entity_id=athlete_id,
        metadata={"targetCoachId": target_coach_id, "targetCoachEmail": target_coach_email, "assignmentRequestId": request_id},
    )
    sync_latest_overall_score(athlete_row)
    return MobileAthleteRegistrationResponse(
        athleteId=athlete_id,
        assignedCoachEmail=target_coach_email,
        notificationCreated=bool(request_id),
        success=True,
    )


@app.get("/api/mobile/athletes/{athlete_id}/profile", response_model=MobileAthleteProfileResponse)
def get_mobile_athlete_profile(athlete_id: str) -> MobileAthleteProfileResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    profile_row = get_mobile_profile_row(athlete_id)
    return MobileAthleteProfileResponse(profile=serialize_mobile_profile(profile_row, athlete_row))


@app.put("/api/mobile/athletes/{athlete_id}/profile", response_model=MobileAthleteProfileResponse)
def upsert_mobile_athlete_profile(
    athlete_id: str,
    payload: MobileAthleteProfileUpsertInput,
) -> MobileAthleteProfileResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    existing_profile = get_mobile_profile_row(athlete_id) or {}
    performance = parse_json_object(existing_profile.get("academic_performance"))
    shooting = parse_json_object(existing_profile.get("reason_for_shooting"))
    goals = parse_json_object(existing_profile.get("athlete_goal"))
    athlete_update: dict[str, Any] = {"updated_by": "mobile-app"}

    if payload.performance_factors is not None and len(normalize_text_list(payload.performance_factors)) > 3:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Select up to 3 performance factors.")
    if payload.full_name is not None:
        athlete_update["name"] = payload.full_name
    if payload.age is not None:
        athlete_update["age"] = payload.age
    if payload.gender is not None:
        athlete_update["gender"] = payload.gender
    if payload.city is not None:
        shooting["city"] = payload.city
    if payload.discipline is not None:
        shooting["discipline"] = payload.discipline
        athlete_update["academy_id"] = payload.discipline
    if payload.experience_level is not None:
        performance["experienceLevel"] = payload.experience_level
    if payload.years_shooting is not None:
        performance["yearsShooting"] = payload.years_shooting
    if payload.academy_club is not None:
        shooting["academyClub"] = payload.academy_club
        if payload.academy_club.strip():
            athlete_update["academy_id"] = payload.academy_club
    if payload.average_practice_score is not None:
        performance["averagePracticeScore"] = payload.average_practice_score
    if payload.target_score is not None:
        performance["targetScore"] = payload.target_score
    if payload.performance_factors is not None:
        shooting["performanceFactors"] = normalize_text_list(payload.performance_factors)
    if payload.goal_30_days is not None:
        goals["goal30Days"] = payload.goal_30_days
    if payload.goal_6_months is not None:
        goals["goal6Months"] = payload.goal_6_months

    profile_status_data = {
        "full_name": athlete_update.get("name") or athlete_row.get("name") or athlete_row.get("athlete_name"),
        "age": athlete_update.get("age") or athlete_row.get("age"),
        "gender": athlete_update.get("gender") or athlete_row.get("gender"),
        "discipline": shooting.get("discipline") or athlete_update.get("academy_id") or athlete_row.get("academy_id"),
        "average_practice_score": performance.get("averagePracticeScore"),
        "target_score": performance.get("targetScore"),
        "goal_30_days": goals.get("goal30Days"),
        "goal_6_months": goals.get("goal6Months"),
    }
    baseline = get_mobile_baseline_row(athlete_id)
    onboarding_status, completion_status = compute_mobile_profile_status(
        profile_status_data,
        row_number((baseline or {}).get("resting_heart_rate"), fallback=None),  # type: ignore[arg-type]
    )
    athlete_update["onboarding_status"] = onboarding_status
    athlete_update["profile_completion_status"] = completion_status
    athlete_update["updated_at"] = datetime.now(timezone.utc).isoformat()

    profile_payload = {
        "details_id": existing_profile.get("details_id") or str(uuid4()),
        "athlete_id": athlete_id,
        "class": existing_profile.get("class") or "Mobile",
        "school_name": existing_profile.get("school_name") or shooting.get("city") or "Not provided",
        "diet_type": existing_profile.get("diet_type") or "Mixed",
        "outside_food_frequency": existing_profile.get("outside_food_frequency") or "Rare",
        "sleep_time": existing_profile.get("sleep_time") or "22:00",
        "wake_time": existing_profile.get("wake_time") or "06:00",
        "friend_circle": existing_profile.get("friend_circle") or "Not provided",
        "anger_pattern": existing_profile.get("anger_pattern") or "Not provided",
        "sadness_pattern": existing_profile.get("sadness_pattern") or "Not provided",
        "academic_performance": compact_json(performance),
        "reason_for_shooting": compact_json(shooting),
        "athlete_goal": compact_json(goals),
    }

    try:
        if existing_profile:
            supabase.table(APP_TABLES["athlete_details"]).update(profile_payload).eq("athlete_id", athlete_id).execute()
        else:
            supabase.table(APP_TABLES["athlete_details"]).insert(profile_payload).execute()
        try:
            supabase.table(APP_TABLES["athletes"]).update(athlete_update).eq("athlete_id", athlete_id).execute()
        except Exception:
            legacy_update = {
                key: value
                for key, value in athlete_update.items()
                if key not in {"onboarding_status", "profile_completion_status", "updated_at"}
            }
            if legacy_update:
                supabase.table(APP_TABLES["athletes"]).update(legacy_update).eq("athlete_id", athlete_id).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save athlete profile: {exception}") from exception

    write_audit_log(
        actor_email=str(athlete_row.get("email") or ""),
        action="mobile_athlete_profile_saved",
        entity_type="athlete",
        entity_id=athlete_id,
        metadata={"profileCompletionStatus": completion_status, "onboardingStatus": onboarding_status},
    )
    updated_athlete_row = ensure_mobile_athlete_row(athlete_id)
    return MobileAthleteProfileResponse(profile=serialize_mobile_profile(get_mobile_profile_row(athlete_id), updated_athlete_row))


@app.post("/api/mobile/athletes/{athlete_id}/baseline", response_model=MobileAthleteProfileResponse)
def save_mobile_athlete_baseline(
    athlete_id: str,
    payload: MobileBaselineInput,
) -> MobileAthleteProfileResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    now = datetime.now(timezone.utc)
    session_id = str(uuid4())
    session_row = {
        "session_id": session_id,
        "athlete_id": athlete_id,
        "coach_id": str(athlete_row.get("coach_id") or ""),
        "session_date": now.date().isoformat(),
        "start_time": now.strftime("%H:%M"),
        "end_time": now.strftime("%H:%M"),
        "duration_minutes": 0,
        "training_type": "Recovery",
        "location": "Polar baseline",
        "notes": compact_json({"source": "mobile_baseline", "polarLinked": payload.polar_linked}),
    }
    physiology_row = {
        "physiology_id": str(uuid4()),
        "athlete_id": athlete_id,
        "session_id": session_id,
        "recorded_date": now.date().isoformat(),
        "resting_heart_rate": payload.resting_hr_baseline,
        "avg_heart_rate": payload.resting_hr_baseline,
        "spo2": 98,
        "breathing_rate": 12,
        "sleep_hours": 0,
        "recovery_score": 50,
        "stress_score": 50,
        "fatigue_level": 0,
        "remarks": compact_json({"source": "mobile_baseline", "hrvBaselineMs": payload.hrv_baseline_ms}),
    }
    profile = serialize_mobile_profile(get_mobile_profile_row(athlete_id), athlete_row)
    onboarding_status = "ready_to_train" if profile.profile_completion_status == "complete" else profile.onboarding_status

    try:
        supabase.table(APP_TABLES["shooting_session_log"]).insert(session_row).execute()
        supabase.table(APP_TABLES["athlete_physiology"]).insert(physiology_row).execute()
        try:
            supabase.table(APP_TABLES["athletes"]).update(
                {
                    "onboarding_status": onboarding_status,
                    "profile_completion_status": profile.profile_completion_status,
                    "updated_at": now.isoformat(),
                    "updated_by": "mobile-app",
                }
            ).eq("athlete_id", athlete_id).execute()
        except Exception:
            supabase.table(APP_TABLES["athletes"]).update({"updated_by": "mobile-app"}).eq("athlete_id", athlete_id).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save baseline: {exception}") from exception

    write_audit_log(
        actor_email=str(athlete_row.get("email") or ""),
        action="mobile_athlete_baseline_saved",
        entity_type="athlete",
        entity_id=athlete_id,
        metadata={"restingHrBaseline": payload.resting_hr_baseline},
    )
    return MobileAthleteProfileResponse(profile=serialize_mobile_profile(get_mobile_profile_row(athlete_id), ensure_mobile_athlete_row(athlete_id)))


@app.post("/api/mobile/athletes/{athlete_id}/daily-checkins", response_model=MobileDailyCheckinResponse, status_code=status.HTTP_201_CREATED)
def save_mobile_daily_checkin(
    athlete_id: str,
    payload: MobileDailyCheckinInput,
) -> MobileDailyCheckinResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    seed_psychology_questions()
    supabase = ensure_supabase()
    now = datetime.now(timezone.utc).isoformat()
    checkin_payload = {
        "checkinDate": (payload.checkin_date or date.today()).isoformat(),
        "mood": payload.mood,
        "energyLevel": payload.energy_level,
        "sleepBand": payload.sleep_band,
        "sleepHours": payload.sleep_hours,
        "tags": normalize_text_list(payload.tags),
        "notes": payload.notes,
    }
    row = {
        "answer_id": str(uuid4()),
        "athlete_id": athlete_id,
        "question_id": "MOBILE_DAILY_CHECKIN",
        "answer_text": compact_json(checkin_payload),
        "answer_score": payload.energy_level,
        "recorded_at": now,
    }
    try:
        supabase.table(APP_TABLES["psychology_responses"]).insert(row).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save daily check-in: {exception}") from exception

    notify_coach_of_athlete_activity(
        athlete_row=athlete_row,
        title="Daily check-in submitted",
        message=f"{athlete_row.get('name') or athlete_row.get('athlete_name') or 'Athlete'} submitted a daily check-in.",
        notification_type="DAILY_CHECKIN",
        action_url=f"/coach/athletes/{athlete_id}",
    )
    return MobileDailyCheckinResponse(checkin=serialize_mobile_checkin(row))


@app.get("/api/mobile/athletes/{athlete_id}/daily-checkins/latest", response_model=MobileDailyCheckinResponse)
def get_mobile_latest_daily_checkin(athlete_id: str) -> MobileDailyCheckinResponse:
    ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["psychology_responses"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("question_id", "MOBILE_DAILY_CHECKIN")
        .order("recorded_at", desc=True)
        .limit(1)
        .execute()
    )
    row = (response.data or [None])[0]
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No check-in found.")
    return MobileDailyCheckinResponse(checkin=serialize_mobile_checkin(row))


@app.get("/api/mobile/athletes/{athlete_id}/home", response_model=MobileAthleteHomeResponse)
def get_mobile_athlete_home(athlete_id: str) -> MobileAthleteHomeResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    profile = serialize_mobile_profile(get_mobile_profile_row(athlete_id), athlete_row)
    checkin_rows = safe_table_rows(
        APP_TABLES["psychology_responses"],
        supabase.table(APP_TABLES["psychology_responses"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("question_id", "MOBILE_DAILY_CHECKIN")
        .order("recorded_at", desc=True)
        .limit(1),
    )
    latest_checkin = serialize_mobile_checkin(checkin_rows[0]) if checkin_rows else None
    session_rows = safe_table_rows(
        APP_TABLES["shooting_session_log"],
        supabase.table(APP_TABLES["shooting_session_log"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .order("session_date", desc=True)
        .limit(3),
    )
    feedback_rows = safe_table_rows(
        APP_TABLES["coach_feedback"],
        supabase.table(APP_TABLES["coach_feedback"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .order("created_at", desc=True)
        .limit(3),
    )
    readiness = calculate_readiness(profile, latest_checkin)
    sleep_hours = latest_checkin.sleep_hours if latest_checkin else None
    if sleep_hours is None and latest_checkin:
        sleep_hours = sleep_band_to_hours(latest_checkin.sleep_band)
    recommendations = ["Start today's check-in"] if not latest_checkin else ["Start training session"]
    if readiness < 60:
        recommendations.insert(0, "Complete a breathing cool-down before shooting")

    return MobileAthleteHomeResponse(
        home={
            "athleteId": athlete_id,
            "displayName": profile.full_name or athlete_row.get("name") or "Athlete",
            "profileCompletionStatus": profile.profile_completion_status,
            "onboardingStatus": profile.onboarding_status,
            "polar": {
                "linked": profile.polar_linked,
                "deviceId": profile.polar_device_id,
            },
            "metrics": {
                "readiness": readiness,
                "sleepHours": sleep_hours,
                "restingHr": profile.resting_hr_baseline,
                "hrvMs": profile.hrv_baseline_ms,
            },
            "dailyCheckin": latest_checkin.model_dump(by_alias=True) if latest_checkin else None,
            "recentSessions": [serialize_mobile_session(row) for row in session_rows],
            "coachFeedback": [
                {
                    "feedbackId": str(row.get("feedback_id") or ""),
                    "coachName": row.get("coach_name") or "Coach",
                    "note": row.get("note") or row.get("coach_observations") or "",
                    "recommendation": row.get("recommendation"),
                    "status": row.get("status"),
                    "createdAt": row.get("created_at"),
                }
                for row in feedback_rows
            ],
            "recommendations": recommendations,
        }
    )


@app.post("/api/mobile/athletes/{athlete_id}/sessions", response_model=MobileTrainingSessionResponse, status_code=status.HTTP_201_CREATED)
def create_mobile_training_session(
    athlete_id: str,
    payload: MobileTrainingSessionCreateInput,
) -> MobileTrainingSessionResponse:
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    session_id = str(uuid4())
    start_time = datetime.now(timezone.utc)
    notes = {
        "source": "mobile_training_session",
        "rangeType": payload.range_type,
        "sessionType": payload.session_type,
        "plannedShots": payload.planned_shots,
        "discipline": payload.discipline or athlete_row.get("academy_id"),
        "intention": payload.intention,
        "visualization": payload.visualization,
        "bodyScanCompleted": payload.body_scan_completed,
        "status": "LIVE" if payload.start_now else "SETUP",
    }
    row = {
        "session_id": session_id,
        "athlete_id": athlete_id,
        "coach_id": str(athlete_row.get("coach_id") or ""),
        "session_date": start_time.date().isoformat(),
        "start_time": start_time.strftime("%H:%M"),
        "end_time": start_time.strftime("%H:%M"),
        "duration_minutes": 0,
        "training_type": "Mental" if payload.session_type == "Dry Fire" else "Shooting",
        "location": payload.range_type,
        "notes": compact_json(notes),
    }
    try:
        supabase.table(APP_TABLES["shooting_session_log"]).insert(row).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to create training session: {exception}") from exception
    notify_coach_of_athlete_activity(
        athlete_row=athlete_row,
        title="Training session started",
        message=f"{athlete_row.get('name') or athlete_row.get('athlete_name') or 'Athlete'} started a training session.",
        notification_type="TRAINING_SESSION_STARTED",
        related_session_id=session_id,
        action_url=f"/coach/athletes/{athlete_id}",
    )
    return MobileTrainingSessionResponse(session=serialize_mobile_session(row))


@app.get("/api/mobile/athletes/{athlete_id}/sessions", response_model=MobileTrainingSessionsResponse)
def list_mobile_training_sessions(
    athlete_id: str,
    limit: int = Query(default=20, ge=1, le=100),
) -> MobileTrainingSessionsResponse:
    ensure_mobile_athlete_row(athlete_id)
    supabase = ensure_supabase()
    response = (
        supabase.table(APP_TABLES["shooting_session_log"])
        .select("*")
        .eq("athlete_id", athlete_id)
        .order("session_date", desc=True)
        .limit(limit)
        .execute()
    )
    return MobileTrainingSessionsResponse(sessions=[serialize_mobile_session(row) for row in response.data or []])


@app.post("/api/mobile/athletes/{athlete_id}/sessions/{session_id}/series", response_model=MobileTrainingSeriesResponse)
def save_mobile_training_series(
    athlete_id: str,
    session_id: str,
    payload: MobileTrainingSeriesInput,
) -> MobileTrainingSeriesResponse:
    session_row = ensure_mobile_session_row(athlete_id, session_id)
    supabase = ensure_supabase()
    now = datetime.now(timezone.utc).isoformat()
    numeric_scores = [normalize_shot_score(score) for score in payload.shots]
    row = {
        "score_id": str(uuid4()),
        "athlete_id": athlete_id,
        "score_type": "mobile_series",
        "score_value": round(sum(numeric_scores), 1),
        "percentile": None,
        "category": f"Series {payload.series_number}",
        "calculated_at": now,
        "source_data": {
            "sessionId": session_id,
            "seriesNumber": payload.series_number,
            "shots": payload.shots,
            "avgHeartRate": payload.avg_heart_rate,
        },
        "created_at": now,
        "updated_at": now,
    }
    try:
        supabase.table(APP_TABLES["athlete_scores"]).insert(row).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save series: {exception}") from exception

    return MobileTrainingSeriesResponse(
        series=serialize_mobile_series(row),
        summary=build_mobile_session_summary(session_row),
    )


@app.post("/api/mobile/athletes/{athlete_id}/sessions/{session_id}/reflection", response_model=MobileSessionReflectionResponse)
def save_mobile_session_reflection(
    athlete_id: str,
    session_id: str,
    payload: MobileSessionReflectionInput,
) -> MobileSessionReflectionResponse:
    session_row = ensure_mobile_session_row(athlete_id, session_id)
    seed_psychology_questions()
    supabase = ensure_supabase()
    now = datetime.now(timezone.utc).isoformat()
    reflection_payload = {
        "sessionId": session_id,
        "mood": payload.mood,
        "whatWorked": payload.what_worked,
        "whatDidnt": payload.what_didnt,
        "voiceNoteUrl": payload.voice_note_url,
        "selfRating": payload.self_rating,
        "fatigueLevel": payload.fatigue_level,
    }
    row = {
        "answer_id": str(uuid4()),
        "athlete_id": athlete_id,
        "question_id": "MOBILE_SESSION_REFLECTION",
        "answer_text": compact_json(reflection_payload),
        "answer_score": payload.self_rating,
        "recorded_at": now,
    }
    try:
        supabase.table(APP_TABLES["psychology_responses"]).insert(row).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to save reflection: {exception}") from exception

    athlete_row = ensure_mobile_athlete_row(athlete_id)
    notify_coach_of_athlete_activity(
        athlete_row=athlete_row,
        title="Session reflection submitted",
        message=f"{athlete_row.get('name') or athlete_row.get('athlete_name') or 'Athlete'} submitted a session reflection.",
        notification_type="SESSION_REFLECTION",
        related_session_id=session_id,
        action_url=f"/coach/athletes/{athlete_id}",
    )
    return MobileSessionReflectionResponse(
        reflection=serialize_mobile_reflection(row) or {},
        summary=build_mobile_session_summary(session_row),
    )


@app.post("/api/mobile/athletes/{athlete_id}/sessions/{session_id}/complete", response_model=MobileSessionSummaryResponse)
def complete_mobile_training_session(
    athlete_id: str,
    session_id: str,
    payload: MobileSessionCompleteInput,
) -> MobileSessionSummaryResponse:
    supabase = ensure_supabase()
    session_row = ensure_mobile_session_row(athlete_id, session_id)
    now = datetime.now(timezone.utc)
    notes = parse_json_object(session_row.get("notes"))
    notes.update(
        {
            "status": "COMPLETED",
            "endedAt": now.isoformat(),
            "durationSeconds": payload.duration_seconds,
            "avgHeartRate": payload.avg_heart_rate,
            "peakHeartRate": payload.peak_heart_rate,
            "fatigue": payload.fatigue,
            "recovery": payload.recovery,
        }
    )
    update_row = {
        "end_time": now.strftime("%H:%M"),
        "duration_minutes": round((payload.duration_seconds or 0) / 60),
        "notes": compact_json(notes),
    }
    physiology_row = None
    if payload.avg_heart_rate:
        physiology_row = {
            "physiology_id": str(uuid4()),
            "athlete_id": athlete_id,
            "session_id": session_id,
            "recorded_date": now.date().isoformat(),
            "resting_heart_rate": round(payload.avg_heart_rate),
            "avg_heart_rate": round(payload.avg_heart_rate),
            "spo2": 98,
            "breathing_rate": 12,
            "sleep_hours": 0,
            "recovery_score": 50,
            "stress_score": 50,
            "fatigue_level": 5,
            "remarks": compact_json({"peakHeartRate": payload.peak_heart_rate, "fatigue": payload.fatigue, "recovery": payload.recovery}),
        }
    try:
        response = (
            supabase.table(APP_TABLES["shooting_session_log"])
            .update(update_row)
            .eq("athlete_id", athlete_id)
            .eq("session_id", session_id)
            .execute()
        )
        if physiology_row:
            supabase.table(APP_TABLES["athlete_physiology"]).insert(physiology_row).execute()
    except Exception as exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to complete session: {exception}") from exception

    session_row = (response.data or [None])[0] or ensure_mobile_session_row(athlete_id, session_id)
    athlete_row = ensure_mobile_athlete_row(athlete_id)
    notify_coach_of_athlete_activity(
        athlete_row=athlete_row,
        title="Training session completed",
        message=f"{athlete_row.get('name') or athlete_row.get('athlete_name') or 'Athlete'} completed a training session.",
        notification_type="TRAINING_SESSION_COMPLETED",
        related_session_id=session_id,
        action_url=f"/coach/athletes/{athlete_id}",
    )
    return MobileSessionSummaryResponse(summary=build_mobile_session_summary(session_row))


@app.get("/api/mobile/athletes/{athlete_id}/sessions/{session_id}/summary", response_model=MobileSessionSummaryResponse)
def get_mobile_training_session_summary(
    athlete_id: str,
    session_id: str,
) -> MobileSessionSummaryResponse:
    session_row = ensure_mobile_session_row(athlete_id, session_id)
    return MobileSessionSummaryResponse(summary=build_mobile_session_summary(session_row))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response) -> AuthResponse:
    try:
        ensure_seed_data()
    except Exception as exception:
        logger.warning("Skipping login seed refresh because it failed: %s", exception)

    try:
        user = get_user_by_email(payload.email.lower())
    except HTTPException:
        raise
    except Exception as exception:
        logger.exception("Unable to load user during login")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable. Check Supabase configuration and schema.",
        ) from exception
    try:
        ensure_seed_data()
    except Exception as exception:
        logger.warning("Skipping login seed refresh because it failed: %s", exception)

    try:
        user = get_user_by_email(payload.email.lower())
    except HTTPException:
        raise
    except Exception as exception:
        logger.exception("Unable to load user during login")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable. Check Supabase configuration and schema.",
        ) from exception

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No account found for this email address.",
        )

    if not verify_password(payload.password, user.salt, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password. Please try again.",
        )

    try:
        session_token = create_persistent_session(user.email)
    except HTTPException:
        raise
    except Exception as exception:
        logger.exception("Unable to create session during login")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable. Check Supabase session table setup.",
        ) from exception
    try:
        session_token = create_persistent_session(user.email)
    except HTTPException:
        raise
    except Exception as exception:
        logger.exception("Unable to create session during login")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable. Check Supabase session table setup.",
        ) from exception

    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_token,
        httponly=True,
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
        max_age=60 * 60 * 8,
    )

    return AuthResponse(user=to_public_user(user))


@app.get("/api/auth/me", response_model=AuthResponse)
def current_user(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AuthResponse:
    user = get_user_from_session(session_token)
    return AuthResponse(user=to_public_user(user))


@app.get("/api/students", response_model=StudentsResponse)
def list_students(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> StudentsResponse:
    user = get_user_from_session(session_token)

    if user.role != "coach":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coaches can view assigned student profiles.",
        )

    students = [to_student_profile(record) for record in list_students_for_coach(user.email)]
    students.sort(key=lambda student: student.full_name)
    return StudentsResponse(students=students)


@app.get("/api/coach/assignment-requests", response_model=CoachAssignmentRequestsResponse)
def list_coach_assignment_requests(
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAssignmentRequestsResponse:
    coach_user = ensure_coach_user(session_token)
    requests = [to_assignment_request_record(item) for item in list_assignment_requests_for_coach(coach_user.email)]
    return CoachAssignmentRequestsResponse(requests=requests)


@app.post("/api/coach/assignment-requests/{student_email}/approve", response_model=StatusResponse)
def approve_coach_assignment_request(
    student_email: str,
    payload: CoachAssignmentApprovalInput,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> StatusResponse:
    coach_user = ensure_coach_user(session_token)
    approve_assignment_request_for_coach(coach_user, student_email, payload.coach_code)
    return StatusResponse(success=True)


@app.post("/api/intake/submit", response_model=AthleteIntakeResponse, status_code=status.HTTP_201_CREATED)
def submit_athlete_intake(
    payload: AthleteIntakeRequest,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> AthleteIntakeResponse:
    current_user = get_authenticated_user(session_token)
    assigned_coach = ensure_assigned_coach_for_student(current_user)
    seed_psychology_questions()

    supabase = ensure_supabase()
    athlete_id = str(uuid4())
    family_id = str(uuid4())
    details_id = str(uuid4())
    session_id = str(uuid4())
    physiology_id = str(uuid4())
    created_at = datetime.utcnow().isoformat()

    athlete_row = {
        "athlete_id": athlete_id,
        "name": current_user.full_name,
        "age": payload.athlete_master.age,
        "gender": payload.athlete_master.gender,
        "height_cm": payload.athlete_master.height_cm,
        "weight_kg": payload.athlete_master.weight_kg,
        "academy_id": payload.athlete_master.academy_id,
        "coach_id": assigned_coach.email,
        "contact_number": payload.athlete_master.contact_number,
        "email": current_user.email,
        "created_at": created_at,
        "updated_by": current_user.email,
    }

    family_row = {
        "family_id": family_id,
        "athlete_id": athlete_id,
        "mother_name": payload.family_details.mother_name,
        "father_name": payload.family_details.father_name,
        "mother_occupation": payload.family_details.mother_occupation,
        "father_occupation": payload.family_details.father_occupation,
        "education_level": payload.family_details.education_level,
        "sibling_details": payload.family_details.sibling_details,
        "family_conservative": payload.family_details.family_conservative,
        "discipline_level": payload.family_details.discipline_level,
        "health_conditions": payload.family_details.health_conditions,
        "father_contact_number": payload.family_details.father_contact_number,
        "mother_contact_number": payload.family_details.mother_contact_number,
        "parent_email": payload.family_details.parent_email,
        "comments": payload.family_details.comments,
    }

    profile_row = {
        "details_id": details_id,
        "athlete_id": athlete_id,
        "class": payload.athlete_profile.athlete_class,
        "school_name": payload.athlete_profile.school_name,
        "diet_type": payload.athlete_profile.diet_type,
        "outside_food_frequency": payload.athlete_profile.outside_food_frequency,
        "sleep_time": payload.athlete_profile.sleep_time,
        "wake_time": payload.athlete_profile.wake_time,
        "friend_circle": payload.athlete_profile.friend_circle,
        "anger_pattern": payload.athlete_profile.anger_pattern,
        "sadness_pattern": payload.athlete_profile.sadness_pattern,
        "academic_performance": payload.athlete_profile.academic_performance,
        "reason_for_shooting": payload.athlete_profile.reason_for_shooting,
        "athlete_goal": payload.athlete_profile.athlete_goal,
    }

    session_row = {
        "session_id": session_id,
        "athlete_id": athlete_id,
        "coach_id": assigned_coach.email,
        "session_date": payload.sessions_log.session_date.isoformat(),
        "start_time": payload.sessions_log.start_time,
        "end_time": payload.sessions_log.end_time,
        "duration_minutes": payload.sessions_log.duration_minutes,
        "training_type": payload.sessions_log.training_type,
        "location": payload.sessions_log.location,
        "notes": payload.sessions_log.notes,
    }

    physiology_row = {
        "physiology_id": physiology_id,
        "athlete_id": athlete_id,
        "session_id": session_id,
        "recorded_date": payload.physiology_data.recorded_date.isoformat(),
        "resting_heart_rate": payload.physiology_data.resting_heart_rate,
        "avg_heart_rate": payload.physiology_data.avg_heart_rate,
        "spo2": payload.physiology_data.spo2,
        "breathing_rate": payload.physiology_data.breathing_rate,
        "sleep_hours": payload.physiology_data.sleep_hours,
        "recovery_score": payload.physiology_data.recovery_score,
        "stress_score": payload.physiology_data.stress_score,
        "fatigue_level": payload.physiology_data.fatigue_level,
        "remarks": payload.physiology_data.remarks,
    }

    psychology_rows = [
        {
            "answer_id": str(uuid4()),
            "athlete_id": athlete_id,
            "question_id": answer.question_id,
            "answer_text": answer.answer_text,
            "answer_score": answer.answer_score,
            "recorded_at": created_at,
        }
        for answer in payload.psychology_responses
    ]

    lookup_row = {
        "athlete_id": athlete_id,
        "name": current_user.full_name,
    }

    try:
        supabase.table(APP_TABLES["athletes"]).insert(athlete_row).execute()
        supabase.table(APP_TABLES["athlete_family"]).insert(family_row).execute()
        supabase.table(APP_TABLES["athlete_details"]).insert(profile_row).execute()
        supabase.table(APP_TABLES["shooting_session_log"]).insert(session_row).execute()
        supabase.table(APP_TABLES["athlete_physiology"]).insert(physiology_row).execute()
        supabase.table(APP_TABLES["psychology_responses"]).insert(psychology_rows).execute()
        supabase.table(APP_TABLES["athletes"]).insert(athlete_row).execute()
        supabase.table(APP_TABLES["athlete_family"]).insert(family_row).execute()
        supabase.table(APP_TABLES["athlete_details"]).insert(profile_row).execute()
        supabase.table(APP_TABLES["shooting_session_log"]).insert(session_row).execute()
        supabase.table(APP_TABLES["athlete_physiology"]).insert(physiology_row).execute()
        supabase.table(APP_TABLES["psychology_responses"]).insert(psychology_rows).execute()
        supabase.table("Athlete_Lookup").upsert(lookup_row, on_conflict="athlete_id").execute()
        sync_latest_overall_score(athlete_row)
        create_notification(
            recipient_email=assigned_coach.email,
            recipient_role="coach",
            title="New intake submitted",
            message=f"{current_user.full_name} submitted a new athlete intake.",
            notification_type="intake_submitted",
            entity_id=athlete_id,
        )
        write_audit_log(
            actor_email=current_user.email,
            action="athlete_intake_submitted",
            entity_type="athlete",
            entity_id=athlete_id,
            metadata={"coachEmail": assigned_coach.email},
        )
        sync_latest_overall_score(athlete_row)
        create_notification(
            recipient_email=assigned_coach.email,
            recipient_role="coach",
            title="New intake submitted",
            message=f"{current_user.full_name} submitted a new athlete intake.",
            notification_type="intake_submitted",
            entity_id=athlete_id,
        )
        write_audit_log(
            actor_email=current_user.email,
            action="athlete_intake_submitted",
            entity_type="athlete",
            entity_id=athlete_id,
            metadata={"coachEmail": assigned_coach.email},
        )
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supabase insert failed: {exception}",
        ) from exception

    return AthleteIntakeResponse(athleteId=athlete_id, sessionId=session_id, success=True)


@app.post("/api/auth/logout", response_model=StatusResponse)
def logout(
    response: Response,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> StatusResponse:
    if session_token:
        delete_persistent_session(session_token)

    clear_session_cookie(response)
    return StatusResponse(success=True)


# ---------------------------------------------------------------------------
# Phone OTP helpers
# ---------------------------------------------------------------------------

def _normalize_phone(phone: str) -> str:
    """Return a consistently formatted phone string.

    Preserves a leading '+' for E.164 numbers; otherwise strips all
    non-digit characters and returns digits only.
    """
    stripped = phone.strip()
    digits = re.sub(r"\D", "", stripped)
    return ("+" + digits) if stripped.startswith("+") else digits


def _phone_digits_tail(phone: str) -> str:
    """Return the last 10 digits of a phone number for fuzzy matching.

    Handles common variants: '+91XXXXXXXXXX', '91XXXXXXXXXX', '0XXXXXXXXXX',
    and bare 10-digit Indian numbers.  For numbers shorter than 10 digits
    (e.g. landlines in tests) the full digit string is returned.
    """
    digits = re.sub(r"\D", "", phone)
    return digits[-10:] if len(digits) >= 10 else digits


# ---------------------------------------------------------------------------
# POST /api/v1/auth/phone/send-otp
# ---------------------------------------------------------------------------

@app.post("/api/v1/auth/phone/send-otp", response_model=PhoneOtpSendResponse)
def send_phone_otp(payload: PhoneOtpSendRequest) -> PhoneOtpSendResponse:
    phone = _normalize_phone(payload.phone)
    if len(re.sub(r"\D", "", phone)) < 7:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Phone number must contain at least 7 digits.",
        )

    otp = f"{secrets.randbelow(1_000_000):06d}"
    salt = generate_salt()
    otp_hash = hash_password(otp, salt)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(minutes=10)).isoformat()

    supabase = ensure_supabase()
    try:
        supabase.table("phone_otp").upsert(
            {
                "phone": phone,
                "otp_hash": otp_hash,
                "otp_salt": salt,
                "expires_at": expires_at,
                "attempts": 0,
                "created_at": now.isoformat(),
            },
            on_conflict="phone",
        ).execute()
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate OTP. Ensure the phone_otp table exists in Supabase (see docs).",
        ) from exception

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token  = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from = os.getenv("TWILIO_PHONE_NUMBER")
    if not account_sid or not auth_token or not twilio_from:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Twilio is not configured. "
                "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER."
            ),
        )

    # E.164: bare 10-digit → +91XXXXXXXXXX; already-prefixed pass through unchanged.
    digits     = re.sub(r"\D", "", phone)
    e164_phone = phone if phone.startswith("+") else (
        f"+91{digits}" if len(digits) == 10 else f"+{digits}"
    )

    try:
        twilio_client = TwilioClient(account_sid, auth_token)
        message = twilio_client.messages.create(
            body=f"Your Hamsa OTP is {otp}. Valid for 10 minutes. Do not share.",
            from_=twilio_from,
            to=e164_phone,
        )
        logger.info("Twilio SMS sent: sid=%s to=%s", message.sid, e164_phone)
    except Exception as twilio_err:
        logger.error("Twilio send failed for %s: %s", e164_phone, twilio_err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again.",
        ) from twilio_err

    masked = "*" * max(0, len(phone) - 4) + phone[-4:]
    return PhoneOtpSendResponse(
        success=True,
        message=f"OTP sent to {masked}",
    )


# ---------------------------------------------------------------------------
# POST /api/v1/auth/phone/verify-otp
# ---------------------------------------------------------------------------

@app.post("/api/v1/auth/phone/verify-otp", response_model=PhoneOtpVerifyResponse)
def verify_phone_otp(payload: PhoneOtpVerifyRequest) -> PhoneOtpVerifyResponse:
    phone = _normalize_phone(payload.phone)
    supabase = ensure_supabase()

    rows = safe_table_rows(
        "phone_otp",
        supabase.table("phone_otp").select("*").eq("phone", phone).limit(1),
    )
    otp_row = rows[0] if rows else None
    if not otp_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No OTP found for this phone number. Request a new OTP first.",
        )

    expires_at = datetime.fromisoformat(str(otp_row["expires_at"]).replace("Z", "+00:00"))
    if expires_at < datetime.now(timezone.utc):
        try:
            supabase.table("phone_otp").delete().eq("phone", phone).execute()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Request a new one.",
        )

    attempts = int(otp_row.get("attempts") or 0)
    if attempts >= 3:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many incorrect attempts. Request a new OTP.",
        )

    if not verify_password(payload.otp, otp_row["otp_salt"], otp_row["otp_hash"]):
        try:
            supabase.table("phone_otp").update({"attempts": attempts + 1}).eq("phone", phone).execute()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect OTP. Please try again.",
        )

    # OTP correct — delete immediately so it cannot be reused.
    try:
        supabase.table("phone_otp").delete().eq("phone", phone).execute()
    except Exception:
        pass

    # Locate the athlete by phone.  Use digit-tail comparison to handle
    # the many phone formats in use (+91, 91, 0-prefix, bare 10-digit).
    phone_tail = _phone_digits_tail(phone)
    athlete_rows = safe_table_rows(
        APP_TABLES["athletes"],
        supabase.table(APP_TABLES["athletes"]).select("athlete_id,contact_number"),
    )
    athlete_row = next(
        (
            row for row in athlete_rows
            if row.get("contact_number")
            and _phone_digits_tail(str(row["contact_number"])) == phone_tail
        ),
        None,
    )
    if not athlete_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No athlete account found for this phone number. Please register first.",
        )

    logger.info("[DEV OTP] verified phone=%s → athleteId=%s", phone, athlete_row["athlete_id"])
    return PhoneOtpVerifyResponse(athleteId=str(athlete_row["athlete_id"]), success=True)
