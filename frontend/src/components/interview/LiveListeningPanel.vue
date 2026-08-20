<template>
  <div class="glass-card rounded-2xl p-4 border border-slate-800 space-y-3 bg-slate-950/90 text-xs">
    
    <!-- Top Row: Microphone & Camera Track Status Badges -->
    <div class="flex items-center justify-between border-b border-slate-800 pb-2.5 font-mono">
      <div class="flex items-center gap-2">
        <span class="font-bold text-slate-300 flex items-center gap-1.5">
          <Mic class="w-4 h-4 text-indigo-400" />
          <span>MICROPHONE STATUS:</span>
        </span>
      </div>

      <!-- State Badges -->
      <div>
        <span v-if="aiState === 'AI_ASKING_QUESTION'" class="px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold flex items-center gap-1.5 animate-pulse">
          <span class="w-2 h-2 rounded-full bg-purple-400"></span>
          <span>🤖 AI SPEAKING QUESTION</span>
        </span>
        <span v-else-if="voiceState === 'SPEECH_DETECTED'" class="px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40 font-bold flex items-center gap-1.5 animate-pulse">
          <span class="w-2 h-2 rounded-full bg-blue-400"></span>
          <span>🔊 SPEECH DETECTED</span>
        </span>
        <span v-else-if="voiceState === 'TRANSCRIBING'" class="px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-bold flex items-center gap-1.5">
          <span>📝 TRANSCRIBING...</span>
        </span>
        <span v-else-if="voiceState === 'LISTENING'" class="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>🟢 LISTENING</span>
        </span>
        <span v-else-if="voiceState === 'SILENCE_WARNING'" class="px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold flex items-center gap-1.5">
          <span>🟠 SILENCE WAITING</span>
        </span>
        <span v-else-if="voiceState === 'MIC_ERROR' || voiceState === 'MIC_BLOCKED'" class="px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold flex items-center gap-1.5">
          <span>🔴 MIC BLOCKED / ERROR</span>
        </span>
        <span v-else class="px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-400 font-bold">
          <span>⚪ IDLE / READY</span>
        </span>
      </div>
    </div>

    <!-- Middle Row: Real RMS Audio Volume Level Meter -->
    <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
      <div class="flex items-center justify-between text-[11px] font-mono">
        <span class="text-slate-400 font-bold">AUDIO LEVEL MONITOR:</span>
        <span class="text-indigo-300 font-bold">{{ audioLevel }}%</span>
      </div>

      <!-- Volume Equalizer Bars -->
      <div class="flex items-end gap-1 h-4 bg-slate-950 px-2 py-1 rounded-lg border border-slate-800">
        <div
          v-for="(barHeight, idx) in bars"
          :key="idx"
          class="flex-1 rounded-sm transition-all duration-75"
          :class="isWeakSignal ? 'bg-amber-500' : 'bg-gradient-to-t from-emerald-500 to-indigo-400'"
          :style="{ height: `${barHeight}%` }"
        ></div>
      </div>

      <!-- Weak Audio Signal Alert Banner -->
      <div v-if="isWeakSignal && micActive" class="flex items-center gap-2 text-[10px] text-amber-400 font-bold pt-1">
        <AlertCircle class="w-3.5 h-3.5" />
        <span>⚠ Weak microphone input signal. Please speak clearly into your microphone.</span>
      </div>
    </div>

    <!-- Bottom Row: Real-time Live Interim Speech Stream Box -->
    <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
      <div class="flex items-center justify-between text-[10px] font-mono text-slate-400 font-bold">
        <span>LIVE SPEECH INPUT STREAM:</span>
        <span v-if="(speakingSeconds || 0) > 0" class="text-emerald-400 font-bold flex items-center gap-1 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
          ⏱️ {{ speakingSeconds }}s Answer Time
        </span>
        <span v-else class="text-slate-500 font-normal">⏱️ 0s</span>
      </div>

      <div class="min-h-[44px] bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 text-xs font-mono flex items-center">
        <p v-if="interimTranscript" class="text-indigo-300 font-bold animate-pulse">
          "{{ interimTranscript }}"
        </p>
        <p v-else-if="finalTranscript" class="text-slate-100 font-semibold">
          "{{ finalTranscript }}"
        </p>
        <p v-else-if="voiceState === 'SPEECH_DETECTED' || voiceState === 'TRANSCRIBING'" class="text-blue-400 font-bold animate-pulse">
          "🔊 Voice detected... Transcribing your speech..."
        </p>
        <p v-else class="text-slate-500 italic">
          {{ silenceMessage || 'Start speaking into your microphone to transcribe your answer live...' }}
        </p>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { Mic, AlertCircle } from 'lucide-vue-next'

defineProps<{
  voiceState: string
  aiState?: string
  audioLevel: number
  isWeakSignal: boolean
  bars: number[]
  interimTranscript: string
  finalTranscript: string
  silenceSeconds: number
  speakingSeconds?: number
  silenceMessage: string
  micActive: boolean
}>()
</script>
