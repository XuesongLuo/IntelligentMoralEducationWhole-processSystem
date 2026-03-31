import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export function loginApi(data) {
  return request.post('/auth/login', data)
}

export function registerApi(data) {
  return request.post('/auth/register', data)
}

export function sendSmsCodeApi(data) {
  return request.post('/auth/send-code', data)
}

export function forgotPasswordApi(data) {
  return request.post('/auth/forgot-password', data)
}