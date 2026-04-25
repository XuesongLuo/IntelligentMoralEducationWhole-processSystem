<template>
  <div class="resource-page">
    <div class="resource-content">
      <h1>{{ categoryName || '德育资源学习' }}</h1>

      <el-card class="list-card" shadow="never">
        <div class="back-row">
          <el-button @click="goBack">上一级</el-button>
        </div>

        <div class="header-row">
          <div>
            <p>点击跳转即可进入外部学习资源，点击过即视为完成。</p>
          </div>
          <div class="summary-chip">
            共 {{ total }} 条资源
          </div>
        </div>

        <el-table :data="records" border class="resource-table">
          <el-table-column type="index" label="序号" width="80" />
          <el-table-column prop="title" label="标题" min-width="360" />
          <el-table-column label="学习状态" width="140">
            <template #default="{ row }">
              <el-tag :type="row.completed ? 'success' : 'info'">
                {{ row.completed ? '已完成' : '未完成' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="点击跳转" width="150">
            <template #default="{ row }">
              <el-button type="primary" :disabled="!row.url" @click="openResource(row)">
                点击跳转
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
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getResourceItems,
  submitResourceHeartbeat,
  visitResource
} from '@/api/resource'

const route = useRoute()
const router = useRouter()

const categoryName = ref('')
const total = ref(0)
const pageNum = ref(1)
const pageSize = ref(10)
const records = ref([])
let heartbeatTimer = null

const categoryId = () => Number(route.params.categoryId)

function goBack() {
  router.push('/student/resource-study')
}

async function loadResources() {
  try {
    const res = await getResourceItems(categoryId(), {
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
  if (!row.url) {
    ElMessage.warning('该资源暂未配置链接')
    return
  }

  try {
    const res = await visitResource(row.id)
    const data = res.data?.data || res.data || {}
    window.open(data.url || row.url, '_blank', 'noopener')
    row.completed = true
    row.clickCount = data.clickCount || (row.clickCount || 0) + 1
  } catch (error) {
    ElMessage.error('打开资源失败')
  }
}

function handlePageChange(page) {
  pageNum.value = page
  loadResources()
}

async function sendHeartbeat() {
  try {
    await submitResourceHeartbeat({ categoryId: categoryId() })
  } catch (error) {
    console.error('resource heartbeat failed', error)
  }
}

function startHeartbeat() {
  sendHeartbeat()
  heartbeatTimer = window.setInterval(() => {
    sendHeartbeat()
  }, 30000)
}

watch(
  () => route.params.categoryId,
  () => {
    pageNum.value = 1
    loadResources()
  }
)

onMounted(() => {
  loadResources()
  startHeartbeat()
})

onBeforeUnmount(() => {
  if (heartbeatTimer) {
    window.clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
})
</script>

<style scoped>
.resource-page {
  min-height: calc(100vh - 64px);
  background: linear-gradient(180deg, #f4f7fb 0%, #edf3ff 100%);
  overflow-x: hidden;
}
  
.resource-content {
  width: min(72vw, calc(100% - 32px));
  max-width: 1280px;
  margin: 20px auto;
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
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.header-row p {
  margin: 0;
  color: #5a6a85;
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

@media (max-width: 720px) {
  .resource-content {
    width: calc(100% - 24px);
  }

  h1 {
    font-size: 40px;
  }

  .header-row {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
