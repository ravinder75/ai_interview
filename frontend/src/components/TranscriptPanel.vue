<template>
  <div class="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
    <div class="flex items-center justify-between text-xs font-semibold text-slate-300">
      <span class="flex items-center gap-2">
        <FileText class="w-4 h-4 text-indigo-400" />
        Live Speech Transcript
      </span>
      <button v-if="transcript" @click="$emit('clear')" class="text-slate-500 hover:text-slate-300 text-[11px]">
        Clear Transcript
      </button>
    </div>

    <div class="bg-slate-900/80 rounded-xl p-4 min-h-[100px] max-h-[180px] overflow-y-auto border border-slate-800 text-sm text-slate-200 leading-relaxed font-mono">
      <p v-if="transcript">{{ transcript }}</p>
      <p v-else class="text-slate-500 italic text-xs">
        Your spoken speech response will appear here in real time... Click 'Start Recording' above to speak.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileText } from 'lucide-vue-next'

defineProps<{
  transcript: string;
}>()

defineEmits(['clear'])
</script>
