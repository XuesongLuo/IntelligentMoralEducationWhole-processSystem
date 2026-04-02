<template>
  <div class="level-badge">
    <span v-for="n in level.crown" :key="'c' + n" class="level-icon">👑</span>
    <span v-for="n in level.sun" :key="'s' + n" class="level-icon">☀️</span>
    <span v-for="n in level.moon" :key="'m' + n" class="level-icon">🌙</span>
    <span v-for="n in level.star" :key="'st' + n" class="level-icon">⭐</span>
    <span v-if="isEmpty" class="level-empty">暂无等级</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  level: {
    type: Object,
    default: () => ({
      crown: 0,
      sun: 0,
      moon: 0,
      star: 0
    })
  }
})

const isEmpty = computed(() => {
  const { crown, sun, moon, star } = props.level
  return crown + sun + moon + star === 0
})
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
  font-size: 20px;
}
.level-empty {
  color: #999;
}
</style>