import request from '@/utils/request'
import {
  mockGetExamNotice,
  mockGetExamInfo,
  mockGetExamPaper,
  mockSubmitExamPaper,
  mockGetExamResultList,
  mockGetExamResultDetail
} from '@/mock'

const USE_MOCK = false

function getRolePrefix() {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  return userInfo.role === 'teacher' ? '/teacher' : '/student'
}

// 考试须知
export function getExamNotice(type) {
  if (USE_MOCK) {
    return mockGetExamNotice(type)
  }

  return request({
    url: `${getRolePrefix()}/exam/${type}/notice`,
    method: 'get'
  })
}

// 获取可参与考试/问卷信息
export function getExamInfo(type) {
  if (USE_MOCK) {
    return mockGetExamInfo(type)
  }

  return request({
    url: `${getRolePrefix()}/exam/${type}/info`,
    method: 'get'
  })
}

// 获取题目
export function getExamPaper(type, examId) {
  if (USE_MOCK) {
    return mockGetExamPaper(type, examId)
  }

  return request({
    url: `${getRolePrefix()}/exam/${type}/paper/${examId}`,
    method: 'get'
  })
}

// 提交试卷
export function submitExamPaper(data) {
  if (USE_MOCK) {
    return mockSubmitExamPaper(data)
  }

  return request({
    url: `${getRolePrefix()}/exam/submit`,
    method: 'post',
    data
  })
}

export function submitExamHeartbeat(data) {
  if (USE_MOCK) {
    return Promise.resolve({
      data: {
        activeSeconds: 0,
        submitted: false
      }
    })
  }

  return request({
    url: `${getRolePrefix()}/exam/heartbeat`,
    method: 'post',
    data
  })
}

// 结果列表
export function getExamResultList(params) {
  if (USE_MOCK) {
    return mockGetExamResultList(params)
  }

  return request({
    url: `${getRolePrefix()}/exam/results`,
    method: 'get',
    params
  })
}

// 单次结果详情
export function getExamResultDetail(resultId, userId) {
  if (USE_MOCK) {
    return mockGetExamResultDetail(resultId, userId)
  }

  return request({
    url: `${getRolePrefix()}/exam/results/${resultId}`,
    method: 'get',
    params: userId ? { userId } : {}
  })
}
