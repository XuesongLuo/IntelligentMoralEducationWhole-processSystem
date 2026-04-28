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
            <el-table-column label="操作" width="460">
              <template #default="{ row }">
                <el-button
                  v-if="row.analysisReady"
                  type="primary"
                  link
                  @click="openDetail(row)"
                >
                  点击查看
                </el-button>
                <template v-else>
                  <el-button
                    v-if="row.analysisStatus === 'failed'"
                    type="danger"
                    link
                    @click="retryAnalysis(row)"
                  >
                    重新分析
                  </el-button>
                  <span v-if="row.analysisStatus === 'failed'" class="status-failed">
                    {{ failedAnalysisMessage }}
                  </span>
                  <span v-else class="status-tip">模型分析中...</span>
                </template>
                <el-button
                  v-if="row.analysisReady"
                  type="success"
                  link
                  @click="handleExportOne(row)"
                >
                  导出本次
                </el-button>
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

    <el-dialog
      v-model="globalExportDialogVisible"
      title="按筛选导出（全体）"
      width="620px"
      :close-on-click-modal="false"
    >
      <div class="global-export-form">
        <div class="field-row">
          <div class="field-label">账号类型</div>
          <el-radio-group v-model="globalFilter.accountScope">
            <el-radio value="teacher">仅老师</el-radio>
            <el-radio value="student">仅学生</el-radio>
            <el-radio value="all">全部人员</el-radio>
          </el-radio-group>
        </div>

        <div class="field-row">
          <div class="field-label">试卷/问卷类型（多选）</div>
          <el-select
            v-model="globalFilter.paperIds"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            placeholder="请选择问卷或试卷（问卷与试卷不能混选）"
            style="width: 100%"
            @change="handleGlobalPaperChange"
          >
            <el-option-group
              v-if="exportOptions.survey.length"
              label="问卷"
            >
              <el-option
                v-for="item in exportOptions.survey"
                :key="item.id"
                :label="item.label"
                :value="item.id"
              />
            </el-option-group>
            <el-option-group
              v-if="exportOptions.exam.length"
              label="试卷（科研诚信 / 思政）"
            >
              <el-option
                v-for="item in exportOptions.exam"
                :key="item.id"
                :label="item.label"
                :value="item.id"
              />
            </el-option-group>
          </el-select>

          <div class="quick-actions">
            <el-button size="small" @click="selectAllSurvey">全部问卷</el-button>
            <el-button size="small" @click="selectAllExam">全部试卷</el-button>
            <el-button size="small" @click="clearAllPapers">清空</el-button>
          </div>

          <div class="tip-text">
            说明：问卷与试卷不能同时导出，系统会按你选择的类别生成不同模板。
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="globalExportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmGlobalExport">确认导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { getTeacherStudentList } from '@/api/user'
import {
  exportExamResult,
  exportExamResultsByFilter,
  exportExamResultsByType,
  getExamResultList,
  getExportFilterOptions,
  retryExamResultAnalysis
} from '@/api/exam'
import { saveExcelBlob } from '@/utils/fileSave'
import { useTeacherViewStore } from '@/stores/teacherView'
import TeacherSidebar from '@/components/teacher/TeacherSidebar.vue'
import ResultDetailDialog from '@/components/common/ResultDetailDialog.vue'

const route = useRoute()
const router = useRouter()
const teacherViewStore = useTeacherViewStore()
const { sidebarCollapsed, selectedUser, userList } = storeToRefs(teacherViewStore)

const tableData = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const currentResultId = ref('')
const batchExportDialogVisible = ref(false)
const batchExportType = ref('survey')

const globalExportDialogVisible = ref(false)
const exportOptions = ref({
  survey: [],
  exam: []
})
const globalFilter = ref({
  accountScope: 'all',
  paperIds: []
})
const previousPaperIds = ref([])

const query = ref({
  pageNum: 1,
  pageSize: 10
})

const failedAnalysisMessage = '额度耗尽，联系管理员@DYQ'

