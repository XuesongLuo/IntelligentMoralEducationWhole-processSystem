<template>
  <div class="teacher-page">
    <TeacherSidebar
      :collapsed="sidebarCollapsed"
      :selected-user="selectedUser"
      :user-list="userList"
      @toggle="toggleSidebar"
      @select-user="handleSelectUser"
    />
    <div v-if="!sidebarCollapsed" class="page-mask" @click="toggleSidebar" />

    <div class="content" :class="{ dimmed: !sidebarCollapsed }">
      <h1>{{ categoryName || '德育资源学习' }}</h1>

      <el-card class="list-card" shadow="never">
        <div class="back-row">
          <el-button @click="goBack">上一级</el-button>
        </div>

        <div class="header-row">
          <div>
            <p>当前查看对象：{{ selectedUserLabel }}</p>
          </div>
          <div class="actions-row">
            <div class="summary-chip">共 {{ total }} 条资源</div>
            <el-button type="primary" @click="openCreateDialog">新增资源</el-button>
          </div>
        </div>

        <el-table :data="records" border class="resource-table">
          <el-table-column type="index" label="序号" width="70" />
          <el-table-column prop="title" label="标题" min-width="280" />
          <el-table-column label="是否展示" width="120">
            <template #default="{ row }">
              <el-switch
                :model-value="row.isVisible"
                @change="value => handleVisibilityChange(row, value)"
              />
            </template>
          </el-table-column>
          <el-table-column label="学习状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.completed ? 'success' : 'info'">
                {{ row.completed ? '已完成' : '未完成' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="点击跳转" width="150">
            <template #default="{ row }">
              <el-button type="primary" plain :disabled="!row.url" @click="openResource(row)">
                点击跳转
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="编辑" width="120">
            <template #default="{ row }">
              <el-button type="warning" plain @click="openEditDialog(row)">
                编辑
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-row">
          <el-pagination
            background
            layout="prev, pager, next"
            :current-page="pageNum"
            :page-size="pageSize"
            :total="total"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="editingRow ? '编辑资源' : '新增资源'"
      width="520px"
      destroy-on-close
    >
      <el-form label-position="top">
        <el-form-item label="标题">
          <el-input v-model.trim="form.title" maxlength="255" />
        </el-form-item>
        <el-form-item label="链接地址">
          <el-input v-model.trim="form.url" placeholder="可稍后补充" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button
            v-if="editingRow"
            type="danger"
            plain
            @click="handleDeleteResource"
          >
            删除
          </el-button>
          <div class="dialog-actions">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitDialog">保存</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { storeToRefs } from 'pinia'
import TeacherSidebar from '@/components/teacher/TeacherSidebar.vue'
import { useTeacherViewStore } from '@/stores/teacherView'
import { getTeacherStudentList } from '@/api/user'
import {
  createResourceItem,
  deleteResourceItem,
  getResourceItems,
  submitResourceHeartbeat,
  updateResourceItem,
  updateResourceVisibility,
  visitResource
} from '@/api/resource'
import { getResourceCategoryFavicon } from '@/utils/resourceCategoryIcons'
import { APP_NAME, setDocumentMeta } from '@/utils/documentMeta'

const route = useRoute()
const router = useRouter()
const teacherViewStore = useTeacherViewStore()
const { sidebarCollapsed, selectedUser, userList, isViewingSelf } = storeToRefs(teacherViewStore)

const categoryName = ref('')
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const records = ref([])
const dialogVisible = ref(false)
const editingRow = ref(null)
const form = reactive({
  title: '',
  url: ''
})
let heartbeatTimer = null

const categoryId = computed(() => Number(route.params.categoryId))
const selectedUserLabel = computed(() => {
  const user = selectedUser.value
  if (!user) return '未选择用户'
  return `${user.teacher_no || user.student_no || ''} ${user.real_name || ''}`.trim()
})

function toggleSidebar() {
  teacherViewStore.toggleSidebar()
}

function handleSelectUser(user) {
  teacherViewStore.selectUser(user)
}

function goBack() {
  router.push('/teacher/resource-study')
}

async function loadResources() {
  if (!selectedUser.value) return

  try {
    const res = await getResourceItems(categoryId.value, {
      userId: selectedUser.value.id,
      pageNum: pageNum.value,
      pageSize: pageSize.value
    })
    const data = res.data?.data || res.data || {}
    categoryName.value = data.categoryName || ''
    records.value = data.records || []
    total.value = data.total || 0
    setDocumentMeta({
      title: `${categoryName.value || '德育资源学习'} - ${APP_NAME}`,
      favicon: getResourceCategoryFavicon(categoryName.value)
    })
  } catch (error) {
    ElMessage.error('获取资源列表失败')
  }
}

async function openResource(row) {
  if (!row.url) {
    ElMessage.warning('该资源暂未配置链接')
    return
  }

  try {
    if (isViewingSelf.value) {
      const res = await visitResource(row.id)
      const data = res.data?.data || res.data || {}
      window.open(data.url || row.url, '_blank', 'noopener')
      row.completed = true
      row.clickCount = data.clickCount || (row.clickCount || 0) + 1
      return
    }

    window.open(row.url, '_blank', 'noopener')
  } catch (error) {
    ElMessage.error('打开资源失败')
  }
}

async function handleVisibilityChange(row, value) {
  try {
    await updateResourceVisibility(row.id, value)
    row.isVisible = value
    ElMessage.success(value ? '资源已重新展示' : '资源已对学生隐藏')
  } catch (error) {
    row.isVisible = !value
    ElMessage.error('更新展示状态失败')
  }
}

function openCreateDialog() {
  editingRow.value = null
  form.title = ''
  form.url = ''
  dialogVisible.value = true
}

function openEditDialog(row) {
  editingRow.value = row
  form.title = row.title
  form.url = row.url
  dialogVisible.value = true
}

async function submitDialog() {
  if (!form.title) {
    ElMessage.warning('请填写标题')
    return
  }

  try {
    if (editingRow.value) {
      await updateResourceItem(editingRow.value.id, {
        title: form.title,
        url: form.url
      })
      ElMessage.success('资源已更新')
    } else {
      await createResourceItem(categoryId.value, {
        title: form.title,
        url: form.url
      })
      ElMessage.success('资源已新增')
    }
    dialogVisible.value = false
    loadResources()
  } catch (error) {
    ElMessage.error('保存资源失败')
  }
}

async function handleDeleteResource() {
  if (!editingRow.value) return

  try {
    await ElMessageBox.confirm(
      `确认删除资源“${editingRow.value.title}”吗？删除后学生的学习记录也会随之移除。`,
      '删除资源',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
  } catch (error) {
    return
  }

  try {
    await deleteResourceItem(editingRow.value.id)
    ElMessage.success('资源已删除')
    dialogVisible.value = false
    if (records.value.length === 1 && pageNum.value > 1) {
      pageNum.value -= 1
    }
    loadResources()
  } catch (error) {
    ElMessage.error('删除资源失败')
  }
}

function handlePageChange(page) {
  pageNum.value = page
  loadResources()
}

async function sendHeartbeat() {
  if (!isViewingSelf.value) return
  try {
    await submitResourceHeartbeat({ categoryId: categoryId.value })
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
  () => route.params.categoryId,
  () => {
    pageNum.value = 1
    loadResources()
  }
)

watch(
  () => selectedUser.value?.id,
  () => {
    pageNum.value = 1
    loadResources()
  },
  { immediate: true }
)

watch(
  () => isViewingSelf.value,
  value => {
    stopHeartbeat()
    if (value) startHeartbeat()
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
  overflow-x: hidden;
}

.content {
  width: min(72vw, calc(100% - 40px));
  max-width: 1280px;
  margin: 20px auto;
  position: relative;
  z-index: 1200;
}

h1 {
  margin: 0 0 24px;
  text-align: center;
  font-size: 52px;
  color: #16335b;
}

.list-card {
  border-radius: 28px;
  border: none;
}

.back-row {
  margin-bottom: 30px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.header-row p {
  margin: 0;
  color: #5a6a85;
}

.actions-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.summary-chip {
  min-width: 120px;
  padding: 10px 16px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1c4f92;
  text-align: center;
  font-weight: 600;
}

.resource-table {
  border-radius: 18px;
  overflow: hidden;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.dialog-actions {
  display: flex;
  gap: 12px;
  margin-left: auto;
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

@media (max-width: 840px) {
  .content {
    width: calc(100% - 20px);
    max-width: none;
  }

  h1 {
    font-size: 40px;
  }

  .actions-row {
    width: 100%;
    justify-content: space-between;
  }

  .header-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
