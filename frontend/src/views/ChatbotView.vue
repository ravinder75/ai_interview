<template>
  <div class="flex h-[calc(100vh-5rem)] max-w-7xl mx-auto rounded-2xl border border-slate-800 overflow-hidden bg-slate-950">
    
    <!-- LEFT SIDEBAR (ChatGPT Style) -->
    <div class="w-72 bg-slate-900/90 border-r border-slate-800/80 flex flex-col shrink-0">
      
      <!-- New Chat & Search Header -->
      <div class="p-4 space-y-3 border-b border-slate-800/80">
        <button
          @click="createNewChat"
          :disabled="isCreatingChat"
          class="w-full py-2.5 px-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 transition"
        >
          <Plus class="w-4 h-4" />
          <span>+ New Chat</span>
        </button>

        <!-- Search Chats Input -->
        <div class="relative">
          <Search class="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search conversations..."
            class="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 outline-none placeholder-slate-500"
          />
        </div>
      </div>

      <!-- Conversations List grouped by Today / Yesterday / Older -->
      <div class="flex-1 overflow-y-auto p-3 space-y-4 text-xs">
        
        <div v-if="isSessionsLoading" class="text-center py-6 text-slate-500 font-mono flex items-center justify-center gap-2">
          <Loader2 class="w-4 h-4 animate-spin text-indigo-400" />
          <span>Loading chats...</span>
        </div>

        <div v-else-if="filteredGroupedSessions.length === 0" class="text-center py-8 text-slate-500 font-mono">
          No chat history found
        </div>

        <div v-else v-for="group in filteredGroupedSessions" :key="group.label" class="space-y-1">
          <h4 class="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-2 pt-1 font-mono">
            {{ group.label }}
          </h4>

          <div
            v-for="session in group.sessions"
            :key="session.session_id"
            :class="[
              'group relative flex items-center justify-between p-2.5 rounded-xl transition cursor-pointer font-medium text-xs',
              activeSessionId === session.session_id
                ? 'bg-indigo-600/20 text-indigo-200 border border-indigo-500/30 font-bold'
                : 'text-slate-300 hover:bg-slate-800/60 hover:text-white border border-transparent'
            ]"
            @click="selectSession(session.session_id)"
          >
            <div class="flex items-center gap-2 min-w-0 pr-6">
              <MessageSquare class="w-3.5 h-3.5 shrink-0 text-indigo-400" />
              
              <!-- Editing title state -->
              <input
                v-if="editingSessionId === session.session_id"
                v-model="editTitleInput"
                @keyup.enter="saveRenamedTitle(session.session_id)"
                @blur="saveRenamedTitle(session.session_id)"
                ref="editTitleRef"
                class="bg-slate-950 border border-indigo-500 text-slate-100 text-xs px-1.5 py-0.5 rounded outline-none w-full"
                @click.stop
              />
              <span v-else class="truncate">{{ session.title || 'New Chat' }}</span>
            </div>

            <!-- Session Actions Menu Button (Visible on hover and on active session) -->
            <div :class="['absolute right-2 transition flex items-center gap-1', activeSessionId === session.session_id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100']">
              <button
                @click.stop.prevent="startRenaming(session)"
                class="p-1 hover:text-indigo-300 text-slate-400"
                title="Rename Chat"
              >
                <Edit2 class="w-3 h-3" />
              </button>
              <button
                @click.stop.prevent="confirmDeleteSession(session.session_id)"
                class="p-1 hover:text-rose-400 text-slate-400"
                title="Delete Chat"
              >
                <Trash2 class="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>

      </div>

      <!-- Sidebar Footer (User Info & Logout) -->
      <div class="p-3 border-t border-slate-800/80 bg-slate-950/80 flex items-center justify-between text-xs">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-7 h-7 rounded-lg bg-indigo-600 text-white font-bold flex items-center justify-center shrink-0">
            {{ (authStore.user?.full_name || 'U').charAt(0).toUpperCase() }}
          </div>
          <div class="truncate min-w-0">
            <p class="font-bold text-slate-200 truncate">{{ authStore.user?.full_name || 'User' }}</p>
            <p class="text-[10px] text-slate-400 truncate">{{ authStore.user?.email }}</p>
          </div>
        </div>
      </div>

    </div>

    <!-- MAIN CHAT AREA -->
    <div class="flex-1 flex flex-col min-w-0 bg-slate-950">
      
      <!-- Top Header Bar -->
      <div class="p-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/50">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20">
            <Bot class="w-5 h-5" />
          </div>
          <div>
            <h2 class="text-sm font-bold text-slate-100 flex items-center gap-2">
              {{ currentSessionTitle }}
            </h2>
            <p class="text-[11px] text-slate-400">Interview Bit AI Technical & Resume Coach</p>
          </div>
        </div>

        <!-- Attached Resume Badge / Attachment Selector -->
        <div class="flex items-center gap-2 text-xs">
          <div v-if="activeResume" class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-indigo-600/15 border border-indigo-500/30 text-indigo-300">
            <FileText class="w-3.5 h-3.5" />
            <span class="font-semibold text-[11px] truncate max-w-[160px]">{{ activeResume.filename }}</span>
            <button @click="detachResume" class="text-slate-400 hover:text-rose-400 font-bold ml-1" title="Detach Resume">×</button>
          </div>

          <div class="relative">
            <button
              @click="showResumeMenu = !showResumeMenu"
              class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 font-bold text-xs flex items-center gap-1.5 transition"
            >
              <Paperclip class="w-3.5 h-3.5 text-indigo-400" />
              <span>📎 Attach Resume PDF</span>
            </button>

            <!-- Dropdown Menu for Resume Options -->
            <div v-if="showResumeMenu" class="absolute right-0 mt-2 w-64 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-50 p-2 text-xs space-y-2">
              <div class="font-bold text-slate-300 text-[11px] px-2 pt-1 border-b border-slate-800 pb-1">
                Select or Upload Resume PDF
              </div>

              <!-- List of User's Resumes -->
              <div v-if="userResumes.length" class="space-y-1 max-h-36 overflow-y-auto">
                <button
                  v-for="r in userResumes"
                  :key="r.id"
                  @click="selectExistingResume(r)"
                  class="w-full text-left p-2 rounded-lg hover:bg-slate-800 text-slate-300 font-medium truncate flex items-center justify-between"
                >
                  <span class="truncate">{{ r.filename }}</span>
                  <span v-if="activeResume?.id === r.id" class="text-emerald-400 font-bold text-[10px]">Active ✓</span>
                </button>
              </div>

              <div class="pt-1 border-t border-slate-800">
                <label class="w-full py-2 px-3 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 font-bold text-xs flex items-center justify-center gap-2 cursor-pointer transition">
                  <Upload class="w-3.5 h-3.5" />
                  <span>Upload PDF Resume</span>
                  <input type="file" ref="pdfInput" @change="onPdfSelected" accept=".pdf" class="hidden" />
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Messages Window Area -->
      <div ref="chatContainer" class="flex-1 p-6 overflow-y-auto space-y-4">
        
        <!-- Welcome Screen when no messages exist -->
        <div v-if="!messages.length && !isMessagesLoading" class="max-w-2xl mx-auto py-12 text-center space-y-6">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 mx-auto flex items-center justify-center text-white font-extrabold shadow-xl shadow-indigo-500/30">
            <Bot class="w-8 h-8" />
          </div>
          <div class="space-y-2">
            <h3 class="text-xl font-extrabold text-slate-100">How can Interview Bit AI help you today?</h3>
            <p class="text-xs text-slate-400">Ask technical concepts, code optimizations, or attach your PDF resume for personalized interview prep!</p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
            <button
              v-for="s in quickStarters"
              :key="s"
              @click="askQuick(s)"
              class="p-3.5 rounded-xl bg-slate-900 hover:bg-indigo-600/10 border border-slate-800 hover:border-indigo-500/40 text-slate-300 hover:text-white text-xs font-medium transition text-left space-y-1"
            >
              <p class="font-bold text-indigo-400 font-mono text-[11px]">"{{ s }}"</p>
            </button>
          </div>
        </div>

        <div v-if="isMessagesLoading" class="text-center py-12 font-mono text-slate-500 flex items-center justify-center gap-2">
          <Loader2 class="w-5 h-5 animate-spin text-indigo-400" />
          <span>Loading session messages...</span>
        </div>

        <!-- Dynamic Message History -->
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="[
            'flex items-start gap-3',
            msg.role === 'user' ? 'justify-end' : 'justify-start'
          ]"
        >
          <!-- Assistant Icon -->
          <div v-if="msg.role === 'assistant'" class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-md">
            <Bot class="w-5 h-5" />
          </div>

          <!-- Message Content Box -->
          <div
            :class="[
              'max-w-2xl p-4 rounded-2xl text-xs leading-relaxed',
              msg.role === 'user'
                ? 'bg-indigo-600 text-white rounded-br-none shadow-lg shadow-indigo-600/20 whitespace-pre-wrap font-sans'
                : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none font-mono space-y-2'
            ]"
          >
            <div v-if="msg.role === 'user'">{{ msg.content }}</div>
            <div v-else>
              <MarkdownRenderer :content="msg.content" />
              <div class="flex items-center justify-end pt-2 border-t border-slate-800/60 text-[10px] text-slate-400">
                <button
                  @click="copyText(msg.content, idx)"
                  class="hover:text-slate-200 flex items-center gap-1 transition"
                >
                  <Check v-if="copiedIdx === idx" class="w-3 h-3 text-emerald-400" />
                  <Copy v-else class="w-3 h-3" />
                  <span>{{ copiedIdx === idx ? '✓ Copied' : 'Copy' }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- User Icon -->
          <div v-if="msg.role === 'user'" class="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-0.5 font-bold text-xs">
            You
          </div>
        </div>

        <!-- Typing / Thinking Indicator -->
        <div v-if="isLoading" class="flex items-center gap-2 text-xs text-indigo-400 italic p-2 font-mono">
          <Loader2 class="w-4 h-4 animate-spin text-indigo-400" />
          <span>{{ statusMessage || 'AI is thinking...' }}</span>
        </div>

      </div>

      <!-- ChatGPT-Style Bottom Composer Bar -->
      <div class="p-4 border-t border-slate-800 bg-slate-950">
        <form @submit.prevent="sendMessage" class="relative bg-slate-900 border border-slate-800 focus-within:border-indigo-500 rounded-2xl p-3 transition shadow-xl space-y-2">
          
          <textarea
            v-model="inputQuery"
            @keydown.enter.exact.prevent="sendMessage"
            placeholder="Message Interview Bit... (Shift+Enter for line break)"
            rows="2"
            class="w-full bg-transparent text-slate-100 placeholder-slate-500 text-xs outline-none resize-none"
          ></textarea>

          <div class="flex items-center justify-between pt-1 border-t border-slate-800/60">
            <div class="flex items-center gap-2">
              <button
                type="button"
                @click="showResumeMenu = !showResumeMenu"
                class="p-2 rounded-xl text-slate-400 hover:text-indigo-300 hover:bg-slate-800 transition text-xs flex items-center gap-1 font-bold"
                title="Attach Resume PDF"
              >
                <Paperclip class="w-4 h-4" />
                <span class="hidden sm:inline font-sans font-normal text-[11px]">{{ activeResume ? activeResume.filename : 'Attach Resume PDF' }}</span>
              </button>

              <button
                type="button"
                @click="toggleSpeech"
                :class="[
                  'p-2 rounded-xl transition flex items-center justify-center',
                  speech.isListening.value ? 'bg-rose-600 text-white animate-pulse' : 'text-slate-400 hover:text-white hover:bg-slate-800'
                ]"
                title="🎙️ Speak"
              >
                <Mic class="w-4 h-4" />
              </button>
            </div>

            <button
              type="submit"
              :disabled="isLoading || !inputQuery.trim()"
              class="btn-primary px-5 py-2 text-xs font-bold flex items-center gap-2 shrink-0 shadow-lg shadow-indigo-600/30 disabled:opacity-50"
            >
              <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
              <Send v-else class="w-4 h-4" />
              <span>Send</span>
            </button>
          </div>

        </form>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { Plus, Search, MessageSquare, Edit2, Trash2, Bot, Send, Loader2, Mic, Copy, Check, Paperclip, FileText, Upload } from 'lucide-vue-next'
