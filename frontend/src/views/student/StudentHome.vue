<template>
  <div class="student-page">
    <div class="content">
      <el-card class="overview-card" shadow="never">
        <div class="overview-grid">
          <div class="left-panel">
            <div class="student-meta">
              <p>学号：{{ homeData.studentId }}</p>
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

            <ScoreRadarChart :score-dimensions="homeData.scoreDimensions" />

            <!--div class="radar-fake">
              <div class="radar-item" v-for="dim in homeData.scoreDimensions" :key="dim.key">
                <div class="dim-name">{{ dim.name }}</div>
                <div class="dim-bar">
                  <div class="best" :style="{ width: dim.best + '%' }"></div>
                  <div class="worst" :style="{ width: dim.worst + '%' }"></div>
                </div>
                <div class="dim-text">{{ dim.best }}/{{ dim.worst }}</div>
              </div>
            </div-->
          </div>
        </div>
      </el-card>

      <el-card class="nav-card" shadow="never">
        <div class="nav-actions">
          <div class="nav-btn" @click="goMoralExam">
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getUserHomeData } from '@/api/user'
import { parseLevel } from '@/utils/level'
import LevelBadge from '@/components/common/LevelBadge.vue'
import ScoreRadarChart from '@/components/common/ScoreRadarChart.vue'

const router = useRouter()

const homeData = ref({
  studentId: '',
  studentName: '',
  phone: '',

  levelValue: 3, // 等级值，先写死，后续后端返回
  aiUsageDuration: 120, // AI使用时长，单位可自定
  highestScore: 88,
  lowestScore: 72,

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

function getProgressColor(val) {
  if (val >= 80) return '#22c55e'
  if (val >= 50) return '#e6a23c'
  return '#f56c6c'
}

function goMoralExam() {
  router.push('/student/moral-exam')
}

function goResults() {
  router.push('/student/results')
}

function goStudy() {
  router.push('/student/resource-study')
}

async function loadData() {
  try {
    const res = await getUserHomeData()
    const data = res.data?.data || res.data || {}

    homeData.value = {
      ...homeData.value,
      ...data
    }
  } catch (error) {
    console.error('获取学生首页数据失败：', error)
  }
}

function loadLoginUser() {
  const localUser = JSON.parse(localStorage.getItem('userInfo') || '{}')

  homeData.value.studentId = localUser.student_no || ''
  homeData.value.studentName = localUser.real_name  || ''
  homeData.value.phone = localUser.phone || ''
}

onMounted(() => {
  loadLoginUser()
  loadData()
})

</script>

<style scoped>
.student-page {
  display: flex;
  justify-content: center; /* 居中内容 */
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
} 
.content {
  width: 1200px;
  margin: 0 auto;
  padding-top: 24px;
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
.radar-fake {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.radar-item {
  display: grid;
  grid-template-columns: 90px 1fr 70px;
  gap: 10px;
  align-items: center;
}
.dim-bar {
  position: relative;
  height: 12px;
  background: #ebeef5;
  border-radius: 999px;
  overflow: hidden;
}
.dim-bar .best {
  position: absolute;
  left: 0;
  top: 0;
  height: 12px;
  background: #409eff;
  opacity: 0.9;
}
.dim-bar .worst {
  position: absolute;
  left: 0;
  top: 0;
  height: 12px;
  background: #e6a23c;
  opacity: 0.7;
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
</style>
