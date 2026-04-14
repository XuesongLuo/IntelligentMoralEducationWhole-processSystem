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
import { computed, onMounted, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { getExamPaper, submitExamHeartbeat, submitExamPaper } from '@/api/exam'
import { useExamTimer } from '@/composables/useExamTimer'
import QuestionRenderer from '@/components/common/QuestionRenderer.vue'
import {
  clearActiveExamSession,
  getExamClientSessionId,
  resetExamClientSessionId,
  setActiveExamSession
} from '@/utils/examSession'

const route = useRoute()
const router = useRouter()

const type = computed(() => route.params.type)
const examId = computed(() => route.params.examId)
const loading = ref(false)
const submitSucceeded = ref(false)
let heartbeatTimer = null

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
  const pageTitleMap = {
    survey: '画像构建',
    integrity: '诚信考核',
    ideology: '思政考试'
  }
  return pageTitleMap[type.value] || '考试'
})

const { timeText, reset, start, stop } = useExamTimer(0, async () => {
  ElMessage.warning('答题时间已结束，系统将自动提交。')
  await handleSubmit(true)
})

// 答题缓存--用户
const currentUser = computed(() => {
  return JSON.parse(localStorage.getItem('userInfo') || '{}')
})
const clientSessionId = ref('')

function syncActiveExamSession() {
  if (!currentUser.value.id || !type.value || !examId.value) return
  setActiveExamSession({
    userId: currentUser.value.id,
    role: currentRole.value,
    type: type.value,
    examId: examId.value
  })
}

function syncClientSessionId(reset = false) {
  if (!currentUser.value.id || !type.value || !examId.value) return ''
  clientSessionId.value = reset
    ? resetExamClientSessionId(currentUser.value.id, type.value, examId.value)
    : getExamClientSessionId(currentUser.value.id, type.value, examId.value)
  return clientSessionId.value
}
// 答题缓存--key
const draftKey = computed(() => {
  return `exam_draft_${currentUser.value.id}_${type.value}_${examId.value}`
})
// 时间戳
const deadlineAt = ref(null)
const restoredRemainingSeconds = ref(null)
const heartbeatPayload = computed(() => ({
  examId: paperData.value.examId || examId.value,
  examType: type.value,
  clientSessionId: clientSessionId.value
}))


function saveDraft() {
  const payload = {
    examId: paperData.value.examId,
    examType: type.value,
    answers: { ...answerMap },
    deadlineAt: deadlineAt.value,
    savedAt: Date.now()
  }
  localStorage.setItem(draftKey.value, JSON.stringify(payload))
}

// 保存和恢复函数
function restoreDraft(questions = []) {
  const raw = localStorage.getItem(draftKey.value)
  if (!raw) return

  try {
    const cache = JSON.parse(raw)
    const cachedAnswers = cache.answers || {}

    questions.forEach(q => {
      if (cachedAnswers[q.id] !== undefined) {
        answerMap[q.id] = cachedAnswers[q.id]
      }
    })
    if (cache.deadlineAt) {
      deadlineAt.value = cache.deadlineAt
      restoredRemainingSeconds.value = Math.max(
        0,
        Math.floor((cache.deadlineAt - Date.now()) / 1000)
      )
    }
  } catch (error) {
    console.error('恢复答题草稿失败：', error)
  }
}
// 清除缓存函数
function clearDraft() {
  localStorage.removeItem(draftKey.value)
}

function resetAnswerMap() {
  Object.keys(answerMap).forEach(key => {
    delete answerMap[key]
  })
}

function handleContextMenu(event) {
  event.preventDefault()
}

