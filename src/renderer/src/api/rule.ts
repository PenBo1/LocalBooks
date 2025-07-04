import request from '@/utils/request'

// 获取规则列表
export function getRules(page: number = 1, page_size: number = 10, sort_by: string = 'updated_at') {
  return request({
    url: '/rule/',
    method: 'get',
    params: { page, page_size, sort_by }
  })
}

// 获取规则详情
export function getRule(id: number) {
  // 确保id是有效的数字，避免发送undefined请求
  if (!id || isNaN(Number(id))) {
    return Promise.reject(new Error('无效的规则ID'))
  }
  return request({
    url: `/rule/${id}`,
    method: 'get'
  })
}

// 创建规则
export function createRule(data: {
  name: string
  source_url: string
  search_url: string
  search_result_rule?: string
  cover_rule?: string
  title_rule: string
  author_rule?: string
  description_rule?: string
  chapter_list_rule: string
  chapter_content_rule: string
}) {
  return request({
    url: '/rule/',
    method: 'post',
    data
  })
}

// 更新规则
export function updateRule(id: number, data: {
  name?: string
  source_url?: string
  search_url?: string
  search_result_rule?: string
  cover_rule?: string
  title_rule?: string
  author_rule?: string
  description_rule?: string
  chapter_list_rule?: string
  chapter_content_rule?: string
}) {
  return request({
    url: `/rule/update/${id}`,
    method: 'post',
    data
  })
}

// 删除规则
export function deleteRule(id: number) {
  return request({
    url: `/rule/delete/${id}`,
    method: 'post'
  })
}