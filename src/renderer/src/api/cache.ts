import request from '@/utils/request'

// 获取缓存信息
export function getCacheInfo() {
  return request({
    url: '/cache/info',
    method: 'get'
  })
}

// 创建缓存目录
export function createCacheDirectory() {
  return request({
    url: '/cache/create',
    method: 'post'
  })
}

// 设置缓存目录路径
export function setCacheDirectory(path: string) {
  return request({
    url: '/cache/set-directory',
    method: 'post',
    data: { path }
  })
}

// 选择缓存目录
export async function selectCacheDirectory() {
  try {
    // 调用Electron的选择目录对话框
    const path = await window.api.selectDirectory({
      title: '选择缓存目录',
      buttonLabel: '设置为缓存目录'
    })
    
    if (path) {
      // 设置选择的目录为缓存目录
      return await setCacheDirectory(path)
    }
    return null
  } catch (error) {
    console.error('选择缓存目录失败:', error)
    throw error
  }
}

// 打开缓存目录
export function openCacheDirectory() {
  return request({
    url: '/cache/open',
    method: 'post'
  })
}

// 清空缓存
export function clearCache() {
  return request({
    url: '/cache/clear',
    method: 'delete'
  })
}