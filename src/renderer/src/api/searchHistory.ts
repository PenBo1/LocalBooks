import request from '@/utils/request'

// 获取搜索历史列表
export function getSearchHistory(limit: number = 10) {
  return request({
    url: '/search_history/list',
    method: 'get',
    params: { limit }
  })
}

// 添加搜索历史
export function addSearchHistory(keyword: string) {
  return request({
    url: '/search_history/add',
    method: 'post',
    data: { keyword }
  })
}

// 删除搜索历史
export function deleteSearchHistory(id: number) {
  return request({
    url: `/search_history/${id}`,
    method: 'delete'
  })
}

// 根据关键词删除搜索历史
export function deleteSearchHistoryByKeyword(keyword: string) {
  return request({
    url: `/search_history/keyword/${keyword}`,
    method: 'delete'
  })
}

// 清空所有搜索历史
export function clearAllSearchHistory() {
  return request({
    url: '/search_history/clear',
    method: 'delete'
  })
}