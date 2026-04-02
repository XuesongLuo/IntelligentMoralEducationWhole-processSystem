import request from '@/utils/request'

// 学生首页数据
export function getStudentHomeData() {
  return request({
    url: '/student/home',
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