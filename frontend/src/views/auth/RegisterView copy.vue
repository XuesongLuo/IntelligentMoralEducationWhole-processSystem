<template>
    <AuthLayout>
        <div class="auth-title">账号注册</div>

        <form class="auth-form" @submit.prevent="handleRegister">
            <AuthInput
                v-model="form.username"
                icon="◉"
                placeholder="设置用户名"
                :status="status.username"
                :error-message="errors.username"
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
                v-model="form.realName"
                icon="🪪"
                placeholder="姓名验证，务必输入真实姓名"
                :status="status.realName"
                :error-message="errors.realName"
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
                action-text="获取验证码"
                :status="status.smsCode"
                :error-message="errors.smsCode"
                @action="handleSendCode"
            />

            <div class="register-row">
                <div class="register-row__left">
                    <AuthInput
                        v-model="form.inviteCode"
                        icon="✉"
                        :placeholder="form.role === 'teacher' ? '请输入教师邀请码' : '请输入邀请码(选填可改为必填)'"
                        :status="status.inviteCode"
                        :error-message="errors.inviteCode"
                    />
                </div>

                <div class="register-row__right">
                    <AuthSwitch v-model="form.role" />
                    <span class="register-role-text">账号类型：{{ form.role === 'teacher' ? '老师' : '学生' }}</span>
                </div>
            </div>

            <div class="agreement-row">
                <label class="agreement-label">
                    <input v-model="form.agree" type="checkbox" />
                    <span>勾选并同意</span>
                    <a href="javascript:;">服务条款</a>
                </label>

                <router-link to="/login" class="auth-link">已有账号?</router-link>
            </div>

            <button class="auth-btn auth-btn--green" type="submit" :disabled="loading">
                {{ loading ? '提交中...' : '注册并登录' }}
            </button>
        </form>
    </AuthLayout>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '@/components/auth/AuthLayout.vue'
import AuthInput from '@/components/auth/AuthInput.vue'
import AuthSwitch from '@/components/auth/AuthSwitch.vue'
import { registerApi, sendSmsCodeApi } from '@/api/auth'
import {
    isInviteCode,
    isPassword,
    isPhone,
    isRealName,
    isSmsCode,
    isStudentOrWorkNo
} from '@/utils/validators'

const router = useRouter()
const loading = ref(false)

const form = reactive({
    username: '',
    password: '',
    confirmPassword: '',
    realName: '',
    phone: '',
    smsCode: '',
    inviteCode: '',
    role: 'student',
    agree: false
})

const errors = reactive({
    username: '',
    password: '',
    confirmPassword: '',
    realName: '',
    phone: '',
    smsCode: '',
    inviteCode: '',
    agree: ''
})

function validate() {
    Object.keys(errors).forEach((key) => {
        errors[key] = ''
    })

    if (!form.username) {
        errors.username = '请输入学号/工号'
    } else if (!isStudentOrWorkNo(form.username)) {
        errors.username = '学号/工号格式不正确'
    }

    if (!form.password) {
        errors.password = '请输入密码'
    } else if (!isPassword(form.password)) {
        errors.password = '密码长度需为6-18位'
    }

    if (!form.confirmPassword) {
        errors.confirmPassword = '请再次输入密码'
    } else if (form.confirmPassword !== form.password) {
        errors.confirmPassword = '两次输入密码不一致'
    }

    if (!form.realName) {
        errors.realName = '请输入真实姓名'
    } else if (!isRealName(form.realName)) {
        errors.realName = '真实姓名格式不正确'
    }

    if (!form.phone) {
        errors.phone = '请输入手机号'
    } else if (!isPhone(form.phone)) {
        errors.phone = '手机号格式不正确'
    }

    if (!form.smsCode) {
        errors.smsCode = '请输入验证码'
    } else if (!isSmsCode(form.smsCode)) {
        errors.smsCode = '验证码格式不正确'
    }

    if (form.role === 'teacher') {
        if (!form.inviteCode) {
        errors.inviteCode = '老师账号必须输入邀请码'
        } else if (!isInviteCode(form.inviteCode)) {
        errors.inviteCode = '邀请码格式不正确'
        }
    }

    if (!form.agree) {
        errors.agree = '请先勾选服务条款'
    }

    return Object.values(errors).every((item) => !item)
}

const status = computed(() => ({
    username: form.username ? (errors.username ? 'error' : 'success') : '',
    password: form.password ? (errors.password ? 'error' : 'success') : '',
    confirmPassword: form.confirmPassword ? (errors.confirmPassword ? 'error' : 'success') : '',
    realName: form.realName ? (errors.realName ? 'error' : 'success') : '',
    phone: form.phone ? (errors.phone ? 'error' : 'success') : '',
    smsCode: form.smsCode ? (errors.smsCode ? 'error' : 'success') : '',
    inviteCode:
        form.role === 'teacher' || form.inviteCode
        ? (errors.inviteCode ? 'error' : 'success')
        : ''
}))

async function handleSendCode() {
    if (!form.phone) {
        errors.phone = '请先输入手机号'
        return
    }

    if (!isPhone(form.phone)) {
        errors.phone = '手机号格式不正确'
        return
    }

    try {
        await sendSmsCodeApi({ phone: form.phone, scene: 'register' })
        alert('验证码已发送，5分钟内有效')
    } catch (error) {
        console.error(error)
        alert(error?.response?.data?.message || '验证码发送失败')
    }
}

async function handleRegister() {
    if (!validate()) {
        if (errors.agree) alert(errors.agree)
        return
    }

    try {
        loading.value = true

        const payload = {
        username: form.username,
        password: form.password,
        realName: form.realName,
        phone: form.phone,
        smsCode: form.smsCode,
        role: form.role,
        inviteCode: form.role === 'teacher' ? form.inviteCode : ''
        }

        await registerApi(payload)
        router.push('/home')
    } catch (error) {
        console.error(error)
        alert(error?.response?.data?.message || '注册失败，请检查信息')
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
    margin: 10px 0 30px;
}

.register-row {
    display: flex;
    gap: 16px;
    align-items: flex-start;
}

.register-row__left {
    flex: 1;
}

.register-row__right {
    width: 210px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 12px;
    padding-top: 8px;
}

.register-role-text {
    font-size: 16px;
    color: #444;
}

.agreement-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -6px 0 18px;
}

.agreement-label {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #666;
    font-size: 14px;
}

.agreement-label a,
.auth-link {
    color: #5daaf7;
    text-decoration: none;
}

.auth-btn {
    width: 100%;
    height: 58px;
    border: none;
    color: #fff;
    font-size: 24px;
    font-weight: 600;
    cursor: pointer;
}

.auth-btn--green {
    background: #8aba35;
}
</style>