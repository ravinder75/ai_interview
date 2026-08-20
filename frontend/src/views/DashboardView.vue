<template>
  <div class="max-w-7xl mx-auto space-y-10 py-4 px-2">
    
    <!-- 3D Animated Hero Banner -->
    <div class="glass-card rounded-3xl p-8 sm:p-10 border border-indigo-500/20 relative overflow-hidden bg-gradient-to-r from-slate-950 via-indigo-950/40 to-slate-950 shadow-2xl space-y-6">
      
      <!-- Ambient Glow Blobs & Animated Particles -->
      <div class="absolute -top-24 -left-24 w-80 h-80 bg-indigo-600/30 rounded-full blur-3xl pointer-events-none animate-pulse-glow"></div>
      <div class="absolute -bottom-24 -right-24 w-80 h-80 bg-purple-600/30 rounded-full blur-3xl pointer-events-none animate-pulse-glow"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
        
        <!-- Left Hero Text Content -->
        <div class="lg:col-span-8 space-y-5">
          <div class="inline-flex items-center space-x-2.5 px-4 py-1.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-xs font-semibold backdrop-blur-md shadow-lg">
            <Sparkles class="w-4 h-4 text-indigo-400 animate-spin" />
            <span>AI-POWERED INTERVIEW COACHING PLATFORM</span>
          </div>

          <h1 class="text-3xl sm:text-5xl lg:text-6xl font-black text-slate-100 tracking-tight leading-none">
            Master Technical & <br class="hidden sm:block" />
            <span class="text-gradient">Behavioral Interviews</span>
          </h1>

          <p class="text-slate-300 text-sm sm:text-base max-w-2xl leading-relaxed">
            Experience real-time 3D voice AI mock interviews, practice STAR framework answers, scan resumes with 100% ATS score calculation, and get personalized career guidance.
          </p>

          <!-- Interactive Readiness Score Widget -->
          <div class="pt-3 max-w-xl space-y-2.5">
            <div class="flex justify-between items-center text-xs sm:text-sm font-bold text-slate-200">
              <span class="flex items-center gap-2">
                <Trophy class="w-4 h-4 text-amber-400" />
                Interview Readiness Score
              </span>
              <span class="text-indigo-400 font-extrabold font-mono text-base bg-indigo-500/10 px-3 py-1 rounded-lg border border-indigo-500/20">88% (Advanced Ready)</span>
            </div>
            <div class="w-full bg-slate-950/80 rounded-full h-4 p-0.5 overflow-hidden border border-indigo-500/30 shadow-inner">
              <div class="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 h-full rounded-full transition-all duration-1000 shadow-lg shadow-indigo-500/50" style="width: 88%"></div>
            </div>
          </div>
        </div>

        <!-- Right 3D Floating Avatar Orb Card -->
        <div class="lg:col-span-4 flex justify-center perspective-1000">
          <div class="relative group preserve-3d animate-float-3d">
            
            <!-- Outer Glowing Aura Ring -->
            <div class="absolute -inset-1.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-3xl blur-lg opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200 animate-pulse"></div>

            <div class="w-56 h-56 sm:w-64 sm:h-64 rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-950 p-1 shadow-2xl relative z-10 border border-indigo-500/40">
              <div class="w-full h-full bg-slate-950/90 rounded-[22px] p-6 flex flex-col items-center justify-center text-center space-y-4 relative overflow-hidden backdrop-blur-xl">
                
                <div class="relative">
                  <div class="w-24 h-24 rounded-full bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center text-white shadow-2xl animate-pulse">
                    <Bot class="w-12 h-12 text-white drop-shadow-md" />
                  </div>
                  <span class="absolute bottom-0 right-0 w-5 h-5 bg-emerald-400 border-2 border-slate-950 rounded-full animate-ping"></span>
                  <span class="absolute bottom-0 right-0 w-5 h-5 bg-emerald-400 border-2 border-slate-950 rounded-full"></span>
                </div>

                <div>
                  <h4 class="text-sm font-black text-slate-100 tracking-wide">SOPHIA AI INTERPRETER</h4>
                  <span class="text-[11px] text-emerald-400 font-mono font-bold block mt-0.5">● Voice & Vision Online</span>
                </div>

                <div class="px-3.5 py-1 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-[10px] font-mono font-bold tracking-wider uppercase">
                  3D Audio STT Engine Active
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- Quick Action Launchpad Cards (4 Columns with 3D Tilt Hover) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      
      <router-link to="/mock-interview" class="glass-card glass-card-hover rounded-2xl p-6 border border-indigo-500/20 space-y-4 group relative overflow-hidden">
        <div class="w-14 h-14 rounded-2xl bg-indigo-500/15 text-indigo-400 flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-xl border border-indigo-500/30">
          <Video class="w-7 h-7" />
        </div>
        <div class="space-y-1">
          <h3 class="font-extrabold text-slate-100 text-lg group-hover:text-indigo-300 transition-colors">Start Mock Interview</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Simulate 5 real-time voice questions with live speech evaluation & video webcam feed.</p>
        </div>
        <div class="pt-2 text-xs text-indigo-400 font-bold flex items-center gap-1.5 group-hover:translate-x-2 transition-transform">
          <span>Launch AI Session</span>
          <ArrowRight class="w-4 h-4" />
        </div>
      </router-link>

      <router-link to="/practice" class="glass-card glass-card-hover rounded-2xl p-6 border border-purple-500/20 space-y-4 group relative overflow-hidden">
        <div class="w-14 h-14 rounded-2xl bg-purple-500/15 text-purple-400 flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-xl border border-purple-500/30">
          <PlayCircle class="w-7 h-7" />
        </div>
        <div class="space-y-1">
          <h3 class="font-extrabold text-slate-100 text-lg group-hover:text-purple-300 transition-colors">Practice Questions</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Explore 100+ role questions categorized by STAR behavioral, technical, and HR frameworks.</p>
        </div>
        <div class="pt-2 text-xs text-purple-400 font-bold flex items-center gap-1.5 group-hover:translate-x-2 transition-transform">
          <span>Explore Bank</span>
          <ArrowRight class="w-4 h-4" />
        </div>
      </router-link>

      <router-link to="/resume" class="glass-card glass-card-hover rounded-2xl p-6 border border-emerald-500/20 space-y-4 group relative overflow-hidden">
        <div class="w-14 h-14 rounded-2xl bg-emerald-500/15 text-emerald-400 flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-xl border border-emerald-500/30">
          <FileText class="w-7 h-7" />
        </div>
        <div class="space-y-1">
          <h3 class="font-extrabold text-slate-100 text-lg group-hover:text-emerald-300 transition-colors">AI ATS Resume Builder</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Instant ATS error scanner, 100% score calculation, 8 templates & PDF/DOCX exporter.</p>
        </div>
        <div class="pt-2 text-xs text-emerald-400 font-bold flex items-center gap-1.5 group-hover:translate-x-2 transition-transform">
          <span>Analyze & Build</span>
          <ArrowRight class="w-4 h-4" />
        </div>
      </router-link>

      <router-link to="/job-analysis" class="glass-card glass-card-hover rounded-2xl p-6 border border-cyan-500/20 space-y-4 group relative overflow-hidden">
        <div class="w-14 h-14 rounded-2xl bg-cyan-500/15 text-cyan-400 flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-xl border border-cyan-500/30">
          <Briefcase class="w-7 h-7" />
        </div>
        <div class="space-y-1">
          <h3 class="font-extrabold text-slate-100 text-lg group-hover:text-cyan-300 transition-colors">Job Match Analysis</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Match your resume against job postings to extract missing skills and 3-day action plans.</p>
        </div>
        <div class="pt-2 text-xs text-cyan-400 font-bold flex items-center gap-1.5 group-hover:translate-x-2 transition-transform">
          <span>Analyze Posting</span>
          <ArrowRight class="w-4 h-4" />
        </div>
      </router-link>

    </div>

    <!-- Recent Sessions Overview & Live Metrics -->
    <div class="glass-card rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-6">
      <div class="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <h3 class="text-xl font-black text-slate-100 flex items-center gap-2.5">
          <History class="w-6 h-6 text-indigo-400" />
          <span>Recent Session Ratings & Evaluation History</span>
        </h3>
        <router-link to="/history" class="text-xs text-indigo-400 font-bold hover:underline flex items-center gap-1">
          <span>View All History</span>
          <ArrowRight class="w-3.5 h-3.5" />
        </router-link>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-slate-950/70 p-5 rounded-2xl border border-slate-800/80 flex items-center justify-between hover:border-indigo-500/30 transition-colors">
          <div class="flex items-center gap-4">
            <span class="w-3.5 h-3.5 rounded-full bg-emerald-400 animate-pulse shadow-lg shadow-emerald-400/50"></span>
            <div>
              <strong class="text-slate-100 text-sm font-bold block">Backend Microservices & Distributed Systems</strong>
              <span class="text-slate-400 text-xs">Software Engineer • Aug 15</span>
            </div>
          </div>
          <div class="text-right">
            <span class="text-2xl font-black text-emerald-400 font-mono">92%</span>
            <span class="text-slate-500 text-[10px] block font-bold uppercase">Readiness</span>
          </div>
        </div>

        <div class="bg-slate-950/70 p-5 rounded-2xl border border-slate-800/80 flex items-center justify-between hover:border-indigo-500/30 transition-colors">
          <div class="flex items-center gap-4">
            <span class="w-3.5 h-3.5 rounded-full bg-indigo-500 shadow-lg shadow-indigo-500/50"></span>
            <div>
              <strong class="text-slate-100 text-sm font-bold block">System Architecture & REST API Design</strong>
              <span class="text-slate-400 text-xs">Senior Full-Stack Engineer • Aug 14</span>
            </div>
          </div>
          <div class="text-right">
            <span class="text-2xl font-black text-indigo-400 font-mono">85%</span>
            <span class="text-slate-500 text-[10px] block font-bold uppercase">Readiness</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { Sparkles, Video, PlayCircle, FileText, Briefcase, History, Bot, Trophy, ArrowRight } from 'lucide-vue-next'
</script>

