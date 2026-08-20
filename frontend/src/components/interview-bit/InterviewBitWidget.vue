<template>
  <div
    ref="widgetWrapper"
    class="fixed z-50 font-sans select-none transition-all duration-300"
    :style="[
      widgetPositionStyle,
      isStealthMode ? {
        opacity: isStealthRevealed ? '0.95' : '0.0',
        visibility: isStealthRevealed ? 'visible' : 'hidden',
        pointerEvents: isStealthRevealed ? 'auto' : 'none',
        boxShadow: 'none',
        transition: 'opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
      } : {
        opacity: '1.0',
        visibility: 'visible',
        pointerEvents: 'auto',
        transition: 'opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
      }
    ]"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    @keydown.esc="store.closeWidget"
    tabindex="-1"
  >
    
    <!-- 1. DRAGGABLE COLLAPSED PILL BUTTON -->
    <div
      v-if="!store.isWidgetOpen"
      @mousedown="startDragButton"
      class="group flex items-center gap-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-700 text-white font-bold text-xs shadow-xl shadow-purple-600/40 border border-purple-400/40 hover:scale-105 transition-transform duration-200 cursor-grab active:cursor-grabbing select-none"
      title="Drag to move anywhere • Click to open • Alt+S for Stealth"
    >
      <span class="text-sm pointer-events-none">🎯</span>
      <span class="tracking-wide font-extrabold flex items-center gap-1.5 pointer-events-none text-xs">
        Interview Bit
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
      </span>
      <span class="text-[9px] opacity-70 text-slate-200 font-mono pointer-events-none ml-1">⋮⋮</span>
    </div>

    <!-- 2. DRAGGABLE OPEN WIDGET WINDOW -->
    <div
      v-else
      :class="[
        'glass-card rounded-3xl border border-slate-700/80 shadow-2xl bg-slate-950/95 backdrop-blur-xl flex flex-col transition-all duration-200 overflow-hidden',
        store.isWidgetExpanded
          ? 'w-[92vw] sm:w-[640px] h-[84vh] max-h-[740px]'
          : 'w-[90vw] sm:w-[420px] h-[550px]'
      ]"
    >
      <!-- Draggable Widget Header -->
      <div
        @mousedown="startDragWindow"
        class="p-3.5 px-4 bg-slate-900/95 border-b border-slate-800 flex items-center justify-between shrink-0 cursor-grab active:cursor-grabbing select-none"
        style="-webkit-app-region: drag;"
        title="Drag header to reposition anywhere on your screen"
      >
        <div class="flex items-center gap-2 pointer-events-none">
          <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-sm shadow-md">
            🎯
          </div>
          <div>
            <h3 class="text-xs font-extrabold text-slate-100 flex items-center gap-1.5">
              <span>Interview Bit</span>
            </h3>
          </div>
        </div>

        <!-- Controls: Stealth, Pop-out Detached Window, Expand, Minimize, Close -->
        <div class="flex items-center gap-1 text-slate-400" style="-webkit-app-region: no-drag;" @mousedown.stop>

          <button
            @click="toggleStealthMode"
            class="p-1 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition"
            :title="isStealthMode ? 'Stealth Mode Active • Press Alt+S or Alt+H to toggle' : 'Enable Stealth Mode • Alt+S'"
          >
            <EyeOff v-if="isStealthMode" class="w-3.5 h-3.5 text-slate-400" />
            <Eye v-else class="w-3.5 h-3.5 text-slate-400" />
          </button>

          <button
            @click="openDetachedWindow"
            class="p-1 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition"
            title="Pop-out Independent Window (100% Anti-Screen-Share proof)"
          >
            <ExternalLink class="w-3.5 h-3.5 text-slate-400" />
          </button>

          <button
            @click="store.toggleExpand"
            class="p-1 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition"
            :title="store.isWidgetExpanded ? 'Restore' : 'Expand'"
          >
            <Maximize2 v-if="!store.isWidgetExpanded" class="w-3.5 h-3.5" />
            <Minimize2 v-else class="w-3.5 h-3.5" />
          </button>
          
          <button
            @click="store.closeWidget"
            class="p-1 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
            title="Close (Esc)"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Messages Stream Area / Mock Interview Auto Answer Container -->
      <div ref="chatContainer" class="flex-1 p-4 overflow-y-auto space-y-4 text-xs select-text ib-answer-scroll">
        
        <!-- MOCK INTERVIEW AUTO-DETECTED MODE VIEW -->
        <div v-if="store.isMockInterviewMode" class="space-y-4 flex-1 flex flex-col min-h-0">
          <!-- Detected Question Header Card -->
          <div class="p-3.5 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 space-y-1.5 shadow-sm shrink-0">
            <div class="flex items-center justify-between text-[10px] text-indigo-400 font-bold uppercase tracking-wider">
              <span>DETECTED QUESTION</span>
              <span class="flex items-center gap-1 text-emerald-400 font-mono font-bold">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                ● Question Detected
              </span>
            </div>
            <p class="text-xs text-slate-100 font-medium leading-relaxed">
              {{ store.detectedQuestion || 'Waiting for AI Interviewer to ask next question...' }}
            </p>
          </div>

          <!-- Divider -->
          <div class="border-t border-slate-800/80 my-1 shrink-0"></div>

          <!-- Auto-Generated Answer Container -->
          <div class="space-y-1.5 flex-1 flex flex-col min-h-0 overflow-hidden">
            <div class="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-slate-400 px-1 shrink-0">
              <span>AI ANSWER</span>
              <span v-if="store.isStreaming" class="text-indigo-400 flex items-center gap-1 font-mono">
                <Loader2 class="w-3 h-3 animate-spin" />
                ● Generating answer...
              </span>
              <span v-else-if="store.messages.length" class="text-emerald-400 font-mono">
                ● AI Answer Ready
              </span>
              <span v-else class="text-slate-500 font-mono">
                ● Waiting
              </span>
            </div>

            <!-- Scrollable Answer Panel -->
            <div class="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-slate-200 shadow-inner flex-1 overflow-y-auto space-y-3 ib-answer-scroll select-text">
              <div v-if="store.isStreaming && !store.streamingText" class="flex items-center gap-2 text-indigo-400 font-mono text-xs py-2">
                <Loader2 class="w-4 h-4 animate-spin" />
                <span>Generating ultra-fast answer...</span>
              </div>
              
              <MarkdownRenderer v-else-if="store.streamingText" :content="store.streamingText + (store.isStreaming ? ' ▌' : '')" />

              <div v-else-if="latestAssistantMessage" class="space-y-2">
                <MarkdownRenderer :content="latestAssistantMessage.content" />
                
                <div class="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
                  <button
                    @click="copyText(latestAssistantMessage.content, 999)"
                    class="hover:text-slate-100 flex items-center gap-1 transition"
                  >
                    <Check v-if="copiedIdx === 999" class="w-3 h-3 text-emerald-400" />
                    <Copy v-else class="w-3 h-3" />
                    <span>{{ copiedIdx === 999 ? '✓ Copied' : 'Copy Answer' }}</span>
                  </button>

                  <span class="text-[10px] text-slate-500 font-mono">Mock Interview Practice Companion</span>
                </div>
              </div>

              <div v-else class="text-slate-500 text-center py-6 text-xs font-mono">
                AI interviewer is preparing the question...
              </div>
            </div>
          </div>

          <!-- Divider -->
          <div class="border-t border-slate-800/80 my-1 shrink-0"></div>

          <!-- Status Indicator Card -->
          <div class="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-[10px] shrink-0 px-3">
            <span class="text-slate-400 font-bold uppercase tracking-wider">Status:</span>
            <div class="flex items-center gap-3 font-mono font-bold">
              <span :class="store.detectedQuestion ? 'text-emerald-400' : 'text-slate-500'">
                ● Question Detected
              </span>
              <span :class="(store.messages.length || store.streamingText) ? 'text-emerald-400' : 'text-slate-500'">
                ● AI Answer Ready
              </span>
            </div>
          </div>
        </div>

        <!-- STANDALONE CHATBOT MODE (UNTOUCHED) -->
        <template v-else>
          <!-- Resume Profile Card (shown when profile is loaded) -->
          <div v-if="!store.messages.length && !store.isStreaming && store.isProfileLoaded && store.profile" class="space-y-3">
            <div class="space-y-1.5">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Ask me anything:</span>
              <div class="flex flex-col gap-1.5 text-[11px]">
                <button
                  v-for="s in quickStarters"
                  :key="s"
                  @click="askQuick(s)"
                  class="p-2 rounded-xl bg-slate-950 hover:bg-indigo-600/20 border border-slate-800 text-slate-300 text-left font-mono transition truncate"
                >
                  "{{ s }}"
                </button>
              </div>
            </div>
          </div>

          <!-- Welcome Prompt (no profile loaded yet) -->
          <div v-else-if="!store.messages.length && !store.isStreaming" class="space-y-3 p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
            <p class="font-bold text-indigo-300">👋 Hi! I'm your Interview Bit practice companion.</p>
            <p class="text-slate-300 leading-relaxed text-[11px]">
              Upload your resume on the Interview Bit or Mock Interview page to personalize your practice.
            </p>
            <div class="space-y-1.5 pt-1">
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Quick Practice Starters:</span>
              <div class="flex flex-col gap-1.5 text-[11px]">
                <button
                  v-for="s in quickStarters"
                  :key="s"
                  @click="askQuick(s)"
                  class="p-2 rounded-xl bg-slate-950 hover:bg-indigo-600/20 border border-slate-800 text-slate-300 text-left font-mono transition truncate"
                >
                  "{{ s }}"
                </button>
              </div>
            </div>
          </div>

          <!-- Dynamic Message History -->
          <div
            v-for="(msg, idx) in store.messages"
            :key="idx"
            :class="[
              'flex flex-col space-y-1.5',
              msg.role === 'user' ? 'items-end' : 'items-start'
            ]"
          >
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-1">
              {{ msg.role === 'user' ? 'You' : 'AI ANSWER' }}
            </span>

            <div
              :class="[
                'p-3.5 rounded-2xl leading-relaxed max-w-[92%]',
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-tr-none shadow-md font-sans text-xs'
                  : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none shadow-inner'
              ]"
            >
              <div v-if="msg.role === 'user'" class="whitespace-pre-wrap">
                {{ msg.content }}
              </div>
              <div v-else class="space-y-2">
                <MarkdownRenderer :content="msg.content" />

                <div class="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
                  <button
                    @click="copyText(msg.content, idx)"
                    class="hover:text-slate-100 flex items-center gap-1 transition"
                  >
                    <Check v-if="copiedIdx === idx" class="w-3 h-3 text-emerald-400" />
                    <Copy v-else class="w-3 h-3" />
                    <span>{{ copiedIdx === idx ? '✓ Copied' : 'Copy' }}</span>
                  </button>

                  <button
                    @click="regenerateAnswer(store.messages[idx - 1]?.content || '')"
                    class="hover:text-slate-100 flex items-center gap-1 transition"
                    v-if="idx > 0"
                  >
                    <RotateCw class="w-3 h-3 text-indigo-400" />
                    <span>Regenerate</span>
                  </button>
                </div>

                <div v-if="msg.follow_ups && msg.follow_ups.length" class="space-y-1 pt-1.5">
                  <span class="text-[10px] text-purple-300 font-bold uppercase tracking-wider block">Possible Follow-ups:</span>
                  <div class="flex flex-wrap gap-1">
                    <button
                      v-for="fu in msg.follow_ups"
                      :key="fu"
                      @click="askQuick(fu)"
                      class="px-2 py-1 rounded-lg bg-slate-950 hover:bg-purple-600/30 border border-slate-800 text-purple-200 text-[10px] text-left transition"
                    >
                      • {{ fu }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Live Streaming Typing State -->
          <div v-if="store.isStreaming" class="flex flex-col items-start space-y-1 max-w-[92%]">
            <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-400 px-1">AI ANSWER Generating...</span>
            <div class="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none space-y-2 shadow-inner w-full">
              <div v-if="!store.streamingText" class="flex items-center gap-2 text-indigo-400 font-mono text-xs">
                <Loader2 class="w-3.5 h-3.5 animate-spin" />
                <span>Thinking & analyzing candidate profile...</span>
              </div>
              <MarkdownRenderer v-else :content="store.streamingText + ' ▌'" />
            </div>
          </div>
        </template>

      </div>

      <!-- Input Area (Hidden during Mock Interview Mode) -->
      <div v-if="!store.isMockInterviewMode" class="p-3 bg-slate-900 border-t border-slate-800 space-y-2 shrink-0 select-text">
        <div v-if="speech.isListening.value" class="flex items-center justify-between text-[11px] text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2.5 py-1 rounded-lg">
          <span class="flex items-center gap-1.5 font-bold">
            <span class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span>
            Listening to your question...
          </span>
          <button @click="speech.stop" class="text-slate-300 hover:text-white font-bold">Stop</button>
        </div>

        <form @submit.prevent="submitQuestion" class="flex items-center gap-2">
          <input
            ref="inputField"
            v-model="inputQuery"
            type="text"
            placeholder="Ask anything... (e.g. Reverse a linked list, Tell me about my project)"
            class="flex-1 bg-slate-950 border border-slate-700 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 outline-none transition"
          />

          <button
            type="button"
            @click="toggleSpeech"
            :class="[
              'p-2.5 rounded-xl border transition flex items-center justify-center shrink-0',
              speech.isListening.value ? 'bg-rose-600 text-white border-rose-500 animate-pulse' : 'bg-slate-950 border-slate-700 text-slate-300 hover:text-white'
            ]"
            title="🎙️ Speak Question"
          >
            <Mic class="w-3.5 h-3.5" />
          </button>

          <button
            type="submit"
            :disabled="store.isStreaming || !inputQuery.trim()"
            class="btn-primary px-3.5 py-2 text-xs font-bold flex items-center gap-1.5 shrink-0 shadow-md shadow-indigo-600/30"
          >
            <Loader2 v-if="store.isStreaming" class="w-3.5 h-3.5 animate-spin" />
            <Send v-else class="w-3.5 h-3.5" />
            <span>Ask</span>
          </button>
        </form>

        <div class="flex items-center justify-between text-[10px] text-slate-500 px-1">
          <span>🎯 Drag anywhere • Resume Personalized</span>
          <button @click="store.clearHistory" class="hover:text-slate-300 transition">Clear Chat</button>
        </div>
      </div>
      <div v-else class="p-2.5 bg-slate-900 border-t border-slate-800 text-[10px] text-slate-400 flex items-center justify-between px-4 shrink-0">
        <span>🎯 Mock Practice Environment</span>
        <span class="text-indigo-400 font-mono font-bold">Interview Bit remains draggable.</span>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import {
  X,
  Maximize2,
  Minimize2,
  Mic,
  Send,
  Loader2,
  Copy,
  Check,
  RotateCw,
  Eye,
  EyeOff,
  ExternalLink
} from 'lucide-vue-next'
import { useInterviewBitStore } from '../../stores/interviewBit'
import { useSpeechRecognition } from '../../composables/useSpeechRecognition'
import MarkdownRenderer from '../MarkdownRenderer.vue'