import { api } from '../services/api'
import { useAuthStore } from '../stores/authStore'
import { useSpeechRecognition } from '../composables/useSpeechRecognition'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'

interface ChatSession {
  id: number;
  session_id: string;
  title: string;
  active_resume_id?: number;
  created_at: string;
  updated_at?: string;
}

interface ChatMsg {
  role: 'user' | 'assistant';
  content: string;
}

const authStore = useAuthStore()
const speech = useSpeechRecognition()

const sessions = ref<ChatSession[]>([])
const activeSessionId = ref<string>('')
const messages = ref<ChatMsg[]>([])
const userResumes = ref<any[]>([])
const activeResume = ref<any>(null)

const searchQuery = ref<string>('')
const inputQuery = ref<string>('')
const isLoading = ref<boolean>(false)
const isSessionsLoading = ref<boolean>(false)
const isMessagesLoading = ref<boolean>(false)
const isCreatingChat = ref<boolean>(false)
const statusMessage = ref<string>('')

const editingSessionId = ref<string | null>(null)
const editTitleInput = ref<string>('')
const editTitleRef = ref<HTMLInputElement | null>(null)
const showResumeMenu = ref<boolean>(false)
const copiedIdx = ref<number | null>(null)
const chatContainer = ref<HTMLElement | null>(null)

