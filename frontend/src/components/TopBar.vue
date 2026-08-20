<template>
  <header class="h-16 border-b border-slate-800/60 bg-slate-900/70 backdrop-blur-xl px-3 sm:px-6 flex items-center justify-between sticky top-0 z-30 relative">
    <!-- Subtle bottom glow line -->
    <div class="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500/40 to-transparent"></div>
    
    <div class="flex items-center gap-2.5">
      <!-- Mobile Sidebar Hamburger Toggle Button -->
      <button
        @click="$emit('toggle-sidebar')"
        class="lg:hidden p-2 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300 hover:text-white hover:border-indigo-500/50 transition-all duration-300"
        title="Open Mobile Navigation Menu"
      >
        <Menu class="w-5 h-5" />
      </button>

      <h2 class="text-base sm:text-lg font-black text-slate-100 tracking-tight truncate max-w-[150px] sm:max-w-none">{{ currentTitle }}</h2>
    </div>

    <!-- Live World Clock -->
    <div class="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800/60 text-[11px] font-mono shadow-inner backdrop-blur-md">
      <select
        v-model="selectedCountry"
        class="bg-transparent text-slate-300 font-bold outline-none cursor-pointer text-[10px]"
      >
        <option value="IN" class="bg-slate-900 text-slate-100">India</option>
        <option value="US" class="bg-slate-900 text-slate-100">United States</option>
        <option value="GB" class="bg-slate-900 text-slate-100">United Kingdom</option>
        <option value="AE" class="bg-slate-900 text-slate-100">UAE</option>
        <option value="SG" class="bg-slate-900 text-slate-100">Singapore</option>
        <option value="AU" class="bg-slate-900 text-slate-100">Australia</option>
      </select>
      <span class="text-slate-700">|</span>
      <span class="text-indigo-400 font-bold text-[10px]">{{ formattedDate }}</span>
      <span class="text-emerald-400 font-bold text-[11px]">{{ formattedTimeWithSeconds }}</span>
    </div>

    <!-- Action & Auth Links -->
    <div class="flex items-center gap-3">
      <NotificationBell />

      <router-link to="/mock-interview" class="btn-primary py-1.5 px-4 text-xs flex items-center gap-2 font-bold shadow-lg shadow-indigo-600/30 hover:shadow-xl hover:shadow-indigo-600/40 transition-all duration-300 hover:scale-105">
        <Video class="w-3.5 h-3.5" />
        <span>Start Mock Session</span>
      </router-link>

      <div class="flex items-center gap-2 pl-2 border-l border-slate-800/60">
        <template v-if="authStore.user">
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800/60 text-xs backdrop-blur-md">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400/50"></span>
            <span class="text-slate-200 font-medium max-w-[120px] truncate">{{ authStore.user.full_name || authStore.user.email }}</span>
          </div>
          <button @click="authStore.logout" class="text-xs font-semibold text-rose-400 hover:text-rose-300 px-2.5 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/20 hover:bg-rose-500/20 transition-all duration-300">
            Logout
          </button>
        </template>
        <template v-else>
          <router-link to="/login" class="text-xs font-bold text-slate-200 hover:text-white px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 hover:border-indigo-500 transition-all duration-300">
            Login
          </router-link>
          <router-link to="/register" class="text-xs font-bold text-white px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 transition-all duration-300 shadow-md shadow-indigo-600/30">
            Register
          </router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { Video, Menu } from 'lucide-vue-next'
import NotificationBell from './NotificationBell.vue'

const emit = defineEmits<{
  (e: 'toggle-sidebar'): void
}>()

const route = useRoute()
const authStore = useAuthStore()

const selectedCountry = ref<string>('IN')
const currentTime = ref<Date>(new Date())
const activeLiveSession = ref<any>(null)
let timer: any = null

const checkActiveSession = () => {
  try {
    const raw = localStorage.getItem('active_live_interview')
    if (raw) {
      activeLiveSession.value = JSON.parse(raw)
    } else {
      activeLiveSession.value = null
    }
  } catch (e) {
    activeLiveSession.value = null
  }
}

const countryTimezones: Record<string, string> = {
  IN: 'Asia/Kolkata',
  US: 'America/New_York',
  GB: 'Europe/London',
  AE: 'Asia/Dubai',
  SG: 'Asia/Singapore',
  AU: 'Australia/Sydney'
}

const formattedDate = computed(() => {
  const tz = countryTimezones[selectedCountry.value] || 'Asia/Kolkata'
  return new Intl.DateTimeFormat('en-IN', {
    timeZone: tz,
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  }).format(currentTime.value)
})

const formattedTimeWithSeconds = computed(() => {
  const tz = countryTimezones[selectedCountry.value] || 'Asia/Kolkata'
  return new Intl.DateTimeFormat('en-IN', {
    timeZone: tz,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  }).format(currentTime.value)
})

onMounted(() => {
  checkActiveSession()
  timer = setInterval(() => {
    currentTime.value = new Date()
    checkActiveSession()
  }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const currentTitle = computed(() => {
  const titles: Record<string, string> = {
    '/dashboard': 'Interview Preparation Dashboard',
    '/mock-interview': 'Simulated AI Mock Interview',
    '/practice': 'Practice Questions Bank',
    '/coding': 'Coding Interview Arena',
    '/resume': 'Resume Intelligence & Skill Gap Analyzer',
    '/job-analysis': 'Job Description Intelligence',
    '/history': 'Session Analytics & Report History',
    '/settings': 'Platform & AI Settings',
    '/login': 'Candidate Sign In',
    '/register': 'Create Candidate Account'
  }
  return titles[route.path] || 'Interview Coach AI'
})
</script>