const store = useInterviewBitStore()
const speech = useSpeechRecognition()

const isStealthMode = ref<boolean>(false)
const isStealthRevealed = ref<boolean>(false)
let autoVanishTimeout: any = null

const scheduleAutoVanish = () => {
  if (autoVanishTimeout) clearTimeout(autoVanishTimeout)
  autoVanishTimeout = setTimeout(() => {
    if (isStealthMode.value) {
      isStealthRevealed.value = false
    }
  }, 8000) // Auto-vanishes back to 0.00% opacity after 8 seconds of inactivity
}

const toggleStealthMode = () => {
  isStealthMode.value = !isStealthMode.value
  isStealthRevealed.value = false // Instantly vanish to 0.00% opacity on Eye button click
  if (autoVanishTimeout) clearTimeout(autoVanishTimeout)
}

const openDetachedWindow = () => {
  window.open(
    '/interview-bit?mode=detached',
    'InterviewBitStealth',
    'width=440,height=600,top=100,left=100,resizable=yes,scrollbars=yes,status=no'
  )
}

const handleMouseEnter = () => {
  if (isStealthMode.value) {
    isStealthRevealed.value = true
    scheduleAutoVanish()
  }
}

const handleMouseLeave = () => {
  if (isStealthMode.value) {
    isStealthRevealed.value = false
    if (autoVanishTimeout) clearTimeout(autoVanishTimeout)
  }
}

