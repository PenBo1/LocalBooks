import request from '@/utils/request'

// 获取所有设置
export function getSettings() {
  return request({
    url: '/settings/',
    method: 'get'
  })
}

// 获取单个设置
export function getSetting(key: string) {
  return request({
    url: `/settings/${key}`,
    method: 'get'
  })
}

// 更新设置
export function updateSetting(key: string, value: any) {
  return request({
    url: `/settings/update/${key}`,
    method: 'post',
    data: value
  })
}

// 重置为默认设置
export function resetToDefault() {
  return request({
    url: '/settings/default/reset',
    method: 'post'
  })
}