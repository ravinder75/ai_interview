<template>
  <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-5">
    <div class="flex items-center justify-between border-b border-slate-800 pb-4">
      <h3 class="text-lg font-bold text-slate-100 flex items-center gap-2">
        <History class="w-5 h-5 text-indigo-400" />
        Recent Session History
      </h3>
      <span class="text-xs text-slate-400">{{ sessions.length }} Saved Sessions</span>
    </div>

    <div v-if="sessions.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <InterviewCard
        v-for="sess in sessions"
        :key="sess.session_id"
        :session="sess"
      />
    </div>
    <div v-else class="text-center py-8 text-xs text-slate-500 italic">
      No completed sessions recorded yet. Start a Mock Interview or Practice Session to track your progress!
    </div>
  </div>
</template>

<script setup lang="ts">
import { History } from 'lucide-vue-next'
import InterviewCard from './InterviewCard.vue'
import type { InterviewSession } from '../types'

defineProps<{
  sessions: InterviewSession[];
}>()
</script>
