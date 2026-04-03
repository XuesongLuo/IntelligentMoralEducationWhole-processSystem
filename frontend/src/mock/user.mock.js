import { mockDb } from './database'

function mockResponse(data, message = '成功', code = 200) {
  return {
    data: {
      code,
      message,
      data
    }
  }
}

function getCurrentUser() {
  return JSON.parse(localStorage.getItem('userInfo') || '{}')
}

export function mockGetUserHomeData(params = {}) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const localUser = getCurrentUser()
      const targetUserId = params.userId || localUser.id
      const data = mockDb.UserHomeMap[targetUserId] || null

      resolve(mockResponse(data || {}, '获取用户首页成功'))
    }, 300)
  })
}

export function mockGetTeacherStudentList() {
  return new Promise((resolve) => {
    setTimeout(() => {
      const list = mockDb.users.map(user => ({
        id: user.id,
        role: user.profile.role,
        account: user.profile.account,
        name: user.profile.name,
        label: `${user.profile.account} ${user.profile.name}`
      }))

      resolve(mockResponse(list, '获取用户列表成功'))
    }, 300)
  })
}

export function mockGetUserResults(params = {}) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const localUser = getCurrentUser()
      const targetUserId = params.userId || localUser.id
      const list = mockDb.examResults[targetUserId] || []
      resolve(mockResponse(list, '获取结果列表成功'))
    }, 300)
  })
}