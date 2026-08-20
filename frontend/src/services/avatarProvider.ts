export type AvatarState = 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'WAITING' | 'FINISHED'
export type AvatarGender = 'male' | 'female'

export interface AvatarOptions {
  gender: AvatarGender
  name: string
  voice: string
  role: string
  style: string
  avatarId?: string
}

export abstract class AvatarProvider {
  protected options: AvatarOptions

  constructor(options: AvatarOptions) {
    this.options = options
  }

  abstract initialize(containerElement?: HTMLElement): Promise<void>
  abstract start(): Promise<void>
  abstract speak(text: string, onEnd?: () => void): Promise<void>
  abstract stop(): void
  abstract setVoice(voice: string): void
  abstract setGender(gender: AvatarGender): void
  abstract destroy(): void
}

/**
 * WebSpeech / Canvas / High-Fidelity SVG Realistic AI Avatar Provider
 */
export class CanvasWebSpeechAvatarProvider extends AvatarProvider {
  private utterance: SpeechSynthesisUtterance | null = null
  private currentOnEnd: (() => void) | null = null
  private speakingStateCallback: ((state: AvatarState) => void) | null = null

  constructor(options: AvatarOptions, onStateChange?: (state: AvatarState) => void) {
    super(options)
    this.speakingStateCallback = onStateChange || null
  }

  async initialize(_containerElement?: HTMLElement): Promise<void> {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
  }

  async start(): Promise<void> {
    if (this.speakingStateCallback) this.speakingStateCallback('IDLE')
  }

  async speak(text: string, onEnd?: () => void): Promise<void> {
    return new Promise((resolve) => {
      this.currentOnEnd = onEnd || null
      if (this.speakingStateCallback) this.speakingStateCallback('SPEAKING')

      if (!('speechSynthesis' in window)) {
        if (this.speakingStateCallback) this.speakingStateCallback('LISTENING')
        if (onEnd) onEnd()
        resolve()
        return
      }

      window.speechSynthesis.cancel()
      const cleanText = text.replace(/[*_#`~]/g, '')
      this.utterance = new SpeechSynthesisUtterance(cleanText)
      this.utterance.rate = 0.95
      this.utterance.pitch = this.options.gender === 'female' ? 1.15 : 0.88

      const voices = window.speechSynthesis.getVoices()
      if (voices.length > 0) {
        let matchedVoice = null
        if (this.options.gender === 'female') {
          matchedVoice = voices.find(v => (v.name.includes('Female') || v.name.includes('Zira') || v.name.includes('Google UK English Female') || v.name.includes('Samantha') || v.name.includes('Victoria') || v.name.includes('Karen')) && v.lang.startsWith('en'))
        } else {
          matchedVoice = voices.find(v => (v.name.includes('Male') || v.name.includes('David') || v.name.includes('Google UK English Male') || v.name.includes('Daniel') || v.name.includes('George') || v.name.includes('Alex')) && v.lang.startsWith('en'))
        }
        if (!matchedVoice) {
          matchedVoice = voices.find(v => v.lang.startsWith('en'))
        }
        if (matchedVoice) {
          this.utterance.voice = matchedVoice
        }
      }

      this.utterance.onend = () => {
        if (this.speakingStateCallback) this.speakingStateCallback('LISTENING')
        if (this.currentOnEnd) this.currentOnEnd()
        resolve()
      }

      this.utterance.onerror = (err) => {
        console.warn('Avatar TTS error:', err)
        if (this.speakingStateCallback) this.speakingStateCallback('LISTENING')
        if (this.currentOnEnd) this.currentOnEnd()
        resolve()
      }

      window.speechSynthesis.speak(this.utterance)
    })
  }

  stop(): void {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
    if (this.speakingStateCallback) this.speakingStateCallback('LISTENING')
    if (this.currentOnEnd) {
      this.currentOnEnd()
      this.currentOnEnd = null
    }
  }

  setVoice(voice: string): void {
    this.options.voice = voice
  }

  setGender(gender: AvatarGender): void {
    this.options.gender = gender
  }

  destroy(): void {
    this.stop()
  }
}
