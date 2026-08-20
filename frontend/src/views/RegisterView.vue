<template>
  <AuthLayout title="Create your account" subtitle="Join Interview Coach AI to build interview confidence">
    <!-- Google OAuth GIS Button -->
    <GoogleLoginButton @success="handleGoogleGISSuccess" @error="handleGoogleGISError" />

    <div class="flex items-center gap-3">
      <div class="flex-1 h-px bg-slate-800"></div>
      <span class="text-[10px] uppercase font-bold text-slate-500">OR</span>
      <div class="flex-1 h-px bg-slate-800"></div>
    </div>

    <!-- Error Banner -->
    <div v-if="authStore.error" class="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
      {{ authStore.error }}
    </div>

    <!-- OTP VERIFICATION STEP -->
    <div v-if="requiresOtp" class="space-y-4 text-xs">
      <div v-if="otpError" class="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
        {{ otpError }}
      </div>

      <div class="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs space-y-1">
        <p class="font-bold">Verification code sent!</p>
        <p class="text-slate-400 text-[11px]">We sent a 6-digit OTP verification code to <strong>{{ email }}</strong>.</p>
      </div>

      <form @submit.prevent="handleVerifyOtp" class="space-y-4">
        <div class="space-y-1">
          <div class="flex items-center justify-between">
            <label class="font-semibold text-slate-300">Enter 6-Digit OTP Code</label>
            <span class="text-[11px] font-mono text-indigo-400 font-bold">Expires in {{ formattedExpiryTimer }}</span>
          </div>
          <input
            v-model="otpCode"
            type="text"
            maxlength="6"
            required
            placeholder="123456"
            class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500 transition text-center tracking-[8px] font-mono text-lg"
          />
          <div class="flex items-center justify-between text-[11px] text-slate-400 mt-1">
            <button
              type="button"
              @click="requiresOtp = false"
              class="text-indigo-400 font-medium hover:underline"
            >
              Edit Email ({{ email }})
            </button>
            <button
              type="button"
              @click="handleResendOtp"
              :disabled="resendCooldown > 0 || isVerifyingOtp"
              class="text-indigo-400 font-bold hover:underline disabled:opacity-50 disabled:no-underline"
            >
              {{ resendCooldown > 0 ? `Resend OTP (${resendCooldown}s)` : 'Resend OTP' }}
            </button>
          </div>
        </div>

        <button
          type="submit"
          :disabled="isVerifyingOtp || otpCode.length !== 6"
          class="w-full btn-primary py-3 font-bold flex items-center justify-center gap-2 text-sm shadow-lg shadow-indigo-600/30"
        >
          <Loader2 v-if="isVerifyingOtp" class="w-4 h-4 animate-spin" />
          <CheckCircle2 v-else class="w-4 h-4" />
          <span>{{ isVerifyingOtp ? 'Verifying OTP...' : 'Verify & Continue' }}</span>
        </button>

        <button
          type="button"
          @click="requiresOtp = false"
          class="w-full text-slate-400 hover:text-slate-200 text-xs py-1.5 flex items-center justify-center gap-1 transition"
        >
          <ArrowLeft class="w-3.5 h-3.5" />
          <span>Back to Edit Registration Details</span>
        </button>
      </form>
    </div>

    <!-- Registration Form -->
    <form v-else @submit.prevent="handleRegister" class="space-y-4 text-xs">
      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Full Name</label>
        <input
          v-model="name"
          type="text"
          required
          placeholder="Enter your full name"
          class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500 transition"
        />
        <p v-if="errors.name" class="text-[11px] text-rose-400 font-medium">{{ errors.name }}</p>
      </div>

      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Email Address</label>
        <input
          v-model="email"
          @input="email = email.toLowerCase()"
          type="email"
          required
          placeholder="you@example.com"
          class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500 transition lowercase"
        />
        <p v-if="errors.email" class="text-[11px] text-rose-400 font-medium">{{ errors.email }}</p>
      </div>

      <div class="space-y-1">
        <PasswordInput
          v-model="password"
          label="Password"
          placeholder="Create password"
          required
        />
        <PasswordStrength :password="password" />
        <p v-if="errors.password" class="text-[11px] text-rose-400 font-medium">{{ errors.password }}</p>
      </div>

      <div class="space-y-1">
        <PasswordInput
          v-model="confirmPassword"
          label="Confirm Password"
          placeholder="Confirm password"
          required
        />
        <p v-if="confirmPassword && !passwordsMatch" class="text-[11px] text-rose-400 font-medium">Passwords do not match</p>
      </div>

      <!-- Country Selection -->
      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Country</label>
        <select
          v-model="country"
          required
          class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-slate-100 outline-none focus:border-indigo-500 transition text-xs font-medium"
        >
          <option value="IN">India (+5:30 IST)</option>
          <option value="US">United States (EST/PST)</option>
          <option value="GB">United Kingdom (GMT/BST)</option>
          <option value="AE">United Arab Emirates (GST)</option>
          <option value="SG">Singapore (SGT)</option>
          <option value="AU">Australia (AEST)</option>
          <option value="CA">Canada (EST/PST)</option>
          <option value="DE">Germany (CET)</option>
        </select>
      </div>

      <!-- Target Role selection -->
      <RoleSelect v-model="targetRole" />
      <p v-if="errors.targetRole" class="text-[11px] text-rose-400 font-medium">{{ errors.targetRole }}</p>

      <!-- Experience Level -->
      <ExperienceSelect v-model="experienceLevel" />
      <p v-if="errors.experienceLevel" class="text-[11px] text-rose-400 font-medium">{{ errors.experienceLevel }}</p>

      <!-- Programming Languages -->
      <LanguageSelect v-model="programmingLanguages" />



      <!-- Terms Checkbox -->
      <div class="space-y-1">
        <label class="flex items-start gap-2 cursor-pointer text-slate-300 text-xs select-none">
          <input v-model="termsAccepted" type="checkbox" class="mt-0.5 rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-indigo-500" />
          <span>I agree to the Terms of Service and Privacy Policy</span>
        </label>
        <p v-if="errors.termsAccepted" class="text-[11px] text-rose-400 font-medium">{{ errors.termsAccepted }}</p>
      </div>

      <button
        type="submit"
        :disabled="authStore.isLoading"
        class="w-full btn-primary py-3 font-bold flex items-center justify-center gap-2 text-sm shadow-lg shadow-indigo-600/30"
      >
        <Loader2 v-if="authStore.isLoading" class="w-4 h-4 animate-spin" />
        <UserPlus v-else class="w-4 h-4" />
        <span>{{ authStore.isLoading ? 'Creating account...' : 'Create Account' }}</span>
      </button>
    </form>

    <div class="text-center text-xs text-slate-400">
      Already have an account?
      <router-link to="/login" class="text-indigo-400 font-bold hover:underline">Login</router-link>
    </div>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { UserPlus, Loader2, CheckCircle2, ArrowLeft } from 'lucide-vue-next'
