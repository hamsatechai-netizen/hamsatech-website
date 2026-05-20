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

export type CoachProfile = {
  coachId: string
  name: string
  email: string
  phone?: string | null
  profileImage?: string | null
  specialization?: string | null
  status: 'active' | 'inactive'
  assignedAthletes: number
  createdAt?: string | null
  updatedAt?: string | null
}

export type AthleteScoreRecord = {
  scoreId: string
  athleteId: string
  scoreType: string
  scoreValue: number
  percentile?: number | null
  category: string
  calculatedAt: string
  sourceData?: Record<string, unknown> | null
  createdAt?: string | null
  updatedAt?: string | null
}

export type NotificationRecord = {
  notificationId: string
  recipientEmail: string
  recipientRole: string
  title: string
  message: string
  type: string
  entityId?: string | null
  readAt?: string | null
  createdAt: string
}

export type CoachNotification = {
  notificationId: string
  type: string
  athleteId?: string | null
  athleteName?: string | null
  sessionId?: string | null
  requestId?: string | null
  message: string
  actionUrl?: string | null
  createdAt: string
  isRead: boolean
}

export type PendingAssignment = {
  requestId: string
  athleteId: string
  athleteName: string
  assignedCoachId?: string | null
  status: 'PENDING' | 'ASSIGNED' | 'REJECTED'
  notes?: string | null
  requestedAt?: string | null
}

export type CoachOption = {
  coachId: string
  coachName: string
  coachIdText?: string | null
  specialization?: string | null
}

export type CoachDashboardV1Athlete = {
  athleteId: string
  athleteName: string
  gender?: string | null
  age?: number | null
  score?: number | null
  scoreCategory: string
  latestStress?: number | null
  latestRecovery?: number | null
  lastSessionDate?: string | null
}

export type CoachDashboardV1 = {
  coachId: string
  totals: {
    totalAssignedAthletes: number
    activeAthletes: number
    inactiveAthletes: number
    newRegistrations: number
  }
  averageScore?: number | null
  scoreDistribution: Record<string, number>
  athletes: CoachDashboardV1Athlete[]
  alerts: string[]
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
  age?: number | null
  gender?: string | null
  academyId?: string | null
  coachId?: string | null
  email?: string | null
  contactNumber?: string | null
  createdAt?: string | null
  latestSessionDate?: string | null
  latestTrainingType?: 'Shooting' | 'Fitness' | 'Mental' | 'Recovery' | null
  latestRecoveryScore?: number | null
  latestStressScore?: number | null
  latestFatigueLevel?: number | null
  latestSleepHours?: number | null
  overallScore?: number | null
}

export type CoachAthleteDetail = {
  athleteMaster: {
    athleteId: string
    name: string
    age?: number | null
    gender?: string | null
    heightCm?: number | null
    weightKg?: number | null
    academyId?: string | null
    coachId?: string | null
    contactNumber?: string | null
    email?: string | null
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
  scores?: AthleteScoreRecord[]
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

type CoachProfileResponse = {
  profile: CoachProfile
}

type AthleteScoresResponse = {
  scores: AthleteScoreRecord[]
}

type NotificationsResponse = {
  notifications: NotificationRecord[]
}

type CoachNotificationsResponse = {
  notifications: CoachNotification[]
  unreadCount: number
}

type PendingAssignmentsResponse = {
  requests: PendingAssignment[]
}

type CoachOptionsResponse = {
  coaches: CoachOption[]
}

type CoachDashboardV1Response = {
  dashboard: CoachDashboardV1
}

type AthleteFullProfileV1Response = {
  athlete: CoachAthleteDetail & { feedbackHistory?: CoachFeedbackRecord[] }
}

export type CoachDashboardSummary = {
  totalAssignedAthletes: number
  newRegistrations: number
  activeAthletes: number
  inactiveAthletes: number
  averageScore?: number | null
  highestPerforming: CoachAthleteListItem[]
  lowestPerforming: CoachAthleteListItem[]
  scoreDistribution: Record<string, number>
  recentActivity: NotificationRecord[]
  alerts: string[]
}

type CoachDashboardSummaryResponse = {
  summary: CoachDashboardSummary
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

function getApiBaseUrl() {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()

  if (configuredBaseUrl && !configuredBaseUrl.includes('your-fastapi-api.example.com')) {
    return configuredBaseUrl.replace(/\/+$/, '')
  }

  if (typeof window !== 'undefined') {
    const { hostname } = window.location
    if (hostname === '127.0.0.1' || hostname === 'localhost') {
      return 'http://127.0.0.1:8000'
    }

    if (hostname.endsWith('.hamsatech-website.pages.dev')) {
      return 'https://hamsatech-api.onrender.com'
    }
  }

  return ''
}

const API_BASE_URL = getApiBaseUrl()

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
  if (!API_BASE_URL) {
    throw new Error('API is not configured. Set VITE_API_BASE_URL for this deployment.')
  }

  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers ?? {}),
      },
      ...init,
    })
  } catch {
    throw new Error(`Unable to reach the API at ${API_BASE_URL}. Check backend deployment and CORS settings.`)
  }

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
  if (!API_BASE_URL) {
    throw new Error('API is not configured. Set VITE_API_BASE_URL for this deployment.')
  }

  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      credentials: 'include',
    })
  } catch {
    throw new Error(`Unable to reach the API at ${API_BASE_URL}. Check backend deployment and CORS settings.`)
  }

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