// Global hotkeys (Alt+S or Alt+H) for 100% Invisible Stealth Mode toggle
onMounted(() => {
  window.addEventListener('keydown', (e: KeyboardEvent) => {
    if (e.altKey && (e.key === 's' || e.key === 'S' || e.key === 'h' || e.key === 'H')) {
      e.preventDefault()
      if (!isStealthMode.value) {
        toggleStealthMode()
      } else {
        // Toggle reveal state when in stealth mode
        isStealthRevealed.value = !isStealthRevealed.value
        if (isStealthRevealed.value) scheduleAutoVanish()
      }
    }
  })
})

const widgetWrapper = ref<HTMLElement | null>(null)
const inputField = ref<HTMLInputElement | null>(null)
const chatContainer = ref<HTMLElement | null>(null)
const inputQuery = ref<string>('')
const copiedIdx = ref<number | null>(null)

const latestAssistantMessage = computed(() => {
  for (let i = store.messages.length - 1; i >= 0; i--) {
    if (store.messages[i].role === 'assistant') {
      return store.messages[i]
    }
  }
  return null
})

// Drag Position Coordinates
const posX = ref<number | null>(null)
const posY = ref<number | null>(null)
let isDragging = false
let dragStartX = 0
let dragStartY = 0
let startPosX = 0
let startPosY = 0
let hasMoved = false

