import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

import Login from '@/views/auth/LoginView.vue'
import Register from '@/views/auth/RegisterView.vue'
import ForgotPassword from '@/views/auth/ForgotPasswordView.vue'

import AppLayout from '@/layouts/AppLayout.vue'

import ExamNotice from '@/views/common/ExamNotice.vue'
import ExamPaper from '@/views/common/ExamPaper.vue'

import StudentHome from '@/views/student/StudentHome.vue'
import StudentMoralExamHub from '@/views/student/StudentMoralExamHub.vue'
import StudentResult from '@/views/student/StudentResultList.vue'
import StudentResourceStudyHub from '@/views/student/StudentResourceStudyHub.vue'
import StudentResourceStudyList from '@/views/student/StudentResourceStudyList.vue'

import TeacherHome from '@/views/teacher/TeacherHome.vue'
import TeacherMoralExamHub from '@/views/teacher/TeacherMoralExamHub.vue'
import TeacherResult from '@/views/teacher/TeacherResultList.vue'
import TeacherResourceStudyHub from '@/views/teacher/TeacherResourceStudyHub.vue'
import TeacherResourceStudyList from '@/views/teacher/TeacherResourceStudyList.vue'

import { useTeacherViewStore } from '@/stores/teacherView'
import {
  buildExamPaperPath,
  getActiveExamSession,
  isExamEntryRoute,
  isExamPaperRoute,
  shouldShowActiveExamNotice
} from '@/utils/examSession'

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
        component: StudentMoralExamHub
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
        component: StudentResult
      },
      {
        path: 'resource-study',
        name: 'StudentResourceStudyHub',
        component: StudentResourceStudyHub
      },
      {
        path: 'resource-study/:categoryId',
        name: 'StudentResourceStudyList',
        component: StudentResourceStudyList,
        props: true
      }
    ]
  },
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
      },
      {
        path: 'resource-study',
        name: 'TeacherResourceStudyHub',
        component: TeacherResourceStudyHub
      },
      {
        path: 'resource-study/:categoryId',
        name: 'TeacherResourceStudyList',
        component: TeacherResourceStudyList,
        props: true
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
  const activeExamSession = getActiveExamSession()

  if (to.meta.public) {
    return next()
  }

  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

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

  if (
    token &&
    activeExamSession &&
    activeExamSession.userId === userInfo.id &&
    activeExamSession.role === userInfo.role
  ) {
    const activeExamPath = buildExamPaperPath(activeExamSession)
    if (to.path !== activeExamPath && isExamEntryRoute(to, userInfo.role)) {
      ElMessage.warning('你有未完成的考试，已为你恢复到当前考试页面')
      return next(activeExamPath)
    }
  }

  if (to.meta.teacherSelfOnly) {
    const teacherViewStore = useTeacherViewStore()
    let isViewingSelf = teacherViewStore.isViewingSelf

    if (
      typeof isViewingSelf !== 'boolean' ||
      !teacherViewStore.teacherUser ||
      !teacherViewStore.selectedUser
    ) {
      const teacherViewState = JSON.parse(localStorage.getItem('teacherViewState') || '{}')
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

router.afterEach(to => {
  const token = localStorage.getItem('token')
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  const activeExamSession = getActiveExamSession()

  if (!activeExamSession) {
    return
  }

  const activeExamPath = buildExamPaperPath(activeExamSession)
  if (to.path === activeExamPath || isExamPaperRoute(to)) {
    return
  }

  if (token && activeExamSession.userId === userInfo.id && activeExamSession.role === userInfo.role) {
    if (shouldShowActiveExamNotice(to.fullPath, activeExamPath)) {
      ElMessage.warning('还有考试未完成，可从考试入口继续当前考试')
    }
    return
  }

  if (!token && shouldShowActiveExamNotice(to.fullPath, activeExamPath)) {
    ElMessage.info('你有未完成的考试，登录后可继续作答')
  }
})

export default router
