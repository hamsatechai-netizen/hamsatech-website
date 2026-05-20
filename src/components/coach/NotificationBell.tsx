import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  getCoachProfile,
  getCoachNotificationsV1,
  markCoachNotificationRead,
  type CoachNotification,
} from '../../lib/authApi'
import { useAuth } from '../../context/AuthContext'

type Props = {
  coachId?: string | null
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('en-IN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

export default function NotificationBell({ coachId }: Props) {
  const { user } = useAuth()
  const [items, setItems] = useState<CoachNotification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)

  const [resolvedCoachId, setResolvedCoachId] = useState<string | null>(coachId ?? null)

  useEffect(() => {
    if (!user || user.role !== 'coach') return
    if (coachId) {
      setResolvedCoachId(coachId)
      return
    }
    void getCoachProfile().then((profile) => setResolvedCoachId(profile.coachId)).catch(() => setResolvedCoachId(null))
  }, [coachId, user])

  useEffect(() => {
    if (!user || user.role !== 'coach' || !resolvedCoachId) return
    let alive = true

    const load = async () => {
      try {
        const data = await getCoachNotificationsV1(resolvedCoachId, { unreadOnly: false, limit: 10 })
        if (!alive) return
        setItems(data.notifications)
        setUnreadCount(data.unreadCount)
      } catch {
        if (!alive) return
        setItems([])
        setUnreadCount(0)
      }
    }

    void load()
    const interval = window.setInterval(() => void load(), 30000)
    return () => {
      alive = false
      window.clearInterval(interval)
    }
  }, [resolvedCoachId, user])

  const bellLabel = useMemo(() => (unreadCount > 0 ? `Notifications (${unreadCount})` : 'Notifications'), [unreadCount])

  if (!user || user.role !== 'coach' || !resolvedCoachId) return null

  return (
    <div className="coach-notification-bell">
      <button type="button" className="coach-notification-trigger" onClick={() => setIsOpen((v) => !v)} aria-label={bellLabel}>
        🔔 Notifications {unreadCount > 0 ? <span className="coach-notification-badge">{unreadCount}</span> : null}
      </button>
      {isOpen ? (
        <div className="coach-notification-dropdown">
          {items.length === 0 ? (
            <p className="coach-notification-empty">No notifications</p>
          ) : (
            items.map((item) => (
              <article key={item.notificationId} className={`coach-notification-item ${item.isRead ? '' : 'unread'}`}>
                <p>{item.message}</p>
                <small>{formatDate(item.createdAt)}</small>
                {item.type === 'NEW_USER_REGISTRATION' ? (
                  <Link to="/coach/assignments/pending" onClick={() => setIsOpen(false)}>
                    Open assignment queue
                  </Link>
                ) : item.athleteId && item.sessionId ? (
                  <Link
                    to={`/coach/feedback/new?athlete_id=${encodeURIComponent(item.athleteId)}&session_id=${encodeURIComponent(item.sessionId)}&request_id=${encodeURIComponent(item.requestId ?? '')}&notification_id=${encodeURIComponent(item.notificationId)}`}
                    onClick={async () => {
                      if (!item.isRead) await markCoachNotificationRead(item.notificationId)
                      setIsOpen(false)
                    }}
                  >
                    Open feedback form
                  </Link>
                ) : null}
              </article>
            ))
          )}
        </div>
      ) : null}
    </div>
  )
}
