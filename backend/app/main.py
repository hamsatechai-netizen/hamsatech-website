from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4
from typing import Annotated, Any
from typing import Literal

from fastapi import Cookie, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field

from .config import settings
from .security import (
    UserRecord,
    generate_salt,
    generate_session_token,
    hash_password,
    verify_password,
)
from .supabase_client import get_supabase_admin_client


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
    age: int
    gender: Literal["Male", "Female", "Other"]
    academy_id: str = Field(alias="academyId")
    coach_id: str = Field(alias="coachId")
    email: EmailStr
    contact_number: str = Field(alias="contactNumber")
    created_at: str = Field(alias="createdAt")


class CoachAthleteListResponse(BaseModel):
    athletes: list[CoachAthleteListItem]


class CoachAthleteDetailResponse(BaseModel):
    athlete: dict[str, Any]


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
    athlete_email: EmailStr = Field(alias="athleteEmail")
    coach_email: EmailStr = Field(alias="coachEmail")
    coach_name: str = Field(alias="coachName")
    note: str
    recommendation: str
    status: Literal["Needs Attention", "Progressing", "Strong"]
    created_at: str = Field(alias="createdAt")


class CoachFeedbackResponse(BaseModel):
    feedback: CoachFeedbackRecord


class CoachFeedbackListResponse(BaseModel):
    feedback: list[CoachFeedbackRecord]


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


DEFAULT_DEMO_USERS = [
    create_user_record(
        email=settings.default_email.lower(),
        full_name=settings.default_full_name,
        password=settings.default_password,
        role="coach",
        coach_code=settings.default_coach_code,
    ),
    create_user_record(
        email="ava.student@hamsatech.ai",
        full_name="Ava Martinez",
        password="Student2026!",
        role="student",
        assigned_coach_email=settings.default_email.lower(),
        assigned_coach_name=settings.default_full_name,
        sport="Tennis",
        focus_area="Footwork and recovery",
        date_of_birth="2008-04-14",
        performance_score=91,
    ),
    create_user_record(
        email="leo.student@hamsatech.ai",
        full_name="Leo Jackson",
        password="Student2026!",
        role="student",
        assigned_coach_email=settings.default_email.lower(),
        assigned_coach_name=settings.default_full_name,
        sport="Swimming",
        focus_area="Endurance pacing",
        date_of_birth="2006-09-02",
        performance_score=88,
    ),
    create_user_record(
        email="maya.student@hamsatech.ai",
        full_name="Maya Chen",
        password="Student2026!",
        role="student",
        assigned_coach_email=settings.default_email.lower(),
        assigned_coach_name=settings.default_full_name,
        sport="Basketball",
        focus_area="Vertical leap and mobility",
        date_of_birth="2007-01-27",
        performance_score=94,
    ),
]


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
    rows = [to_user_row(user) for user in DEFAULT_DEMO_USERS]
    supabase.table("App_Users").upsert(rows, on_conflict="email").execute()


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
        "name": row["name"],
        "age": row["age"],
        "gender": row["gender"],
        "heightCm": row["height_cm"],
        "weightKg": row["weight_kg"],
        "academyId": row["academy_id"],
        "coachId": row["coach_id"],
        "contactNumber": row["contact_number"],
        "email": row["email"],
        "createdAt": row["created_at"],
        "updatedBy": row.get("updated_by"),
    }