const widgetPositionStyle = computed(() => {
  if (posX.value !== null && posY.value !== null) {
    return {
      left: `${posX.value}px`,
      top: `${posY.value}px`,
      right: 'auto',
      bottom: 'auto'
    }
  }
  return {
    right: '24px',
    bottom: '24px'
  }
})

// Drag Handlers for Collapsed Pill Button
const startDragButton = (e: MouseEvent) => {
  if (e.button !== 0) return // Only primary click
  isDragging = true
  hasMoved = false
  dragStartX = e.clientX
  dragStartY = e.clientY

  const rect = widgetWrapper.value?.getBoundingClientRect()
  startPosX = rect ? rect.left : window.innerWidth - 180
  startPosY = rect ? rect.top : window.innerHeight - 80

  window.addEventListener('mousemove', onDragging)
  window.addEventListener('mouseup', stopDragButton)
}

const onDragging = (e: MouseEvent) => {
  if (!isDragging) return
  const dx = e.clientX - dragStartX
  const dy = e.clientY - dragStartY

  if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
    hasMoved = true
  }

  const newX = Math.max(10, Math.min(window.innerWidth - 160, startPosX + dx))
  const newY = Math.max(10, Math.min(window.innerHeight - 60, startPosY + dy))

  posX.value = newX
  posY.value = newY
}

