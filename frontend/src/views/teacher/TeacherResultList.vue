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
      <div class="main-box">
        <h1>结果查看</h1>

        <el-card class="panel" shadow="never">
          <div class="toolbar-row">
            <el-button @click="goBack">上一级</el-button>
            <el-button type="warning" @click="openBatchExportDialog">一键导出同类型</el-button>
          </div>
          <div class="viewing-row">
            <span>正在查看：{{ selectedUser?.label || '-' }}</span>
          </div>

          <el-table :data="tableData" border stripe>
            <el-table-column type="index" label="序号" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="paperType" label="类型" width="130">
              <template #default="{ row }">
                {{ formatPaperType(row.paperType) }}
              </template>
            </el-table-column>
            <el-table-column prop="submitTime" label="提交时间" width="220" />
            <el-table-column prop="durationMinutes" label="答题时长(min)" width="130" />
            <el-table-column label="操作" width="360">
              <template #default="{ row }">
                <el-button
                  v-if="row.analysisReady"
                  type="primary"
                  link
                  @click="openDetail(row)"
                >
                  点击查看
                </el-button>
                <span v-else class="status-tip">模型分析中...</span>
                <el-button type="success" link @click="handleExportOne(row)">导出本次</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-row">
            <el-pagination
              background
              layout="prev, pager, next"
              :page-size="query.pageSize"
              :current-page="query.pageNum"
              :total="total"
              @current-change="handlePageChange"
            />
          </div>
        </el-card>
      </div>
    </div>

    <ResultDetailDialog
      v-model="dialogVisible"
      :result-id="currentResultId"
      :user-id="selectedUser?.id"
    />

    <el-dialog
      v-model="batchExportDialogVisible"
      title="选择导出类型"
      width="360px"
      :close-on-click-modal="false"
    >
      <el-radio-group v-model="batchExportType" class="batch-export-type-group">
        <el-radio value="survey">问卷</el-radio>
        <el-radio value="integrity">科研诚信试卷</el-radio>
        <el-radio value="ideology">思政试卷</el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="batchExportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchExport">确认导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { getTeacherStudentList } from '@/api/user'
import { exportExamResult, exportExamResultsByType, getExamResultList } from '@/api/exam'
import { useTeacherViewStore } from '@/stores/teacherView'
import TeacherSidebar from '@/components/teacher/TeacherSidebar.vue'
import ResultDetailDialog from '@/components/common/ResultDetailDialog.vue'

const router = useRouter()
const teacherViewStore = useTeacherViewStore()
const { sidebarCollapsed, selectedUser, userList } = storeToRefs(teacherViewStore)

const tableData = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const currentResultId = ref('')
const batchExportDialogVisible = ref(false)
const batchExportType = ref('survey')

const query = ref({
  pageNum: 1,
  pageSize: 10
})

function goBack() {
  router.back()
}

function toggleSidebar() {
  teacherViewStore.toggleSidebar()
}

function handleSelectUser(user) {
  teacherViewStore.selectUser(user)
}

function formatPaperType(type) {
  return {
    survey: '问卷',
    integrity: '科研诚信试卷',
    ideology: '思政试卷'
  }[type] || type
}

async function loadList() {
  if (!selectedUser.value) return
  const res = await getExamResultList({
    ...query.value,
    userId: selectedUser.value.id
  })
  tableData.value = res.data.records || []
  total.value = res.data.total || 0
}

function handlePageChange(page) {
  query.value.pageNum = page
  loadList()
}

function openDetail(row) {
  currentResultId.value = row.id
  dialogVisible.value = true
}

function triggerFileDownload(blob, fileName) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

async function handleExportOne(row) {
  if (!selectedUser.value?.id) return
  try {
    const blob = await exportExamResult(row.id, selectedUser.value.id)
    triggerFileDownload(blob, `${formatPaperType(row.paperType)}_${row.title}_单次导出.xlsx`)
    ElMessage.success('导出成功')
  } catch (error) {
    const message = error?.response?.data?.detail || '导出失败，请稍后重试'
    ElMessage.error(message)
  }
}

function openBatchExportDialog() {
  batchExportType.value = 'survey'
  batchExportDialogVisible.value = true
}

async function confirmBatchExport() {
  if (!selectedUser.value?.id) return
  try {
    const blob = await exportExamResultsByType(selectedUser.value.id, batchExportType.value)
    triggerFileDownload(
      blob,
      `${selectedUser.value.label}_${formatPaperType(batchExportType.value)}_全部导出.xlsx`
    )
    batchExportDialogVisible.value = false
    ElMessage.success('导出成功')
  } catch (error) {
    const message = error?.response?.data?.detail || '导出失败，请稍后重试'
    ElMessage.error(message)
  }
}

watch(
  () => selectedUser.value,
  () => {
    query.value.pageNum = 1
    loadList()
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
    console.error('获取老师侧边栏用户列表失败：', error)
    teacherViewStore.init(currentTeacher, [currentTeacher])
  }
})
</script>

<style scoped>
.teacher-page {
  min-height: 100vh;
  background: #f5f7fa;
  position: relative;
}

.main-box {
  width: 1200px;
  margin: 30px auto;
}

h1 {
  text-align: center;
  font-size: 52px;
  margin-bottom: 24px;
}

.panel {
  border-radius: 16px;
  min-height: 560px;
}

.toolbar-row {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.viewing-row {
  margin-bottom: 16px;
  color: #606266;
  font-weight: 500;
}

.status-tip {
  color: #999;
  margin-right: 8px;
}

.batch-export-type-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pagination-row {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.page-mask {
  position: fixed;
  inset: 64px 0 0 0;
  z-index: 1500;
  background: rgba(18, 30, 48, 0.28);
  backdrop-filter: blur(2px);
}

.content {
  position: relative;
  z-index: 1200;
}

.content.dimmed {
  filter: brightness(0.88);
}
</style>
