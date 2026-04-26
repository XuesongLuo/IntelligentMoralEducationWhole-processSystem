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

    <div class="right-actions">
      <el-tooltip
        v-if="showGlobalExport"
        content="筛选导出试卷/问卷"
        placement="bottom"
      >
        <button
          class="export-btn"
          type="button"
          :disabled="globalExportDisabled"
          @click="handleGlobalExport"
        >
          <el-icon><Download /></el-icon>
          <span>筛选导出</span>
        </button>
      </el-tooltip>

      <el-dropdown trigger="click" @command="handleCommand">
        <button class="account-trigger" type="button">
          <div class="right-box">
            <el-icon><User /></el-icon>
            <span class="username">{{ username || '用户' }}</span>
            <el-icon class="caret"><ArrowDown /></el-icon>
          </div>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-if="showRosterManage"
              command="roster-manage"
              :disabled="rosterManageDisabled"
            >
              预录入名单管理
            </el-dropdown-item>
            <el-dropdown-item command="logout" :disabled="logoutDisabled">
              {{ logoutDisabled ? '考试中不可退出账号' : '退出账号' }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup>
import { ArrowDown, Download, User } from '@element-plus/icons-vue'

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
  },
  showRosterManage: {
    type: Boolean,
    default: false
  },
  rosterManageDisabled: {
    type: Boolean,
    default: false
  },
  showGlobalExport: {
    type: Boolean,
    default: false
  },
  globalExportDisabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['logout', 'go-home', 'go-roster-manage', 'go-global-export'])

function handleCommand(command) {
  if (command === 'roster-manage' && !props.rosterManageDisabled) {
    emit('go-roster-manage')
    return
  }
  if (command === 'logout' && !props.logoutDisabled) {
    emit('logout')
  }
}

function handleGoHome() {
  if (!props.homeDisabled) {
    emit('go-home')
  }
}

function handleGlobalExport() {
  if (!props.globalExportDisabled) {
    emit('go-global-export')
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

.right-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.export-btn {
  border: 1px solid #dcdfe6;
  background: #fff;
  color: #303133;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.export-btn:hover {
  border-color: #409eff;
  color: #409eff;
}

.export-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
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

.logo-img {
  width: 40px;
  height: 40px;
  object-fit: contain;
  flex-shrink: 0;
  display: block;
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
