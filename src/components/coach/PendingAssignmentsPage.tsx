import { useCallback, useEffect, useRef, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import {
  assignAthlete,
  getAvailableCoaches,
  getCoachProfile,
  getPendingAssignments,
  type CoachOption,
  type PendingAssignment,
} from '../../lib/authApi'
import '../../styles/Dashboard.css'

export default function PendingAssignmentsPage() {
  const { user, isLoading } = useAuth()
  const [coachId, setCoachId] = useState('')
  const [requests, setRequests] = useState<PendingAssignment[]>([])
  const [coaches, setCoaches] = useState<CoachOption[]>([])
  const [selectedCoachByRequest, setSelectedCoachByRequest] = useState<Record<string, string>>({})
  const [isLoadingData, setIsLoadingData] = useState(false)
  const [assigningRequestId, setAssigningRequestId] = useState('')
  const [error, setError] = useState('')
  const hasLoadedAssignments = useRef(false)

  const load = useCallback(async () => {
    if (!user || user.role !== 'coach') return
    setIsLoadingData(true)
    if (!hasLoadedAssignments.current) setError('')
    try {
      const profile = await getCoachProfile()
      setCoachId(profile.coachId)
      const [pending, allCoaches] = await Promise.all([
        getPendingAssignments(profile.coachId),
        getAvailableCoaches(),
      ])
      setRequests(pending)
      setCoaches(allCoaches)
      const initial: Record<string, string> = {}
      for (const request of pending) {
        initial[request.requestId] = request.assignedCoachId ?? profile.coachId
      }
      setSelectedCoachByRequest(initial)
      hasLoadedAssignments.current = true
      setError('')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to load pending assignments'
      setError(hasLoadedAssignments.current ? 'Connection is unstable. Showing the last loaded assignments.' : message)
    } finally {
      setIsLoadingData(false)
    }
  }, [user])

  useEffect(() => {
    void load()
  }, [load])

  if (!isLoading && !user) return <Navigate to="/coach/login" replace />
  if (!isLoading && user?.role !== 'coach') return <Navigate to="/coach/login" replace />

  return (
    <section className="dashboard-shell">
      <div className="dashboard-container">
        <div className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>Pending Assignments</h2>
            <p>Review new athlete registrations and assign coach ownership.</p>
          </div>
          {error ? <p className={`dashboard-message ${requests.length > 0 ? 'dashboard-warning' : 'dashboard-error'}`}>{error}</p> : null}
          {isLoadingData ? <p className="dashboard-message">Loading pending assignments...</p> : null}
          {requests.length === 0 && !isLoadingData ? (
            <div className="dashboard-empty-card"><p>No pending assignments.</p></div>
          ) : null}
          {requests.map((request) => (
            <article key={request.requestId} className="student-card assignment-card">
              <div className="student-card-header">
                <div>
                  <p className="student-role">Pending</p>
                  <h2>{request.athleteName}</h2>
                </div>
              </div>
              <dl className="student-meta">
                <div><dt>Athlete ID</dt><dd>{request.athleteId}</dd></div>
                <div><dt>Requested At</dt><dd>{request.requestedAt ?? 'N/A'}</dd></div>
              </dl>
              <label className="dashboard-search">
                <span>Assign Coach</span>
                <select
                  value={selectedCoachByRequest[request.requestId] ?? coachId}
                  onChange={(event) => setSelectedCoachByRequest((prev) => ({ ...prev, [request.requestId]: event.target.value }))}
                >
                  {coaches.map((coach) => (
                    <option key={coach.coachId} value={coach.coachId}>
                      {coach.coachName} {coach.coachIdText ? `(${coach.coachIdText})` : ''}
                    </option>
                  ))}
                </select>
              </label>
              <div className="dashboard-inline-actions">
                <button
                  type="button"
                  className="dashboard-inline-link"
                  disabled={assigningRequestId === request.requestId}
                  onClick={async () => {
                    const assignedCoachId = selectedCoachByRequest[request.requestId]
                    if (!assignedCoachId) return
                    setAssigningRequestId(request.requestId)
                    setError('')
                    try {
                      await assignAthlete({
                        requestId: request.requestId,
                        athleteId: request.athleteId,
                        assignedCoachId,
                        notes: 'Assigned from pending assignments page',
                      })
                      await load()
                    } catch (err) {
                      setError(err instanceof Error ? err.message : 'Unable to assign athlete')
                    } finally {
                      setAssigningRequestId('')
                    }
                  }}
                >
                  {assigningRequestId === request.requestId ? 'Assigning...' : 'Assign'}
                </button>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
