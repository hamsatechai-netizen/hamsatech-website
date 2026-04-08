import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  approveCoachAssignment,
  getCoachAssignmentRequests,
  getCoachAthleteDetails,
  getCoachAthletes,
  getStudentFeedback,
  getStudents,
  requestCoachAssignment,
  type CoachAssignmentRequest,
  type CoachAthleteDetail,
  type CoachAthleteListItem,
  type CoachFeedbackRecord,
  type StudentProfile,
} from '../lib/authApi'
import { getStoredProfile, subscribeToStoredProfile } from '../lib/profileStorage'
import '../styles/Dashboard.css'

function formatDate(dateValue?: string | null) {
  if (!dateValue) {
    return 'Not provided'
  }

  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(dateValue))
}

function getGreeting(fullName: string) {
  const hour = new Date().getHours()
  const firstName = fullName.trim().split(/\s+/)[0] || fullName
  const salutation =
    hour < 12 ? 'good morning' : hour < 17 ? 'good afternoon' : 'good evening'
  return `Hey ${firstName}, ${salutation}.`
}

function DashboardPage() {
  const { user, isLoading, refreshUser } = useAuth()
  const [students, setStudents] = useState<StudentProfile[]>([])
  const [athletes, setAthletes] = useState<CoachAthleteListItem[]>([])
  const [assignmentRequests, setAssignmentRequests] = useState<CoachAssignmentRequest[]>([])
  const [feedback, setFeedback] = useState<CoachFeedbackRecord[]>([])
  const [error, setError] = useState('')
  const [isFetching, setIsFetching] = useState(false)
  const [studentSearchTerm, setStudentSearchTerm] = useState('')
  const [intakeSearchTerm, setIntakeSearchTerm] = useState('')
  const [selectedStudentEmail, setSelectedStudentEmail] = useState('')
  const [selectedAthleteId, setSelectedAthleteId] = useState('')
  const [selectedRequestEmail, setSelectedRequestEmail] = useState('')
  const [selectedAthleteDetail, setSelectedAthleteDetail] = useState<CoachAthleteDetail | null>(null)
  const [isLoadingAthleteDetail, setIsLoadingAthleteDetail] = useState(false)
  const [studentProfileOverrides, setStudentProfileOverrides] = useState({
    sport: '',
    focusArea: '',
    dateOfBirth: '',
  })
  const [coachRequestState, setCoachRequestState] = useState({
    loading: false,
    error: '',
    success: '',
  })
  const [approvalCode, setApprovalCode] = useState('')
  const [approvalState, setApprovalState] = useState({
    loading: false,
    error: '',
    success: '',
  })

  const normalizedStudentSearchTerm = studentSearchTerm.trim().toLowerCase()

  useEffect(() => {
    if (!user?.email || user.role !== 'student') {
      setStudentProfileOverrides({ sport: '', focusArea: '', dateOfBirth: '' })
      return
    }

    const syncProfile = () => {
      const storedProfile = getStoredProfile(user.email)
      setStudentProfileOverrides({
        sport: storedProfile.sport ?? user.sport ?? '',
        focusArea: storedProfile.focusArea ?? user.focusArea ?? '',
        dateOfBirth: storedProfile.dateOfBirth ?? user.dateOfBirth ?? '',
      })
    }

    syncProfile()
    return subscribeToStoredProfile((email) => {
      if (!email || email === user.email.toLowerCase()) {
        syncProfile()
      }
    })
  }, [user])

  const loadDashboard = useCallback(async () => {
    if (!user) {
      return
    }

    setIsFetching(true)
    setError('')

    try {
      if (user.role === 'coach') {
        const [studentProfiles, athleteRecords, pendingRequests] = await Promise.all([
          getStudents(),
          getCoachAthletes(intakeSearchTerm),
          getCoachAssignmentRequests(),
        ])
        setStudents(studentProfiles)
        setAthletes(athleteRecords)
        setAssignmentRequests(pendingRequests)
        setFeedback([])
      } else {
        const feedbackRecords = await getStudentFeedback()
        setFeedback(feedbackRecords)
        setStudents([])
        setAthletes([])
        setAssignmentRequests([])
      }
    } catch (fetchError) {
      const nextMessage =
        fetchError instanceof Error ? fetchError.message : 'Unable to load dashboard data'
      setStudents([])
      setAthletes([])
      setAssignmentRequests([])
      setFeedback([])
      setError(nextMessage)
    } finally {
      setIsFetching(false)
    }
  }, [intakeSearchTerm, user])

  useEffect(() => {
    void loadDashboard()
  }, [loadDashboard])

  const filteredStudents = useMemo(() => {
    if (user?.role !== 'coach') {
      return []
    }

    if (!normalizedStudentSearchTerm) {
      return students
    }

    return students.filter((student) => {
      const haystacks = [student.fullName, student.email, student.sport, student.focusArea]
      return haystacks.some((value) => value.toLowerCase().includes(normalizedStudentSearchTerm))
    })
  }, [normalizedStudentSearchTerm, students, user?.role])

  useEffect(() => {
    if (user?.role !== 'coach') {
      setSelectedStudentEmail('')
      return
    }

    if (!filteredStudents.some((student) => student.email === selectedStudentEmail)) {
      setSelectedStudentEmail('')
    }
  }, [filteredStudents, selectedStudentEmail, user?.role])

  useEffect(() => {
    if (user?.role !== 'coach') {
      setSelectedAthleteId('')
      setSelectedAthleteDetail(null)
      return
    }

    if (!athletes.some((athlete) => athlete.athleteId === selectedAthleteId)) {
      setSelectedAthleteId('')
      setSelectedAthleteDetail(null)
    }
  }, [athletes, selectedAthleteId, user?.role])

  useEffect(() => {
    if (user?.role !== 'coach') {
      setSelectedRequestEmail('')
      return
    }

    if (!assignmentRequests.some((request) => request.email === selectedRequestEmail)) {
      setSelectedRequestEmail('')
    }
  }, [assignmentRequests, selectedRequestEmail, user?.role])

  useEffect(() => {
    const loadSelectedAthlete = async () => {
      if (!user || user.role !== 'coach' || !selectedAthleteId) {
        setSelectedAthleteDetail(null)
        return
      }

      setIsLoadingAthleteDetail(true)

      try {
        const detail = await getCoachAthleteDetails(selectedAthleteId)
        setSelectedAthleteDetail(detail)
      } catch {
        setSelectedAthleteDetail(null)
      } finally {
        setIsLoadingAthleteDetail(false)
      }
    }

    void loadSelectedAthlete()
  }, [selectedAthleteId, user])

  if (!isLoading && !user) {
    return <Navigate to="/signin" replace state={{ from: { pathname: '/dashboard' } }} />
  }

  if (!user) {
    return null
  }

  const selectedStudent =
    user.role === 'coach'
      ? filteredStudents.find((student) => student.email === selectedStudentEmail) ?? null
      : null

  const selectedAthlete =
    user.role === 'coach'
      ? athletes.find((athlete) => athlete.athleteId === selectedAthleteId) ?? null
      : null

  const selectedRequest =
    user.role === 'coach'
      ? assignmentRequests.find((request) => request.email === selectedRequestEmail) ?? null
      : null

  const handleCoachRequestSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setCoachRequestState({ loading: true, error: '', success: '' })

    try {
      await requestCoachAssignment()
      await refreshUser()
      setCoachRequestState({
        loading: false,
        error: '',
        success: 'Your assignment request has been sent to the main coach profile for review.',
      })
    } catch (requestError) {
      setCoachRequestState({
        loading: false,
        error:
          requestError instanceof Error
            ? requestError.message
            : 'Unable to send coach request.',
        success: '',
      })
    }
  }

  const handleApproveRequest = async () => {
    if (!selectedRequest) {
      return
    }

    setApprovalState({ loading: true, error: '', success: '' })

    try {
      await approveCoachAssignment(selectedRequest.email, approvalCode)
      await loadDashboard()
      setApprovalCode('')
      setApprovalState({
        loading: false,
        error: '',
        success: `${selectedRequest.fullName} is now assigned to your coach profile.`,
      })
    } catch (approvalError) {
      setApprovalState({
        loading: false,
        error: approvalError instanceof Error ? approvalError.message : 'Unable to approve request.',
        success: '',
      })
    }
  }

  return (
    <section className="dashboard-shell">
      <div className="dashboard-container">
        <div className="dashboard-hero">
          <h1>{getGreeting(user.fullName)}</h1>
          <p>
            {user.role === 'coach'
              ? 'Review assigned students, approve incoming requests, and open intake submissions only when you need them.'
              : 'Check your progress, request coach access when needed, and keep your intake and feedback connected to the right coach.'}
          </p>
        </div>

        {error ? <p className="dashboard-message dashboard-error">{error}</p> : null}
        {isFetching ? <p className="dashboard-message">Loading dashboard data...</p> : null}

        {user.role === 'coach' ? (
          <>
            <div className="dashboard-toolbar">
              <div className="dashboard-toolbar-stats">
                <article>
                  <span>Assigned Students</span>
                  <strong>{filteredStudents.length}</strong>
                </article>
                <article>
                  <span>Submitted Intakes</span>
                  <strong>{athletes.length}</strong>
                </article>
              </div>
            </div>

            <section className="dashboard-section">
              <div className="dashboard-section-header">
                <h2>Student Assignment Requests</h2>
                <p>Approve only the students who have requested your coach code.</p>
              </div>
              {approvalState.error ? (
                <p className="dashboard-message dashboard-error">{approvalState.error}</p>
              ) : null}
              {approvalState.success ? (
                <p className="dashboard-message dashboard-success">{approvalState.success}</p>
              ) : null}
              {assignmentRequests.length > 0 ? (
                <div className="coach-student-browser">
                  <div className="coach-student-tabs" role="tablist" aria-label="Student assignment requests">
                    {assignmentRequests.map((request) => (
                      <button
                        key={request.email}
                        type="button"
                        className={`coach-student-tab ${selectedRequest?.email === request.email ? 'active' : ''}`}
                        onClick={() => setSelectedRequestEmail(request.email)}
                      >
                        <span className="coach-student-tab-name">{request.fullName}</span>
                        <span className="coach-student-tab-meta">Pending assignment</span>
                      </button>
                    ))}
                  </div>

                  {selectedRequest ? (
                    <article className="student-card coach-student-panel">
                      <div className="student-card-header">
                        <div>
                          <p className="student-role">Pending Request</p>
                          <h2>{selectedRequest.fullName}</h2>
                        </div>
                        <span className="student-score">New</span>
                      </div>
                      <dl className="student-meta">
                        <div>
                          <dt>Email</dt>
                          <dd>{selectedRequest.email}</dd>
                        </div>
                        <div>
                          <dt>Requested Coach</dt>
                          <dd>{selectedRequest.requestedCoachName}</dd>
                        </div>
                        <div>
                          <dt>Sport</dt>
                          <dd>{selectedRequest.sport}</dd>
                        </div>
                        <div>
                          <dt>Focus Area</dt>
                          <dd>{selectedRequest.focusArea}</dd>
                        </div>
                        <div>
                          <dt>Requested On</dt>
                          <dd>{formatDate(selectedRequest.requestedAt)}</dd>
                        </div>
                      </dl>
                      <div className="dashboard-request-form dashboard-inline-actions">
                        <label className="dashboard-search">
                          <span>Enter Coach Code To Approve</span>
                          <input
                            type="text"
                            placeholder="Enter your coach code"
                            value={approvalCode}
                            onChange={(event) => {
                              setApprovalCode(event.target.value.toUpperCase())
                              setApprovalState((current) => ({ ...current, error: '', success: '' }))
                            }}
                            minLength={4}
                            required
                          />
                        </label>
                        <button
                          type="button"
                          className="dashboard-action-button"
                          onClick={handleApproveRequest}
                          disabled={approvalState.loading || approvalCode.trim().length < 4}
                        >
                          {approvalState.loading ? 'Assigning...' : 'Assign To My Coach Profile'}
                        </button>
                      </div>
                    </article>
                  ) : (
                    <div className="dashboard-empty-card coach-student-placeholder">
                      <p>Select a request to review the student and approve the assignment.</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="dashboard-empty-card">
                  <p>No pending coach assignment requests are waiting for you right now.</p>
                </div>
              )}
            </section>

            <section className="dashboard-section">
              <div className="dashboard-section-header">
                <h2>Assigned Student Accounts</h2>
                <p>Open a student name to review the full profile without listing every detail for everyone at once.</p>
              </div>
              <label className="dashboard-search dashboard-section-search">
                <span>Search Student Profiles</span>
                <input
                  type="search"
                  placeholder="Search by student name, email, sport, or focus area"
                  value={studentSearchTerm}
                  onChange={(event) => setStudentSearchTerm(event.target.value)}
                />
              </label>
              {filteredStudents.length > 0 ? (
                <div className="coach-student-browser">
                  <div className="coach-student-tabs" role="tablist" aria-label="Assigned student profiles">
                    {filteredStudents.map((student) => (
                      <button
                        key={student.email}
                        type="button"
                        className={`coach-student-tab ${selectedStudent?.email === student.email ? 'active' : ''}`}
                        onClick={() => setSelectedStudentEmail(student.email)}
                      >
                        <span className="coach-student-tab-name">{student.fullName}</span>
                        <span className="coach-student-tab-meta">{student.sport}</span>
                      </button>
                    ))}
                  </div>

                  {selectedStudent ? (
                    <article className="student-card coach-student-panel">
                      <div className="student-card-header">
                        <div>
                          <p className="student-role">Student</p>
                          <h2>{selectedStudent.fullName}</h2>
                        </div>
                        <span className="student-score">{selectedStudent.performanceScore}</span>
                      </div>
                      <dl className="student-meta">
                        <div>
                          <dt>Email</dt>
                          <dd>{selectedStudent.email}</dd>
                        </div>
                        <div>
                          <dt>Sport</dt>
                          <dd>{selectedStudent.sport}</dd>
                        </div>
                        <div>
                          <dt>Focus Area</dt>
                          <dd>{selectedStudent.focusArea}</dd>
                        </div>
                        <div>
                          <dt>Date of Birth</dt>
                          <dd>{formatDate(selectedStudent.dateOfBirth)}</dd>
                        </div>
                      </dl>
                    </article>
                  ) : (
                    <div className="dashboard-empty-card coach-student-placeholder">
                      <p>Select a student name to open the full profile.</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="dashboard-empty-card">
                  <p>
                    {normalizedStudentSearchTerm
                      ? 'No assigned student profiles match the current search.'
                      : 'No students are mapped to your coach account yet.'}
                  </p>
                </div>
              )}
            </section>

            <section className="dashboard-section">
              <div className="dashboard-section-header">
                <h2>Student Intake Records</h2>
                <p>Open a record to review details, identify weak areas, and add coach feedback.</p>
              </div>
              <label className="dashboard-search dashboard-section-search">
                <span>Search Intake Records</span>
                <input
                  type="search"
                  placeholder="Search by student or intake name"
                  value={intakeSearchTerm}
                  onChange={(event) => setIntakeSearchTerm(event.target.value)}
                />
              </label>
              {athletes.length > 0 ? (
                <div className="coach-student-browser">
                  <div className="coach-student-tabs" role="tablist" aria-label="Student intake records">
                    {athletes.map((athlete) => (
                      <button
                        key={athlete.athleteId}
                        type="button"
                        className={`coach-student-tab ${selectedAthlete?.athleteId === athlete.athleteId ? 'active' : ''}`}
                        onClick={() => setSelectedAthleteId(athlete.athleteId)}
                      >
                        <span className="coach-student-tab-name">{athlete.name}</span>
                        <span className="coach-student-tab-meta">{formatDate(athlete.createdAt)}</span>
                      </button>
                    ))}
                  </div>

                  {isLoadingAthleteDetail ? (
                    <div className="dashboard-empty-card coach-student-placeholder">
                      <p>Loading intake details...</p>
                    </div>
                  ) : selectedAthlete && selectedAthleteDetail ? (
                    <article className="student-card coach-student-panel">
                      <div className="student-card-header">
                        <div>
                          <p className="student-role">Submitted Intake</p>
                          <h2>{selectedAthlete.name}</h2>
                        </div>
                        <span className="student-score">{selectedAthlete.age}</span>
                      </div>
                      <dl className="student-meta">
                        <div>
                          <dt>Email</dt>
                          <dd>{selectedAthlete.email}</dd>
                        </div>
                        <div>
                          <dt>Gender</dt>
                          <dd>{selectedAthlete.gender}</dd>
                        </div>
                        <div>
                          <dt>Academy ID</dt>
                          <dd>{selectedAthlete.academyId}</dd>
                        </div>
                        <div>
                          <dt>Latest Session</dt>
                          <dd>
                            {selectedAthleteDetail.sessionsLog[0]
                              ? formatDate(selectedAthleteDetail.sessionsLog[0].sessionDate)
                              : 'Not added'}
                          </dd>
                        </div>
                        <div>
                          <dt>Latest Recovery</dt>
                          <dd>{selectedAthleteDetail.physiologyData[0]?.recoveryScore ?? 'Not added'}</dd>
                        </div>
                        <div>
                          <dt>Latest Stress</dt>
                          <dd>{selectedAthleteDetail.physiologyData[0]?.stressScore ?? 'Not added'}</dd>
                        </div>
                      </dl>
                      <div className="dashboard-inline-actions">
                        <Link
                          to={`/coach/athletes/${selectedAthlete.athleteId}`}
                          className="dashboard-inline-link"
                        >
                          Open Full Intake
                        </Link>
                      </div>
                    </article>
                  ) : (
                    <div className="dashboard-empty-card coach-student-placeholder">
                      <p>Select an intake record to open the actual submission details.</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="dashboard-empty-card">
                  <p>No intake submissions match the current filter.</p>
                </div>
              )}
            </section>
          </>
        ) : (
          <div className="student-dashboard-layout">
            <article className="student-card student-card-single">
              <div className="student-card-header">
                <div>
                  <p className="student-role">Student</p>
                  <h2>{user.fullName}</h2>
                </div>
                <span className="student-score">{user.performanceScore ?? 85}</span>
              </div>
              <dl className="student-meta">
                <div>
                  <dt>Email</dt>
                  <dd>{user.email}</dd>
                </div>
                <div>
                  <dt>Assignment Status</dt>
                  <dd className="dashboard-status-line">
                    <span className={`dashboard-status-pill ${user.assignmentStatus ?? 'unassigned'}`}>
                      {user.assignmentStatus ?? 'unassigned'}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt>Assigned Coach</dt>
                  <dd>{user.assignedCoachName ?? 'Not assigned yet'}</dd>
                </div>
                <div>
                  <dt>Coach Email</dt>
                  <dd>{user.assignedCoachEmail ?? 'Not assigned yet'}</dd>
                </div>
                <div>
                  <dt>Sport</dt>
                  <dd>{studentProfileOverrides.sport || 'General Training'}</dd>
                </div>
                <div>
                  <dt>Focus Area</dt>
                  <dd>{studentProfileOverrides.focusArea || 'Performance consistency'}</dd>
                </div>
                <div>
                  <dt>Date of Birth</dt>
                  <dd>{formatDate(studentProfileOverrides.dateOfBirth || user.dateOfBirth)}</dd>
                </div>
              </dl>
            </article>

            <section className="dashboard-section">
              <div className="dashboard-section-header">
                <h2>Coach Assignment</h2>
                <p>
                  {user.assignmentStatus === 'assigned'
                    ? 'Your coach assignment is active, so your intake and feedback stay linked to the right coach.'
                    : user.assignmentStatus === 'pending'
                      ? 'Your request is waiting for coach approval. You can update the coach code below if needed.'
                      : 'You can request a coach assignment here after signup. Intake submission unlocks once your coach approves you.'}
                </p>
              </div>

              <article className="student-card dashboard-request-card">
                <dl className="student-meta">
                  <div>
                    <dt>Requested Coach</dt>
                    <dd>{user.requestedCoachName ?? 'Main coach review queue'}</dd>
                  </div>
                  <div>
                    <dt>Request Destination</dt>
                    <dd>{user.requestedCoachEmail ?? 'Main coach dashboard'}</dd>
                  </div>
                  <div>
                    <dt>Coach Access</dt>
                    <dd>
                      {user.assignmentStatus === 'assigned'
                        ? 'Approved'
                        : user.assignmentStatus === 'pending'
                          ? 'Waiting for coach approval'
                          : 'No request sent yet'}
                    </dd>
                  </div>
                </dl>

                {user.assignmentStatus !== 'assigned' ? (
                  <form className="dashboard-request-form" onSubmit={handleCoachRequestSubmit}>
                    <div className="dashboard-request-note">
                      <strong>Request coach assignment</strong>
                      <p>
                        Send your request to the main coach profile. The coach will review your
                        name and complete the assignment from their dashboard.
                      </p>
                    </div>
                    {coachRequestState.error ? (
                      <p className="dashboard-message dashboard-error">{coachRequestState.error}</p>
                    ) : null}
                    {coachRequestState.success ? (
                      <p className="dashboard-message dashboard-success">{coachRequestState.success}</p>
                    ) : null}
                    <button
                      type="submit"
                      className="dashboard-action-button"
                      disabled={coachRequestState.loading}
                    >
                      {coachRequestState.loading
                        ? 'Sending Request...'
                        : user.assignmentStatus === 'pending'
                          ? 'Send Request Again'
                          : 'Request Coach Assignment'}
                    </button>
                  </form>
                ) : null}
              </article>
            </section>

            <section className="dashboard-section">
              <div className="dashboard-section-header">
                <h2>Coach Feedback</h2>
                <p>Your assigned coach&apos;s observations and recommendations appear here.</p>
              </div>
              {feedback.length > 0 ? (
                <div className="athlete-detail-list">
                  {feedback.map((item) => (
                    <article key={item.feedbackId} className="athlete-detail-row">
                      <strong>{item.status}</strong>
                      <span>
                        {item.coachName} | {formatDate(item.createdAt)}
                      </span>
                      <p>{item.note}</p>
                      <p>
                        <strong>Recommendation:</strong> {item.recommendation}
                      </p>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="dashboard-empty-card">
                  <p>
                    {user.assignmentStatus === 'assigned'
                      ? 'No coach feedback has been shared with you yet.'
                      : 'Coach feedback will appear here after your assignment is approved and your coach reviews your intake.'}
                  </p>
                </div>
              )}
            </section>
          </div>
        )}

        <div className="dashboard-links">
          <Link to="/home">Home</Link>
          {user.role === 'student' ? <Link to="/athlete-intake">My Intake</Link> : null}
          <Link to="/profile">Profile</Link>
        </div>
      </div>
    </section>
  )
}

export default DashboardPage
