import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../services/api'
import type { AppSettings } from '../types'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings>({
    app_name: 'Interview Coach AI',
    ai_provider: 'Omniroute OpenAI Compatible',
    ai_model: 'auto/coding:free',
    response_style: 'Professional',
    difficulty: 'Medium',
    speech_recognition: 'Web Speech API',
    theme: 'Dark',
    data_retention_days: 30,
    api_key_configured: true
  })

  const fetchSettings = async () => {
    try {
      const res = await api.get('/api/settings')
      settings.value = res.data
    } catch (err) {
      console.warn('Failed to fetch app settings:', err)
    }
  }

  const updateSettings = async (newSettings: Partial<AppSettings>) => {
    try {
      const res = await api.put('/api/settings', newSettings)
      settings.value = res.data
      return res.data
    } catch (err) {
      console.error('Failed to update app settings:', err)
      throw err
    }
  }

  return {
    settings,
    fetchSettings,
    updateSettings
  }
})
