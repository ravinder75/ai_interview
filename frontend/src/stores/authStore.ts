import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../services/api'
import type { User, RegisterData, TokenResponse } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // ── Initialize ──
  const initializeAuth = async () => {
    const stored = localStorage.getItem('token')
    if (stored) {
      token.value = stored
      try {
        await fetchCurrentUser()
      } catch {
        logout()
      }
    }
  }

  // ── Register ──
  const register = async (data: RegisterData): Promise<boolean> => {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.post<TokenResponse>('/api/auth/register', data)
      token.value = res.data.access_token
      user.value = res.data.user
      localStorage.setItem('token', res.data.access_token)
      return true
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        error.value = detail.map((d: any) => d.msg || d).join('. ')
      } else {
        error.value = detail || 'Registration failed. Please try again.'
      }
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // ── Login ──
  const login = async (email: string, password: string): Promise<boolean> => {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.post<TokenResponse>('/api/auth/login', { email, password })
      token.value = res.data.access_token
      user.value = res.data.user
      localStorage.setItem('token', res.data.access_token)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Invalid email or password.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // ── Google Login ──
  const loginWithGoogle = () => {
    // Redirect to backend Google OAuth endpoint
    const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005'
    window.location.href = `${backendUrl}/api/auth/google`
  }

  // ── Handle Google Callback Token ──
  const handleGoogleCallback = (accessToken: string) => {
    token.value = accessToken
    localStorage.setItem('token', accessToken)
  }

  // ── Fetch Current User ──
  const fetchCurrentUser = async () => {
    if (!token.value) return
    try {
      const res = await api.get<User>('/api/auth/me')
      user.value = res.data
    } catch {
      logout()
    }
  }

  // ── Update Profile & Picture ──
  const updateProfile = async (profileData: { full_name?: string; target_role?: string; experience_level?: string; profile_picture?: string }) => {
    isLoading.value = true
    try {
      const res = await api.put<User>('/api/auth/profile', profileData)
      user.value = res.data
      return res.data
    } finally {
      isLoading.value = false
    }
  }

  // ── Logout ──
  const logout = async () => {
    try {
      if (token.value) {
        await api.post('/api/auth/logout').catch(() => {})
      }
    } finally {
      token.value = null
      user.value = null
      error.value = null
      localStorage.clear()
      sessionStorage.clear()

      try {
        const { useInterviewBitStore } = await import('./interviewBit')
        useInterviewBitStore().resetState()
      } catch (e) {
        console.warn('Store reset error:', e)
      }
    }
  }

  // ── Forgot Password ──
  const forgotPassword = async (email: string): Promise<string> => {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.post('/api/auth/forgot-password', { email })
      return res.data.message
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Something went wrong.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // ── Reset Password ──
  const resetPassword = async (resetToken: string, newPassword: string): Promise<string> => {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.post('/api/auth/reset-password', {
        token: resetToken,
        new_password: newPassword,
      })
      return res.data.message
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to reset password.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    initializeAuth,
    register,
    login,
    loginWithGoogle,
    handleGoogleCallback,
    fetchCurrentUser,
    updateProfile,
    logout,
    forgotPassword,
    resetPassword,
  }
})
