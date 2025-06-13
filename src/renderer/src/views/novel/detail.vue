<template>
  <div class="novel-detail-container">
    <el-skeleton :loading="loading" animated>
      <template #template>
        <div class="novel-header skeleton">
          <div class="novel-cover-skeleton"></div>
          <div class="novel-info-skeleton">
            <el-skeleton-item variant="h1" style="width: 50%" />
            <el-skeleton-item variant="text" style="margin-top: 10px; width: 30%" />
            <el-skeleton-item variant="text" style="margin-top: 10px; width: 80%" />
            <el-skeleton-item variant="text" style="margin-top: 10px; width: 80%" />
          </div>
        </div>
      </template>

      <template #default>
        <div v-if="novel" class="novel-detail">
          <!-- 小说头部信息 -->
          <div class="novel-header">
            <div class="novel-cover">
              <el-image
                :src="novel.cover || defaultCover"
                fit="cover"
                :lazy="true"
                loading="lazy"
                :alt="novel.title"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>

            <div class="novel-info">
              <h1 class="novel-title">{{ novel.title }}</h1>
              <p class="novel-author" v-if="novel.author">
                <el-icon><User /></el-icon>
                作者：{{ novel.author }}
              </p>
              <p class="novel-source" v-if="novel.source_url">
                <el-icon><Link /></el-icon>
                来源：
                <el-link :href="novel.source_url" target="_blank" :underline="false">
                  {{ getSourceName(novel.source_url) }}
                </el-link>
              </p>
              <div class="novel-actions">
                <el-button
                  v-if="!novel.in_bookshelf"
                  type="primary"
                  @click="addToBookshelf"
                >
                  <el-icon><Star /></el-icon>
                  加入书架
                </el-button>
                <el-button
                  v-else
                  type="danger"
                  @click="removeFromBookshelf"
                >
                  <el-icon><Delete /></el-icon>
                  移出书架
                </el-button>
                <el-button
                  v-if="lastReadChapter"
                  type="success"
                  @click="continueReading"
                >
                  <el-icon><VideoPlay /></el-icon>
                  继续阅读
                </el-button>
                <el-button
                  v-else
                  type="success"
                  @click="startReading"
                >
                  <el-icon><Reading /></el-icon>
                  开始阅读
                </el-button>
              </div>
            </div>
          </div>

          <!-- 小说简介 -->
          <div class="novel-description">
            <h3>内容简介</h3>
            <p v-if="novel.description">{{ novel.description }}</p>
            <p v-else>暂无简介</p>
          </div>

          <!-- 章节列表 -->
          <div class="novel-chapters">
            <div class="chapters-header">
              <h3>章节列表</h3>
              <div class="chapters-actions">
                <el-input
                  v-model="chapterSearchQuery"
                  placeholder="搜索章节"
                  clearable
                  @input="filterChapters"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button-group>
                  <el-button
                    :type="sortOrder === 'asc' ? 'primary' : ''"
                    @click="changeSortOrder('asc')"
                  >
                    正序
                  </el-button>
                  <el-button
                    :type="sortOrder === 'desc' ? 'primary' : ''"
                    @click="changeSortOrder('desc')"
                  >
                    倒序
                  </el-button>
                </el-button-group>
              </div>
            </div>

            <el-skeleton v-if="chaptersLoading" :rows="10" animated />

            <template v-else>
              <el-empty v-if="filteredChapters.length === 0" description="暂无章节" />

              <div v-else class="chapters-list">
                <div
                  v-for="chapter in paginatedChapters"
                  :key="chapter.id"
                  class="chapter-item"
                  :class="{ 'is-read': isChapterRead(chapter.id) }"
                  @click="goToChapter(chapter.id)"
                >
                  <span class="chapter-title">{{ chapter.title }}</span>
                  <span v-if="isChapterRead(chapter.id)" class="read-badge">
                    <el-icon><Check /></el-icon>
                  </span>
                </div>
              </div>

              <el-pagination
                v-if="filteredChapters.length > pageSize"
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[20, 50, 100, 200]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="filteredChapters.length"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </template>
          </div>
        </div>

        <el-empty v-else description="未找到小说信息" />
      </template>
    </el-skeleton>

    <!-- 书架确认对话框 -->
    <el-dialog
      v-model="bookshelfDialogVisible"
      :title="bookshelfDialogTitle"
      width="30%"
      :close-on-click-modal="false"
    >
      <span>{{ bookshelfDialogMessage }}</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="bookshelfDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmBookshelfAction">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Picture, User, Link, Star, Delete, VideoPlay, Reading, Search, Check } from '@element-plus/icons-vue'
