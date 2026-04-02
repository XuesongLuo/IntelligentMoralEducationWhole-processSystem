<template>
  <div class="page-wrap">

    <div class="main-box">
      <h1>德育画像构建与考试</h1>

      <el-card class="panel" shadow="never">
        <div class="back-row">
          <el-button @click="goBack">上一级</el-button>
        </div>

        <div class="module-actions">
          <div class="triangle-btn" @click="goNotice('survey')">画像构建</div>
          <div class="hexagon-btn" @click="goNotice('integrity')">诚信考核</div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goBack() {
  router.back()
}

function goNotice(type) {
  router.push(`/student/exam-notice/${type}`)
}
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
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 120px;
}
.triangle-btn,
.hexagon-btn {
  width: 220px;
  height: 220px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40px;
  cursor: pointer;
  transition: all 0.25s;
}
.triangle-btn {
  clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
  border: 2px solid #333;
}
.hexagon-btn {
  clip-path: polygon(25% 6%, 75% 6%, 100% 50%, 75% 94%, 25% 94%, 0% 50%);
  border: 2px solid #333;
}
.triangle-btn:hover,
.hexagon-btn:hover {
  color: #409eff;
  transform: translateY(-4px);
}
</style>