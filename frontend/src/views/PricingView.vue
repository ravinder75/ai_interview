<template>
  <div class="max-w-7xl mx-auto space-y-10 py-6">
    <!-- Header -->
    <div class="text-center space-y-3 max-w-3xl mx-auto">
      <span class="text-xs px-3.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-bold uppercase tracking-wider">
        SPECIAL OFFER FOR INDIA 🇮🇳
      </span>
      <h1 class="text-3xl sm:text-4xl font-extrabold text-slate-100">
        Invest in Your Career with <span class="text-gradient">Interview Coach AI</span>
      </h1>
      <p class="text-sm text-slate-400">
        Start with a <strong>3-Day Free Trial</strong> — Unlimited AI video mock interviews, STAR framework feedback, coding arena, and instant resume matching.
      </p>

      <!-- Monthly / Yearly Billing Toggle -->
      <div class="pt-4 flex items-center justify-center gap-3">
        <span :class="!isYearly ? 'text-slate-100 font-bold' : 'text-slate-400'" class="text-xs">Monthly Billing</span>
        <button
          @click="isYearly = !isYearly"
          class="w-14 h-7 rounded-full bg-slate-900 border border-slate-700 p-1 relative transition"
        >
          <div
            :class="[
              'w-5 h-5 rounded-full bg-indigo-600 shadow-md transition-all duration-300',
              isYearly ? 'translate-x-7 bg-purple-500' : 'translate-x-0'
            ]"
          ></div>
        </button>
        <span :class="isYearly ? 'text-slate-100 font-bold' : 'text-slate-400'" class="text-xs flex items-center gap-1.5">
          <span>Yearly Billing</span>
          <span class="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-extrabold uppercase">
            Save 30% Extra
          </span>
        </span>
      </div>
    </div>

    <!-- Pricing Cards Grid in INR (₹) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- 3-Day Free Trial Starter -->
      <div
        @click="selectedPlan = 'starter'"
        :class="[
          'glass-card rounded-2xl p-8 border transition cursor-pointer flex flex-col justify-between space-y-6 relative overflow-hidden',
          selectedPlan === 'starter'
            ? 'border-indigo-500 bg-indigo-950/20 shadow-2xl shadow-indigo-600/20 ring-2 ring-indigo-500/50 scale-[1.02]'
            : 'border-slate-800 hover:border-slate-700'
        ]"
      >
        <!-- Active Glow Gradient -->
        <div v-if="selectedPlan === 'starter'" class="absolute -top-24 -left-24 w-48 h-48 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none"></div>

        <div class="space-y-4">
          <div class="space-y-1">
            <span class="px-2.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-[10px] font-bold uppercase">NO CREDIT CARD REQUIRED</span>
            <h3 class="text-lg font-bold text-slate-100 pt-1 flex items-center justify-between">
              <span>3-Day Free Trial</span>
              <span v-if="selectedPlan === 'starter'" class="text-[10px] px-2 py-0.5 rounded bg-indigo-600 text-white font-mono font-bold">SELECTED</span>
            </h3>
            <p class="text-xs text-slate-400">Full platform access for 3 days, absolutely free</p>
          </div>
          <div class="flex items-baseline gap-1">
            <span class="text-4xl font-extrabold text-slate-100 font-mono">₹0</span>
            <span class="text-xs text-slate-400">/ 3 Days Access</span>
          </div>

          <div class="space-y-2.5 pt-4 border-t border-slate-800 text-xs text-slate-300">
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span class="font-bold">3 Days Full Platform Access</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Full AI Video Mock Interview Access</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>STAR Scorecard & Evaluation</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Interview Bit Copilot Assistant</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>1 Resume Analysis Scan</span>
            </div>
          </div>
        </div>

        <router-link to="/register" class="w-full btn-secondary py-3 text-xs font-bold text-center block">
          Start 3-Day Free Trial
        </router-link>
      </div>

      <!-- Pro Coach (POPULAR - ACTIVATED LIGHTING CARD) -->
      <div
        @click="selectedPlan = 'pro'"
        :class="[
          'glass-card rounded-2xl p-8 border-2 transition cursor-pointer flex flex-col justify-between space-y-6 relative overflow-hidden',
          selectedPlan === 'pro'
            ? 'border-indigo-400 bg-gradient-to-b from-indigo-950/40 via-slate-900/80 to-purple-950/40 shadow-2xl shadow-indigo-500/30 ring-2 ring-indigo-400/80 scale-[1.03]'
            : 'border-indigo-500/50 hover:border-indigo-500'
        ]"
      >
        <!-- Lightning Glow Animations -->
        <div class="absolute -top-16 -right-16 w-40 h-40 bg-purple-500/30 rounded-full blur-3xl pointer-events-none animate-pulse"></div>
        <div class="absolute -bottom-16 -left-16 w-40 h-40 bg-indigo-500/30 rounded-full blur-3xl pointer-events-none animate-pulse"></div>

        <div class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 text-white text-[10px] font-extrabold uppercase tracking-wider shadow-lg shadow-indigo-500/40 flex items-center gap-1">
          <Zap class="w-3 h-3 text-amber-300 fill-amber-300 animate-bounce" />
          <span>BEST VALUE • RECOMMENDED</span>
        </div>

        <div class="space-y-4 pt-2">
          <div class="space-y-1">
            <h3 class="text-lg font-bold text-slate-100 flex items-center justify-between">
              <span class="flex items-center gap-2">
                <span>Pro Coach</span>
                <Zap class="w-4 h-4 text-amber-400 fill-amber-400 animate-pulse" />
              </span>
              <span v-if="selectedPlan === 'pro'" class="text-[10px] px-2.5 py-0.5 rounded-full bg-indigo-500 text-white font-mono font-extrabold shadow-md">
                ACTIVE PLAN
              </span>
            </h3>
            <p class="text-xs text-slate-400">Complete AI interview coaching suite for job seekers</p>
          </div>

          <div class="space-y-1 bg-slate-900/90 p-4 rounded-xl border border-indigo-500/40 shadow-inner">
            <div class="flex items-baseline gap-1">
              <span class="text-4xl font-extrabold text-slate-100 font-mono text-gradient">
                ₹{{ isYearly ? '9,588' : '1,199' }}
              </span>
              <span class="text-xs text-slate-400 font-bold">/ {{ isYearly ? 'year' : 'month' }}</span>
            </div>

            <!-- Detailed Breakdown -->
            <p v-if="isYearly" class="text-[11px] text-emerald-400 font-semibold font-mono pt-1 flex items-center gap-1">
              <span>⚡ Equivalent to ₹799/month (Save ₹4,800/yr)</span>
            </p>
            <p v-else class="text-[11px] text-slate-400 font-mono pt-1">
              Billed monthly
            </p>
          </div>

          <div class="space-y-2.5 pt-4 border-t border-slate-800 text-xs text-slate-200">
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span class="font-bold">Includes 3-Day Free Trial</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span class="font-bold">Unlimited AI Video Mock Interviews</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Live AI Voice & Speech Recognition</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Full STAR Scorecard & Evaluation</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span class="font-bold">Interview Bit Practice Copilot</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Interactive Coding Arena & Test Execution</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Unlimited Resume & Job Analyzer Scans</span>
            </div>
          </div>
        </div>

        <router-link to="/register" class="w-full btn-primary py-3.5 text-xs font-bold text-center block shadow-xl shadow-indigo-600/40 transform hover:-translate-y-0.5 transition">
          ⚡ Start Pro 3-Day Trial
        </router-link>
      </div>

      <!-- Enterprise Prep -->
      <div
        @click="selectedPlan = 'enterprise'"
        :class="[
          'glass-card rounded-2xl p-8 border transition cursor-pointer flex flex-col justify-between space-y-6 relative overflow-hidden',
          selectedPlan === 'enterprise'
            ? 'border-purple-500 bg-purple-950/20 shadow-2xl shadow-purple-600/20 ring-2 ring-purple-500/50 scale-[1.02]'
            : 'border-slate-800 hover:border-slate-700'
        ]"
      >
        <div class="space-y-4">
          <div class="space-y-1">
            <h3 class="text-lg font-bold text-slate-100 flex items-center justify-between">
              <span>Enterprise Prep</span>
              <span v-if="selectedPlan === 'enterprise'" class="text-[10px] px-2 py-0.5 rounded bg-purple-600 text-white font-mono font-bold">SELECTED</span>
            </h3>
            <p class="text-xs text-slate-400">Advanced coaching for senior engineers & teams</p>
          </div>

          <div class="space-y-1 bg-slate-900/80 p-4 rounded-xl border border-slate-800">
            <div class="flex items-baseline gap-1">
              <span class="text-4xl font-extrabold text-slate-100 font-mono">
                ₹{{ isYearly ? '29,988' : '3,499' }}
              </span>
              <span class="text-xs text-slate-400 font-bold">/ {{ isYearly ? 'year' : 'month' }}</span>
            </div>

            <!-- Detailed Breakdown -->
            <p v-if="isYearly" class="text-[11px] text-emerald-400 font-semibold font-mono pt-1">
              ✓ Equivalent to ₹2,499/month (Save ₹12,000/yr)
            </p>
            <p v-else class="text-[11px] text-slate-400 font-mono pt-1">
              Billed monthly
            </p>
          </div>

          <div class="space-y-2.5 pt-4 border-t border-slate-800 text-xs text-slate-300">
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span class="font-bold">Everything in Pro Coach</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Priority AI Response Speed</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Custom Interviewer Persona & Voice</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Downloadable PDF Performance Reports</span>
            </div>
            <div class="flex items-center gap-2">
              <Check class="w-4 h-4 text-emerald-400 shrink-0" />
              <span>1-on-1 Prep Strategy Review</span>
            </div>
          </div>
        </div>

        <button @click="contactSales" class="w-full btn-secondary py-3 text-xs font-bold text-center block">
          Contact Sales
        </button>
      </div>
    </div>

    <!-- FAQ Section -->
    <div class="max-w-3xl mx-auto space-y-6 pt-8">
      <h2 class="text-xl font-bold text-slate-100 text-center">Frequently Asked Questions</h2>

      <div class="space-y-3">
        <div v-for="(faq, idx) in faqs" :key="idx" class="glass-card rounded-xl p-4 border border-slate-800 space-y-2">
          <h4 class="font-bold text-slate-200 text-xs flex items-center justify-between cursor-pointer" @click="faq.open = !faq.open">
            <span>{{ faq.q }}</span>
            <span class="text-indigo-400 text-sm">{{ faq.open ? '−' : '+' }}</span>
          </h4>
          <p v-if="faq.open" class="text-xs text-slate-400 leading-relaxed pt-1 border-t border-slate-800/60">
            {{ faq.a }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Check, Zap } from 'lucide-vue-next'

const isYearly = ref(true)
const selectedPlan = ref('pro')

const faqs = ref([
  {
    q: "How does the 3-Day Free Trial work?",
    a: "You get 3 full days of access with 0 charge and no credit card required upon registration. Test out AI Video Mock Interviews, STAR feedback, and Interview Bit Copilot.",
    open: true
  },
  {
    q: "How much do I save with yearly billing?",
    a: "With yearly billing on the Pro Coach plan, you pay ₹9,588/year (equivalent to ₹799/month), saving ₹4,800 every year compared to paying monthly at ₹1,199/month.",
    open: false
  },
  {
    q: "Are payment methods like UPI, Paytm, and Net Banking supported in India?",
    a: "Yes! Payments can be processed seamlessly via UPI, credit/debit cards, Paytm, and Net Banking.",
    open: false
  },
  {
    q: "Can I cancel my subscription at any time?",
    a: "Yes! You can upgrade, downgrade, or cancel your plan at any time directly from your settings panel without hidden fees.",
    open: false
  }
])

const contactSales = () => {
  alert('Enterprise sales request submitted! Our team will reach out to your registered email.')
}
</script>
