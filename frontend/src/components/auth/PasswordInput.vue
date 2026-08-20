<template>
  <div class="space-y-1">
    <label v-if="label" class="font-semibold text-slate-300 text-xs block">{{ label }}</label>
    <div class="relative">
      <input
        :value="modelValue"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        :type="showPassword ? 'text' : 'password'"
        :placeholder="placeholder || '••••••••'"
        :required="required"
        class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 pr-10 text-slate-100 text-xs placeholder-slate-500 outline-none focus:border-indigo-500 transition"
      />
      <button
        type="button"
        @click="showPassword = !showPassword"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 transition focus:outline-none"
        :title="showPassword ? 'Hide password' : 'Show password'"
      >
        <EyeOff v-if="showPassword" class="w-4 h-4" />
        <Eye v-else class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Eye, EyeOff } from 'lucide-vue-next'

defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
  required?: boolean
}>()

defineEmits(['update:modelValue'])

const showPassword = ref(false)
</script>
