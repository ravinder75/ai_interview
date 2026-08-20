<template>
  <div class="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
    <div class="flex items-center justify-between">
      <span class="text-xs font-bold uppercase tracking-wider text-indigo-400">
        Question {{ questionOrder }}
      </span>
      <div class="flex items-center gap-2">
        <button
          @click="speakQuestion"
          :class="[
            'p-2 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition',
            isSpeaking
              ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300 animate-pulse'
              : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'
          ]"
          :title="isSpeaking ? 'Stop Voice' : 'Listen AI Question Voice'"
        >
          <Volume2 class="w-4 h-4" />
          <span>{{ isSpeaking ? 'Speaking...' : 'Listen Voice' }}</span>
        </button>
        <span class="px-2.5 py-1 bg-slate-800 rounded-lg text-xs font-semibold text-slate-300">
          {{ category }}
        </span>
      </div>
    </div>

    <p class="text-xl font-semibold text-slate-100 leading-relaxed">
      "{{ questionText }}"
    </p>

    <div v-if="keyAspects && keyAspects.length" class="pt-2 text-xs text-slate-400 space-y-1">
      <span class="font-semibold text-slate-300">Key Aspects to Address:</span>
      <div class="flex flex-wrap gap-1.5 pt-1">
        <span
          v-for="aspect in keyAspects"
          :key="aspect"
          class="px-2.5 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[11px]"
        >
          • {{ aspect }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Volume2 } from 'lucide-vue-next'

const props = defineProps<{
  questionOrder: number;
  category: string;
  questionText: string;
  keyAspects?: string[];
}>()

const isSpeaking = ref<boolean>(false)

const speakQuestion = () => {
  if (!('speechSynthesis' in window)) {
    alert('Voice speech synthesis is not supported by your browser.')
    return
  }

  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel()
    isSpeaking.value = false
    return
  }

  const utterance = new SpeechSynthesisUtterance(props.questionText)
  utterance.rate = 0.95
  utterance.pitch = 1.0

  utterance.onstart = () => {
    isSpeaking.value = true
  }

  utterance.onend = () => {
    isSpeaking.value = false
  }

  utterance.onerror = () => {
    isSpeaking.value = false
  }

  window.speechSynthesis.speak(utterance)
}

watch(() => props.questionText, (newText) => {
  if (newText) {
    speakQuestion()
  }
})

onMounted(() => {
  if (props.questionText) {
    speakQuestion()
  }
})
</script>
