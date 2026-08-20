import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../services/api'
import type { InterviewSession, FeedbackData } from '../types'

export const useInterviewStore = defineStore('interview', () => {
  const currentSession = ref<InterviewSession | null>(null)
  const sessionHistory = ref<InterviewSession[]>([])
  const currentQuestionIndex = ref<number>(0)
  const evaluations = ref<FeedbackData[]>([])
  const isLoading = ref<boolean>(false)

  const startSession = async (payload: {
    role: string;
    experience_level: string;
    industry: string;
    mode: string;
    interview_type: string;
    difficulty: string;
    question_count: number;
  }) => {
    isLoading.value = true
    try {
      const res = await api.post('/api/interviews/start', payload)
      currentSession.value = res.data
      currentQuestionIndex.value = 0
      evaluations.value = []
      return res.data
    } catch (err) {
      console.error('Failed to start interview session:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const submitAnswer = async (payload: {
    session_id: string;
    question_id: number;
    user_answer: string;
    audio_duration?: number;
  }) => {
    isLoading.value = true
    try {
      const res = await api.post('/api/interviews/submit-answer', payload)
      evaluations.value.push(res.data)
      return res.data
    } catch (err) {
      console.error('Failed to submit answer for evaluation:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchHistory = async () => {
    try {
      const res = await api.get('/api/interviews/sessions')
      sessionHistory.value = res.data
    } catch (err) {
      console.warn('Failed to fetch session history:', err)
    }
  }

  return {
    currentSession,
    sessionHistory,
    currentQuestionIndex,
    evaluations,
    isLoading,
    startSession,
    submitAnswer,
    fetchHistory
  }
})
