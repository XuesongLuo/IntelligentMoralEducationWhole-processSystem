import { createRouter, createWebHistory } from 'vue-router'

import Register from '@/views/auth/LoginView.vue'
import Login from '@/views/auth/LoginView.vue'
import ForgotPassword from '@/views/auth/ForgotPasswordView.vue'

import AppLayout from '@/layouts/AppLayout.vue'

import ExamNotice from '@/views/common/ExamNotice.vue'
import ExamPaper from '@/views/common/ExamPaper.vue'

import StudentHome from '@/views/student/StudentHome.vue'
import MoralExamHub from '@/views/student/MoralExamHub.vue'
import ResultList from '@/views/student/ResultList.vue'

import TeacherHome from '@/views/teacher/TeacherHome.vue'
import TeacherMoralExamHub from '@/views/teacher/TeacherMoralExamHub.vue'
import TeacherResult from '@/views/teacher/TeacherResult.vue'



import { useTeacherViewStore } from '@/stores/teacherView'


const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { public: true }
  },
  {
    path: '/ResetPassword',
    name: 'ResetPassword',
    component: ForgotPassword,
    meta: { public: true }
  },

  // 学生端
  {
    path: '/student',
    component: AppLayout,
    meta: { requiresAuth: true, role: 'student' },
    children: [
      {
        path: 'home',
        name: 'StudentHome',
        component: StudentHome
      },
      {
        path: 'moral-exam',
        name: 'StudentMoralExamHub',
        component: MoralExamHub
      },
      {
        path: 'exam-notice/:type',
        name: 'StudentExamNotice',
        component: ExamNotice,
        props: true
      },
      {
        path: 'exam-paper/:type/:examId',
        name: 'StudentExamPaper',
        component: ExamPaper,
        props: true
      },
      {
        path: 'results',
        name: 'StudentResults',
        component: ResultList
      }
    ]
  },

  // 教师端
  {
    path: '/teacher',
    component: AppLayout,
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      {
        path: 'home',
        name: 'TeacherHome',
        component: TeacherHome
      },
      {
        path: 'moral-exam',
        name: 'TeacherMoralExamHub',
        component: TeacherMoralExamHub,
        meta: { teacherSelfOnly: true }
      },
      {
        path: 'exam-notice/:type',
        name: 'TeacherExamNotice',
        component: ExamNotice,
        props: true,
        meta: { teacherSelfOnly: true }
      },
      {
        path: 'exam-paper/:type/:examId',
        name: 'TeacherExamPaper',
        component: ExamPaper,
        props: true,
        meta: { teacherSelfOnly: true }
      },
      {
        path: 'results',
        name: 'TeacherResults',
        component: TeacherResult
      }
    ]
  },

  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  const token = localStorage.getItem('token')

  // 1. 公共页面直接放行
  if (to.meta.public) {
    return next()
  }

  // 2. 需要登录但没登录，回登录页
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  // 3. 角色校验
  if (to.meta.role) {
    const currentRole = userInfo.role
    if (!currentRole) {
      return next('/login')
    }

    if (to.meta.role !== currentRole) {
      if (currentRole === 'teacher') {
        return next('/teacher/home')
      }
      return next('/student/home')
    }
  }

  // 4. 老师端考试权限校验：只有查看自己时才能进入
  if (to.meta.teacherSelfOnly) {
    const teacherViewStore = useTeacherViewStore()

    // 优先从 store 读
    let isViewingSelf = teacherViewStore.isViewingSelf

    // 如果刷新后 store 丢了，就从 localStorage 兜底
    if (
      typeof isViewingSelf !== 'boolean' ||
      !teacherViewStore.teacherUser ||
      !teacherViewStore.selectedUser
    ) {
      const teacherViewState = JSON.parse(
        localStorage.getItem('teacherViewState') || '{}'
      )

      const teacherUserId = teacherViewState.teacherUser?.id
      const selectedUserId = teacherViewState.selectedUser?.id

      isViewingSelf =
        !!teacherUserId &&
        !!selectedUserId &&
        teacherUserId === selectedUserId
    }

    if (!isViewingSelf) {
      return next('/teacher/home')
    }
  }

  next()
})

export default router