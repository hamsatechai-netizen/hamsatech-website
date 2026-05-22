import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { getCoachDashboardV1, getCoachProfile, type CoachDashboardV1, type CoachDashboardV1Athlete } from '../../lib/authApi'
import '../../styles/Dashboard.css'

type SortKey = 'performance' | 'readiness' | 'fatigue' | 'stress' | 'consistency'

function formatDate(value?: string | null) {
  if (!value) return 'N/A'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return 'N/A'
  return new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(parsed)
}

function formatScore(value?: number | null) {
  return typeof value === 'number' ? Math.round(value) : '-'
}

function scoreTone(score?: number | null) {
  if (typeof score !== 'number') return 'pending'
  if (score >= 75) return 'elite'
  if (score >= 50) return 'functional'
  return 'risk'
}

function statusTone(status: CoachDashboardV1Athlete['status']) {
  if (status === 'Strong') return 'strong'
  if (status === 'At Risk') return 'attention'
  if (status === 'Needs Attention') return 'risk'
  return 'progressing'
}

function sortValue(athlete: CoachDashboardV1Athlete, key: SortKey) {
  if (key === 'performance') return athlete.score ?? -1
  if (key === 'readiness') return athlete.readinessScore ?? -1
  if (key === 'fatigue') return athlete.fatigueScore ?? -1
  if (key === 'stress') return athlete.latestStress ?? -1
  return athlete.disciplineScore ?? -1
}

function notifyCoachIntent(message: string) {
  const fn = (window as Window & { sendPrompt?: (value: string) => void }).sendPrompt
  if (typeof fn === 'function') fn(message)
}

function RankingChips({ athlete }: { athlete: CoachDashboardV1Athlete }) {
  return (
    <div className="coach-ranking-chips">
      <span>30d {formatScore(athlete.score)}</span>
      <span>Best {formatScore(athlete.score)}</span>
      <span>Series {formatScore(athlete.score)}</span>
      <span>Cons {formatScore(athlete.disciplineScore)}</span>
      <span>Fatigue {formatScore(athlete.fatigueScore)}</span>
    </div>
  )
}

