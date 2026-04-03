<template>
  <div class="level-badge">
    <span v-for="n in crowns" :key="'crown' + n">👑</span>
    <span v-for="n in suns" :key="'sun' + n">☀️</span>
    <span v-for="n in moons" :key="'moon' + n">🌙</span>
    <span v-for="n in stars" :key="'star' + n">⭐</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  levelValue: {
    type: Number,
    default: 0
  }
})

const MAX_LEVEL = 5 * 5 * 5 * 5 - 1

const normalizedLevel = computed(() => {
  return Math.max(0, Math.min(props.levelValue, MAX_LEVEL))
})

const crowns = computed(() => Math.floor(normalizedLevel.value / 125))
const remainsAfterCrowns = computed(() => normalizedLevel.value % 125)

const suns = computed(() => Math.floor(remainsAfterCrowns.value / 25))
const remainsAfterSuns = computed(() => remainsAfterCrowns.value % 25)

const moons = computed(() => Math.floor(remainsAfterSuns.value / 5))
const stars = computed(() => remainsAfterSuns.value % 5)

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