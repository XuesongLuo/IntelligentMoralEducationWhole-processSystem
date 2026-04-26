<template>
  <AuthLayout>
    <div class="auth-title">欢迎回来</div>

    <form class="auth-form" @submit.prevent="handleLogin">
      <AuthInput
        v-model="form.account"
        :icon-image="userIcon"
        icon-alt="用户"
        placeholder="用户名"
        :status="inputStatus.account"
        :error-message="errors.account"
      />

      <AuthInput
        v-model="form.password"
        :icon-image="passwordIcon"
        icon-alt="密码"
        type="password"
        placeholder="密码"
        :status="inputStatus.password"
        :error-message="errors.password"
      />

      <div class="auth-link-row">
        <router-link to="/ResetPassword" class="auth-link">忘记密码?</router-link>
      </div>

      <el-button class="action-btn btn-green" native-type="submit" :loading="loading">
        登录
      </el-button>

      <el-button class="action-btn btn-blue" @click="router.push('/register')">
        注册
      </el-button>
    </form>

    <div class="auth-footer-tip">如有登录问题，请联系管理员 DYQ</div>
  </AuthLayout>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import AuthLayout from '@/components/auth/AuthLayout.vue'
import AuthInput from '@/components/auth/AuthInput.vue'
import { loginApi } from '@/api/auth'
import { isAccount, isPassword } from '@/utils/validators'
import userIcon from '@/assets/images/auth/用户.svg'
import passwordIcon from '@/assets/images/auth/密码.svg'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  account: '',
  password: ''
})

const errors = reactive({
  account: '',
  password: ''
})

function validate() {
  errors.account = ''
  errors.password = ''

  if (!form.account) {
    errors.account = '请输入学号或手机号'
  } else if (!isAccount(form.account)) {
    errors.account = '账号格式不正确'
  }

  if (!form.password) {
    errors.password = '请输入密码'
  } else if (!isPassword(form.password)) {
    errors.password = '密码长度需为 6-10 位'
  }

  return !errors.account && !errors.password
}

const inputStatus = computed(() => ({
  account: form.account ? (errors.account ? 'error' : 'success') : '',
  password: form.password ? (errors.password ? 'error' : 'success') : ''
}))

async function handleLogin() {
  if (!validate()) return

  try {
    loading.value = true

    const res = await loginApi({
      account: form.account,
      password: form.password
    })

    const bizData = res?.data || {}
    const token = bizData.token
    const userInfo = bizData.user_info
    const role = userInfo?.role

    if (!token) {
      throw new Error('登录返回缺少 token')
    }
    if (!userInfo) {
      throw new Error('登录返回缺少 user_info')
    }
    if (!role) {
      throw new Error('登录返回缺少 role')
    }

    localStorage.setItem('token', token || '')
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    localStorage.setItem('role', role || '')

    router.push(role === 'teacher' ? '/teacher/home' : '/student/home')
  } catch (error) {
    ElMessage.error(
      error?.response?.data?.detail ||
        error?.response?.data?.message ||
        error?.message ||
        '登录失败，请检查账号或密码'
    )
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
  margin-bottom: 50px;
  letter-spacing: 4px;
}

.auth-form {
  width: 100%;
}

.auth-link-row {
  text-align: right;
  margin: -15px 60px 45px 0;
}

.auth-link {
  color: #5daaf7;
  text-decoration: none;
  font-size: 18px;
}

.action-btn {
  width: calc(100% - 110px) !important;
  margin-left: 50px !important;
  height: 64px;
  font-size: 26px;
  font-weight: 600;
  border: none;
  border-radius: 0;
  margin-bottom: 25px;
  color: #fff;
  display: block;
}

.btn-green {
  background-color: #8aba35 !important;
}

.btn-green:hover {
  opacity: 0.9;
}

.btn-blue {
  background-color: #1f47f0 !important;
}

.btn-blue:hover {
  opacity: 0.9;
}

.auth-footer-tip {
  margin-top: 80px;
  width: 100%;
  text-align: center;
}

@media (max-width: 1024px) {
  .auth-title {
    font-size: 36px;
    margin-bottom: 25px;
  }
}

@media (max-width: 480px) {
  .auth-title {
    font-size: 30px;
    margin-bottom: 20px;
  }
}
</style>
