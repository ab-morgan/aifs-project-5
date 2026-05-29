import type { JobMatch } from '../app/components/JobResultCard'

const API_BASE = (import.meta.env['VITE_API_URL'] as string | undefined) ?? ''

export interface MatchRequest {
  resume_text: string
  preferences?: string
  exclusions?: string
  match_count?: number
}

export async function fetchMatches(req: MatchRequest): Promise<JobMatch[]> {
  const res = await fetch(`${API_BASE}/api/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })

  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`
    try {
      const body = (await res.json()) as { detail?: string }
      if (body.detail) detail = body.detail
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }

  return res.json() as Promise<JobMatch[]>
}
