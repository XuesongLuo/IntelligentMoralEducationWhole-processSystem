import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 这里可以统一带上 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response) {
      const status = error.response.status
      const requestUrl = error.config?.url || ''
      const hasToken = !!localStorage.getItem('token')

      if (status === 401 && hasToken && !requestUrl.includes('/auth/login')) {
        console.error('未登录或登录已过期')
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        localStorage.removeItem('role')
        window.location.href = '/login'
      } else if (status === 403) {
        console.error('没有权限访问')
      } else if (status === 404) {
        console.error('接口不存在')
      } else if (status >= 500) {
        console.error('服务器错误')
      }
    } else if (error.request) {
      console.error('网络错误，后端未响应')
    } else {
      console.error('请求配置错误：', error.message)
    }

    return Promise.reject(error)
  }
)

export default request
