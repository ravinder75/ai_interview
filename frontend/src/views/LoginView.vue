<template>
  <AuthLayout title="Welcome back" subtitle="Sign in to your candidate account">
    <!-- Google OAuth GIS Button -->
    <GoogleLoginButton @success="handleGoogleGISSuccess" @error="handleGoogleGISError" />

    <div class="flex items-center gap-3">
      <div class="flex-1 h-px bg-slate-800"></div>
      <span class="text-[10px] uppercase font-bold text-slate-500">OR</span>
      <div class="flex-1 h-px bg-slate-800"></div>
    </div>

    <!-- Success Banner from Registration OTP Verification -->
    <div v-if="successBanner" class="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 font-semibold text-center">
      {{ successBanner }}
    </div>

    <!-- Error Banner -->
    <div v-if="authStore.error" class="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
      {{ authStore.error }}
    </div>

    <!-- Login Form -->
    <form @submit.prevent="handleLogin" class="space-y-4 text-xs">
      <div class="space-y-1">
        <label class="font-semibold text-slate-300">Email</label>
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
          placeholder="Password"
          required
        />
        <p v-if="errors.password" class="text-[11px] text-rose-400 font-medium">{{ errors.password }}</p>
      </div>

      <div class="flex items-center justify-end">
        <router-link to="/forgot-password" class="text-indigo-400 hover:underline text-xs font-semibold">
          Forgot password?
        </router-link>
      </div>

      <button
        type="submit"
        :disabled="authStore.isLoading"
        class="w-full btn-primary py-3 font-bold flex items-center justify-center gap-2 text-sm shadow-lg shadow-indigo-600/30"
      >
        <Loader2 v-if="authStore.isLoading" class="w-4 h-4 animate-spin" />
        <LogIn v-else class="w-4 h-4" />
        <span>{{ authStore.isLoading ? 'Authenticating...' : 'Login' }}</span>
      </button>
    </form>

    <div class="text-center text-xs text-slate-400">
      Don't have an account?
      <router-link to="/register" class="text-indigo-400 font-bold hover:underline">Register</router-link>
    </div>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { LogIn, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '../stores/authStore'
import AuthLayout from '../components/auth/AuthLayout.vue'
import PasswordInput from '../components/auth/PasswordInput.vue'
import GoogleLoginButton from '../components/auth/GoogleLoginButton.vue'
import { api } from '../services/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const successBanner = ref('')
const errors = ref<Record<string, string>>({})

onMounted(() => {
  if (route.query.token) {
    const tokenStr = route.query.token as string
    authStore.handleGoogleCallback(tokenStr)
    authStore.fetchCurrentUser().then(() => {
      router.push('/dashboard')
    })
  }
  if (route.query.registered === 'true') {
    successBanner.value = 'Email verified successfully! Please log in to your account.'
  }
  if (route.query.email) {
    email.value = (route.query.email as string).toLowerCase()
  }
})

const validateForm = (): boolean => {
  errors.value = {}
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.value || !emailRegex.test(email.value)) {
    errors.value.email = 'Valid email required'
  }
  if (!password.value) {
    errors.value.password = 'Password required'
  }
  return Object.keys(errors.value).length === 0
}

const handleLogin = async () => {
  if (!validateForm()) return
  try {
    await authStore.login(email.value.trim().toLowerCase(), password.value)
    router.push('/dashboard')
  } catch (err: any) {
    // authStore handles error state
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
