<template>
  <div class="app-layout">
    <AppHeader
      :username="headerDisplayText"
      :logo="userInfo.logo"
      :system-name="systemName"
      :logout-disabled="logoutDisabled"
      @logout="handleLogout"
    />

    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/common/AppHeader.vue'
import { getActiveExamSession } from '@/utils/examSession'

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

const logoutDisabled = computed(() => {
  const activeExamSession = getActiveExamSession()
  return (
    !!activeExamSession &&
    activeExamSession.userId === userInfo.id &&
    activeExamSession.role === userInfo.role
  )
})

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
    ElMessage.warning('考试进行中，当前不允许退出账号')
    return
  }

  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  localStorage.removeItem('role')
  localStorage.removeItem('teacherViewState')
  router.replace('/login')
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
}
</style>
