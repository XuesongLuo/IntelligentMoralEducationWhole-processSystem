<template>
  <div class="level-badge">
    <span v-if="currentLevel.icon" class="level-icon">{{ currentLevel.icon }}</span>
    <span class="level-text">
      {{ currentLevel.label }}
      <template v-if="currentLevel.count">x{{ currentLevel.count }}</template>
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { parseLevel } from '@/utils/level'

const props = defineProps({
  levelValue: {
    type: Number,
    default: 0
  }
})

const currentLevel = computed(() => parseLevel(props.levelValue))
</script>

<style scoped>
.level-badge {
  min-height: 36px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.level-icon {
  font-size: 22px;
}

.level-text {
  font-size: 16px;
  color: #1f3f6d;
  font-weight: 600;
}
</style>
