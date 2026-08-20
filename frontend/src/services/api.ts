import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Automatically attach JWT token from localStorage if present
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle HTTP errors cleanly
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response ? error.response.status : null
    if (status === 401) {
      localStorage.removeItem('token')
    }
    return Promise.reject(error)
  }
)

export async function uploadResume(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/api/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data
}

export async function createInterview(data: {
  resume_id?: string;
  candidate_profile?: any;
  role?: string;
  target_role?: string;
  experience_level?: string;
  interview_type?: string;
  difficulty?: string;
  interview_style?: string;
  target_duration?: string;
}) {
  const chosenRole = data.role || data.target_role || data.candidate_profile?.target_role || 'AI/ML Engineer'
  const res = await api.post('/api/interviews/start', {
    role: chosenRole,
    experience_level: data.experience_level || data.candidate_profile?.experience_level || 'Fresher',
    interview_type: data.interview_type || 'mixed',
    difficulty: data.difficulty || 'medium',
    interview_style: data.interview_style || 'Professional',
    target_duration: data.target_duration || '15 min',
    resume_id: data.resume_id,
    candidate_profile: data.candidate_profile
  })
  return res.data
}

export async function getInterview(sessionId: string) {
  const res = await api.get(`/api/interviews/${sessionId}`)
  return res.data
}

export async function endInterview(sessionId: string) {
  const res = await api.post(`/api/interviews/${sessionId}/end`)
  return res.data
}

export async function exitInterviewSession(sessionId: string, reason = 'user_exit') {
  const res = await api.post(`/api/interviews/${sessionId}/exit`, { reason })
  return res.data
}

export async function generateInterviewReport(sessionId: string) {
  const res = await api.post(`/api/interviews/${sessionId}/report`)
  return res.data
}

export async function getInterviewReportStatus(sessionId: string) {
  const res = await api.get(`/api/interviews/${sessionId}/report/status`)
  return res.data
}

export async function getInterviewReport(sessionId: string) {
  const res = await api.get(`/api/interviews/${sessionId}/report`)
  return res.data
}

export async function scheduleInterview(data: {
  role: string
  interview_type?: string
  difficulty?: string
  scheduled_date?: string
  scheduled_time?: string
  scheduled_at?: string
  duration_minutes?: number
  resume_id?: string
  timezone?: string
}) {
  const res = await api.post('/api/interviews/schedule', data)
  return res.data
}

export async function getScheduledInterviews() {
  const res = await api.get('/api/interviews/scheduled')
  return res.data
}

export async function startScheduledInterview(sessionId: string) {
  const res = await api.post(`/api/interviews/${sessionId}/start`)
  return res.data
}

export async function getInterviewNotifications() {
  const res = await api.get('/api/interviews/notifications')
  return res.data
}

export async function getInterviewHistory() {
  const res = await api.get('/api/interviews/history/list')
  return res.data
}

export async function updateInterviewSession(sessionId: string, payload: { role?: string; interview_type?: string; difficulty?: string }) {
  const res = await api.put(`/api/interviews/session/${sessionId}`, payload)
  return res.data
}

export async function deleteInterviewSession(sessionId: string) {
  const res = await api.delete(`/api/interviews/session/${sessionId}`)
  return res.data
}

export async function askQuestion(sessionId: string, question: string) {
  const res = await api.post(`/api/interviews/${sessionId}/ask`, { question })
  return res.data
}

export async function streamQuestion(
  sessionId: string,
  question: string,
  onChunk: (chunk: string) => void,
  onDone: (fullText: string) => void
) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/interviews/${sessionId}/ask/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': localStorage.getItem('token') ? `Bearer ${localStorage.getItem('token')}` : ''
      },
      body: JSON.stringify({ question })
    })

    if (!response.ok || !response.body) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.chunk) {
              onChunk(data.chunk)
            }
            if (data.done) {
              onDone(data.full_text || '')
              return
            }
          } catch (e) {
            console.warn('SSE JSON parse error:', e)
          }
        }
      }
    }
  } catch (err) {
    console.error('Streaming API error:', err)
    // Fallback to non-streaming endpoint
    const res = await askQuestion(sessionId, question)
    onDone(res.reply)
  }
}

export async function fetchGlobalJobs(params: Record<string, any>) {
  const res = await api.get('/api/jobs', { params })
  return res.data
}

export async function fetchLiveJobMatches(payload: {
  resume_id?: number;
  days_limit?: number;
  minMatchScore?: number;
  job_type_filter?: string;
  work_mode_filter?: string;
  location_filter?: string;
}) {
  const res = await api.post('/api/jobs/match', payload)
  return res.data
}

export async function toggleSaveJob(jobId: number) {
  const res = await api.post(`/api/jobs/save/${jobId}`)
  return res.data
}

export async function recordApplyClick(jobId: number) {
  const res = await api.post(`/api/jobs/${jobId}/apply-click`)
  return res.data
}

export async function trackJobApplication(jobId: number, data: { status?: string; source?: string; application_url: string }) {
  const res = await api.post(`/api/jobs/apply/${jobId}`, data)
  return res.data
}

export async function getUserJobApplications() {
  const res = await api.get('/api/jobs/applications')
  return res.data
}
