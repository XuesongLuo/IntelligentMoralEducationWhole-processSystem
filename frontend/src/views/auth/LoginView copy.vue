<template>
    <AuthLayout>
        <div class="auth-title">欢迎回来</div>

        <form class="auth-form" @submit.prevent="handleLogin">
            <AuthInput
                v-model="form.account"
                icon="◉"
                placeholder="用户名"
                :status="inputStatus.account"
                :error-message="errors.account"
            />

            <AuthInput
                v-model="form.password"
                icon="🔒"
                type="password"
                placeholder="密码"
                :status="inputStatus.password"
                :error-message="errors.password"
            />

            <div class="auth-link-row">
                <router-link to="/forgot-password" class="auth-link">忘记密码?</router-link>
            </div>

            <button class="auth-btn auth-btn--green" type="submit" :disabled="loading">
                {{ loading ? '登录中...' : '登录' }}
            </button>

            <button class="auth-btn auth-btn--blue" type="button" @click="router.push('/register')">
                注册
            </button>
        </form>

        <div class="auth-footer-tip">如有登录问题，请联系管理员@DYQ</div>
    </AuthLayout>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '@/components/auth/AuthLayout.vue'
import AuthInput from '@/components/auth/AuthInput.vue'
import { loginApi } from '@/api/auth'
import { isAccount, isPassword } from '@/utils/validators'

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
        errors.password = '密码长度需为6-18位'
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

        const payload = {
        account: form.account,
        password: form.password
        }

        await loginApi(payload)
        router.push('/home')
    } catch (error) {
        console.error(error)
        alert(error?.response?.data?.message || '登录失败，请检查账号或密码')
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
    margin: 10px 0 42px;
}

.auth-form {
    margin-top: 10px;
}

.auth-link-row {
    text-align: right;
    margin-top: -12px;
    margin-bottom: 38px;
}

.auth-link {
    color: #67aff7;
    text-decoration: none;
    font-size: 16px;
}

.auth-btn {
    width: 100%;
    height: 58px;
    border: none;
    color: #fff;
    font-size: 24px;
    font-weight: 600;
    cursor: pointer;
    margin-bottom: 28px;
}

.auth-btn--green {
    background: #8aba35;
}

.auth-btn--blue {
    background: #1f47f0;
}

.auth-footer-tip {
    color: #999;
    text-align: center;
    margin-top: 110px;
    font-size: 16px;
}
</style>