const quickStarters = [
  "Explain Python decorators",
  "What is the difference between GET and POST?",
  "Write a Python function for Two Sum",
  "How to optimize SQL query indexing?"
]

const currentSessionTitle = computed(() => {
  const s = sessions.value.find(x => x.session_id === activeSessionId.value)
  return s ? s.title : 'Interview Bit AI Assistant'
})

// Group sessions by Today, Yesterday, Older
const filteredGroupedSessions = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  let list = sessions.value
  if (query) {
    list = list.filter(s => s.title.toLowerCase().includes(query))
  }

  const today: ChatSession[] = []
  const yesterday: ChatSession[] = []
  const older: ChatSession[] = []

  const now = new Date()
  const todayStr = now.toDateString()
  const yesterdayDate = new Date(now)
  yesterdayDate.setDate(yesterdayDate.getDate() - 1)
  const yesterdayStr = yesterdayDate.toDateString()

  for (const s of list) {
    const sDate = new Date(s.created_at || s.updated_at || Date.now()).toDateString()
    if (sDate === todayStr) {
      today.push(s)
    } else if (sDate === yesterdayStr) {
      yesterday.push(s)
    } else {
      older.push(s)
    }
  }

  const groups = []
  if (today.length) groups.push({ label: 'Today', sessions: today })
  if (yesterday.length) groups.push({ label: 'Yesterday', sessions: yesterday })
  if (older.length) groups.push({ label: 'Older', sessions: older })
  return groups
})

