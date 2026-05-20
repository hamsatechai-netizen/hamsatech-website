import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, Navigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  getCoachAssignmentRequests,
  getCoachAthletes,
  getCoachDashboardSummary,
  getCoachProfile,
  getNotifications,
  type CoachAssignmentRequest,
  type CoachAthleteListItem,
  type CoachDashboardSummary,
  type CoachProfile,
  type NotificationRecord,
} from '../lib/authApi'
import '../styles/Dashboard.css'

type AthleteRow = CoachAthleteListItem & {
  performanceScore: number | null
  sport: string | null
  focusArea: string | null
}

function getGreeting(fullName: string) {
  const hour = new Date().getHours()
  const firstName = fullName.trim().split(/\s+/)[0] || fullName
  const salutation = hour < 12 ? 'good morning' : hour < 17 ? 'good afternoon' : 'good evening'
  return `Hey ${firstName}, ${salutation}.`
}

function getScoreStatus(score: number | null): { label: string; cls: string } {
  if (score === null) return { label: 'Pending', cls: 'pending' }
  if (score >= 80) return { label: 'Top Performer', cls: 'strong' }
  if (score >= 60) return { label: 'Progressing', cls: 'progressing' }
  return { label: 'Needs Attention', cls: 'attention' }
}

function formatDate(value?: string | null) {
  if (!value) return 'Not added'
  return new Intl.DateTimeFormat('en-IN', { year: 'numeric', month: 'short', day: 'numeric' }).format(new Date(value))
}

