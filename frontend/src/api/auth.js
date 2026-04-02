import request from '@/utils/request'

export function loginApi(data) {
  /*
  return request({
    url: '/auth/login', 
    method: 'post',
    data
  })
  */
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const user = mockUsers.find(
        item =>
          item.account === data.account &&
          item.password === data.password
      )

      if (user) {
        resolve({
          data: {
            code: 200,
            message: '登录成功',
            data: {
              token: user.token,
              role: user.role,
              userInfo: user.userInfo
            }
          }
        })
      } else {
        reject({
          response: {
            data: {
              code: 401,
              message: '账号或密码错误'
            }
          }
        })
      }
    }, 500)
  })
}

export function registerApi(data) {
  return request({
    url: '/auth/register', 
    method: 'post',
    data
  })
}

export function sendSmsCodeApi(data) {
  return request({
    url: '/auth/send-code', 
    method: 'post',
    data
  })
}

export function forgotPasswordApi(data) {
  return request.post({
    url: '/auth/forgot-password', 
    method: 'post',
    data
  })
}





// 模拟数据
const mockUsers = [
  {
    account: '20260001',
    password: '123456',
    role: 'student',
    token: 'mock-token-student-001',
    userInfo: {
      id: 1,
      name: '张三',
      account: '20260001',
      phone: '13800000000'
    }
  },
  {
    account: 'teacher001',
    password: '123456',
    role: 'teacher',
    token: 'mock-token-teacher-001',
    userInfo: {
      id: 2,
      name: '李老师',
      account: '2020007',
      phone: '13900000000'
    }
  }
]