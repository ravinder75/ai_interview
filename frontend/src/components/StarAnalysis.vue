<template>
  <div class="bg-slate-900/90 rounded-2xl p-5 border border-indigo-500/30 space-y-4">
    <div class="flex items-center justify-between">
      <h4 class="text-sm font-bold text-slate-100 flex items-center gap-2">
        <Sparkles class="w-4 h-4 text-amber-400" />
        STAR Behavioral Score Analysis
      </h4>
      <span class="text-xs text-indigo-400 font-semibold uppercase tracking-wider">Framework Evaluation</span>
    </div>

    <!-- 4 STAR Pillar Scores -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 text-center space-y-1">
        <span class="text-xs text-slate-400 font-semibold">Situation</span>
        <div class="text-lg font-extrabold text-indigo-400">{{ starScore?.situation || 8 }}/10</div>
      </div>
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 text-center space-y-1">
        <span class="text-xs text-slate-400 font-semibold">Task</span>
        <div class="text-lg font-extrabold text-purple-400">{{ starScore?.task || 7 }}/10</div>
      </div>
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 text-center space-y-1">
        <span class="text-xs text-slate-400 font-semibold">Action</span>
        <div class="text-lg font-extrabold text-emerald-400">{{ starScore?.action || 9 }}/10</div>
      </div>
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 text-center space-y-1">
        <span class="text-xs text-slate-400 font-semibold">Result</span>
        <div class="text-lg font-extrabold text-cyan-400">{{ starScore?.result || 6 }}/10</div>
      </div>
    </div>

    <!-- Weakest Section Advice -->
    <div class="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-slate-200 flex items-start gap-2.5">
      <AlertCircle class="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
      <div>
        <strong class="text-amber-300 block mb-0.5">Focus Recommendation:</strong>
        <span v-if="weakestSection === 'Result'">
          Your <strong>Result</strong> section ({{ starScore?.result || 6 }}/10) can be improved by adding explicit SLA performance metrics and percentage improvements achieved.
        </span>
        <span v-else-if="weakestSection === 'Task'">
          Your <strong>Task</strong> section ({{ starScore?.task || 7 }}/10) can be strengthened by explicitly framing your individual responsibility vs team scope.
        </span>
        <span v-else>
          Elaborate further on concrete engineering tradeoffs to maximize impact.
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Sparkles, AlertCircle } from 'lucide-vue-next'
import type { StarScore } from '../types'

const props = defineProps<{
  starScore?: StarScore;
}>()

const weakestSection = computed(() => {
  if (!props.starScore) return 'Result'
  const scores = [
    { name: 'Situation', val: props.starScore.situation },
    { name: 'Task', val: props.starScore.task },
    { name: 'Action', val: props.starScore.action },
    { name: 'Result', val: props.starScore.result },
  ]
  scores.sort((a, b) => a.val - b.val)
  return scores[0].name
})
</script>
