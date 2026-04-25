<template>
  <div class="page-wrap">

    <div class="main-box">
      <h1>德育画像构建与考试</h1>

      <el-card class="panel" shadow="never">
        <div class="back-row">
          <el-button @click="goBack">上一级</el-button>
        </div>

        <div class="module-actions">
          <div class="triangle-btn" @click="goNotice('survey')"><span>画像构建</span></div>
          <div class="hexagon-btn" @click="goNotice('integrity')"><span>诚信考核</span></div>
          <div class="square-btn" @click="goNotice('ideology')"><span>思政考试</span></div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useTeacherViewStore } from '@/stores/teacherView'

const router = useRouter()
const teacherViewStore = useTeacherViewStore()
const { isViewingSelf } = storeToRefs(teacherViewStore)

onMounted(() => {
  if (!teacherViewStore.teacherUser || !teacherViewStore.selectedUser) {
    teacherViewStore.restore()
  }
})

function goBack() {
    router.push('/teacher/home')
}

function goNotice(type) {
    if (!isViewingSelf.value) {
        ElMessage.warning('只有查看本人账号时才可进入考试页面')
        return
    }
    router.push(`/teacher/exam-notice/${type}`)
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
  display: flex;
  justify-content: center;
  align-items: center;
  gap: clamp(28px, 4vw, 56px);
  flex-wrap: wrap;
}
.triangle-btn,
.hexagon-btn,
.square-btn {
  width: 232px;
  height: 232px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  font-size: 34px;
  line-height: 1.25;
  font-weight: 500;
  padding: 20px;
  cursor: pointer;
  transition: all 0.25s;
  box-sizing: border-box;
  color: #303133;
}
.triangle-btn::before,
.triangle-btn::after,
.hexagon-btn::before,
.hexagon-btn::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.triangle-btn {
  padding-top: 58px;
}
.triangle-btn::before {
  background: #333;
  clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
}
.triangle-btn::after {
  inset: 3px;
  background: #fff;
  clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
}
.hexagon-btn {
  padding-inline: 34px;
}
.hexagon-btn::before {
  background: #333;
  clip-path: polygon(25% 6%, 75% 6%, 100% 50%, 75% 94%, 25% 94%, 0% 50%);
}
.hexagon-btn::after {
  inset: 3px;
  background: #fff;
  clip-path: polygon(25% 6%, 75% 6%, 100% 50%, 75% 94%, 25% 94%, 0% 50%);
}
.square-btn {
  border: 2px solid #333;
  border-radius: 24px;
}
.triangle-btn,
.hexagon-btn {
  isolation: isolate;
}
.triangle-btn,
.hexagon-btn,
.square-btn {
  z-index: 0;
}
.triangle-btn span,
.hexagon-btn span,
.square-btn span {
  position: relative;
  z-index: 1;
}
.triangle-btn:hover,
.hexagon-btn:hover,
.square-btn:hover {
  color: #409eff;
  transform: translateY(-4px);
}

@media (max-width: 960px) {
  .main-box {
    width: calc(100% - 20px);
    max-width: none;
  }

  .module-actions {
    flex-direction: column;
    gap: 28px;
  }
}
</style>
