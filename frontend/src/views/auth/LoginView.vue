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

            <el-button 
                class="action-btn btn-green" 
                native-type="submit" 
                :loading="loading"
            >
                登录
            </el-button>

            <el-button 
                class="action-btn btn-blue" 
                @click="router.push('/register')"
            >
                注册
            </el-button>
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

// 逻辑保留自原始代码 [cite: 14, 15]
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
        //await loginApi({ account: form.account, password: form.password })
        // 假设后端返回 role: 'student' | 'teacher'
        //const role = res?.data?.role
        const res = await loginApi({
            account: form.account,
            password: form.password
        })

        const result = res.data
        const role = result?.data?.role
        const token = result?.data?.token
        const userInfo = result?.data?.userInfo

        localStorage.setItem('token', token)
        localStorage.setItem('userInfo', JSON.stringify(userInfo))
        localStorage.setItem('role', role)
    
        if (role === 'teacher') {
            alert('老师端页面暂未开发，当前仅支持学生端登录')
            //router.push('/teacher/home') // 临时占位
        } else {
            router.push('/student/home')
        }
    } catch (error) {
            alert(error?.response?.data?.message || '登录失败，请检查账号或密码')
    } finally {
            loading.value = false
    }
}
</script>

<style scoped>
.auth-title {
    font-size: 64px; /* 匹配设计稿字号  */
    font-weight: 500;
    text-align: center;
    margin-bottom: 50px;
    letter-spacing: 4px;
}

.auth-form {
    /* 确保表单容器有明确的宽度管理 */
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
    /* 关键修改：按钮不占 100%，而是要减去图标和状态位的宽度 */
    /* 或者通过 margin 抵消左侧图标宽度 */
    width: calc(100% - 110px) !important; /* 100% 减去左 50px 和 右 60px */
    margin-left: 50px !important; /* 跳过左侧图标的宽度，实现与输入框左对齐 */

    height: 64px;
    font-size: 26px;
    font-weight: 600;
    border: none;
    border-radius: 0;
    margin-bottom: 25px;
    color: #fff;
    display: block; /* 确保占据整行 */
}

.btn-green { background-color: #8aba35 !important; }
.btn-green:hover { opacity: 0.9; }

.btn-blue { background-color: #1f47f0 !important; }
.btn-blue:hover { opacity: 0.9; }

.auth-footer-tip {
    margin-top: 80px;
    /* 底部文字通常也需要避开左侧图标位来居中，或者直接全宽居中 */
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