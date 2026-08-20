<template>
  <div class="max-w-7xl mx-auto space-y-6 py-4 px-2 sm:px-4 font-sans">
    
    <!-- Top Header Banner -->
    <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-4 bg-slate-950">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span class="text-[10px] text-indigo-400 font-extrabold uppercase tracking-widest font-mono bg-indigo-500/10 px-2.5 py-0.5 rounded border border-indigo-500/20">
            RESUME-MATCHED JOB DISCOVERY & LIVE OPPORTUNITIES
          </span>
          <h1 class="text-2xl font-extrabold text-slate-100 mt-1 flex items-center gap-2">
            <Briefcase class="w-7 h-7 text-indigo-400" />
            <span>REAL-TIME VERIFIED JOB OPPORTUNITIES</span>
          </h1>
          <p class="text-xs text-slate-400 mt-1">
            Verified opportunities from Greenhouse, Lever, Ashby, Adzuna & Direct Careers posted within the last 14 days.
          </p>
        </div>

        <div class="flex items-center gap-2 flex-wrap">
          <button
            @click="showMobileFilters = true"
            class="md:hidden btn-secondary py-2 px-3 text-xs font-bold flex items-center gap-1.5"
          >
            <SlidersHorizontal class="w-4 h-4 text-indigo-400" />
            <span>Filters</span>
          </button>

          <button
            @click="loadJobs"
            :disabled="isLoading"
            class="btn-primary py-2 px-4 text-xs font-bold flex items-center gap-1.5 shadow-md shadow-indigo-600/30"
          >
            <RefreshCw :class="['w-4 h-4', isLoading ? 'animate-spin' : '']" />
            <span>Refresh Jobs</span>
          </button>
        </div>
      </div>

      <!-- Candidate Extracted Profile Info Bar (If Resume Present) -->
      <div v-if="candidateProfile" class="p-3.5 rounded-xl bg-indigo-950/40 border border-indigo-500/30 space-y-2 text-xs">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <span class="text-[11px] font-bold text-indigo-300 flex items-center gap-1.5">
            <UserCheck class="w-4 h-4 text-indigo-400" />
            <span>Extracted Resume Profile: <strong>{{ candidateProfile.name }}</strong> ({{ candidateProfile.target_role }})</span>
          </span>
          <span class="text-[10px] text-slate-400 font-mono">Experience: {{ candidateProfile.experience_level || 'Fresher' }}</span>
        </div>
        <div v-if="candidateProfile.skills && candidateProfile.skills.length" class="flex flex-wrap items-center gap-1">
          <span class="text-[10px] text-slate-400 font-bold uppercase mr-1">Matched Skills:</span>
          <span v-for="sk in candidateProfile.skills.slice(0, 8)" :key="sk" class="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-200 border border-indigo-500/30 text-[10px] font-mono font-bold">
            {{ sk }}
          </span>
        </div>
      </div>

      <!-- Provider Status & Sync Timestamp Bar -->
      <div class="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
        <div class="flex items-center gap-2 flex-wrap">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Live Providers:</span>
          <span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[10px] font-mono font-bold">🟢 Greenhouse</span>
          <span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[10px] font-mono font-bold">🟢 Lever</span>
          <span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[10px] font-mono font-bold">🟢 Ashby</span>
          <span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[10px] font-mono font-bold">🟢 Adzuna</span>
          <span class="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 text-[10px] font-mono font-bold">🏢 Direct Careers</span>
        </div>

        <div class="flex items-center gap-2 text-[11px]">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="text-slate-300 font-mono">Last updated: <strong>{{ formatDate(lastSyncedAt) }}</strong></span>
        </div>
      </div>
    </div>

    <!-- GLOBAL FILTER BAR (Desktop) -->
    <div class="glass-card rounded-2xl p-5 border border-slate-800 space-y-4 bg-slate-950">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 text-xs">
        
        <!-- Search Input -->
        <div class="lg:col-span-2 space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Search Keywords</label>
          <div class="relative">
            <Search class="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              v-model="filters.q"
              @keyup.enter="applyFilters"
              type="text"
              placeholder="Title, Company, Skill..."
              class="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none"
            />
          </div>
        </div>

        <!-- Date Filter (Posted) -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Posted Date</label>
          <select v-model="filters.postedWithin" @change="applyFilters" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none font-mono text-[11px]">
            <option :value="14">Last 14 Days (Default)</option>
            <option :value="1">Posted Today (24h)</option>
            <option :value="3">Last 3 Days</option>
            <option :value="7">Last 7 Days</option>
          </select>
        </div>

        <!-- Job Type (Multi-select) -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Job Type</label>
          <select v-model="filters.jobType" @change="applyFilters" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none">
            <option value="All">All Job Types</option>
            <option value="FULL_TIME">Full-time</option>
            <option value="INTERNSHIP">Internships</option>
            <option value="FRESHER">Fresher / Entry</option>
            <option value="FREELANCE">Freelance</option>
            <option value="CONTRACT">Contract</option>
            <option value="PART_TIME">Part-time</option>
            <option value="APPRENTICESHIP">Apprenticeship</option>
          </select>
        </div>

        <!-- Location Preset Filter -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Location Preset</label>
          <select v-model="filters.location" @change="applyFilters" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none">
            <option value="All">All Locations</option>
            <option value="India">🇮🇳 India (Prioritized)</option>
            <option value="Bengaluru">Bengaluru</option>
            <option value="Hyderabad">Hyderabad</option>
            <option value="Mumbai">Mumbai / Pune</option>
            <option value="Gurugram">Delhi NCR / Gurugram</option>
            <option value="Remote India">Remote India</option>
            <option value="International Remote">International Remote</option>
          </select>
        </div>

        <!-- Work Mode -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Work Mode</label>
          <select v-model="filters.workMode" @change="applyFilters" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none">
            <option value="All">All Modes</option>
            <option value="REMOTE">Remote / WFH</option>
            <option value="HYBRID">Hybrid</option>
            <option value="ONSITE">On-site</option>
          </select>
        </div>

        <!-- Sort -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Sort By</label>
          <select v-model="filters.sort" @change="applyFilters" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-2.5 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none">
            <option value="newest">Newest Jobs First</option>
            <option value="match_high">Resume Match Score</option>
            <option value="salary_high">Salary: High → Low</option>
          </select>
        </div>

        <!-- Reset Button -->
        <div class="space-y-1 flex items-end">
          <button @click="resetFilters" class="w-full btn-secondary py-2 px-3 text-xs font-bold flex items-center justify-center gap-1">
            <RotateCcw class="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>

      </div>
    </div>

    <!-- DAY GROUPING HEADERS & CARDS FEED -->
    <div v-if="isLoading" class="space-y-4 py-8">
      <div v-for="i in 4" :key="i" class="glass-card rounded-2xl p-6 border border-slate-800 space-y-3 animate-pulse bg-slate-950">
        <div class="h-5 bg-slate-800 rounded w-1/3"></div>
        <div class="h-4 bg-slate-900 rounded w-1/4"></div>
        <div class="h-16 bg-slate-900/60 rounded"></div>
      </div>
    </div>

    <div v-else-if="jobList.length === 0" class="glass-card rounded-2xl p-12 border border-slate-800 text-center space-y-4 my-8 bg-slate-950">
      <AlertCircle class="w-12 h-12 text-amber-400 mx-auto" />
      <h3 class="text-lg font-bold text-slate-100">No matching opportunities posted in the last 14 days.</h3>
      <p class="text-xs text-slate-400 max-w-md mx-auto">
        Try adjusting your search criteria, switching to "Last 14 Days", or selecting "All Locations".
      </p>
      <button @click="resetFilters" class="btn-primary py-2 px-4 text-xs font-bold shadow-lg shadow-indigo-600/30">
        Reset All Filters
      </button>
    </div>

    <div v-else class="space-y-8">
      <!-- DAY GROUP: TODAY -->
      <div v-if="todayJobs.length" class="space-y-4">
        <div class="flex items-center justify-between border-b border-indigo-500/30 pb-2">
          <h2 class="text-base font-extrabold text-slate-100 flex items-center gap-2 font-mono">
            <span>🔥 TODAY'S OPPORTUNITIES</span>
            <span class="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-bold">
              {{ todayJobs.length }} jobs
            </span>
          </h2>
          <span class="text-xs text-slate-400 font-mono">Posted within last 24 hours</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="job in todayJobs" :key="job.canonical_job_id || job.id" class="glass-card glass-card-hover rounded-2xl p-5 border border-slate-800 space-y-4 bg-slate-950 flex flex-col justify-between">
            <div class="space-y-3">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <span class="text-[10px] font-bold text-slate-400 font-mono uppercase block">{{ job.company }}</span>
                  <h3 class="font-extrabold text-slate-100 text-base leading-snug mt-0.5">{{ job.title }}</h3>
                </div>

                <!-- Match Score & Merged Source Badges -->
                <div class="flex flex-col items-end gap-1">
                  <span v-if="job.overall_match_score" class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono text-[10px] font-extrabold flex items-center gap-1">
                    🎯 {{ job.overall_match_score }}% Match
                  </span>
                  <span v-for="src in (job.sources_json || [job.source])" :key="src" class="text-[9px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-indigo-300 font-bold">
                    {{ src }}
                  </span>
                </div>
              </div>

              <!-- Tags -->
              <div class="flex flex-wrap gap-1.5 text-[11px] font-mono">
                <span class="px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">📍 {{ job.location }}</span>
                <span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">💼 {{ job.work_mode }}</span>
                <span class="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">⏱️ {{ job.job_type }}</span>
                <span v-if="job.salary_range" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">💰 {{ job.salary_range }}</span>
              </div>

              <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                {{ job.description }}
              </p>

              <!-- Skills -->
              <div v-if="job.skills && job.skills.length" class="flex flex-wrap gap-1">
                <span v-for="skill in job.skills.slice(0, 5)" :key="skill" class="px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800 text-[10px] font-mono">
                  {{ skill }}
                </span>
              </div>
            </div>

            <!-- Card Footer & Direct Apply Link -->
            <div class="border-t border-slate-800/80 pt-3 mt-3 flex items-center justify-between gap-2">
              <span class="text-[10px] text-slate-500 font-mono">Posted Today</span>

              <div class="flex items-center gap-2">
                <button @click="openJobModal(job)" class="btn-secondary py-1.5 px-3 text-xs font-bold">
                  Details
                </button>

                <a
                  :href="getApplyUrl(job)"
                  target="_blank"
                  rel="noopener noreferrer"
                  @click="handleApplyClick(job)"
                  class="btn-primary py-1.5 px-3 text-xs font-extrabold flex items-center gap-1 shadow-md shadow-indigo-600/30"
                >
                  <span>Apply Now</span>
                  <ExternalLink class="w-3.5 h-3.5" />
                </a>
              </div>
            </div>

          </div>
        </div>
      </div>

      <!-- DAY GROUP: EARLIER (1..14 Days Ago) -->
      <div v-if="earlierJobs.length" class="space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <h2 class="text-base font-extrabold text-slate-100 flex items-center gap-2 font-mono">
            <span>📅 EARLIER OPPORTUNITIES (LAST 14 DAYS)</span>
            <span class="text-xs px-2.5 py-0.5 rounded-full bg-slate-900 text-slate-300 border border-slate-800 font-bold">
              {{ earlierJobs.length }} jobs
            </span>
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="job in earlierJobs" :key="job.canonical_job_id || job.id" class="glass-card glass-card-hover rounded-2xl p-5 border border-slate-800 space-y-4 bg-slate-950 flex flex-col justify-between">
            <div class="space-y-3">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <span class="text-[10px] font-bold text-slate-400 font-mono uppercase block">{{ job.company }}</span>
                  <h3 class="font-extrabold text-slate-100 text-base leading-snug mt-0.5">{{ job.title }}</h3>
                </div>

                <div class="flex flex-col items-end gap-1">
                  <span v-if="job.overall_match_score" class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono text-[10px] font-extrabold flex items-center gap-1">
                    🎯 {{ job.overall_match_score }}% Match
                  </span>
                  <span v-for="src in (job.sources_json || [job.source])" :key="src" class="text-[9px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-indigo-300 font-bold">
                    {{ src }}
                  </span>
                </div>
              </div>

              <div class="flex flex-wrap gap-1.5 text-[11px] font-mono">
                <span class="px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">📍 {{ job.location }}</span>
                <span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">💼 {{ job.work_mode }}</span>
                <span class="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">⏱️ {{ job.job_type }}</span>
                <span v-if="job.salary_range" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">💰 {{ job.salary_range }}</span>
              </div>

              <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                {{ job.description }}
              </p>

              <div v-if="job.skills && job.skills.length" class="flex flex-wrap gap-1">
                <span v-for="skill in job.skills.slice(0, 5)" :key="skill" class="px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800 text-[10px] font-mono">
                  {{ skill }}
                </span>
              </div>
            </div>

            <div class="border-t border-slate-800/80 pt-3 mt-3 flex items-center justify-between gap-2">
              <span class="text-[10px] text-slate-500 font-mono">{{ job.posted_text || 'Recently' }}</span>

              <div class="flex items-center gap-2">
                <button @click="openJobModal(job)" class="btn-secondary py-1.5 px-3 text-xs font-bold">
                  Details
                </button>

                <a
                  :href="getApplyUrl(job)"
                  target="_blank"
                  rel="noopener noreferrer"
                  @click="handleApplyClick(job)"
                  class="btn-primary py-1.5 px-3 text-xs font-extrabold flex items-center gap-1 shadow-md shadow-indigo-600/30"
                >
                  <span>Apply Now</span>
                  <ExternalLink class="w-3.5 h-3.5" />
                </a>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- SERVER PAGINATION UI -->
    <div v-if="pagination.totalPages > 1" class="flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-800 pt-6 my-6 text-xs font-mono">
      <span class="text-slate-400">
        Showing Page <strong>{{ pagination.page }}</strong> of <strong>{{ pagination.totalPages }}</strong> ({{ pagination.total }} total jobs)
      </span>

      <div class="flex items-center gap-2">
        <button
          @click="goToPage(pagination.page - 1)"
          :disabled="!pagination.hasPrevious || isLoading"
          class="btn-secondary py-2 px-3 text-xs font-bold flex items-center gap-1 disabled:opacity-40"
        >
          <ChevronLeft class="w-4 h-4" />
          <span>Previous</span>
        </button>

        <div class="flex items-center gap-1">
          <button
            v-for="p in pageNumbers"
            :key="p"
            @click="goToPage(p)"
            :class="[
              'py-1.5 px-3 rounded-lg text-xs font-bold transition',
              p === pagination.page ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            ]"
          >
            {{ p }}
          </button>
        </div>

        <button
          @click="goToPage(pagination.page + 1)"
          :disabled="!pagination.hasNext || isLoading"
          class="btn-secondary py-2 px-3 text-xs font-bold flex items-center gap-1 disabled:opacity-40"
        >
          <span>Next</span>
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- JOB DETAILS MODAL -->
    <div v-if="selectedJobModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div class="glass-card rounded-2xl p-6 border border-slate-800 max-w-2xl w-full space-y-5 bg-slate-950 shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h3 class="text-lg font-extrabold text-slate-100">{{ selectedJobModal.title }}</h3>
            <p class="text-xs text-indigo-400 font-mono font-bold">{{ selectedJobModal.company }} • {{ selectedJobModal.location }}</p>
          </div>
          <button @click="selectedJobModal = null" class="text-slate-400 hover:text-slate-100 text-lg font-bold">✕</button>
        </div>

        <div class="space-y-4 text-xs">
          <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <span class="font-extrabold text-slate-200 text-sm font-mono">Job Specifications</span>
              <span class="text-[10px] text-slate-400 font-mono">Posted {{ selectedJobModal.posted_text || 'Recently' }}</span>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[11px] font-mono pt-1">
              <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
                <span class="text-slate-400 block text-[10px]">Employment Type</span>
                <span class="text-slate-200 font-bold">{{ selectedJobModal.job_type }}</span>
              </div>
              <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
                <span class="text-slate-400 block text-[10px]">Work Mode</span>
                <span class="text-emerald-400 font-bold">{{ selectedJobModal.work_mode }}</span>
              </div>
              <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
                <span class="text-slate-400 block text-[10px]">Experience Level</span>
                <span class="text-purple-300 font-bold">{{ selectedJobModal.experience_level }}</span>
              </div>
            </div>
          </div>

          <div class="space-y-1">
            <h4 class="font-bold text-slate-200 uppercase text-[11px] tracking-wider">Job Description:</h4>
            <p class="text-slate-300 leading-relaxed bg-slate-900 p-4 rounded-xl border border-slate-800 whitespace-pre-line">{{ selectedJobModal.description }}</p>
          </div>
        </div>

        <div class="flex items-center justify-end gap-3 border-t border-slate-800 pt-4">
          <button @click="selectedJobModal = null" class="btn-secondary py-2 px-4 text-xs font-bold">Close</button>
          <a
            :href="getApplyUrl(selectedJobModal)"
            target="_blank"
            rel="noopener noreferrer"
            @click="handleApplyClick(selectedJobModal)"
            class="btn-primary py-2 px-5 text-xs font-extrabold flex items-center gap-2 shadow-lg shadow-indigo-600/30"
          >
            <span>[ Apply Directly on Source ]</span>
            <ExternalLink class="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Briefcase, RefreshCw, Search, RotateCcw, AlertCircle, ExternalLink, SlidersHorizontal, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { fetchGlobalJobs, fetchLiveJobMatches, recordApplyClick } from '../services/api'

