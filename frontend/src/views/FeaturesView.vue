<template>
  <div class="max-w-7xl mx-auto space-y-12 py-6">
    <!-- Hero Header -->
    <div class="text-center space-y-3 max-w-3xl mx-auto">
      <span class="text-xs px-3.5 py-1 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 font-bold uppercase tracking-wider">
        PLATFORM CAPABILITIES
      </span>
      <h1 class="text-3xl sm:text-4xl font-extrabold text-slate-100">
        Everything You Need to Ace <span class="text-gradient">Tech & Behavioral Interviews</span>
      </h1>
      <p class="text-sm text-slate-400">
        Explore the end-to-end suite of AI-powered tools designed to turn technical preparation into confident offer letters.
      </p>
    </div>

    <!-- Feature Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <div v-for="feat in features" :key="feat.title" class="glass-card rounded-2xl p-6 border border-slate-800 space-y-4 hover:border-indigo-500/50 transition">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-600/20 to-purple-600/20 text-indigo-400 border border-indigo-500/20 flex items-center justify-center font-bold">
          <component :is="feat.icon" class="w-6 h-6" />
        </div>
        <div class="space-y-1.5">
          <h3 class="text-base font-bold text-slate-100">{{ feat.title }}</h3>
          <p class="text-xs text-slate-400 leading-relaxed">{{ feat.description }}</p>
        </div>
        <div class="pt-2 border-t border-slate-800/60">
          <span class="text-[11px] font-semibold text-indigo-400 font-mono flex items-center gap-1">
            <span>{{ feat.badge }}</span> →
          </span>
        </div>
      </div>
    </div>

    <!-- Interactive Callout -->
    <div class="glass-card rounded-2xl p-8 border border-indigo-500/30 bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-purple-950/40 flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl">
      <div class="space-y-2 max-w-xl">
        <h3 class="text-xl font-bold text-slate-100">Ready to start practicing with AI?</h3>
        <p class="text-xs text-slate-400">Create your account in seconds and schedule your first interactive mock interview.</p>
      </div>
      <router-link to="/register" class="btn-primary px-6 py-3 text-xs font-bold shrink-0 shadow-lg shadow-indigo-600/30">
        Start Free Practice Now
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Video, Sparkles, Award, Code2, FileSearch, ShieldCheck } from 'lucide-vue-next'

const features = [
  {
    icon: Video,
    title: "AI Video Mock Interview",
    description: "Live camera feed, browser speech synthesis voice, real-time speech-to-text recognition, and countdown session timer.",
    badge: "Interactive Video Room"
  },
  {
    icon: Sparkles,
    title: "Interview Bit Practice Copilot",
    description: "On-the-fly preparation coach panel providing code snippets, complexity analysis, and STAR structured answers.",
    badge: "Real-time AI Guidance"
  },
  {
    icon: Award,
    title: "STAR Framework Evaluator",
    description: "Instant rubric evaluation measuring Situation, Task, Action, Result along with technical accuracy and clarity scores.",
    badge: "Automated Feedback"
  },
  {
    icon: Code2,
    title: "Coding Interview Arena",
    description: "Integrated code editor with instant test execution for Data Structures, Algorithms, and System Design problems.",
    badge: "Multi-Language Execution"
  },
  {
    icon: FileSearch,
    title: "Resume & Job Analyzer",
    description: "Upload candidate resumes or paste job descriptions to extract missing skills, key projects, and likely interview questions.",
    badge: "Tailored Context"
  },
  {
    icon: ShieldCheck,
    title: "Secure Authentication",
    description: "Argon2id password hashing, JWT session security, and Google OAuth 2.0 / OpenID Connect integration.",
    badge: "Production Security"
  }
]
</script>
