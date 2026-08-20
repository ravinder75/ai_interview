<template>
  <div class="max-w-6xl mx-auto space-y-6 py-4 px-2 sm:px-4 font-sans">
    
    <!-- 1. SETUP / PROFILE EDIT MODE -->
    <div v-if="!isProfileSaved || isEditing" class="glass-card rounded-3xl p-8 border border-slate-800 space-y-8 bg-slate-950">
      
      <!-- Top Title Header -->
      <div class="space-y-1.5 border-b border-slate-800 pb-5 flex items-center justify-between">
        <div>
          <h2 class="text-xl font-extrabold text-slate-100 flex items-center gap-2">
            <span class="text-2xl">🎯</span>
            INTERVIEW BIT — RESUME INTELLIGENCE & MATCHING
          </h2>
          <p class="text-xs text-slate-400">Upload candidate resume to activate personalized job discovery</p>
        </div>
        <button
          v-if="isEditing && isProfileSaved"
          @click="isEditing = false"
          class="btn-secondary py-1.5 px-3 text-xs font-bold"
        >
          Cancel
        </button>
      </div>

      <!-- Upload Resume Area -->
      <div class="space-y-3">
        <label class="text-xs font-bold text-slate-300 uppercase tracking-wider block">Upload Resume Document</label>
        
        <div
          @click="triggerUpload"
          class="border-2 border-dashed border-slate-700 bg-slate-950/70 hover:border-indigo-500/70 rounded-2xl p-8 text-center cursor-pointer transition flex flex-col items-center justify-center gap-3"
        >
          <input type="file" ref="fileInput" @change="handleFileUpload" class="hidden" accept=".pdf,.docx,.doc,.txt" />
          
          <div class="w-12 h-12 rounded-2xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center text-2xl border border-indigo-500/30">
            📄
          </div>
          <div>
            <span class="text-sm font-bold text-slate-200 block">Upload candidate resume</span>
            <span class="text-xs text-slate-400">PDF / DOCX / TXT (Mandatory for personalized matching)</span>
          </div>

          <button type="button" class="btn-primary py-2 px-5 text-xs font-bold shadow-md shadow-indigo-600/30 mt-1">
            [ Choose File ]
          </button>

          <div v-if="isUploading" class="flex items-center gap-2 text-xs text-indigo-400 font-bold mt-2">
            <Loader2 class="w-4 h-4 animate-spin" />
            <span>Analyzing resume & populating candidate profile...</span>
          </div>

          <div v-else-if="resumeAnalyzedToast" class="text-xs text-emerald-400 font-bold flex items-center gap-1.5 mt-2 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 font-mono">
            <span>✓ Resume parsed successfully! Profile activated.</span>
          </div>
        </div>
      </div>

      <!-- Candidate Details Form -->
      <form @submit.prevent="handleSaveProfile" class="space-y-6">
        <div class="space-y-3">
          <label class="text-xs font-bold text-slate-300 uppercase tracking-wider block">Candidate Attributes</label>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div class="space-y-1">
              <span class="text-slate-400 font-semibold">Candidate Name</span>
              <input
                v-model="form.name"
                type="text"
                required
                placeholder="Alex Johnson"
                class="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-slate-100 placeholder-slate-500 outline-none transition"
              />
            </div>

            <div class="space-y-1">
              <span class="text-slate-400 font-semibold">Target Role <span class="text-rose-400">*</span></span>
              <select
                v-model="form.target_role"
                required
                class="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-slate-100 outline-none transition font-mono text-xs"
              >
                <option value="" disabled>-- Select Candidate Role (Mandatory) --</option>
                <option value="AI/ML Engineer">AI/ML Engineer</option>
                <option value="Software Engineer">Software Engineer</option>
                <option value="Full-Stack Developer">Full-Stack Developer</option>
                <option value="Frontend Developer">Frontend Developer</option>
                <option value="Backend Developer">Backend Developer</option>
                <option value="Data Scientist">Data Scientist</option>
                <option value="Data Analyst">Data Analyst</option>
                <option value="DevOps / Cloud Engineer">DevOps / Cloud Engineer</option>
                <option value="Cybersecurity Engineer">Cybersecurity Engineer</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Skill Chips -->
        <div class="space-y-2">
          <label class="text-xs font-bold text-slate-300 uppercase tracking-wider block">Extracted Skill Keywords</label>
          <div class="p-3 rounded-2xl bg-slate-950 border border-slate-700 space-y-2">
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="(s, sIdx) in form.skills"
                :key="sIdx"
                class="px-2.5 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono text-[11px] flex items-center gap-1.5"
              >
                <span>{{ s }}</span>
                <button type="button" @click="removeSkill(sIdx)" class="hover:text-rose-400 font-bold text-xs">✕</button>
              </span>
            </div>
          </div>
        </div>

        <button
          type="submit"
          :disabled="store.isSavingProfile"
          class="w-full btn-primary py-3 text-xs font-extrabold flex items-center justify-center gap-2 shadow-xl shadow-indigo-600/30 rounded-2xl"
        >
          <Loader2 v-if="store.isSavingProfile" class="w-4 h-4 animate-spin" />
          <Check v-else class="w-4 h-4" />
          <span>[ Save & Activate Resume-Matched Jobs ]</span>
        </button>
      </form>
    </div>

    <!-- 2. PERSONALIZED RESUME-MATCHED DASHBOARD -->
    <div v-else class="space-y-6">
      
      <!-- Candidate Profile Summary Header Card -->
      <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-4 bg-slate-950">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-extrabold text-lg">
              🎯
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h2 class="text-lg font-extrabold text-slate-100">{{ store.profile?.name || 'Candidate' }}</h2>
                <span class="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  ● ACTIVE RESUME PROFILE
                </span>
              </div>
              <p class="text-xs text-indigo-300 font-mono">
                Target Role: <strong>{{ store.profile?.target_role }}</strong> • Filtered to <strong>Last 14 Days</strong>
              </p>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button @click="startEdit" class="btn-secondary py-2 px-3 text-xs font-bold flex items-center gap-1.5">
              <Edit3 class="w-3.5 h-3.5 text-indigo-400" />
              <span>Edit Profile</span>
            </button>
            <button @click="triggerUpload" class="btn-primary py-2 px-4 text-xs font-bold shadow-md shadow-indigo-600/30 flex items-center gap-1.5">
              <UploadCloud class="w-3.5 h-3.5" />
              <span>[ Upload New Resume ]</span>
            </button>
            <input type="file" ref="fileInput" @change="handleFileUpload" class="hidden" accept=".pdf,.docx,.doc,.txt" />
          </div>
        </div>

        <!-- Parsed Skills Pills -->
        <div v-if="store.profile?.skills && store.profile.skills.length" class="space-y-1 text-xs">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Parsed Candidate Skills:</span>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="s in store.profile.skills.slice(0, 15)" :key="s" class="px-2.5 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 text-[11px] font-mono font-semibold">
              ✓ {{ s }}
            </span>
          </div>
        </div>
      </div>

      <!-- MATCHED JOBS CARDS LIST -->
      <div v-if="isLoadingMatches" class="space-y-4 py-8">
        <div v-for="i in 3" :key="i" class="glass-card rounded-2xl p-6 border border-slate-800 space-y-3 animate-pulse bg-slate-950">
          <div class="h-5 bg-slate-800 rounded w-1/3"></div>
          <div class="h-4 bg-slate-900 rounded w-1/4"></div>
          <div class="h-20 bg-slate-900/60 rounded"></div>
        </div>
      </div>

      <div v-else class="space-y-4">
        <div class="flex items-center justify-between border-b border-indigo-500/30 pb-2">
          <h2 class="text-base font-extrabold text-slate-100 flex items-center gap-2 font-mono">
            <span>🎯 YOUR RESUME MATCHED OPPORTUNITIES</span>
            <span class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">
              {{ matchedJobs.length }} matches
            </span>
          </h2>
          <span class="text-xs text-slate-400 font-mono">Sorted by Best Match + Newest</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="job in matchedJobs" :key="job.canonical_job_id || job.id" class="glass-card glass-card-hover rounded-2xl p-6 border border-slate-800 space-y-4 bg-slate-950 flex flex-col justify-between">
            
            <div class="space-y-3">
              <!-- Top Row: Title, Company, Match Score Badge -->
              <div class="flex items-start justify-between gap-3">
                <div>
                  <span class="text-[10px] font-bold text-slate-400 font-mono uppercase block">{{ job.company }}</span>
                  <h3 class="font-extrabold text-slate-100 text-lg leading-snug mt-0.5">{{ job.title }}</h3>
                </div>

                <div class="flex flex-col items-end gap-1">
                  <!-- Match Score Badge -->
                  <span :class="[
                    'text-sm font-extrabold font-mono px-3 py-1 rounded-xl border shadow-md',
                    job.overall_match_score >= 85 ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-emerald-950' :
                    (job.overall_match_score >= 75 ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40 shadow-indigo-950' : 'bg-amber-500/20 text-amber-300 border-amber-500/40')
                  ]">
                    🎯 {{ job.overall_match_score }}% Match
                  </span>

                  <!-- Merged Sources -->
                  <div class="flex items-center gap-1 flex-wrap">
                    <span v-for="src in (job.sources_json || [job.source])" :key="src" class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400 font-bold">
                      {{ src }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Tags -->
              <div class="flex flex-wrap gap-1.5 text-[11px] font-mono">
                <span class="px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">📍 {{ job.location }}</span>
                <span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">💼 {{ job.work_mode }}</span>
                <span class="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">⏱️ {{ job.job_type }}</span>
              </div>

              <!-- Match Explanation Box -->
              <div class="p-3 rounded-xl bg-indigo-950/30 border border-indigo-500/20 space-y-1 text-xs">
                <span class="text-[10px] font-bold text-indigo-300 uppercase tracking-wider block font-mono">Why this job matches you:</span>
                <p class="text-slate-300 text-[11px] leading-relaxed font-sans">{{ job.why_matches }}</p>
              </div>

              <!-- Matched Skills (Green) vs Missing Skills (Amber) -->
              <div class="space-y-1.5 text-xs pt-1">
                <div v-if="job.matched_skills && job.matched_skills.length" class="space-y-1">
                  <span class="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block font-mono">Matched Skills:</span>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="mSkill in job.matched_skills" :key="mSkill" class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[10px] font-mono font-bold">
                      ✓ {{ mSkill }}
                    </span>
                  </div>
                </div>

                <div v-if="job.missing_skills && job.missing_skills.length" class="space-y-1 pt-1">
                  <span class="text-[10px] font-bold text-amber-400 uppercase tracking-wider block font-mono">Skills to Develop:</span>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="missSkill in job.missing_skills.slice(0, 4)" :key="missSkill" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[10px] font-mono">
                      + {{ missSkill }}
                    </span>
                  </div>
                </div>
              </div>

            </div>

            <!-- Card Footer -->
            <div class="border-t border-slate-800/80 pt-3 mt-3 flex items-center justify-between gap-2">
              <span class="text-[10px] text-slate-500 font-mono">Posted {{ job.posted_text || 'Recently' }}</span>

              <div class="flex items-center gap-2">
                <button @click="openJobModal(job)" class="btn-secondary py-1.5 px-3 text-xs font-bold">
                  View Details
                </button>

                <a
                  :href="getApplyUrl(job)"
                  target="_blank"
                  rel="noopener noreferrer"
                  @click="handleApplyClick(job)"
                  class="btn-primary py-1.5 px-4 text-xs font-extrabold flex items-center gap-1.5 shadow-md shadow-indigo-600/30"
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
          <div class="p-4 rounded-xl bg-slate-900 border border-indigo-500/30 space-y-2">
            <div class="flex items-center justify-between">
              <span class="font-extrabold text-emerald-400 text-sm font-mono">🎯 {{ selectedJobModal.overall_match_score }}% Match Breakdown</span>
              <span class="text-[10px] text-slate-400 font-mono">Posted {{ selectedJobModal.posted_text || 'Recently' }}</span>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px] font-mono pt-1">
              <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
                <span class="text-slate-400 block">Skills Match</span>
                <span class="text-emerald-400 font-bold">{{ selectedJobModal.match_breakdown?.skills_match || 80 }}%</span>
              </div>
              <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
                <span class="text-slate-400 block">Role Match</span>
                <span class="text-indigo-300 font-bold">{{ selectedJobModal.match_breakdown?.role_match || 85 }}%</span>
              </div>
              <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
                <span class="text-slate-400 block">Experience</span>
                <span class="text-purple-300 font-bold">{{ selectedJobModal.match_breakdown?.experience_match || 90 }}%</span>
              </div>
              <div class="p-2.5 rounded bg-slate-950 border border-slate-800">
                <span class="text-slate-400 block">Location</span>
                <span class="text-blue-300 font-bold">{{ selectedJobModal.match_breakdown?.location_match || 100 }}%</span>
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
            <span>[ Apply Directly on {{ selectedJobModal.source }} ]</span>
            <ExternalLink class="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Loader2, Check, Edit3, UploadCloud, ExternalLink } from 'lucide-vue-next'
