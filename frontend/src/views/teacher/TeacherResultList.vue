<template>
  <div class="teacher-page">
    <TeacherSidebar
      :collapsed="sidebarCollapsed"
      :selected-user="selectedUser"
      :user-list="userList"
      @toggle="toggleSidebar"
      @select-user="handleSelectUser"
    />

    <div class="content" :class="{ expand: sidebarCollapsed }">
      <div class="main-box">
        <h1>结果查看</h1>

        <el-card class="panel" shadow="never">
          <div class="back-row">
            <el-button @click="goBack">上一级</el-button>
          </div>

          <el-table :data="tableData" border stripe>
            <el-table-column type="index" label="序号" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="submitTime" label="提交时间" width="220" />
            <el-table-column prop="durationMinutes" label="答题时间(min)" width="140" />
            <el-table-column label="操作" width="140">
              <template #default="{ row }">
                <el-button
                  v-if="row.analysisReady"
                  type="primary"
                  link
                  @click="openDetail(row)"
                >
                  点击查看
                </el-button>
                <span v-else style="color:#999;">模型分析中</span>
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
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { getTeacherStudentList } from '@/api/user'
import { useTeacherViewStore } from '@/stores/teacherView'
import { getExamResultList } from '@/api/exam'
import TeacherSidebar from '@/components/teacher/TeacherSidebar.vue'
import ResultDetailDialog from '@/components/common/ResultDetailDialog.vue'


const router = useRouter()
const teacherViewStore = useTeacherViewStore()
const { sidebarCollapsed, selectedUser, userList } = storeToRefs(teacherViewStore)

const tableData = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const currentResultId = ref('')

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

async function loadList() {
  if (!selectedUser.value) return
  const res = await getExamResultList({
    ...query.value,
    userId: selectedUser.value.id
  })

  //const res = await getExamResultList(query.value)
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

watch(
  () => selectedUser.value,
  () => {
    query.value.pageNum = 1
    loadList()
  },
  { immediate: true }
)

onMounted(async () => {
  //loadList()
  if (!teacherViewStore.teacherUser) {
    const localUser = JSON.parse(localStorage.getItem('userInfo') || '{}')

    teacherViewStore.restore()
    
    const res = await getTeacherStudentList()
    const userListFromApi = res.data?.data || []

    if (!teacherViewStore.teacherUser) {
      teacherViewStore.init(
        {
          id: localUser.id,
          role: 'teacher',
          account: localUser.account || localUser.username,
          name: localUser.name
        },
        userListFromApi
      )
    } else {
      teacherViewStore.userList = userListFromApi
      teacherViewStore.persist()
    }
  }
})
</script>

<style scoped>
.teacher-page {
  min-height: 100vh;
  background: #f5f7fa;
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
.back-row {
  margin-bottom: 24px;
}
.pagination-row {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>