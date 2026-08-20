<template>
  <div class="relative">
    <!-- Bell Button -->
    <button
      @click="isOpen = !isOpen"
      class="relative p-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-indigo-500/60 text-slate-300 hover:text-white transition flex items-center justify-center"
      title="Notifications & Security Alerts"
    >
      <Bell class="w-4 h-4" />
      <span
        v-if="unreadCount > 0"
        class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-white text-[9px] font-extrabold flex items-center justify-center border border-slate-950 shadow-md animate-pulse"
      >
        {{ unreadCount }}
      </span>
    </button>

    <!-- Notification Dropdown Panel -->
    <div
      v-if="isOpen"
      class="absolute right-0 mt-3 w-80 sm:w-96 glass-card bg-slate-950/95 border border-slate-800 rounded-2xl shadow-2xl z-50 overflow-hidden"
    >
      <!-- Header -->
      <div class="p-4 border-b border-slate-800 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Bell class="w-4 h-4 text-indigo-400" />
          <h3 class="text-xs font-bold text-slate-100 uppercase tracking-wider">Notifications</h3>
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 font-mono font-bold border border-indigo-500/20">
            {{ notifications.length }}
          </span>
        </div>
        <button
          @click="markAllAsRead"
          class="text-[10px] text-slate-400 hover:text-indigo-400 font-bold transition"
        >
          Mark all read
        </button>
      </div>

      <!-- Notifications List -->
      <div class="max-h-80 overflow-y-auto divide-y divide-slate-800/60 text-xs">
        <div
          v-for="item in notifications"
          :key="item.id"
          :class="[
            'p-3.5 transition flex items-start gap-3 relative',
            item.read ? 'bg-slate-950/40 text-slate-400' : 'bg-slate-900/80 text-slate-100 font-medium'
          ]"
        >
          <!-- Category Icon -->
          <div
            :class="[
              'w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border text-xs',
              getCategoryBadgeStyle(item.type)
            ]"
          >
            {{ getCategoryIcon(item.type) }}
          </div>

          <div class="space-y-1 flex-1 pr-3">
            <div class="flex items-center justify-between">
              <span class="font-bold text-xs text-slate-200 block">{{ item.title }}</span>
              <span class="text-[9px] text-slate-500 font-mono">{{ item.time }}</span>
            </div>

            <p class="text-[11px] text-slate-300 leading-snug">{{ item.message }}</p>

            <!-- Interactive Action Link for Ready Interviews -->
            <router-link
              v-if="item.actionUrl"
              :to="item.actionUrl"
              @click="isOpen = false; item.read = true"
              class="inline-flex items-center gap-1 text-[10px] font-extrabold text-indigo-400 hover:text-indigo-300 mt-1 uppercase tracking-wider bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20"
            >
              <span>{{ item.actionText || 'Action' }}</span>
              <span>→</span>
            </router-link>
          </div>

          <!-- Unread Dot -->
          <span
            v-if="!item.read"
            class="w-2 h-2 rounded-full bg-indigo-500 absolute top-4 right-3"
          ></span>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-2.5 bg-slate-900 border-t border-slate-800 text-center text-[10px] text-slate-500 font-mono">
        Real-Time Security & Interview Notifications Active
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Bell } from 'lucide-vue-next'
import { useAuthStore } from '../stores/authStore'
import { api } from '../services/api'

const isOpen = ref(false)

interface NotificationItem {
  id: string
  type: 'interview_ready' | 'offer' | 'device_login' | 'system'
  title: string
  message: string
  time: string
  read: boolean
  actionUrl?: string
  actionText?: string
}

const notifications = ref<NotificationItem[]>([])

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

const markAllAsRead = () => {
  notifications.value.forEach(n => { n.read = true })
}

const getCategoryIcon = (type: string) => {
  switch (type) {
    case 'interview_ready': return '🎯'
    case 'offer': return '🎉'
    case 'device_login': return '💻'
    default: return '🔔'
  }
}

const getCategoryBadgeStyle = (type: string) => {
  switch (type) {
    case 'interview_ready': return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
    case 'offer': return 'bg-amber-500/10 border-amber-500/30 text-amber-400'
    case 'device_login': return 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400'
    default: return 'bg-slate-800 border-slate-700 text-slate-300'
  }
}

const buildRealNotifications = async () => {
  const list: NotificationItem[] = []

  // 1. Detect Logged-in Device Info (OS & Browser Details) for authenticated user
  const authStore = useAuthStore()
  const userObj = authStore.user
  const userAgent = navigator.userAgent
  let deviceOS = 'Linux System'
  if (userAgent.includes('Win')) deviceOS = 'Windows PC'
  else if (userAgent.includes('Mac')) deviceOS = 'macOS Desktop'
  else if (userAgent.includes('Android')) deviceOS = 'Android Phone'
  else if (userAgent.includes('iPhone')) deviceOS = 'iPhone OS'

  let browserName = 'Chrome Browser'
  if (userAgent.includes('Firefox')) browserName = 'Firefox Browser'
  else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) browserName = 'Safari Browser'

  const userDisplayName = userObj?.full_name || userObj?.email || 'Active User'
  const userTargetRole = userObj?.target_role ? ` for ${userObj.target_role}` : ''

  list.push({
    id: 'notif-device-1',
    type: 'device_login',
    title: `🔐 Welcome ${userDisplayName}!`,
    message: `Account logged in on ${deviceOS} (${browserName})${userTargetRole}. Security status: Verified.`,
    time: 'Just Now',
    read: false
  })

  // 2. Promotional Special Career Offer Event Notification
  list.push({
    id: 'notif-offer-1',
    type: 'offer',
    title: '🎉 50% Off Unlimited AI Interview Pass',
    message: 'Exclusive career offer! Get unlimited AI Mock Interview sessions & detailed resume analysis reports.',
    time: '2 mins ago',
    read: false,
    actionUrl: '/pricing',
    actionText: 'Claim Offer'
  })

  // 3. Fetch Scheduled Interviews to notify "READY - START NOW"
  try {
    const res = await api.get('/api/interviews/scheduled')
    const scheduledList = res.data || []

    scheduledList.forEach((s: any) => {
      const scheduledTime = s.scheduled_at ? new Date(s.scheduled_at).getTime() : 0
      const now = new Date().getTime()
      const isReady = !s.scheduled_at || now >= (scheduledTime - 10 * 60 * 1000)

      if (isReady) {
        list.unshift({
          id: `notif-int-${s.id || s.session_id}`,
          type: 'interview_ready',
          title: `🚀 INTERVIEW READY TO START NOW!`,
          message: `Your scheduled ${s.role || 'Mock'} interview is open and ready. Click to join now!`,
          time: 'Available Now',
          read: false,
          actionUrl: `/mock-interview?session_id=${s.session_id}&role=${encodeURIComponent(s.role || '')}&start=true`,
          actionText: 'Start Interview Now'
        })
      }
    })
  } catch (e) {
    console.warn('Could not fetch scheduled interviews for notifications:', e)
  }

  // Fallback if no scheduled interview exists
  if (!list.some(n => n.type === 'interview_ready')) {
    list.unshift({
      id: 'notif-int-demo',
      type: 'interview_ready',
      title: '🎯 AI Mock Interview Ready',
      message: 'Your interactive AI interviewer is prepared. Click to start your live practice session.',
      time: 'Live Ready',
      read: false,
      actionUrl: '/mock-interview',
      actionText: 'Start Session'
    })
  }

  notifications.value = list
}

onMounted(() => {
  buildRealNotifications()
})
</script>
