<template>
  <div v-if="password" class="space-y-2 mt-2">
    <div class="flex items-center justify-between text-[11px]">
      <span class="text-slate-400">Password strength:</span>
      <span :class="strengthClass" class="font-bold uppercase tracking-wider">{{ strengthLabel }}</span>
    </div>

    <!-- Progress bar -->
    <div class="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden flex gap-1">
      <div
        class="h-full transition-all duration-300 rounded-full"
        :class="barColor"
        :style="{ width: `${(score / 5) * 100}%` }"
      ></div>
    </div>

    <!-- Criteria Checklist -->
    <div class="grid grid-cols-2 gap-1 text-[10px] text-slate-400 pt-1">
      <div :class="checks.length ? 'text-emerald-400 font-medium' : ''" class="flex items-center gap-1">
        <span>{{ checks.length ? '✓' : '○' }}</span> 8+ characters
      </div>
      <div :class="checks.upper ? 'text-emerald-400 font-medium' : ''" class="flex items-center gap-1">
        <span>{{ checks.upper ? '✓' : '○' }}</span> Uppercase letter
      </div>
      <div :class="checks.lower ? 'text-emerald-400 font-medium' : ''" class="flex items-center gap-1">
        <span>{{ checks.lower ? '✓' : '○' }}</span> Lowercase letter
      </div>
      <div :class="checks.number ? 'text-emerald-400 font-medium' : ''" class="flex items-center gap-1">
        <span>{{ checks.number ? '✓' : '○' }}</span> Number
      </div>
      <div :class="checks.special ? 'text-emerald-400 font-medium' : ''" class="flex items-center gap-1 col-span-2">
        <span>{{ checks.special ? '✓' : '○' }}</span> Special character (!@#$%^&*)
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  password: string
}>()

const checks = computed(() => ({
  length: props.password.length >= 8,
  upper: /[A-Z]/.test(props.password),
  lower: /[a-z]/.test(props.password),
  number: /\d/.test(props.password),
  special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]/.test(props.password),
}))

const score = computed(() => {
  let s = 0
  if (checks.value.length) s++
  if (checks.value.upper) s++
  if (checks.value.lower) s++
  if (checks.value.number) s++
  if (checks.value.special) s++
  return s
})

const strengthLabel = computed(() => {
  if (score.value <= 2) return 'Weak'
  if (score.value <= 4) return 'Medium'
  return 'Strong'
})

const strengthClass = computed(() => {
  if (score.value <= 2) return 'text-rose-400'
  if (score.value <= 4) return 'text-amber-400'
  return 'text-emerald-400'
})

const barColor = computed(() => {
  if (score.value <= 2) return 'bg-rose-500'
  if (score.value <= 4) return 'bg-amber-500'
  return 'bg-emerald-500'
})
</script>
