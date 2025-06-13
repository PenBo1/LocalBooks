import request from '@/utils/request'

// 获取书架列表
export function getBookshelf(page: number = 1, page_size: number = 10, sort_by: string = 'updated_at') {
  return request({
    url: '/bookshelf',
    method: 'get',
    params: { page, page_size, sort_by }
  })
}

// 添加到书架
export function addToBookshelf(data: {
  novel_id: number
  last_read_chapter_id?: number
  last_read_position?: number
}) {
  return request({
    url: '/bookshelf',
    method: 'post',
    data
  })
}

// 更新书架项
export function updateBookshelfItem(id: number, data: {
  last_read_chapter_id?: number
  last_read_position?: number
}) {
  return request({
    url: `/bookshelf/${id}`,
    method: 'put',
    data
  })
}

// 从书架移除
export function removeFromBookshelf(novel_id: number) {
  return request({
    url: `/bookshelf/${novel_id}`,
    method: 'delete'
  })
}