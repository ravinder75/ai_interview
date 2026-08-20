<template>
  <div class="flex items-center gap-1.5 h-8 px-3 rounded-lg bg-slate-950 border border-slate-800">
    <span class="text-[11px] font-bold text-slate-400 mr-2 flex items-center gap-1">
      <span class="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
      Voice Mic Level
    </span>
    <div
      v-for="(bar, index) in bars"
      :key="index"
      class="w-1.5 bg-gradient-to-t from-indigo-500 via-purple-500 to-rose-400 rounded-full transition-all duration-75"
      :style="{ height: `${bar}px` }"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  isListening: boolean
}>()

const bars = ref<number[]>([4, 6, 8, 12, 8, 6, 4])
let audioCtx: AudioContext | null = null
let analyser: AnalyserNode | null = null
let mediaStream: MediaStream | null = null
let animationFrameId: number | null = null

const startAudioVisualization = async () => {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)()
    analyser = audioCtx.createAnalyser()
    analyser.fftSize = 32

    const source = audioCtx.createMediaStreamSource(mediaStream)
    source.connect(analyser)

    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)

    const updateBars = () => {
      if (!analyser || !props.isListening) return
      analyser.getByteFrequencyData(dataArray)

      // Sample frequency spectrum to compute bar heights (min 4px, max 28px)
      const newBars: number[] = []
      const step = Math.floor(bufferLength / 7)
      for (let i = 0; i < 7; i++) {
        const val = dataArray[i * step] || 0
        const height = Math.max(4, Math.min(28, (val / 255) * 28 + 4))
        newBars.push(height)
      }
      bars.value = newBars
      animationFrameId = requestAnimationFrame(updateBars)
    }

    updateBars()
  } catch (err) {
    console.warn('Audio visualization mic access error:', err)
  }
}

const stopAudioVisualization = () => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  if (audioCtx) {
    audioCtx.close()
    audioCtx = null
  }
  bars.value = [4, 6, 8, 12, 8, 6, 4]
}

onMounted(() => {
  if (props.isListening) {
    startAudioVisualization()
  }
})

onUnmounted(() => {
  stopAudioVisualization()
})
</script>
