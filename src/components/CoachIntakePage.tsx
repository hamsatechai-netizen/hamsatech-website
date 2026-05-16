import { useEffect, useMemo, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getCoachAthleteDetails, getCoachAthletes, type CoachAthleteDetail, type CoachAthleteListItem } from '../lib/authApi'
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

function CoachIntakePage() {
  const { user, isLoading } = useAuth()
  const [athletes, setAthletes] = useState<CoachAthleteListItem[]>([])
  const [error, setError] = useState('')
  const [isFetching, setIsFetching] = useState(false)
  const [intakeSearchTerm, setIntakeSearchTerm] = useState('')
  const [selectedAthleteId, setSelectedAthleteId] = useState('')
  const [selectedAthleteDetail, setSelectedAthleteDetail] = useState<CoachAthleteDetail | null>(null)
  const [isLoadingAthleteDetail, setIsLoadingAthleteDetail] = useState(false)

  const selectedAthlete = useMemo(
    () => athletes.find((athlete) => athlete.athleteId === selectedAthleteId) ?? null,
    [athletes, selectedAthleteId],
  )

  useEffect(() => {
    if (!user || user.role !== 'coach') {
      return
    }

    let isCancelled = false

    const loadAthletes = async () => {
      setIsFetching(true)
      setError('')

      try {
        const athleteRecords = await getCoachAthletes(intakeSearchTerm)
        if (isCancelled) {
          return
        }

        setAthletes(athleteRecords)
        setSelectedAthleteId((current) => {
          if (current && athleteRecords.some((item) => item.athleteId === current)) {
            return current
          }
          return athleteRecords[0]?.athleteId ?? ''
        })
      } catch (fetchError) {
        if (isCancelled) {
          return
        }
        setAthletes([])
        setSelectedAthleteId('')
        setSelectedAthleteDetail(null)
        setError(fetchError instanceof Error ? fetchError.message : 'Unable to load intake records')
      } finally {
        if (!isCancelled) {
          setIsFetching(false)
        }
      }
    }

    void loadAthletes()

    return () => {
      isCancelled = true
    }
  }, [intakeSearchTerm, user])

  useEffect(() => {
    if (!user || user.role !== 'coach') {
      return
    }

    const loadSelectedAthlete = async () => {
      if (!selectedAthleteId) {
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
    return <Navigate to="/signin" replace state={{ from: { pathname: '/athlete-intake' } }} />
  }

  if (!user) {
    return null
  }

  if (user.role !== 'coach') {
    return <Navigate to="/athlete-intake" replace />
  }

  return (
    <section className="dashboard-shell">
      <div className="dashboard-container">
        <div className="dashboard-hero">
          <h1>Student Intake Records</h1>
          <p>Open a record to review details, identify weak areas, and add coach feedback.</p>
        </div>

        <section className="dashboard-section">
          <label className="dashboard-search dashboard-section-search">
            <span>Search Intake Records</span>
            <input
              type="search"
              placeholder="Search by student or intake name"
              value={intakeSearchTerm}
              onChange={(event) => setIntakeSearchTerm(event.target.value)}
            />
          </label>

          {error ? (
            <div className="dashboard-empty-card">
              <p>{error}</p>
            </div>
          ) : isFetching ? (
            <div className="dashboard-empty-card">
              <p>Loading intake records...</p>
            </div>
          ) : athletes.length > 0 ? (
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
                      <dt>Academy</dt>
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

        <div className="dashboard-links">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/profile">Profile</Link>
        </div>
      </div>
    </section>
  )
}

export default CoachIntakePage
