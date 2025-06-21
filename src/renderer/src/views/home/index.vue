<template>
  <div class="home-container">
    <!-- 搜索区域 -->
    <div class="search-container">
      <el-input
        v-model="searchQuery"
        placeholder="请输入小说名称或作者"
        class="search-input"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </template>
      </el-input>
      
      <!-- 搜索历史标签 -->
      <div v-if="searchHistories && searchHistories.length > 0" class="search-history-tags">
        <span class="history-label">搜索历史：</span>
        <el-tag 
          v-for="history in searchHistories" 
          :key="history.id"
          class="history-tag"
          size="small"
          closable
          @click="useSearchHistory(history.keyword)"
          @close="deleteSearchHistory(history.id)"
        >
          {{ history.keyword }}
        </el-tag>
        <el-button 
          type="text" 
          size="small" 
          @click="clearAllSearchHistory"
        >
          清空历史
        </el-button>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-if="showSearchResults" class="search-results">
      <div class="section-header">
        <h2>搜索结果</h2>
        <el-button text @click="clearSearchResults">清空</el-button>
      </div>

      <el-empty v-if="!searchResults || searchResults.length === 0" description="暂无搜索结果" />

      <div v-else class="novel-grid">
        <novel-card
          v-for="novel in searchResults"
          :key="novel.id"
          :novel="novel"
          @click="goToNovelDetail(novel.id)"
        />
      </div>

      <el-pagination
        v-if="searchResults && searchResults.length > 0"
        v-model:current-page="searchPage"
        v-model:page-size="searchPageSize"
        :page-sizes="[10, 20, 30, 40]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="searchTotal"
        @size-change="handleSearchSizeChange"
        @current-change="handleSearchCurrentChange"
      />
    </div>

    <!-- 搜索历史标签展示 -->
    <div class="search-history-section">
      <div class="section-header">
        <h2>搜索历史</h2>
        <el-button text @click="fetchSearchHistory">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <el-skeleton v-if="loading" :rows="3" animated />

      <el-empty v-else-if="!searchHistories || searchHistories.length === 0" description="暂无搜索历史" />

      <div v-else class="search-history-container">
        <el-tag 
          v-for="history in searchHistories" 
          :key="history.id"
          class="history-tag-large"
          size="large"
          closable
          @click="useSearchHistory(history.keyword)"
          @close="deleteSearchHistory(history.id)"
        >
          {{ history.keyword }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { searchNovels } from '@/api/novel'
import { getSearchHistory, deleteSearchHistory as deleteSearchHistoryApi, clearAllSearchHistory as clearAllSearchHistoryApi } from '@/api/searchHistory'
import NovelCard from '@/components/NovelCard.vue'

const router = useRouter()

// 搜索相关
const searchQuery = ref('')
const searchResults = ref([])
const searchPage = ref(1)
const searchPageSize = ref(10)
const searchTotal = ref(0)
const showSearchResults = ref(false)

// 搜索历史相关
const searchHistories = ref([])

// 加载状态
const loading = ref(false)

// 获取搜索历史
const fetchSearchHistory = async () => {
  try {
    const response = await getSearchHistory(10) // 获取最近10条搜索历史
    searchHistories.value = response // 直接使用 response，因为 request.ts 中的响应拦截器已经返回了 response.data
    console.log('搜索历史数据:', searchHistories.value) // 添加日志以便调试
  } catch (error) {
    console.error('获取搜索历史失败:', error)
  }
}

// 使用搜索历史
const useSearchHistory = (keyword: string) => {
  searchQuery.value = keyword
  handleSearch()
}

// 删除搜索历史
const deleteSearchHistory = async (id: number) => {
  try {
    await deleteSearchHistoryApi(id)
    await fetchSearchHistory() // 重新获取搜索历史
    ElMessage.success('删除搜索历史成功')
  } catch (error) {
    console.error('删除搜索历史失败:', error)
    ElMessage.error('删除搜索历史失败，请稍后重试')
  }
}

// 清空所有搜索历史
const clearAllSearchHistory = async () => {
  try {
    await clearAllSearchHistoryApi()
    searchHistories.value = []
    ElMessage.success('清空搜索历史成功')
  } catch (error) {
    console.error('清空搜索历史失败:', error)
    ElMessage.error('清空搜索历史失败，请稍后重试')
  }
}

// 搜索小说
const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }

  try {
    const response = await searchNovels(searchQuery.value, 1) // 使用规则ID 1进行搜索
    searchResults.value = response // 直接使用 response，因为 request.ts 中的响应拦截器已经返回了 response.data
    searchTotal.value = response.length
    showSearchResults.value = true
    console.log('搜索结果数据:', searchResults.value) // 添加日志以便调试
    
    // 搜索成功后刷新搜索历史
    await fetchSearchHistory()
  } catch (error) {
    console.error('搜索小说失败:', error)
    ElMessage.error('搜索小说失败，请稍后重试')
  }
}

// 清空搜索结果
const clearSearchResults = () => {
  searchResults.value = []
  showSearchResults.value = false
  searchQuery.value = ''
}

// 处理搜索分页大小变化
const handleSearchSizeChange = (size: number) => {
  searchPageSize.value = size
  handleSearch()
}

// 处理搜索分页页码变化
const handleSearchCurrentChange = (page: number) => {
  searchPage.value = page
  handleSearch()
}

// 刷新搜索历史
const refreshSearchHistory = () => {
  loading.value = true
  fetchSearchHistory().finally(() => {
    loading.value = false
  })
}

// 跳转到小说详情页
const goToNovelDetail = (novelId: number) => {
  router.push(`/novel/${novelId}`)
}

onMounted(async () => {
  // 获取搜索历史
  await refreshSearchHistory()
})
</script>

<style scoped lang="scss">
.home-container {
  padding: 20px;
}

.search-container {
  margin-bottom: 30px;
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;

  .search-input {
    width: 100%;
    max-width: 600px;
  }
}

.search-history-tags {
  margin-top: 10px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  width: 100%;
  max-width: 600px;
}

.history-label {
  margin-right: 10px;
  color: #606266;
  font-size: 14px;
}

.history-tag {
  margin-right: 8px;
  margin-bottom: 5px;
  cursor: pointer;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h2 {
    font-size: 20px;
    font-weight: 600;
    margin: 0;
  }
}

.novel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.search-results {
  margin-bottom: 30px;
}

.search-history-section {
  margin-bottom: 30px;
}

.search-history-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.history-tag-large {
  font-size: 14px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.history-tag-large:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>