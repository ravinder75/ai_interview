import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getLatestProfile,
  saveInterviewBitProfile,
  streamInterviewBit,
  getInterviewBitHistory,
  clearInterviewBitHistory,
  type CandidateProfile
} from '../services/interviewBitApi'

export interface MessageItem {
  id?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  category?: string;
  follow_ups?: string[];
  created_at?: string;
}

export const useInterviewBitStore = defineStore('interviewBit', () => {
  const profile = ref<CandidateProfile | null>(null)
  const isProfileLoaded = ref<boolean>(false)
  const isSavingProfile = ref<boolean>(false)

  const messages = ref<MessageItem[]>([])
  const isStreaming = ref<boolean>(false)
  const streamingText = ref<string>('')
  const currentSessionId = ref<string>('')
  const answerStyle = ref<'concise' | 'normal' | 'detailed'>('normal')

  const isWidgetOpen = ref<boolean>(false)
  const isWidgetExpanded = ref<boolean>(false)

  // Automatic Mock Interview Mode State
  const isMockInterviewMode = ref<boolean>(false)
  const detectedQuestion = ref<string>('')
  const detectedQuestionType = ref<string>('general')
  const lastProcessedQuestionHash = ref<string>('')
  const autoAnswerStatus = ref<'idle' | 'detecting' | 'generating' | 'ready'>('idle')

  const setMockInterviewQuestion = async (questionText: string, sessionId?: string) => {
    if (!questionText || !questionText.trim()) return

    isMockInterviewMode.value = true

    // Simple normalization & hash calculation for duplicate protection
    const normalized = questionText.trim().replace(/\s+/g, ' ')
    const activeSess = sessionId || currentSessionId.value || 'sess-mock'
    const hash = `${activeSess}:${normalized}`

    if (hash === lastProcessedQuestionHash.value) {
      return // Duplicate event skip
    }

    // Explicitly unlock streaming state
    isStreaming.value = false
    streamingText.value = ''

    lastProcessedQuestionHash.value = hash
    detectedQuestion.value = normalized
    autoAnswerStatus.value = 'generating'

    // Open widget automatically in mock mode if closed
    if (!isWidgetOpen.value) {
      isWidgetOpen.value = true
    }

    // Automatically trigger question ask
    await askQuestion(normalized)
    autoAnswerStatus.value = 'ready'
  }

  const fetchProfile = async () => {
    try {
      const data = await getLatestProfile()
      profile.value = data
      isProfileLoaded.value = true
    } catch (err) {
      console.warn('Could not fetch Interview Bit profile:', err)
    }
  }

  const saveProfile = async (newProfile: Partial<CandidateProfile>) => {
    isSavingProfile.value = true
    try {
      const saved = await saveInterviewBitProfile(newProfile)
      profile.value = saved
      isProfileLoaded.value = true
      return saved
    } finally {
      isSavingProfile.value = false
    }
  }

  const fetchHistory = async (sessionId?: string) => {
    try {
      const list = await getInterviewBitHistory(sessionId)
      if (list && list.length) {
        messages.value = list.map((m: any) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          category: m.category,
          created_at: m.created_at
        }))
        currentSessionId.value = list[0]?.session_id || currentSessionId.value
      }
    } catch (err) {
      console.warn('Could not fetch history:', err)
    }
  }

  const clearHistory = async () => {
    try {
      await clearInterviewBitHistory(currentSessionId.value)
      messages.value = []
    } catch (err) {
      console.error('Error clearing history:', err)
    }
  }

  const askQuestion = async (questionText: string) => {
    if (!questionText.trim()) return

    isStreaming.value = true
    streamingText.value = ''

    messages.value.push({ role: 'user', content: questionText })

    try {
      await streamInterviewBit(
        {
          question: questionText,
          profile_id: profile.value?.id,
          session_id: currentSessionId.value,
          style: answerStyle.value
        },
        (chunk, meta) => {
          if (!streamingText.value) {
            streamingText.value = chunk
          } else {
            streamingText.value += chunk
          }
          if (meta.session_id) currentSessionId.value = meta.session_id
        },
        (meta) => {
          messages.value.push({
            role: 'assistant',
            content: meta.full_text || streamingText.value || 'AI service is temporarily unavailable. Please try again.',
            follow_ups: meta.follow_ups
          })
          if (meta.session_id) currentSessionId.value = meta.session_id
          streamingText.value = ''
          isStreaming.value = false

          // Keep maximum 2 QnA pairs (4 messages total). If 3rd question pair is generated, remove 1st pair.
          if (messages.value.length > 4) {
            messages.value = messages.value.slice(messages.value.length - 4)
          }
        }
      )
    } catch (err) {
      console.error('Error in askQuestion:', err)
      messages.value.push({
        role: 'assistant',
        content: 'AI service is temporarily unavailable. Please try again.'
      })
    } finally {
      streamingText.value = ''
      isStreaming.value = false
    }
  }

  const openWidget = () => {
    isWidgetOpen.value = true
  }

  const closeWidget = () => {
    isWidgetOpen.value = false
    isWidgetExpanded.value = false
  }

  const toggleExpand = () => {
    isWidgetExpanded.value = !isWidgetExpanded.value
  }

  const resetState = () => {
    profile.value = null
    isProfileLoaded.value = false
    messages.value = []
    currentSessionId.value = ''
    streamingText.value = ''
    isStreaming.value = false
  }

  return {
    profile,
    isProfileLoaded,
    isSavingProfile,
    messages,
    isStreaming,
    streamingText,
    currentSessionId,
    answerStyle,
    isWidgetOpen,
    isWidgetExpanded,
    isMockInterviewMode,
    detectedQuestion,
    detectedQuestionType,
    autoAnswerStatus,
    setMockInterviewQuestion,
    fetchProfile,
    saveProfile,
    fetchHistory,
    clearHistory,
    askQuestion,
    openWidget,
    closeWidget,
    toggleExpand,
    resetState
  }
})