const stopDragButton = () => {
  isDragging = false
  window.removeEventListener('mousemove', onDragging)
  window.removeEventListener('mouseup', stopDragButton)

  // If clicked without dragging, open widget!
  if (!hasMoved) {
    openAndFocus()
  }
}

// Drag Handlers for Open Window Header
const startDragWindow = (e: MouseEvent) => {
  if (e.button !== 0) return
  isDragging = true
  dragStartX = e.clientX
  dragStartY = e.clientY

  const rect = widgetWrapper.value?.getBoundingClientRect()
  startPosX = rect ? rect.left : window.innerWidth - 440
  startPosY = rect ? rect.top : window.innerHeight - 580

  window.addEventListener('mousemove', onDraggingWindow)
  window.addEventListener('mouseup', stopDragWindow)
}

const onDraggingWindow = (e: MouseEvent) => {
  if (!isDragging) return
  const dx = e.clientX - dragStartX
  const dy = e.clientY - dragStartY

  const width = store.isWidgetExpanded ? (window.innerWidth > 640 ? 640 : window.innerWidth * 0.92) : 420
  const height = store.isWidgetExpanded ? 700 : 550

  const newX = Math.max(10, Math.min(window.innerWidth - width - 10, startPosX + dx))
  const newY = Math.max(10, Math.min(window.innerHeight - height - 10, startPosY + dy))

  posX.value = newX
  posY.value = newY
}

const stopDragWindow = () => {
  isDragging = false
  window.removeEventListener('mousemove', onDraggingWindow)
  window.removeEventListener('mouseup', stopDragWindow)
}

const quickStarters = [
  "What is the difference between GET and POST?",
  "Explain my strongest project from my resume.",
  "Write a Python program to reverse a linked list.",
  "What is a Python dictionary and its complexity?",
  "A train travels 120 km in 2 hours. What is its speed?"
]

// Auto-sync voice transcription into input box
watch(speech.transcript, (newVal) => {
  if (newVal) {
    inputQuery.value = newVal
  }
})

const openAndFocus = async () => {
  store.openWidget()
  await nextTick()
  inputField.value?.focus()
  scrollToBottom()
}

const toggleSpeech = () => {
  if (speech.isListening.value) {
    speech.stop()
  } else {
    speech.start()
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const askQuick = (q: string) => {
  inputQuery.value = q
  submitQuestion()
}

const copyText = (text: string, idx: number) => {
  navigator.clipboard.writeText(text)
  copiedIdx.value = idx
  setTimeout(() => { copiedIdx.value = null }, 2000)
}

const regenerateAnswer = (lastQuestion: string) => {
  if (lastQuestion) {
    store.askQuestion(lastQuestion)
    scrollToBottom()
  }
}

const submitQuestion = async () => {
  const query = inputQuery.value.trim()
  if (!query || store.isStreaming) return

  if (speech.isListening.value) speech.stop()
  inputQuery.value = ''
  
  await store.askQuestion(query)
  scrollToBottom()
}

onMounted(async () => {
  if (!store.isProfileLoaded) {
    await store.fetchProfile()
  }
})
</script>

<style scoped>
.ib-answer-scroll {
  flex: 1 1 0%;
  min-height: 0;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  scroll-behavior: smooth;
}
.ib-answer-scroll pre {
  overflow-x: auto;
  max-width: 100%;
}
</style>
