<template>
  <header class="app-header">
    <button
      type="button"
      class="left-box"
      :class="{ disabled: homeDisabled }"
      :disabled="homeDisabled"
      @click="handleGoHome"
    >
      <img v-if="logo" :src="logo" class="logo-img" alt="logo" />
      <div v-else class="logo-text">LOGO</div>
      <span class="system-name">{{ systemName }}</span>
    </button>

    <el-dropdown trigger="click" :disabled="logoutDisabled" @command="handleCommand">
      <button class="account-trigger" type="button" :disabled="logoutDisabled">
        <div class="right-box">
          <el-icon><User /></el-icon>
          <span class="username">{{ username || '用户' }}</span>
          <el-icon class="caret"><ArrowDown /></el-icon>
        </div>
      </button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="logout" :disabled="logoutDisabled">
            {{ logoutDisabled ? '考试中不可退出账号' : '退出账号' }}
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </header>
</template>

<script setup>
import { ArrowDown, User } from '@element-plus/icons-vue'

const props = defineProps({
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
  },
  logoutDisabled: {
    type: Boolean,
    default: false
  },
  homeDisabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['logout', 'go-home'])

function handleCommand(command) {
  if (command === 'logout' && !props.logoutDisabled) {
    emit('logout')
  }
}

function handleGoHome() {
  if (!props.homeDisabled) {
    emit('go-home')
  }
}
</script>

<style scoped>
.app-header {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #999999;
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

.left-box {
  border: none;
  background: transparent;
  padding: 8px 10px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.2s ease, opacity 0.2s ease;
}

.left-box:hover {
  background: #f3f6fb;
}

.left-box.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.left-box.disabled:hover {
  background: transparent;
}

.account-trigger {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 8px 10px;
  border-radius: 999px;
  transition: background 0.2s ease, opacity 0.2s ease;
}

.account-trigger:hover {
  background: #f3f6fb;
}

.account-trigger:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.account-trigger:disabled:hover {
  background: transparent;
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

.caret {
  color: #909399;
  font-size: 14px;
}
</style>