watch(speech.transcript, (newVal) => {
  if (newVal) {
    inputQuery.value = newVal
  }
})

const toggleSpeech = () => {
  if (speech.isListening.value) speech.stop()
  else speech.start()
}

const copyText = (text: string, idx: number) => {
  navigator.clipboard.writeText(text)
  copiedIdx.value = idx
  setTimeout(() => { copiedIdx.value = null }, 2000)
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// Fetch all chat sessions for authenticated user
const fetchSessions = async () => {
  isSessionsLoading.value = true
  try {
    const res = await api.get('/api/interview-bit/sessions')
    sessions.value = res.data
    if (!activeSessionId.value && sessions.value.length) {
      selectSession(sessions.value[0].session_id)
    } else if (!sessions.value.length) {
      await createNewChat()
    }
  } catch (err) {
    console.error('Failed to load chat sessions:', err)
  } finally {
    isSessionsLoading.value = false
  }
}

// Fetch user resumes
const fetchUserResumes = async () => {
  try {
    const res = await api.get('/api/resumes')
    userResumes.value = res.data
  } catch (err) {
    console.error('Failed to fetch resumes:', err)
  }
}

// Create New Chat Session
const createNewChat = async () => {
  isCreatingChat.value = true
  try {
    const res = await api.post('/api/interview-bit/sessions')
    const newSess: ChatSession = res.data
    // Prepend to sessions list and activate immediately
    sessions.value.unshift(newSess)
    activeSessionId.value = newSess.session_id
    messages.value = []
    activeResume.value = null
  } catch (err) {
    console.error('Failed to create new chat:', err)
  } finally {
    isCreatingChat.value = false
  }
}

// Select a Chat Session & Load Messages
const selectSession = async (sessionId: string) => {
  activeSessionId.value = sessionId
  isMessagesLoading.value = true
  messages.value = []
  try {
    const res = await api.get(`/api/interview-bit/sessions/${sessionId}`)
    const sess: any = res.data
    messages.value = (sess.messages || []).map((m: any) => ({
      role: m.role as 'user' | 'assistant',
      content: m.content
    }))
    
    // Set active resume if session has one
    if (sess.active_resume_id && userResumes.value.length) {
      activeResume.value = userResumes.value.find(r => r.id === sess.active_resume_id) || null
    } else {
      activeResume.value = null
    }
    scrollToBottom()
  } catch (err) {
    console.error('Failed to load session messages:', err)
  } finally {
    isMessagesLoading.value = false
  }
}

// Rename session
const startRenaming = (session: ChatSession) => {
  editingSessionId.value = session.session_id
  editTitleInput.value = session.title
  nextTick(() => {
    if (editTitleRef.value) editTitleRef.value.focus()
  })
}

const saveRenamedTitle = async (sessionId: string) => {
  if (!editingSessionId.value) return
  const newTitle = editTitleInput.value.trim()
  editingSessionId.value = null
  if (!newTitle) return

  try {
    await api.patch(`/api/interview-bit/sessions/${sessionId}`, { title: newTitle })
    const sess = sessions.value.find(s => s.session_id === sessionId)
    if (sess) sess.title = newTitle
  } catch (err) {
    console.error('Failed to rename session:', err)
  }
}

// Delete session
const confirmDeleteSession = async (sessionId: string) => {
  try {
    // Delete session from DB via API
    await api.delete(`/api/interview-bit/sessions/${sessionId}`)
    // Remove immediately from reactive session list
    sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
    
    // Switch to another session or create a clean chat if active session was deleted
    if (activeSessionId.value === sessionId) {
      if (sessions.value.length) {
        await selectSession(sessions.value[0].session_id)
      } else {
        await createNewChat()
      }
    }
  } catch (err) {
    console.error('Failed to delete chat session:', err)
  }
}

// Resume PDF Upload
const onPdfSelected = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (!target.files || !target.files[0]) return
  const file = target.files[0]
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    alert('Invalid file type! Only PDF resumes (.pdf) are allowed.')
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    alert('File size exceeds maximum 10 MB limit.')
    return
  }

  showResumeMenu.value = false
  statusMessage.value = 'Uploading and extracting PDF resume text...'
  isLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/api/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const uploadedResume = res.data
    userResumes.value.unshift(uploadedResume)
    activeResume.value = uploadedResume

    if (activeSessionId.value) {
      await api.post(`/api/interview-bit/sessions/${activeSessionId.value}/attach-resume/${uploadedResume.id}`)
    }
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Unable to read this PDF. Please upload a valid readable resume PDF.')
  } finally {
    isLoading.value = false
    statusMessage.value = ''
  }
}

