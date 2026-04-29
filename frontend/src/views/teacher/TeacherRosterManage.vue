<template>
  <div class="page-wrap">
    <div class="main-box">
      <h1>预录入名单管理</h1>

      <el-card class="panel" shadow="never">
        <div class="toolbar-row">
          <el-button @click="goBack">上一级</el-button>
          <div class="right-actions">
            <el-button plain @click="downloadTemplate">下载{{ activeTab === 'student' ? '学生' : '老师' }}模板</el-button>
            <el-button plain @click="triggerImport">批量导入{{ activeTab === 'student' ? '学生' : '老师' }}</el-button>
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
            <el-table :data="teacherRows" border stripe row-class-name="teacher-row-class">
              <el-table-column type="index" label="序号" width="70" />
              <el-table-column prop="teacher_no" label="工号" width="180" />
              <el-table-column prop="real_name" label="姓名" width="160" />
              <el-table-column label="标记" width="120">
                <template #default="{ row }">
                  <el-tag v-if="row.is_current_user" type="warning">当前登录</el-tag>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_enabled ? 'success' : 'info'">
                    {{ row.is_enabled ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="更新时间" />
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    link
                    :disabled="row.is_current_user"
                    @click="openEditDialog('teacher', row)"
                  >
                    编辑
                  </el-button>
                  <el-button
                    type="danger"
                    link
                    :disabled="row.is_current_user"
                    @click="removeTeacher(row)"
                  >
                    删除
                  </el-button>
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

    <input
      ref="studentImportInput"
      type="file"
      accept=".xlsx"
      class="hidden-file-input"
      @change="handleImportChange('student', $event)"
    />
    <input
      ref="teacherImportInput"
      type="file"
      accept=".xlsx"
      class="hidden-file-input"
      @change="handleImportChange('teacher', $event)"
    />
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
  downloadStudentRosterTemplate,
  downloadTeacherRosterTemplate,
  getStudentRosterList,
  getTeacherRosterList,
  importStudentRoster,
  importTeacherRoster,
  updateStudentRoster,
  updateTeacherRoster
} from '@/api/user'
import { saveExcelBlob } from '@/utils/fileSave'

const router = useRouter()
const activeTab = ref('student')
const studentRows = ref([])
const teacherRows = ref([])
const studentImportInput = ref(null)
const teacherImportInput = ref(null)

const dialogVisible = ref(false)
const dialogMode = ref('create')
const dialogType = ref('student')
const editingId = ref(null)
const form = reactive({
  no: '',
  real_name: '',
  is_enabled: true
})

const selfTeacherNo = computed(() => {
  const localUser = JSON.parse(localStorage.getItem('userInfo') || '{}')
  return localUser.teacher_no || ''
})

const dialogTitle = computed(() => {
  const target = dialogType.value === 'student' ? '学生' : '老师'
  return `${dialogMode.value === 'create' ? '新增' : '编辑'}${target}名单`
})

function goBack() {
  router.push('/teacher/home')
}

async function downloadTemplate() {
  try {
    if (activeTab.value === 'student') {
      const blob = await downloadStudentRosterTemplate()
      const result = await saveExcelBlob(blob, '学生预录入名单模板.xlsx')
      if (result.canceled) return
    } else {
      const blob = await downloadTeacherRosterTemplate()
      const result = await saveExcelBlob(blob, '老师预录入名单模板.xlsx')
      if (result.canceled) return
    }
    ElMessage.success('模板下载成功')
  } catch (error) {
    const message = error?.response?.data?.detail || '模板下载失败，请稍后重试'
    ElMessage.error(message)
  }
}

function triggerImport() {
  const targetInput = activeTab.value === 'student' ? studentImportInput.value : teacherImportInput.value
  if (!targetInput) return
  targetInput.value = ''
  targetInput.click()
}

function buildImportSummary(title, result) {
  const errors = Array.isArray(result?.errors) ? result.errors : []
  const lines = [
    `新增：${result?.createdCount || 0} 条`,
    `更新：${result?.updatedCount || 0} 条`,
    `跳过空行：${result?.skippedCount || 0} 条`,
    `错误：${result?.errorCount || 0} 条`
  ]
  if (errors.length) {
    lines.push('', '错误明细：', ...errors)
  }
  return ElMessageBox.alert(lines.join('\n'), title, {
    confirmButtonText: '知道了'
  })
}

async function handleImportChange(type, event) {
  const input = event.target
  const file = input?.files?.[0]
  if (!file) return

  try {
    const response =
      type === 'student'
        ? await importStudentRoster(file)
        : await importTeacherRoster(file)
    ElMessage.success(response?.message || '批量导入成功')
    await buildImportSummary(type === 'student' ? '学生名单导入结果' : '老师名单导入结果', response?.data || {})
    await loadAll()
  } catch (error) {
    const message = error?.response?.data?.detail || '批量导入失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    if (input) input.value = ''
  }
}

function resetForm() {
  form.no = ''
  form.real_name = ''
  form.is_enabled = true
}

function normalizeTeacherRows(rows) {
  return (rows || []).map(row => ({
    ...row,
    is_current_user: Boolean(row.is_current_user || (selfTeacherNo.value && row.teacher_no === selfTeacherNo.value))
  }))
}

async function loadAll() {
  const [studentRes, teacherRes] = await Promise.all([
    getStudentRosterList(),
    getTeacherRosterList()
  ])
  studentRows.value = studentRes.data || []
  teacherRows.value = normalizeTeacherRows(teacherRes.data)
}

function openCreateDialog(type) {
  dialogMode.value = 'create'
  dialogType.value = type
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(type, row) {
  if (type === 'teacher' && row.is_current_user) {
    ElMessage.warning('不允许操作当前登录老师自己的预录入名单')
    return
  }

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
  if (row.is_current_user) {
    ElMessage.warning('不允许操作当前登录老师自己的预录入名单')
    return
  }

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
  min-height: calc(100vh - 64px);
  background: #f5f7fa;
  overflow-x: hidden;
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
  gap: 12px;
  flex-wrap: wrap;
}

.right-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.hidden-file-input {
  display: none;
}

.tabs-wrap {
  margin-top: 6px;
}

:deep(.el-button.is-disabled.is-link) {
  opacity: 0.45;
}

@media (max-width: 960px) {
  .main-box {
    width: calc(100% - 20px);
    max-width: none;
  }

  .toolbar-row,
  .right-actions {
    align-items: stretch;
  }
}
</style>
