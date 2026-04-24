export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function fetchHealth() {
  const response = await fetch(`${API_BASE}/api/health`)
  if (!response.ok) throw new Error('Health check failed')
  return response.json()
}

export async function fetchSampleTranscript() {
  const response = await fetch(`${API_BASE}/api/sample-transcript`)
  if (!response.ok) throw new Error('Could not load sample transcript')
  return response.json()
}

export async function runPipeline(transcript) {
  const response = await fetch(`${API_BASE}/api/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transcript })
  })
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}))
    throw new Error(detail.detail || 'Pipeline failed')
  }
  return response.json()
}

export async function fetchRequirements(search = '') {
  const query = search ? `?search=${encodeURIComponent(search)}` : ''
  const response = await fetch(`${API_BASE}/api/requirements${query}`)
  if (!response.ok) throw new Error('Could not load requirements')
  return response.json()
}

export async function fetchGraph() {
  const response = await fetch(`${API_BASE}/api/graph`)
  if (!response.ok) throw new Error('Could not load graph')
  return response.json()
}

export async function transcribeAudio(file) {
  const form = new FormData()
  form.append('file', file)
  const response = await fetch(`${API_BASE}/api/transcribe`, {
    method: 'POST',
    body: form
  })
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}))
    throw new Error(detail.detail || 'Transcription failed')
  }
  return response.json()
}
