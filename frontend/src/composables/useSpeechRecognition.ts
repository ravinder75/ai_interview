import { ref, onUnmounted } from 'vue'

export type SpeechState = 'IDLE' | 'LISTENING' | 'PROCESSING' | 'FINALIZED' | 'ERROR'

export function useSpeechRecognition() {
  const isListening = ref<boolean>(false)
  const transcript = ref<string>('')
  const micStatus = ref<string>('Microphone ready')
  const speechState = ref<SpeechState>('IDLE')
  const isSupported = ref<boolean>(false)
  const hasHardwareMic = ref<boolean>(true)
  const errorMessage = ref<string>('')

  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  let recognitionInstance: any = null
  let debounceTimer: any = null

  if (SpeechRecognition) {
    isSupported.value = true
    try {
      recognitionInstance = new SpeechRecognition()
      recognitionInstance.continuous = true
      recognitionInstance.interimResults = true
      recognitionInstance.lang = 'en-US'

      recognitionInstance.onstart = () => {
        isListening.value = true
        speechState.value = 'LISTENING'
        micStatus.value = '🟢 Listening...'
        errorMessage.value = ''
      }

      recognitionInstance.onresult = (event: any) => {
        speechState.value = 'LISTENING'
        let currentText = ''
        for (let i = event.resultIndex; i < event.results.length; i++) {
          currentText += event.results[i][0].transcript
        }
        if (currentText.trim()) {
          transcript.value = currentText.trim()
        }

        if (debounceTimer) clearTimeout(debounceTimer)
        debounceTimer = setTimeout(() => {
          if (transcript.value.trim() && isListening.value) {
            speechState.value = 'PROCESSING'
            micStatus.value = '🟡 Processing transcription...'
          }
        }, 1200)
      }

      recognitionInstance.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error)
        speechState.value = 'ERROR'
        isListening.value = false

        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          errorMessage.value = 'Microphone permission is blocked. Allow microphone access for Interview Bit and try again.'
          micStatus.value = '🔴 Permission Denied'
        } else if (event.error === 'no-speech') {
          micStatus.value = '🟡 No speech detected'
          speechState.value = 'IDLE'
        } else {
          errorMessage.value = `Microphone error: ${event.error}`
          micStatus.value = '🔴 Microphone Unavailable'
        }
      }

      recognitionInstance.onend = () => {
        isListening.value = false
        if (speechState.value === 'LISTENING' || speechState.value === 'PROCESSING') {
          speechState.value = 'FINALIZED'
          micStatus.value = '🔵 Answer ready'
        }
      }
    } catch (e) {
      console.warn('Failed to initialize Web Speech API:', e)
    }
  } else {
    micStatus.value = 'Web Speech API not supported in browser'
  }

  const start = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        hasHardwareMic.value = true
        stream.getTracks().forEach(t => t.stop())
      } catch (err: any) {
        speechState.value = 'ERROR'
        hasHardwareMic.value = false
        if (err.name === 'NotAllowedError') {
          errorMessage.value = 'Microphone permission is blocked. Allow microphone access in browser settings and try again.'
          micStatus.value = '🔴 Permission Blocked'
        } else {
          errorMessage.value = 'Microphone unavailable or not detected.'
          micStatus.value = '🔴 Mic Unavailable'
        }
        return
      }
    }

    if (recognitionInstance && !isListening.value) {
      try {
        transcript.value = ''
        recognitionInstance.start()
      } catch (err) {
        console.error('Error starting speech recognition:', err)
      }
    }
  }

  const stop = () => {
    if (recognitionInstance && isListening.value) {
      try {
        recognitionInstance.stop()
        speechState.value = 'FINALIZED'
        micStatus.value = '🔵 Stopped'
      } catch (err) {
        console.error('Error stopping speech recognition:', err)
      }
    }
  }

  const clear = () => {
    transcript.value = ''
    speechState.value = 'IDLE'
    micStatus.value = 'Microphone ready'
  }

  onUnmounted(() => {
    if (debounceTimer) clearTimeout(debounceTimer)
    if (recognitionInstance && isListening.value) {
      recognitionInstance.stop()
    }
  })

  return {
    isListening,
    transcript,
    micStatus,
    speechState,
    isSupported,
    hasHardwareMic,
    errorMessage,
    start,
    stop,
    clear
  }
}
