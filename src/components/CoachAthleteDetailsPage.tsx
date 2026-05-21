import { useEffect, useState } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
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

function CoachAthleteDetailsPage() {
  const { athleteId } = useParams()
  const { user, isLoading } = useAuth()
  const [widget, setWidget] = useState<CoachAthleteWidget | null>(null)
  const [sessionsWidget, setSessionsWidget] = useState<CoachAthleteSessionsWidget | null>(null)
  const [insightsWidget, setInsightsWidget] = useState<CoachAthleteInsightsWidget | null>(null)
  const [profileWidget, setProfileWidget] = useState<CoachAthleteProfileWidget | null>(null)
  const [error, setError] = useState('')
  const [isFetching, setIsFetching] = useState(false)

  useEffect(() => {
    if (!user || user.role !== 'coach' || !athleteId) {
      return
    }

    const loadWidget = async () => {
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
    }

    void loadWidget()
  }, [athleteId, user])

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
          <h1>{widget?.athleteId ? `Athlete ${widget.athleteId}` : 'Athlete Dashboard'}</h1>
          <p>Calculated snapshot from derived scores and session summaries.</p>
        </div>

        <div className="dashboard-links">
          <Link to="/coach/dashboard">Dashboard</Link>
        </div>

        {isFetching ? <p className="dashboard-message">Loading athlete...</p> : null}
        {error ? <p className="dashboard-message dashboard-error">{error}</p> : null}

        {widget ? (
          <div className="dashboard-panel" style={{ marginTop: 18 }}>
            <p className="dashboard-panel-title">Athlete Home</p>
            <div className="dashboard-metrics">
              <div className="dashboard-metric">
                <span>Readiness</span>
                <strong>{widget.readiness ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Performance</span>
                <strong>{widget.performance ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Fatigue</span>
                <strong>{widget.fatigue ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Next Focus</span>
                <strong>{widget.nextFocus ?? '-'}</strong>
              </div>
            </div>
          </div>
        ) : null}

        {sessionsWidget?.lastSession ? (
          <div className="dashboard-panel" style={{ marginTop: 18 }}>
            <p className="dashboard-panel-title">Sessions</p>
            <div className="dashboard-metrics">
              <div className="dashboard-metric">
                <span>Performance</span>
                <strong>{sessionsWidget.lastSession.performance ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Readiness</span>
                <strong>{sessionsWidget.lastSession.readiness ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Hold stability</span>
                <strong>{sessionsWidget.lastSession.holdStability ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Mental score</span>
                <strong>{sessionsWidget.lastSession.mentalScore ?? '-'}</strong>
              </div>
            </div>
          </div>
        ) : null}

        {insightsWidget ? (
          <div className="dashboard-panel" style={{ marginTop: 18 }}>
            <p className="dashboard-panel-title">Insights</p>
            <div className="dashboard-metrics">
              <div className="dashboard-metric">
                <span>Social</span>
                <strong>{insightsWidget.scores?.social ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Arousal</span>
                <strong>{insightsWidget.scores?.arousal ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Decision</span>
                <strong>{insightsWidget.scores?.decision ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Focus</span>
                <strong>{insightsWidget.scores?.focus ?? '-'}</strong>
              </div>
            </div>
            {insightsWidget.recommendation ? (
              <p className="dashboard-message" style={{ marginTop: 12 }}>
                {insightsWidget.recommendation}
              </p>
            ) : null}
          </div>
        ) : null}

        {profileWidget ? (
          <div className="dashboard-panel" style={{ marginTop: 18 }}>
            <p className="dashboard-panel-title">Profile</p>
            <div className="dashboard-metrics">
              <div className="dashboard-metric">
                <span>Best avg (30d)</span>
                <strong>{profileWidget.scores?.bestAvg30d ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Period avg</span>
                <strong>{profileWidget.scores?.periodAvg ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Best series</span>
                <strong>{profileWidget.scores?.bestSeries ?? '-'}</strong>
              </div>
              <div className="dashboard-metric">
                <span>Last session</span>
                <strong>{profileWidget.scores?.lastSession ?? '-'}</strong>
              </div>
            </div>
            {profileWidget.trainingPlan ? (
              <p className="dashboard-message" style={{ marginTop: 12 }}>
                Training plan: {profileWidget.trainingPlan}
              </p>
            ) : null}
            {profileWidget.feedbackHistory && profileWidget.feedbackHistory.length > 0 ? (
              <div style={{ marginTop: 12 }}>
                <p className="dashboard-panel-title" style={{ marginBottom: 8 }}>Coach Feedback</p>
                {profileWidget.feedbackHistory.slice(0, 5).map((item, index) => (
                  <p key={index} className="dashboard-message" style={{ margin: '6px 0' }}>
                    {item.status ? `${item.status}: ` : ''}{item.note || item.trainingPlan || ''}
                  </p>
                ))}
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </section>
  )
}

export default CoachAthleteDetailsPage
