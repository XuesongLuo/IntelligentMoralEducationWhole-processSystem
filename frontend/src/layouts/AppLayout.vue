<template>
    <div class="app-layout">
        <AppHeader
            :username="userInfo.username"
            :logo="userInfo.logo"
        />

        <main class="app-main">
            <router-view />
        </main>
    </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import AppHeader from '@/components/common/AppHeader.vue'

const userInfo = reactive({
  username: '',
  logo: ''
})

function loadUserInfo() {
    const localUser = JSON.parse(localStorage.getItem('userInfo') || '{}')
    userInfo.username = localUser.name || localUser.username || localUser.realName || '用户名'
    userInfo.logo = localUser.logo || ''
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

.app-main {
    min-height: calc(100vh - 64px);
}
</style>