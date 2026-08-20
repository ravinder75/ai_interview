<template>
  <div class="flex items-center gap-3">
    <button
      @click="$emit('toggle')"
      :class="[
        'px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition shadow-lg',
        isListening
          ? 'bg-rose-600/30 border border-rose-500 text-rose-300 shadow-rose-600/20 animate-pulse'
          : 'bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/25'
      ]"
    >
      <Mic class="w-4 h-4" />
      <span>{{ isListening ? 'Stop Recording' : 'Start Recording (Speech-to-Text)' }}</span>
    </button>

    <!-- Real-time Voice Audio Visualizer Wave Animation -->
    <AudioVisualizer v-if="isListening" :isListening="isListening" />

    <span v-else class="text-xs font-medium text-slate-400">
      Status: <strong class="text-slate-300">{{ statusText }}</strong>
    </span>
  </div>
</template>

<script setup lang="ts">
import { Mic } from 'lucide-vue-next'
import AudioVisualizer from './AudioVisualizer.vue'

defineProps<{
  isListening: boolean;
  statusText: string;
}>()

defineEmits(['toggle'])
</script>
