<template>
  <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-5">
    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
      <div class="flex items-center gap-2">
        <FileText class="w-5 h-5 text-purple-400" />
        <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider">RESUME PROFILE</h3>
      </div>
      <span class="text-[11px] px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20 font-mono">
        {{ profile.experience_level || 'Fresher' }}
      </span>
    </div>

    <!-- Profile Details Grid -->
    <div class="space-y-4 text-xs">
      
      <!-- Target Role -->
      <div class="space-y-1">
        <span class="text-slate-400 font-semibold uppercase text-[10px] tracking-wider block">Target Role</span>
        <span class="text-sm font-bold text-slate-100 block font-mono">{{ profile.target_role || 'Backend Developer' }}</span>
      </div>

      <!-- Skills -->
      <div class="space-y-1">
        <span class="text-slate-400 font-semibold uppercase text-[10px] tracking-wider block">Skills</span>
        <div class="flex flex-wrap gap-1.5 pt-0.5">
          <span
            v-for="s in profile.skills"
            :key="s"
            class="px-2.5 py-1 rounded-lg bg-purple-500/15 border border-purple-500/30 text-purple-300 font-semibold"
          >
            {{ s }}
          </span>
        </div>
      </div>

      <!-- Projects -->
      <div class="space-y-1">
        <span class="text-slate-400 font-semibold uppercase text-[10px] tracking-wider block">Projects</span>
        <div class="space-y-1.5">
          <div
            v-for="p in profile.projects"
            :key="p.name"
            class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 flex items-center justify-between"
          >
            <span class="font-bold text-slate-100">{{ p.name }}</span>
            <span class="text-[11px] text-slate-400 font-mono">{{ (p.technologies || []).join(' · ') }}</span>
          </div>
        </div>
      </div>

      <!-- Experience -->
      <div class="space-y-1">
        <span class="text-slate-400 font-semibold uppercase text-[10px] tracking-wider block">Experience</span>
        <span class="text-slate-200 block font-mono bg-slate-950 p-2.5 rounded-xl border border-slate-800">
          {{ (profile.experience || []).join(', ') || 'Fresher' }}
        </span>
      </div>

    </div>

    <!-- Actions -->
    <div class="flex items-center gap-3 pt-2 border-t border-slate-800">
      <input type="file" ref="fileInput" @change="onFileSelected" class="hidden" accept=".pdf,.doc,.docx,.txt" />
      <button @click="triggerUpload" class="btn-primary py-2 px-4 text-xs font-bold flex items-center gap-1.5">
        <UploadCloud class="w-4 h-4" />
        <span>Upload New Resume</span>
      </button>
      <button @click="$emit('reanalyze')" class="btn-secondary py-2 px-4 text-xs font-bold flex items-center gap-1.5">
        <RefreshCw class="w-3.5 h-3.5 text-cyan-400" />
        <span>Re-analyze</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FileText, UploadCloud, RefreshCw } from 'lucide-vue-next'

interface ProjectDetail {
  name: string;
  technologies: string[];
}

interface ProfileData {
  target_role: string;
  experience_level: string;
  skills: string[];
  projects: ProjectDetail[];
  experience: string[];
}

const props = withDefaults(defineProps<{
  profile?: ProfileData
}>(), {
  profile: () => ({
    target_role: 'Backend Developer',
    experience_level: 'Fresher',
    skills: ['Python', 'FastAPI', 'SQL', 'JavaScript'],
    projects: [
      { name: 'AI Interview Platform', technologies: ['FastAPI', 'Vue', 'PostgreSQL'] }
    ],
    experience: ['Fresher']
  })
})

const emit = defineEmits(['upload-resume', 'reanalyze'])
const fileInput = ref<HTMLInputElement | null>(null)

const triggerUpload = () => {
  fileInput.value?.click()
}

const onFileSelected = (e: Event) => {
  const files = (e.target as HTMLInputElement).files
  if (files && files[0]) {
    emit('upload-resume', files[0])
  }
}
</script>
