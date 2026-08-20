<template>
  <AuthLayout title="Forgot Password" subtitle="Reset your password using a 6-digit OTP code sent to your email">
    <div v-if="step === 4" class="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs space-y-3 text-center">
      <p class="font-bold">Password changed successfully.</p>
      <router-link to="/login" class="inline-block btn-primary px-4 py-2 text-xs font-bold">
        Proceed to Login
      </router-link>
    </div>

    <!-- STEP 1: Enter Email -->
    <form v-else-if="step === 1" @submit.prevent="handleSendOtp" class="space-y-4 text-xs">
      <div v-if="errorMessage" class="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
        {{ errorMessage }}
      </div>

      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Email Address</label>
        <input
          v-model="email"
          type="email"
          required
          placeholder="you@example.com"
          class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500 transition"
        />
      </div>

      <button
        type="submit"
        :disabled="isLoading"
        class="w-full btn-primary py-3 font-bold flex items-center justify-center gap-2 text-sm shadow-lg shadow-indigo-600/30"
      >
        <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
        <Send v-else class="w-4 h-4" />
        <span>{{ isLoading ? 'Sending OTP...' : 'Send OTP' }}</span>
      </button>
    </form>

    <!-- STEP 2: Enter 6-digit OTP -->
    <form v-else-if="step === 2" @submit.prevent="handleVerifyOtp" class="space-y-4 text-xs">
      <div v-if="errorMessage" class="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
        {{ errorMessage }}
      </div>

      <div class="space-y-1">
        <div class="flex items-center justify-between">
          <label class="font-semibold text-slate-300">Enter 6-Digit OTP Code</label>
          <span class="text-[11px] font-mono text-indigo-400 font-bold">Expires in {{ formattedExpiryTimer }}</span>
        </div>
        <input
          v-model="otp"
          type="text"
          maxlength="6"
          required
          placeholder="123456"
          class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-500 transition text-center tracking-[8px] font-mono text-lg"
        />
        <div class="flex items-center justify-between text-[11px] text-slate-400 mt-1">
          <span>Sent to {{ email }}</span>
          <button
            type="button"
            @click="handleResendOtp"
            :disabled="resendCooldown > 0 || isLoading"
            class="text-indigo-400 font-bold hover:underline disabled:opacity-50 disabled:no-underline"
          >
            {{ resendCooldown > 0 ? `Resend OTP (${resendCooldown}s)` : 'Resend OTP' }}
          </button>
        </div>
      </div>

      <button
        type="submit"
        :disabled="isLoading || otp.length !== 6"
        class="w-full btn-primary py-3 font-bold flex items-center justify-center gap-2 text-sm shadow-lg shadow-indigo-600/30"
      >
        <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
        <CheckCircle2 v-else class="w-4 h-4" />
        <span>{{ isLoading ? 'Verifying...' : 'Verify OTP' }}</span>
      </button>

      <button
        type="button"
        @click="step = 1"
        class="w-full text-slate-400 hover:text-slate-200 text-xs py-1.5 flex items-center justify-center gap-1 transition"
      >
        <ArrowLeft class="w-3.5 h-3.5" />
        <span>Back to Change Email Address</span>
      </button>
    </form>

    <!-- STEP 3: Create New Password -->
    <form v-else-if="step === 3" @submit.prevent="handleResetPassword" class="space-y-4 text-xs">
      <div v-if="errorMessage" class="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
        {{ errorMessage }}
      </div>

      <div class="space-y-1">
        <PasswordInput
          v-model="newPassword"
          label="New Password"
          placeholder="Create new password"
          required
        />
        <PasswordStrength :password="newPassword" />
      </div>

      <div class="space-y-1">
        <PasswordInput
          v-model="confirmPassword"
          label="Confirm New Password"
          placeholder="Re-enter new password"
          required
        />
        <p v-if="confirmPassword && newPassword !== confirmPassword" class="text-[11px] text-rose-400 font-medium">
          Passwords do not match
        </p>
      </div>

      <button
        type="submit"
        :disabled="isLoading || newPassword !== confirmPassword"
        class="w-full btn-primary py-3 font-bold flex items-center justify-center gap-2 text-sm shadow-lg shadow-indigo-600/30"
      >
        <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
        <KeyRound v-else class="w-4 h-4" />
        <span>{{ isLoading ? 'Resetting...' : 'Reset Password' }}</span>
      </button>
    </form>

    <div v-if="step !== 4" class="text-center text-xs text-slate-400 pt-2">
      Remembered your password?
      <router-link to="/login" class="text-indigo-400 font-bold hover:underline">Back to Login</router-link>
    </div>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Send, Loader2, CheckCircle2, KeyRound, ArrowLeft } from 'lucide-vue-next'
import AuthLayout from '../../components/auth/AuthLayout.vue'
import PasswordInput from '../../components/auth/PasswordInput.vue'
import PasswordStrength from '../../components/auth/PasswordStrength.vue'
import { api } from '../../services/api'

const step = ref(1) // 1: Send OTP, 2: Verify OTP, 3: New Password, 4: Success
const email = ref('')
const otp = ref('')
const resetToken = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

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

const handleSendOtp = async () => {
  if (!email.value) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    await api.post('/api/auth/forgot-password', { email: email.value.trim().toLowerCase() })
    step.value = 2
    startTimers()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to send OTP.'
  } finally {
    isLoading.value = false
  }
}

const handleResendOtp = async () => {
  if (resendCooldown.value > 0 || !email.value) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    await api.post('/api/auth/forgot-password', { email: email.value.trim().toLowerCase() })
    startTimers()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to resend OTP.'
  } finally {
    isLoading.value = false
  }
}

const handleVerifyOtp = async () => {
  if (otp.value.length !== 6) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res = await api.post('/api/auth/verify-reset-otp', {
      email: email.value.trim().toLowerCase(),
      otp: otp.value.trim()
    })
    resetToken.value = res.data.reset_token
    step.value = 3
    clearInterval(cooldownInterval)
    clearInterval(expiryInterval)
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Invalid or expired OTP code.'
  } finally {
    isLoading.value = false
  }
}

const handleResetPassword = async () => {
  if (newPassword.value !== confirmPassword.value) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    await api.post('/api/auth/reset-password', {
      token: resetToken.value,
      new_password: newPassword.value
    })
    step.value = 4
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to reset password.'
  } finally {
    isLoading.value = false
  }
}
</script>
