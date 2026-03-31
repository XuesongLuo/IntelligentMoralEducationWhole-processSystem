import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterView.vue')
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/auth/ForgotPasswordView.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: {
      template: '<div style="padding: 40px; font-size: 24px;">登录成功，进入主界面</div>'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router