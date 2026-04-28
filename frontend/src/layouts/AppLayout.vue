<template>
  <div class="app-layout">
    <AppHeader
      :username="headerDisplayText"
      :logo="headerLogo"
      :system-name="systemName"
      :logout-disabled="logoutDisabled"
      :home-disabled="homeDisabled"
      :show-roster-manage="userInfo.role === 'teacher'"
      :roster-manage-disabled="homeDisabled"
      :show-global-export="showGlobalExport"
      :global-export-disabled="homeDisabled"
      @logout="handleLogout"
      @go-home="handleGoHome"
      @go-roster-manage="handleGoRosterManage"
      @go-global-export="handleGoGlobalExport"
    />

    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/common/AppHeader.vue'
import defaultHeaderLogo from '@/assets/images/dyq_icon_64_64.png'
import {
  EXAM_BLOCKED_MESSAGE,
  EXAM_LOGOUT_BLOCKED_MESSAGE,
  getActiveExamSession,
  isExamPaperRoute,
  notifyExamWarning
} from '@/utils/examSession'

const route = useRoute()
const router = useRouter()

const userInfo = reactive({
  id: null,
  real_name: '',
  student_no: '',
  teacher_no: '',
  logo: '',
  role: ''
})

const systemName = computed(() => {
  return userInfo.role === 'teacher' ? '教师端' : '学生端'
})

const headerDisplayText = computed(() => {
  if (userInfo.role === 'teacher') {
    return userInfo.teacher_no || userInfo.real_name || '老师'
  }
  return userInfo.student_no || userInfo.real_name || '学号'
})

const headerLogo = computed(() => {
  return userInfo.logo || defaultHeaderLogo
})

const hasActiveExam = computed(() => {
  const activeExamSession = getActiveExamSession()
  return Boolean(
    activeExamSession &&
      activeExamSession.userId === userInfo.id &&
      activeExamSession.role === userInfo.role
  )
})

const logoutDisabled = computed(() => {
  return isExamPaperRoute(route) || hasActiveExam.value
})

const homeDisabled = computed(() => {
  return isExamPaperRoute(route) || hasActiveExam.value
})

const showGlobalExport = computed(() => {
  return userInfo.role === 'teacher' && route.path === '/teacher/results'
})

function getHomePath() {
  return userInfo.role === 'teacher' ? '/teacher/home' : '/student/home'
}

function loadUserInfo() {
  const localUser = JSON.parse(localStorage.getItem('userInfo') || '{}')
  userInfo.id = localUser.id ?? null
  userInfo.real_name = localUser.real_name || ''
  userInfo.student_no = localUser.student_no || ''
  userInfo.teacher_no = localUser.teacher_no || ''
  userInfo.logo = localUser.logo || ''
  userInfo.role = localUser.role || localStorage.getItem('role') || 'student'
}

function handleLogout() {
  if (logoutDisabled.value) {
    notifyExamWarning(EXAM_LOGOUT_BLOCKED_MESSAGE)
    return
  }

  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  localStorage.removeItem('role')
  localStorage.removeItem('teacherViewState')
  router.replace('/login')
}

function handleGoHome() {
  if (homeDisabled.value) {
    notifyExamWarning(EXAM_BLOCKED_MESSAGE)
    return
  }

  router.push(getHomePath())
}

function handleGoRosterManage() {
  if (homeDisabled.value) {
    notifyExamWarning(EXAM_BLOCKED_MESSAGE)
    return
  }
  router.push('/teacher/roster-manage')
}

function handleGoGlobalExport() {
  if (homeDisabled.value) {
    notifyExamWarning(EXAM_BLOCKED_MESSAGE)
    return
  }
  router.push({
    path: '/teacher/results',
    query: {
      globalExport: String(Date.now())
    }
  })
}

watch(
  () => route.fullPath,
  () => {
    loadUserInfo()
  }
)

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f5f7fa;
  overflow-x: hidden;
}

.app-main {
  min-height: calc(100vh - 64px);
  overflow-x: hidden;
}
</style>
