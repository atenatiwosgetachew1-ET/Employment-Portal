import { apiFetch } from '../api/client'

export async function fetchAuditLogs({ page = 1, q = '' } = {}) {
  const params = new URLSearchParams()
  params.set('page', String(page))
  if (q.trim()) params.set('q', q.trim())

  const response = await apiFetch(`/api/audit-logs/?${params.toString()}`)
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to load activity log')
  }
  return response.json()
}
