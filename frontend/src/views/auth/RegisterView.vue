<template>
  <AuthLayout>
    <div class="auth-title">账号注册</div>

    <form class="auth-form" @submit.prevent="handleRegister">
      <AuthInput
        v-model="currentNo"
        icon="◉"
        :placeholder="form.role === 'student' ? '请输入学号' : '请输入工号'"
        :status="status.no"
        :error-message="errors.no"
        @blur="validateField('no')"
      />

      <AuthInput
        v-model="form.password"
        icon="🔐"
        type="password"
        placeholder="设置6-10位登录密码"
        :status="status.password"
        :error-message="errors.password"
        @blur="validateField('password')"
      />

      <AuthInput
        v-model="form.confirmPassword"
        icon="🔐"
        type="password"
        placeholder="再次输入密码"
        :status="status.confirmPassword"
        :error-message="errors.confirmPassword"
        @blur="validateField('confirmPassword')"
      />

      <AuthInput
        v-model="form.real_name"
        icon="👤"
        placeholder="姓名验证，请务必输入真实姓名"
        :status="status.real_name"
        :error-message="errors.real_name"
        @blur="validateField('real_name')"
      />

      <AuthInput
        v-model="form.phone"
        icon="📫"
        placeholder="输入手机号"
        :status="status.phone"
        :error-message="errors.phone"
        @blur="validateField('phone')"
      />

      <AuthInput
        v-model="form.smsCode"
        icon="✔"
        placeholder="输入手机验证码"
        :action-text="smsActionText"
        :status="status.smsCode"
        :error-message="errors.smsCode"
        @action="handleSendCode"
        @blur="validateField('smsCode')"
      />

      <div class="role-selection-bar">
        <div class="role-label-group">
          <span class="role-main-label">账号类型</span>
          <span class="role-sub-label">{{ form.role === 'teacher' ? '老师' : '学生' }}</span>
        </div>
        <div class="role-switch-container">
          <span :class="['role-text', { active: form.role === 'student' }]">学生</span>
          <AuthSwitch v-model="form.role" />
          <span :class="['role-text', { active: form.role === 'teacher' }]">老师</span>
        </div>
      </div>

      <transition name="expand">
        <div v-if="form.role === 'teacher'" class="dynamic-input-container">
          <div class="dynamic-input-wrapper">
            <AuthInput
              v-model="form.invite_code"
              icon="🎓"
              placeholder="请输入教师专属邀请码（必填）"
              :status="status.invite_code"
              :error-message="errors.invite_code"
              @blur="validateField('invite_code')"
            />
          </div>
        </div>
      </transition>

      <div class="agreement-row">
        <el-checkbox v-model="form.agree" class="custom-checkbox">
          <span class="agreement-text">勾选并同意 <a href="javascript:;" class="auth-link-inline">服务条款</a></span>
        </el-checkbox>

        <router-link to="/login" class="auth-link">已有账号?</router-link>
      </div>

      <el-button
        class="action-btn btn-green"
        native-type="submit"
        :loading="loading"
      >
        {{ loading ? '提交中...' : '注册并登录' }}
      </el-button>
    </form>
  </AuthLayout>
</template>

