import { ref, onUnmounted } from 'vue'

export function useWebSocket(sessionId: string) {
  const isConnected = ref<boolean>(false)
  const lastMessage = ref<any>(null)
  let socket: WebSocket | null = null

  const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8005'

  const connect = () => {
    if (!sessionId) return
    const wsUrl = `${WS_BASE_URL}/ws/interview/${sessionId}`
    socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      isConnected.value = true
      console.log(`WebSocket connected to ${wsUrl}`)
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        lastMessage.value = data
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err)
      }
    }

    socket.onerror = (err) => {
      console.error('WebSocket connection error:', err)
    }

    socket.onclose = () => {
      isConnected.value = false
      console.log(`WebSocket closed for session ${sessionId}`)
    }
  }

  const send = (data: any) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(data))
    }
  }

  const disconnect = () => {
    if (socket) {
      socket.close()
      socket = null
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    lastMessage,
    connect,
    send,
    disconnect
  }
}
