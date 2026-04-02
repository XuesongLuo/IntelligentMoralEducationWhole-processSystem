import { computed, onBeforeUnmount, ref } from 'vue'

export function useExamTimer(initialSeconds = 0, onTimeout) {
  const leftSeconds = ref(initialSeconds)
  let timer = null

  const timeText = computed(() => {
    const h = String(Math.floor(leftSeconds.value / 3600)).padStart(2, '0')
    const m = String(Math.floor((leftSeconds.value % 3600) / 60)).padStart(2, '0')
    const s = String(leftSeconds.value % 60).padStart(2, '0')
    return `${h}:${m}:${s}`
  })

  function start() {
    stop()
    timer = setInterval(() => {
      if (leftSeconds.value <= 0) {
        stop()
        onTimeout && onTimeout()
        return
      }
      leftSeconds.value -= 1
    }, 1000)
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function reset(seconds) {
    leftSeconds.value = seconds
  }

  onBeforeUnmount(() => {
    stop()
  })

  return {
    leftSeconds,
    timeText,
    start,
    stop,
    reset
  }
}