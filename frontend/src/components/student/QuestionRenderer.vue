<template>
  <div class="question-card">
    <div class="q-title">
      {{ index + 1 }}. {{ question.title }}
      <span class="required">*</span>
    </div>

    <div class="q-body">
      <template v-if="question.type === 'single'">
        <el-radio-group v-model="localValue">
          <el-radio
            v-for="opt in question.options"
            :key="opt.value"
            :label="opt.value"
          >
            {{ opt.label }}
          </el-radio>
        </el-radio-group>
      </template>

      <template v-else-if="question.type === 'multiple'">
        <el-checkbox-group v-model="localValue">
          <el-checkbox
            v-for="opt in question.options"
            :key="opt.value"
            :label="opt.value"
          >
            {{ opt.label }}
          </el-checkbox>
        </el-checkbox-group>
      </template>

      <template v-else-if="question.type === 'judge'">
        <el-radio-group v-model="localValue">
          <el-radio :label="true">对</el-radio>
          <el-radio :label="false">错</el-radio>
        </el-radio-group>
      </template>

      <template v-else-if="question.type === 'blank'">
        <el-input v-model="localValue" placeholder="请输入内容" />
      </template>

      <template v-else-if="question.type === 'essay'">
        <el-input
          v-model="localValue"
          type="textarea"
          :rows="5"
          maxlength="1000"
          show-word-limit
          placeholder="请输入内容"
        />
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  question: {
    type: Object,
    required: true
  },
  modelValue: {
    type: [String, Number, Boolean, Array],
    default: ''
  },
  index: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue'])

const localValue = computed({
  get() {
    if (props.question.type === 'multiple') {
      return Array.isArray(props.modelValue) ? props.modelValue : []
    }
    return props.modelValue
  },
  set(val) {
    emit('update:modelValue', val)
  }
})
</script>

<style scoped>
.question-card {
  border: 1px solid #dcdfe6;
  padding: 20px;
  margin-bottom: 18px;
  border-radius: 8px;
}
.q-title {
  margin-bottom: 16px;
  font-size: 18px;
  line-height: 1.8;
  font-weight: 600;
}
.required {
  color: #f56c6c;
  margin-left: 4px;
}
.q-body {
  padding-left: 12px;
}
:deep(.el-radio),
:deep(.el-checkbox) {
  display: block;
  margin-bottom: 14px;
}
</style>