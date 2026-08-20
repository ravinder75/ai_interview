<template>
  <div class="space-y-1">
    <div v-if="label" class="flex justify-between text-xs font-semibold text-slate-300">
      <span>{{ label }}</span>
      <span class="text-indigo-400 font-bold">{{ progress }}%</span>
    </div>
    <div class="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
      <div
        class="bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-400 h-full rounded-full transition-all duration-500"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  progress: number;
  label?: string;
}>()
</script>