import { useInterviewBitStore } from '../stores/interviewBit'
import { uploadInterviewBitResume } from '../services/interviewBitApi'
import { fetchLiveJobMatches, recordApplyClick } from '../services/api'

const store = useInterviewBitStore()

const fileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref<boolean>(false)
const resumeAnalyzedToast = ref<boolean>(false)
const isEditing = ref<boolean>(false)
const isProfileSaved = ref<boolean>(false)

const isLoadingMatches = ref<boolean>(false)
const matchedJobs = ref<any[]>([])
const jobTypeFilter = ref<string>('All')
const workModeFilter = ref<string>('All')
const locationFilter = ref<string>('All')
const selectedJobModal = ref<any>(null)

const form = reactive<{
  name: string
  target_role: string
  experience_level: string
  location: string
  skills: string[]
  additional_information: string
}>({
  name: '',
  target_role: '',
  experience_level: '',
  location: '',
  skills: [],
  additional_information: ''
})

const triggerUpload = () => {
  if (fileInput.value) fileInput.value.click()
}

const handleFileUpload = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (!target.files || !target.files.length) return
  const file = target.files[0]

  isUploading.value = true
  try {
    const data = await uploadInterviewBitResume(file)
    if (data.profile) {
      store.profile = data.profile
      populateFormFromProfile(data.profile)
      resumeAnalyzedToast.value = true
      isProfileSaved.value = true
      loadMatchedJobs()
    }
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to upload and analyze resume.')
  } finally {
    isUploading.value = false
    target.value = ''
  }
}

