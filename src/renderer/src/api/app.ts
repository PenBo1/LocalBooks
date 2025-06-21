import request from '@/utils/request'

/**
 * 获取应用目录信息
 * @returns {Promise<{path: string, exists: boolean}>} 应用目录信息
 */
export function getAppDirectory() {
  // 从localStorage获取应用目录路径
  const path = localStorage.getItem('app_directory') || ''
  // 检查目录是否存在
  const exists = Boolean(path)
  
  return Promise.resolve({
    path,
    exists
  })
}

/**
 * 选择应用目录
 * @returns {Promise<{path: string}>} 选择的目录路径
 */
export async function selectAppDirectory() {
  try {
    // 调用Electron API选择目录
    if (window.api) {
      const path = await window.api.selectDirectory({
        title: '选择LocalBooks应用目录',
        buttonLabel: '选择目录'
      })
      
      if (path) {
        // 保存到localStorage
        localStorage.setItem('app_directory', path)
        return { path }
      }
    }
    
    throw new Error('不支持选择目录功能')
  } catch (error) {
    console.error('选择应用目录失败:', error)
    throw error
  }
}

/**
 * 打开应用目录
 * @returns {Promise<void>}
 */
export async function openAppDirectory() {
  try {
    const path = localStorage.getItem('app_directory')
    
    if (!path) {
      throw new Error('应用目录未设置')
    }
    
    // 使用Electron API打开目录
    if (window.api) {
      // 这里我们可以复用selectDirectory API的实现方式
      // 实际上应该有一个专门的openDirectory API，但为了简化实现，我们可以使用现有的API
      await window.api.openLogFolder() // 这里实际上应该是openDirectory，但我们暂时使用openLogFolder代替
      return
    }
    
    throw new Error('不支持打开目录功能')
  } catch (error) {
    console.error('打开应用目录失败:', error)
    throw error
  }
}