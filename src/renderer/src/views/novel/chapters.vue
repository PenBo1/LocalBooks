<template>
  <div class="chapters-container">
    <div class="chapters-header">
      <div class="novel-info" v-if="novel">
        <div class="novel-cover">
          <el-image :src="novel.cover" fit="cover" :lazy="true">
            <template #error>
              <div class="image-placeholder">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </div>
        <div class="novel-meta">
          <h1 class="novel-title">{{ novel.title }}</h1>
          <p class="novel-author">作者：{{ novel.author }}</p>
          <p class="novel-source">来源：{{ novel.source }}</p>
          <div class="novel-actions">
            <el-button type="primary" @click="startReading" :loading="loading">
              {{ novel.last_read_chapter_id ? '继续阅读' : '开始阅读' }}
            </el-button>
            <el-button 
              :type="novel.in_bookshelf ? 'danger' : 'success'"
              @click="toggleBookshelf"
              :loading="bookshelfLoading"
            >
              {{ novel.in_bookshelf ? '移出书架' : '加入书架' }}
            </el-button>
            <el-button 
              type="warning"
              @click="downloadChapters"
              :loading="downloadLoading"
            >
              <el-icon><Download /></el-icon> 下载全部章节
            </el-button>
          </div>
        </div>
      </div>
      <el-skeleton v-else :rows="3" animated />
    </div>

    <div class="chapters-toolbar">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索章节"
          clearable
          @input="filterChapters"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="sort-options">
        <el-radio-group v-model="sortOrder" @change="sortChapters">
          <el-radio-button label="asc">正序</el-radio-button>
          <el-radio-button label="desc">倒序</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div class="chapters-list">
      <el-skeleton v-if="loading" :rows="10" animated />
      <template v-else>
        <el-empty v-if="filteredChapters.length === 0" description="暂无章节" />
        <div v-else class="chapter-grid">
          <div
            v-for="chapter in filteredChapters"
            :key="chapter.id"
            class="chapter-item"
            :class="{ 'read': chapter.is_read, 'current': chapter.id === novel?.last_read_chapter_id }"
            @click="goToChapter(chapter.id)"
          >
            <span class="chapter-title">{{ chapter.title }}</span>
            <span v-if="chapter.is_read" class="read-mark">已读</span>
            <span v-if="chapter.id === novel?.last_read_chapter_id" class="current-mark">当前</span>
          </div>
        </div>
      </template>
    </div>

    <div class="pagination-container" v-if="!loading && totalChapters > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalChapters"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Picture, Search, Download } from '@element-plus/icons-vue'
import { getNovelDetail, getNovelChapters, downloadAllChapters } from '@/api/novel'
import { addToBookshelf, removeFromBookshelf } from '@/api/bookshelf'

const route = useRoute()
const router = useRouter()

// 小说ID
const novelId = computed(() => Number(route.params.novelId))

// 小说和章节数据
const novel = ref(null)
const chapters = ref([])
const filteredChapters = ref([])
const loading = ref(true)
const bookshelfLoading = ref(false)
const downloadLoading = ref(false)

// 搜索和排序
const searchQuery = ref('')
const sortOrder = ref('asc')

// 分页
const currentPage = ref(1)
const pageSize = ref(50)
const totalChapters = computed(() => chapters.value.length)

// 获取小说详情
const fetchNovelDetail = async () => {
  try {
    const response = await getNovelDetail(novelId.value)
    novel.value = response.data
  } catch (error) {
    console.error('获取小说详情失败:', error)
    ElMessage.error('获取小说详情失败，请稍后重试')
  }
}

// 获取小说章节列表
const fetchNovelChapters = async () => {
  loading.value = true
  try {
    const response = await getNovelChapters(novelId.value)
    chapters.value = response.data
    sortChapters()
    filterChapters()
  } catch (error) {
    console.error('获取小说章节失败:', error)
    ElMessage.error('获取小说章节失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 过滤章节
const filterChapters = () => {
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filteredChapters.value = chapters.value.filter(chapter => 
      chapter.title.toLowerCase().includes(query)
    )
  } else {
    filteredChapters.value = [...chapters.value]
  }
  
  // 应用分页
  applyPagination()
}

// 排序章节
const sortChapters = () => {
  const sorted = [...chapters.value]
  
  if (sortOrder.value === 'asc') {
    sorted.sort((a, b) => a.order - b.order)
  } else {
    sorted.sort((a, b) => b.order - a.order)
  }
  
  chapters.value = sorted
  filterChapters()
}

// 应用分页
const applyPagination = () => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  filteredChapters.value = filteredChapters.value.slice(start, end)
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  applyPagination()
}

// 处理每页显示数量变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  applyPagination()
}

