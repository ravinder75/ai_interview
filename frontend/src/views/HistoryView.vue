<template>
  <div class="max-w-5xl mx-auto space-y-6 py-2">
    <InterviewHistory :sessions="interviewStore.sessionHistory" />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useInterviewStore } from '../stores/interviewStore'
import InterviewHistory from '../components/InterviewHistory.vue'

const interviewStore = useInterviewStore()

onMounted(() => {
  interviewStore.fetchHistory()
})
</script>
