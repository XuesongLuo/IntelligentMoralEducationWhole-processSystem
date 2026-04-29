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
              <LevelBadge :level-value="homeData.levelValue || 0" />
            </div>

            <div class="ai-time">
              AI 工具使用时长：{{ homeData.aiUsageDuration || '0时0分0秒' }}
            </div>

            <div class="completion">
              <div class="completion-label">虚拟仿真训练完成率</div>
              <el-progress type="dashboard" :percentage="homeData.simulationCompletion || 0" :width="164" />
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
                  :stroke-width="16"
                  :color="getProgressColor(item.progress)"
                />
              </div>
              <div class="remain">剩余 {{ item.leftCount }} 项</div>
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
          </div>
        </div>
      </el-card>

      <el-card class="nav-card" shadow="never">
        <div class="nav-actions">
          <button class="nav-btn" type="button" @click="goMoralExam" aria-label="德育画像构建与考试">
            <img :src="moralExamButton" alt="德育画像构建与考试" class="nav-btn-image" />
          </button>
          <button class="nav-btn" type="button" @click="goResults" aria-label="结果查看">
            <img :src="resultButton" alt="结果查看" class="nav-btn-image" />
          </button>
          <button class="nav-btn" type="button" @click="goStudy" aria-label="德育资源学习">
            <img :src="resourceStudyButton" alt="德育资源学习" class="nav-btn-image" />
          </button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getUserHomeData } from '@/api/user'
import LevelBadge from '@/components/common/LevelBadge.vue'
import ScoreRadarChart from '@/components/common/ScoreRadarChart.vue'
import moralExamButton from '@/assets/images/home-navigation/moral-exam.png'
import resultButton from '@/assets/images/home-navigation/results.png'
import resourceStudyButton from '@/assets/images/home-navigation/resource-study.png'

const router = useRouter()

const homeData = ref({
  studentId: '',
  studentName: '',
  phone: '',
  levelValue: 3,
  aiUsageDuration: 120,
  highestScore: 88,
  lowestScore: 72,
  simulationCompletion: 0,
  studyProgressList: [],
  scoreDimensions: []
})

const radarScores = computed(() => {
  const list = homeData.value.scoreDimensions || []
  if (!list.length) {
    return [
      { label: '提升后成绩', color: '#409eff' },
      { label: '初始成绩', color: '#e6a23c' }
    ]
  }

  const hasWorst = list.some(item => item.worst !== undefined && item.worst !== null)

  return hasWorst
    ? [
        { label: '提升后成绩', color: '#409eff' },
        { label: '初始成绩', color: '#e6a23c' }
      ]
    : [{ label: '提升后成绩', color: '#409eff' }]
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
  homeData.value.studentName = localUser.real_name || ''
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
  justify-content: center;
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
  overflow-x: hidden;
}

.content {
  width: min(72vw, calc(100% - 32px));
  max-width: 1380px;
  margin: 0 auto;
  padding: 18px 0;
}

.overview-card,
.nav-card {
  border-radius: 18px;
  margin-bottom: 28px;
}

:deep(.overview-card .el-card__body),
:deep(.nav-card .el-card__body) {
  min-height: 415px;
  box-sizing: border-box;
}

:deep(.nav-card .el-card__body) {
  display: flex;
  align-items: center;
}

.overview-grid {
  display: grid;
  grid-template-columns: minmax(240px, 0.88fr) minmax(300px, 1.15fr) minmax(340px, 1.08fr);
  align-items: start;
  gap: 20px;
  min-height: 100%;
}

.left-panel,
.middle-panel,
.right-panel,
.bar-wrap {
  min-width: 0;
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
  margin-bottom: 22px;
  font-size: 16px;
}

.completion {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.completion-label {
  font-size: 16px;
  max-width: 84px;
  line-height: 1.4;
  text-align: right;
}

.middle-panel h3,
.right-panel h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 26px;
}

.middle-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 10px 0;
}

.right-panel {
  padding: 10px 0;
}

.progress-row {
  display: grid;
  grid-template-columns: minmax(96px, 140px) minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
}

.label {
  font-size: 15px;
  overflow-wrap: anywhere;
}

.remain {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
  min-width: 64px;
  text-align: right;
}

.score-list {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.score-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.score-row span:last-child {
  white-space: nowrap;
}

.score-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.nav-actions {
  width: 100%;
  min-height: 100%;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  align-items: center;
  align-content: center;
  justify-items: center;
  gap: 20px;
}

.nav-btn {
  width: 174px;
  height: 174px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
  transition: transform 0.25s;
}

.nav-btn:hover {
  transform: translateY(-4px);
}

.nav-btn-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

@media (max-width: 1440px) {
  .overview-grid {
    grid-template-columns: minmax(220px, 0.86fr) minmax(260px, 1.05fr) minmax(320px, 1fr);
  }
}

@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .left-panel {
    grid-column: 1 / -1;
  }
}

@media (max-width: 960px) {
  :deep(.overview-card .el-card__body),
  :deep(.nav-card .el-card__body) {
    min-height: unset;
  }

  :deep(.nav-card .el-card__body) {
    display: block;
  }

  .content {
    width: calc(100% - 20px);
    max-width: none;
    padding-top: 14px;
  }

  .overview-grid,
  .nav-actions {
    grid-template-columns: 1fr;
  }

  .progress-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .remain {
    white-space: normal;
  }

  .completion {
    flex-direction: column;
    gap: 12px;
  }

  .completion-label {
    max-width: none;
    text-align: center;
  }

  .score-row span:last-child {
    white-space: normal;
    overflow-wrap: anywhere;
  }
}
</style>
