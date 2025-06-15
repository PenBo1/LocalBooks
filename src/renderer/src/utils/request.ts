import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service = axios.create({
  baseURL: '/api', // API的base_url
  timeout: 15000, // 请求超时时间
  maxRedirects: 5, // 允许的最大重定向次数
  withCredentials: true // 允许跨域请求携带凭证
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 在发送请求之前做些什么
    return config
  },
  (error) => {
    // 对请求错误做些什么
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    // 对响应数据做点什么
    return response.data
  },
  (error) => {
    // 对响应错误做点什么
    console.error('响应错误:', error)
    const message = error.response?.data?.detail || '服务器错误，请稍后再试'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service