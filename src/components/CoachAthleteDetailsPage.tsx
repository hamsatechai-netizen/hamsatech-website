import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  createCoachAthleteFeedback,
  getCoachAthleteInsightsWidget,
  getCoachAthleteProfileWidget,
  getCoachAthleteSessionsWidget,
  getCoachAthleteWidget,
  type CoachAthleteInsightsWidget,
  type CoachAthleteProfileWidget,
  type CoachAthleteSessionsWidget,
  type CoachAthleteWidget,
} from '../lib/authApi'
import '../styles/Dashboard.css'

function formatScore(value?: number | null) {
  return typeof value === 'number' ? Math.round(value) : '-'
}

function formatDate(value?: string | null) {
  if (!value) return 'N/A'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return 'N/A'
  return new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(parsed)
}

function scoreCategory(value?: number | null) {
  if (typeof value !== 'number') return 'Pending'
  if (value >= 80) return 'Strong'
  if (value >= 60) return 'Good'
  if (value >= 45) return 'Moderate'
  return 'Low'
}

function trendFromHistory(history?: CoachAthleteSessionsWidget['history']) {
  const values = (history ?? []).map((item) => item.performance).filter((value): value is number => typeof value === 'number')
  if (values.length < 2) return 'Stable'
  const delta = values[0] - values[values.length - 1]
  if (delta >= 5) return 'Improving'
  if (delta <= -5) return 'Declining'
  return 'Stable'
}

function ScoreCard({ label, value, previous, source }: { label: string; value?: number | null; previous?: number | null; source: string }) {
  const delta = typeof value === 'number' && typeof previous === 'number' ? value - previous : null
  const trend = delta === null ? 'Stable' : delta >= 3 ? 'Improving' : delta <= -3 ? 'Declining' : 'Stable'
  return (
    <article className="athlete-score-card">
      <div>
        <span>{label}</span>
        <strong>{formatScore(value)}</strong>
      </div>
      <p>{scoreCategory(value)} / {trend}</p>
      <small>{source}</small>
    </article>
  )
}

function MetricTile({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div className="dashboard-metric">
      <span>{label}</span>
      <strong>{typeof value === 'number' ? formatScore(value) : value ?? '-'}</strong>
    </div>
  )
}

