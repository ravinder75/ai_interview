<template>
  <div class="max-w-7xl mx-auto space-y-8 py-4 font-sans">
    <!-- Header -->
    <div class="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-950">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-100 flex items-center gap-3">
          <span>🎯 INTERVIEW SCHEDULE</span>
        </h1>
        <p class="text-xs text-slate-400 mt-1">Manage, schedule, and join your authenticated AI-powered mock interviews</p>
      </div>
      <button
        @click="openScheduleModal"
        class="btn-primary px-5 py-2.5 text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30"
      >
        <Plus class="w-4 h-4" />
        <span>+ Schedule New Interview</span>
      </button>
    </div>

    <!-- Live Notification Alert Banner for Scheduled Interviews Ready Now -->
    <div
      v-if="readyInterviewNotification"
      class="p-5 rounded-2xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl shadow-emerald-500/10 animate-pulse"
    >
      <div class="flex items-center gap-4">
        <span class="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-2xl shrink-0 border border-emerald-500/30">
          🚀
        </span>
        <div class="space-y-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h4 class="font-extrabold text-sm text-slate-100 font-mono tracking-wide">INTERVIEW READY TO START NOW!</h4>
            <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-bold border border-emerald-500/30">
              JOIN WINDOW ACTIVE
            </span>
          </div>
          <p class="text-xs text-slate-300">
            Scheduled: <strong class="text-slate-100">{{ readyInterviewNotification.role }}</strong> ({{ formatType(readyInterviewNotification.interview_type) }})
          </p>
          <p class="text-xs text-amber-300 font-mono font-bold flex items-center gap-1.5">
            <Clock class="w-3.5 h-3.5 text-amber-400" />
            <span>{{ getCountdownText(readyInterviewNotification) }}</span>
          </p>
        </div>
      </div>

      <button
        @click="handleStartInterview(readyInterviewNotification)"
        :disabled="startingId === readyInterviewNotification.session_id"
        class="btn-primary py-3 px-6 text-xs font-extrabold flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 border-emerald-400 shadow-lg shadow-emerald-600/30 shrink-0"
      >
        <Loader2 v-if="startingId === readyInterviewNotification.session_id" class="w-4 h-4 animate-spin" />
        <Play v-else class="w-4 h-4 fill-emerald-100" />
        <span>[ START INTERVIEW NOW ]</span>
      </button>
    </div>

    <!-- Active Notifications Alert Bar -->
    <div v-if="activeSystemNotification" class="p-4 rounded-xl bg-indigo-950/60 border border-indigo-500/40 text-indigo-200 text-xs flex items-center justify-between gap-3 shadow-md font-mono">
      <div class="flex items-center gap-2.5">
        <Bell class="w-4 h-4 text-indigo-400 animate-bounce" />
        <span><strong>{{ activeSystemNotification.title }}:</strong> {{ activeSystemNotification.message }}</span>
      </div>
      <button @click="activeSystemNotification = null" class="text-indigo-400 hover:text-indigo-200">✕</button>
    </div>

    <!-- Upcoming Interviews Section -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-bold text-slate-200 flex items-center gap-2">
          <Calendar class="w-5 h-5 text-indigo-400" />
          <span>Upcoming Interviews</span>
        </h2>
        <span class="text-xs font-mono text-slate-400">Active Schedules: {{ upcomingInterviews.length }}</span>
      </div>

      <div v-if="upcomingInterviews.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="interview in upcomingInterviews"
          :key="interview.id || interview.session_id"
          class="glass-card rounded-2xl p-6 border border-slate-800 hover:border-indigo-500/50 transition flex flex-col justify-between space-y-6 bg-slate-950/80"
        >
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20">
                {{ formatType(interview.interview_type) }}
              </span>
              <span :class="[
                'text-[10px] font-extrabold px-2.5 py-0.5 rounded uppercase font-mono border',
                getCardStatusBadgeClass(interview)
              ]">
                {{ getCardStatusLabel(interview) }}
              </span>
            </div>

            <h3 class="text-base font-bold text-slate-100">{{ interview.role }}</h3>

            <div class="space-y-2 text-xs text-slate-300">
              <div class="flex items-center gap-2">
                <Calendar class="w-3.5 h-3.5 text-slate-400" />
                <span>{{ formatDate(interview.scheduled_at) }}</span>
              </div>
              <div class="flex items-center gap-2">
                <Clock class="w-3.5 h-3.5 text-slate-400" />
                <span>Start Time: <strong class="text-slate-100 font-mono">{{ formatTime(interview.scheduled_at) }}</strong></span>
              </div>
              <div class="flex items-center gap-2">
                <Timer class="w-3.5 h-3.5 text-slate-400" />
                <span>Duration: {{ interview.duration_minutes || 30 }} minutes</span>
              </div>
            </div>

            <!-- Dynamic Countdown Display Box -->
            <div :class="[
              'p-3 rounded-xl border text-center font-mono text-xs space-y-1',
              isReady(interview) ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300' : 'bg-slate-900 border-slate-800 text-indigo-300'
            ]">
              <span class="text-[10px] uppercase text-slate-400 block tracking-wider font-semibold">SCHEDULE COUNTDOWN STATUS</span>
              <strong class="text-sm font-extrabold block">
                ⏱️ {{ getCountdownText(interview) }}
              </strong>
            </div>
          </div>

          <!-- Actions Bar: Edit, Delete & Join -->
          <div class="space-y-2 pt-2 border-t border-slate-800/80">
            <div class="flex items-center justify-between gap-2">
              <button
                @click="openEditModal(interview)"
                class="flex-1 py-1.5 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition"
              >
                <Edit3 class="w-3.5 h-3.5 text-indigo-400" />
                <span>Edit</span>
              </button>

              <button
                @click="handleDelete(interview)"
                class="py-1.5 px-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 text-rose-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition"
              >
                <Trash2 class="w-3.5 h-3.5 text-rose-400" />
                <span>Delete</span>
              </button>
            </div>

            <!-- START / JOIN BUTTON STATE -->
            <button
              v-if="isReady(interview)"
              @click="handleStartInterview(interview)"
              :disabled="startingId === interview.session_id"
              class="w-full btn-primary py-2.5 text-xs font-extrabold flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 border-emerald-400 shadow-lg shadow-emerald-600/30"
            >
              <Loader2 v-if="startingId === interview.session_id" class="w-4 h-4 animate-spin" />
              <Play v-else class="w-4 h-4 fill-emerald-100" />
              <span>[ START INTERVIEW NOW ]</span>
            </button>

            <button
              v-else
              @click="alertNotTime(interview)"
              disabled
              class="w-full py-2.5 text-xs font-bold flex items-center justify-center gap-2 bg-slate-900 text-slate-500 border border-slate-800 rounded-xl cursor-not-allowed"
            >
              <Clock class="w-4 h-4 text-slate-500" />
              <span>[ JOIN INTERVIEW — AVAILABLE AT {{ formatTime(interview.scheduled_at) }} ]</span>
            </button>
          </div>
        </div>
      </div>

      <div v-else class="glass-card rounded-2xl p-8 border border-slate-800 text-center space-y-3 bg-slate-950">
        <p class="text-slate-400 text-sm">No upcoming interviews scheduled for your account.</p>
        <button @click="openScheduleModal" class="text-xs text-indigo-400 font-bold hover:underline">
          + Schedule your first mock interview now
        </button>
      </div>
    </div>

    <!-- Completed & Missed Session History Section -->
    <div class="space-y-4 pt-4 border-t border-slate-800">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-bold text-slate-200 flex items-center gap-2">
          <CheckCircle2 class="w-5 h-5 text-emerald-400" />
          <span>Completed & Missed Session History</span>
        </h2>
        <span class="text-xs text-slate-400 font-mono">History Count: {{ historyInterviews.length }}</span>
      </div>

      <div v-if="historyInterviews.length > 0" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="session in historyInterviews"
            :key="session.id || session.session_id"
            :class="[
              'glass-card rounded-xl p-4 border transition flex flex-col justify-between space-y-3 bg-slate-950/70',
              session.status === 'MISSED' ? 'border-rose-500/30 hover:border-rose-500/50' : 'border-slate-800/90 hover:border-slate-700'
            ]"
          >
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded-full border border-indigo-500/20">
                  {{ formatType(session.interview_type) }}
                </span>
                
                <span v-if="session.status === 'MISSED'" class="text-[10px] font-mono font-extrabold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20 flex items-center gap-1">
                  ⚠️ MISSED
                </span>
                <span v-else class="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 flex items-center gap-1">
                  ✓ Score: {{ session.score || 82 }}/100
                </span>
              </div>

              <div>
                <h4 class="text-sm font-bold text-slate-100">{{ session.role }}</h4>
                <div class="flex items-center gap-3 text-[11px] text-slate-400 mt-1 font-mono">
                  <span class="flex items-center gap-1">
                    <Clock class="w-3 h-3 text-slate-500" />
                    {{ formatDate(session.scheduled_at || session.created_at) }}
                  </span>
                  <span>•</span>
                  <span class="flex items-center gap-1">
                    <Timer class="w-3 h-3 text-slate-500" />
                    {{ session.duration_minutes || 30 }} mins
                  </span>
                </div>
              </div>

              <div v-if="session.status === 'MISSED'" class="p-2 rounded-lg bg-rose-950/30 border border-rose-500/20 text-[10px] text-rose-300 font-mono">
                ⚠️ Interview missed — the 10-minute join window has expired.
              </div>
            </div>

            <!-- View Full Evaluation Report Link -->
            <div class="pt-2 border-t border-slate-900 flex items-center justify-between text-xs">
              <span class="text-[10px] font-mono text-slate-500">ID: {{ (session.session_id || session.id).slice(0, 14) }}</span>
              <router-link
                v-if="session.status !== 'MISSED'"
                :to="`/interview-result/${session.session_id || session.id}`"
                class="font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 text-[11px]"
              >
                <span>View Report</span>
                <ArrowRight class="w-3.5 h-3.5" />
              </router-link>
              <span v-else class="text-[10px] font-mono text-slate-500 italic">Not Assessed</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="glass-card rounded-2xl p-6 border border-slate-800 text-center text-slate-400 text-xs bg-slate-950">
        No completed or missed session history recorded yet.
      </div>
    </div>

    <!-- Schedule / Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div class="glass-card rounded-2xl p-6 border border-slate-800 w-full max-w-md space-y-5 shadow-2xl bg-slate-950">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 class="text-base font-bold text-slate-100">{{ editingSession ? 'Edit Scheduled Interview' : 'Schedule Mock Interview' }}</h3>
          <button @click="closeModal" class="text-slate-400 hover:text-slate-100">✕</button>
        </div>

        <form @submit.prevent="handleScheduleSubmit" class="space-y-4 text-xs">
          <RoleSelect v-model="form.role" />

          <div class="space-y-1">
            <label class="font-semibold text-slate-300">Interview Type</label>
            <select v-model="form.type" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-slate-100 outline-none focus:border-indigo-500 font-mono">
              <option value="technical">Technical Round</option>
              <option value="coding">Coding & Data Structures</option>
              <option value="system_design">System Design & Architecture</option>
              <option value="behavioral">Behavioral & HR Round</option>
              <option value="ai_ml">AI / Machine Learning Round</option>
              <option value="aptitude">Aptitude & Logical Reasoning</option>
              <option value="technical_behavioral">Technical + Behavioral Combined</option>
              <option value="full_mock">Full End-to-End Mock Interview</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-semibold text-slate-300">Difficulty</label>
              <select v-model="form.difficulty" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-slate-100 outline-none focus:border-indigo-500">
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
                <option value="expert">Expert</option>
              </select>
            </div>

            <div class="space-y-1">
              <label class="font-semibold text-slate-300">Duration</label>
              <select v-model="form.duration_minutes" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-slate-100 outline-none focus:border-indigo-500">
                <option :value="15">15 minutes</option>
                <option :value="30">30 minutes</option>
                <option :value="45">45 minutes</option>
                <option :value="60">60 minutes</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-semibold text-slate-300">Date</label>
              <input v-model="form.date" type="date" :min="minDate" required class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 outline-none focus:border-indigo-500" />
            </div>

            <div class="space-y-1">
              <label class="font-semibold text-slate-300">Time</label>
              <input v-model="form.time" type="time" :min="minTime" required class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 outline-none focus:border-indigo-500" />
            </div>
          </div>

          <div class="space-y-1">
            <label class="font-semibold text-slate-300">Upload Resume <span class="text-rose-400 font-bold">* (Optional / Mandatory for custom profile)</span></label>
            <div class="flex items-center gap-2">
              <input type="file" ref="resumeInput" accept=".pdf,.docx,.doc" class="hidden" @change="handleResumeUpload" />
              <button type="button" @click="triggerResumeUpload" class="w-full bg-slate-900 border border-dashed border-indigo-500/40 hover:border-indigo-500 rounded-xl px-4 py-2.5 text-indigo-300 hover:text-indigo-200 text-xs font-semibold flex items-center justify-center gap-2 transition">
                <FileText class="w-4 h-4 text-indigo-400" />
                <span>{{ resumeFileName || '📄 Upload Resume (PDF / Word .docx .doc)' }}</span>
              </button>
            </div>
            <p v-if="resumeFileName" class="text-[10px] text-emerald-400 font-medium">✓ Resume attached: {{ resumeFileName }}</p>
          </div>

          <div class="flex items-center justify-end gap-3 pt-2">
            <button type="button" @click="closeModal" class="btn-secondary px-4 py-2 text-xs font-bold">
              Cancel
            </button>
            <button type="submit" :disabled="loading" class="btn-primary px-5 py-2 text-xs font-bold flex items-center gap-2">
              <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
              <span>{{ editingSession ? 'Save Changes' : 'Schedule Interview' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Calendar, Clock, Timer, Plus, Play, Loader2, FileText, Edit3, Trash2, CheckCircle2, ArrowRight, Bell } from 'lucide-vue-next'
import RoleSelect from '../components/auth/RoleSelect.vue'
import { api, getScheduledInterviews, scheduleInterview, startScheduledInterview, getInterviewNotifications } from '../services/api'

const router = useRouter()

const showModal = ref(false)
const loading = ref(false)
const startingId = ref<string | null>(null)
const resumeFileName = ref('')
const resumeInput = ref<HTMLInputElement | null>(null)
const editingSession = ref<any>(null)
const activeSystemNotification = ref<any>(null)

const now = ref<number>(Date.now())
let timerId: any = null
let notificationPollId: any = null

const form = ref({
  role: 'Software Engineer',
  type: 'technical',
  difficulty: 'medium',
  duration_minutes: 30,
  date: new Date().toISOString().split('T')[0],
  time: '10:30'
})

const sessions = ref<any[]>([])
const seenNotificationKeys = new Set<string>()

const openScheduleModal = () => {
  editingSession.value = null
  const defaultDate = new Date()
  defaultDate.setMinutes(defaultDate.getMinutes() + 30)
  form.value = {
    role: 'Software Engineer',
    type: 'technical',
    difficulty: 'medium',
    duration_minutes: 30,
    date: defaultDate.toISOString().split('T')[0],
    time: defaultDate.toTimeString().slice(0, 5)
  }
  resumeFileName.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingSession.value = null
  resumeFileName.value = ''
}

const openEditModal = (interview: any) => {
  editingSession.value = interview
  const d = interview.scheduled_at ? new Date(interview.scheduled_at) : new Date()
  form.value = {
    role: interview.role || 'Software Engineer',
    type: interview.interview_type || 'technical',
    difficulty: interview.difficulty || 'medium',
    duration_minutes: interview.duration_minutes || 30,
    date: d.toISOString().split('T')[0],
    time: d.toTimeString().slice(0, 5)
  }
  resumeFileName.value = interview.resume_filename || 'Attached Resume'
  showModal.value = true
}

const handleDelete = async (interview: any) => {
  const sessId = interview.session_id || interview.id
  if (!confirm(`Are you sure you want to cancel and delete the scheduled ${interview.role} interview?`)) {
    return
  }

  try {
    await api.delete(`/api/interviews/session/${sessId}`)
    await fetchInterviews()
  } catch (err) {
    alert('Failed to delete scheduled interview.')
  }
}

const triggerResumeUpload = () => {
  if (resumeInput.value) {
    resumeInput.value.click()
  }
}

const handleResumeUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file) {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!['pdf', 'docx', 'doc'].includes(ext || '')) {
      alert('Invalid file format. Please upload your resume in Word (.docx / .doc) or PDF (.pdf) format only.')
      resumeFileName.value = ''
      if (resumeInput.value) resumeInput.value.value = ''
      return
    }
    resumeFileName.value = file.name
  }
}

