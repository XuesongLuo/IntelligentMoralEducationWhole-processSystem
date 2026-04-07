<template>
    <div class="app-layout">
        <AppHeader
            :username="headerDisplayText"
            :logo="userInfo.logo"
            :system-name="systemName"
        />

        <main class="app-main">
            <router-view />
        </main>
    </div>
</template>

<script setup>
import { reactive, computed, onMounted } from 'vue'
import AppHeader from '@/components/common/AppHeader.vue'

const userInfo = reactive({
  real_name: '',
  student_no: '',
  teacher_no: '',
  logo: '',
  role: ''
})

const systemName = computed(() => {
  return userInfo.role === 'teacher' ? '老师端' : '学生端'
})

const headerDisplayText = computed(() => {
  if (userInfo.role === 'teacher') {
    return userInfo.teacher_no || userInfo.real_name || '老师'
  }
  return userInfo.student_no || userInfo.real_name || '学号'
})

function loadUserInfo() {
    const localUser = JSON.parse(localStorage.getItem('userInfo') || '{}')
    
    userInfo.real_name = localUser.real_name || ''
    userInfo.student_no = localUser.student_no || ''
    userInfo.teacher_no = localUser.teacher_no || ''
    userInfo.logo = localUser.logo || ''
    userInfo.role = localUser.role || localStorage.getItem('role') || 'student'
}

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