const route = useRoute()
const router = useRouter()

const isLoading = ref<boolean>(false)
const showMobileFilters = ref<boolean>(false)

const filters = ref({
  q: '',
  postedWithin: 14,
  jobType: 'All',
  workMode: 'All',
  experience: 'All',
  category: 'All',
  location: 'All',
  sort: 'newest',
  page: 1,
  limit: 24
})

const candidateProfile = ref<any>(null)
const jobList = ref<any[]>([])
const lastSyncedAt = ref<string>('')
const selectedJobModal = ref<any>(null)

const pagination = ref({
  page: 1,
  limit: 24,
  total: 0,
  totalPages: 1,
  hasNext: false,
  hasPrevious: false
})

const todayJobs = computed(() => {
  return jobList.value.filter(j => j.days_ago === 0)
})

const earlierJobs = computed(() => {
  return jobList.value.filter(j => j.days_ago > 0)
})

const pageNumbers = computed(() => {
  const current = pagination.value.page
  const total = pagination.value.totalPages
  const pages: number[] = []
  for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) {
    pages.push(i)
  }
  return pages
})

const loadJobs = async () => {
  isLoading.value = true
  try {
    const resMatches = await fetchLiveJobMatches({
      days_limit: filters.value.postedWithin,
      minMatchScore: 40,
      job_type_filter: filters.value.jobType,
      work_mode_filter: filters.value.workMode,
      location_filter: filters.value.location !== 'All' ? filters.value.location : 'All'
    })

    if (resMatches && resMatches.candidate_profile) {
      candidateProfile.value = resMatches.candidate_profile
    }

    if (resMatches && resMatches.matched_jobs) {
      let matched = resMatches.matched_jobs || []

      // Keyword query filter
      if (filters.value.q && filters.value.q.trim()) {
        const query = filters.value.q.trim().toLowerCase()
        matched = matched.filter((j: any) =>
          (j.title || '').toLowerCase().includes(query) ||
          (j.company || '').toLowerCase().includes(query) ||
          (j.description || '').toLowerCase().includes(query) ||
          (j.skills || []).some((s: string) => s.toLowerCase().includes(query))
        )
      }

      // Sort handling
      if (filters.value.sort === 'newest') {
        matched.sort((a: any, b: any) => new Date(b.posted_at).getTime() - new Date(a.posted_at).getTime())
      } else if (filters.value.sort === 'match_high') {
        matched.sort((a: any, b: any) => (b.overall_match_score || 0) - (a.overall_match_score || 0))
      }

      jobList.value = matched
      pagination.value.total = matched.length
      pagination.value.totalPages = Math.max(1, Math.ceil(matched.length / filters.value.limit))
      lastSyncedAt.value = resMatches.last_updated || new Date().toISOString()
    } else {
      // Fallback to global jobs discovery endpoint
      const res = await fetchGlobalJobs({
        q: filters.value.q || undefined,
        postedWithin: filters.value.postedWithin,
        jobType: filters.value.jobType,
        workMode: filters.value.workMode,
        location: filters.value.location !== 'All' ? filters.value.location : undefined,
        sort: filters.value.sort,
        page: filters.value.page,
        limit: filters.value.limit
      })
      jobList.value = res.items || []
      if (res.pagination) pagination.value = res.pagination
      lastSyncedAt.value = res.lastSyncedAt || new Date().toISOString()
    }
  } catch (err) {
    console.error('Failed to load discovery jobs:', err)
  } finally {
    isLoading.value = false
  }
}