const fetchInterviews = async () => {
  try {
    const data = await getScheduledInterviews()
    sessions.value = data || []
  } catch (err) {
    console.error('Failed to fetch scheduled interviews:', err)
  }
}

const fetchNotifications = async () => {
  try {
    const notifs = await getInterviewNotifications()
    if (notifs && notifs.length > 0) {
      const latest = notifs[0]
      const key = `${latest.session_id}_${latest.notification_type}`
      if (!seenNotificationKeys.has(key)) {
        seenNotificationKeys.add(key)
        activeSystemNotification.value = latest

        // Trigger HTML5 Browser Notification if permitted
        if ('Notification' in window && Notification.permission === 'granted') {
          try {
            new Notification(latest.title, {
              body: latest.message,
              icon: '/favicon.ico'
            })
          } catch (e) {
            console.warn('Browser notification trigger warning:', e)
          }
        }
      }
    }
  } catch (err) {
    console.warn('Notification fetch warning:', err)
  }
}

onMounted(() => {
  // Request Browser Notification Permission if supported
  if ('Notification' in window && Notification.permission !== 'granted' && Notification.permission !== 'denied') {
    Notification.requestPermission()
  }

  // Reactive timer updating 'now' every second for exact countdowns
  timerId = setInterval(() => {
    now.value = Date.now()
  }, 1000)

  // Poll for interviews and notifications every 10 seconds
  fetchInterviews()
  fetchNotifications()
  notificationPollId = setInterval(() => {
    fetchInterviews()
    fetchNotifications()
  }, 10000)
})

