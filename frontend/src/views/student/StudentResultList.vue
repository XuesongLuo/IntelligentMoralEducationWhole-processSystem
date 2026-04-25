<template>
  <div class="page-wrap">
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
          <el-table-column prop="durationMinutes" label="答题时长(min)" width="140" />
          <el-table-column label="操作" width="260">
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
                <span v-if="row.analysisStatus === 'failed'" class="status-failed">分析失败</span>
                <span v-else class="status-pending">模型分析中...</span>
                <el-button
                  v-if="row.analysisStatus === 'failed'"
                  type="danger"
                  link
                  @click="retryAnalysis(row)"
                >
                  重新分析
                </el-button>
              </template>
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

    <ResultDetailDialog
      v-model="dialogVisible"
      :result-id="currentResultId"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getExamResultList, retryExamResultAnalysis } from '@/api/exam'
import ResultDetailDialog from '@/components/common/ResultDetailDialog.vue'

const router = useRouter()

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

async function loadList() {
  const res = await getExamResultList(query.value)
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
  try {
    await retryExamResultAnalysis(row.id)
    ElMessage.success('已触发重新分析，请稍后刷新查看')
    loadList()
  } catch (error) {
    const message = error?.response?.data?.detail || '重新分析失败，请稍后重试'
    ElMessage.error(message)
  }
}

onMounted(() => {
  loadList()
})
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

.status-pending {
  color: #999;
}

.status-failed {
  color: #f56c6c;
  margin-right: 8px;
}

.pagination-row {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

@media (max-width: 960px) {
  .main-box {
    width: calc(100% - 20px);
    max-width: none;
  }
}
</style>
