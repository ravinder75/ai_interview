<template>
  <div class="space-y-1">
    <label class="font-semibold text-slate-300 text-xs block">Experience Level</label>
    <select
      :value="modelValue"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-slate-100 text-xs outline-none focus:border-indigo-500 transition"
    >
      <option value="" disabled>Select experience level</option>
      <option v-for="level in experienceLevels" :key="level" :value="level">{{ level }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
}>()

defineEmits(['update:modelValue'])

const experienceLevels = [
  'Fresher',
  'Student',
  'Intern',
  '0-1 Years',
  '1-3 Years',
  '3-5 Years',
  '5-8 Years',
  '8+ Years'
]
</script>