onUnmounted(() => {
  if (timerId) clearInterval(timerId)
  if (notificationPollId) clearInterval(notificationPollId)
})

const getSchedTime = (interview: any): number => {
  if (!interview.scheduled_at) return now.value
  return new Date(interview.scheduled_at).getTime()
}

const getGraceExpiryTime = (interview: any): number => {
  return getSchedTime(interview) + 10 * 60 * 1000
}

const isReady = (interview: any): boolean => {
  if (interview.status === 'MISSED' || interview.status === 'COMPLETED') return false
  const schedTime = getSchedTime(interview)
  const graceExpiry = getGraceExpiryTime(interview)
  return now.value >= schedTime && now.value <= graceExpiry
}

const isMissed = (interview: any): boolean => {
  if (interview.status === 'MISSED') return true
  if (interview.status === 'COMPLETED' || interview.status === 'IN_PROGRESS') return false
  return now.value > getGraceExpiryTime(interview)
}

const getCountdownText = (interview: any): string => {
  if (isMissed(interview)) {
    return 'Expired — Join window closed'
  }
  const schedTime = getSchedTime(interview)
  const graceExpiry = getGraceExpiryTime(interview)

  if (now.value < schedTime) {
    const diffSec = Math.floor((schedTime - now.value) / 1000)
    const mins = Math.floor(diffSec / 60)
    const secs = diffSec % 60
    if (mins >= 60) {
      const hours = Math.floor(mins / 60)
      const remMins = mins % 60
      return `Starts in ${hours}h ${remMins}m`
    }
    return `Starts in ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  } else if (now.value <= graceExpiry) {
    const diffSec = Math.floor((graceExpiry - now.value) / 1000)
    const mins = Math.floor(diffSec / 60)
    const secs = diffSec % 60
    return `Join window closes in ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  } else {
    return 'Interview Missed'
  }
}

