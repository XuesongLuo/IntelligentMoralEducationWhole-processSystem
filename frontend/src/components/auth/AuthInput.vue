<template>
  <div class="custom-input-wrapper">
    <div class="input-row">
      <div class="input-icon-box">
        <slot name="icon">
          <div class="input-icon-inner">
            <img
              v-if="iconImage"
              :src="iconImage"
              :alt="iconAlt || placeholder || 'input icon'"
              class="input-icon-image"
            />
            <span v-else class="input-icon-text">{{ icon }}</span>
          </div>
        </slot>
      </div>

      <div class="input-main">
        <el-input
          :type="type"
          :placeholder="placeholder"
          :model-value="modelValue"
          @input="$emit('update:modelValue', $event)"
          @blur="$emit('blur')"
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
defineProps({
  modelValue: String,
  placeholder: String,
  type: { type: String, default: 'text' },
  icon: String,
  iconImage: String,
  iconAlt: String,
  status: String,
  errorMessage: String,
  actionText: String
})

defineEmits(['update:modelValue', 'action', 'blur'])
</script>

<style scoped>
.custom-input-wrapper {
  margin-bottom: 30px;
}

.input-row {
  display: flex;
  align-items: center;
}

.input-icon-box {
  width: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.input-icon-inner {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-icon-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.input-icon-text {
  font-size: 24px;
  line-height: 1;
  color: #333;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.input-main {
  flex: 1;
  position: relative;
}

.status-box {
  width: 50px;
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
