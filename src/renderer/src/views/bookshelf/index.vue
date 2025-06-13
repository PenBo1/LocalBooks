<template>
  <div class="bookshelf-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索书架中的小说"
        class="search-input"
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <div class="sort-options">
        <el-radio-group v-model="sortBy" size="small" @change="handleSortChange">
          <el-radio-button label="updated_at">时间排序</el-radio-button>
          <el-radio-button label="title">名称排序</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 书架内容 -->
    <div class="bookshelf-content">
      <el-empty v-if="filteredNovels.length === 0" description="书架空空如也" />

      <div v-else class="novel-grid">
        <novel-card
          v-for="novel in filteredNovels"
          :key="novel.id"
          :novel="novel"
          :show-bookshelf-badge="true"
          :show-last-read="true"
          :show-remove-from-bookshelf="true"
          @click="goToNovelDetail(novel.id)"
          @remove-from-bookshelf="confirmRemoveFromBookshelf(novel)"
        />
      </div>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 36, 48]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 移除确认对话框 -->
    <el-dialog
      v-model="removeDialogVisible"
      title="移除确认"
      width="30%"
      :close-on-click-modal="false"
    >
      <span>确定要将《{{ novelToRemove?.title }}》从书架中移除吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="removeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="removeFromBookshelf">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getBookshelf, removeFromBookshelf as apiRemoveFromBookshelf } from '@/api/bookshelf'
import NovelCard from '@/components/NovelCard.vue'

const router = useRouter()

// 分页相关
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 排序和搜索
const sortBy = ref('updated_at')
const searchQuery = ref('')

// 书架数据
const novels = ref([])
const loading = ref(false)

// 移除相关
const removeDialogVisible = ref(false)
const novelToRemove = ref(null)

// 过滤后的小说列表
const filteredNovels = computed(() => {
  if (!searchQuery.value) {
    return novels.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return novels.value.filter(novel => {
    return novel.title.toLowerCase().includes(query) || 
           (novel.author && novel.author.toLowerCase().includes(query))
  })
})

// 获取书架数据
const fetchBookshelf = async () => {
  loading.value = true
  try {
    const response = await getBookshelf(currentPage.value, pageSize.value, sortBy.value)
    novels.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('获取书架数据失败:', error)
    ElMessage.error('获取书架数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  // 本地搜索，不需要重新请求
}

// 处理排序变化
const handleSortChange = () => {
  currentPage.value = 1
  fetchBookshelf()
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  fetchBookshelf()
}

// 处理分页页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchBookshelf()
}

// 跳转到小说详情页
const goToNovelDetail = (novelId: number) => {
  router.push(`/novel/${novelId}`)
}

// 确认移除书架
const confirmRemoveFromBookshelf = (novel) => {
  novelToRemove.value = novel
  removeDialogVisible.value = true
}

// 从书架移除
const removeFromBookshelf = async () => {
  if (!novelToRemove.value) return
  
  try {
    await apiRemoveFromBookshelf(novelToRemove.value.id)
    ElMessage.success(`已将《${novelToRemove.value.title}》从书架中移除`)
    removeDialogVisible.value = false
    fetchBookshelf()
  } catch (error) {
    console.error('从书架移除失败:', error)
    ElMessage.error('从书架移除失败，请稍后重试')
  }
}

// 监听搜索查询变化
watch(searchQuery, (newVal) => {
  if (!newVal) {
    // 如果搜索框被清空，重新获取所有数据
    fetchBookshelf()
  }
})

onMounted(() => {
  fetchBookshelf()
})
</script>

<style scoped lang="scss">
.bookshelf-container {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .search-input {
    width: 300px;
  }

  .sort-options {
    display: flex;
    align-items: center;
  }
}

.novel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>