const paperTypeById = computed(() => {
  const map = new Map()
  exportOptions.value.survey.forEach(item => map.set(item.id, item.paperType))
  exportOptions.value.exam.forEach(item => map.set(item.id, item.paperType))
  return map
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

async function retryAnalysis(row) {
  if (!selectedUser.value?.id) return
  try {
    await retryExamResultAnalysis(row.id, selectedUser.value.id)
    ElMessage.success('已触发重新分析，请稍后刷新查看')
    loadList()
  } catch (error) {
    const message = error?.response?.data?.detail || failedAnalysisMessage
    ElMessage.error(message)
  }
}

async function handleExportOne(row) {
  if (!selectedUser.value?.id) return
  try {
    const blob = await exportExamResult(row.id, selectedUser.value.id)
    const result = await saveExcelBlob(blob, `${formatPaperType(row.paperType)}_${row.title}_单次导出.xlsx`)
    if (result.canceled) return
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
    const result = await saveExcelBlob(
      blob,
      `${selectedUser.value.label}_${formatPaperType(batchExportType.value)}_全部导出.xlsx`
    )
    if (result.canceled) return
    batchExportDialogVisible.value = false
    ElMessage.success('导出成功')
  } catch (error) {
    const message = error?.response?.data?.detail || '导出失败，请稍后重试'
    ElMessage.error(message)
  }
}

async function loadExportOptions() {
  const res = await getExportFilterOptions()
  const data = res.data || {}
  exportOptions.value = {
    survey: Array.isArray(data.survey) ? data.survey : [],
    exam: Array.isArray(data.exam) ? data.exam : []
  }
}

async function openGlobalExportDialog() {
  try {
    await loadExportOptions()
    globalFilter.value.accountScope = 'all'
    globalFilter.value.paperIds = []
    previousPaperIds.value = []
    globalExportDialogVisible.value = true
  } catch (error) {
    const message = error?.response?.data?.detail || '获取导出筛选项失败'
    ElMessage.error(message)
  }
}

function detectSelectedCategory(paperIds) {
  const selectedTypes = new Set(
    paperIds.map(id => paperTypeById.value.get(id)).filter(Boolean)
  )
  const hasSurvey = selectedTypes.has('survey')
  const hasExam = selectedTypes.has('integrity') || selectedTypes.has('ideology')
  if (hasSurvey && hasExam) return 'mixed'
  if (hasSurvey) return 'survey'
  if (hasExam) return 'exam'
  return 'none'
}

function handleGlobalPaperChange(values) {
  const category = detectSelectedCategory(values)
  if (category === 'mixed') {
    ElMessage.warning('问卷和试卷不能同时选择，请分开导出')
    globalFilter.value.paperIds = [...previousPaperIds.value]
    return
  }
  previousPaperIds.value = [...values]
}

function selectAllSurvey() {
  globalFilter.value.paperIds = exportOptions.value.survey.map(item => item.id)
  previousPaperIds.value = [...globalFilter.value.paperIds]
}

function selectAllExam() {
  globalFilter.value.paperIds = exportOptions.value.exam.map(item => item.id)
  previousPaperIds.value = [...globalFilter.value.paperIds]
}

function clearAllPapers() {
  globalFilter.value.paperIds = []
  previousPaperIds.value = []
}

async function confirmGlobalExport() {
  if (!globalFilter.value.paperIds.length) {
    ElMessage.warning('请先选择至少一套问卷或试卷')
    return
  }

  const selectedCategory = detectSelectedCategory(globalFilter.value.paperIds)
  if (selectedCategory === 'mixed') {
    ElMessage.warning('问卷和试卷不能同时选择，请分开导出')
    return
  }

  try {
    const blob = await exportExamResultsByFilter({
      accountScope: globalFilter.value.accountScope,
      paperIds: globalFilter.value.paperIds
    })
    const categoryText = selectedCategory === 'survey' ? '问卷' : '试卷'
    const accountText =
      globalFilter.value.accountScope === 'teacher'
        ? '仅老师'
        : globalFilter.value.accountScope === 'student'
        ? '仅学生'
        : '全部人员'
    const result = await saveExcelBlob(blob, `${categoryText}_${accountText}_筛选导出.xlsx`)
    if (result.canceled) return
    globalExportDialogVisible.value = false
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

watch(
  () => route.query.globalExport,
  async val => {
    if (!val) return
    await openGlobalExportDialog()
    const nextQuery = { ...route.query }
    delete nextQuery.globalExport
    router.replace({ path: route.path, query: nextQuery })
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
  min-height: calc(100vh - 64px);
  background: #f5f7fa;
  position: relative;
  overflow-x: hidden;
}

.main-box {
  width: min(72vw, calc(100% - 40px));
  max-width: 1380px;
  margin: 20px auto;
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
}

.status-failed {
  color: #f56c6c;
  margin-left: 8px;
}

.batch-export-type-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
}

.batch-export-type-group :deep(.el-radio) {
  margin-right: 0;
}

.global-export-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-label {
  color: #303133;
  font-weight: 600;
}

.quick-actions {
  display: flex;
  gap: 10px;
}

.tip-text {
  color: #909399;
  font-size: 13px;
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

@media (max-width: 960px) {
  .main-box {
    width: calc(100% - 20px);
    max-width: none;
  }
}
</style>
