<template>
  <div class="max-w-4xl mx-auto space-y-6 py-2">

    <!-- Profile Picture & Personal Details Section -->
    <div v-if="authStore.user" class="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 class="text-xl font-bold text-slate-100 flex items-center gap-2">
            <UserIcon class="w-5 h-5 text-indigo-400" />
            User Profile Details & Image
          </h3>
          <p class="text-xs text-slate-400">Upload or change your profile picture and update personal details</p>
        </div>
        <span class="text-xs px-3 py-1 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-full font-bold">
          {{ authStore.user.auth_provider || 'Local' }}
        </span>
      </div>

      <div class="flex flex-col sm:flex-row items-center gap-6">
        <!-- User Avatar Image & Upload Button -->
        <div class="relative group">
          <div class="w-20 h-20 rounded-2xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center text-white font-extrabold text-2xl shadow-xl border-2 border-slate-700 overflow-hidden relative">
            <img v-if="profilePicture" :src="profilePicture" class="w-full h-full object-cover" alt="Profile Picture" />
            <span v-else>{{ userInitial }}</span>

            <!-- Hover overlay -->
            <label class="absolute inset-0 bg-slate-950/70 opacity-0 group-hover:opacity-100 flex flex-col items-center justify-center cursor-pointer transition-opacity duration-200 text-slate-200">
              <Camera class="w-5 h-5 text-indigo-400" />
              <span class="text-[9px] font-bold mt-0.5">Upload</span>
              <input type="file" accept="image/*" @change="handleImageUpload" class="hidden" />
            </label>
          </div>

          <button
            v-if="profilePicture"
            @click="removeImage"
            class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-rose-600 text-white flex items-center justify-center text-[10px] font-bold shadow-md hover:bg-rose-500 transition"
            title="Remove Photo"
          >
            ✕
          </button>
        </div>

        <div class="flex-1 space-y-3 w-full text-xs">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-semibold text-slate-300">Full Name</label>
              <input v-model="formName" type="text" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-100 outline-none focus:border-indigo-500" />
            </div>

            <div class="space-y-1">
              <label class="font-semibold text-slate-300">Target Role <span class="text-rose-400">*</span></label>
              <select
                v-model="formRole"
                required
                class="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-3.5 py-2 text-slate-100 outline-none transition font-mono text-xs"
              >
                <option value="" disabled>-- Select Candidate Role (Mandatory) --</option>
                <optgroup label="IT / Software Engineering & AI">
                  <option value="AI/ML Engineer">AI/ML Engineer</option>
                  <option value="Software Engineer">Software Engineer</option>
                  <option value="Full-Stack Developer">Full-Stack Developer</option>
                  <option value="Frontend Developer">Frontend Developer</option>
                  <option value="Backend Developer">Backend Developer</option>
                  <option value="Data Scientist">Data Scientist</option>
                  <option value="DevOps / Cloud Engineer">DevOps / Cloud Engineer</option>
                  <option value="Cybersecurity Engineer">Cybersecurity Engineer</option>
                </optgroup>
                <optgroup label="Medical & Healthcare">
                  <option value="Medical Officer / Physician">Medical Officer / Physician</option>
                  <option value="Clinical Researcher">Clinical Researcher</option>
                  <option value="Registered Nurse">Registered Nurse</option>
                  <option value="Pharmacist">Pharmacist</option>
                  <option value="Medical Lab Specialist">Medical Lab Specialist</option>
                </optgroup>
                <optgroup label="Business & Non-IT">
                  <option value="Product Manager">Product Manager</option>
                  <option value="Business Analyst">Business Analyst</option>
                  <option value="Human Resources (HR)">Human Resources (HR)</option>
                  <option value="Financial Analyst">Financial Analyst</option>
                  <option value="Marketing Manager">Marketing Manager</option>
                </optgroup>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-semibold text-slate-300">Experience Level</label>
              <select v-model="formExperience" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-slate-100 outline-none focus:border-indigo-500">
                <option value="Fresher">Fresher</option>
                <option value="Student">Student</option>
                <option value="Intern">Intern</option>
                <option value="0-1 Years">0-1 Years</option>
                <option value="1-3 Years">1-3 Years</option>
                <option value="3-5 Years">3-5 Years</option>
                <option value="5-8 Years">5-8 Years</option>
                <option value="8+ Years">8+ Years</option>
              </select>
            </div>

            <div class="space-y-1">
              <label class="font-semibold text-slate-300">Email Address (Read Only)</label>
              <input :value="authStore.user.email" disabled class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-slate-400 font-mono cursor-not-allowed" />
            </div>
          </div>

          <div class="flex justify-end pt-1">
            <button @click="saveProfile" :disabled="savingProfile" class="btn-primary py-2 px-5 text-xs font-bold flex items-center gap-1.5">
              <Loader2 v-if="savingProfile" class="w-3.5 h-3.5 animate-spin" />
              <Save v-else class="w-3.5 h-3.5" />
              <span>Save Profile</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Platform Settings Card -->
    <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 class="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Settings class="w-5 h-5 text-indigo-400" />
            Platform Preferences
          </h3>
          <p class="text-xs text-slate-400">Configure response style, difficulty, speech engine, and data retention</p>
        </div>
        <span class="text-xs px-3 py-1 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full font-bold">Preferences</span>
      </div>

      <!-- Settings Form -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
        
        <!-- Response Style -->
        <div class="space-y-1">
          <label class="font-semibold text-slate-300">Coaching Response Style</label>
          <select v-model="formStyle" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-100 outline-none">
            <option value="Professional">Professional & Direct</option>
            <option value="Encouraging">Encouraging & Constructive</option>
            <option value="Rigorous">Rigorous Hiring Bar</option>
          </select>
        </div>

        <!-- Default Difficulty -->
        <div class="space-y-1">
          <label class="font-semibold text-slate-300">Default Difficulty</label>
          <select v-model="formDifficulty" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-100 outline-none">
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard (FAANG Level)</option>
          </select>
        </div>

        <!-- Speech Engine -->
        <div class="space-y-1">
          <label class="font-semibold text-slate-300">Speech Recognition Engine</label>
          <select v-model="formSpeech" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-100 outline-none">
            <option value="Web Speech API">Web Speech API (Browser Native)</option>
            <option value="Whisper API (Backend Abstraction)">Whisper API (Backend Abstraction)</option>
          </select>
        </div>

        <!-- Data Retention -->
        <div class="space-y-1">
          <label class="font-semibold text-slate-300">Data Retention Days</label>
          <input
            v-model.number="formRetention"
            type="number"
            min="1"
            max="365"
            class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-100 outline-none"
          />
        </div>

      </div>

      <!-- Security Note -->
      <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 flex items-start gap-2.5">
        <ShieldCheck class="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <strong class="text-slate-200 block mb-0.5">Security Guarantee:</strong>
          All API secrets, JWT signature keys, and LLM credentials are strictly isolated on the backend server and never sent to browser responses.
        </div>
      </div>

      <!-- Save Button -->
      <div class="flex justify-end pt-2">
        <button @click="saveSettings" class="btn-primary py-2.5 px-6 text-xs font-bold flex items-center gap-2">
          <Save class="w-4 h-4" />
          <span>Save Preferences</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { Settings, ShieldCheck, Save, User as UserIcon, Loader2, Camera } from 'lucide-vue-next'