export async function getCoachAthletes(options?: {
  search?: string
  athleteIds?: string[]
  includePending?: boolean
}): Promise<CoachAthleteListItem[]> {
  const search = options?.search?.trim() ?? ''
  const params = new URLSearchParams()
  if (search) params.set('search', search)
  if (options?.athleteIds && options.athleteIds.length > 0) params.set('athleteIds', options.athleteIds.join(','))
  if (typeof options?.includePending === 'boolean') params.set('includePending', String(options.includePending))
  const query = params.toString() ? `?${params.toString()}` : ''
  const data = await request<CoachAthleteListResponse>(`/api/coach/athletes${query}`, {
    method: 'GET',
  })

  return data.athletes
}

export async function getCoachDashboardSummary(): Promise<CoachDashboardSummary> {
  const data = await request<CoachDashboardSummaryResponse>('/api/coach/dashboard-summary', {
    method: 'GET',
  })

  return data.summary
}

export async function getCoachProfile(): Promise<CoachProfile> {
  const data = await request<CoachProfileResponse>('/api/coach/profile', {
    method: 'GET',
  })

  return data.profile
}

export async function updateCoachProfile(payload: Partial<Pick<CoachProfile, 'name' | 'phone' | 'profileImage' | 'specialization' | 'status'>>): Promise<CoachProfile> {
  const data = await request<CoachProfileResponse>('/api/coach/profile', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })

  return data.profile
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

export async function getCoachAthleteScores(athleteId: string): Promise<AthleteScoreRecord[]> {
  const data = await request<AthleteScoresResponse>(
    `/api/coach/athletes/${encodeURIComponent(athleteId)}/scores`,
    {
      method: 'GET',
    },
  )

  return data.scores
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

export async function getNotifications(): Promise<NotificationRecord[]> {
  const data = await request<NotificationsResponse>('/api/notifications', {
    method: 'GET',
  })

  return data.notifications
}

export async function markNotificationRead(notificationId: string): Promise<void> {
  await request<{ success: boolean }>(`/api/notifications/${encodeURIComponent(notificationId)}/read`, {
    method: 'POST',
  })
}

export async function createFeedbackRequest(payload: {
  athleteId: string
  sessionId: string
  coachId: string
}): Promise<{ requestId: string; status: 'PENDING'; message: string }> {
  return request('/api/v1/feedback_requests', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function getCoachNotificationsV1(
  coachId: string,
  options?: { unreadOnly?: boolean; limit?: number },
): Promise<CoachNotificationsResponse> {
  const params = new URLSearchParams()
  if (typeof options?.unreadOnly === 'boolean') params.set('unreadOnly', String(options.unreadOnly))
  if (typeof options?.limit === 'number') params.set('limit', String(options.limit))
  const query = params.toString() ? `?${params.toString()}` : ''
  return request<CoachNotificationsResponse>(`/api/v1/coaches/${encodeURIComponent(coachId)}/notifications${query}`, {
    method: 'GET',
  })
}

export async function markCoachNotificationRead(notificationId: string): Promise<{
  notificationId: string
  isRead: boolean
  readAt?: string | null
}> {
  return request(`/api/v1/notifications/${encodeURIComponent(notificationId)}/mark_read`, {
    method: 'PATCH',
  })
}

export async function createCoachFeedbackV1(payload: {
  requestId: string
  athleteId: string
  note: string
  recommendation: string
  status: 'Needs Attention' | 'Progressing' | 'Strong'
}): Promise<CoachFeedbackRecord> {
  const data = await request<CoachFeedbackResponse>('/api/v1/coach_feedback', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return data.feedback
}

export async function getPendingAssignments(coachId: string): Promise<PendingAssignment[]> {
  const data = await request<PendingAssignmentsResponse>(`/api/v1/coaches/${encodeURIComponent(coachId)}/pending_assignments`, {
    method: 'GET',
  })
  return data.requests
}

export async function getAvailableCoaches(): Promise<CoachOption[]> {
  const data = await request<CoachOptionsResponse>('/api/v1/coaches/available', {
    method: 'GET',
  })
  return data.coaches
}

export async function assignAthlete(payload: {
  requestId: string
  athleteId: string
  assignedCoachId: string
  notes?: string
}): Promise<void> {
  await request('/api/v1/assignments/assign', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function getCoachDashboardV1(
  coachId: string,
  options?: { gender?: string; minScore?: number; maxScore?: number },
): Promise<CoachDashboardV1> {
  const params = new URLSearchParams()
  if (options?.gender) params.set('gender', options.gender)
  if (typeof options?.minScore === 'number') params.set('minScore', String(options.minScore))
  if (typeof options?.maxScore === 'number') params.set('maxScore', String(options.maxScore))
  const query = params.toString() ? `?${params.toString()}` : ''
  const data = await request<CoachDashboardV1Response>(`/api/v1/coaches/${encodeURIComponent(coachId)}/dashboard${query}`, {
    method: 'GET',
  })
  return data.dashboard
}

export async function getAthleteFullProfileV1(athleteId: string): Promise<CoachAthleteDetail & { feedbackHistory?: CoachFeedbackRecord[] }> {
  const data = await request<AthleteFullProfileV1Response>(`/api/v1/athletes/${encodeURIComponent(athleteId)}/full_profile`, {
    method: 'GET',
  })
  return data.athlete
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
