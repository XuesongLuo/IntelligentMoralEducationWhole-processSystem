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
            />

            <AuthInput
                v-model="form.password"
                icon="🔒"
                type="password"
                placeholder="设置6-18位登录密码"
                :status="status.password"
                :error-message="errors.password"
            />

            <AuthInput
                v-model="form.confirmPassword"
                icon="🔒"
                type="password"
                placeholder="再次输入密码"
                :status="status.confirmPassword"
                :error-message="errors.confirmPassword"
            />

            <AuthInput
                v-model="form.real_name"
                icon="🪪"
                placeholder="姓名验证，务必输入真实姓名"
                :status="status.real_name"
                :error-message="errors.real_name"
            />

            <AuthInput
                v-model="form.phone"
                icon="📱"
                placeholder="输入手机号"
                :status="status.phone"
                :error-message="errors.phone"
            />

            <AuthInput
                v-model="form.smsCode"
                icon="✉"
                placeholder="输入手机验证码"
                :action-text="smsActionText"
                :status="status.smsCode"
                :error-message="errors.smsCode"
                @action="handleSendCode"
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
                            icon="🎟️"
                            placeholder="请输入教师专属邀请码 (必填)"
                            :status="status.invite_code"
                            :error-message="errors.invite_code"
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
/* 逻辑部分保持不变，确保功能完整性 */
import { computed, reactive, ref, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '@/components/auth/AuthLayout.vue'
import AuthInput from '@/components/auth/AuthInput.vue'
import AuthSwitch from '@/components/auth/AuthSwitch.vue'
import { registerStudentApi, registerTeacherApi, sendSmsCodeApi } from '@/api/auth'
import { isInviteCode, isPassword, isPhone, isRealName, isSmsCode, isStudentOrWorkNo } from '@/utils/validators'

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
        confirmPassword: form.confirmPassword
            ? (errors.confirmPassword ? 'error' : 'success')
            : '',
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
    Object.keys(errors).forEach(key => errors[key] = '')
    const currentNo = form.role === 'student' ? form.student_no : form.teacher_no

    if (!currentNo) {
        errors.no = form.role === 'student' ? '请输入学号' : '请输入工号'
    } else if (!isStudentOrWorkNo(currentNo)) {
        errors.no = form.role === 'student' ? '学号格式不正确' : '工号格式不正确'
    }
    if (!form.password) errors.password = '请输入密码'
    else if (!isPassword(form.password)) errors.password = '密码长度需为6-18位'

    if (form.confirmPassword !== form.password) errors.confirmPassword = '两次输入密码不一致'

    if (!form.real_name) errors.real_name = '请输入真实姓名'

    if (!form.phone) {
        errors.phone = '请输入手机号'
    } else if (!isPhone(form.phone)) {
        errors.phone = '手机号格式不正确'
    }

    if (!form.smsCode) errors.smsCode = '请输入验证码'

    if (form.role === 'teacher') {
        if (!form.invite_code) {
            errors.invite_code = '老师账号必须输入邀请码'
        } else if (!isInviteCode(form.invite_code)) {
            errors.invite_code = '邀请码格式不正确'
        }
    }
    if (!form.agree) { alert('请先勾选服务条款'); return false }
    return Object.values(errors).every(item => !item)
}

// 短信验证码按钮点击计时
function startCountdown(seconds = 60) {
  countdown.value = seconds
  timer && clearInterval(timer)
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
            form.role === 'teacher' ? {
                    teacher_no: form.teacher_no,
                    real_name: form.real_name,
                    phone: form.phone,
                    password: form.password,
                    invite_code: form.invite_code,
                    sms_code: form.smsCode
                } : {
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
  (role) => {
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
  timer && clearInterval(timer)
})

</script>

<style scoped>
.auth-title {
    font-size: 72px; /* 匹配设计稿大字号 */
    font-weight: 500;
    text-align: center;
    margin-bottom: 40px;
    letter-spacing: 4px;
}

.auth-form { width: 100%; }


/* 身份选择条整体样式 */
.role-selection-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 64px;
    padding: 0  25px;
    margin: 0 60px 25px 50px; /* 50px 是为了和上方图标位对齐 */
    background: #fcfcfc;
    border: 1px solid #eeeeee;
    border-radius: 4px;
    border-color: #b3b3b3;
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
    color: #6ea115; /* 绿色点缀 */
    margin-top: 2px;
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

/* 动态展开动画逻辑 */
.expand-enter-active,
.expand-leave-active {
    transition: all 0.3s ease-in-out;
    max-height: 85px; /* 预估输入框高度 */
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
    transform: scaleY(0.95); /* 用缩放代替位移，视觉上更自然 */
}

.dynamic-input-wrapper {
    padding-bottom: 20px;
}


/* 协议行样式 */
.agreement-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -10px 60px 30px 50px; /* 左右间距对齐输入框主体 */
}

.agreement-text { font-size: 14px; color: #666; }
.auth-link-inline { color: #5daaf7; text-decoration: none; }
.auth-link { color: #5daaf7; text-decoration: none; font-size: 18px; }

/* 统一按钮样式 */
.action-btn {
    width: calc(100% - 110px) !important; /* 减去左边50px图标位和右边60px状态位 */
    margin-left: 50px !important; /* 实现与输入框文字对齐 */
    height: 64px;
    font-size: 26px;
    font-weight: 600;
    border: none;
    border-radius: 0;
    color: #fff;
    display: block;
}

.btn-green { background-color: #8aba35 !important; }
.btn-green:hover { opacity: 0.9; }

/* 深度覆盖 Element Plus  大小 */
:deep(.el-checkbox) {
    transform: scale(1.4); /* 整体放大 1.4 倍 */
    transform-origin: left center; /* 确保放大后左侧对齐，不会挤压左边距 */
    margin-right: 15px; /* 放大后会占用更多空间，适当增加右边距 */
}

/* 深度覆盖 Element Plus 复选框颜色 */
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