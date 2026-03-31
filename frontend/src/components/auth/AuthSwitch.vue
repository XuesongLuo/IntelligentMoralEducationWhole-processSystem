<template>
  <el-switch
    :model-value="modelValue"
    @change="(val) => $emit('update:modelValue', val)"
    active-value="teacher"
    inactive-value="student"
    class="custom-switch"
  />
</template>

<script setup>
defineProps(['modelValue'])
defineEmits(['update:modelValue'])
</script>

<style scoped>
.custom-switch {
  /* 只修改颜色，不修改尺寸 */
  --el-switch-on-color: #18d860;
  --el-switch-off-color: #e0e0e0;
}

/* 如果觉得默认圆点太小，可以微调，但不建议改 core 的 width */
:deep(.el-switch__core) {
  border: none !important;
}
</style>