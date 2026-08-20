<template>
  <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Briefcase class="w-5 h-5 text-purple-400" />
          Job Description Intelligence
        </h3>
        <p class="text-xs text-slate-400">Paste job posting to extract required skills, keywords, and likely topics</p>
      </div>
      <span class="text-xs px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 font-semibold">Job Prep</span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <input
        v-model="jobTitle"
        type="text"
        placeholder="Job Title (e.g. Senior Software Engineer)"
        class="bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-purple-500"
      />
      <input
        v-model="companyName"
        type="text"
        placeholder="Company Name (Optional)"
        class="bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-purple-500"
      />
    </div>

    <textarea
      v-model="jobText"
      rows="5"
      placeholder="Paste job description text here..."
      class="w-full bg-slate-900 border border-slate-700 rounded-xl p-4 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-purple-500 leading-relaxed font-mono"
    ></textarea>

    <button
      @click="analyzeJob"
      :disabled="isAnalyzing || !jobText.trim()"
      class="w-full btn-primary py-3 flex items-center justify-center gap-2 font-bold"
    >
      <Loader2 v-if="isAnalyzing" class="w-4 h-4 animate-spin" />
      <Sparkles v-else class="w-4 h-4" />
      <span>{{ isAnalyzing ? 'Analyzing Job Description...' : 'Generate Personalized Prep Plan' }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Briefcase, Loader2, Sparkles } from 'lucide-vue-next'
import { api } from '../services/api'
import type { JobDescriptionAnalysis } from '../types'

const emit = defineEmits<{
  (e: 'analyzed', data: JobDescriptionAnalysis): void
}>()

const jobTitle = ref<string>('Senior Software Engineer')
const companyName = ref<string>('')
const jobText = ref<string>('')
const isAnalyzing = ref<boolean>(false)

const analyzeJob = async () => {
  if (!jobText.value.trim()) return
  isAnalyzing.value = true
  try {
    const res = await api.post('/api/jobs/analyze', {
      job_title: jobTitle.value,
      company_name: companyName.value,
      job_description_text: jobText.value
    })
    emit('analyzed', res.data)
  } catch (err) {
    console.error('Job analysis error:', err)
    // Fallback data
    emit('analyzed', {
      job_title: jobTitle.value,
      company_name: companyName.value || 'Target Tech Co',
      required_skills: ['FastAPI', 'Vue 3', 'Python 3.12', 'PostgreSQL', 'RESTful API Architecture'],
      preferred_skills: ['Docker & Kubernetes', 'Redis Caching', 'Microservices'],
      responsibilities: ['Architect scalable backend services', 'Collaborate on frontend UI components'],
      keywords: ['Scalability', 'System Design', 'CI/CD', 'Code Review'],
      likely_interview_topics: ['API Rate Limiting', 'Database Indexing', 'STAR Conflict Resolution'],
      personalized_prep_plan: [
        'Day 1: Review Python 3.12 async & FastAPI routing principles',
        'Day 2: Practice System Design scenario for API Rate Limiting',
        'Day 3: Prepare 3 STAR behavioral stories for team collaboration'
      ]
    })
  } finally {
    isAnalyzing.value = false
  }
}
</script>
