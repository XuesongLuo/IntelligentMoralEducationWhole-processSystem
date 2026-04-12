<template>
  <div class="teacher-page">
    <TeacherSidebar
      :collapsed="sidebarCollapsed"
      :selected-user="selectedUser"
      :user-list="userList"
      @toggle="toggleSidebar"
      @select-user="handleSelectUser"
    />
    <div
      v-if="!sidebarCollapsed"
      class="page-mask"
      @click="toggleSidebar"
    />

    <div class="content" :class="{ expand: sidebarCollapsed, dimmed: !sidebarCollapsed }">
      <h1>德育资源学习</h1>

      <el-card class="hub-card" shadow="never">
        <div class="back-row">
          <el-button @click="goBack">上一页</el-button>
        </div>

        <div class="page-header">
          <p>当前查看对象：{{ selectedUserLabel }}</p>
        </div>

        <div class="hub-grid">
          <div
            v-for="item in categories"
            :key="item.id"
            class="hub-item"
            @click="goCategory(item)"
          >
            <div class="circle-button">
              <span>{{ item.name }}</span>
            </div>
            <div class="battery-wrap">
              <div class="battery">
                <span
                  v-for="segment in 10"
                  :key="segment"
                  class="battery-segment"
                  :class="{ active: segment <= filledSegments(item.progress) }"
                />
                <span class="battery-cap" />
              </div>
              <div class="progress-text">{{ formatPercent(item.progress) }}</div>
            </div>
          </div>
        </div>

        <el-empty
          v-if="!categories.length"
          description="暂时还没有可学习的德育资源场景"
        />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import TeacherSidebar from '@/components/teacher/TeacherSidebar.vue'
import { useTeacherViewStore } from '@/stores/teacherView'
import { getTeacherStudentList } from '@/api/user'
import { getResourceCategories, submitResourceHeartbeat } from '@/api/resource'

const router = useRouter()
const teacherViewStore = useTeacherViewStore()
const { sidebarCollapsed, selectedUser, userList, isViewingSelf } = storeToRefs(teacherViewStore)

const categories = ref([])
let heartbeatTimer = null

const selectedUserLabel = computed(() => {
  const user = selectedUser.value
  if (!user) return '未选择用户'
  return `${user.teacher_no || user.student_no || ''} ${user.real_name || ''}`.trim()
})

function formatPercent(value) {
  return `${Number(value || 0).toFixed(1)}%`
}

function filledSegments(progress) {
  return Math.max(0, Math.min(10, Math.round((Number(progress) || 0) / 10)))
}

function toggleSidebar() {
  teacherViewStore.toggleSidebar()
}

function handleSelectUser(user) {
  teacherViewStore.selectUser(user)
}

function goBack() {
  router.push('/teacher/home')
}

function goCategory(item) {
  router.push(`/teacher/resource-study/${item.id}`)
}

async function loadCategories() {
  if (!selectedUser.value) return

  try {
    const res = await getResourceCategories({ userId: selectedUser.value.id })
    categories.value = res.data?.items || res.data?.data?.items || res.data || []
  } catch (error) {
    ElMessage.error('获取资源学习场景失败')
  }
}

async function sendHeartbeat() {
  if (!isViewingSelf.value) return
  try {
    await submitResourceHeartbeat({})
  } catch (error) {
    console.error('teacher resource heartbeat failed', error)
  }
}

