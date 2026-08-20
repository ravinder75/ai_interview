<template>
  <AuthLayout title="Reset Password" subtitle="Create a new password for your account">
    <div v-if="successMessage" class="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs space-y-3 text-center">
      <p class="font-bold">{{ successMessage }}</p>
      <router-link to="/login" class="inline-block btn-primary px-4 py-2 text-xs font-bold">
        Proceed to Login
      </router-link>
    </div>

    <form v-else @submit.prevent="handleReset" class="space-y-4 text-xs">
      <div v-if="authStore.error" class="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
        {{ authStore.error }}
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
        :disabled="authStore.isLoading || newPassword !== confirmPassword"
        class="w-full btn-primary py-3 font-bold flex items-center justify-center gap-2 text-sm shadow-lg shadow-indigo-600/30"
      >
        <Loader2 v-if="authStore.isLoading" class="w-4 h-4 animate-spin" />
        <KeyRound v-else class="w-4 h-4" />
        <span>{{ authStore.isLoading ? 'Updating password...' : 'Reset Password' }}</span>
      </button>
    </form>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { KeyRound, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '../../stores/authStore'
import AuthLayout from '../../components/auth/AuthLayout.vue'
import PasswordInput from '../../components/auth/PasswordInput.vue'
import PasswordStrength from '../../components/auth/PasswordStrength.vue'

const route = useRoute()
const authStore = useAuthStore()

const token = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const successMessage = ref('')

onMounted(() => {
  token.value = (route.query.token as string) || ''
})

const handleReset = async () => {
  if (!token.value) {
    authStore.error = 'Invalid or missing reset token.'
    return
  }
  if (newPassword.value !== confirmPassword.value) return

  try {
    const msg = await authStore.resetPassword(token.value, newPassword.value)
    successMessage.value = msg
  } catch (err) {
    // Handled in store
  }
}
</script>
