import request from '@/utils/request'

import {
  mockGetUserHomeData,
  mockGetUserResults,
  mockGetTeacherStudentList
} from '@/mock'

const USE_MOCK = false


function getRolePrefix() {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  return userInfo.role === 'teacher' ? '/teacher' : '/student'
}

// 首页数据
export function getUserHomeData(params) {
  if (USE_MOCK) {
    return mockGetUserHomeData(params)
  }
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  if (userInfo.role === 'teacher') {
    return request({
      url: '/teacher/home',
      method: 'get',
      params
    })
  }
  return request({
    url: '/student/home',
    method: 'get'
  })
}

export function getUserResults(params) {
  if (USE_MOCK) {
    return mockGetUserResults(params)
  }

  return request({
    url: '/student/results',
    method: 'get',
    params
  })
}

export function getTeacherStudentList() {
  if (USE_MOCK) {
    return mockGetTeacherStudentList()
  }

  return request({
    url: '/teacher/student-list',
    method: 'get'
  })
}

export function getStudentRosterList() {
  return request({
    url: '/teacher/roster/students',
    method: 'get'
  })
}

export function createStudentRoster(data) {
  return request({
    url: '/teacher/roster/students',
    method: 'post',
    data
  })
}

export function downloadStudentRosterTemplate() {
  return request({
    url: '/teacher/roster/students/template',
    method: 'get',
    responseType: 'blob'
  })
}

export function importStudentRoster(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/teacher/roster/students/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function updateStudentRoster(id, data) {
  return request({
    url: `/teacher/roster/students/${id}`,
    method: 'put',
    data
  })
}

export function deleteStudentRoster(id) {
  return request({
    url: `/teacher/roster/students/${id}`,
    method: 'delete'
  })
}

export function getTeacherRosterList() {
  return request({
    url: '/teacher/roster/teachers',
    method: 'get'
  })
}

export function createTeacherRoster(data) {
  return request({
    url: '/teacher/roster/teachers',
    method: 'post',
    data
  })
}

export function downloadTeacherRosterTemplate() {
  return request({
    url: '/teacher/roster/teachers/template',
    method: 'get',
    responseType: 'blob'
  })
}

export function importTeacherRoster(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/teacher/roster/teachers/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function updateTeacherRoster(id, data) {
  return request({
    url: `/teacher/roster/teachers/${id}`,
    method: 'put',
    data
  })
}

export function deleteTeacherRoster(id) {
  return request({
    url: `/teacher/roster/teachers/${id}`,
    method: 'delete'
  })
}



// 德育资源学习进度
export function getStudyProgress() {

  
  return request({
    url: '/student/study/progress',
    method: 'get'
  })
}

// 成绩记录（首页雷达图使用：只取最高/最低）
export function getScoreSummary() {


  return request({
    url: '/student/score/summary',
    method: 'get'
  })
}