const applyFilters = () => {
  filters.value.page = 1
  syncUrl()
  loadJobs()
}

const resetFilters = () => {
  filters.value = {
    q: '',
    postedWithin: 14,
    jobType: 'All',
    workMode: 'All',
    experience: 'All',
    category: 'All',
    location: 'All',
    sort: 'newest',
    page: 1,
    limit: 24
  }
  syncUrl()
  loadJobs()
}

const goToPage = (newPage: number) => {
  if (newPage < 1 || newPage > pagination.value.totalPages) return
  filters.value.page = newPage
  syncUrl()
  loadJobs()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const syncUrl = () => {
  router.push({
    query: {
      q: filters.value.q || undefined,
      postedWithin: filters.value.postedWithin !== 14 ? String(filters.value.postedWithin) : undefined,
      jobType: filters.value.jobType !== 'All' ? filters.value.jobType : undefined,
      workMode: filters.value.workMode !== 'All' ? filters.value.workMode : undefined,
      category: filters.value.category !== 'All' ? filters.value.category : undefined,
      page: filters.value.page > 1 ? String(filters.value.page) : undefined
    }
  }).catch(() => {})
}

const getApplyUrl = (job: any): string => {
  if (!job) return '#'
  return job.apply_url || job.application_url || job.source_url || job.url || '#'
}

const handleApplyClick = (job: any) => {
  if (job && job.id) {
    recordApplyClick(job.id).catch(() => {})
  }
}

const openJobModal = (job: any) => {
  selectedJobModal.value = job
}

const formatDate = (isoStr: string) => {
  if (!isoStr) return 'Recently'
  return new Date(isoStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  // Read query params from URL
  const q = route.query
  if (q.q) filters.value.q = String(q.q)
  if (q.postedWithin) filters.value.postedWithin = Number(q.postedWithin)
  if (q.jobType) filters.value.jobType = String(q.jobType)
  if (q.workMode) filters.value.workMode = String(q.workMode)
  if (q.category) filters.value.category = String(q.category)
  if (q.page) filters.value.page = Number(q.page)

  loadJobs()
})
</script>