def serialize_family_details(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        "motherName": row["mother_name"],
        "fatherName": row["father_name"],
        "motherOccupation": row["mother_occupation"],
        "fatherOccupation": row["father_occupation"],
        "educationLevel": row["education_level"],
        "siblingDetails": row["sibling_details"],
        "familyConservative": row["family_conservative"],
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


def seed_psychology_questions() -> None:
    try:
        supabase = get_supabase_admin_client()
        supabase.table("Psychology_Questions").upsert(
            DEFAULT_PSYCHOLOGY_QUESTIONS,
            on_conflict="question_id",
        ).execute()
    except HTTPException:
        # Keep intake usable even before Supabase is configured.
        return


@app.on_event("startup")
def seed_application_data() -> None:
    try:
        ensure_seed_data()
        seed_psychology_questions()
    except HTTPException:
        # Allow the API to boot even before local env vars are configured.
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


@app.get("/api/coach/athletes", response_model=CoachAthleteListResponse)
def list_coach_athletes(
    search: str = Query(default="", max_length=100),
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteListResponse:
    coach_user = ensure_coach_user(session_token)
    supabase = ensure_supabase()

    query = supabase.table("Athletes_Master").select(
        "athlete_id,name,age,gender,academy_id,coach_id,email,contact_number,created_at"
    ).eq("coach_id", coach_user.email)
    if search.strip():
        query = query.ilike("name", f"%{search.strip()}%")

    try:
        response = query.order("name").execute()
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load athletes: {exception}",
        ) from exception

    athletes = [
        CoachAthleteListItem(
            athleteId=row["athlete_id"],
            name=row["name"],
            age=row["age"],
            gender=row["gender"],
            academyId=row["academy_id"],
            coachId=row["coach_id"],
            email=row["email"],
            contactNumber=row["contact_number"],
            createdAt=row["created_at"],
        )
        for row in response.data or []
    ]
    return CoachAthleteListResponse(athletes=athletes)


@app.get("/api/coach/athletes/{athlete_id}", response_model=CoachAthleteDetailResponse)
def get_coach_athlete_detail(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachAthleteDetailResponse:
    coach_user = ensure_coach_user(session_token)
    supabase = ensure_supabase()

    try:
        athlete_result = (
            supabase.table("Athletes_Master")
            .select("*")
            .eq("athlete_id", athlete_id)
            .limit(1)
            .execute()
        )
        athlete_row = (athlete_result.data or [None])[0]
        if not athlete_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
        if athlete_row["coach_id"].lower() != coach_user.email.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This athlete is not assigned to your coach account.",
            )

        family_result = (
            supabase.table("Family_Details").select("*").eq("athlete_id", athlete_id).limit(1).execute()
        )
        profile_result = (
            supabase.table("Athlete_Profile").select("*").eq("athlete_id", athlete_id).limit(1).execute()
        )
        session_result = (
            supabase.table("Sessions_Log").select("*").eq("athlete_id", athlete_id).order("session_date", desc=True).execute()
        )
        physiology_result = (
            supabase.table("Physiology_Data").select("*").eq("athlete_id", athlete_id).order("recorded_date", desc=True).execute()
        )
        psychology_result = (
            supabase.table("Psychology_Responses")
            .select("answer_id,question_id,answer_text,answer_score,recorded_at,Psychology_Questions(question_text,category,question_type)")
            .eq("athlete_id", athlete_id)
            .order("recorded_at", desc=True)
            .execute()
        )
    except HTTPException:
        raise
    except Exception as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to load athlete details: {exception}",
        ) from exception

    athlete = {
        "athleteMaster": serialize_athlete_master(athlete_row),
        "familyDetails": serialize_family_details((family_result.data or [None])[0]),
        "athleteProfile": serialize_athlete_profile((profile_result.data or [None])[0]),
        "sessionsLog": [
            {
                "sessionId": row["session_id"],
                "coachId": row["coach_id"],
                "sessionDate": row["session_date"],
                "startTime": row["start_time"],
                "endTime": row["end_time"],
                "durationMinutes": row["duration_minutes"],
                "trainingType": row["training_type"],
                "location": row["location"],
                "notes": row["notes"],
            }
            for row in session_result.data or []
        ],
        "physiologyData": [
            {
                "physiologyId": row["physiology_id"],
                "sessionId": row["session_id"],
                "recordedDate": row["recorded_date"],
                "restingHeartRate": row["resting_heart_rate"],
                "avgHeartRate": row["avg_heart_rate"],
                "spo2": row["spo2"],
                "breathingRate": row["breathing_rate"],
                "sleepHours": row["sleep_hours"],
                "recoveryScore": row["recovery_score"],
                "stressScore": row["stress_score"],
                "fatigueLevel": row["fatigue_level"],
                "remarks": row["remarks"],
            }
            for row in physiology_result.data or []
        ],
        "psychologyResponses": [
            {
                "answerId": row["answer_id"],
                "questionId": row["question_id"],
                "questionText": (
                    row.get("Psychology_Questions")[0].get("question_text", "")
                    if isinstance(row.get("Psychology_Questions"), list) and row.get("Psychology_Questions")
                    else (row.get("Psychology_Questions") or {}).get("question_text", "")
                ),
                "category": (
                    row.get("Psychology_Questions")[0].get("category", "")
                    if isinstance(row.get("Psychology_Questions"), list) and row.get("Psychology_Questions")
                    else (row.get("Psychology_Questions") or {}).get("category", "")
                ),
                "questionType": (
                    row.get("Psychology_Questions")[0].get("question_type", "")
                    if isinstance(row.get("Psychology_Questions"), list) and row.get("Psychology_Questions")
                    else (row.get("Psychology_Questions") or {}).get("question_type", "")
                ),
                "answerText": row["answer_text"],
                "answerScore": row.get("answer_score"),
                "recordedAt": row["recorded_at"],
            }
            for row in psychology_result.data or []
        ],
    }
    return CoachAthleteDetailResponse(athlete=athlete)


