<template>
    <AuthLayout>
        <div class="auth-title">密码找回</div>

        <form class="auth-form" @submit.prevent="handleSubmit">
            <AuthInput
                v-model="form.username"
                icon="◉"
                placeholder="用户名"
                :status="status.username"
                :error-message="errors.username"
            />

            <AuthInput
                v-model="form.realName"
                icon="🪪"
                placeholder="真实姓名"
                :status="status.realName"
                :error-message="errors.realName"
            />

            <AuthInput
                v-model="form.newPassword"
                icon="🔒"
                type="password"
                placeholder="请输入新密码"
                :status="status.newPassword"
                :error-message="errors.newPassword"
            />

            <AuthInput
                v-model="form.confirmPassword"
                icon="🔒"
                type="password"
                placeholder="再次输入密码"
                :status="status.confirmPassword"
                :error-message="errors.confirmPassword"
            />

            <div class="btn-row">
                <button class="auth-btn auth-btn--blue" type="submit" :disabled="loading">
                    {{ loading ? '提交中...' : '提交' }}
                </button>

                <button class="auth-btn auth-btn--gray" type="button" @click="router.push('/login')">
                    返回
                </button>
            </div>
        </form>
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
    errors.username = ''
    errors.realName = ''
    errors.newPassword = ''
    errors.confirmPassword = ''

    if (!form.username) {
        errors.username = '请输入学号/工号'
    } else if (!isStudentOrWorkNo(form.username)) {
        errors.username = '学号/工号格式不正确'
    }

    if (!form.realName) {
        errors.realName = '请输入真实姓名'
    } else if (!isRealName(form.realName)) {
        errors.realName = '姓名格式不正确'
    }

    if (!form.newPassword) {
        errors.newPassword = '请输入新密码'
    } else if (!isPassword(form.newPassword)) {
        errors.newPassword = '密码长度需为6-18位'
    }

    if (!form.confirmPassword) {
        errors.confirmPassword = '请再次输入密码'
    } else if (form.confirmPassword !== form.newPassword) {
        errors.confirmPassword = '两次密码输入不一致'
    }

    return !Object.values(errors).some(Boolean)
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
        alert(error?.response?.data?.message || '找回失败，请确认学号和姓名是否匹配')
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

.btn-row {
  display: flex;
  gap: 28px;
  margin-top: 8px;
}

.auth-btn {
  flex: 1;
  height: 58px;
  border: none;
  color: #fff;
  font-size: 24px;
  font-weight: 600;
  cursor: pointer;
}

.auth-btn--blue {
  background: #1f47f0;
}

.auth-btn--gray {
  background: #b9b9b9;
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