function startHeartbeat() {
  if (!isViewingSelf.value) return
  sendHeartbeat()
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

watch(
  () => selectedUser.value?.id,
  () => {
    loadCategories()
  },
  { immediate: true }
)

watch(
  () => isViewingSelf.value,
  value => {
    stopHeartbeat()
    if (value) {
      startHeartbeat()
    }
  },
  { immediate: true }
)

onMounted(async () => {
  const localUser = JSON.parse(localStorage.getItem('userInfo') || '{}')

  teacherViewStore.restore()
  const currentTeacher = {
    id: localUser.id,
    role: 'teacher',
    real_name: localUser.real_name,
    teacher_no: localUser.teacher_no,
    label: `${localUser.teacher_no || localUser.phone} ${localUser.real_name}`
  }

  try {
    const res = await getTeacherStudentList()
    const apiList = Array.isArray(res.data) ? res.data : []
    const mergedList = apiList.some(item => item.id === currentTeacher.id)
      ? apiList
      : [currentTeacher, ...apiList]

    if (!teacherViewStore.teacherUser) {
      teacherViewStore.init(currentTeacher, mergedList)
    } else {
      teacherViewStore.teacherUser = currentTeacher
      teacherViewStore.userList = mergedList
      if (
        !teacherViewStore.selectedUser ||
        !mergedList.some(item => item.id === teacherViewStore.selectedUser.id)
      ) {
        teacherViewStore.selectedUser = currentTeacher
      }
      teacherViewStore.persist()
    }
  } catch (error) {
    teacherViewStore.init(currentTeacher, [currentTeacher])
  }
})

onBeforeUnmount(() => {
  stopHeartbeat()
})
</script>

<style scoped>
.teacher-page {
  display: flex;
  min-height: calc(100vh - 64px);
  background: linear-gradient(180deg, #f4f7fb 0%, #edf3ff 100%);
  position: relative;
}

.content {
  width: min(1240px, calc(100% - 72px));
  margin: 30px auto;
  position: relative;
  z-index: 1200;
}

h1 {
  margin: 0 0 24px;
  text-align: center;
  font-size: 52px;
  color: #16335b;
}

.hub-card {
  border-radius: 28px;
  border: none;
}

.back-row {
  margin-bottom: 30px;
}

.page-header {
  margin-bottom: 28px;
  text-align: center;
}

.page-header p {
  margin: 0;
  color: #5a6a85;
  font-size: 16px;
}

.hub-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 28px 22px;
}

.hub-item {
  padding: 16px 12px 8px;
  border-radius: 22px;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  cursor: pointer;
}

.hub-item:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 36px rgba(30, 72, 132, 0.12);
}

.circle-button {
  width: 220px;
  height: 220px;
  margin: 0 auto 20px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 30% 25%, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.18) 30%, transparent 32%),
    linear-gradient(145deg, #2e6bba, #57a5ff);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  box-shadow: inset 0 2px 12px rgba(255, 255, 255, 0.16), 0 18px 28px rgba(46, 107, 186, 0.28);
}

.circle-button span {
  width: 70%;
  font-size: 28px;
  line-height: 1.45;
  font-weight: 600;
}

.battery-wrap {
  width: 78%;
  margin: 0 auto;
}

.battery {
  position: relative;
  padding: 4px 12px 4px 8px;
  border: 2px solid #9fb8d8;
  border-radius: 12px;
  background: #f8fbff;
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 4px;
}

.battery-cap {
  position: absolute;
  right: -8px;
  top: 50%;
  width: 6px;
  height: 18px;
  border-radius: 0 6px 6px 0;
  background: #9fb8d8;
  transform: translateY(-50%);
}

.battery-segment {
  height: 22px;
  border-radius: 6px;
  background: #dce8f5;
}

.battery-segment.active {
  background: linear-gradient(180deg, #67d46d, #2c9f43);
}

.progress-text {
  margin-top: 10px;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: #20426e;
}

.page-mask {
  position: fixed;
  inset: 64px 0 0 0;
  z-index: 1500;
  background: rgba(18, 30, 48, 0.28);
  backdrop-filter: blur(2px);
}

.content.dimmed {
  filter: brightness(0.88);
}

@media (max-width: 1180px) {
  .hub-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .content {
    width: calc(100% - 24px);
  }

  h1 {
    font-size: 40px;
  }

  .hub-grid {
    grid-template-columns: 1fr;
  }
}
</style>