@app.get("/api/coach/athletes/{athlete_id}/feedback", response_model=CoachFeedbackListResponse)
def list_coach_athlete_feedback(
    athlete_id: str,
    session_token: Annotated[str | None, Cookie(alias=settings.session_cookie_name)] = None,
) -> CoachFeedbackListResponse:
    coach_user = ensure_coach_user(session_token)
    supabase = ensure_supabase()
    response = (
        supabase.table("Coach_Feedback")
        .select("*")
        .eq("athlete_id", athlete_id)
        .eq("coach_email", coach_user.email.lower())
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
    supabase = ensure_supabase()

    athlete_result = (
        supabase.table("Athletes_Master")
        .select("athlete_id,name,email,coach_id")
        .eq("athlete_id", athlete_id)
        .limit(1)
        .execute()
    )
    athlete_row = (athlete_result.data or [None])[0]
    if not athlete_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found.")
    if athlete_row["coach_id"].lower() != coach_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only leave feedback for athletes assigned to you.",
        )

    feedback_item = {
        "feedback_id": str(uuid4()),
        "athlete_id": athlete_row["athlete_id"],
        "athlete_name": athlete_row["name"],
        "athlete_email": athlete_row["email"],
        "coach_email": coach_user.email,
        "coach_name": coach_user.full_name,
        "note": payload.note,
        "recommendation": payload.recommendation,
        "status": payload.status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table("Coach_Feedback").insert(feedback_item).execute()
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
        supabase.table("Coach_Feedback")
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

    user = create_user_record(
        email=email,
        full_name=payload.full_name,
        password=payload.password,
        role="student",
        assignment_status="unassigned",
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


@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response) -> AuthResponse:
    ensure_seed_data()
    user = get_user_by_email(payload.email.lower())

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

    session_token = create_persistent_session(user.email)

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
        supabase.table("Athletes_Master").insert(athlete_row).execute()
        supabase.table("Family_Details").insert(family_row).execute()
        supabase.table("Athlete_Profile").insert(profile_row).execute()
        supabase.table("Sessions_Log").insert(session_row).execute()
        supabase.table("Physiology_Data").insert(physiology_row).execute()
        supabase.table("Psychology_Responses").insert(psychology_rows).execute()
        supabase.table("Athlete_Lookup").upsert(lookup_row, on_conflict="athlete_id").execute()
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