function CoachAthleteDetailsPage() {
  const { athleteId } = useParams()
  const { user, isLoading } = useAuth()
  const [widget, setWidget] = useState<CoachAthleteWidget | null>(null)
  const [sessionsWidget, setSessionsWidget] = useState<CoachAthleteSessionsWidget | null>(null)
  const [insightsWidget, setInsightsWidget] = useState<CoachAthleteInsightsWidget | null>(null)
  const [profileWidget, setProfileWidget] = useState<CoachAthleteProfileWidget | null>(null)
  const [feedbackNote, setFeedbackNote] = useState('')
  const [recommendation, setRecommendation] = useState('')
  const [feedbackStatus, setFeedbackStatus] = useState<'Needs Attention' | 'Progressing' | 'Strong'>('Progressing')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isFetching, setIsFetching] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  const loadWidget = useMemo(() => async () => {
    if (!user || user.role !== 'coach' || !athleteId) return
    setIsFetching(true)
    setError('')

    try {
      const [widgetSnapshot, sessionsSnapshot, insightsSnapshot, profileSnapshot] = await Promise.all([
        getCoachAthleteWidget(athleteId),
        getCoachAthleteSessionsWidget(athleteId),
        getCoachAthleteInsightsWidget(athleteId),
        getCoachAthleteProfileWidget(athleteId),
      ])
      setWidget(widgetSnapshot)
      setSessionsWidget(sessionsSnapshot)
      setInsightsWidget(insightsSnapshot)
      setProfileWidget(profileSnapshot)
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : 'Unable to load athlete details')
    } finally {
      setIsFetching(false)
    }
  }, [athleteId, user])

  useEffect(() => { void loadWidget() }, [loadWidget])

  const athleteName = profileWidget?.name ?? (widget?.athleteId ? `Athlete ${widget.athleteId}` : 'Athlete Dashboard')
  const trend = trendFromHistory(sessionsWidget?.history)
  const lastSession = sessionsWidget?.lastSession
  const previousSession = sessionsWidget?.history?.[1]
  const insightCards = [
    {
      title: widget?.fatigue && widget.fatigue >= 70 ? 'Fatigue is affecting readiness' : 'Readiness pattern',
      text: widget?.fatigue && widget.fatigue >= 70
        ? 'Performance may drop when fatigue is elevated. Reduce session load and check sleep/recovery.'
        : 'Readiness and performance are currently stable enough for normal training load.',
      priority: widget?.fatigue && widget.fatigue >= 70 ? 'High' : 'Medium',
    },
    {
      title: (insightsWidget?.scores?.focus ?? 0) >= 70 ? 'Focus is a strength' : 'Focus needs support',
      text: (insightsWidget?.scores?.focus ?? 0) >= 70
        ? 'Focus score is strong. Preserve pre-shot routine and avoid unnecessary technical changes.'
        : 'Add one short attention drill before the next live session.',
      priority: (insightsWidget?.scores?.focus ?? 0) >= 70 ? 'Low' : 'Medium',
    },
    {
      title: trend === 'Declining' ? 'Performance trend is declining' : 'Performance trend',
      text: trend === 'Declining'
        ? 'Review the latest session reflection and identify whether the driver is technical, physical, or mental.'
        : `Recent sessions are ${trend.toLowerCase()}. Keep tracking fatigue, stress, and recovery before changing plan.`,
      priority: trend === 'Declining' ? 'High' : 'Low',
    },
  ]

  const handleFeedback = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!athleteId || feedbackNote.trim().length < 2 || recommendation.trim().length < 2) return
    setIsSaving(true)
    setMessage('')
    setError('')
    try {
      await createCoachAthleteFeedback(athleteId, {
        note: feedbackNote.trim(),
        recommendation: recommendation.trim(),
        status: feedbackStatus,
      })
      setFeedbackNote('')
      setRecommendation('')
      setFeedbackStatus('Progressing')
      setMessage('Feedback saved.')
      await loadWidget()
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : 'Unable to save feedback')
    } finally {
      setIsSaving(false)
    }
  }

  if (!isLoading && !user) {
    return <Navigate to="/signin" replace state={{ from: { pathname: `/coach/athletes/${athleteId ?? ''}` } }} />
  }

  if (!user) return null
  if (user.role !== 'coach') return <Navigate to="/dashboard" replace />

  return (
    <section className="dashboard-shell">
      <div className="dashboard-container">
        <div className="dashboard-hero">
          <p className="dashboard-eyebrow">Athlete Detail Dashboard</p>
          <h1>{athleteName}</h1>
          <p>Understand the full performance story: scores, readiness, fatigue, focus, training plan, insights, and coach feedback.</p>
        </div>

        <div className="dashboard-links">
          <Link to="/coach/dashboard">Dashboard</Link>
        </div>

        {isFetching ? <p className="dashboard-message">Loading athlete...</p> : null}
        {error ? <p className="dashboard-message dashboard-error">{error}</p> : null}
        {message ? <p className="dashboard-message dashboard-success">{message}</p> : null}

        <section className="dashboard-section">
          <h2>Athlete Summary</h2>
          <div className="coach-overview-grid">
            <article className="coach-stat-tile"><span>Age / Gender</span><strong>{profileWidget?.age ?? '-'} / {profileWidget?.gender ?? '-'}</strong></article>
            <article className="coach-stat-tile"><span>Sport / Discipline</span><strong>{profileWidget?.sport ?? '-'}</strong></article>
            <article className="coach-stat-tile"><span>Coach</span><strong>{profileWidget?.coachName ?? profileWidget?.coachId ?? '-'}</strong></article>
            <article className="coach-stat-tile"><span>Status</span><strong>{profileWidget?.currentStatus ?? '-'}</strong></article>
            <article className="coach-stat-tile"><span>Performance</span><strong>{formatScore(widget?.performance)}</strong></article>
            <article className="coach-stat-tile"><span>Readiness</span><strong>{formatScore(widget?.readiness)}</strong></article>
            <article className="coach-stat-tile"><span>Fatigue</span><strong>{formatScore(widget?.fatigue)}</strong></article>
            <article className="coach-stat-tile"><span>Focus</span><strong>{formatScore(insightsWidget?.scores?.focus)}</strong></article>
            <article className="coach-stat-tile"><span>Latest Session</span><strong>{formatDate(lastSession?.sessionDate)}</strong></article>
            <article className="coach-stat-tile"><span>Trend</span><strong>{trend}</strong></article>
          </div>
        </section>

        <section className="dashboard-section">
          <h2>Performance Summary</h2>
          <div className="athlete-detail-card">
            <div className="performance-line">
              {(sessionsWidget?.history ?? []).slice(0, 8).reverse().map((item) => (
                <span key={item.sessionId} style={{ height: `${Math.max(8, item.performance ?? 0)}%` }} title={`${formatDate(item.sessionDate)}: ${formatScore(item.performance)}`} />
              ))}
            </div>
            <div className="dashboard-metrics">
              <div className="dashboard-metric"><span>Latest session score</span><strong>{formatScore(lastSession?.performance)}</strong></div>
              <div className="dashboard-metric"><span>7-day average</span><strong>{formatScore(profileWidget?.scores?.avg7d)}</strong></div>
              <div className="dashboard-metric"><span>Best 30d average</span><strong>{formatScore(profileWidget?.scores?.bestAvg30d)}</strong></div>
              <div className="dashboard-metric"><span>Best score</span><strong>{formatScore(profileWidget?.scores?.bestScore)}</strong></div>
              <div className="dashboard-metric"><span>Best series</span><strong>{formatScore(profileWidget?.scores?.bestSeries)}</strong></div>
              <div className="dashboard-metric"><span>Improvement rate</span><strong>{formatScore(profileWidget?.scores?.improvementRate)}</strong></div>
              <div className="dashboard-metric"><span>Session frequency</span><strong>{sessionsWidget?.history?.length ?? 0}</strong></div>
              <div className="dashboard-metric"><span>Best vs latest</span><strong>{formatScore((profileWidget?.scores?.bestScore ?? 0) - (lastSession?.performance ?? 0))}</strong></div>
            </div>
          </div>
        </section>

        <section className="dashboard-section">
          <h2>Derived Score Breakdown</h2>
          <div className="athlete-score-grid">
            <ScoreCard label="Overall Performance" value={widget?.performance} previous={previousSession?.performance} source="Session summary and score records" />
            <ScoreCard label="Readiness" value={widget?.readiness} previous={previousSession?.readiness} source="Recovery, stress, sleep, and physiology" />
            <ScoreCard label="Focus" value={insightsWidget?.scores?.focus} source="Psychology responses" />
            <ScoreCard label="Discipline" value={profileWidget?.scores?.periodAvg} source="Session frequency and consistency" />
            <ScoreCard label="Recovery" value={profileWidget?.psychology?.recovery} source="Physiology and psychology scores" />
            <ScoreCard label="Fatigue Load" value={widget?.fatigue} previous={previousSession?.fatigue} source="Fatigue level and session load" />
            <ScoreCard label="Stress Control" value={widget?.fatigue ? Math.max(0, 100 - widget.fatigue) : null} source="Stress and fatigue readiness signals" />
            <ScoreCard label="Mental Resilience" value={insightsWidget?.scores?.focus} source="Focus, reflection, and mental score breakdown" />
            <ScoreCard label="Consistency" value={profileWidget?.scores?.periodAvg} source="Session history and scoring stability" />
            <ScoreCard label="Decision Making" value={insightsWidget?.scores?.decision} source="Mental score breakdown" />
            <ScoreCard label="Arousal Control" value={insightsWidget?.scores?.arousal} source="Mental score breakdown" />
            <ScoreCard label="Social Support" value={insightsWidget?.scores?.social} source="Environment and support signals" />
          </div>
        </section>

        <section className="dashboard-section">
          <h2>Health and Readiness Mapping</h2>
          <div className="coach-map-grid">
            <article className="coach-map-card"><strong>Performance vs Fatigue</strong><p>{formatScore(widget?.performance)} performance / {formatScore(widget?.fatigue)} fatigue</p></article>
            <article className="coach-map-card"><strong>Readiness vs Performance</strong><p>{formatScore(widget?.readiness)} readiness / {formatScore(widget?.performance)} performance</p></article>
            <article className="coach-map-card"><strong>Focus vs Consistency</strong><p>{formatScore(insightsWidget?.scores?.focus)} focus / {formatScore(profileWidget?.scores?.periodAvg)} period average</p></article>
            <article className="coach-map-card"><strong>Mental Load</strong><p>{formatScore(insightsWidget?.scores?.arousal)} arousal / {formatScore(insightsWidget?.scores?.decision)} decision</p></article>
            <article className="coach-map-card"><strong>Stress and Recovery</strong><p>{formatScore(profileWidget?.physiology?.stress)} stress / {formatScore(profileWidget?.physiology?.recovery)} recovery</p></article>
            <article className="coach-map-card"><strong>HR and HRV</strong><p>{formatScore(profileWidget?.physiology?.restingHr)} resting HR / {formatScore(profileWidget?.physiology?.hrv)} HRV</p></article>
            <article className="coach-map-card"><strong>Sleep and Energy</strong><p>{profileWidget?.physiology?.sleepHours ?? '-'}h sleep / {formatScore(profileWidget?.physiology?.energyLevel)} energy</p></article>
            <article className="coach-map-card"><strong>Mood Check-in</strong><p>{profileWidget?.physiology?.mood ?? 'No check-in mood recorded'}</p></article>
          </div>
        </section>

        <section className="dashboard-section">
          <h2>Physiology Panel</h2>
          <div className="dashboard-panel">
            <div className="dashboard-metrics">
              <MetricTile label="Avg HR" value={profileWidget?.physiology?.avgHr} />
              <MetricTile label="Min HR" value={profileWidget?.physiology?.minHr} />
              <MetricTile label="Max HR" value={profileWidget?.physiology?.maxHr} />
              <MetricTile label="RMSSD / HRV" value={profileWidget?.physiology?.hrv} />
              <MetricTile label="HR Std Dev" value={profileWidget?.physiology?.hrStdDev} />
              <MetricTile label="Sleep Hours" value={profileWidget?.physiology?.sleepHours} />
            </div>
            <div className="zone-strip" aria-label="Heart rate zones">
              {(profileWidget?.physiology?.zones ?? [0, 0, 0, 0, 0]).map((zone, index) => (
                <span key={index} style={{ flexGrow: Math.max(1, zone) }}>Z{index + 1}: {zone}</span>
              ))}
            </div>
          </div>
        </section>

        <section className="dashboard-section">
          <h2>Hold Stability</h2>
          <div className="dashboard-metrics">
            <MetricTile label="Stability Score" value={profileWidget?.holdStability?.stabilityScore} />
            <MetricTile label="Hold Stability" value={profileWidget?.holdStability?.holdStability} />
            <MetricTile label="Settle Score" value={profileWidget?.holdStability?.settleScore} />
            <MetricTile label="Spike Count" value={profileWidget?.holdStability?.spikeCount} />
          </div>
        </section>

        <section className="dashboard-section">
          <h2>Training Plan</h2>
          <div className="dashboard-panel">
            <p className="dashboard-panel-title">{widget?.nextFocus ? `Focus area: ${widget.nextFocus}` : 'Focus area: Needs review'}</p>
            <p className="dashboard-message">{profileWidget?.trainingPlan || insightsWidget?.recommendation || 'Review weakest score, latest reflection, fatigue, and recovery before assigning the next training block.'}</p>
            <div className="risk-chip-row">
              <span className="risk-chip risk-chip--progressing">Plan Status: {profileWidget?.trainingPlanStatus ?? 'Needs Review'}</span>
              <span className="risk-chip">Session frequency: {sessionsWidget?.history?.length ?? 0}</span>
              <span className="risk-chip">Trend: {trend}</span>
            </div>
          </div>
        </section>

        <section className="dashboard-section">
          <h2>Insights</h2>
          <div className="notification-list">
            {[...insightCards, ...(insightsWidget?.insights ?? []).map((item) => ({
              title: item.title ?? 'Insight',
              text: `${item.insightText ?? ''}${item.suggestedAction ? ` Suggested action: ${item.suggestedAction}` : ''}`,
              priority: item.priority ?? 'Medium',
              category: item.category ?? 'coach',
            }))].map((item) => (
              <article key={item.title} className="notification-item">
                <span>{item.priority} Priority{'category' in item ? ` / ${item.category}` : ''}</span>
                <p><strong>{item.title}</strong> - {'text' in item ? item.text : ''}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="dashboard-section">
          <h2>Session History</h2>
          <div className="dashboard-empty-card coach-v1-table-wrap">
            <table className="coach-v1-table">
              <thead>
                <tr><th align="left">Date</th><th align="left">Type</th><th align="left">Score</th><th align="left">Best Series</th><th align="left">Avg HR</th><th align="left">Fatigue</th><th align="left">Recovery</th><th align="left">Reflection</th><th align="left">Coach Notes</th></tr>
              </thead>
              <tbody>
                {(sessionsWidget?.history ?? []).map((session) => (
                  <tr key={session.sessionId}>
                    <td>{formatDate(session.sessionDate)}</td>
                    <td>{session.trainingType ?? '-'}</td>
                    <td>{formatScore(session.performance)}</td>
                    <td>{formatScore(session.bestSeries)}</td>
                    <td>{formatScore(session.avgHr)}</td>
                    <td>{formatScore(session.fatigue)}</td>
                    <td>{formatScore(session.recovery)}</td>
                    <td>{session.reflection || lastSession?.summaryTitle || 'Review session notes'}</td>
                    <td>{session.coachNotes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="dashboard-section">
          <h2>Coach Feedback</h2>
          <div className="athlete-detail-card">
            <form className="coach-feedback-form" onSubmit={handleFeedback}>
              <label>
                <span>Status</span>
                <select value={feedbackStatus} onChange={(event) => setFeedbackStatus(event.target.value as typeof feedbackStatus)}>
                  <option value="Progressing">Progressing</option>
                  <option value="Strong">Strong</option>
                  <option value="Needs Attention">Needs Attention</option>
                </select>
              </label>
              <label>
                <span>Feedback</span>
                <textarea value={feedbackNote} onChange={(event) => setFeedbackNote(event.target.value)} placeholder="What should the athlete understand from this review?" />
              </label>
              <label>
                <span>Recommendation</span>
                <textarea value={recommendation} onChange={(event) => setRecommendation(event.target.value)} placeholder="Next training action, drill, recovery instruction, or mental note" />
              </label>
              <button className="dashboard-action-button" disabled={isSaving} type="submit">{isSaving ? 'Saving...' : 'Save Feedback'}</button>
            </form>
            <div className="athlete-detail-list">
              {(profileWidget?.feedbackHistory ?? insightsWidget?.feedbackHistory ?? []).slice(0, 8).map((item, index) => (
                <article key={`${item.createdAt}-${index}`} className="athlete-detail-row">
                  <strong>{item.status ?? 'Feedback'}</strong>
                  <span>{formatDate(item.createdAt)}</span>
                  <p>{item.note || item.trainingPlan || 'No details recorded.'}</p>
                  {item.trainingPlan ? <p>{item.trainingPlan}</p> : null}
                </article>
              ))}
            </div>
          </div>
        </section>
      </div>
    </section>
  )
}

export default CoachAthleteDetailsPage
