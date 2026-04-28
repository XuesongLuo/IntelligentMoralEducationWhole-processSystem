<template>
  <div class="level-badge">
    <template v-if="currentLevel.icons.length">
      <span
        v-for="(item, index) in currentLevel.icons"
        :key="`${item.label}-${index}`"
        class="level-icon"
        :aria-label="item.label"
      >
        {{ item.icon }}
      </span>
    </template>
    <span v-else class="level-text">{{ currentLevel.label }}</span>
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
  gap: 6px;
  flex-wrap: wrap;
}

.level-icon {
  font-size: 22px;
  line-height: 1;
}

.level-text {
  font-size: 16px;
  color: #1f3f6d;
  font-weight: 600;
}
</style>
