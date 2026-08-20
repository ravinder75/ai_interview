<template>
  <div class="space-y-1">
    <label class="font-semibold text-slate-300 text-xs block">Preferred Programming Languages (Optional)</label>
    <div class="flex flex-wrap gap-1.5 pt-1">
      <button
        v-for="lang in availableLanguages"
        :key="lang"
        type="button"
        @click="toggleLang(lang)"
        :class="[
          'px-2.5 py-1 rounded-lg text-xs font-semibold transition flex items-center gap-1',
          modelValue.includes(lang)
            ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
            : 'bg-slate-900 border border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
        ]"
      >
        <span>{{ lang }}</span>
        <span v-if="modelValue.includes(lang)" class="text-[10px]">✓</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: string[]
}>()

const emit = defineEmits(['update:modelValue'])

const availableLanguages = [
  'Python', 'Java', 'JavaScript', 'TypeScript',
  'C', 'C++', 'C#', 'Go', 'Rust', 'PHP',
  'Kotlin', 'Swift', 'Dart'
]

const toggleLang = (lang: string) => {
  const current = [...props.modelValue]
  const idx = current.indexOf(lang)
  if (idx >= 0) {
    current.splice(idx, 1)
  } else {
    current.push(lang)
  }
  emit('update:modelValue', current)
}
</script>
