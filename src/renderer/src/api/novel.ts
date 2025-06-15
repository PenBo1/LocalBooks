import request from '@/utils/request'

// 搜索小说
export function searchNovels(keyword: string, rule_id: number) {
  return request({
    url: '/novel/search',
    method: 'get',
    params: { keyword, rule_id }
  })
}

// 获取热门小说
export function getHotNovels(limit: number = 10) {
  return request({
    url: '/novel/hot',
    method: 'get',
    params: { limit }
  })
}

// 获取小说详情
export function getNovelDetail(id: number) {
  return request({
    url: `/novel/${id}`,
    method: 'get'
  })
}

// 获取小说章节列表
export function getNovelChapters(id: number) {
  return request({
    url: `/novel/${id}/chapters`,
    method: 'get'
  })
}

// 获取章节内容
export function getChapterContent(novelId: number, chapterId: number) {
  return request({
    url: `/novel/${novelId}/chapter/${chapterId}`,
    method: 'get'
  })
}

// 从网络获取小说详情
export function getNovelDetailFromNetwork(id: number) {
  return request({
    url: `/novel/${id}/detail/network`,
    method: 'get'
  })
}

// 从网络获取小说章节列表
export function getNovelChaptersFromNetwork(id: number) {
  return request({
    url: `/novel/${id}/chapters/network`,
    method: 'get'
  })
}

// 从网络获取章节内容
export function getChapterContentFromNetwork(novelId: number, chapterId: number) {
  return request({
    url: `/novel/${novelId}/chapter/${chapterId}/network`,
    method: 'get'
  })
}

// 下载小说所有章节
export function downloadAllChapters(novelId: number) {
  return request({
    url: `/novel/${novelId}/download`,
    method: 'post'
  })
}