async function sendHeartbeat(options = {}) {
  const payload = heartbeatPayload.value
  if (!payload.examId || !payload.examType) return

  if (options.keepalive) {
    const token = localStorage.getItem('token')
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const rolePrefix = userInfo.role === 'teacher' ? '/teacher' : '/student'

    try {
      await fetch(`/api/v1${rolePrefix}/exam/heartbeat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify(payload),
        keepalive: true
      })
    } catch (error) {
      console.error('发送离开前心跳失败：', error)
    }
    return
  }

  try {
    const res = await submitExamHeartbeat(payload)
    const remainingSeconds = res?.data?.remainingSeconds
    if (typeof remainingSeconds === 'number' && remainingSeconds >= 0) {
      deadlineAt.value = Date.now() + remainingSeconds * 1000
    }
  } catch (error) {
    console.error('发送考试心跳失败：', error)
  }
}

function startHeartbeat() {
  stopHeartbeat()
  heartbeatTimer = window.setInterval(() => {
    sendHeartbeat()
  }, 30000)
}

function stopHeartbeat() {
  if (heartbeatTimer) {
    window.clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}
// 设置题目默认答案
function buildDefaultAnswer(q) {
  if (q.type === 'multiple') return []
  if (q.type === 'judge') return null
  return ''
}
function initAnswers(questions = []) {
  questions.forEach(q => {
    if (!(q.id in answerMap)) {
      answerMap[q.id] = buildDefaultAnswer(q)
    }
  })
}

// 加载试卷
async function loadPaper() {
  loading.value = true
  restoredRemainingSeconds.value = null
  try {
    syncClientSessionId()
    const res = await getExamPaper(type.value, examId.value, clientSessionId.value)
    paperData.value = res.data
    syncActiveExamSession()
    if (paperData.value.sessionMismatch) {
      clearDraft()
      resetAnswerMap()
      ElMessage.warning('检测到你更换了设备，本次考试将重新作答，但剩余时间保持不变')
    } else {
      restoreDraft(paperData.value.questions || [])
    }
    initAnswers(paperData.value.questions || [])

    if (restoredRemainingSeconds.value !== null) {
      const serverRemainingSeconds = paperData.value.remainingSeconds
      if (typeof serverRemainingSeconds === 'number') {
        restoredRemainingSeconds.value = Math.min(restoredRemainingSeconds.value, serverRemainingSeconds)
      }
      if (restoredRemainingSeconds.value <= 0) {
        ElMessage.warning('考试时间已结束，系统将自动提交。')
        await handleSubmit(true)
        return
      }
      reset(restoredRemainingSeconds.value)
    } else {
      const totalSeconds = paperData.value.remainingSeconds ?? (paperData.value.durationSeconds || 3600)
      deadlineAt.value = Date.now() + totalSeconds * 1000
      reset(totalSeconds)
      saveDraft()
    }
    start()
    await sendHeartbeat()
    startHeartbeat()
  } finally {
    loading.value = false
  }
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
// 试卷提交函数
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
      clientSessionId: clientSessionId.value,
      answers: Object.keys(answerMap).map(questionId => ({
        questionId,
        answer: answerMap[questionId]
      })),
      forced: force
    }

    await submitExamPaper(payload)
    submitSucceeded.value = true
    clearActiveExamSession()
    clearDraft()
    stopHeartbeat()
    stop()
    ElMessage.success(force ? '已自动提交' : '提交成功')
    router.replace(`${routePrefix.value}/home`)
  } catch (error) {
    const message =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      '提交失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}
// 离开页面前提示用户
function handleBeforeUnload(event) {
  const hasDraft = !!localStorage.getItem(draftKey.value)
  sendHeartbeat({ keepalive: true })
  if (!hasDraft) return
  event.preventDefault()
  event.returnValue = ''
}

watch(
  answerMap,
  () => {
    if (!paperData.value.examId) return
    saveDraft()
  },
  { deep: true }
)

onMounted(() => {
  syncActiveExamSession()
  syncClientSessionId()
  loadPaper()
  window.addEventListener('beforeunload', handleBeforeUnload)
  window.addEventListener('contextmenu', handleContextMenu)
})

onBeforeRouteLeave(to => {
  if (!submitSucceeded.value && to.fullPath !== route.fullPath) {
    return false
  }
})

onBeforeUnmount(() => {
  stopHeartbeat()
  stop()
  window.removeEventListener('beforeunload', handleBeforeUnload)
  window.removeEventListener('contextmenu', handleContextMenu)
  if (!submitSucceeded.value) {
    sendHeartbeat({ keepalive: true })
  }
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
