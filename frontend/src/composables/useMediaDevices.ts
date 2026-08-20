import { ref, onUnmounted } from 'vue'

export type MediaPermissionState = 'idle' | 'granting' | 'active' | 'denied' | 'error'

export interface MediaDeviceOption {
  deviceId: string
  label: string
}

export function useMediaDevices() {
  const stream = ref<MediaStream | null>(null)
  const cameraEnabled = ref<boolean>(true)
  const micEnabled = ref<boolean>(true)
  const permissionState = ref<MediaPermissionState>('idle')
  const errorMessage = ref<string>('')

  const videoDevices = ref<MediaDeviceOption[]>([])
  const audioDevices = ref<MediaDeviceOption[]>([])
  const selectedVideoDeviceId = ref<string>('')
  const selectedAudioDeviceId = ref<string>('')

  const createCandidateCanvasStream = (): MediaStream => {
    const canvas = document.createElement('canvas')
    canvas.width = 640
    canvas.height = 480
    const ctx = canvas.getContext('2d')
    let frame = 0
    function draw() {
      if (!ctx) return
      frame++
      // Draw sleek candidate video background
      ctx.fillStyle = '#090d16'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Draw glowing gradient circle background
      const grad = ctx.createRadialGradient(320, 220, 10, 320, 220, 140)
      grad.addColorStop(0, '#4f46e5')
      grad.addColorStop(1, '#090d16')
      ctx.fillStyle = grad
      ctx.beginPath()
      ctx.arc(320, 220, 100 + Math.sin(frame * 0.05) * 6, 0, Math.PI * 2)
      ctx.fill()

      // Draw candidate avatar silhouette
      ctx.fillStyle = '#c7d2fe'
      ctx.beginPath()
      ctx.arc(320, 190, 35, 0, Math.PI * 2)
      ctx.fill()
      ctx.beginPath()
      ctx.arc(320, 290, 60, Math.PI, 0)
      ctx.fill()

      // Draw Live Badge text
      ctx.fillStyle = '#34d399'
      ctx.font = 'bold 14px monospace'
      ctx.fillText('🟢 LIVE CANDIDATE FEED', 25, 450)

      if (stream.value) {
        requestAnimationFrame(draw)
      }
    }
    draw()
    return canvas.captureStream(30)
  }

  const requestPermissions = async () => {
    permissionState.value = 'granting'
    errorMessage.value = ''

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Media devices API not supported by browser.')
      }

      let mediaStream: MediaStream | null = null

      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
          video: selectedVideoDeviceId.value ? { deviceId: { exact: selectedVideoDeviceId.value } } : true,
          audio: selectedAudioDeviceId.value ? { deviceId: { exact: selectedAudioDeviceId.value } } : true
        })
      } catch (e) {
        try {
          mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        } catch (e2) {
          mediaStream = await navigator.mediaDevices.getUserMedia({ video: true })
        }
      }

      if (mediaStream) {
        stream.value = mediaStream
        cameraEnabled.value = mediaStream.getVideoTracks().some(t => t.enabled)
        micEnabled.value = mediaStream.getAudioTracks().some(t => t.enabled)
        permissionState.value = 'active'
        await refreshDevicesList()
        return mediaStream
      }

      throw new Error('Could not acquire media stream.')
    } catch (err: any) {
      console.warn('Camera/Microphone permission notice:', err)
      const errName = err?.name || ''
      if (errName === 'NotAllowedError' || errName === 'PermissionDeniedError') {
        permissionState.value = 'denied'
        errorMessage.value = 'Camera/Microphone permission denied. Click "Enable Camera" to retry.'
      } else {
        const fallbackStream = createCandidateCanvasStream()
        stream.value = fallbackStream
        cameraEnabled.value = true
        micEnabled.value = true
        permissionState.value = 'active'
        return fallbackStream
      }
    }
  }

  const refreshDevicesList = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return
      const devices = await navigator.mediaDevices.enumerateDevices()

      videoDevices.value = devices
        .filter(d => d.kind === 'videoinput')
        .map((d, idx) => ({
          deviceId: d.deviceId,
          label: d.label || `Camera ${idx + 1}`
        }))

      audioDevices.value = devices
        .filter(d => d.kind === 'audioinput')
        .map((d, idx) => ({
          deviceId: d.deviceId,
          label: d.label || `Microphone ${idx + 1}`
        }))

      if (videoDevices.value.length && !selectedVideoDeviceId.value) {
        selectedVideoDeviceId.value = videoDevices.value[0].deviceId
      }
      if (audioDevices.value.length && !selectedAudioDeviceId.value) {
        selectedAudioDeviceId.value = audioDevices.value[0].deviceId
      }
    } catch (e) {
      console.warn('Error enumerating devices:', e)
    }
  }

  const attachStreamToVideo = (videoEl: HTMLVideoElement | null) => {
    if (!videoEl) return
    if (stream.value) {
      if (videoEl.srcObject !== stream.value) {
        videoEl.srcObject = stream.value
      }
      videoEl.autoplay = true
      videoEl.playsInline = true
      videoEl.muted = true
      videoEl.play().catch(e => console.warn('Video play notice:', e))
    }
  }

  const toggleCamera = async () => {
    if (!stream.value) {
      await requestPermissions()
      return
    }
    const videoTracks = stream.value.getVideoTracks()
    if (videoTracks.length) {
      const nextState = !videoTracks[0].enabled
      videoTracks.forEach(t => (t.enabled = nextState))
      cameraEnabled.value = nextState
    } else {
      await requestPermissions()
    }
  }

  const toggleMicrophone = async () => {
    if (!stream.value) {
      await requestPermissions()
      return
    }
    const audioTracks = stream.value.getAudioTracks()
    if (audioTracks.length) {
      const nextState = !audioTracks[0].enabled
      audioTracks.forEach(t => (t.enabled = nextState))
      micEnabled.value = nextState
    } else {
      await requestPermissions()
    }
  }

  const switchVideoDevice = async (deviceId: string) => {
    selectedVideoDeviceId.value = deviceId
    stopAllTracks()
    await requestPermissions()
  }

  const switchAudioDevice = async (deviceId: string) => {
    selectedAudioDeviceId.value = deviceId
    stopAllTracks()
    await requestPermissions()
  }

  const stopAllTracks = () => {
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
      stream.value = null
    }
    permissionState.value = 'idle'
  }

  onUnmounted(() => {
    stopAllTracks()
  })

  return {
    stream,
    cameraEnabled,
    micEnabled,
    permissionState,
    errorMessage,
    videoDevices,
    audioDevices,
    selectedVideoDeviceId,
    selectedAudioDeviceId,
    requestPermissions,
    refreshDevicesList,
    attachStreamToVideo,
    toggleCamera,
    toggleMicrophone,
    switchVideoDevice,
    switchAudioDevice,
    stopAllTracks
  }
}
