import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

import StudentHome from '@/views/student/StudentHome.vue'
import MoralExamHub from '@/views/student/MoralExamHub.vue'
import ExamNotice from '@/views/student/ExamNotice.vue'
import ExamPaper from '@/views/student/ExamPaper.vue'
import ResultList from '@/views/student/ResultList.vue'

import TeacherHome from '@/views/teacher/TeacherHome.vue'

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
    path: '/ResetPassword',
    name: 'ResetPassword',
    component: () => import('@/views/auth/ForgotPasswordView.vue')
  },
  // 学生端
  {
    path: '/student',
    component: AppLayout,
    children: [
      {
        path: '',
        redirect: '/student/home'
      },
      {
        path: 'home',
        component: StudentHome
      },
      {
        path: 'moral-exam',
        component: MoralExamHub
      },
      {
        path: 'exam-notice/:type',
        component: ExamNotice
      },
      {
        path: 'exam-paper/:type/:examId',
        component: ExamPaper
      },
      {
        path: 'results',
        component: ResultList
      }
    ]
  },
   // 教师端
  {
    path: '/teacher',
    component: AppLayout,
    children: [
      {
        path: '',
        redirect: '/teacher/home'
      },
      {
        path: 'home',
        name: 'TeacherHome',
        component: TeacherHome
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router