const selectExistingResume = async (resumeObj: any) => {
  activeResume.value = resumeObj
  showResumeMenu.value = false
  if (activeSessionId.value) {
    try {
      await api.post(`/api/interview-bit/sessions/${activeSessionId.value}/attach-resume/${resumeObj.id}`)
    } catch (e) {
      console.warn('Failed to attach resume to session:', e)
    }
  }
}

const detachResume = () => {
  activeResume.value = null
}

const askQuick = (q: string) => {
  inputQuery.value = q
  sendMessage()
}

// Send Message Flow
const sendMessage = async () => {
  const query = inputQuery.value.trim()
  if (!query || isLoading.value) return

  if (!activeSessionId.value) {
    await createNewChat()
  }

  if (speech.isListening.value) speech.stop()
  messages.value.push({ role: 'user', content: query })
  inputQuery.value = ''
  isLoading.value = true
  statusMessage.value = 'AI is thinking...'
  scrollToBottom()

  try {
    const payload: any = {
      question: query,
      session_id: activeSessionId.value,
      style: 'normal'
    }
    const res = await api.post('/api/interview-bit/ask', payload)
    messages.value.push({ role: 'assistant', content: res.data.answer })

    // Refresh sessions list to update auto-generated chat title if needed
    const updatedSessions = await api.get('/api/interview-bit/sessions')
    sessions.value = updatedSessions.data
  } catch (err) {
    console.error('Chat error:', err)
    messages.value.push({
      role: 'assistant',
      content: 'Unable to generate a response. Please try again.'
    })
  } finally {
    isLoading.value = false
    statusMessage.value = ''
    scrollToBottom()
  }
}

onMounted(async () => {
  await fetchUserResumes()
  await fetchSessions()
})
</script>
