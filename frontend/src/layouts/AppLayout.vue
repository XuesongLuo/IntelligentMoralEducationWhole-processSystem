<template>
    <div class="app-layout">
        <AppHeader
            :username="userInfo.username"
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
  username: '',
  logo: '',
  role: ''
})

const systemName = computed(() => {
  return userInfo.role === 'teacher' ? '老师端' : '学生端'
})

function loadUserInfo() {
    const localUser = JSON.parse(localStorage.getItem('userInfo') || '{}')
    
    userInfo.username = localUser.name || '用户名'
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