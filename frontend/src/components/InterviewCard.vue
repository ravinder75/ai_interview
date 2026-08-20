<template>
  <router-link :to="`/mock-interview/${session.session_id || session.id}/report`" class="glass-card glass-card-hover rounded-2xl p-5 border border-slate-800 space-y-4 block hover:border-indigo-500/50 transition-all cursor-pointer">
    <div class="flex items-center justify-between">
      <span class="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold uppercase font-mono">
        {{ session.mode || 'Mock' }} Mode
      </span>
      <span class="text-xs text-slate-400 font-mono">{{ formatDate(session.created_at) }}</span>
    </div>

    <div>
      <h4 class="font-bold text-slate-100 text-base leading-tight flex items-center justify-between">
        <span>{{ session.title }}</span>
        <span class="text-indigo-400 text-xs font-mono">View Report ➔</span>
      </h4>
      <p class="text-xs text-slate-400 mt-1">Role: <strong class="text-slate-200">{{ session.role }}</strong> ({{ session.experience_level || 'Mid-Level' }})</p>
    </div>

    <!-- Score Bar -->
    <div class="space-y-1">
      <div class="flex justify-between text-xs font-semibold font-mono">
        <span class="text-slate-400">Assessment Score</span>
        <span :class="session.overall_score !== null && session.overall_score !== undefined ? 'text-emerald-400 font-bold' : 'text-slate-400 font-normal italic'">
          {{ session.overall_score !== null && session.overall_score !== undefined ? `${Math.round(session.overall_score)}%` : 'Not Assessed' }}
        </span>
      </div>
      <div class="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
        <div class="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full transition-all" :style="{ width: `${session.overall_score || 0}%` }"></div>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import type { InterviewSession } from '../types'

defineProps<{
  session: InterviewSession;
}>()

const formatDate = (dateStr?: string) => {
  if (!dateStr) return 'Recent'
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}
</script>
