<template>
  <div class="glass-card rounded-2xl p-5 border border-slate-800 space-y-4 bg-slate-950 flex flex-col justify-between shadow-xl relative overflow-hidden">
    
    <!-- Top Header -->
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <div class="flex items-center gap-2">
        <Bot class="w-4 h-4 text-indigo-400" />
        <span class="text-xs font-bold text-slate-100 uppercase tracking-wider">AI HUMAN INTERVIEWER</span>
      </div>

      <!-- State Badge -->
      <span
        :class="[
          'text-[10px] px-2.5 py-1 rounded-full border font-mono font-bold flex items-center gap-1.5 transition-all',
          currentState === 'SPEAKING' ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40 animate-pulse' :
          currentState === 'LISTENING' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40' :
          currentState === 'THINKING' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40 animate-pulse' :
          'bg-slate-900 text-slate-400 border-slate-700'
        ]"
      >
        <span
          :class="[
            'w-2 h-2 rounded-full',
            currentState === 'SPEAKING' ? 'bg-indigo-400 animate-ping' :
            currentState === 'LISTENING' ? 'bg-emerald-400 animate-pulse' :
            currentState === 'THINKING' ? 'bg-purple-400 animate-ping' :
            'bg-slate-500'
          ]"
        ></span>
        <span>{{ stateBadgeText }}</span>
      </span>
    </div>

    <!-- Avatar Visual Stage -->
    <div class="relative h-[250px] rounded-xl overflow-hidden bg-slate-900/90 border border-slate-800 flex flex-col items-center justify-center p-4 shadow-inner group">
      
      <!-- Ambient Glow Behind Avatar -->
      <div
        :class="[
          'absolute w-40 h-40 rounded-full blur-3xl transition-all duration-700 opacity-30',
          currentState === 'SPEAKING' ? 'bg-indigo-500 scale-125' :
          currentState === 'LISTENING' ? 'bg-emerald-500 scale-110' :
          currentState === 'THINKING' ? 'bg-purple-500 scale-125' :
          'bg-slate-700'
        ]"
      ></div>

      <!-- SVG Animated Vector Humanoid Avatar -->
      <div class="relative z-10 flex flex-col items-center justify-center space-y-3">
        <div class="relative">
          <!-- Animated Speaking Halo Ring -->
          <div
            v-if="currentState === 'SPEAKING'"
            class="absolute -inset-3 rounded-full border-2 border-indigo-400/40 animate-ping pointer-events-none"
          ></div>
          <div
            v-if="currentState === 'LISTENING'"
            class="absolute -inset-2 rounded-full border border-emerald-400/30 animate-pulse pointer-events-none"
          ></div>

          <!-- Avatar Face Circle Graphic -->
          <div class="w-24 h-24 rounded-full bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-slate-700 flex items-center justify-center shadow-2xl relative overflow-hidden">
            
            <!-- Female Avatar SVG -->
            <svg v-if="gender === 'female'" viewBox="0 0 100 100" class="w-20 h-20 text-indigo-300">
              <!-- Hair Back -->
              <path d="M25 40 Q50 15 75 40 Q80 70 75 85 Q50 90 25 85 Z" fill="#312E81" />
              <!-- Face Skin -->
              <circle cx="50" cy="45" r="24" fill="#FCE7F3" />
              <!-- Hair Front Fringe -->
              <path d="M26 38 Q50 20 74 38 Q60 25 40 28 Z" fill="#4338CA" />
              <!-- Eyes -->
              <circle cx="41" cy="44" r="3" fill="#1E1B4B" />
              <circle cx="59" cy="44" r="3" fill="#1E1B4B" />
              <!-- Mouth (Animated when speaking) -->
              <path
                v-if="currentState === 'SPEAKING'"
                d="M43 57 Q50 65 57 57 Z"
                fill="#BE185D"
                class="animate-bounce"
              />
              <path v-else d="M44 56 Q50 60 56 56" stroke="#BE185D" stroke-width="2.5" stroke-linecap="round" fill="none" />
            </svg>

            <!-- Male Avatar SVG -->
            <svg v-else viewBox="0 0 100 100" class="w-20 h-20 text-slate-200">
              <!-- Hair Back -->
              <path d="M28 35 Q50 15 72 35 L74 45 Q50 30 26 45 Z" fill="#1E293B" />
              <!-- Face Skin -->
              <circle cx="50" cy="46" r="23" fill="#FEF3C7" />
              <!-- Hair Top -->
              <path d="M27 38 Q50 20 73 38 Q50 25 27 38 Z" fill="#0F172A" />
              <!-- Glasses Frame -->
              <rect x="34" y="40" width="13" height="9" rx="2" stroke="#334155" stroke-width="2" fill="none" />
              <rect x="53" y="40" width="13" height="9" rx="2" stroke="#334155" stroke-width="2" fill="none" />
              <line x1="47" y1="44" x2="53" y2="44" stroke="#334155" stroke-width="2" />
              <!-- Eyes -->
              <circle cx="40.5" cy="44.5" r="2" fill="#0F172A" />
              <circle cx="59.5" cy="44.5" r="2" fill="#0F172A" />
              <!-- Mouth (Animated when speaking) -->
              <path
                v-if="currentState === 'SPEAKING'"
                d="M44 58 Q50 65 56 58 Z"
                fill="#475569"
                class="animate-bounce"
              />
              <path v-else d="M44 57 Q50 60 56 57" stroke="#475569" stroke-width="2.5" stroke-linecap="round" fill="none" />
            </svg>
          </div>
        </div>

        <!-- Name & Title -->
        <div class="text-center space-y-0.5">
          <h4 class="font-extrabold text-slate-100 text-sm tracking-wide flex items-center justify-center gap-1.5">
            <span>{{ name }}</span>
            <span class="text-[10px] text-indigo-400 font-mono font-bold bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">AI</span>
          </h4>
          <p class="text-[11px] text-slate-400 font-medium">{{ role }}</p>
        </div>
      </div>

      <!-- Action Subtitle / Captions Bar -->
      <div class="absolute bottom-2 left-3 right-3 bg-slate-950/80 backdrop-blur-sm border border-slate-800 rounded-lg p-2 text-[10px] text-center text-slate-300 font-sans">
        <span v-if="currentState === 'SPEAKING'" class="text-indigo-300 font-semibold">{{ name }} is asking a question...</span>
        <span v-else-if="currentState === 'LISTENING'" class="text-emerald-400 font-semibold">Listening to your answer...</span>
        <span v-else-if="currentState === 'THINKING'" class="text-purple-300 font-semibold">Reviewing your response...</span>
        <span v-else class="text-slate-400">Interviewer ready.</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Bot } from 'lucide-vue-next'
import type { AvatarState, AvatarGender } from '../services/avatarProvider'

const props = withDefaults(
  defineProps<{
    gender?: AvatarGender
    name?: string
    role?: string
    currentState?: AvatarState
  }>(),
  {
    gender: 'female',
    name: 'Sophia',
    role: 'Senior Technical Interviewer',
    currentState: 'IDLE'
  }
)

const stateBadgeText = computed(() => {
  switch (props.currentState) {
    case 'SPEAKING':
      return '🔵 SPEAKING'
    case 'LISTENING':
      return '🟢 LISTENING'
    case 'THINKING':
      return '🟡 THINKING'
    case 'FINISHED':
      return '🏁 FINISHED'
    default:
      return '⚪ IDLE'
  }
})
</script>