import { useSettingsStore } from '../stores/settingsStore'
import { useAuthStore } from '../stores/authStore'

const settingsStore = useSettingsStore()
const authStore = useAuthStore()

const formName = ref('')
const formRole = ref('')
const formExperience = ref('')
const profilePicture = ref('')
const savingProfile = ref(false)

const formStyle = ref<string>('Professional')
const formDifficulty = ref<string>('Medium')
const formSpeech = ref<string>('Web Speech API')
const formRetention = ref<number>(30)

const userInitial = computed(() => {
  if (authStore.user?.full_name) return authStore.user.full_name.charAt(0).toUpperCase()
  if (authStore.user?.email) return authStore.user.email.charAt(0).toUpperCase()
  return 'U'
})

onMounted(async () => {
  await settingsStore.fetchSettings()
  formStyle.value = settingsStore.settings.response_style
  formDifficulty.value = settingsStore.settings.difficulty
  formSpeech.value = settingsStore.settings.speech_recognition
  formRetention.value = settingsStore.settings.data_retention_days

  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }

  if (authStore.user) {
    formName.value = authStore.user.full_name || ''
    formRole.value = authStore.user.target_role || ''
    formExperience.value = authStore.user.experience_level || 'Fresher'
    profilePicture.value = authStore.user.profile_picture || ''
  }
})

watch(() => authStore.user, (u) => {
  if (u) {
    formName.value = u.full_name || ''
    formRole.value = u.target_role || ''
    formExperience.value = u.experience_level || 'Fresher'
    profilePicture.value = u.profile_picture || ''
  }
}, { immediate: true })

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    if (file.size > 10 * 1024 * 1024) {
      alert('Image file size is too large. Please select an image under 10MB.')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        // Resize image to maximum 300x300 thumbnail for lightweight profile storage
        const canvas = document.createElement('canvas')
        const maxDim = 300
        let width = img.width
        let height = img.height

        if (width > height) {
          if (width > maxDim) {
            height = Math.round((height * maxDim) / width)
            width = maxDim
          }
        } else {
          if (height > maxDim) {
            width = Math.round((width * maxDim) / height)
            height = maxDim
          }
        }

        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        if (ctx) {
          ctx.drawImage(img, 0, 0, width, height)
          // Compress to JPEG with 0.82 quality
          profilePicture.value = canvas.toDataURL('image/jpeg', 0.82)
        } else {
          profilePicture.value = e.target?.result as string
        }
      }
      img.src = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const removeImage = () => {
  profilePicture.value = ''
}

const saveProfile = async () => {
  savingProfile.value = true
  try {
    await authStore.updateProfile({
      full_name: formName.value,
      target_role: formRole.value,
      experience_level: formExperience.value,
      profile_picture: profilePicture.value
    })
    alert('✅ Profile and photo updated successfully!')
  } catch (err) {
    alert('Failed to update profile.')
  } finally {
    savingProfile.value = false
  }
}

const saveSettings = async () => {
  try {
    await settingsStore.updateSettings({
      response_style: formStyle.value,
      difficulty: formDifficulty.value,
      speech_recognition: formSpeech.value,
      data_retention_days: formRetention.value
    })
    alert('✅ Settings saved successfully!')
  } catch (err) {
    console.error('Failed to update settings:', err)
  }
}
</script>
