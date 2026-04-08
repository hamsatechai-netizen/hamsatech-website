export type AuthUser = {
  email: string
  fullName: string
  role: 'coach' | 'student'
  coachCode?: string | null
  assignmentStatus?: 'unassigned' | 'pending' | 'assigned'
  assignedCoachCode?: string | null
  assignedCoachEmail?: string | null
  assignedCoachName?: string | null
  requestedCoachCode?: string | null
  requestedCoachEmail?: string | null
  requestedCoachName?: string | null
  sport?: string | null
  focusArea?: string | null
  dateOfBirth?: string | null
  performanceScore?: number | null
}

export type StudentProfile = {
  email: string
  fullName: string
  assignedCoachEmail?: string | null
  assignedCoachName?: string | null
  sport: string
  focusArea: string
  dateOfBirth: string
  performanceScore: number
}

export type CoachFeedbackRecord = {
  feedbackId: string
  athleteId: string
  athleteName: string
  athleteEmail: string
  coachEmail: string
  coachName: string
  note: string
  recommendation: string
  status: 'Needs Attention' | 'Progressing' | 'Strong'
  createdAt: string
}

export type CoachAssignmentRequest = {
  email: string
  fullName: string
  sport: string
  focusArea: string
  requestedCoachCode: string
  requestedCoachName: string
  requestedAt?: string | null
  assignmentStatus: 'pending'
}

export type CoachAthleteListItem = {
  athleteId: string
  name: string
  age: number
  gender: 'Male' | 'Female' | 'Other'
  academyId: string
  coachId: string
  email: string
  contactNumber: string
  createdAt: string
}

export type CoachAthleteDetail = {
  athleteMaster: {
    athleteId: string
    name: string
    age: number
    gender: 'Male' | 'Female' | 'Other'
    heightCm: number
    weightKg: number
    academyId: string
    coachId: string
    contactNumber: string
    email: string
    createdAt: string
    updatedBy?: string | null
  }
  familyDetails: {
    motherName: string
    fatherName: string
    motherOccupation: string
    fatherOccupation: string
    educationLevel: string
    siblingDetails: string
    familyConservative: 'Yes' | 'No'
    disciplineLevel: string
    healthConditions: string
    fatherContactNumber: string
    motherContactNumber: string
    parentEmail: string
    comments: string
  } | null
  athleteProfile: {
    class: string
    schoolName: string
    dietType: 'Veg' | 'Non-Veg' | 'Mixed'
    outsideFoodFrequency: 'Rare' | 'Weekly' | 'Frequent'
    sleepTime: string
    wakeTime: string
    friendCircle: string
    angerPattern: string
    sadnessPattern: string
    academicPerformance: string
    reasonForShooting: string
    athleteGoal: string
  } | null
  sessionsLog: Array<{
    sessionId: string
    coachId: string
    sessionDate: string
    startTime: string
    endTime: string
    durationMinutes: number
    trainingType: 'Shooting' | 'Fitness' | 'Mental' | 'Recovery'
    location: string
    notes: string
  }>
  physiologyData: Array<{
    physiologyId: string
    sessionId: string
    recordedDate: string
    restingHeartRate: number
    avgHeartRate: number
    spo2: number
    breathingRate: number
    sleepHours: number
    recoveryScore: number
    stressScore: number
    fatigueLevel: number
    remarks: string
  }>
  psychologyResponses: Array<{
    answerId: string
    questionId: string
    questionText: string
    category: string
    questionType: string
    answerText: string
    answerScore?: number | null
    recordedAt: string
  }>
}

export type PsychologyQuestion = {
  questionId: string
  questionText: string
  category: string
  questionType: string
}

export type AthleteIntakePayload = {
  athleteMaster: {
    name: string
    age: number
    gender: 'Male' | 'Female' | 'Other'
    heightCm: number
    weightKg: number
    academyId: string
    coachId: string
    contactNumber: string
    email: string
  }
  familyDetails: {
    motherName: string
    fatherName: string
    motherOccupation: string
    fatherOccupation: string
    educationLevel: string
    siblingDetails: string
    familyConservative: 'Yes' | 'No'
    disciplineLevel: string
    healthConditions: string
    fatherContactNumber: string
    motherContactNumber: string
    parentEmail: string
    comments: string
  }
  athleteProfile: {
    class: string
    schoolName: string
    dietType: 'Veg' | 'Non-Veg' | 'Mixed'
    outsideFoodFrequency: 'Rare' | 'Weekly' | 'Frequent'
    sleepTime: string
    wakeTime: string
    friendCircle: string
    angerPattern: string
    sadnessPattern: string
    academicPerformance: string
    reasonForShooting: string
    athleteGoal: string
  }
  sessionsLog: {
    coachId: string
    sessionDate: string
    startTime: string
    endTime: string
    trainingType: 'Shooting' | 'Fitness' | 'Mental' | 'Recovery'
    location: string
    notes: string
  }
  physiologyData: {
    recordedDate: string
    restingHeartRate: number
    avgHeartRate: number
    spo2: number
    breathingRate: number
    sleepHours: number
    recoveryScore: number
    stressScore: number
    fatigueLevel: number
    remarks: string
  }
  psychologyResponses: Array<{
    questionId: string
    answerText: string
    answerScore?: number
  }>
}

