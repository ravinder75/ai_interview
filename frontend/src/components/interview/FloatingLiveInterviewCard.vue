<template>
  <div
    v-if="activeLiveSession && !isMockInterviewPage"
    ref="floatingWrapper"
    class="fixed z-50 font-sans select-none transition-shadow"
    :style="cardPositionStyle"
  >
    <!-- Floating Draggable Active Live Interview Card with AI Avatar & Stream Status -->
    <div class="glass-card rounded-2xl p-4 border border-emerald-500/50 bg-slate-950/95 backdrop-blur-xl shadow-2xl shadow-emerald-500/20 w-84 space-y-3.5">
      
      <!-- Card Header (Draggable Handle) -->
      <div
        @mousedown="startDrag"
        class="flex items-center justify-between pb-2 border-b border-slate-800 cursor-grab active:cursor-grabbing"
        title="Drag to reposition live interview card anywhere"
      >
        <div class="flex items-center gap-2 pointer-events-none">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="text-xs font-extrabold text-slate-100 uppercase tracking-wider">LIVE INTERVIEW ACTIVE</span>
        </div>
        <span class="text-[10px] text-slate-400 font-mono pointer-events-none">⋮⋮ Drag</span>
      </div>

      <!-- Live Session Details & AI Interviewer Avatar -->
      <div class="flex items-center gap-3 bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
        <!-- AI Bot Avatar Icon -->
        <div class="w-10 h-10 rounded-xl bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-xl shrink-0">
          🤖
        </div>

        <div class="space-y-0.5 min-w-0 flex-1">
          <h4 class="font-extrabold text-slate-100 text-xs truncate">{{ activeLiveSession.role }}</h4>
          <div class="flex items-center gap-2 text-[10px] text-slate-400 font-mono">
            <span>ID: <strong class="text-slate-300">{{ activeLiveSession.session_id ? activeLiveSession.session_id.slice(0, 10) + '...' : 'sess-live' }}</strong></span>
            <span class="text-emerald-400 font-bold bg-emerald-500/10 px-1.5 py-0.2 rounded border border-emerald-500/20">LIVE 🔴</span>
          </div>
        </div>
      </div>

      <!-- Mini Dual Video Stage: AI Interviewer Avatar & Candidate Live Stream -->
      <div class="grid grid-cols-2 gap-2">
        <!-- AI Interviewer Mini Video Stage -->
        <div class="relative h-28 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center justify-center overflow-hidden p-2 text-center">
          <div class="w-10 h-10 rounded-full bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-xl shadow-md shadow-indigo-600/20 animate-pulse">
            👩
          </div>
          <span class="text-[10px] font-bold text-slate-200 mt-1">Sophia (AI)</span>
          <span class="text-[9px] text-emerald-400 font-mono font-bold flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Listening...
          </span>
        </div>

        <!-- Candidate Live Camera Mini Video Stream -->
        <div class="relative h-28 rounded-xl bg-slate-900 border border-slate-800 overflow-hidden flex items-center justify-center">
          <video ref="candidateMiniVideo" autoplay playsinline muted class="w-full h-full object-cover bg-slate-950"></video>
          <span class="absolute top-1.5 right-1.5 text-[9px] px-1.5 py-0.2 rounded bg-slate-950/80 text-emerald-400 font-mono font-bold border border-emerald-500/20 z-10">
            YOU 📹
          </span>
        </div>
      </div>

      <!-- Action Button to Return to Live Room -->
      <button
        @click="returnToLiveRoom"
        type="button"
        class="w-full btn-primary py-2 px-3 text-xs font-extrabold flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 border-emerald-400 shadow-md shadow-emerald-600/30 uppercase tracking-wider text-[11px] cursor-pointer"
      >
        <Play class="w-3.5 h-3.5" />
        <span>[ Return to Live Room ]</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Play } from 'lucide-vue-next'
import { useMediaDevices } from '../../composables/useMediaDevices'

const route = useRoute()
const router = useRouter()
const media = useMediaDevices()
const activeLiveSession = ref<any>(null)
const candidateMiniVideo = ref<HTMLVideoElement | null>(null)

const returnToLiveRoom = () => {
  if (activeLiveSession.value && activeLiveSession.value.session_id) {
    router.push({
      path: '/mock-interview',
      query: {
        session_id: activeLiveSession.value.session_id,
        role: activeLiveSession.value.role || 'Software Engineer',
        start: 'true',
        t: Date.now().toString()
      }
    })
  } else {
    router.push('/mock-interview')
  }
}

const isMockInterviewPage = computed(() => route.path === '/mock-interview')

// Draggable positioning state (Default bottom-right corner)
const posX = ref<number>(window.innerWidth - 350)
const posY = ref<number>(window.innerHeight - 200)
let isDragging = false
let dragStartX = 0
let dragStartY = 0
let startPosX = 0
let startPosY = 0

const cardPositionStyle = computed(() => ({
  left: `${posX.value}px`,
  top: `${posY.value}px`
}))

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

const startDrag = (e: MouseEvent) => {
  isDragging = true
  dragStartX = e.clientX
  dragStartY = e.clientY
  startPosX = posX.value
  startPosY = posY.value

  window.addEventListener('mousemove', onDragging)
  window.addEventListener('mouseup', stopDrag)
}

const onDragging = (e: MouseEvent) => {
  if (!isDragging) return
  const dx = e.clientX - dragStartX
  const dy = e.clientY - dragStartY

  const width = 320
  const height = 160

  const newX = Math.max(10, Math.min(window.innerWidth - width - 10, startPosX + dx))
  const newY = Math.max(10, Math.min(window.innerHeight - height - 10, startPosY + dy))

  posX.value = newX
  posY.value = newY
}

const stopDrag = () => {
  isDragging = false
  window.removeEventListener('mousemove', onDragging)
  window.removeEventListener('mouseup', stopDrag)
}

watch(
  () => route.path,
  async () => {
    checkActiveSession()
    if (activeLiveSession.value && !isMockInterviewPage.value) {
      if (!media.stream.value) {
        try {
          await media.requestPermissions()
        } catch (e) {}
      }
      await nextTick()
      if (candidateMiniVideo.value && media.stream.value) {
        media.attachStreamToVideo(candidateMiniVideo.value)
      }
    }
  },
  { immediate: true }
)

watch(
  [candidateMiniVideo, media.stream],
  async ([videoEl, newStream]) => {
    await nextTick()
    if (videoEl && newStream) {
      media.attachStreamToVideo(videoEl)
    }
  },
  { immediate: true }
)

let timer: any = null

onMounted(async () => {
  checkActiveSession()
  try {
    await media.requestPermissions()
  } catch (e) {
    console.warn('Mini media permission skipped:', e)
  }
  timer = setInterval(() => {
    checkActiveSession()
  }, 500)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
