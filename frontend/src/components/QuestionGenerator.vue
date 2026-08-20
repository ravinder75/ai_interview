<template>
  <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-lg font-bold text-slate-100 flex items-center gap-2">
          <HelpCircle class="w-5 h-5 text-cyan-400" />
          AI Question Set Generator
        </h3>
        <p class="text-xs text-slate-400">Generate targeted practice questions filtered by role, type, and difficulty</p>
      </div>
      <span class="text-xs px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-semibold">Config</span>
    </div>

    <!-- Controls Form -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Target Role / Branch</label>
        <select v-model="role" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 outline-none focus:border-cyan-500 font-mono">
          <optgroup label="IT & Computer Science">
            <option value="Software Engineer">Software Engineer</option>
            <option value="Frontend Developer">Frontend Developer</option>
            <option value="Backend Developer">Backend Developer</option>
            <option value="Full-Stack Developer">Full-Stack Developer</option>
            <option value="Data Scientist">Data Scientist</option>
            <option value="AI/ML Engineer">AI/ML Engineer</option>
            <option value="DevOps Engineer">DevOps Engineer</option>
            <option value="Cybersecurity Engineer">Cybersecurity Engineer</option>
            <option value="QA / Test Engineer">QA / Test Engineer</option>
          </optgroup>
          <optgroup label="Medical & Healthcare">
            <option value="Medical Coding Specialist">Medical Coding Specialist</option>
            <option value="Certified Professional Coder (CPC)">Certified Professional Coder (CPC)</option>
            <option value="Medical Billing & Coding">Medical Billing & Coding</option>
            <option value="Medical Officer / Doctor">Medical Officer / Doctor</option>
            <option value="Registered Nurse">Registered Nurse</option>
          </optgroup>
          <optgroup label="Core Engineering Branches">
            <option value="Mechanical Engineer">Mechanical Engineer</option>
            <option value="Electrical Engineer">Electrical Engineer</option>
            <option value="Civil Engineer">Civil Engineer</option>
            <option value="Chemical Engineer">Chemical Engineer</option>
          </optgroup>
          <optgroup label="Business, Finance & Management">
            <option value="Financial Analyst">Financial Analyst</option>
            <option value="Chartered Accountant (CA)">Chartered Accountant (CA)</option>
            <option value="Human Resources (HR)">Human Resources (HR)</option>
            <option value="Marketing Executive / Manager">Marketing Executive / Manager</option>
            <option value="Product Manager">Product Manager</option>
            <option value="Business Analyst">Business Analyst</option>
          </optgroup>
        </select>
      </div>

      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Experience Level</label>
        <select v-model="experience" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 outline-none">
          <option value="Fresher / College Graduate">Fresher / Graduate (0-1 Year)</option>
          <option value="Junior Level (1-2 years)">Junior Level (1-2 Years)</option>
          <option value="Mid-Level (3-4 years)">Mid-Level (3-4 Years)</option>
          <option value="Senior Level (5+ years)">Senior Level (5+ Years)</option>
          <option value="Lead / Specialist (8+ years)">Lead / Specialist (8+ Years)</option>
        </select>
      </div>

      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Interview Type</label>
        <select v-model="interviewType" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 outline-none focus:border-cyan-500 font-mono">
          <option value="technical">Technical Deep-Dive</option>
          <option value="coding">Coding & Data Structures</option>
          <option value="system_design">System Design & Architecture</option>
          <option value="behavioral">Behavioral & STAR</option>
          <option value="medical_coding">Medical Coding & Guidelines</option>
          <option value="clinical">Clinical Documentation</option>
          <option value="full_mock">Full End-to-End Mock Interview</option>
        </select>
      </div>

      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Difficulty</label>
        <select v-model="difficulty" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 outline-none">
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
          <option value="expert">Expert</option>
        </select>
      </div>

      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Timer Limit per Question</label>
        <select v-model="timerLimit" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 outline-none font-mono">
          <option :value="2">⏱️ 2 Minutes (Speed Round)</option>
          <option :value="5">⏱️ 5 Minutes (Standard)</option>
          <option :value="10">⏱️ 10 Minutes (Deep Problem)</option>
          <option :value="0">⏳ No Time Limit</option>
        </select>
      </div>

      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Question Count</label>
        <input
          v-model.number="count"
          type="number"
          min="1"
          max="10"
          class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 outline-none"
        />
      </div>
    </div>

    <button
      @click="generate"
      :disabled="isGenerating"
      class="w-full btn-primary py-3 flex items-center justify-center gap-2 font-bold"
    >
      <Loader2 v-if="isGenerating" class="w-4 h-4 animate-spin" />
      <Sparkles v-else class="w-4 h-4" />
      <span>{{ isGenerating ? 'Generating AI Questions...' : 'Generate Practice Questions' }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { HelpCircle, Loader2, Sparkles } from 'lucide-vue-next'
import { api } from '../services/api'
import type { Question } from '../types'

const emit = defineEmits<{
  (e: 'generated', questions: Question[]): void
}>()

const role = ref<string>('CS Fundamentals (OS, DBMS, CN)')
const experience = ref<string>('Fresher / College Graduate')
const interviewType = ref<string>('cs_theory')
const difficulty = ref<string>('medium')
const timerLimit = ref<number>(5)
const count = ref<number>(5)
const isGenerating = ref<boolean>(false)

const generate = async () => {
  isGenerating.value = true
  try {
    const res = await api.post('/api/questions/generate', {
      role: role.value,
      experience: experience.value,
      industry: 'Technology',
      interview_type: interviewType.value,
      difficulty: difficulty.value,
      count: count.value,
      seed: Math.floor(Math.random() * 1000000)
    })
    const questionsData = res.data.map((q: any) => ({
      ...q,
      options: q.options || [
        `Optimal approach utilizing ${q.key_aspects?.[0] || 'core concepts'}`,
        `Alternative solution focusing on ${q.key_aspects?.[1] || 'scalability'}`,
        'Basic implementation without optimization',
        'None of the above'
      ]
    }))
    emit('generated', questionsData)
  } catch (err) {
    console.error('Error generating questions:', err)
    // Fallback questions with multiple-choice options
    emit('generated', [
      {
        question_order: 1,
        category: 'CS Fundamentals',
        question_text: 'Which process scheduling algorithm guarantees minimum average waiting time for a given set of processes?',
        key_aspects: ['CPU Scheduling', 'Shortest Job First', 'Preemptive vs Non-preemptive'],
        options: [
          'First-Come, First-Served (FCFS)',
          'Shortest Job First (SJF / SRTF)',
          'Round Robin (RR)',
          'Priority Scheduling'
        ],
        correct_option: 'Shortest Job First (SJF / SRTF)'
      },
      {
        question_order: 2,
        category: 'Data Structures & Algorithms',
        question_text: 'What is the worst-case time complexity of QuickSort when bad pivot selection occurs?',
        key_aspects: ['QuickSort', 'Time Complexity', 'Pivot Selection'],
        options: [
          'O(N log N)',
          'O(N)',
          'O(N^2)',
          'O(log N)'
        ],
        correct_option: 'O(N^2)'
      },
      {
        question_order: 3,
        category: 'System Design & DBMS',
        question_text: 'Which ACID property guarantees that database transactions are executed in isolation without interference?',
        key_aspects: ['ACID Properties', 'Isolation Levels', 'Concurrency Control'],
        options: [
          'Atomicity',
          'Consistency',
          'Isolation',
          'Durability'
        ],
        correct_option: 'Isolation'
      }
    ])
  } finally {
    isGenerating.value = false
  }
}
</script>