const upcomingInterviews = computed(() => {
  return sessions.value.filter(s => {
    if (s.status === 'COMPLETED' || s.status === 'finished' || s.status === 'IN_PROGRESS') return false
    return !isMissed(s)
  })
})

const historyInterviews = computed(() => {
  return sessions.value.filter(s => {
    return s.status === 'COMPLETED' || s.status === 'finished' || isMissed(s) || s.overall_score !== undefined
  })
})

const readyInterviewNotification = computed(() => {
  return upcomingInterviews.value.find(s => isReady(s))
})

const getCardStatusLabel = (interview: any) => {
  if (isReady(interview)) return 'READY TO START'
  if (isMissed(interview)) return 'MISSED'
  return 'SCHEDULED'
}

const getCardStatusBadgeClass = (interview: any) => {
  if (isReady(interview)) return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 animate-pulse'
  if (isMissed(interview)) return 'bg-rose-500/10 text-rose-400 border-rose-500/30'
  return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
}

const handleStartInterview = async (interview: any) => {
  const sessId = interview.session_id || interview.id
  startingId.value = sessId

  try {
    const res = await startScheduledInterview(sessId)
    if (res && res.session_id) {
      router.push(`/mock-interview?session_id=${res.session_id}&role=${encodeURIComponent(res.role || interview.role)}&start=true`)
    } else {
      router.push(`/mock-interview?session_id=${sessId}&role=${encodeURIComponent(interview.role)}&start=true`)
    }
  } catch (err: any) {
    const detail = err.response?.data?.detail || err.message || 'Failed to start interview.'
    alert(`Unable to start interview: ${detail}`)
    await fetchInterviews()
  } finally {
    startingId.value = null
  }
}

