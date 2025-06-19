import request from '@/utils/request'

// 获取所有设置
// 已移除后端API调用，改为使用localStorage
export function getSettings() {
  console.warn('getSettings API已弃用，请使用localStorage');
  return Promise.resolve({});
}

// 获取单个设置
// 已移除后端API调用，改为使用localStorage
export function getSetting(key: string) {
  console.warn('getSetting API已弃用，请使用localStorage');
  const value = localStorage.getItem(key);
  return Promise.resolve({ [key]: value });
}

// 更新设置
// 已移除后端API调用，改为使用localStorage
export function updateSetting(key: string, value: any) {
  console.warn('updateSetting API已弃用，请使用localStorage');
  localStorage.setItem(key, typeof value === 'string' ? value : JSON.stringify(value));
  return Promise.resolve({ message: `设置 ${key} 更新成功` });
}

// 重置为默认设置
// 已移除后端API调用，改为使用localStorage
export function resetToDefault() {
  console.warn('resetToDefault API已弃用，请使用localStorage');
  // 清除所有设置
  localStorage.removeItem('theme');
  localStorage.removeItem('font_size');
  localStorage.removeItem('font_family');
  localStorage.removeItem('line_height');
  localStorage.removeItem('cache_enabled');
  localStorage.removeItem('cache_expiration');
  localStorage.removeItem('log_level');
  return Promise.resolve({ message: '设置已重置为默认值' });
}