<template>
  <el-dialog
    :model-value="modelValue"
    width="90%"
    top="4vh"
    destroy-on-close
    :close-on-click-modal="false"
    @close="closeDialog"
  >
    <template #header>
      <div class="dialog-header">
        <span>{{ detail.paperName || '试卷名称' }}</span>
      </div>
    </template>

    <div class="detail-layout" v-loading="loading">
      <div class="left-info">
        <el-card shadow="never">
          <p>用户编号：{{ detail.studentNo }}</p>
          <p>姓名：{{ detail.realName }}</p>
          <p>提交时间：{{ detail.submitTime }}</p>
          <p>答题时间：{{ detail.durationMinutes }} min</p>
        </el-card>
      </div>

      <div class="middle-answer">
        <el-card shadow="never">
          <div class="answer-scroll">
            <div
              v-for="(item, index) in detail.answerList"
              :key="item.questionId"
              class="answer-item"
            >
              <div class="q-title">{{ index + 1 }}. {{ item.questionTitle }}</div>

              <div class="q-answer">
                <span class="label">我的答案：</span>
                <span>{{ formatAnswer(item.answer) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <div class="right-analysis">
        <el-card shadow="never">
          <h3>模型智能分析结果</h3>

          <div class="analysis-scroll">
            <template v-if="detail.aiAnalysis?.dimensions?.length">
              <div
                v-for="item in detail.aiAnalysis.dimensions"
                :key="item.dimension"
                class="score-card"
              >
                <div class="score-head">
                  <span>{{ item.dimension }}</span>
                  <el-tag type="primary">{{ item.score }}分</el-tag>
                </div>
                <p>{{ item.reason }}</p>
              </div>

              <div class="summary-box">
                <h4>综合结论</h4>
                <p>{{ detail.aiAnalysis.summary || '-' }}</p>
              </div>
            </template>

            <div v-else class="summary-box empty-summary">
              <h4>分析状态</h4>
              <p>{{ detail.aiAnalysis?.summary || '分析结果暂未生成' }}</p>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getExamResultDetail } from '@/api/exam'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  resultId: {
    type: [String, Number],
    default: ''
  },
  userId: {
    type: [String, Number],
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const loading = ref(false)
const detail = ref({
  paperName: '',
  studentNo: '',
  realName: '',
  submitTime: '',
  durationMinutes: 0,
  answerList: [],
  aiAnalysis: {
    dimensions: [],
    summary: ''
  }
})

function closeDialog() {
  emit('update:modelValue', false)
}

function formatAnswer(answer) {
  if (Array.isArray(answer)) return answer.join('、')
  if (answer === true) return '正确'
  if (answer === false) return '错误'
  if (answer === null || answer === undefined || answer === '') return '-'
  if (typeof answer === 'object') {
    const selected = Array.isArray(answer.selected)
      ? answer.selected
      : answer.selected
        ? [answer.selected]
        : []
    const extras = answer.extras && typeof answer.extras === 'object' ? answer.extras : {}

    if (selected.length) {
      return selected
        .map(item => {
          const extraValue = extras[item]
          if (Array.isArray(extraValue) && extraValue.length) {
            return `${item}（补充：${extraValue.filter(Boolean).join('、')}）`
          }
          if (typeof extraValue === 'string' && extraValue.trim()) {
            return `${item}（补充：${extraValue.trim()}）`
          }
          return item
        })
        .join('；')
    }
    return JSON.stringify(answer)
  }
  return String(answer)
}

async function loadDetail() {
  if (!props.resultId || !props.modelValue) return

  loading.value = true
  try {
    const res = await getExamResultDetail(props.resultId, props.userId)
    detail.value = res.data
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.modelValue, props.resultId, props.userId],
  () => {
    loadDetail()
  },
  { immediate: true }
)
</script>

<style scoped>
.detail-layout {
  display: grid;
  grid-template-columns: 240px 1fr 320px;
  gap: 16px;
  min-height: 620px;
}

.left-info,
.middle-answer,
.right-analysis {
  min-height: 620px;
}

.answer-scroll,
.analysis-scroll {
  height: 560px;
  overflow-y: auto;
}

.answer-item {
  padding: 16px 0;
  border-bottom: 1px solid #ebeef5;
}

.q-title {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.8;
  margin-bottom: 10px;
}

.q-answer {
  color: #606266;
}

.label {
  font-weight: 600;
}

.score-card {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 14px;
}

.score-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.summary-box {
  margin-top: 18px;
  padding: 14px;
  background: #f8fafc;
  border-radius: 10px;
}

.empty-summary {
  margin-top: 0;
}
</style>