const populateFormFromProfile = (p: any) => {
  form.name = p.name || ''
  form.target_role = p.target_role || ''
  form.experience_level = p.experience_level || ''
  form.location = p.location || ''
  form.skills = [...(p.skills || [])]
  form.additional_information = p.additional_information || ''
}

const removeSkill = (idx: number) => {
  form.skills.splice(idx, 1)
}

const handleSaveProfile = async () => {
  if (!form.name || !form.target_role) return
  try {
    await store.saveProfile({
      name: form.name,
      target_role: form.target_role,
      experience_level: form.experience_level,
      location: form.location,
      skills: form.skills,
      additional_information: form.additional_information
    })
    isProfileSaved.value = true
    isEditing.value = false
    loadMatchedJobs()
  } catch (err) {
    console.error('Error saving profile:', err)
  }
}

const startEdit = () => {
  if (store.profile) {
    populateFormFromProfile(store.profile)
  }
  isEditing.value = true
}

const loadMatchedJobs = async () => {
  isLoadingMatches.value = true
  try {
    const res = await fetchLiveJobMatches({
      days_limit: 14,
      minMatchScore: 0,
      job_type_filter: jobTypeFilter.value,
      work_mode_filter: workModeFilter.value,
      location_filter: locationFilter.value !== 'All' ? locationFilter.value : undefined
    })
    matchedJobs.value = res.matched_jobs || []
  } catch (err) {
    console.error('Failed to load personalized job matches:', err)
  } finally {
    isLoadingMatches.value = false
  }
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

onMounted(async () => {
  await store.fetchProfile()
  if (store.profile && store.profile.target_role) {
    isProfileSaved.value = true
  }
  loadMatchedJobs()
})
</script>
