<template>
  <div class="teacher-page">
    <TeacherSidebar
      :collapsed="sidebarCollapsed"
      :selected-user="selectedUser"
      :user-list="userList"
      @toggle="toggleSidebar"
      @select-user="handleSelectUser"
    />



    <div class="content" :class="{ expand: sidebarCollapsed }">
      <el-card class="overview-card" shadow="never">
        <div class="overview-grid">
          <div class="left-panel">
            <div class="student-meta">
              <p>用户名：{{ homeData.studentId }}</p>
              <p>姓名：{{ homeData.studentName }}</p>
            </div>

            <div class="level-box">
              <LevelBadge :level="levelInfo" />
            </div>

            <div class="ai-time">
              AI工具使用时长：{{ homeData.aiUsageDuration || '0时0分0秒' }}
            </div>

            <div class="completion">
              <div class="completion-label">虚拟仿真训练完成率</div>
              <el-progress
                type="dashboard"
                :percentage="homeData.simulationCompletion || 0"
                :width="170"
              />
            </div>
          </div>

          <div class="middle-panel">
            <h3>德育资源学习进度</h3>
            <div
              v-for="item in homeData.studyProgressList"
              :key="item.id"
              class="progress-row"
            >
              <div class="label">{{ item.name }}</div>
              <div class="bar-wrap">
                <el-progress
                  :percentage="item.progress"
                  :stroke-width="18"
                  :color="getProgressColor(item.progress)"
                />
              </div>
              <div class="remain">{{ item.leftCount }} left</div>
            </div>
          </div>

          <div class="right-panel">
            <h3>思政课程成绩与提升</h3>
            <div class="score-list">
              
              <div
                v-for="item in radarScores"
                :key="item.label"
                class="score-row"
              >
                <span class="score-dot" :style="{ background: item.color }"></span>
                <span>{{ item.label }}</span>
              </div>
            </div>

            <div ref="radarChartRef" class="radar-chart"></div>
          </div>
        </div>

      </el-card>

      <el-card class="nav-card" shadow="never">
        <div class="nav-actions">
          <div 
            class="nav-btn"
            :class="{ disabled: !isViewingSelf }"
            @click="goMoralExam"

          >
            <span>德育画像<br />构建与考试</span>
          </div>
          <div class="nav-btn" @click="goResults">
            <span>结果查看</span>
          </div>
          <div class="nav-btn" @click="goStudy">
            <span>德育资源学习</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts'
import { getUserHomeData, getTeacherStudentList } from '@/api/user'
import { parseLevel } from '@/utils/level'
import { useTeacherViewStore } from '@/stores/teacherView'
import LevelBadge from '@/components/common/LevelBadge.vue'
import TeacherSidebar from '@/components/teacher/TeacherSidebar.vue'

const router = useRouter()
const teacherViewStore = useTeacherViewStore()
const { sidebarCollapsed, selectedUser, userList, isViewingSelf } = storeToRefs(teacherViewStore)

const radarChartRef = ref(null)
let radarChartInstance = null

const homeData = ref({
  studentId: '',
  studentName: '',
  phone: '',

  levelValue: 0, // 等级值，先写死，后续后端返回
  aiUsageDuration: '', // AI使用时长，单位可自定

  simulationCompletion: 0,
  studyProgressList: [],
  scoreDimensions: []
})

const levelInfo = computed(() => parseLevel(homeData.value.levelValue || 0))

const radarScores = computed(() => {
  const list = homeData.value.scoreDimensions || []
  if (!list.length) return []

  const hasWorst = list.some(item => item.worst !== undefined && item.worst !== null)
  return hasWorst
    ? [
        { label: '最好成绩', color: '#409eff' },
        { label: '最低成绩', color: '#e6a23c' }
      ]
    : [
        { label: '最好成绩', color: '#409eff' }
      ]
})

const radarIndicators = computed(() => {
  return (homeData.value.scoreDimensions || []).map(item => ({
    name: item.name,
    max: 100
  }))
})

const bestScoreValues = computed(() => {
  return (homeData.value.scoreDimensions || []).map(item => Number(item.best || 0))
})

const worstScoreValues = computed(() => {
  return (homeData.value.scoreDimensions || []).map(item => {
    if (item.worst === undefined || item.worst === null) {
      return Number(item.best || 0)
    }
    return Number(item.worst || 0)
  })
})

