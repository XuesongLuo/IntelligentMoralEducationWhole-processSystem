<template>
  <div class="page-wrap">
  
    <div class="main-box">
      <div class="title-row">
        <h1>{{ pageTitle }}</h1>
        <div class="timer-box">⏱ {{ timeText }}</div>
      </div>

      <el-card class="paper-panel" shadow="never" v-loading="loading">
        <div class="paper-name">{{ paperData.paperName || '试卷名称' }}</div>

        <div class="question-scroll">
          <QuestionRenderer
            v-for="(q, index) in paperData.questions"
            :key="q.id"
            :question="q"
            :index="index"
            v-model="answerMap[q.id]"
          />
        </div>

        <div class="submit-row">
          <el-button type="primary" size="large" @click="handleSubmit(false)">
            提交
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { getExamPaper, submitExamPaper } from '@/api/exam'
import { useExamTimer } from '@/composables/useExamTimer'
import QuestionRenderer from '@/components/student/QuestionRenderer.vue'

const route = useRoute()
const router = useRouter()

const type = computed(() => route.params.type)
const examId = computed(() => route.params.examId)
const loading = ref(false)

const currentRole = computed(() => {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  return userInfo.role || 'student'
})

const routePrefix = computed(() => {
  return currentRole.value === 'teacher' ? '/teacher' : '/student'
})


const paperData = ref({
  examId: '',
  paperName: '',
  durationSeconds: 3600,
  questions: []
})

const answerMap = reactive({})

const pageTitle = computed(() => {
  return type.value === 'survey' ? '画像构建' : '诚信考核'
})

const { timeText, reset, start, stop } = useExamTimer(0, async () => {
  ElMessage.warning('答题时间已结束，系统将自动提交。')
  await handleSubmit(true)
})

function initAnswers(questions = []) {
  questions.forEach(q => {
    if (q.type === 'multiple') {
      answerMap[q.id] = []
    } else if (q.type === 'judge') {
      answerMap[q.id] = null
    } else {
      answerMap[q.id] = ''
    }
  })
}

function validateAnswers() {
  for (const q of paperData.value.questions) {
    const ans = answerMap[q.id]

    if (q.type === 'multiple') {
      if (!Array.isArray(ans) || ans.length === 0) {
        return `${q.title} 未作答`
      }
    } else if (q.type === 'judge') {
      if (ans !== true && ans !== false) {
        return `${q.title} 未作答`
      }
    } else {
      if (ans === '' || ans === null || ans === undefined) {
        return `${q.title} 未作答`
      }
    }
  }
  return ''
}

async function handleSubmit(force) {
  if (!force) {
    const errorText = validateAnswers()
    if (errorText) {
      ElMessage.error(errorText)
      return
    }

    try {
      await ElMessageBox.confirm('确认提交当前答卷吗？提交后不可修改。', '提交确认', {
        type: 'warning'
      })
    } catch {
      return
    }
  }

  try {
    loading.value = true
    const payload = {
      examId: paperData.value.examId,
      examType: type.value,
      answers: Object.keys(answerMap).map(questionId => ({
        questionId,
        answer: answerMap[questionId]
      })),
      forced: force
    }

    await submitExamPaper(payload)
    stop()
    ElMessage.success(force ? '已自动提交' : '提交成功')
    router.push(`${routePrefix.value}/moral-exam`)
  } finally {
    loading.value = false
  }
}

async function loadPaper() {
  loading.value = true
  try {
    const res = await getExamPaper(type.value, examId.value)
    paperData.value = res.data
    initAnswers(paperData.value.questions || [])
    reset(paperData.value.durationSeconds || 3600)
    start()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPaper()
})
</script>

<style scoped>
.page-wrap {
  background: #f5f7fa;
}
.main-box {
  width: 1200px;
  margin: 30px auto;
}
.title-row {
  position: relative;
  margin-bottom: 24px;
}
h1 {
  text-align: center;
  font-size: 52px;
  margin: 0;
}
.timer-box {
  position: absolute;
  right: 0;
  top: 12px;
  font-size: 32px;
  color: #303133;
}
.paper-panel {
  min-height: 640px;
  border-radius: 16px;
}
.paper-name {
  text-align: center;
  font-size: 34px;
  font-weight: 600;
  margin-bottom: 20px;
}
.question-scroll {
  height: 520px;
  overflow-y: auto;
  padding: 6px 10px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
}
.submit-row {
  text-align: center;
  margin-top: 24px;
}
</style>