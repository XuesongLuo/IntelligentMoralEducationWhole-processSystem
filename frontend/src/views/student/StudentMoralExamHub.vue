<template>
  <div class="page-wrap">
    <div class="main-box">
      <h1>德育画像构建与考试</h1>

      <el-card class="panel" shadow="never">
        <div class="back-row">
          <el-button @click="goBack">上一级</el-button>
        </div>

        <div class="module-actions">
          <button class="exam-btn" type="button" @click="goNotice('survey')" aria-label="画像构建">
            <img :src="surveyButton" alt="画像构建" class="exam-btn-image" />
          </button>
          <button class="exam-btn" type="button" @click="goNotice('integrity')" aria-label="诚信考核">
            <img :src="integrityButton" alt="诚信考核" class="exam-btn-image" />
          </button>
          <button class="exam-btn" type="button" @click="goNotice('ideology')" aria-label="思政考试">
            <img :src="ideologyButton" alt="思政考试" class="exam-btn-image" />
          </button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import surveyButton from '@/assets/images/moral-exam/survey.png'
import integrityButton from '@/assets/images/moral-exam/integrity.png'
import ideologyButton from '@/assets/images/moral-exam/ideology.png'

const router = useRouter()

function goBack() {
  router.push('/student/home')
}

function goNotice(type) {
  router.push(`/student/exam-notice/${type}`)
}
</script>

<style scoped>
.page-wrap {
  min-height: calc(100vh - 64px);
  background: #f5f7fa;
  overflow-x: hidden;
}

.main-box {
  width: min(72vw, calc(100% - 32px));
  max-width: 1380px;
  margin: 20px auto;
}

h1 {
  text-align: center;
  font-size: 48px;
  margin-bottom: 30px;
}

.panel {
  min-height: 520px;
  border-radius: 16px;
}

.back-row {
  margin-bottom: 40px;
}

.module-actions {
  min-height: 360px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  align-items: center;
  justify-items: center;
  gap: 20px;
}

.exam-btn {
  width: 232px;
  height: 232px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
  transition: transform 0.25s;
}

.exam-btn:hover {
  transform: translateY(-4px);
}

.exam-btn-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

@media (max-width: 960px) {
  .main-box {
    width: calc(100% - 20px);
    max-width: none;
  }

  .module-actions {
    grid-template-columns: 1fr;
    gap: 28px;
  }
}
</style>