function CoachDashboardPage() {
  const { user, isLoading } = useAuth()
  const [searchParams] = useSearchParams()
  const [athletes, setAthletes] = useState<CoachAthleteListItem[]>([])
  const [requests, setRequests] = useState<CoachAssignmentRequest[]>([])
  const [summary, setSummary] = useState<CoachDashboardSummary | null>(null)
  const [coachProfile, setCoachProfile] = useState<CoachProfile | null>(null)
  const [notifications, setNotifications] = useState<NotificationRecord[]>([])
  const [isFetching, setIsFetching] = useState(false)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [genderFilter, setGenderFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sportFilter, setSportFilter] = useState('all')
  const [selectedAthleteId, setSelectedAthleteId] = useState('')
  const [selectedRequestEmail, setSelectedRequestEmail] = useState('')
  const scopedAthleteIds = useMemo(
    () => (searchParams.get('athleteIds') ?? '').split(',').map((value) => value.trim()).filter(Boolean),
    [searchParams],
  )

  const loadDashboard = useCallback(async () => {
    if (!user) return
    setIsFetching(true)
    setError('')
    try {
      const [athleteList, requestList, dashboardSummary, profile, notificationList] = await Promise.all([
        getCoachAthletes({ athleteIds: scopedAthleteIds, includePending: false }),
        getCoachAssignmentRequests(),
        getCoachDashboardSummary(),
        getCoachProfile(),
        getNotifications(),
      ])
      setAthletes(athleteList)
      setRequests(requestList)
      setSummary(dashboardSummary)
      setCoachProfile(profile)
      setNotifications(notificationList)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load dashboard data')
    } finally {
      setIsFetching(false)
    }
  }, [scopedAthleteIds, user])

  useEffect(() => {
    void loadDashboard()
  }, [loadDashboard])

  const mergedAthletes = useMemo<AthleteRow[]>(
    () =>
      athletes.map((athlete) => ({
        ...athlete,
        performanceScore: athlete.overallScore ?? null,
        sport: null,
        focusArea: null,
      })),
    [athletes],
  )

  const filteredAthletes = useMemo(() => {
    const term = searchTerm.trim().toLowerCase()
    return mergedAthletes.filter((athlete) => {
      const status = getScoreStatus(athlete.performanceScore).cls
      const matchesTerm =
        !term ||
        athlete.name.toLowerCase().includes(term) ||
        (athlete.email ?? '').toLowerCase().includes(term) ||
        (athlete.sport ?? '').toLowerCase().includes(term) ||
        (athlete.latestTrainingType ?? '').toLowerCase().includes(term)
      const matchesGender = genderFilter === 'all' || (athlete.gender ?? '').toLowerCase() === genderFilter
      const matchesStatus = statusFilter === 'all' || status === statusFilter
      const matchesSport = sportFilter === 'all' || (athlete.sport ?? 'Not added') === sportFilter
      return matchesTerm && matchesGender && matchesStatus && matchesSport
    })
  }, [genderFilter, mergedAthletes, searchTerm, sportFilter, statusFilter])

  const sportOptions = useMemo(
    () => Array.from(new Set(mergedAthletes.map((athlete) => athlete.sport ?? 'Not added'))).sort(),
    [mergedAthletes],
  )

  const teamStats = useMemo(() => {
    const withScores = mergedAthletes.filter((athlete) => athlete.performanceScore !== null)
    const withRecovery = mergedAthletes.filter((athlete) => typeof athlete.latestRecoveryScore === 'number')
    const avgScore = withScores.length
      ? Math.round(withScores.reduce((sum, athlete) => sum + athlete.performanceScore!, 0) / withScores.length)
      : null
    const avgRecovery = withRecovery.length
      ? Math.round(withRecovery.reduce((sum, athlete) => sum + (athlete.latestRecoveryScore ?? 0), 0) / withRecovery.length)
      : null
    const topPerformers = mergedAthletes.filter((athlete) => (athlete.performanceScore ?? -1) >= 80)
    const progressing = mergedAthletes.filter((athlete) => {
      const score = athlete.performanceScore
      return score !== null && score >= 60 && score < 80
    })
    const needsAttention = mergedAthletes.filter((athlete) => athlete.performanceScore !== null && athlete.performanceScore < 60)
    const pendingAssessment = mergedAthletes.filter((athlete) => athlete.performanceScore === null)
    const highStress = mergedAthletes.filter((athlete) => (athlete.latestStressScore ?? -1) >= 65)

    return { total: mergedAthletes.length, avgScore, avgRecovery, topPerformers, progressing, needsAttention, pendingAssessment, highStress }
  }, [mergedAthletes])

  const selectedAthlete = useMemo(
    () => filteredAthletes.find((athlete) => athlete.athleteId === selectedAthleteId) ?? null,
    [filteredAthletes, selectedAthleteId],
  )

  const selectedRequest = useMemo(
    () => requests.find((request) => request.email === selectedRequestEmail) ?? null,
    [requests, selectedRequestEmail],
  )

  useEffect(() => {
    if (!filteredAthletes.some((athlete) => athlete.athleteId === selectedAthleteId)) {
      setSelectedAthleteId(filteredAthletes[0]?.athleteId ?? '')
    }
  }, [filteredAthletes, selectedAthleteId])

  useEffect(() => {
    if (!requests.some((request) => request.email === selectedRequestEmail)) {
      setSelectedRequestEmail(requests[0]?.email ?? '')
    }
  }, [requests, selectedRequestEmail])

  if (!isLoading && !user) {
    return <Navigate to="/coach/login" replace />
  }

  if (!isLoading && user && user.role !== 'coach') {
    return <Navigate to="/dashboard" replace />
  }

  if (!user) return null

  return (
    <section className="dashboard-shell">
      <div className="dashboard-container">
        <div className="dashboard-hero">
          <p className="dashboard-eyebrow">Coach Dashboard</p>
          <h1>{getGreeting(user.fullName)}</h1>
          <p>{coachProfile?.specialization ? `${coachProfile.specialization}. ` : ''}Monitor assigned athletes, score trends, alerts, and mobile-app registration activity from Supabase.</p>
        </div>

        {error ? <p className="dashboard-message dashboard-error">{error}</p> : null}
        {isFetching ? <p className="dashboard-message">Loading dashboard...</p> : null}

        <section className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>Team Overview</h2>
          </div>
          <div className="coach-overview-grid">
            <article className="coach-stat-tile">
              <span>Total Athletes</span>
              <strong>{summary?.totalAssignedAthletes ?? teamStats.total}</strong>
            </article>
            <article className="coach-stat-tile">
              <span>New Registrations</span>
              <strong>{summary?.newRegistrations ?? 0}</strong>
            </article>
            <article className="coach-stat-tile">
              <span>Active Athletes</span>
              <strong>{summary?.activeAthletes ?? teamStats.total}</strong>
            </article>
            <article className="coach-stat-tile coach-stat-tile--alert">
              <span>Action Items</span>
              <strong>{summary?.alerts.length ?? teamStats.highStress.length}</strong>
            </article>
            <article className="coach-stat-tile">
              <span>Average Score</span>
              <strong>{summary?.averageScore ?? teamStats.avgScore ?? '-'}</strong>
            </article>
          </div>
        </section>

        <section className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>Score Distribution</h2>
            <p>Read from backend score records, with fallback calculated scores when the score table has not been populated yet.</p>
          </div>
          <div className="score-chart-grid">
            {Object.entries(summary?.scoreDistribution ?? {}).map(([label, value]) => (
              <article key={label} className="score-bar-card">
                <span>{label.replace(/([A-Z])/g, ' $1')}</span>
                <div className="score-bar-track">
                  <div className="score-bar-fill" style={{ width: `${Math.min(100, value * 20)}%` }} />
                </div>
                <strong>{value}</strong>
              </article>
            ))}
          </div>
        </section>

        <section className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>Notifications</h2>
            <p>Mobile registrations, assignments, intake submissions, and score alerts appear here.</p>
          </div>
          {notifications.length > 0 ? (
            <div className="notification-list">
              {notifications.slice(0, 6).map((notification) => (
                <article key={notification.notificationId} className={`notification-item ${notification.readAt ? '' : 'unread'}`}>
                  <strong>{notification.title}</strong>
                  <span>{formatDate(notification.createdAt)}</span>
                  <p>{notification.message}</p>
                </article>
              ))}
            </div>
          ) : (
            <div className="dashboard-empty-card"><p>No notifications yet.</p></div>
          )}
        </section>

        {mergedAthletes.length > 0 ? (
          <section className="dashboard-section">
            <div className="dashboard-section-header">
              <h2>Status Breakdown</h2>
              <p>Based on account scores and latest physiology records from the connected intake tables.</p>
            </div>
            <div className="coach-status-bands">
              {teamStats.topPerformers.length > 0 ? (
                <div className="coach-status-band coach-status-band--strong">
                  <span className="coach-status-band-label">Top Performers ({teamStats.topPerformers.length})</span>
                  <div className="risk-chip-row">
                    {teamStats.topPerformers.map((athlete) => (
                      <Link key={athlete.athleteId} to={`/coach/athletes/${athlete.athleteId}`} className="risk-chip risk-chip--strong">
                        {athlete.name} - {athlete.performanceScore}
                      </Link>
                    ))}
                  </div>
                </div>
              ) : null}

              {teamStats.progressing.length > 0 ? (
                <div className="coach-status-band coach-status-band--progressing">
                  <span className="coach-status-band-label">Progressing ({teamStats.progressing.length})</span>
                  <div className="risk-chip-row">
                    {teamStats.progressing.map((athlete) => (
                      <Link key={athlete.athleteId} to={`/coach/athletes/${athlete.athleteId}`} className="risk-chip risk-chip--progressing">
                        {athlete.name} - {athlete.performanceScore}
                      </Link>
                    ))}
                  </div>
                </div>
              ) : null}

              {teamStats.needsAttention.length > 0 ? (
                <div className="coach-status-band coach-status-band--attention">
                  <span className="coach-status-band-label">Needs Attention ({teamStats.needsAttention.length})</span>
                  <div className="risk-chip-row">
                    {teamStats.needsAttention.map((athlete) => (
                      <Link key={athlete.athleteId} to={`/coach/athletes/${athlete.athleteId}`} className="risk-chip risk-chip--attention">
                        {athlete.name} - {athlete.performanceScore}
                      </Link>
                    ))}
                  </div>
                </div>
              ) : null}

              {teamStats.pendingAssessment.length > 0 ? (
                <div className="coach-status-band coach-status-band--pending">
                  <span className="coach-status-band-label">Pending Assessment ({teamStats.pendingAssessment.length})</span>
                  <div className="risk-chip-row">
                    {teamStats.pendingAssessment.map((athlete) => (
                      <span key={athlete.athleteId} className="risk-chip risk-chip--pending">{athlete.name}</span>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </section>
        ) : null}

        <section className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>Athlete Profiles</h2>
            <p>Select an athlete to preview their latest Supabase intake data and open the full profile.</p>
          </div>
          <label className="dashboard-search dashboard-section-search">
            <span>Search Athletes</span>
            <input
              type="search"
              placeholder="Search by name, email, sport, or training type"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />
          </label>
          <div className="dashboard-filter-row">
            <label>
              <span>Gender</span>
              <select value={genderFilter} onChange={(event) => setGenderFilter(event.target.value)}>
                <option value="all">All</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </label>
            <label>
              <span>Sport</span>
              <select value={sportFilter} onChange={(event) => setSportFilter(event.target.value)}>
                <option value="all">All</option>
                {sportOptions.map((sport) => <option key={sport} value={sport}>{sport}</option>)}
              </select>
            </label>
            <label>
              <span>Status</span>
              <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
                <option value="all">All</option>
                <option value="strong">Top Performer</option>
                <option value="progressing">Progressing</option>
                <option value="attention">Needs Attention</option>
              </select>
            </label>
          </div>
          {filteredAthletes.length > 0 ? (
            <div className="coach-student-browser">
              <div className="coach-student-tabs" role="tablist" aria-label="Athlete profiles">
                {filteredAthletes.map((athlete) => {
                  const status = getScoreStatus(athlete.performanceScore)
                  return (
                    <button
                      key={athlete.athleteId}
                      type="button"
                      className={`coach-student-tab ${selectedAthleteId === athlete.athleteId ? 'active' : ''}`}
                      onClick={() => setSelectedAthleteId(athlete.athleteId)}
                    >
                      <span className="coach-student-tab-name">{athlete.name}</span>
                      <span className="coach-student-tab-meta">{status.label}</span>
                    </button>
                  )
                })}
              </div>

              {selectedAthlete ? (
                <article className="student-card coach-student-panel">
                  <div className="student-card-header">
                    <div>
                      <p className="student-role">{getScoreStatus(selectedAthlete.performanceScore).label}</p>
                      <h2>{selectedAthlete.name}</h2>
                    </div>
                    {selectedAthlete.performanceScore !== null ? (
                      <span className="student-score">{selectedAthlete.performanceScore}</span>
                    ) : null}
                  </div>
                  <dl className="student-meta">
                    <div><dt>Email</dt><dd>{selectedAthlete.email || 'Not provided'}</dd></div>
                    <div><dt>Age</dt><dd>{selectedAthlete.age ?? 'Not provided'}</dd></div>
                    <div><dt>Gender</dt><dd>{selectedAthlete.gender || 'Not provided'}</dd></div>
                    {selectedAthlete.sport ? <div><dt>Sport</dt><dd>{selectedAthlete.sport}</dd></div> : null}
                    {selectedAthlete.focusArea ? <div><dt>Focus Area</dt><dd>{selectedAthlete.focusArea}</dd></div> : null}
                    <div><dt>Latest Session</dt><dd>{formatDate(selectedAthlete.latestSessionDate)}</dd></div>
                    <div><dt>Training Type</dt><dd>{selectedAthlete.latestTrainingType ?? 'Not added'}</dd></div>
                    <div><dt>Recovery</dt><dd>{selectedAthlete.latestRecoveryScore ?? 'Not added'}</dd></div>
                    <div><dt>Stress</dt><dd>{selectedAthlete.latestStressScore ?? 'Not added'}</dd></div>
                    <div><dt>Sleep</dt><dd>{selectedAthlete.latestSleepHours ?? 'Not added'}</dd></div>
                    <div><dt>Registered</dt><dd>{formatDate(selectedAthlete.createdAt)}</dd></div>
                  </dl>
                  <div className="dashboard-inline-actions">
                    <Link to={`/coach/athletes/${selectedAthlete.athleteId}`} className="dashboard-inline-link">
                      View Full Profile
                    </Link>
                  </div>
                </article>
              ) : (
                <div className="dashboard-empty-card coach-student-placeholder">
                  <p>Select an athlete to preview their record.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="dashboard-empty-card">
              <p>
                {searchTerm.trim()
                  ? 'No athletes match the current search.'
                  : 'No athlete profiles are linked to your coach account yet.'}
              </p>
            </div>
          )}
        </section>

        <section className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>Assignment Requests</h2>
            <p>View students who requested coach assignment. Assignment actions stay in the app.</p>
          </div>
          {requests.length > 0 ? (
            <div className="coach-student-browser">
              <div className="coach-student-tabs" role="tablist" aria-label="Pending assignment requests">
                {requests.map((request) => (
                  <button
                    key={request.email}
                    type="button"
                    className={`coach-student-tab ${selectedRequestEmail === request.email ? 'active' : ''}`}
                    onClick={() => setSelectedRequestEmail(request.email)}
                  >
                    <span className="coach-student-tab-name">{request.fullName}</span>
                    <span className="coach-student-tab-meta">Pending</span>
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
                    <div><dt>Email</dt><dd>{selectedRequest.email}</dd></div>
                    <div><dt>Sport</dt><dd>{selectedRequest.sport}</dd></div>
                    <div><dt>Focus Area</dt><dd>{selectedRequest.focusArea}</dd></div>
                    <div><dt>Requested On</dt><dd>{formatDate(selectedRequest.requestedAt)}</dd></div>
                    <div><dt>Status</dt><dd>Waiting for app approval workflow</dd></div>
                  </dl>
                </article>
              ) : (
                <div className="dashboard-empty-card coach-student-placeholder">
                  <p>Select a request to review and approve the assignment.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="dashboard-empty-card">
              <p>No pending assignment requests right now.</p>
            </div>
          )}
        </section>

        <div className="dashboard-links">
          <Link to="/">Home</Link>
          <Link to="/athlete-intake">Intake Records</Link>
          <Link to="/profile">Profile</Link>
          <Link to="/signout">Sign Out</Link>
        </div>
      </div>
    </section>
  )
}

export default CoachDashboardPage
