<template>
  <div class="flex min-h-screen bg-slate-950 text-slate-100 font-sans relative overflow-x-hidden">
    <!-- Sidebar component with mobile drawer support -->
    <Sidebar v-if="!isAuthPage" :isOpen="isMobileOpen" @close="isMobileOpen = false" />
    
    <div class="flex-1 flex flex-col min-w-0">
      <TopBar v-if="!isAuthPage" @toggle-sidebar="isMobileOpen = !isMobileOpen" />
      <main class="flex-1 p-3 sm:p-6 overflow-y-auto max-w-full">
        <slot></slot>
      </main>
    </div>

    <!-- Global Floating Interview Bit AI Assistant (Admin Only) -->
    <InterviewBitWidget v-if="!isAuthPage && isAdminUser" />

    <!-- Global Floating Draggable Active Live Interview Card -->
    <FloatingLiveInterviewCard v-if="!isAuthPage" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
import InterviewBitWidget from './interview-bit/InterviewBitWidget.vue'
import FloatingLiveInterviewCard from './interview/FloatingLiveInterviewCard.vue'
import { useAuthStore } from '../stores/authStore'

const route = useRoute()
const authStore = useAuthStore()
const isMobileOpen = ref<boolean>(false)

// Close mobile drawer on route change
watch(() => route.path, () => {
  isMobileOpen.value = false
})

onMounted(() => {
  authStore.initializeAuth()
})

const isAuthPage = computed(() => ['/login', '/register', '/forgot-password', '/reset-password'].includes(route.path))
const isAdminUser = computed(() => authStore.user?.email?.toLowerCase() === 'ravinderkama14@gmail.com')
</script>
