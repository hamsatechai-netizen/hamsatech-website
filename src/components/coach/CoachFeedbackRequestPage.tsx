import { FormEvent, useMemo, useState } from 'react'
import { Link, Navigate, useSearchParams } from 'react-router-dom'
import { createCoachFeedbackV1, markCoachNotificationRead } from '../../lib/authApi'
import { useAuth } from '../../context/AuthContext'
import '../../styles/Dashboard.css'

export default function CoachFeedbackRequestPage() {
  const { user, isLoading } = useAuth()
  const [searchParams] = useSearchParams()
  const athleteId = searchParams.get('athlete_id') ?? ''
  const requestId = searchParams.get('request_id') ?? ''
  const notificationId = searchParams.get('notification_id') ?? ''
  const [note, setNote] = useState('')
  const [recommendation, setRecommendation] = useState('')
  const [status, setStatus] = useState<'Needs Attention' | 'Progressing' | 'Strong'>('Progressing')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  const canSubmit = useMemo(() => athleteId && requestId && note.trim().length >= 2 && recommendation.trim().length >= 2, [athleteId, requestId, note, recommendation])

  if (!isLoading && !user) return <Navigate to="/coach/login" replace />
  if (!isLoading && user?.role !== 'coach') return <Navigate to="/coach/login" replace />

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!canSubmit) return
    setIsSaving(true)
    setError('')
    setSuccess('')
    try {
      await createCoachFeedbackV1({
        requestId,
        athleteId,
        note: note.trim(),
        recommendation: recommendation.trim(),
        status,
      })
      if (notificationId) {
        await markCoachNotificationRead(notificationId)
      }
      setSuccess('Feedback submitted successfully.')
      setNote('')
      setRecommendation('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to submit feedback.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <section className="dashboard-shell">
      <div className="dashboard-container">
        <div className="dashboard-section">
          <div className="dashboard-section-header">
            <h2>Coach Feedback</h2>
            <p>Complete feedback request for athlete {athleteId || 'N/A'}.</p>
          </div>
          <form className="student-card" onSubmit={onSubmit}>
            <label className="dashboard-search">
              <span>Feedback Note</span>
              <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={4} />
            </label>
            <label className="dashboard-search">
              <span>Recommendation</span>
              <textarea value={recommendation} onChange={(e) => setRecommendation(e.target.value)} rows={4} />
            </label>
            <label className="dashboard-search">
              <span>Status</span>
              <select value={status} onChange={(e) => setStatus(e.target.value as 'Needs Attention' | 'Progressing' | 'Strong')}>
                <option value="Needs Attention">Needs Attention</option>
                <option value="Progressing">Progressing</option>
                <option value="Strong">Strong</option>
              </select>
            </label>
            {error ? <p className="dashboard-message dashboard-error">{error}</p> : null}
            {success ? <p className="dashboard-message">{success}</p> : null}
            <div className="dashboard-inline-actions">
              <button type="submit" className="dashboard-inline-link" disabled={!canSubmit || isSaving}>
                {isSaving ? 'Submitting...' : 'Submit feedback'}
              </button>
              <Link to="/coach/dashboard" className="dashboard-inline-link">Back to dashboard</Link>
            </div>
          </form>
        </div>
      </div>
    </section>
  )
}