import { useAuthStore } from '../stores/authStore'
import AuthLayout from '../components/auth/AuthLayout.vue'
import PasswordInput from '../components/auth/PasswordInput.vue'
import PasswordStrength from '../components/auth/PasswordStrength.vue'
import RoleSelect from '../components/auth/RoleSelect.vue'
import ExperienceSelect from '../components/auth/ExperienceSelect.vue'
import LanguageSelect from '../components/auth/LanguageSelect.vue'
import GoogleLoginButton from '../components/auth/GoogleLoginButton.vue'
import { api } from '../services/api'

const router = useRouter()
const authStore = useAuthStore()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const country = ref('IN')
const targetRole = ref('')
const experienceLevel = ref('')
const programmingLanguages = ref<string[]>([])
const termsAccepted = ref(false)

const requiresOtp = ref(false)
const otpCode = ref('')
const isVerifyingOtp = ref(false)
const otpError = ref('')

const errors = ref<Record<string, string>>({})

const passwordsMatch = computed(() => password.value === confirmPassword.value)

const validateForm = (): boolean => {
  errors.value = {}
  if (!name.value.trim()) errors.value.name = 'Please enter your full name.'
  
  const emailRegex = /^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$/
  const trimmedEmail = email.value ? email.value.trim().toLowerCase() : ''
  if (!trimmedEmail || !emailRegex.test(trimmedEmail)) {
    errors.value.email = 'Please enter a valid email address (e.g. user@example.com).'
  }

  if (!password.value) {
    errors.value.password = 'Password is required.'
  }

  if (!passwordsMatch.value) {
    errors.value.confirmPassword = 'Passwords do not match.'
  }

  if (!targetRole.value) {
    errors.value.targetRole = 'Please select your target role.'
  }

  if (!experienceLevel.value) {
    errors.value.experienceLevel = 'Please select your experience level.'
  }

  if (!termsAccepted.value) {
    errors.value.termsAccepted = 'Please accept the Terms and Privacy Policy.'
  }

  return Object.keys(errors.value).length === 0
}

