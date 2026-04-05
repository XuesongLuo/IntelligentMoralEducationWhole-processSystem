<template>
  <div class="page-wrap">
  
    <div class="main-box">
      <h1>{{ pageTitle }}</h1>

      <el-card class="panel" shadow="never">
        <div class="back-row">
          <el-button @click="goBack">上一级</el-button>
        </div>

        <div class="notice-box">
          <div class="notice-inner">
            <h3>{{ type === 'survey' ? '问卷须知：' : '考核须知：' }}</h3>
            <div v-if="noticeList.length">
              <p v-for="(item, index) in noticeList" :key="index">{{ index + 1 }}. {{ item }}</p>
            </div>
            <div v-else>
              <p>1. 所有题均为必答题。</p>
              <p>2. 考试开始后请勿关闭浏览器。</p>
              <p>3. 到时自动提交。</p>
              <p>4. 提交前请认真检查。</p>
            </div>
          </div>

          <el-button type="primary" size="large" @click="startExam">
            我已知晓，开始答题
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getExamInfo, getExamNotice } from '@/api/exam'

const route = useRoute()
const router = useRouter()

const type = computed(() => route.params.type)
const examInfo = ref({})
const noticeList = ref([])

const currentRole = computed(() => {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  return userInfo.role || 'student'
})

const routePrefix = computed(() => {
  return currentRole.value === 'teacher' ? '/teacher' : '/student'
})


const pageTitle = computed(() => {
  return type.value === 'survey' ? '画像构建' : '诚信考核'
})

function goBack() {
  router.back()
}

async function loadData() {
  const [noticeRes, infoRes] = await Promise.all([
    getExamNotice(type.value),
    getExamInfo(type.value)
  ])
  noticeList.value = noticeRes.data?.items || []
  examInfo.value = infoRes.data || {}
}

function startExam() {
  router.push(`${routePrefix.value}/exam-paper/${type.value}/${examInfo.value.examId}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-wrap {
  min-height: 100vh;
  background: #f5f7fa;
}
.main-box {
  width: 1100px;
  margin: 30px auto;
}
h1 {
  text-align: center;
  font-size: 52px;
  margin-bottom: 24px;
}
.panel {
  min-height: 560px;
  border-radius: 16px;
}
.back-row {
  margin-bottom: 30px;
}
.notice-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}
.notice-inner {
  width: 420px;
  min-height: 260px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
}
.notice-inner p {
  line-height: 2;
}
</style>