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

    <div class="content" :class="{ dimmed: !sidebarCollapsed }">
      <div class="page-top">
        <el-button class="back-btn" type="primary" plain @click="goBack">
          返回资源学习
        </el-button>
      </div>

      <el-card class="list-card" shadow="never">
        <div class="header-row">
          <div>
            <h2>{{ categoryName || '德育资源学习' }}</h2>
            <p>当前查看对象：{{ selectedUserLabel }}</p>
          </div>
          <div class="actions-row">
            <div class="summary-chip">共 {{ total }} 条资源</div>
            <el-button type="primary" @click="openCreateDialog">
              新增资源
            </el-button>
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
              <el-button type="primary" plain @click="openResource(row)">
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
          <el-input v-model.trim="form.url" placeholder="https://example.com" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitDialog">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import TeacherSidebar from '@/components/teacher/TeacherSidebar.vue'
import { useTeacherViewStore } from '@/stores/teacherView'
import { getTeacherStudentList } from '@/api/user'
import {
  createResourceItem,
  getResourceItems,
  submitResourceHeartbeat,
  updateResourceItem,
  updateResourceVisibility,
  visitResource
} from '@/api/resource'

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
  } catch (error) {
    ElMessage.error('获取资源列表失败')
  }
}

async function openResource(row) {
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
  if (!form.title || !form.url) {
    ElMessage.warning('请完整填写标题和链接地址')
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
}

.content {
  width: min(1240px, calc(100% - 72px));
  margin: 0 auto;
  padding: 24px 20px 40px;
}

.page-top {
  margin-bottom: 18px;
}

.back-btn {
  min-width: 132px;
}

.list-card {
  border-radius: 28px;
  border: none;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.header-row h2 {
  margin: 0 0 10px;
  font-size: 34px;
  color: #16335b;
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

@media (max-width: 840px) {
  .header-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions-row {
    width: 100%;
    justify-content: space-between;
  }
}
.page-mask {
  position: fixed;
  inset: 64px 0 0 0;
  z-index: 1500;
  background: rgba(18, 30, 48, 0.28);
  backdrop-filter: blur(2px);
}
.teacher-page {
  position: relative;
}
.content {
  position: relative;
  z-index: 1200;
}
.content.dimmed {
  filter: brightness(0.88);
}
</style>