function renderRadarChart() {
  if (!radarChartRef.value) return
  if (!radarIndicators.value.length) return

  if (!radarChartInstance) {
    radarChartInstance = echarts.init(radarChartRef.value)
  }

  const hasWorst = (homeData.value.scoreDimensions || []).some(
    item => item.worst !== undefined && item.worst !== null
  )

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
  if (hasWorst) {
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

  radarChartInstance.setOption({
    tooltip: {
      trigger: 'item'
    },
    legend: {
      show: false
    },
    radar: {
      radius: '62%',
      center: ['50%', '55%'],
      indicator: radarIndicators.value,
      splitNumber: 5,
      axisName: {
        color: '#333',
        fontSize: 14
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

function resizeRadarChart() {
  radarChartInstance?.resize()
}

function getProgressColor(val) {
  if (val >= 80) return '#22c55e'
  if (val >= 50) return '#e6a23c'
  return '#f56c6c'
}

function toggleSidebar() {
  teacherViewStore.toggleSidebar()
}

function handleSelectUser(user) {
  teacherViewStore.selectUser(user)
}

function goMoralExam() {
  if (!isViewingSelf.value) {
    ElMessage.warning('当前查看的是其他账号，不能进入考试模块')
    return
  }
  router.push('/teacher/moral-exam')
}

function goResults() {
  router.push('/teacher/results')
}

function goStudy() {
  ElMessage.info('德育资源学习页面开发中')
  //router.push('/teacher/resource-study')
}

async function loadData() {
  if (!selectedUser.value) return

  const localData = {
    studentId:
    selectedUser.value.role === 'teacher'
      ? selectedUser.value.teacher_no
      : selectedUser.value.student_no,
    studentName: selectedUser.value.real_name
  }

  try {
    const res = await getUserHomeData({ userId: selectedUser.value.id })
    const data = res.data?.data || res.data || {}

    homeData.value = {
      ...homeData.value,
      ...localData,
      ...data
    }
  } catch (error) {
    homeData.value = {
      ...homeData.value,
      ...localData
    }
    console.error('获取老师端首页数据失败：', error)

    await nextTick()
    renderRadarChart()
  }
}

watch(
  () => selectedUser.value,
  () => {
    loadData()
  },
  { immediate: true }
)

watch(
  () => homeData.value.scoreDimensions,
  async () => {
    await nextTick()
    renderRadarChart()
  },
  { deep: true }
)

onMounted(async () => {
  const localUser = JSON.parse(localStorage.getItem('userInfo') || '{}')

  const res = await getTeacherStudentList()
  const userListFromApi = res.data?.data || []

  const currentTeacher = {
    id: localUser.id,
    role: 'teacher',
    real_name: localUser.real_name,
    teacher_no: localUser.teacher_no,
    label: `${localUser.teacher_no || localUser.username} ${localUser.real_name}`
  }

  teacherViewStore.init(currentTeacher, userListFromApi)

  window.addEventListener('resize', resizeRadarChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeRadarChart)
  radarChartInstance?.dispose()
  radarChartInstance = null
})

</script>

<style scoped>
.teacher-page {
  display: flex;
  justify-content: center; /* 居中内容 */
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
} 
.content {
  width: 1200px;
  margin: 0 auto;
  transition: all 0.3s;
  padding: 24px 20px;
}
.overview-card,
.nav-card {
  border-radius: 18px;
  margin-bottom: 56px;
}
.overview-grid {
  display: grid;
  grid-template-columns: 320px 1fr 360px;
  gap: 24px;
}
.student-meta p {
  margin: 6px 0;
  font-size: 18px;
}
.level-box {
  margin: 4px 0;
  min-height: 36px;
}
.ai-time {
  margin-bottom: 24px;
  font-size: 16px;
}
.completion {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.completion-label {
  margin-bottom: 12px;
  font-size: 16px;
}
.middle-panel h3,
.right-panel h3 {
  margin-top: 0;
  margin-bottom: 18px;
  font-size: 28px;
}
.progress-row {
  display: grid;
  grid-template-columns: 140px 1fr 80px;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}
.label {
  font-size: 15px;
}
.remain {
  font-size: 14px;
  color: #666;
}
.score-list {
  display: flex;
  gap: 16px;
  margin-bottom: 18px;
}
.score-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.score-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.radar-chart {
  width: 100%;
  height: 300px;
}

.nav-actions {
  min-height: 240px;
  display: flex;
  align-items: center;
  justify-content: space-around;
}
.nav-btn {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  border: 2px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 30px;
  cursor: pointer;
  transition: all 0.25s;
  background: #fff;
}
.nav-btn:hover {
  transform: translateY(-4px);
  border-color: #409eff;
  color: #409eff;
}
.nav-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>