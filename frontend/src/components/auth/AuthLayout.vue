<template>
  <div class="min-h-screen flex items-center justify-center p-3 sm:p-6 bg-slate-950 overflow-y-auto py-8">
    <div class="glass-card rounded-2xl p-4 sm:p-8 border border-slate-800 w-full max-w-lg space-y-5 sm:space-y-6 shadow-2xl my-auto">
      <div class="text-center space-y-1.5 sm:space-y-2">
        <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 mx-auto flex items-center justify-center text-white font-bold text-lg sm:text-xl shadow-lg shadow-indigo-500/30">
          <slot name="logo">
            <Bot class="w-6 h-6 sm:w-7 sm:h-7" />
          </slot>
        </div>
        <h2 class="text-xl sm:text-2xl font-bold text-slate-100">{{ title }}</h2>
        <p v-if="subtitle" class="text-[11px] sm:text-xs text-slate-400 max-w-xs sm:max-w-none mx-auto">{{ subtitle }}</p>
      </div>

      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Bot } from 'lucide-vue-next'

defineProps<{
  title: string
  subtitle?: string
}>()
</script>
