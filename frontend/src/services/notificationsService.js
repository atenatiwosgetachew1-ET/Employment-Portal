import { apiFetch } from '../api/client'

export async function fetchNotifications() {
  const response = await apiFetch('/api/notifications/')
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to load notifications')
  }
  return response.json()
}

export async function patchNotification(id, payload) {
  const response = await apiFetch(`/api/notifications/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(payload)
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to update notification')
  }
  return data
}

export async function markAllNotificationsRead() {
  const response = await apiFetch('/api/notifications/mark-all-read/', {
    method: 'POST',
    body: JSON.stringify({})
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to mark notifications read')
  }
  return response.json()
}
