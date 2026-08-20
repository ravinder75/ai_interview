<template>
  <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-base font-bold text-slate-100 flex items-center gap-2">
        <Award class="w-5 h-5 text-amber-400" />
        Overall Answer Score
      </h3>
      <div class="text-2xl font-extrabold text-gradient-gold">
        {{ overallScore }} <span class="text-xs text-slate-400 font-normal">/ 100</span>
      </div>
    </div>

    <!-- 4 Pillar Metrics Grid -->
    <div class="grid grid-cols-2 gap-3 text-xs">
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between items-center">
        <span class="text-slate-400">Technical Depth</span>
        <span class="font-bold text-indigo-400">{{ technicalDepth }}%</span>
      </div>
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between items-center">
        <span class="text-slate-400">Clarity</span>
        <span class="font-bold text-purple-400">{{ clarity }}%</span>
      </div>
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between items-center">
        <span class="text-slate-400">Relevance</span>
        <span class="font-bold text-emerald-400">{{ relevance }}%</span>
      </div>
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between items-center">
        <span class="text-slate-400">Confidence</span>
        <span class="font-bold text-cyan-400">{{ confidence }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Award } from 'lucide-vue-next'

defineProps<{
  overallScore: number;
  technicalDepth: number;
  clarity: number;
  relevance: number;
  confidence: number;
}>()
</script>
