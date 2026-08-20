<template>
  <div class="max-w-7xl mx-auto space-y-12 py-6 px-2 sm:px-4">
    
    <!-- Hero Section with 3D Visual Floating Card -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center glass-card rounded-3xl p-8 border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-purple-950/40 shadow-2xl relative overflow-hidden">
      
      <!-- Ambient Glow Blobs -->
      <div class="absolute -top-24 -left-24 w-72 h-72 bg-purple-600/20 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-24 -right-24 w-72 h-72 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Left Text -->
      <div class="lg:col-span-7 space-y-4 relative z-10">
        <span class="text-xs px-3.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold uppercase tracking-wider font-mono">
          ABOUT INTERVIEW COACH AI
        </span>
        
        <h1 class="text-3xl sm:text-4xl md:text-5xl font-black text-slate-100 leading-tight">
          Empowering Candidates to Build Confidence & <span class="text-gradient">Ace Every Interview</span>
        </h1>

        <p class="text-sm text-slate-300 leading-relaxed">
          We bridge the gap between technical knowledge and real-time interview performance through AI video mock interviews, instant speech analysis, and 100% ATS-optimized resume intelligence.
        </p>

        <div class="flex items-center gap-3 pt-2 text-xs font-bold">
          <router-link to="/mock-interview" class="btn-primary py-2.5 px-5 flex items-center gap-2 shadow-lg shadow-indigo-600/30">
            <Sparkles class="w-4 h-4" />
            <span>Try AI Mock Interview</span>
          </router-link>
          
          <router-link to="/resume" class="btn-secondary py-2.5 px-5 text-indigo-300 border-indigo-500/30">
            <span>Scan Resume</span>
          </router-link>
        </div>
      </div>

      <!-- Right 3D Visual Floating Card -->
      <div class="lg:col-span-5 flex justify-center relative z-10">
        <div class="w-full max-w-sm p-1 rounded-3xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-emerald-400 shadow-2xl animate-pulse">
          <div class="bg-slate-950 p-6 rounded-[22px] text-center space-y-4 border border-slate-800">
            
            <div class="w-24 h-24 rounded-3xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white mx-auto shadow-2xl text-4xl animate-bounce">
              <Bot class="w-12 h-12" />
            </div>

            <div>
              <h3 class="font-bold text-slate-100 text-lg">Realtime Interview Engine</h3>
              <p class="text-xs text-indigo-300 font-mono mt-0.5">Asynchronous AI Evaluation & Voice Synthesis</p>
            </div>

            <div class="grid grid-cols-2 gap-2 text-[11px] font-mono">
              <div class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-emerald-400 font-bold">
                100% ATS Ready
              </div>
              <div class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-purple-300 font-bold">
                &lt; 1s Latency
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Banner -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="glass-card rounded-2xl p-6 border border-slate-800 text-center space-y-1 hover:border-indigo-500 transition">
        <span class="text-3xl font-extrabold text-indigo-400 font-mono">50,000+</span>
        <span class="text-xs text-slate-400 block font-medium">Mock Interviews Conducted</span>
      </div>
      <div class="glass-card rounded-2xl p-6 border border-slate-800 text-center space-y-1 hover:border-purple-500 transition">
        <span class="text-3xl font-extrabold text-purple-400 font-mono">94%</span>
        <span class="text-xs text-slate-400 block font-medium">Candidate Confidence Boost</span>
      </div>
      <div class="glass-card rounded-2xl p-6 border border-slate-800 text-center space-y-1 hover:border-emerald-500 transition">
        <span class="text-3xl font-extrabold text-emerald-400 font-mono">30+</span>
        <span class="text-xs text-slate-400 block font-medium">Tech Roles Supported</span>
      </div>
      <div class="glass-card rounded-2xl p-6 border border-slate-800 text-center space-y-1 hover:border-amber-500 transition">
        <span class="text-3xl font-extrabold text-amber-400 font-mono">&lt; 1s</span>
        <span class="text-xs text-slate-400 block font-medium">AI Feedback Latency</span>
      </div>
    </div>

    <!-- Technology Stack Section -->
    <div class="glass-card rounded-2xl p-8 border border-slate-800 space-y-6">
      <div class="text-center space-y-2">
        <h2 class="text-xl font-bold text-slate-100 flex items-center justify-center gap-2">
          <Cpu class="w-6 h-6 text-indigo-400" />
          <span>Modern Engineering & Architecture</span>
        </h2>
        <p class="text-xs text-slate-400 max-w-xl mx-auto">
          Built with FastAPI, Vue 3, TypeScript, Argon2 password security, OpenID Connect, and real-time Speech AI engines.
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
        <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1 hover:border-indigo-500/50 transition">
          <span class="font-bold text-slate-200 block">FastAPI & Python</span>
          <span class="text-slate-400 text-[11px]">Asynchronous backend API engine delivering instant evaluation pipelines.</span>
        </div>

        <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1 hover:border-purple-500/50 transition">
          <span class="font-bold text-slate-200 block">Vue 3 & TypeScript</span>
          <span class="text-slate-400 text-[11px]">Reactive glassmorphic single-page frontend application architecture.</span>
        </div>

        <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1 hover:border-emerald-500/50 transition">
          <span class="font-bold text-slate-200 block">Argon2id Security</span>
          <span class="text-slate-400 text-[11px]">Password hashing and JWT access tokens for user data privacy.</span>
        </div>

        <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1 hover:border-cyan-500/50 transition">
          <span class="font-bold text-slate-200 block">Google OpenID Connect</span>
          <span class="text-slate-400 text-[11px]">OAuth 2.0 single sign-on authentication flow.</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sparkles, Bot, Cpu } from 'lucide-vue-next'
</script>
