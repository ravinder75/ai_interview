<template>
  <div>
    <!-- Mobile Backdrop Overlay -->
    <div
      v-if="isOpen"
      @click="$emit('close')"
      class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 lg:hidden transition-opacity"
    ></div>

    <aside :class="[
      'w-64 bg-slate-900/95 lg:bg-slate-900/80 backdrop-blur-xl border-r border-slate-800/60 flex flex-col justify-between p-4 sticky top-0 h-screen z-50 relative overflow-hidden transition-transform duration-300',
      'max-lg:fixed max-lg:top-0 max-lg:bottom-0 max-lg:left-0',
      isOpen ? 'max-lg:translate-x-0' : 'max-lg:-translate-x-full'
    ]">
      
      <!-- Background ambient glow -->
      <div class="absolute -top-32 -left-32 w-64 h-64 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-32 -right-32 w-64 h-64 bg-purple-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div class="space-y-6 overflow-y-auto pr-1 relative z-10">
        <!-- App Brand with Animated Gradient -->
        <div class="flex items-center justify-between px-2 py-3">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center text-white shadow-xl shadow-indigo-500/40 font-bold animate-pulse">
              <Bot class="w-6 h-6 drop-shadow-lg" />
            </div>
            <div>
              <span class="font-black text-lg tracking-tight text-slate-100 block leading-tight">Interview Coach</span>
              <span class="text-[10px] text-indigo-400 font-bold uppercase tracking-widest">AI Practice Platform</span>
            </div>
          </div>
          <!-- Mobile Close Button -->
          <button @click="$emit('close')" class="lg:hidden text-slate-400 hover:text-white p-1 rounded-lg bg-slate-800/80">
            <X class="w-5 h-5" />
          </button>
        </div>

      <!-- Navigation Links with Animated Active Indicator -->
      <nav class="space-y-1">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 relative group',
            $route.path === item.path
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-600/30 font-bold scale-[1.02]'
              : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60 hover:translate-x-1'
          ]"
        >
          <!-- Animated left border indicator -->
          <div v-if="$route.path === item.path" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-indigo-400 rounded-full shadow-lg shadow-indigo-400/50"></div>
          <component :is="item.icon" :class="['w-4 h-4 transition-transform duration-300', $route.path === item.path ? 'scale-110' : 'group-hover:scale-110']" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
    </div>

    <!-- User Profile Footer & Popover Card -->
    <div class="pt-3 border-t border-slate-800/60 space-y-2 relative z-10">
      <div class="flex items-center justify-between px-2 text-[11px] text-slate-400">
        <span class="flex items-center gap-1.5 text-emerald-400 font-medium">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-lg shadow-emerald-400/50"></span>
          AI Engine Active
        </span>
      </div>

      <!-- Logged-In User Profile Clickable Pill -->
      <div
        v-if="authStore.user"
        @click="showProfileCard = !showProfileCard"
        class="bg-slate-950/80 hover:bg-slate-900 rounded-xl p-2.5 border border-slate-800 hover:border-indigo-500/50 flex items-center justify-between cursor-pointer transition-all duration-300 select-none group hover:shadow-lg hover:shadow-indigo-500/10"
      >
        <div class="flex items-center gap-2.5 overflow-hidden">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center text-white font-extrabold text-xs shadow-md shrink-0 overflow-hidden group-hover:scale-105 transition-transform">
            <img v-if="authStore.user.profile_picture" :src="authStore.user.profile_picture" class="w-full h-full object-cover" />
            <span v-else>{{ userInitial }}</span>
          </div>
          <div class="overflow-hidden">
            <span class="text-xs text-slate-100 font-bold block truncate group-hover:text-indigo-300 transition">
              {{ authStore.user.full_name || 'Candidate User' }}
            </span>
            <span class="text-[10px] text-slate-400 block truncate font-mono">
              {{ authStore.user.email }}
            </span>
          </div>
        </div>
        <ChevronUp :class="['w-4 h-4 text-slate-400 transition-transform duration-300', showProfileCard ? 'rotate-180 text-indigo-400' : '']" />
      </div>

      <!-- Guest User Pill -->
      <div v-else class="bg-slate-950/80 rounded-xl p-3 border border-slate-800 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <UserIcon class="w-4 h-4 text-slate-400 shrink-0" />
          <span class="text-xs text-slate-300 font-medium">Guest User</span>
        </div>
        <div class="flex items-center gap-1.5 text-xs">
          <router-link to="/login" class="text-indigo-400 font-bold hover:underline">Login</router-link>
        </div>
      </div>

      <!-- User Profile Details Popover Modal -->
      <div
        v-if="showProfileCard && authStore.user"
        class="absolute bottom-16 left-0 right-0 glass-card rounded-2xl p-4 border border-indigo-500/30 shadow-2xl space-y-3.5 z-50 bg-slate-900/95 backdrop-blur-xl"
        style="animation: slideUp 0.3s ease-out"
      >
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2.5">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center text-white font-extrabold text-sm shadow-md overflow-hidden">
              <img v-if="authStore.user.profile_picture" :src="authStore.user.profile_picture" class="w-full h-full object-cover" />
              <span v-else>{{ userInitial }}</span>
            </div>
            <div>
              <h4 class="text-xs font-bold text-slate-100">{{ authStore.user.full_name || 'Candidate User' }}</h4>
              <p class="text-[10px] text-indigo-400 font-mono font-semibold">{{ authStore.user.target_role || 'Software Engineer' }}</p>
            </div>
          </div>
          <button @click="showProfileCard = false" class="text-slate-400 hover:text-slate-100 text-xs transition">✕</button>
        </div>

        <div class="space-y-1.5 text-[11px] text-slate-300">
          <div class="flex justify-between">
            <span class="text-slate-400">Email:</span>
            <span class="font-mono text-slate-200 text-[10px] truncate max-w-[130px]">{{ authStore.user.email }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Experience:</span>
            <span class="font-semibold text-purple-300">{{ authStore.user.experience_level || 'Fresher' }}</span>
          </div>
          <div v-if="authStore.user.auth_provider" class="flex justify-between">
            <span class="text-slate-400">Auth Method:</span>
            <span class="font-bold uppercase text-[10px] text-emerald-400">{{ authStore.user.auth_provider }}</span>
          </div>
        </div>

        <div class="pt-2 border-t border-slate-800 space-y-1.5">
          <router-link
            to="/settings"
            @click="showProfileCard = false"
            class="w-full btn-secondary py-1.5 text-xs font-semibold flex items-center justify-center gap-1.5 text-slate-200 hover:text-white"
          >
            <Settings class="w-3.5 h-3.5" />
            <span>Edit Profile & Settings</span>
          </router-link>

          <button
            @click="handleLogout"
            class="w-full py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 text-rose-400 font-bold text-xs flex items-center justify-center gap-1.5 transition"
          >
            <LogOut class="w-3.5 h-3.5" />
            <span>Logout Account</span>
          </button>
        </div>
      </div>
    </div>
  </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import {
  Bot,
  LayoutDashboard,
  Calendar,
  PlayCircle,
  Video,
  Target,
  Code2,
  FileText,
  Briefcase,
  History,
  MessageSquare,
  CreditCard,
  Sparkles,
  Info,
  Settings,
  User as UserIcon,
  ChevronUp,
  LogOut,
  X
} from 'lucide-vue-next'

const props = defineProps<{
  isOpen?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const $route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const showProfileCard = ref(false)

const userInitial = computed(() => {
  if (authStore.user?.full_name) {
    return authStore.user.full_name.charAt(0).toUpperCase()
  }
  if (authStore.user?.email) {
    return authStore.user.email.charAt(0).toUpperCase()
  }
  return 'U'
})

const handleLogout = async () => {
  showProfileCard.value = false
  await authStore.logout()
  router.push('/login')
}

const allNavItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/interview-bit', label: '🎯 Interview Bit', icon: Target },
  { path: '/interview-schedule', label: '🎯 Interview Schedule', icon: Calendar },
  { path: '/mock-interview', label: 'Mock Interview', icon: Video },
  { path: '/practice', label: 'Practice Questions', icon: PlayCircle },
  { path: '/coding', label: 'Coding Interview', icon: Code2 },
  { path: '/resume', label: 'Resume Analyzer', icon: FileText },
  { path: '/job-analysis', label: 'Job Analyzer', icon: Briefcase },
  { path: '/chatbot', label: 'AI Chatbot', icon: MessageSquare },
  { path: '/history', label: 'Session History', icon: History },
  { path: '/pricing', label: '💎 Pricing', icon: CreditCard },
  { path: '/features', label: '🚀 Features', icon: Sparkles },
  { path: '/about', label: 'ℹ️ About Us', icon: Info },
  { path: '/settings', label: 'Settings', icon: Settings },
]

const navItems = computed(() => {
  const isAdmin = authStore.user?.email?.toLowerCase() === 'ravinderkama14@gmail.com'
  return allNavItems.filter(item => {
    if (item.path === '/interview-bit') return isAdmin
    return true
  })
})
</script>
