<template>
  <div class="page-wrap">
    <div class="main-box">
      <h1>预录入名单管理</h1>

      <el-card class="panel" shadow="never">
        <div class="toolbar-row">
          <el-button @click="goBack">上一级</el-button>
          <div class="right-actions">
            <el-button type="primary" @click="openCreateDialog('student')">新增学生名单</el-button>
            <el-button type="primary" plain @click="openCreateDialog('teacher')">新增老师名单</el-button>
          </div>
        </div>

        <el-tabs v-model="activeTab" class="tabs-wrap">
          <el-tab-pane label="学生预录入名单" name="student">
            <el-table :data="studentRows" border stripe>
              <el-table-column type="index" label="序号" width="70" />
              <el-table-column prop="student_no" label="学号" width="180" />
              <el-table-column prop="real_name" label="姓名" width="160" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_enabled ? 'success' : 'info'">
                    {{ row.is_enabled ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="更新时间" />
              <el-table-column label="操作" width="180">
                <template #default="{ row }">
                  <el-button type="primary" link @click="openEditDialog('student', row)">编辑</el-button>
                  <el-button type="danger" link @click="removeStudent(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="老师预录入名单" name="teacher">
            <el-table :data="teacherRows" border stripe>
              <el-table-column type="index" label="序号" width="70" />
              <el-table-column prop="teacher_no" label="工号" width="180" />
              <el-table-column prop="real_name" label="姓名" width="160" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_enabled ? 'success' : 'info'">
                    {{ row.is_enabled ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="更新时间" />
              <el-table-column label="操作" width="180">
                <template #default="{ row }">
                  <el-button type="primary" link @click="openEditDialog('teacher', row)">编辑</el-button>
                  <el-button type="danger" link @click="removeTeacher(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="420px"
      :close-on-click-modal="false"
    >
      <el-form label-width="80px">
        <el-form-item :label="dialogType === 'student' ? '学号' : '工号'">
          <el-input v-model.trim="form.no" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model.trim="form.real_name" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="form.is_enabled"
            active-text="启用"
            inactive-text="禁用"
          />
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
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  createStudentRoster,
  createTeacherRoster,
  deleteStudentRoster,
  deleteTeacherRoster,
  getStudentRosterList,
  getTeacherRosterList,
  updateStudentRoster,
  updateTeacherRoster
} from '@/api/user'

const router = useRouter()
const activeTab = ref('student')
const studentRows = ref([])
const teacherRows = ref([])

const dialogVisible = ref(false)
const dialogMode = ref('create')
const dialogType = ref('student')
const editingId = ref(null)
const form = reactive({
  no: '',
  real_name: '',
  is_enabled: true
})

const dialogTitle = computed(() => {
  const target = dialogType.value === 'student' ? '学生' : '老师'
  return `${dialogMode.value === 'create' ? '新增' : '编辑'}${target}名单`
})

function goBack() {
  router.push('/teacher/home')
}

function resetForm() {
  form.no = ''
  form.real_name = ''
  form.is_enabled = true
}

async function loadAll() {
  const [studentRes, teacherRes] = await Promise.all([
    getStudentRosterList(),
    getTeacherRosterList()
  ])
  studentRows.value = studentRes.data || []
  teacherRows.value = teacherRes.data || []
}

function openCreateDialog(type) {
  dialogMode.value = 'create'
  dialogType.value = type
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(type, row) {
  dialogMode.value = 'edit'
  dialogType.value = type
  editingId.value = row.id
  form.no = type === 'student' ? row.student_no : row.teacher_no
  form.real_name = row.real_name
  form.is_enabled = !!row.is_enabled
  dialogVisible.value = true
}

function validateForm() {
  if (!form.no) {
    ElMessage.error(dialogType.value === 'student' ? '学号不能为空' : '工号不能为空')
    return false
  }
  if (!form.real_name) {
    ElMessage.error('姓名不能为空')
    return false
  }
  return true
}

async function submitDialog() {
  if (!validateForm()) return

  const data =
    dialogType.value === 'student'
      ? {
          student_no: form.no,
          real_name: form.real_name,
          is_enabled: form.is_enabled
        }
      : {
          teacher_no: form.no,
          real_name: form.real_name,
          is_enabled: form.is_enabled
        }

  try {
    if (dialogType.value === 'student') {
      if (dialogMode.value === 'create') {
        await createStudentRoster(data)
      } else {
        await updateStudentRoster(editingId.value, data)
      }
    } else if (dialogMode.value === 'create') {
      await createTeacherRoster(data)
    } else {
      await updateTeacherRoster(editingId.value, data)
    }

    ElMessage.success('保存成功')
    dialogVisible.value = false
    await loadAll()
  } catch (error) {
    const message = error?.response?.data?.detail || '保存失败，请稍后重试'
    ElMessage.error(message)
  }
}

async function removeStudent(row) {
  try {
    await ElMessageBox.confirm(`确认删除学生 ${row.student_no} ${row.real_name} 吗？`, '删除确认', {
      type: 'warning'
    })
  } catch {
    return
  }
  try {
    await deleteStudentRoster(row.id)
    ElMessage.success('删除成功')
    await loadAll()
  } catch (error) {
    const message = error?.response?.data?.detail || '删除失败，请稍后重试'
    ElMessage.error(message)
  }
}

async function removeTeacher(row) {
  try {
    await ElMessageBox.confirm(`确认删除老师 ${row.teacher_no} ${row.real_name} 吗？`, '删除确认', {
      type: 'warning'
    })
  } catch {
    return
  }
  try {
    await deleteTeacherRoster(row.id)
    ElMessage.success('删除成功')
    await loadAll()
  } catch (error) {
    const message = error?.response?.data?.detail || '删除失败，请稍后重试'
    ElMessage.error(message)
  }
}

onMounted(() => {
  loadAll()
})
</script>

<style scoped>
.page-wrap {
  min-height: 100vh;
  background: #f5f7fa;
}

.teacher-page {
  min-height: calc(100vh - 64px);
}

.main-box {
  width: min(72vw, calc(100% - 40px));
  max-width: 1380px;
  margin: 20px auto;
}

h1 {
  text-align: center;
  font-size: 44px;
  margin-bottom: 24px;
}

.panel {
  border-radius: 16px;
  min-height: 640px;
}

.toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.right-actions {
  display: flex;
  gap: 10px;
}

.tabs-wrap {
  margin-top: 6px;
}

@media (max-width: 960px) {
  .main-box {
    width: calc(100% - 20px);
    max-width: none;
  }
}
</style>
