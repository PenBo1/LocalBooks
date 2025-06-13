import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/index.vue'),
    redirect: '/home',
    children: [
      {
        path: '/home',
        name: 'Home',
        component: () => import('@/views/home/index.vue'),
        meta: { title: '首页', icon: 'House' }
      },
      {
        path: '/bookshelf',
        name: 'Bookshelf',
        component: () => import('@/views/bookshelf/index.vue'),
        meta: { title: '书架', icon: 'Collection' }
      },
      {
        path: '/history',
        name: 'History',
        component: () => import('@/views/history/index.vue'),
        meta: { title: '历史', icon: 'Clock' }
      },
      {
        path: '/rule',
        name: 'Rule',
        component: () => import('@/views/rule/index.vue'),
        meta: { title: '管理', icon: 'Setting' }
      },
      {
        path: '/about',
        name: 'About',
        component: () => import('@/views/about/index.vue'),
        meta: { title: '关于', icon: 'InfoFilled' }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '设置', icon: 'Tools' }
      }
    ]
  },
  {
    path: '/novel/:id',
    name: 'NovelDetail',
    component: () => import('@/views/novel/detail.vue'),
    meta: { title: '小说详情' }
  },
  {
    path: '/novel/:id/chapters',
    name: 'NovelChapters',
    component: () => import('@/views/novel/chapters.vue'),
    meta: { title: '章节列表' }
  },
  {
    path: '/novel/:novelId/chapter/:chapterId',
    name: 'NovelReading',
    component: () => import('@/views/novel/reading.vue'),
    meta: { title: '阅读' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/404.vue'),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router