const minDate = computed(() => {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})

const minTime = computed(() => {
  if (form.value.date === minDate.value) {
    const d = new Date()
    const hours = String(d.getHours()).padStart(2, '0')
    const mins = String(d.getMinutes()).padStart(2, '0')
    return `${hours}:${mins}`
  }
  return '00:00'
})

const handleScheduleSubmit = async () => {
  if (form.value.date < minDate.value) {
    alert('Please select today or a future date.')
    return
  }

  const scheduledDateObj = new Date(`${form.value.date}T${form.value.time}:00`)
  if (isNaN(scheduledDateObj.getTime()) || scheduledDateObj.getTime() <= Date.now()) {
    alert('Please select a future interview time.')
    return
  }

  loading.value = true
  try {
    let scheduled_at = scheduledDateObj.toISOString()
    const tzStr = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'

    if (editingSession.value) {
      const sessId = editingSession.value.session_id || editingSession.value.id
      await api.put(`/api/interviews/session/${sessId}`, {
        role: form.value.role,
        interview_type: form.value.type,
        difficulty: form.value.difficulty,
        duration_minutes: Number(form.value.duration_minutes) || 30,
        scheduled_at: scheduled_at
      })
    } else {
      await scheduleInterview({
        role: form.value.role,
        interview_type: form.value.type,
        difficulty: form.value.difficulty,
        duration_minutes: Number(form.value.duration_minutes) || 30,
        scheduled_date: form.value.date,
        scheduled_time: form.value.time,
        scheduled_at: scheduled_at,
        timezone: tzStr
      })
    }

    closeModal()
    await fetchInterviews()
  } catch (err: any) {
    console.error('Schedule interview error:', err)
    alert(`Failed to save interview schedule: ${err.response?.data?.detail || err.message}`)
  } finally {
    loading.value = false
  }
}

const formatDate = (isoStr: string) => {
  if (!isoStr) return 'Aug 20, 2026'
  return new Date(isoStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatTime = (isoStr: string) => {
  if (!isoStr) return '10:30 AM'
  return new Date(isoStr).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

const formatType = (t: string) => {
  if (!t) return 'Technical + Behavioral'
  return t.replace('_', ' ').toUpperCase()
}

const alertNotTime = (interview: any) => {
  const timeStr = formatTime(interview.scheduled_at)
  const dateStr = formatDate(interview.scheduled_at)
  alert(`This interview is scheduled for ${dateStr} at ${timeStr}. It will open at the exact scheduled start time!`)
}
</script>