// 跳转到阅读页面
const goToChapter = (chapterId: number) => {
  router.push(`/novel/${novelId.value}/chapter/${chapterId}`)
}

// 开始阅读
const startReading = () => {
  if (!novel.value) return
  
  if (novel.value.last_read_chapter_id) {
    // 继续上次阅读
    goToChapter(novel.value.last_read_chapter_id)
  } else if (chapters.value.length > 0) {
    // 从第一章开始
    goToChapter(chapters.value[0].id)
  } else {
    ElMessage.warning('暂无可阅读章节')
  }
}

// 切换书架状态
const toggleBookshelf = async () => {
  if (!novel.value) return
  
  bookshelfLoading.value = true
  try {
    if (novel.value.in_bookshelf) {
      // 从书架移除
      await removeFromBookshelf(novelId.value)
      novel.value.in_bookshelf = false
      ElMessage.success('已从书架移除')
    } else {
      // 添加到书架
      await addToBookshelf({
        novel_id: novelId.value,
        last_read_chapter_id: novel.value.last_read_chapter_id || null,
        last_read_position: novel.value.last_read_position || 0
      })
      novel.value.in_bookshelf = true
      ElMessage.success('已添加到书架')
    }
  } catch (error) {
    console.error('操作书架失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    bookshelfLoading.value = false
  }
}

// 下载全部章节
const downloadChapters = async () => {
  if (!novel.value) return
  
  downloadLoading.value = true
  try {
    await downloadAllChapters(novelId.value)
    ElMessage.success('章节下载任务已开始，请稍后查看')
    
    // 刷新章节列表以更新下载状态
    setTimeout(() => {
      fetchNovelChapters()
    }, 1000)
  } catch (error) {
    console.error('下载章节失败:', error)
    ElMessage.error('下载失败，请稍后重试')
  } finally {
    downloadLoading.value = false
  }
}

// 监听搜索和排序变化
watch([searchQuery, sortOrder], () => {
  currentPage.value = 1
})

onMounted(() => {
  fetchNovelDetail()
  fetchNovelChapters()
})
</script>

<style scoped lang="scss">
.chapters-container {
  padding: 20px;
}

.chapters-header {
  margin-bottom: 30px;
  
  .novel-info {
    display: flex;
    gap: 30px;
    
    .novel-cover {
      width: 180px;
      height: 240px;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      
      .el-image {
        width: 100%;
        height: 100%;
      }
      
      .image-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: var(--el-fill-color-light);
        color: var(--el-text-color-secondary);
        
        .el-icon {
          font-size: 40px;
        }
      }
    }
    
    .novel-meta {
      flex: 1;
      
      .novel-title {
        font-size: 24px;
        font-weight: 600;
        margin: 0 0 15px;
      }
      
      .novel-author,
      .novel-source {
        margin: 8px 0;
        color: var(--el-text-color-secondary);
      }
      
      .novel-actions {
        margin-top: 20px;
        display: flex;
        gap: 15px;
      }
    }
  }
}

.chapters-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .search-box {
    width: 300px;
  }
}

.chapters-list {
  margin-bottom: 30px;
  
  .chapter-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
  }
  
  .chapter-item {
    position: relative;
    padding: 15px;
    border-radius: 6px;
    background-color: var(--el-fill-color-light);
    cursor: pointer;
    transition: all 0.2s;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    
    &:hover {
      background-color: var(--el-color-primary-light-9);
    }
    
    &.read {
      color: var(--el-text-color-secondary);
    }
    
    &.current {
      background-color: var(--el-color-primary-light-8);
      color: var(--el-color-primary-dark-2);
      font-weight: 500;
    }
    
    .read-mark,
    .current-mark {
      position: absolute;
      top: 0;
      right: 0;
      font-size: 12px;
      padding: 2px 6px;
      color: #fff;
    }
    
    .read-mark {
      background-color: var(--el-color-info);
      border-bottom-left-radius: 6px;
    }
    
    .current-mark {
      background-color: var(--el-color-primary);
      border-bottom-left-radius: 6px;
    }
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>