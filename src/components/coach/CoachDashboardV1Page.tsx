import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { getCoachDashboardV1, getCoachProfile, type CoachDashboardV1, type CoachDashboardV1Athlete } from '../../lib/authApi'
import '../../styles/Dashboard.css'

function formatDate(value?: string | null) {
  if (!value) return 'N/A'
  return new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value))
}

function scoreTone(score?: number | null) {
  if (typeof score !== 'number') return 'pending'
  if (score >= 75) return 'elite'
  if (score >= 50) return 'functional'
  return 'risk'
}

function notifyCoachIntent(message: string) {
  const fn = (window as Window & { sendPrompt?: (value: string) => void }).sendPrompt
  if (typeof fn === 'function') fn(message)
}

export default function CoachDashboardV1Page() {
  const { user, isLoading } = useAuth()
  const [dashboard, setDashboard] = useState<CoachDashboardV1 | null>(null)
  const [coachId, setCoachId] = useState('')
  const [gender, setGender] = useState('all')
  const [minScore, setMinScore] = useState('')
  const [isFetching, setIsFetching] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    if (!user || user.role !== 'coach') return
    setIsFetching(true)
    setError('')
    try {
      const profile = await getCoachProfile()
      setCoachId(profile.coachId)
      const data = await getCoachDashboardV1(profile.coachId, {
        gender: gender === 'all' ? undefined : gender,
        minScore: minScore ? Number(minScore) : undefined,
      })
      setDashboard(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load dashboard')
    } finally {
      setIsFetching(false)
    }
  }, [gender, minScore, user])

  useEffect(() => { void load() }, [load])

  const topAthletes = useMemo(() => {
    const rows = [...(dashboard?.athletes ?? [])]
    rows.sort((a, b) => (b.score ?? -1) - (a.score ?? -1))
    return rows.slice(0, 5)
  }, [dashboard])

  const lowAthletes = useMemo(() => {
    const rows = (dashboard?.athletes ?? []).filter((item) => typeof item.score === 'number')
    rows.sort((a, b) => (a.score ?? 0) - (b.score ?? 0))
    return rows.slice(0, 5)
  }, [dashboard])

  if (!isLoading && !user) return <Navigate to="/coach/login" replace />
  if (!isLoading && user?.role !== 'coach') return <Navigate to="/coach/login" replace />

  return (
    <section className="dashboard-shell coach-visual-theme">
      <div className="dashboard-container">
        <div className="dashboard-hero coach-v1-hero">
          <p className="dashboard-eyebrow">Coach Dashboard</p>
          <h1>Performance Overview</h1>
          <p>Single-source backend metrics synced for web and mobile.</p>
        </div>

        <section className="dashboard-section">
          <div className="dashboard-filter-row">
            <label>
              <span>Gender</span>
              <select value={gender} onChange={(e) => setGender(e.target.value)}>
                <option value="all">All</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </label>
            <label>
              <span>Min Score</span>
              <input value={minScore} onChange={(e) => setMinScore(e.target.value)} placeholder="e.g. 60" />
            </label>
            <button className="dashboard-inline-link" type="button" onClick={() => void load()}>
              Apply
            </button>
          </div>
        </section>

        {error ? <p className="dashboard-message dashboard-error">{error}</p> : null}
        {isFetching ? <p className="dashboard-message">Loading dashboard...</p> : null}

        {dashboard ? (
          <>
            <section className="dashboard-section">
              <h2>Team Overview</h2>
              <div className="coach-overview-grid coach-overview-grid-v1">
                <article className="coach-stat-tile"><span>Athletes</span><strong>{dashboard.totals.totalAssignedAthletes}</strong></article>
                <article className="coach-stat-tile"><span>Sessions</span><strong>{dashboard.totals.newRegistrations}</strong></article>
                <article className="coach-stat-tile"><span>Feedback</span><strong>{dashboard.athletes.filter((item) => typeof item.score === 'number').length}</strong></article>
                <article className="coach-stat-tile"><span>Avg Score</span><strong>{dashboard.averageScore ?? '-'}</strong></article>
              </div>
            </section>

            <section className="dashboard-section">
              <h2>Score Distribution</h2>
              <div className="score-chart-grid">
                {Object.entries(dashboard.scoreDistribution).map(([label, value]) => (
                  <article key={label} className="score-bar-card">
                    <span>{label}</span>
                    <div className="score-bar-track"><div className="score-bar-fill" style={{ width: `${Math.min(100, value * 20)}%` }} /></div>
                    <strong>{value}</strong>
                  </article>
                ))}
              </div>
            </section>

            <section className="dashboard-section">
              <h2>Athletes</h2>
              <div className="dashboard-empty-card coach-v1-table-wrap">
                <table className="coach-v1-table">
                  <thead>
                    <tr>
                      <th align="left">Athlete</th><th align="left">Psych Score</th><th align="left">Band</th><th align="left">Stress</th><th align="left">Recovery</th><th align="left">Last Session</th><th align="left">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboard.athletes.map((athlete: CoachDashboardV1Athlete) => (
                      <tr
                        key={athlete.athleteId}
                        className="coach-v1-row"
                        onMouseEnter={() => notifyCoachIntent(`Review athlete ${athlete.athleteName}`)}
                      >
                        <td>{athlete.athleteName}</td>
                        <td><span className={`score-pill score-pill--${scoreTone(athlete.score)}`}>{athlete.score ?? '-'}</span></td>
                        <td>{athlete.scoreCategory}</td>
                        <td className={(athlete.latestStress ?? 0) >= 65 ? 'coach-v1-alert-cell' : ''}>{athlete.latestStress ?? '-'}</td>
                        <td>{athlete.latestRecovery ?? '-'}</td>
                        <td>{formatDate(athlete.lastSessionDate)}</td>
                        <td><Link to={`/coach/athletes/${athlete.athleteId}`} onClick={() => notifyCoachIntent(`Open profile ${athlete.athleteName}`)}>View</Link></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="dashboard-section">
              <h2>Top / Needs Attention</h2>
              <div className="coach-status-bands">
                <div className="coach-status-band coach-status-band--strong">
                  <span className="coach-status-band-label">Top Athletes</span>
                  <div className="risk-chip-row">{topAthletes.map((a) => <span key={a.athleteId} className="risk-chip risk-chip--strong">{a.athleteName} {a.score ?? '-'}</span>)}</div>
                </div>
                <div className="coach-status-band coach-status-band--attention">
                  <span className="coach-status-band-label">Needs Attention</span>
                  <div className="risk-chip-row">{lowAthletes.map((a) => <span key={a.athleteId} className="risk-chip risk-chip--attention">{a.athleteName} {a.score ?? '-'}</span>)}</div>
                </div>
              </div>
            </section>

            {dashboard.alerts.length > 0 ? (
              <section className="dashboard-section">
                <h2>Alerts</h2>
                <div className="dashboard-empty-card"><ul className="coach-v1-alert-list">{dashboard.alerts.map((alert) => <li key={alert}>{alert}</li>)}</ul></div>
              </section>
            ) : null}
          </>
        ) : null}

        {coachId ? <input type="hidden" value={coachId} readOnly /> : null}
      </div>
    </section>
  )
}