type LoginPayload = {
  email: string
  password: string
}

type SignUpPayload = {
  fullName: string
  email: string
  password: string
  role: 'student'
  sport?: string
  focusArea?: string
  dateOfBirth?: string
}

type AuthResponse = {
  user: AuthUser
}

type StudentsResponse = {
  students: StudentProfile[]
}

type CoachAthleteListResponse = {
  athletes: CoachAthleteListItem[]
}

type CoachAthleteDetailResponse = {
  athlete: CoachAthleteDetail
}

type CoachFeedbackListResponse = {
  feedback: CoachFeedbackRecord[]
}

type CoachFeedbackResponse = {
  feedback: CoachFeedbackRecord
}

type CoachAssignmentRequestsResponse = {
  requests: CoachAssignmentRequest[]
}

type PsychologyQuestionsResponse = {
  questions: PsychologyQuestion[]
}

type AthleteIntakeResponse = {
  athleteId: string
  sessionId: string
  success: boolean
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

type ErrorResponse = {
  detail?: string | Array<{ msg?: string; loc?: Array<string | number> }>
}

function getErrorMessage(data: ErrorResponse, fallback: string) {
  if (typeof data.detail === 'string' && data.detail.trim()) {
    return data.detail
  }

  if (Array.isArray(data.detail) && data.detail.length > 0) {
    return data.detail
      .map((item) => {
        const location = item.loc?.slice(1).join(' > ')
        return location ? `${location}: ${item.msg ?? fallback}` : item.msg ?? fallback
      })
      .join(' | ')
  }

  return fallback
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    let message = 'Request failed'

    try {
      const data = (await response.json()) as ErrorResponse
      message = getErrorMessage(data, message)
    } catch {
      message = response.statusText || message
    }

    throw new Error(message)
  }

  return (await response.json()) as T
}

export async function signIn(payload: LoginPayload): Promise<AuthUser> {
  const data = await request<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

  return data.user
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    credentials: 'include',
  })

  if (response.status === 401) {
    return null
  }

  if (!response.ok) {
    throw new Error('Unable to load current user')
  }

  const data = (await response.json()) as AuthResponse
  return data.user
}

export async function signUp(payload: SignUpPayload): Promise<AuthUser> {
  const data = await request<AuthResponse>('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

  return data.user
}

export async function requestCoachAssignment(): Promise<AuthUser> {
  const data = await request<AuthResponse>('/api/student/coach-request', {
    method: 'POST',
  })

  return data.user
}

export async function getStudents(): Promise<StudentProfile[]> {
  const data = await request<StudentsResponse>('/api/students', {
    method: 'GET',
  })

  return data.students
}

export async function getCoachAthletes(search = ''): Promise<CoachAthleteListItem[]> {
  const query = search.trim() ? `?search=${encodeURIComponent(search.trim())}` : ''
  const data = await request<CoachAthleteListResponse>(`/api/coach/athletes${query}`, {
    method: 'GET',
  })

  return data.athletes
}

export async function getCoachAthleteDetails(athleteId: string): Promise<CoachAthleteDetail> {
  const data = await request<CoachAthleteDetailResponse>(`/api/coach/athletes/${encodeURIComponent(athleteId)}`, {
    method: 'GET',
  })

  return data.athlete
}

export async function getCoachAthleteFeedback(athleteId: string): Promise<CoachFeedbackRecord[]> {
  const data = await request<CoachFeedbackListResponse>(
    `/api/coach/athletes/${encodeURIComponent(athleteId)}/feedback`,
    {
      method: 'GET',
    },
  )

  return data.feedback
}

export async function createCoachAthleteFeedback(
  athleteId: string,
  payload: {
    note: string
    recommendation: string
    status: 'Needs Attention' | 'Progressing' | 'Strong'
  },
): Promise<CoachFeedbackRecord> {
  const data = await request<CoachFeedbackResponse>(
    `/api/coach/athletes/${encodeURIComponent(athleteId)}/feedback`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  )

  return data.feedback
}

export async function getCoachAssignmentRequests(): Promise<CoachAssignmentRequest[]> {
  const data = await request<CoachAssignmentRequestsResponse>('/api/coach/assignment-requests', {
    method: 'GET',
  })

  return data.requests
}

export async function approveCoachAssignment(studentEmail: string, coachCode: string): Promise<void> {
  await request<{ success: boolean }>(
    `/api/coach/assignment-requests/${encodeURIComponent(studentEmail)}/approve`,
    {
      method: 'POST',
      body: JSON.stringify({ coachCode }),
    },
  )
}

export async function getStudentFeedback(): Promise<CoachFeedbackRecord[]> {
  const data = await request<CoachFeedbackListResponse>('/api/student/feedback', {
    method: 'GET',
  })

  return data.feedback
}

export async function getPsychologyQuestions(): Promise<PsychologyQuestion[]> {
  const data = await request<PsychologyQuestionsResponse>('/api/intake/questions', {
    method: 'GET',
  })

  return data.questions
}

export async function submitAthleteIntake(payload: AthleteIntakePayload): Promise<AthleteIntakeResponse> {
  return request<AthleteIntakeResponse>('/api/intake/submit', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function signOut(): Promise<void> {
  await request<{ success: boolean }>('/api/auth/logout', {
    method: 'POST',
  })
}
