<template>
  <div class="glass-card rounded-2xl p-6 border border-indigo-500/30 space-y-6 bg-slate-900/90">
    
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-800 pb-4">
      <div>
        <span class="text-xs uppercase font-extrabold tracking-wider text-indigo-400">AI Coaching Feedback</span>
        <h3 class="text-xl font-bold text-slate-100 mt-0.5">Evaluation & Answer Practice Refinement</h3>
      </div>
      <div class="text-right">
        <span class="text-xs text-slate-400 font-semibold block">Overall Readiness</span>
        <span class="text-3xl font-extrabold text-gradient-gold">{{ feedback.overall_score }}/100</span>
      </div>
    </div>

    <!-- STAR Framework Component -->
    <StarAnalysis v-if="feedback.star_analysis" :starScore="feedback.star_analysis" />

    <!-- Strengths & Growth Bullet Points -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
      
      <!-- Demonstrated Strengths -->
      <div class="space-y-2">
        <span class="font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
          <CheckCircle2 class="w-4 h-4" /> Strong Elements
        </span>
        <ul class="space-y-1.5">
          <li
            v-for="s in feedback.strengths"
            :key="s"
            class="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-slate-200 flex items-start gap-2"
          >
            <span class="text-emerald-400 font-bold">✓</span>
            {{ s }}
          </li>
        </ul>
      </div>

      <!-- Key Growth Areas -->
      <div class="space-y-2">
        <span class="font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
          <AlertCircle class="w-4 h-4" /> Recommended Improvements
        </span>
        <ul class="space-y-1.5">
          <li
            v-for="imp in feedback.improvements"
            :key="imp"
            class="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-slate-200 flex items-start gap-2"
          >
            <span class="text-amber-400 font-bold">•</span>
            {{ imp }}
          </li>
        </ul>
      </div>

    </div>

    <!-- Suggested Practice Answer -->
    <div class="bg-slate-950/90 rounded-xl p-4 border border-slate-800 space-y-2">
      <span class="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
        <Lightbulb class="w-4 h-4" /> Practice Refined Answer (For Revision Only)
      </span>
      <p class="text-xs text-slate-300 italic leading-relaxed">
        "{{ feedback.suggested_answer }}"
      </p>
    </div>

    <!-- Follow up questions -->
    <div v-if="feedback.follow_up_questions && feedback.follow_up_questions.length" class="space-y-2">
      <span class="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
        <HelpCircle class="w-4 h-4" /> Potential Follow-Up Questions
      </span>
      <ol class="space-y-1 list-decimal list-inside text-xs text-slate-300 pl-1">
        <li v-for="q in feedback.follow_up_questions" :key="q" class="py-1 border-b border-slate-800/50">
          {{ q }}
        </li>
      </ol>
    </div>

  </div>
</template>

<script setup lang="ts">
import { CheckCircle2, AlertCircle, Lightbulb, HelpCircle } from 'lucide-vue-next'
import StarAnalysis from './StarAnalysis.vue'
import type { FeedbackData } from '../types'

defineProps<{
  feedback: FeedbackData;
}>()
</script>
