import { ref, onUnmounted } from 'vue'

export function useAudioLevel() {
  const audioLevel = ref<number>(0) // 0 to 100%
  const decibels = ref<number>(-100)
  const isWeakSignal = ref<boolean>(false)
  const bars = ref<number[]>([10, 10, 10, 10, 10, 10, 10, 10, 10, 10])

  let audioCtx: AudioContext | null = null
  let analyser: AnalyserNode | null = null
  let sourceNode: MediaStreamAudioSourceNode | null = null
  let animId: number | null = null

  const startAnalyser = (stream: MediaStream | null, active: boolean = true) => {
    stopAnalyser()
    if (!stream || !active) return

    const audioTracks = stream.getAudioTracks()
    if (!audioTracks.length || !audioTracks[0].enabled) return

    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext
      audioCtx = new AudioCtx()
      analyser = audioCtx.createAnalyser()
      analyser.fftSize = 64
      analyser.smoothingTimeConstant = 0.8

      sourceNode = audioCtx.createMediaStreamSource(stream)
      sourceNode.connect(analyser)

      const bufferLength = analyser.frequencyBinCount
      const dataArray = new Uint8Array(bufferLength)

      const calculateVolume = () => {
        if (!analyser) return
        analyser.getByteFrequencyData(dataArray)

        let sum = 0
        for (let i = 0; i < bufferLength; i++) {
          sum += dataArray[i]
        }
        const average = sum / bufferLength
        const level = Math.min(100, Math.round((average / 128) * 100))
        audioLevel.value = level
        isWeakSignal.value = active && level < 5

        // Generate 10 visual bars
        const step = Math.floor(bufferLength / 10) || 1
        const newBars: number[] = []
        for (let b = 0; b < 10; b++) {
          const val = dataArray[b * step] || 0
          const barHeight = Math.max(10, Math.min(100, Math.round((val / 255) * 100)))
          newBars.push(barHeight)
        }
        bars.value = newBars

        animId = requestAnimationFrame(calculateVolume)
      }

      calculateVolume()
    } catch (e) {
      console.warn('useAudioLevel AudioContext error:', e)
    }
  }

  const stopAnalyser = () => {
    if (animId) {
      cancelAnimationFrame(animId)
      animId = null
    }
    if (sourceNode) {
      sourceNode.disconnect()
      sourceNode = null
    }
    if (audioCtx && audioCtx.state !== 'closed') {
      audioCtx.close().catch(() => {})
      audioCtx = null
    }
    analyser = null
    audioLevel.value = 0
    isWeakSignal.value = false
    bars.value = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
  }

  onUnmounted(() => {
    stopAnalyser()
  })

  return {
    audioLevel,
    decibels,
    isWeakSignal,
    bars,
    startAnalyser,
    stopAnalyser
  }
}
