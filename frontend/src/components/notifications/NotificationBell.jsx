import { useCallback, useEffect, useRef, useState } from 'react'
import * as notificationsService from '../../services/notificationsService'

export default function NotificationBell() {
  const [open, setOpen] = useState(false)
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const wrapRef = useRef(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await notificationsService.fetchNotifications()
      setItems(Array.isArray(data) ? data : [])
    } catch {
      setItems([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    if (!open) return
    load()
  }, [open, load])

  useEffect(() => {
    function onDocClick(e) {
      if (!wrapRef.current?.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [])

  const unread = items.filter((n) => !n.read).length

  const markRead = async (row) => {
    if (row.read) return
    try {
      await notificationsService.patchNotification(row.id, { read: true })
      setItems((prev) =>
        prev.map((n) => (n.id === row.id ? { ...n, read: true } : n))
      )
    } catch {
      /* ignore */
    }
  }

  const markAllRead = async () => {
    try {
      await notificationsService.markAllNotificationsRead()
      setItems((prev) => prev.map((n) => ({ ...n, read: true })))
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="notification-bell-wrap" ref={wrapRef}>
      <button
        type="button"
        className="notification-bell-btn"
        aria-expanded={open}
        aria-label="Notifications"
        onClick={() => setOpen((o) => !o)}
      >
        <span className="notification-bell-icon" aria-hidden>
          &#128276;
        </span>
        {unread > 0 && <span className="notification-bell-badge">{unread > 99 ? '99+' : unread}</span>}
      </button>
      {open && (
        <div className="notification-dropdown" role="dialog" aria-label="Notifications list">
          <div className="notification-dropdown-header">
            <span>Notifications</span>
            {unread > 0 && (
              <button type="button" className="notification-mark-all" onClick={markAllRead}>
                Mark all read
              </button>
            )}
          </div>
          <div className="notification-dropdown-body">
            {loading && <p className="muted-text">Loading…</p>}
            {!loading && items.length === 0 && (
              <p className="muted-text notification-empty">No notifications yet.</p>
            )}
            {!loading &&
              items.map((n) => (
                <button
                  key={n.id}
                  type="button"
                  className={`notification-item${n.read ? '' : ' is-unread'}`}
                  onClick={() => markRead(n)}
                >
                  <span className="notification-item-title">{n.title}</span>
                  {n.body && <span className="notification-item-body">{n.body}</span>}
                  <span className="notification-item-time">
                    {n.created_at
                      ? new Date(n.created_at).toLocaleString()
                      : ''}
                  </span>
                </button>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
