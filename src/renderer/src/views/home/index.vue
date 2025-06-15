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
    </div>

    <!-- 搜索结果 -->
    <div v-if="showSearchResults" class="search-results">
      <div class="section-header">
        <h2>搜索结果</h2>
        <el-button text @click="clearSearchResults">清空</el-button>
      </div>

      <el-empty v-if="searchResults.length === 0" description="暂无搜索结果" />

      <div v-else class="novel-grid">
        <novel-card
          v-for="novel in searchResults"
          :key="novel.id"
          :novel="novel"
          @click="goToNovelDetail(novel.id)"
        />
      </div>

      <el-pagination
        v-if="searchResults.length > 0"
        v-model:current-page="searchPage"
        v-model:page-size="searchPageSize"
        :page-sizes="[10, 20, 30, 40]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="searchTotal"
        @size-change="handleSearchSizeChange"
        @current-change="handleSearchCurrentChange"
      />
    </div>

    <!-- 热门推荐 -->
    <div class="hot-novels">
      <div class="section-header">
        <h2>热门推荐</h2>
        <el-button text @click="refreshHotNovels">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <el-skeleton v-if="loading" :rows="3" animated />

      <el-empty v-else-if="hotNovels.length === 0" description="暂无热门小说" />

      <div v-else class="novel-grid">
        <novel-card
          v-for="novel in hotNovels"
          :key="novel.id"
          :novel="novel"
          @click="goToNovelDetail(novel.id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { searchNovels, getHotNovels } from '@/api/novel'
import NovelCard from '@/components/NovelCard.vue'

const router = useRouter()

// 搜索相关
const searchQuery = ref('')
const searchResults = ref([])
const searchPage = ref(1)
const searchPageSize = ref(10)
const searchTotal = ref(0)
const showSearchResults = ref(false)

// 热门推荐相关
const hotNovels = ref([])
const loading = ref(false)

// 搜索小说
const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }

  try {
    const response = await searchNovels(searchQuery.value, searchPage.value, searchPageSize.value)
    searchResults.value = response.data.items
    searchTotal.value = response.data.total
    showSearchResults.value = true
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

// 获取热门小说
const fetchHotNovels = async () => {
  loading.value = true
  try {
    const response = await getHotNovels()
    hotNovels.value = response.data
  } catch (error) {
    console.error('获取热门小说失败:', error)
    ElMessage.error('获取热门小说失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 刷新热门小说
const refreshHotNovels = () => {
  fetchHotNovels()
}

// 跳转到小说详情页
const goToNovelDetail = (novelId: number) => {
  router.push(`/novel/${novelId}`)
}

onMounted(() => {
  fetchHotNovels()
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

  .search-input {
    width: 100%;
    max-width: 600px;
  }
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

.hot-novels {
  margin-bottom: 30px;
}
</style>