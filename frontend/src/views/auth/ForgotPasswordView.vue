<template>
  <AuthLayout>
    <div class="auth-title">密码找回</div>

    <el-form class="auth-form" @submit.prevent="handleSubmit">
      <AuthInput
        v-model="form.username"
        icon="◉"
        placeholder="学号/工号"
        :status="status.username"
        :error-message="errors.username"
        @blur="validateField('username')"
      />

      <AuthInput
        v-model="form.realName"
        icon="🪪"
        placeholder="真实姓名"
        :status="status.realName"
        :error-message="errors.realName"
        @blur="validateField('realName')"
      />

      <AuthInput
        v-model="form.newPassword"
        icon="🔒"
        type="password"
        placeholder="请输入新密码"
        :status="status.newPassword"
        :error-message="errors.newPassword"
        @blur="validateField('newPassword')"
      />

      <AuthInput
        v-model="form.confirmPassword"
        icon="🔒"
        type="password"
        placeholder="再次输入密码"
        :status="status.confirmPassword"
        :error-message="errors.confirmPassword"
        @blur="validateField('confirmPassword')"
      />

      <div class="btn-group">
        <el-button 
          class="auth-custom-btn submit-btn" 
          type="primary" 
          :loading="loading" 
          @click="handleSubmit"
        >
          提交
        </el-button>
        
        <el-button 
          class="auth-custom-btn back-btn" 
          @click="router.push('/login')"
        >
          返回
        </el-button>
      </div>
    </el-form>
  </AuthLayout>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '@/components/auth/AuthLayout.vue'
import AuthInput from '@/components/auth/AuthInput.vue'
import { forgotPasswordApi } from '@/api/auth'
import { isPassword, isRealName, isStudentOrWorkNo } from '@/utils/validators'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  realName: '',
  newPassword: '',
  confirmPassword: ''
})

const errors = reactive({
  username: '',
  realName: '',
  newPassword: '',
  confirmPassword: ''
})

function validate() {
  validateField('username')
  validateField('realName')
  validateField('newPassword')
  validateField('confirmPassword')
  return !Object.values(errors).some(Boolean)
}

function validateField(field) {
  if (field === 'username') {
    errors.username = ''
    if (!form.username) errors.username = '请输入学号/工号'
    else if (!isStudentOrWorkNo(form.username)) errors.username = '学号/工号格式不正确'
  }

  if (field === 'realName') {
    errors.realName = ''
    if (!form.realName) errors.realName = '请输入真实姓名'
    else if (!isRealName(form.realName)) errors.realName = '姓名格式不正确'
  }

  if (field === 'newPassword') {
    errors.newPassword = ''
    if (!form.newPassword) errors.newPassword = '请输入新密码'
    else if (!/^.{6,10}$/.test(form.newPassword)) errors.newPassword = '密码长度需为6-10位'

    if (form.confirmPassword) {
      validateField('confirmPassword')
    }
  }

  if (field === 'confirmPassword') {
    errors.confirmPassword = ''
    if (!form.confirmPassword) errors.confirmPassword = '请再次输入密码'
    else if (form.confirmPassword !== form.newPassword) errors.confirmPassword = '两次密码输入不一致'
  }
}

const status = computed(() => ({
  username: form.username ? (errors.username ? 'error' : 'success') : '',
  realName: form.realName ? (errors.realName ? 'error' : 'success') : '',
  newPassword: form.newPassword ? (errors.newPassword ? 'error' : 'success') : '',
  confirmPassword: form.confirmPassword ? (errors.confirmPassword ? 'error' : 'success') : ''
}))

async function handleSubmit() {
  if (!validate()) return

  try {
    loading.value = true
    await forgotPasswordApi({
      username: form.username,
      realName: form.realName,
      newPassword: form.newPassword
    })
    alert('密码重置成功，请重新登录')
    router.push('/login')
  } catch (error) {
    console.error(error)
    alert(error?.response?.data?.detail || error?.response?.data?.message || '找回失败，请确认学号和姓名是否匹配')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-title {
  font-size: 64px;
  font-weight: 500;
  text-align: center;
  margin: 10px 0 40px;
}

/* 按钮组容器 */
.btn-group {
  display: flex;
  flex-direction: row; /* 纵向排列以保证宽度100%对齐，或使用gap */
  gap: 20px;
  margin-top: 20px;
  /* 关键：确保容器不被 AuthInput 的状态图标空间挤压 */
  padding-right: 60px;  /* 对应 AuthInput 的 status-box 宽度 + 间距 */
  padding-left: 50px;   /* 对应 AuthInput 的 icon-box 宽度 */
}

/* 抽离公共按钮样式 */
.auth-custom-btn {
  flex: 1;             /* 平分剩余空间，确保两按钮等宽 */
  height: 58px;
  font-size: 24px;
  font-weight: 600;
  border-radius: 0;
  margin: 0 !important; /* 清除 Element 默认的 margin-left */
}

/* 提交按钮样式 - 对应设计稿蓝色 */
.submit-btn {
  background-color: #1f47f0 !important;
  border-color: #1f47f0 !important;
  color: #fff;
}

/* 返回按钮样式 - 对应设计稿灰色 */
.back-btn {
  background-color: #b9b9b9 !important;
  border-color: #b9b9b9 !important;
  color: #fff;
  
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .auth-title { font-size: 36px; margin-bottom: 25px; }
  .btn-group { gap: 15px; }
}
@media (max-width: 480px) {
  .auth-title { font-size: 30px; margin-bottom: 20px; }
  .btn-group { 
        flex-direction: column;
    }
}
</style>
