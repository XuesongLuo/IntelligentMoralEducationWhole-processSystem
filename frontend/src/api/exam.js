import request from '@/utils/request'

// 考试须知
export function getExamNotice(type) {
  return request({
    url: `/student/exam/${type}/notice`,
    method: 'get'
  })
}

// 获取可参与考试/问卷信息
export function getExamInfo(type) {
  return request({
    url: `/student/exam/${type}/info`,
    method: 'get'
  })
}

// 获取题目
export function getExamPaper(type, examId) {
  return request({
    url: `/student/exam/${type}/paper/${examId}`,
    method: 'get'
  })
}

// 提交试卷
export function submitExamPaper(data) {
  return request({
    url: '/student/exam/submit',
    method: 'post',
    data
  })
}

// 结果列表
export function getExamResultList(params) {
  return request({
    url: '/student/exam/results',
    method: 'get',
    params
  })
}

// 单次结果详情
export function getExamResultDetail(resultId) {
  return request({
    url: `/student/exam/results/${resultId}`,
    method: 'get'
  })
}