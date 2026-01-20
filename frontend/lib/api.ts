// API client functions for backend communication

import type { DecisionInput, Decision, DecisionListItem, ReflectionInsight } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL

if (!API_BASE_URL) {
  throw new Error('NEXT_PUBLIC_API_BASE_URL environment variable is not defined. Please set it to your backend URL.')
}

// Centralized API endpoints matching backend routes
const endpoints = {
  decisions: `${API_BASE_URL}/api/decisions`,
  decision: (id: string) => `${API_BASE_URL}/api/decisions/${id}`,
  reflect: (id: string) => `${API_BASE_URL}/api/decisions/${id}/reflect`,
}

class APIError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = 'APIError'
  }
}

export async function createDecision(input: DecisionInput): Promise<Decision> {
  const response = await fetch(endpoints.decisions, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Failed to create decision' }))
    throw new APIError(error.error || 'Failed to create decision', response.status)
  }

  return response.json()
}

export async function getDecisions(): Promise<{ decisions: DecisionListItem[] }> {
  const response = await fetch(endpoints.decisions)

  if (!response.ok) {
    throw new APIError('Failed to fetch decisions', response.status)
  }

  return response.json()
}

export async function getDecision(id: string): Promise<Decision> {
  const response = await fetch(endpoints.decision(id))

  if (!response.ok) {
    if (response.status === 404) {
      throw new APIError('Decision not found', 404)
    }
    throw new APIError('Failed to fetch decision', response.status)
  }

  return response.json()
}

export async function addReflection(
  id: string,
  actualOutcome: string
): Promise<{ reflection_insight: ReflectionInsight }> {
  const response = await fetch(endpoints.reflect(id), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ actual_outcome: actualOutcome }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Failed to add reflection' }))
    throw new APIError(error.error || 'Failed to add reflection', response.status)
  }

  return response.json()
}
