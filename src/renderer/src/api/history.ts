import request from '@/utils/request'

// 获取历史记录列表
export function getHistory(page: number = 1, page_size: number = 10, sort_by: string = 'read_at') {
  return request({
    url: '/history/',
    method: 'get',
    params: { page, page_size, sort_by }
  })
}

// 添加历史记录
export function addHistory(data: {
  novel_id: number
  chapter_id: number
  read_position: number
}) {
  return request({
    url: '/history/',
    method: 'post',
    data
  })
}

// 删除历史记录
export function deleteHistory(id: number) {
  return request({
    url: `/history/delete/${id}`,
    method: 'post'
  })
}

// 删除小说的所有历史记录
export function deleteNovelHistory(novel_id: number) {
  return request({
    url: `/history/delete/novel/${novel_id}`,
    method: 'post'
  })
}

// 清空所有历史记录
export function clearAllHistory() {
  return request({
    url: '/history/all/clear',
    method: 'post'
  })
}