import { getNovelDetail, getNovelChapters } from '@/api/novel'
import { addToBookshelf, removeFromBookshelf as apiRemoveFromBookshelf } from '@/api/bookshelf'

const route = useRoute()
const router = useRouter()

// 默认封面
const defaultCover = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgMzAwIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2YyZjJmMiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMzYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIGZpbGw9IiM5OTkiPuaXoOWbvueJhzwvdGV4dD48L3N2Zz4='

// 小说ID
const novelId = computed(() => Number(route.params.id))

// 小说数据
const novel = ref(null)
const chapters = ref([])
const loading = ref(true)
const chaptersLoading = ref(true)

// 章节搜索和排序
const chapterSearchQuery = ref('')
const sortOrder = ref('asc')
const filteredChapters = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(50)

// 书架相关
const bookshelfDialogVisible = ref(false)
const bookshelfDialogTitle = ref('')
const bookshelfDialogMessage = ref('')
const bookshelfAction = ref('')

// 最后阅读的章节
const lastReadChapter = computed(() => {
  return novel.value?.last_read_chapter || null
})

// 分页后的章节列表
const paginatedChapters = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredChapters.value.slice(start, end)
})

// 获取小说详情
const fetchNovelDetail = async () => {
  loading.value = true
  try {
    const response = await getNovelDetail(novelId.value)
    novel.value = response.data
  } catch (error) {
    console.error('获取小说详情失败:', error)
    ElMessage.error('获取小说详情失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 获取小说章节
const fetchNovelChapters = async () => {
  chaptersLoading.value = true
  try {
    const response = await getNovelChapters(novelId.value)
    chapters.value = response.data
    filterChapters()
  } catch (error) {
    console.error('获取小说章节失败:', error)
    ElMessage.error('获取小说章节失败，请稍后重试')
  } finally {
    chaptersLoading.value = false
  }
}

// 过滤章节
const filterChapters = () => {
  let result = [...chapters.value]
  
  // 搜索过滤
  if (chapterSearchQuery.value) {
    const query = chapterSearchQuery.value.toLowerCase()
    result = result.filter(chapter => 
      chapter.title.toLowerCase().includes(query)
    )
  }
  
  // 排序
  result.sort((a, b) => {
    if (sortOrder.value === 'asc') {
      return a.index - b.index
    } else {
      return b.index - a.index
    }
  })
  
  filteredChapters.value = result
}

// 改变排序顺序
const changeSortOrder = (order) => {
  sortOrder.value = order
  filterChapters()
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

// 处理分页页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 获取来源网站名称
const getSourceName = (url: string) => {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname
  } catch (e) {
    return url
  }
}

// 判断章节是否已读
const isChapterRead = (chapterId: number) => {
  if (!novel.value || !novel.value.read_chapters) return false
  return novel.value.read_chapters.includes(chapterId)
}

// 跳转到章节阅读页
const goToChapter = (chapterId: number) => {
  router.push(`/novel/${novelId.value}/chapter/${chapterId}`)
}

// 开始阅读（第一章）
const startReading = () => {
  if (chapters.value.length > 0) {
    const firstChapter = chapters.value.find(c => c.index === 1) || chapters.value[0]
    goToChapter(firstChapter.id)
  } else {
    ElMessage.warning('暂无章节可阅读')
  }
}

// 继续阅读
const continueReading = () => {
  if (lastReadChapter.value) {
    goToChapter(lastReadChapter.value.id)
  } else {
    startReading()
  }
}

// 加入书架
const addToBookshelf = () => {
  bookshelfDialogTitle.value = '加入书架'
  bookshelfDialogMessage.value = `确定将《${novel.value.title}》加入书架吗？`
  bookshelfAction.value = 'add'
  bookshelfDialogVisible.value = true
}

// 移出书架
const removeFromBookshelf = () => {
  bookshelfDialogTitle.value = '移出书架'
  bookshelfDialogMessage.value = `确定将《${novel.value.title}》从书架中移除吗？`
  bookshelfAction.value = 'remove'
  bookshelfDialogVisible.value = true
}

// 确认书架操作
const confirmBookshelfAction = async () => {
  try {
    if (bookshelfAction.value === 'add') {
      await addToBookshelf({
        novel_id: novelId.value,
        last_read_chapter_id: lastReadChapter.value?.id,
        last_read_position: 0
      })
      novel.value.in_bookshelf = true
      ElMessage.success(`已将《${novel.value.title}》加入书架`)
    } else if (bookshelfAction.value === 'remove') {
      await apiRemoveFromBookshelf(novelId.value)
      novel.value.in_bookshelf = false
      ElMessage.success(`已将《${novel.value.title}》从书架中移除`)
    }
    bookshelfDialogVisible.value = false
  } catch (error) {
    console.error('书架操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 监听路由参数变化
watch(
  () => route.params.id,
  () => {
    fetchNovelDetail()
    fetchNovelChapters()
  }
)

onMounted(() => {
  fetchNovelDetail()
  fetchNovelChapters()
})
</script>

<style scoped lang="scss">
.novel-detail-container {
  padding: 20px;
}

.novel-detail {
  background-color: var(--el-bg-color);
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
  overflow: hidden;
}

.novel-header {
  display: flex;
  padding: 20px;
  border-bottom: 1px solid var(--el-border-color-light);

  &.skeleton {
    height: 240px;
  }

  .novel-cover {
    width: 180px;
    height: 240px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: var(--el-box-shadow);
    flex-shrink: 0;

    .el-image {
      width: 100%;
      height: 100%;
    }

    .image-error {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      height: 100%;
      background-color: var(--el-fill-color-light);
      color: var(--el-text-color-secondary);
      font-size: 24px;
    }
  }

  .novel-cover-skeleton {
    width: 180px;
    height: 240px;
    background-color: var(--el-fill-color);
    border-radius: 8px;
  }

  .novel-info {
    flex: 1;
    margin-left: 20px;
    display: flex;
    flex-direction: column;

    .novel-title {
      font-size: 24px;
      font-weight: 600;
      margin: 0 0 15px;
      color: var(--el-text-color-primary);
    }

    .novel-author,
    .novel-source {
      display: flex;
      align-items: center;
      margin: 8px 0;
      color: var(--el-text-color-regular);

      .el-icon {
        margin-right: 8px;
      }
    }

    .novel-actions {
      margin-top: auto;
      display: flex;
      gap: 10px;
    }
  }

  .novel-info-skeleton {
    flex: 1;
    margin-left: 20px;
  }
}

.novel-description {
  padding: 20px;
  border-bottom: 1px solid var(--el-border-color-light);

  h3 {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 15px;
    color: var(--el-text-color-primary);
  }

  p {
    margin: 0;
    line-height: 1.8;
    color: var(--el-text-color-regular);
    white-space: pre-line;
  }
}

.novel-chapters {
  padding: 20px;

  .chapters-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 {
      font-size: 18px;
      font-weight: 600;
      margin: 0;
      color: var(--el-text-color-primary);
    }

    .chapters-actions {
      display: flex;
      align-items: center;
      gap: 15px;

      .el-input {
        width: 200px;
      }
    }
  }

  .chapters-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
    margin-bottom: 20px;

    .chapter-item {
      padding: 10px 15px;
      border-radius: 4px;
      background-color: var(--el-fill-color-light);
      cursor: pointer;
      transition: all 0.3s;
      display: flex;
      justify-content: space-between;
      align-items: center;
      overflow: hidden;

      &:hover {
        background-color: var(--el-color-primary-light-9);
      }

      &.is-read {
        color: var(--el-text-color-secondary);
      }

      .chapter-title {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .read-badge {
        flex-shrink: 0;
        margin-left: 5px;
        color: var(--el-color-success);
      }
    }
  }

  .el-pagination {
    justify-content: center;
    margin-top: 20px;
  }
}
</style>