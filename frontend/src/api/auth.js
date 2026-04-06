import request from '@/utils/request'

import {
  mockLogin,
  mockRegister,
  mockSendSmsCode,
  mockForgotPassword
} from '@/mock'

const USE_MOCK = false

export function loginApi(data) {
  if (USE_MOCK) {
    return mockLogin(data)
  }
  
  return request({
    url: '/auth/login', 
    method: 'post',
    data
  })
}

export function registerApi(data) {
  if (USE_MOCK) {
    return mockRegister(data)
  }

  return request({
    url: '/auth/register', 
    method: 'post',
    data
  })
}

export function sendSmsCodeApi(data) {
  if (USE_MOCK) {
    return mockSendSmsCode(data)
  }

  return request({
    url: '/auth/send-code', 
    method: 'post',
    data
  })
}

export function forgotPasswordApi(data) {
  if (USE_MOCK) {
    return mockForgotPassword(data)
  }

  return request({
    url: '/auth/forgot-password', 
    method: 'post',
    data
  })
}
