<template>
  <div class="flex items-center gap-2 px-3 py-1 bg-slate-900/90 rounded-xl border border-slate-800 font-mono text-[11px] select-none">
    <div class="flex items-center gap-1.5 font-bold" :class="audioLevel.isWeakSignal.value ? 'text-amber-400' : 'text-emerald-400'">
      <span class="w-2 h-2 rounded-full" :class="audioLevel.isWeakSignal.value ? 'bg-amber-400 animate-ping' : 'bg-emerald-400 animate-pulse'"></span>
      <span>MIC</span>
    </div>

    <!-- 10 Bar Volume Meter -->
    <div class="flex items-end gap-0.5 h-3.5 w-20 bg-slate-950 px-1 py-0.5 rounded border border-slate-800/80">
      <div
        v-for="(barHeight, idx) in audioLevel.bars.value"
        :key="idx"
        class="flex-1 rounded-sm transition-all duration-75"
        :class="audioLevel.isWeakSignal.value ? 'bg-amber-500' : 'bg-gradient-to-t from-emerald-500 to-indigo-400'"
        :style="{ height: `${barHeight}%` }"
      ></div>
    </div>

    <span class="text-[10px] text-slate-400 font-bold min-w-[28px]">
      {{ audioLevel.audioLevel.value }}%
    </span>
  </div>
</template>

<script setup lang="ts">
import { watch, onMounted, onUnmounted } from 'vue'
import { useAudioLevel } from '../composables/useAudioLevel'

const props = defineProps<{
  stream: MediaStream | null
  active: boolean
}>()

const audioLevel = useAudioLevel()

watch(
  () => [props.stream, props.active],
  () => {
    if (props.stream && props.active) {
      audioLevel.startAnalyser(props.stream, props.active)
    } else {
      audioLevel.stopAnalyser()
    }
  },
  { immediate: true }
)

onMounted(() => {
  if (props.stream && props.active) {
    audioLevel.startAnalyser(props.stream, props.active)
  }
})

onUnmounted(() => {
  audioLevel.stopAnalyser()
})
</script>
