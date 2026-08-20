import { ref, onUnmounted } from 'vue'

export type VoiceState =
  | 'IDLE'
  | 'REQUESTING_PERMISSION'
  | 'LISTENING'
  | 'SPEECH_DETECTED'
  | 'PROCESSING'
  | 'ANSWER_READY'
  | 'SILENCE_WARNING'
  | 'MIC_ERROR'
  | 'NETWORK_ERROR'

export type AIInterviewerState =
  | 'AI_ASKING_QUESTION'
  | 'AI_LISTENING'
  | 'AI_ANALYZING'
  | 'AI_GENERATING_ANSWER'
  | 'AI_READY'

export function useInterviewEngine() {
  const voiceState = ref<VoiceState>('IDLE')
  const aiState = ref<AIInterviewerState>('AI_READY')
  
  const interimTranscript = ref<string>('')
  const finalTranscript = ref<string>('')
  const currentQuestion = ref<string>('')

  const silenceSeconds = ref<number>(0)
  const speakingSeconds = ref<number>(0)
  const silenceMessage = ref<string>('')
  const showSilenceModal = ref<boolean>(false)

  const isTTSActive = ref<boolean>(false)
  const isSpeechSupported = ref<boolean>(false)

  let silenceTimerId: any = null
  let speakingTimerId: any = null
  let recognitionInstance: any = null

  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (SpeechRecognition) {
    isSpeechSupported.value = true
    try {
      recognitionInstance = new SpeechRecognition()
      recognitionInstance.continuous = true
      recognitionInstance.interimResults = true
      recognitionInstance.lang = 'en-US'

      recognitionInstance.onstart = () => {
        if (!isTTSActive.value) {
          voiceState.value = 'LISTENING'
          startSilenceTimer()
        }
      }

      recognitionInstance.onspeechstart = () => {
        if (isTTSActive.value) return
        voiceState.value = 'SPEECH_DETECTED'
        resetSilenceTimer()
      }

      recognitionInstance.onresult = (event: any) => {
        if (isTTSActive.value) return
        voiceState.value = 'SPEECH_DETECTED'
        resetSilenceTimer()

        let interim = ''
        let final = ''

        for (let i = 0; i < event.results.length; i++) {
          const res = event.results[i]
          const trans = res[0]?.transcript || ''
          if (res.isFinal) {
            final += trans + ' '
          } else {
            interim += trans + ' '
          }
        }

        interimTranscript.value = interim.trim()
        if (final.trim()) {
          finalTranscript.value = final.trim()
        }
      }

      recognitionInstance.onerror = (event: any) => {
        console.warn('Speech Engine Error:', event.error)
        if (event.error === 'not-allowed') {
          voiceState.value = 'MIC_ERROR'
        } else if (event.error === 'no-speech') {
          // Keep listening state without failing
        } else {
          voiceState.value = 'MIC_ERROR'
        }
      }

      recognitionInstance.onend = () => {
        if (voiceState.value === 'SPEECH_DETECTED' || voiceState.value === 'LISTENING') {
          if (!isTTSActive.value) {
            try {
              recognitionInstance.start()
            } catch (e) {}
          }
        }
      }
    } catch (err) {
      console.warn('Failed to init speech recognition:', err)
    }
  }

  const startListening = () => {
    if (isTTSActive.value) return
    stopSilenceTimer()
    silenceSeconds.value = 0
    showSilenceModal.value = false

    if (recognitionInstance) {
      try {
        voiceState.value = 'LISTENING'
        aiState.value = 'AI_LISTENING'
        recognitionInstance.start()
      } catch (e) {
        voiceState.value = 'LISTENING'
      }
    }
    startSilenceTimer()
    startSpeakingTimer()
  }

  const stopListening = () => {
    stopSilenceTimer()
    stopSpeakingTimer()
    if (recognitionInstance) {
      try {
        recognitionInstance.stop()
      } catch (e) {}
    }
    if (voiceState.value !== 'PROCESSING') {
      voiceState.value = 'IDLE'
    }
  }

  const getAvailableVoice = () => {
    if (!('speechSynthesis' in window)) return null
    const voices = window.speechSynthesis.getVoices()
    return voices.find(v => v.lang.startsWith('en') || v.name.includes('English') || v.name.includes('Google') || v.name.includes('Natural')) || voices[0] || null
  }

  if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
      getAvailableVoice()
    }
  }

  const speakQuestionTTS = (text: string, onEnd?: () => void) => {
    currentQuestion.value = text
    isTTSActive.value = true
    aiState.value = 'AI_ASKING_QUESTION'
    stopListening()

    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel()
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume()
        }

        const cleanText = text
          .replace(/###?\s*/g, '')
          .replace(/\*\*([^*]+)\*\*/g, '$1')
          .replace(/👉\s*"/g, '')
          .replace(/`/g, '')

        const utterance = new SpeechSynthesisUtterance(cleanText)
        const voice = getAvailableVoice()
        if (voice) {
          utterance.voice = voice
        }
        utterance.rate = 0.95
        utterance.pitch = 1.0
        utterance.volume = 1.0

        utterance.onend = () => {
          isTTSActive.value = false
          aiState.value = 'AI_LISTENING'
          startListening()
          if (onEnd) onEnd()
        }

        utterance.onerror = (err) => {
          console.warn('TTS Synthesis Error:', err)
          isTTSActive.value = false
          aiState.value = 'AI_LISTENING'
          startListening()
          if (onEnd) onEnd()
        }

        window.speechSynthesis.speak(utterance)
      } catch (err) {
        console.warn('TTS Execution Error:', err)
        isTTSActive.value = false
        aiState.value = 'AI_LISTENING'
        startListening()
        if (onEnd) onEnd()
      }
    } else {
      isTTSActive.value = false
      aiState.value = 'AI_LISTENING'
      startListening()
      if (onEnd) onEnd()
    }
  }

  const startSilenceTimer = () => {
    stopSilenceTimer()
    silenceSeconds.value = 0
    silenceTimerId = setInterval(() => {
      silenceSeconds.value++
      if (silenceSeconds.value < 5) {
        silenceMessage.value = 'Waiting for answer...'
      } else if (silenceSeconds.value >= 5 && silenceSeconds.value < 15) {
        silenceMessage.value = 'Still waiting... Take your time.'
      } else {
        silenceMessage.value = 'Take your time answering.'
      }
    }, 1000)
  }

  const resetSilenceTimer = () => {
    silenceSeconds.value = 0
    showSilenceModal.value = false
    silenceMessage.value = 'Your voice is being received'
  }

  const stopSilenceTimer = () => {
    if (silenceTimerId) {
      clearInterval(silenceTimerId)
      silenceTimerId = null
    }
  }

  const startSpeakingTimer = () => {
    stopSpeakingTimer()
    speakingTimerId = setInterval(() => {
      if (voiceState.value === 'SPEECH_DETECTED' || interimTranscript.value.length > 0 || finalTranscript.value.length > 0) {
        speakingSeconds.value++
      }
    }, 1000)
  }

  const stopSpeakingTimer = () => {
    if (speakingTimerId) {
      clearInterval(speakingTimerId)
      speakingTimerId = null
    }
  }

  const resetTranscripts = () => {
    interimTranscript.value = ''
    finalTranscript.value = ''
    speakingSeconds.value = 0
  }

  onUnmounted(() => {
    stopSilenceTimer()
    stopSpeakingTimer()
    stopListening()
  })

  return {
    voiceState,
    aiState,
    interimTranscript,
    finalTranscript,
    currentQuestion,
    silenceSeconds,
    speakingSeconds,
    silenceMessage,
    showSilenceModal,
    isTTSActive,
    isSpeechSupported,
    startListening,
    stopListening,
    speakQuestionTTS,
    resetSilenceTimer,
    stopSilenceTimer,
    resetTranscripts
  }
}
