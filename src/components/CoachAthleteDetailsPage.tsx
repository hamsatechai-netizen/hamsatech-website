import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  createCoachAthleteFeedback,
  getCoachAthleteDetails,
  getCoachAthleteFeedback,
  type CoachAthleteDetail,
  type CoachFeedbackRecord,
} from '../lib/authApi'
import '../styles/Dashboard.css'

function formatDate(value?: string | null) {
  if (!value) {
    return 'Not provided'
  }

  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(value))
}

function clampPercent(value: number) {
  return Math.max(0, Math.min(100, Math.round(value)))
}

function CoachAthleteDetailsPage() {
  const { athleteId } = useParams()
  const { user, isLoading } = useAuth()
  const [athlete, setAthlete] = useState<CoachAthleteDetail | null>(null)
  const [feedback, setFeedback] = useState<CoachFeedbackRecord[]>([])
  const [error, setError] = useState('')
  const [feedbackError, setFeedbackError] = useState('')
  const [isFetching, setIsFetching] = useState(false)
  const [isSavingFeedback, setIsSavingFeedback] = useState(false)
  const [feedbackForm, setFeedbackForm] = useState({
    note: '',
    recommendation: '',
    status: 'Progressing' as CoachFeedbackRecord['status'],
  })

  useEffect(() => {
    if (!user || user.role !== 'coach' || !athleteId) {
      return
    }

    const loadAthlete = async () => {
      setIsFetching(true)
      setError('')

      try {
        const [details, feedbackItems] = await Promise.all([
          getCoachAthleteDetails(athleteId),
          getCoachAthleteFeedback(athleteId),
        ])
        setAthlete(details)
        setFeedback(feedbackItems)
      } catch (fetchError) {
        setError(fetchError instanceof Error ? fetchError.message : 'Unable to load athlete details')
      } finally {
        setIsFetching(false)
      }
    }

    void loadAthlete()
  }, [athleteId, user])

  const latestSession = useMemo(() => athlete?.sessionsLog[0] ?? null, [athlete])
  const latestPhysiology = useMemo(() => athlete?.physiologyData[0] ?? null, [athlete])

  const insightMetrics = useMemo(() => {
    if (!athlete || !latestPhysiology) {
      return []
    }

    const scaleResponses = athlete.psychologyResponses.filter((response) => typeof response.answerScore === 'number')
    const focusScores = scaleResponses
      .filter((response) => response.category.toLowerCase() === 'focus')
      .map((response) => response.answerScore as number)
    const focusAverage = focusScores.length
      ? Math.round(focusScores.reduce((total, value) => total + value, 0) / focusScores.length) * 10
      : 50

    return [
      {
        label: 'Recovery',
        score: clampPercent(latestPhysiology.recoveryScore),
        target: 80,
      },
      {
        label: 'Sleep',
        score: clampPercent((latestPhysiology.sleepHours / 8) * 100),
        target: 90,
      },
      {
        label: 'Stress Control',
        score: clampPercent(100 - latestPhysiology.stressScore),
        target: 75,
      },
      {
        label: 'Fatigue Readiness',
        score: clampPercent(100 - latestPhysiology.fatigueLevel * 10),
        target: 80,
      },
      {
        label: 'Focus',
        score: clampPercent(focusAverage),
        target: 80,
      },
    ].sort((left, right) => left.score - right.score)
  }, [athlete, latestPhysiology])

  const weakestAreas = useMemo(() => insightMetrics.slice(0, 3), [insightMetrics])

  const handleSubmitFeedback = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!athleteId) {
      return
    }

    setIsSavingFeedback(true)
    setFeedbackError('')

    try {
      const created = await createCoachAthleteFeedback(athleteId, feedbackForm)
      setFeedback((current) => [created, ...current])
      setFeedbackForm({
        note: '',
        recommendation: '',
        status: 'Progressing',
      })
    } catch (submissionError) {
      setFeedbackError(submissionError instanceof Error ? submissionError.message : 'Unable to save coach feedback')
    } finally {
      setIsSavingFeedback(false)
    }
  }

  if (!isLoading && !user) {
    return <Navigate to="/signin" replace state={{ from: { pathname: `/coach/athletes/${athleteId ?? ''}` } }} />
  }

  if (!user) {
    return null
  }

  if (user.role !== 'coach') {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <section className="dashboard-shell">
      <div className="dashboard-container">
        <div className="dashboard-hero">
          <p className="dashboard-eyebrow">Athlete Review</p>
          <h1>{athlete?.athleteMaster.name ?? 'Athlete Profile'}</h1>
          <p>Review this student intake, spot weak areas quickly, and share coach observations back to the student dashboard.</p>
        </div>

        <div className="dashboard-links">
          <Link to="/dashboard">Dashboard</Link>
        </div>

        {isFetching ? <p className="dashboard-message">Loading athlete...</p> : null}
        {error ? <p className="dashboard-message dashboard-error">{error}</p> : null}

        {athlete ? (
          <div className="athlete-detail-layout">
            <aside className="athlete-summary-card">
              <p className="student-role">Overview</p>
              <h2>{athlete.athleteMaster.name}</h2>
              <dl className="student-meta">
                <div>
                  <dt>Email</dt>
                  <dd>{athlete.athleteMaster.email}</dd>
                </div>
                <div>
                  <dt>Academy ID</dt>
                  <dd>{athlete.athleteMaster.academyId}</dd>
                </div>
                <div>
                  <dt>Coach ID</dt>
                  <dd>{athlete.athleteMaster.coachId}</dd>
                </div>
                <div>
                  <dt>Gender</dt>
                  <dd>{athlete.athleteMaster.gender}</dd>
                </div>
                <div>
                  <dt>Created</dt>
                  <dd>{formatDate(athlete.athleteMaster.createdAt)}</dd>
                </div>
                <div>
                  <dt>Latest Session</dt>
                  <dd>{latestSession ? formatDate(latestSession.sessionDate) : 'Not added'}</dd>
                </div>
              </dl>
            </aside>

            <div className="athlete-detail-sections">
              <section className="athlete-detail-card">
                <h2>Weak Area Snapshot</h2>
                <p className="dashboard-footnote">A quick comparison of the latest intake against coach-friendly target bands.</p>
                {insightMetrics.length > 0 ? (
                  <div className="insight-metric-list">
                    {insightMetrics.map((metric) => (
                      <article key={metric.label} className="insight-metric-card">
                        <div className="insight-metric-header">
                          <strong>{metric.label}</strong>
                          <span>{metric.score}%</span>
                        </div>
                        <div className="insight-meter">
                          <div className="insight-meter-fill" style={{ width: `${metric.score}%` }} />
                          <div className="insight-meter-target" style={{ left: `${metric.target}%` }} />
                        </div>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="dashboard-footnote">Insight bars appear after physiology and psychology data are available.</p>
                )}
                {weakestAreas.length > 0 ? (
                  <div className="risk-chip-row">
                    {weakestAreas.map((area) => (
                      <span key={area.label} className="risk-chip">
                        {area.label}: {area.score}%
                      </span>
                    ))}
                  </div>
                ) : null}
              </section>

              <section className="athlete-detail-card">
                <h2>Coach Feedback</h2>
                <form className="coach-feedback-form" onSubmit={handleSubmitFeedback}>
                  <label>
                    <span>Status</span>
                    <select
                      value={feedbackForm.status}
                      onChange={(event) =>
                        setFeedbackForm((current) => ({
                          ...current,
                          status: event.target.value as CoachFeedbackRecord['status'],
                        }))
                      }
                    >
                      <option>Needs Attention</option>
                      <option>Progressing</option>
                      <option>Strong</option>
                    </select>
                  </label>
                  <label>
                    <span>Observation</span>
                    <textarea
                      value={feedbackForm.note}
                      onChange={(event) =>
                        setFeedbackForm((current) => ({ ...current, note: event.target.value }))
                      }
                      minLength={2}
                      maxLength={500}
                      required
                    />
                  </label>
                  <label>
                    <span>Recommendation</span>
                    <textarea
                      value={feedbackForm.recommendation}
                      onChange={(event) =>
                        setFeedbackForm((current) => ({
                          ...current,
                          recommendation: event.target.value,
                        }))
                      }
                      minLength={2}
                      maxLength={500}
                      required
                    />
                  </label>
                  {feedbackError ? <p className="dashboard-message dashboard-error">{feedbackError}</p> : null}
                  <button type="submit" className="dashboard-action-button" disabled={isSavingFeedback}>
                    {isSavingFeedback ? 'Saving feedback...' : 'Save Feedback'}
                  </button>
                </form>

                {feedback.length > 0 ? (
                  <div className="athlete-detail-list">
                    {feedback.map((item) => (
                      <article key={item.feedbackId} className="athlete-detail-row">
                        <strong>{item.status}</strong>
                        <span>{item.coachName} | {formatDate(item.createdAt)}</span>
                        <p>{item.note}</p>
                        <p><strong>Recommendation:</strong> {item.recommendation}</p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="dashboard-footnote">No feedback has been saved for this athlete yet.</p>
                )}
              </section>

              <section className="athlete-detail-card">
                <h2>Athlete Master</h2>
                <dl className="student-meta">
                  <div><dt>Age</dt><dd>{athlete.athleteMaster.age}</dd></div>
                  <div><dt>Height</dt><dd>{athlete.athleteMaster.heightCm} cm</dd></div>
                  <div><dt>Weight</dt><dd>{athlete.athleteMaster.weightKg} kg</dd></div>
                  <div><dt>Contact Number</dt><dd>{athlete.athleteMaster.contactNumber}</dd></div>
                </dl>
              </section>

              <section className="athlete-detail-card">
                <h2>Family Details</h2>
                {athlete.familyDetails ? (
                  <dl className="student-meta">
                    <div><dt>Mother Name</dt><dd>{athlete.familyDetails.motherName}</dd></div>
                    <div><dt>Father Name</dt><dd>{athlete.familyDetails.fatherName}</dd></div>
                    <div><dt>Mother Occupation</dt><dd>{athlete.familyDetails.motherOccupation}</dd></div>
                    <div><dt>Father Occupation</dt><dd>{athlete.familyDetails.fatherOccupation}</dd></div>
                    <div><dt>Education Level</dt><dd>{athlete.familyDetails.educationLevel}</dd></div>
                    <div><dt>Sibling Details</dt><dd>{athlete.familyDetails.siblingDetails}</dd></div>
                    <div><dt>Family Conservative</dt><dd>{athlete.familyDetails.familyConservative}</dd></div>
                    <div><dt>Discipline Level</dt><dd>{athlete.familyDetails.disciplineLevel}</dd></div>
                    <div><dt>Health Conditions</dt><dd>{athlete.familyDetails.healthConditions}</dd></div>
                    <div><dt>Father Contact</dt><dd>{athlete.familyDetails.fatherContactNumber}</dd></div>
                    <div><dt>Mother Contact</dt><dd>{athlete.familyDetails.motherContactNumber}</dd></div>
                    <div><dt>Parent Email</dt><dd>{athlete.familyDetails.parentEmail}</dd></div>
                    <div><dt>Comments</dt><dd>{athlete.familyDetails.comments}</dd></div>
                  </dl>
                ) : (
                  <p className="dashboard-footnote">Not added.</p>
                )}
              </section>

              <section className="athlete-detail-card">
                <h2>Athlete Profile</h2>
                {athlete.athleteProfile ? (
                  <dl className="student-meta">
                    <div><dt>Class</dt><dd>{athlete.athleteProfile.class}</dd></div>
                    <div><dt>School Name</dt><dd>{athlete.athleteProfile.schoolName}</dd></div>
                    <div><dt>Diet Type</dt><dd>{athlete.athleteProfile.dietType}</dd></div>
                    <div><dt>Outside Food</dt><dd>{athlete.athleteProfile.outsideFoodFrequency}</dd></div>
                    <div><dt>Sleep Time</dt><dd>{athlete.athleteProfile.sleepTime}</dd></div>
                    <div><dt>Wake Time</dt><dd>{athlete.athleteProfile.wakeTime}</dd></div>
                    <div><dt>Friend Circle</dt><dd>{athlete.athleteProfile.friendCircle}</dd></div>
                    <div><dt>Anger Pattern</dt><dd>{athlete.athleteProfile.angerPattern}</dd></div>
                    <div><dt>Sadness Pattern</dt><dd>{athlete.athleteProfile.sadnessPattern}</dd></div>
                    <div><dt>Academic Performance</dt><dd>{athlete.athleteProfile.academicPerformance}</dd></div>
                    <div><dt>Reason for Shooting</dt><dd>{athlete.athleteProfile.reasonForShooting}</dd></div>
                    <div><dt>Athlete Goal</dt><dd>{athlete.athleteProfile.athleteGoal}</dd></div>
                  </dl>
                ) : (
                  <p className="dashboard-footnote">Not added.</p>
                )}
              </section>

              <section className="athlete-detail-card">
                <h2>Sessions Log</h2>
                {athlete.sessionsLog.length > 0 ? (
                  <div className="athlete-detail-list">
                    {athlete.sessionsLog.map((session) => (
                      <article key={session.sessionId} className="athlete-detail-row">
                        <strong>{formatDate(session.sessionDate)}</strong>
                        <span>{session.trainingType} at {session.location}</span>
                        <p>{session.startTime} - {session.endTime} ({session.durationMinutes} mins)</p>
                        <p>{session.notes}</p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="dashboard-footnote">Not added.</p>
                )}
              </section>

              <section className="athlete-detail-card">
                <h2>Physiology Data</h2>
                {athlete.physiologyData.length > 0 ? (
                  <div className="athlete-detail-list">
                    {athlete.physiologyData.map((record) => (
                      <article key={record.physiologyId} className="athlete-detail-row">
                        <strong>{formatDate(record.recordedDate)}</strong>
                        <span>SpO2 {record.spo2} | Resting HR {record.restingHeartRate} | Avg HR {record.avgHeartRate}</span>
                        <p>Sleep {record.sleepHours} hrs | Recovery {record.recoveryScore} | Stress {record.stressScore} | Fatigue {record.fatigueLevel}</p>
                        <p>{record.remarks}</p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="dashboard-footnote">Not added.</p>
                )}
              </section>

              <section className="athlete-detail-card">
                <h2>Psychology Responses</h2>
                {athlete.psychologyResponses.length > 0 ? (
                  <div className="athlete-detail-list">
                    {athlete.psychologyResponses.map((response) => (
                      <article key={response.answerId} className="athlete-detail-row">
                        <strong>{response.questionText}</strong>
                        <span>{response.category} | {response.questionType} | {formatDate(response.recordedAt)}</span>
                        {response.answerScore ? <p>Score: {response.answerScore}/10</p> : null}
                        <p>{response.answerText}</p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="dashboard-footnote">Not added.</p>
                )}
              </section>
            </div>
          </div>
        ) : null}
      </div>
    </section>
  )
}

export default CoachAthleteDetailsPage
