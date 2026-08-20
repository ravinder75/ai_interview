import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import DashboardView from '../views/DashboardView.vue'
import PracticeView from '../views/PracticeView.vue'
import MockInterviewView from '../views/MockInterviewView.vue'
import CodingView from '../views/CodingView.vue'
import ResumeView from '../views/ResumeView.vue'
import JobAnalysisView from '../views/JobAnalysisView.vue'
import HistoryView from '../views/HistoryView.vue'
import SettingsView from '../views/SettingsView.vue'
import ChatbotView from '../views/ChatbotView.vue'
import InterviewBitView from '../views/InterviewBit.vue'
import InterviewScheduleView from '../views/InterviewSchedule.vue'
import LiveInterviewView from '../views/LiveInterview.vue'
import InterviewResultView from '../views/InterviewResult.vue'
import DeviceCheckView from '../views/DeviceCheckView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ForgotPasswordView from '../views/auth/ForgotPassword.vue'
import ResetPasswordView from '../views/auth/ResetPassword.vue'

import PricingView from '../views/PricingView.vue'
import FeaturesView from '../views/FeaturesView.vue'
import AboutUsView from '../views/AboutUsView.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: DashboardView, meta: { requiresAuth: true } },
  { path: '/device-check', name: 'DeviceCheck', component: DeviceCheckView, meta: { requiresAuth: true } },
  { path: '/interview-schedule', name: 'InterviewSchedule', component: InterviewScheduleView, meta: { requiresAuth: true } },
  { path: '/interview-schedule/:interviewId/live', name: 'LiveInterview', component: LiveInterviewView, meta: { requiresAuth: true } },
  { path: '/interview-schedule/:interviewId/result', name: 'InterviewResult', component: InterviewResultView, meta: { requiresAuth: true } },
  { path: '/pricing', name: 'Pricing', component: PricingView },
  { path: '/features', name: 'Features', component: FeaturesView },
  { path: '/about', name: 'AboutUs', component: AboutUsView },
  { path: '/practice', name: 'Practice', component: PracticeView, meta: { requiresAuth: true } },
  { path: '/mock-interview', name: 'MockInterview', component: MockInterviewView, meta: { requiresAuth: true } },
  { path: '/mock-interview/:sessionId/report', name: 'MockInterviewReportBySessionId', component: InterviewResultView, meta: { requiresAuth: true } },
  { path: '/mock-interview/report/:sessionId', name: 'MockInterviewReport', component: InterviewResultView, meta: { requiresAuth: true } },
  { path: '/interview-bit', name: 'InterviewBit', component: InterviewBitView, meta: { requiresAuth: true } },
  { path: '/coding', name: 'Coding', component: CodingView, meta: { requiresAuth: true } },
  { path: '/resume', name: 'Resume', component: ResumeView, meta: { requiresAuth: true } },
  { path: '/resume/dashboard', redirect: '/resume?tab=dashboard' },
  { path: '/resume/analyzer', redirect: '/resume?tab=analyzer' },
  { path: '/resume/editor', redirect: '/resume?tab=editor' },
  { path: '/resume/templates', redirect: '/resume?tab=templates' },
  { path: '/resume/export', redirect: '/resume?tab=export' },
  { path: '/job-analysis', name: 'JobAnalysis', component: JobAnalysisView, meta: { requiresAuth: true } },
  { path: '/history', name: 'History', component: HistoryView, meta: { requiresAuth: true } },
  { path: '/chatbot', name: 'Chatbot', component: ChatbotView, meta: { requiresAuth: true } },
  { path: '/settings', name: 'Settings', component: SettingsView, meta: { requiresAuth: true } },
  { path: '/login', name: 'Login', component: LoginView, meta: { guestOnly: true } },
  { path: '/register', name: 'Register', component: RegisterView, meta: { guestOnly: true } },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPasswordView, meta: { guestOnly: true } },
  { path: '/reset-password', name: 'ResetPassword', component: ResetPasswordView, meta: { guestOnly: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.guestOnly && token) {
    next('/dashboard')
  } else if (to.meta.requiresAdmin) {
    const isAdmin = authStore.user?.email?.toLowerCase() === 'ravinderkama14@gmail.com'
    if (!isAdmin) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