<script setup>
import { computed, reactive, ref, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '@/components/auth/AuthLayout.vue'
import AuthInput from '@/components/auth/AuthInput.vue'
import AuthSwitch from '@/components/auth/AuthSwitch.vue'
import { registerStudentApi, registerTeacherApi, sendSmsCodeApi } from '@/api/auth'
import {
  isInviteCode,
  isPhone,
  isRealName,
  isSmsCode,
  isStudentNo,
  isTeacherNo
} from '@/utils/validators'

const router = useRouter()
const loading = ref(false)

const sendingCode = ref(false)
const countdown = ref(0)
let timer = null

const form = reactive({
  student_no: '',
  teacher_no: '',
  password: '',
  confirmPassword: '',
  real_name: '',
  phone: '',
  smsCode: '',
  invite_code: '',
  role: 'student',
  agree: false
})

const errors = reactive({
  no: '',
  password: '',
  confirmPassword: '',
  real_name: '',
  phone: '',
  smsCode: '',
  invite_code: '',
  agree: ''
})

const status = computed(() => {
  const currentNo = form.role === 'student' ? form.student_no : form.teacher_no

  return {
    no: currentNo ? (errors.no ? 'error' : 'success') : '',
    password: form.password ? (errors.password ? 'error' : 'success') : '',
    confirmPassword: form.confirmPassword ? (errors.confirmPassword ? 'error' : 'success') : '',
    real_name: form.real_name ? (errors.real_name ? 'error' : 'success') : '',
    phone: form.phone ? (errors.phone ? 'error' : 'success') : '',
    smsCode: form.smsCode ? (errors.smsCode ? 'error' : 'success') : '',
    invite_code:
      form.role === 'teacher' && form.invite_code
        ? (errors.invite_code ? 'error' : 'success')
        : ''
  }
})

const currentNo = computed({
  get() {
    return form.role === 'student' ? form.student_no : form.teacher_no
  },
  set(value) {
    if (form.role === 'student') {
      form.student_no = value
    } else {
      form.teacher_no = value
    }
  }
})

const smsActionText = computed(() => {
  if (sendingCode.value) return '发送中...'
  if (countdown.value > 0) return `${countdown.value}s后重试`
  return '获取验证码'
})

function validate() {
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
  validateField('no')
  validateField('password')
  validateField('confirmPassword')
  validateField('real_name')
  validateField('phone')
  validateField('smsCode')
  if (form.role === 'teacher') validateField('invite_code')
  if (!form.agree) {
    alert('请先勾选服务条款')
    return false
  }
  return Object.values(errors).every(item => !item)
}

function validateField(field) {
  const currentNoValue = form.role === 'student' ? form.student_no : form.teacher_no

  if (field === 'no') {
    errors.no = ''
    if (!currentNoValue) {
      errors.no = form.role === 'student' ? '请输入学号' : '请输入工号'
    } else if (form.role === 'student' ? !isStudentNo(currentNoValue) : !isTeacherNo(currentNoValue)) {
      errors.no = form.role === 'student' ? '学号格式不正确' : '工号格式不正确'
    }
  }

  if (field === 'password') {
    errors.password = ''
    if (!form.password) {
      errors.password = '请输入密码'
    } else if (!/^.{6,10}$/.test(form.password)) {
      errors.password = '密码长度需为6-10位'
    }

    if (form.confirmPassword) {
      validateField('confirmPassword')
    }
  }

  if (field === 'confirmPassword') {
    errors.confirmPassword = ''
    if (!form.confirmPassword) {
      errors.confirmPassword = '请再次输入密码'
    } else if (form.confirmPassword !== form.password) {
      errors.confirmPassword = '两次输入密码不一致'
    }
  }

  if (field === 'real_name') {
    errors.real_name = ''
    if (!form.real_name) {
      errors.real_name = '请输入真实姓名'
    } else if (!isRealName(form.real_name)) {
      errors.real_name = '姓名格式不正确'
    }
  }

  if (field === 'phone') {
    errors.phone = ''
    if (!form.phone) {
      errors.phone = '请输入手机号'
    } else if (!isPhone(form.phone)) {
      errors.phone = '手机号格式不正确'
    }
  }

  if (field === 'smsCode') {
    errors.smsCode = ''
    if (!form.smsCode) {
      errors.smsCode = '请输入验证码'
    } else if (!isSmsCode(form.smsCode)) {
      errors.smsCode = '验证码格式不正确'
    }
  }

  if (field === 'invite_code') {
    errors.invite_code = ''
    if (form.role === 'teacher') {
      if (!form.invite_code) {
        errors.invite_code = '老师账号必须输入邀请码'
      } else if (!isInviteCode(form.invite_code)) {
        errors.invite_code = '邀请码格式不正确'
      }
    }
  }
}

function startCountdown(seconds = 60) {
  countdown.value = seconds
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

async function handleSendCode() {
  if (sendingCode.value || countdown.value > 0) return

  if (!form.phone) {
    errors.phone = '请输入手机号'
    return
  }

  if (!isPhone(form.phone)) {
    errors.phone = '手机号格式不正确'
    return
  }

  try {
    sendingCode.value = true
    const res = await sendSmsCodeApi({ phone: form.phone })
    const bizData = res?.data || {}
    if (bizData?.debug_code) {
      alert(`验证码发送成功（开发模式）：${bizData.debug_code}`)
    } else {
      alert('验证码发送成功，请注意查收短信')
    }
    startCountdown(60)
  } catch (error) {
    alert(error?.response?.data?.detail || error?.response?.data?.message || '验证码发送失败')
  } finally {
    sendingCode.value = false
  }
}

async function handleRegister() {
  if (!validate()) return

  try {
    loading.value = true
    const payload =
      form.role === 'teacher'
        ? {
            teacher_no: form.teacher_no,
            real_name: form.real_name,
            phone: form.phone,
            password: form.password,
            invite_code: form.invite_code,
            sms_code: form.smsCode
          }
        : {
            student_no: form.student_no,
            real_name: form.real_name,
            phone: form.phone,
            password: form.password,
            sms_code: form.smsCode
          }

    const res =
      form.role === 'teacher'
        ? await registerTeacherApi(payload)
        : await registerStudentApi(payload)

    const bizData = res?.data || {}
    const token = bizData.token
    const userInfo = bizData.user_info

    if (!token) {
      throw new Error('注册返回缺少 token')
    }
    if (!userInfo || !userInfo.role) {
      throw new Error('注册返回缺少用户信息')
    }

    localStorage.setItem('token', token)
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    localStorage.setItem('role', userInfo.role)

    router.push(userInfo.role === 'teacher' ? '/teacher/home' : '/student/home')
  } catch (error) {
    alert(error?.response?.data?.detail || error?.response?.data?.message || '注册失败')
  } finally {
    loading.value = false
  }
}

watch(
  () => form.role,
  role => {
    errors.no = ''
    errors.invite_code = ''

    if (role === 'student') {
      form.teacher_no = ''
      form.invite_code = ''
    } else {
      form.student_no = ''
    }
  }
)

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.auth-title {
  font-size: 72px;
  font-weight: 500;
  text-align: center;
  margin-bottom: 40px;
  letter-spacing: 4px;
}

.auth-form {
  width: 100%;
}

.role-selection-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 25px;
  margin: 0 60px 25px 50px;
  background: #fcfcfc;
  border: 1px solid #b3b3b3;
  border-radius: 4px;
}

.role-label-group {
  display: flex;
  flex-direction: column;
}

.role-main-label {
  font-size: 18px;
  color: #333;
  font-weight: 500;
}

.role-sub-label {
  font-size: 16px;
  color: #6ea115;
  margin: 0 auto;
  font-weight: 500;
}

.role-switch-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-text {
  font-size: 14px;
  color: #999;
  transition: all 0.3s;
}

.role-text.active {
  color: #333;
  font-weight: bold;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease-in-out;
  max-height: 85px;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
  margin-bottom: 0;
}

.expand-enter-from {
  transform: scaleY(0.95);
}

.dynamic-input-wrapper {
  padding-bottom: 20px;
}

.agreement-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: -10px 60px 30px 50px;
}

.agreement-text {
  font-size: 14px;
  color: #666;
}

.auth-link-inline {
  color: #5daaf7;
  text-decoration: none;
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
  color: #fff;
  display: block;
}

.btn-green {
  background-color: #8aba35 !important;
}

.btn-green:hover {
  opacity: 0.9;
}

:deep(.el-checkbox) {
  transform: scale(1.4);
  transform-origin: left center;
  margin-right: 15px;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #8aba35;
  border-color: #8aba35;
}

:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #666;
}

@media (max-width: 1024px) {
  .auth-title {
    font-size: 24px;
    margin-bottom: 25px;
  }

  .role-selection-bar {
    padding: 0 10px;
  }

  .role-main-label {
    font-size: 14px;
    font-weight: 500;
  }

  .role-sub-label {
    font-size: 12px;
    font-weight: 500;
  }
}

@media (max-width: 480px) {
  .auth-title {
    font-size: 30px;
    margin-bottom: 20px;
  }

  .role-selection-bar {
    padding: 0 8px;
  }
}
</style>
