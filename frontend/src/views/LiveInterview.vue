<template>
  <div class="max-w-7xl mx-auto space-y-4 py-2">
    <!-- DEVICE CHECK STEP -->
    <div v-if="step === 'device_check'" class="glass-card rounded-2xl p-8 border border-slate-800 max-w-xl mx-auto my-8 space-y-6 shadow-2xl">
      <div class="text-center space-y-2">
        <h2 class="text-xl font-bold text-slate-100">Interview Setup & Device Check</h2>
        <p class="text-xs text-slate-400 font-sans">Verify your camera and microphone permissions before entering the live session</p>
      </div>

      <div class="relative bg-slate-950 rounded-xl overflow-hidden aspect-video border border-slate-800 flex items-center justify-center">
        <video ref="previewVideo" autoplay playsinline muted class="w-full h-full object-cover"></video>
        <div v-if="!media.cameraEnabled.value || !media.stream.value" class="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/90 text-slate-400 space-y-2 text-center p-4">
          <CameraOff class="w-8 h-8 text-slate-500" />
          <span class="text-xs font-semibold">Camera is turned off / Permission pending</span>
        </div>
      </div>

      <div class="space-y-2 text-xs">
        <div class="flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800">
          <span class="flex items-center gap-2">
            <Video class="w-4 h-4 text-indigo-400" />
            <span>Camera</span>
          </span>
          <span :class="media.cameraEnabled.value ? 'text-emerald-400' : 'text-amber-400'" class="font-bold">
            {{ media.cameraEnabled.value ? '✓ Camera Active' : '○ Pending' }}
          </span>
        </div>

        <div class="flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800">
          <span class="flex items-center gap-2">
            <Mic class="w-4 h-4 text-indigo-400" />
            <span>Microphone</span>
          </span>
          <span :class="media.micEnabled.value ? 'text-emerald-400' : 'text-amber-400'" class="font-bold">
            {{ media.micEnabled.value ? '✓ Microphone Active' : '○ Pending' }}
          </span>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <button @click="media.requestPermissions" class="flex-1 btn-secondary py-2.5 text-xs font-bold flex items-center justify-center gap-2">
          <RefreshCw class="w-3.5 h-3.5" />
          <span>Grant Media Permissions</span>
        </button>

        <button @click="enterInterviewRoom" class="flex-1 btn-primary py-2.5 text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30">
          <Play class="w-4 h-4" />
          <span>Enter Live Room</span>
        </button>
      </div>
    </div>

    <!-- LIVE INTERVIEW ROOM -->
    <div v-else class="space-y-4">
      <!-- Top Bar Navigation -->
      <div class="glass-card rounded-2xl p-4 border border-slate-800 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold">
            <Bot class="w-5 h-5" />
          </div>
          <div>
            <h2 class="text-sm font-bold text-slate-100">AI MOCK INTERVIEW ROOM</h2>
            <p class="text-[11px] text-slate-400 font-mono">{{ roleName }}</p>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <!-- Audio Equalizer -->
          <AudioWaveform :stream="media.stream.value" :active="media.micEnabled.value" />

          <!-- AI Status Badge -->
          <span v-if="engine.aiState.value === 'AI_ASKING_QUESTION'" class="px-3 py-1 rounded-xl bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 text-xs font-bold flex items-center gap-1.5 animate-pulse">
            🤖 AI Asking Question
          </span>
          <span v-else-if="engine.aiState.value === 'AI_LISTENING'" class="px-3 py-1 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-bold flex items-center gap-1.5">
            🎧 AI Listening
          </span>

          <button @click="confirmEndInterview" class="btn-secondary py-1.5 px-3 text-xs font-bold text-rose-400 border-rose-500/20 hover:bg-rose-500/10">
            End Interview
          </button>
        </div>
      </div>

      <!-- Main Room Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- AI Avatar -->
        <div class="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col items-center justify-between min-h-[340px] relative space-y-3">
          <div class="relative mt-2">
            <div
              :class="[
                'w-24 h-24 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-2xl transition-all duration-300',
                engine.isTTSActive.value ? 'ring-8 ring-indigo-500/30 scale-105' : 'ring-2 ring-slate-700'
              ]"
            >
              <Bot class="w-12 h-12" />
            </div>
          </div>

          <div class="text-center space-y-1 w-full px-2">
            <h3 class="font-bold text-slate-100 text-sm">AI Technical Interviewer</h3>
            <p class="text-[11px] text-indigo-300 italic line-clamp-2">"{{ currentQuestionText || 'Generating questions...' }}"</p>
          </div>
        </div>

        <!-- User Live Video Preview -->
        <div class="glass-card rounded-2xl p-4 border border-slate-800 flex flex-col justify-between min-h-[340px] relative bg-slate-950">
          <div class="relative flex-1 rounded-xl overflow-hidden bg-slate-900 flex items-center justify-center">
            <video ref="userVideo" autoplay playsinline muted class="w-full h-full object-cover"></video>
          </div>

          <div class="mt-2.5 space-y-2">
            <div class="flex items-center gap-1.5">
              <input
                v-model="userAnswerText"
                type="text"
                placeholder="Type/speak your answer..."
                @keyup.enter="submitAnswer"
                class="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500"
              />
              <button @click="submitAnswer" class="btn-primary px-3 py-1.5 text-xs font-bold flex items-center gap-1">
                <Send class="w-3 h-3" />
                <span>Send</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Candidate Info Card -->
        <div class="glass-card rounded-2xl p-5 border border-slate-800 space-y-3 flex flex-col justify-between min-h-[340px]">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5 border-b border-slate-800 pb-2">
            <CheckCircle class="w-4 h-4 text-emerald-400" />
            <span>Profile Context & Status</span>
          </h4>
          <div class="space-y-2 text-xs">
            <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
              <span class="text-[9px] font-bold text-slate-400 uppercase">Voice State:</span>
              <p class="text-indigo-300 font-bold font-mono">{{ engine.silenceMessage.value || 'AI is listening...' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMediaDevices } from '../composables/useMediaDevices'
import { useInterviewEngine } from '../composables/useInterviewEngine'
import AudioWaveform from '../components/AudioWaveform.vue'
import { Bot, CameraOff, Video, Mic, RefreshCw, Play, Send, CheckCircle } from 'lucide-vue-next'
import { api } from '../services/api'

const route = useRoute()
const router = useRouter()
const media = useMediaDevices()
const engine = useInterviewEngine()

const interviewId = computed(() => route.params.interviewId as string)

const step = ref<'device_check' | 'room'>('device_check')
const previewVideo = ref<HTMLVideoElement | null>(null)
const userVideo = ref<HTMLVideoElement | null>(null)
const roleName = ref('Software Engineer')
const currentQuestionText = ref('')
const userAnswerText = ref('')

watch(engine.finalTranscript, (newText) => {
  if (newText) {
    userAnswerText.value = newText
  }
})

watch(
  () => [step.value, media.stream.value],
  async () => {
    await nextTick()
    if (step.value === 'device_check' && previewVideo.value && media.stream.value) {
      media.attachStreamToVideo(previewVideo.value)
    } else if (step.value === 'room' && userVideo.value && media.stream.value) {
      media.attachStreamToVideo(userVideo.value)
    }
  }
)

const enterInterviewRoom = async () => {
  if (!media.stream.value) {
    await media.requestPermissions()
  }
  step.value = 'room'
  await nextTick()
  if (userVideo.value) {
    media.attachStreamToVideo(userVideo.value)
  }
}

const submitAnswer = async () => {
  const ans = userAnswerText.value.trim()
  if (!ans) return
  userAnswerText.value = ''
  engine.resetTranscripts()
  try {
    await api.post('/api/interviews/submit-answer', {
      session_id: interviewId.value,
      question_id: 1,
      user_answer: ans
    })
  } catch (e) {}
}

const confirmEndInterview = () => {
  media.stopAllTracks()
  engine.stopListening()
  router.push('/mock-interview')
}

onMounted(() => {
  media.refreshDevicesList()
  media.requestPermissions()
})

onUnmounted(() => {
  media.stopAllTracks()
  engine.stopListening()
})
</script>
