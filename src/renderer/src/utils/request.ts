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
    console.log('API响应成功:', response.config.url, response.data)
    return response.data
  },
  (error) => {
    // 对响应错误做点什么
    console.error('API响应错误:', error)
    
    // 根据错误类型显示不同的错误信息
    if (error.response) {
      // 服务器返回了错误状态码
      const status = error.response.status
      const data = error.response.data
      
      console.error(`服务器返回错误 ${status}:`, data)
      
      let message = '服务器错误，请稍后再试'
      if (data) {
        if (typeof data === 'string') {
          message = data
        } else if (data.detail) {
          message = data.detail
        } else if (data.message) {
          message = data.message
        } else if (data.error) {
          message = data.error
        }
      }
      
      ElMessage.error(message)
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('未收到服务器响应:', error.request)
      ElMessage.error('网络错误，未收到服务器响应')
    } else {
      // 请求配置出错
      console.error('请求配置错误:', error.message)
      ElMessage.error(`请求错误: ${error.message}`)
    }
    
    return Promise.reject(error)
  }
)

export default service