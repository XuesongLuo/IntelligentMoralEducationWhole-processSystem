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

function mockError(message = '请求失败', code = 400) {
  return Promise.reject({
    response: {
      data: {
        code,
        message
      }
    }
  })
}

export function mockLogin(data) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const user = mockDb.users.find(
        item =>
          item.account === data.account &&
          item.password === data.password
      )

      if (!user) {
        reject({
          response: {
            data: {
              code: 401,
              message: '账号或密码错误'
            }
          }
        })
        return
      }

      resolve(
        mockResponse({
          token: user.token,
          userInfo: user.profile
        }, '登录成功')
      )
    }, 300)
  })
}

export function mockRegister(data) {
  return Promise.resolve(
    mockResponse(
      {
        account: data.account
      },
      '注册成功'
    )
  )
}

export function mockSendSmsCode() {
  return Promise.resolve(mockResponse(null, '验证码发送成功'))
}

export function mockForgotPassword() {
  return Promise.resolve(mockResponse(null, '密码重置成功'))
}