const resendCooldown = ref(0)
const expirySeconds = ref(600) // 10 minutes
let cooldownInterval: any = null
let expiryInterval: any = null

const formattedExpiryTimer = computed(() => {
  const m = Math.floor(expirySeconds.value / 60)
  const s = expirySeconds.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

const startTimers = () => {
  resendCooldown.value = 60
  expirySeconds.value = 600

  clearInterval(cooldownInterval)
  clearInterval(expiryInterval)

  cooldownInterval = setInterval(() => {
    if (resendCooldown.value > 0) resendCooldown.value--
    else clearInterval(cooldownInterval)
  }, 1000)

  expiryInterval = setInterval(() => {
    if (expirySeconds.value > 0) expirySeconds.value--
    else clearInterval(expiryInterval)
  }, 1000)
}

const handleRegister = async () => {
  if (!validateForm()) return

  try {
    await authStore.register({
      name: name.value.trim(),
      email: email.value.trim().toLowerCase(),
      password: password.value,
      target_role: targetRole.value,
      experience_level: experienceLevel.value,
      programming_languages: programmingLanguages.value,
      terms_accepted: termsAccepted.value
    })
    requiresOtp.value = true
    startTimers()
  } catch (err: any) {
    // Auth store handles setting error message
  }
}

const handleResendOtp = async () => {
  if (resendCooldown.value > 0 || !email.value) return
  isVerifyingOtp.value = true
  otpError.value = ''
  try {
    await api.post('/api/auth/send-otp', { email: email.value.trim().toLowerCase() })
    startTimers()
  } catch (err: any) {
    otpError.value = err.response?.data?.detail || 'Failed to resend verification code.'
  } finally {
    isVerifyingOtp.value = false
  }
}

const handleVerifyOtp = async () => {
  if (otpCode.value.length !== 6) return
  isVerifyingOtp.value = true
  otpError.value = ''
  try {
    await api.post('/api/auth/verify-email', {
      email: email.value.trim().toLowerCase(),
      otp: otpCode.value.trim()
    })
    // Redirect to login page with success notification and pre-filled email
    router.push({
      path: '/login',
      query: { registered: 'true', email: email.value.trim().toLowerCase() }
    })
  } catch (err: any) {
    otpError.value = err.response?.data?.detail || 'Invalid or expired OTP code.'
  } finally {
    isVerifyingOtp.value = false
  }
}

const handleGoogleGISSuccess = async (credentialToken: string) => {
  try {
    const res = await api.post('/api/auth/google', {
      credential: credentialToken
    })
    authStore.handleGoogleCallback(res.data.access_token)
    await authStore.fetchCurrentUser()
    router.push('/dashboard')
  } catch (err: any) {
    authStore.error = err.response?.data?.detail || 'Google authentication failed'
  }
}

const handleGoogleGISError = (errMessage: string) => {
  authStore.error = errMessage
}
</script>