function HabitCard({ athlete }: { athlete: CoachDashboardV1Athlete }) {
  const habits = [
    ['Sleep', athlete.sleepHours ? `${athlete.sleepHours.toFixed(1)}h` : '-'],
    ['Stress', formatScore(athlete.latestStress)],
    ['Fatigue', formatScore(athlete.fatigueScore)],
    ['HR/HRV', `${formatScore(athlete.restingHr)} / ${formatScore(athlete.hrvIndicator)}`],
    ['Recovery', formatScore(athlete.latestRecovery)],
    ['Focus', formatScore(athlete.focusScore)],
  ]
  return (
    <Link className="coach-habit-card" to={`/coach/athletes/${athlete.athleteId}`}>
      <div>
        <strong>{athlete.athleteName}</strong>
        <span>{athlete.trend}</span>
      </div>
      <dl>
        {habits.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </Link>
  )
}

function ScatterPlot({
  title,
  points,
  xKey,
  yKey,
}: {
  title: string
  points: NonNullable<CoachDashboardV1['mapping'][string]>
  xKey: 'fatigue' | 'stress' | 'sleep' | 'restingHr' | 'hrvIndicator' | 'performance' | 'consistency'
  yKey: 'performance' | 'readiness' | 'focus'
}) {
  const usable = points.filter((point) => typeof point[xKey] === 'number' && typeof point[yKey] === 'number')
  return (
    <article className="coach-map-card">
      <div className="coach-map-card-header">
        <strong>{title}</strong>
        <span>{usable.length} athletes</span>
      </div>
      <div className="coach-scatter" aria-label={title}>
        {usable.map((point) => (
          <Link
            key={`${point.athleteId}-${title}`}
            to={`/coach/athletes/${point.athleteId}`}
            className="coach-scatter-dot"
            style={{
              left: `${Math.min(95, Math.max(4, Number(point[xKey])))}%`,
              bottom: `${Math.min(92, Math.max(5, Number(point[yKey])))}%`,
            }}
            title={`${point.athleteName}: ${xKey} ${formatScore(point[xKey])}, ${yKey} ${formatScore(point[yKey])}`}
          />
        ))}
      </div>
    </article>
  )
}

export default function CoachDashboardV1Page() {
  const { user, isLoading } = useAuth()
  const [dashboard, setDashboard] = useState<CoachDashboardV1 | null>(null)
  const [coachId, setCoachId] = useState('')
  const [gender, setGender] = useState('all')
  const [minScore, setMinScore] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('performance')
  const [isFetching, setIsFetching] = useState(false)
  const [error, setError] = useState('')
  const hasLoadedDashboard = useRef(false)

  const load = useCallback(async () => {
    if (!user || user.role !== 'coach') return
    setIsFetching(true)
    if (!hasLoadedDashboard.current) setError('')
    try {
      const profile = await getCoachProfile()
      setCoachId(profile.coachId)
      const data = await getCoachDashboardV1(profile.coachId, {
        gender: gender === 'all' ? undefined : gender,
        minScore: minScore ? Number(minScore) : undefined,
      })
      setDashboard(data)
      hasLoadedDashboard.current = true
      setError('')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to load dashboard'
      setError(hasLoadedDashboard.current ? 'Connection is unstable. Showing the last loaded dashboard data.' : message)
    } finally {
      setIsFetching(false)
    }
  }, [gender, minScore, user])

  useEffect(() => { void load() }, [load])

  const visibleAthletes = useMemo(() => {
    const term = search.trim().toLowerCase()
    return [...(dashboard?.athletes ?? [])]
      .filter((athlete) => !term || athlete.athleteName.toLowerCase().includes(term))
      .filter((athlete) => statusFilter === 'all' || athlete.status === statusFilter)
      .sort((a, b) => {
        return sortValue(b, sortKey) - sortValue(a, sortKey)
      })
  }, [dashboard, search, sortKey, statusFilter])

  if (!isLoading && !user) return <Navigate to="/coach/login" replace />
  if (!isLoading && user?.role !== 'coach') return <Navigate to="/coach/login" replace />

  return (
    <section className="dashboard-shell coach-visual-theme">
      <div className="dashboard-container">
        <div className="dashboard-hero coach-v1-hero">
          <p className="dashboard-eyebrow">Operational Coach Dashboard</p>
          <h1>Team Readiness and Performance Command Center</h1>
          <p>Monitor assigned athletes, identify top performers and at-risk athletes, and connect performance with stress, fatigue, recovery, sleep, and discipline.</p>
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
              <span>Min Performance</span>
              <input value={minScore} onChange={(e) => setMinScore(e.target.value)} placeholder="e.g. 60" />
            </label>
            <label>
              <span>Status</span>
              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <option value="all">All</option>
                <option value="Strong">Strong</option>
                <option value="Stable">Stable</option>
                <option value="Needs Attention">Needs Attention</option>
                <option value="At Risk">At Risk</option>
              </select>
            </label>
            <label>
              <span>Sort</span>
              <select value={sortKey} onChange={(e) => setSortKey(e.target.value as SortKey)}>
                <option value="performance">Performance</option>
                <option value="readiness">Readiness</option>
                <option value="fatigue">Fatigue</option>
                <option value="stress">Stress</option>
                <option value="consistency">Consistency</option>
              </select>
            </label>
            <button className="dashboard-inline-link" type="button" onClick={() => void load()}>
              Apply
            </button>
          </div>
        </section>

        {error ? <p className={`dashboard-message ${dashboard ? 'dashboard-warning' : 'dashboard-error'}`}>{error}</p> : null}
        {isFetching ? <p className="dashboard-message">Loading dashboard...</p> : null}

        {dashboard ? (
          <>
            <section className="dashboard-section">
              <h2>Team Summary</h2>
              <div className="coach-overview-grid coach-overview-grid-v1">
                <article className="coach-stat-tile"><span>Total Athletes</span><strong>{dashboard.totals.totalAssignedAthletes}</strong></article>
                <article className="coach-stat-tile"><span>Active This Week</span><strong>{dashboard.totals.activeAthletes}</strong></article>
                <article className="coach-stat-tile"><span>Avg Performance</span><strong>{formatScore(dashboard.averageScore)}</strong></article>
                <article className="coach-stat-tile"><span>Avg Readiness</span><strong>{formatScore(dashboard.averageReadiness)}</strong></article>
                <article className="coach-stat-tile"><span>Avg Fatigue</span><strong>{formatScore(dashboard.averageFatigue)}</strong></article>
                <article className="coach-stat-tile"><span>Avg Stress</span><strong>{formatScore(dashboard.averageStress)}</strong></article>
                <article className="coach-stat-tile coach-stat-tile--alert"><span>Need Attention</span><strong>{dashboard.totals.athletesNeedingAttention ?? 0}</strong></article>
                <article className="coach-stat-tile"><span>Disciplined</span><strong>{dashboard.totals.mostDisciplined ?? 0}</strong></article>
              </div>
            </section>

            <section className="dashboard-section">
              <h2>Athlete Performance Table</h2>
              <label className="dashboard-search dashboard-section-search">
                <span>Search Athlete</span>
                <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by athlete name" />
              </label>
              <div className="dashboard-empty-card coach-v1-table-wrap">
                <table className="coach-v1-table">
                  <thead>
                    <tr>
                      <th align="left">Athlete</th><th align="left">Sport</th><th align="left">Performance</th><th align="left">Ready</th><th align="left">Focus</th><th align="left">Consistency</th><th align="left">Stress</th><th align="left">HR / HRV</th><th align="left">Fatigue</th><th align="left">Recovery</th><th align="left">Last Session</th><th align="left">Status</th><th align="left">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visibleAthletes.map((athlete) => (
                      <tr key={athlete.athleteId} className="coach-v1-row" onMouseEnter={() => notifyCoachIntent(`Review athlete ${athlete.athleteName}`)}>
                        <td>{athlete.athleteName}</td>
                        <td>{athlete.sport ?? athlete.discipline ?? '-'}</td>
                        <td><span className={`score-pill score-pill--${scoreTone(athlete.score)}`}>{formatScore(athlete.score)}</span></td>
                        <td>{formatScore(athlete.readinessScore)}</td>
                        <td>{formatScore(athlete.focusScore)}</td>
                        <td>{formatScore(athlete.disciplineScore)}</td>
                        <td className={(athlete.latestStress ?? 0) >= 70 ? 'coach-v1-alert-cell' : ''}>{formatScore(athlete.latestStress)}</td>
                        <td>{formatScore(athlete.restingHr)} / {formatScore(athlete.hrvIndicator)}</td>
                        <td>{formatScore(athlete.fatigueScore)}</td>
                        <td>{formatScore(athlete.latestRecovery)}</td>
                        <td>{formatDate(athlete.lastSessionDate)}</td>
                        <td><span className={`risk-chip risk-chip--${statusTone(athlete.status)}`}>{athlete.status}</span></td>
                        <td><Link to={`/coach/athletes/${athlete.athleteId}`} onClick={() => notifyCoachIntent(`Open profile ${athlete.athleteName}`)}>View</Link></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="dashboard-section">
              <h2>Score Mapping</h2>
              <div className="coach-map-grid">
                <ScatterPlot title="Performance vs Fatigue" points={dashboard.mapping.performanceVsFatigue ?? []} xKey="fatigue" yKey="performance" />
                <ScatterPlot title="Performance vs Stress" points={dashboard.mapping.performanceVsStress ?? []} xKey="stress" yKey="performance" />
                <ScatterPlot title="Performance vs Resting HR" points={dashboard.mapping.performanceVsHeartRate ?? []} xKey="restingHr" yKey="performance" />
                <ScatterPlot title="Performance vs HRV" points={dashboard.mapping.performanceVsHrv ?? []} xKey="hrvIndicator" yKey="performance" />
                <ScatterPlot title="Performance vs Sleep" points={dashboard.mapping.performanceVsSleep ?? []} xKey="sleep" yKey="performance" />
                <ScatterPlot title="Readiness vs Performance" points={dashboard.mapping.readinessVsPerformance ?? []} xKey="performance" yKey="readiness" />
                <ScatterPlot title="Focus vs Consistency" points={dashboard.mapping.focusVsConsistency ?? []} xKey="consistency" yKey="focus" />
              </div>
              <div className="coach-heatmap">
                {visibleAthletes.slice(0, 12).map((athlete) => (
                  <article key={athlete.athleteId}>
                    <strong>{athlete.athleteName}</strong>
                    {[athlete.score, athlete.readinessScore, athlete.focusScore, athlete.disciplineScore, athlete.latestRecovery].map((value, index) => (
                      <span key={index} style={{ opacity: typeof value === 'number' ? Math.max(0.25, value / 100) : 0.2 }} />
                    ))}
                  </article>
                ))}
              </div>
            </section>

            <section className="dashboard-section">
              <h2>Top, Disciplined, Healthy</h2>
              <div className="coach-ranking-grid">
                <Ranking title="Top Performers" athletes={dashboard.topPerformers} metric="score" />
                <Ranking title="Most Disciplined" athletes={dashboard.mostDisciplined} metric="disciplineScore" />
                <Ranking title="Healthy and Focused" athletes={dashboard.healthyFocused} metric="latestRecovery" />
              </div>
            </section>

            <section className="dashboard-section">
              <h2>Healthy and Focused Habits</h2>
              <div className="coach-habit-grid">
                {dashboard.healthyFocused.slice(0, 6).map((athlete) => (
                  <HabitCard key={athlete.athleteId} athlete={athlete} />
                ))}
              </div>
            </section>

            <section className="dashboard-section">
              <h2>Risk / Attention Queue</h2>
              <div className="coach-risk-grid">
                {dashboard.riskQueue.length > 0 ? dashboard.riskQueue.map((item) => (
                  <article key={item.athleteId} className="coach-risk-card">
                    <div>
                      <span className={`risk-chip risk-chip--${item.severity === 'High' ? 'attention' : 'risk'}`}>{item.severity}</span>
                      <h3>{item.athleteName}</h3>
                    </div>
                    <p>{item.reasons.join(', ')}</p>
                    <strong>{item.suggestedAction}</strong>
                    <Link to={`/coach/athletes/${item.athleteId}`}>Open athlete dashboard</Link>
                  </article>
                )) : <p className="dashboard-message">No athletes need immediate intervention.</p>}
              </div>
            </section>

            <section className="dashboard-section">
              <h2>Team Insights Feed</h2>
              <div className="notification-list">
                {dashboard.insights.map((insight) => (
                  <article key={insight.title} className="notification-item">
                    <span>{insight.priority} Priority / {insight.category}</span>
                    <p><strong>{insight.title}</strong> - {insight.insightText}</p>
                  </article>
                ))}
              </div>
            </section>
          </>
        ) : null}

        {coachId ? <input type="hidden" value={coachId} readOnly /> : null}
      </div>
    </section>
  )
}

function Ranking({ title, athletes, metric }: { title: string; athletes: CoachDashboardV1Athlete[]; metric: keyof CoachDashboardV1Athlete }) {
  return (
    <article className="coach-ranking-card">
      <h3>{title}</h3>
      {athletes.length > 0 ? athletes.map((athlete, index) => (
        <Link key={athlete.athleteId} to={`/coach/athletes/${athlete.athleteId}`}>
          <div>
            <span>{index + 1}. {athlete.athleteName}</span>
            <RankingChips athlete={athlete} />
          </div>
          <strong>{formatScore(athlete[metric] as number | null | undefined)}</strong>
        </Link>
      )) : <p>No athletes yet.</p>}
    </article>
  )
}
