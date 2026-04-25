<template>
    <div ref="chartRef" class="radar-chart"></div>
</template>


<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  scoreDimensions: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chartInstance = null

const radarIndicators = computed(() => {
  return (props.scoreDimensions|| []).map(item => ({
    name: item.name,
    max: 100
  }))
})

function formatIndicatorName(name) {
  const text = String(name || '')
  if (text.length <= 6) return text
  const midpoint = Math.ceil(text.length / 2)
  return `${text.slice(0, midpoint)}\n${text.slice(midpoint)}`
}

const bestScoreValues = computed(() => {
  return (props.scoreDimensions || []).map(item => Number(item.best || 0))
})

const worstScoreValues = computed(() => {
  return (props.scoreDimensions || []).map(item => {
    if (item.worst === undefined || item.worst === null) {
      return Number(item.best || 0)
    }
    return Number(item.worst || 0)
  })
})

const hasWorst = computed(() => {
  return (props.scoreDimensions || []).some(
    item => item.worst !== undefined && item.worst !== null
  )
})

function renderChart() {
  if (!chartRef.value) return
  if (!radarIndicators.value.length) {
    chartInstance?.clear()
    return
  }

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const seriesData = [
    {
      value: bestScoreValues.value,
      name: '最好成绩',
      areaStyle: {
        opacity: 0.18
      },
      lineStyle: {
        width: 2,
        color: '#409eff'
      },
      itemStyle: {
        color: '#409eff'
      },
      symbolSize: 6
    }
  ]

  if (hasWorst.value) {
    seriesData.push({
      value: worstScoreValues.value,
      name: '最低成绩',
      areaStyle: {
        opacity: 0.15
      },
      lineStyle: {
        width: 2,
        color: '#e6a23c'
      },
      itemStyle: {
        color: '#e6a23c'
      },
      symbolSize: 6
    })
  }

  chartInstance.setOption({
    tooltip: {
      trigger: 'item'
    },
    legend: {
      show: false
    },
    radar: {
      radius: '62%',
      center: ['50%', '55%'],
      indicator: radarIndicators.value.map(item => ({
        ...item,
        name: formatIndicatorName(item.name)
      })),
      splitNumber: 5,
      axisName: {
        color: '#333',
        fontSize: 13,
        lineHeight: 18
      },
      splitArea: {
        areaStyle: {
          color: ['#fff']
        }
      },
      splitLine: {
        lineStyle: {
          color: '#dcdfe6'
        }
      },
      axisLine: {
        lineStyle: {
          color: '#dcdfe6'
        }
      }
    },
    series: [
      {
        type: 'radar',
        data: seriesData
      }
    ]
  })
}

function resizeChart() {
  chartInstance?.resize()
}

watch(
  () => props.scoreDimensions,
  async () => {
    await nextTick()
    renderChart()
  },
  { deep: true, immediate: true }
)

onMounted(() => {
  window.addEventListener('resize', resizeChart)
  nextTick(() => {
    renderChart()
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
  chartInstance = null
})

</script>

<style scoped>
.radar-chart {
  width: 100%;
  height: clamp(220px, 26vh, 280px);
}
</style>
