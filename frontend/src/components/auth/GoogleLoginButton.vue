<template>
  <div class="w-full flex justify-center">
    <div id="googleSignInButton" ref="buttonContainer" class="w-full flex justify-center min-h-[44px]"></div>
    <button
      v-if="!gisLoaded"
      @click="handleFallbackGoogleLogin"
      type="button"
      class="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-bold flex items-center justify-center gap-2 transition"
    >
      <svg class="w-4 h-4" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
      </svg>
      <span>Continue with Google</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const emit = defineEmits(['success', 'error'])
const buttonContainer = ref<HTMLElement | null>(null)
const gisLoaded = ref(false)

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

const getGoogleObj = () => (window as any).google

const handleCredentialResponse = (response: any) => {
  if (response && response.credential) {
    emit('success', response.credential)
  } else {
    emit('error', 'No Google credential received')
  }
}

const handleFallbackGoogleLogin = () => {
  if (!googleClientId) {
    emit('error', 'Google OAuth Client ID is missing. Please add VITE_GOOGLE_CLIENT_ID to frontend/.env and GOOGLE_CLIENT_ID to backend/.env')
    return
  }
  const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005'
  window.location.href = `${backendUrl}/api/auth/google`
}

onMounted(() => {
  if (!googleClientId) {
    console.warn('VITE_GOOGLE_CLIENT_ID is not configured in frontend/.env')
    return
  }
  const initGis = () => {
    const g = getGoogleObj()
    if (g?.accounts?.id && buttonContainer.value) {
      gisLoaded.value = true
      g.accounts.id.initialize({
        client_id: googleClientId,
        callback: handleCredentialResponse,
        auto_select: false
      })

      g.accounts.id.renderButton(buttonContainer.value, {
        theme: 'outline',
        size: 'large',
        type: 'standard',
        shape: 'pill',
        text: 'continue_with',
        logo_alignment: 'left',
        width: 320
      })
    }
  }

  const g = getGoogleObj()
  if (g?.accounts?.id) {
    initGis()
  } else {
    let checkInterval = setInterval(() => {
      const gCheck = getGoogleObj()
      if (gCheck?.accounts?.id) {
        clearInterval(checkInterval)
        initGis()
      }
    }, 200)
    setTimeout(() => clearInterval(checkInterval), 4000)
  }
})
</script>
