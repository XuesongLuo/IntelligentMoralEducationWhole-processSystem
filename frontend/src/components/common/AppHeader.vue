<template>
    <header class="app-header">
        <div class="left-box">
            <img v-if="logo" :src="logo" class="logo-img" alt="logo" />
            <div v-else class="logo-text">LOGO</div>
            <span class="system-name">{{ systemName }}</span>
        </div>

        <div class="right-box">
            <el-icon><User /></el-icon>
            <span class="username">{{ username || '用户名' }}</span>
        </div>
    </header>
</template>

<script setup>
import { User } from '@element-plus/icons-vue'

defineProps({
    username: {
        type: String,
        default: ''
    },
    logo: {
        type: String,
        default: ''
    },
    systemName: {
    type: String,
    default: '学生端'
  }
})
</script>

<style scoped>
.app-header {
    height: 64px;
    background: #fff;
    border-bottom: 1px solid #e5e7eb;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-sizing: border-box;
}

.left-box,
.right-box {
    display: flex;
    align-items: center;
    gap: 10px;
}

.logo-img {
    width: 32px;
    height: 32px;
    object-fit: contain;
}

.logo-text {
    font-size: 20px;
    font-weight: 700;
    color: #409eff;
}

.system-name {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
}

.username {
    font-size: 15px;
    color: #303133;
}
</style>