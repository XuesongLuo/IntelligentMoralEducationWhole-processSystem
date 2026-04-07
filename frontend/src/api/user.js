import request from '@/utils/request'

import {
  mockGetUserHomeData,
  mockGetUserResults,
  mockGetTeacherStudentList
} from '@/mock'

const USE_MOCK = false

// 首页数据
export function getUserHomeData(params) {
  if (USE_MOCK) {
    return mockGetUserHomeData(params)
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