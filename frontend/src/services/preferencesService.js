import { apiFetch } from '../api/client'

export async function fetchPreferences() {
  const response = await apiFetch('/api/preferences/me/')
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to load settings')
  }
  return response.json()
}

export async function patchPreferences(payload) {
  const response = await apiFetch('/api/preferences/me/', {
    method: 'PATCH',
    body: JSON.stringify(payload)
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const msg =
      typeof data === 'object' && data !== null
        ? Object.entries(data)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
            .join(' ')
        : 'Failed to save settings'
    throw new Error(msg || 'Failed to save settings')
  }
  return data
}
