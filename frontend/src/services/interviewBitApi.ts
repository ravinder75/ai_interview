import { api } from './api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005'

export interface CandidateProfile {
  id?: string;
  name?: string;
  email?: string;
  phone?: string;
  target_role?: string;
  experience_level?: string;
  location?: string;
  skills: string[];
  languages?: string[];
  frameworks?: string[];
  databases?: string[];
  cloud?: string[];
  projects: any[];
  experience?: any[];
  education?: any[];
  certifications?: any[];
  achievements?: any[];
  additional_information?: string;
  resume_filename?: string;
}

export async function uploadInterviewBitResume(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/api/interview-bit/resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data
}

export async function saveInterviewBitProfile(profile: Partial<CandidateProfile>) {
  const res = await api.post('/api/interview-bit/profile', profile)
  return res.data
}

export async function getLatestProfile(): Promise<CandidateProfile> {
  const res = await api.get('/api/interview-bit/profile')
  return res.data
}

export async function updateInterviewBitProfile(id: string, profile: Partial<CandidateProfile>) {
  const res = await api.put(`/api/interview-bit/profile/${id}`, profile)
  return res.data
}

export async function askInterviewBit(data: {
  question: string;
  profile_id?: string;
  session_id?: string;
  style?: string;
}) {
  const res = await api.post('/api/interview-bit/ask', data)
  return res.data
}

export async function streamInterviewBit(
  data: { question: string; profile_id?: string; session_id?: string; style?: string },
  onChunk: (chunk: string, meta: { session_id?: string; category?: string }) => void,
  onDone: (meta: { full_text: string; follow_ups: string[]; session_id: string }) => void
) {
  try {
    const token = localStorage.getItem('token') || ''
    const response = await fetch(`${API_BASE_URL}/api/interview-bit/ask/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify(data)
    })

    if (!response.ok || !response.body) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    let accumulatedText = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const parsed = JSON.parse(line.slice(6))
            if (parsed.chunk) {
              accumulatedText += parsed.chunk
              onChunk(parsed.chunk, { session_id: parsed.session_id, category: parsed.category })
            }
            if (parsed.done) {
              onDone({
                full_text: parsed.full_text || accumulatedText || '',
                follow_ups: parsed.follow_ups || [],
                session_id: parsed.session_id || ''
              })
              return
            }
          } catch (e) {
            console.warn('SSE stream parse error:', e)
          }
        }
      }
    }

    // Safety fallback if stream ended without explicit done message
    if (accumulatedText) {
      onDone({
        full_text: accumulatedText,
        follow_ups: [],
        session_id: ''
      })
    }
  } catch (err) {
    console.error('Streaming error fallback to standard endpoint:', err)
    try {
      const res = await askInterviewBit(data)
      onDone({
        full_text: res?.answer || 'AI service is temporarily unavailable. Please try again.',
        follow_ups: res?.follow_ups || [],
        session_id: res?.session_id || ''
      })
    } catch (fallbackErr) {
      console.error('Fallback endpoint failed:', fallbackErr)
      onDone({
        full_text: 'AI service is temporarily unavailable. Please try again.',
        follow_ups: [],
        session_id: ''
      })
    }
  }
}

export async function getInterviewBitHistory(sessionId?: string) {
  const url = sessionId ? `/api/interview-bit/history?session_id=${sessionId}` : '/api/interview-bit/history'
  const res = await api.get(url)
  return res.data
}

export async function clearInterviewBitHistory(sessionId?: string) {
  const url = sessionId ? `/api/interview-bit/history?session_id=${sessionId}` : '/api/interview-bit/history'
  const res = await api.delete(url)
  return res.data
}
