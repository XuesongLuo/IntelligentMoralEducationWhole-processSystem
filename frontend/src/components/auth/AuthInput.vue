<template>
  <div class="custom-input-wrapper">
    <div class="input-row">
      <div class="input-icon-box">{{ icon }}</div>
      
      <div class="input-main">
        <el-input
          :type="type"
          :placeholder="placeholder"
          :model-value="modelValue"
          @input="$emit('update:modelValue', $event)"
          class="styled-el-input"
        >
          <template #suffix v-if="actionText || $slots.suffix">
            <el-button v-if="actionText" link type="primary" @click="$emit('action')">
              {{ actionText }}
            </el-button>
            <slot name="suffix" />
          </template>
        </el-input>
        
        <div class="error-msg" v-if="errorMessage">{{ errorMessage }}</div>
      </div>

      <div class="status-box">
        <el-icon v-if="status === 'success'" color="#8aba35" size="32px"><CircleCheck /></el-icon>
        <el-icon v-if="status === 'error'" color="#f56c6c" size="32px"><CircleClose /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
/* 必须保留原有的 Props 定义，否则父组件传入的参数会失效 */
defineProps({
  modelValue: String,
  placeholder: String,
  type: { type: String, default: 'text' },
  icon: String,
  status: String,
  errorMessage: String,
  actionText: String
})

defineEmits(['update:modelValue', 'action'])
</script>

<style scoped>
.custom-input-wrapper {
  margin-bottom: 30px;
}

.input-row {
  display: flex;
  align-items: center; /* 垂直居中 */
}

.input-icon-box {
  width: 50px; /* 固定宽度，确保所有行对齐 */
  font-size: 24px;
  color: #333;
  display: flex;
  justify-content: flex-start;
  flex-shrink: 0;
}

.input-main {
  flex: 1; /* 自动撑满中间剩余空间 */
  position: relative;
}

.status-box {
  width: 50px; /* 为右侧勾选预留固定空间 */
  display: flex;
  justify-content: center;
  margin-left: 10px;
  flex-shrink: 0;
}

:deep(.styled-el-input .el-input__wrapper) {
  height: 50px;
  border-radius: 0;
  border: 1px solid #b3b3b3 !important;
  box-shadow: none !important;
  padding: 0 20px;
}

/* 错误时的边框颜色 */
:deep(.styled-el-input.is-error .el-input__wrapper) {
  border-color: #f56c6c !important;
}

.error-msg {
  color: #f56c6c;
  font-size: 14px;
  position: absolute;
  bottom: -22px;
  left: 0;
}
</style>