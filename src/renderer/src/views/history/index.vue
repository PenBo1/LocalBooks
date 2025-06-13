<template>
  <div class="history-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索历史记录"
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
          <el-radio-button label="read_at">时间排序</el-radio-button>
          <el-radio-button label="title">名称排序</el-radio-button>
        </el-radio-group>
      </div>

      <el-button type="danger" @click="confirmClearAllHistory">
        <el-icon><Delete /></el-icon>
        清空历史
      </el-button>
    </div>

    <!-- 历史内容 -->
    <div class="history-content">
      <el-empty v-if="filteredHistory.length === 0" description="暂无阅读历史" />

      <div v-else class="novel-grid">
        <novel-card
          v-for="item in filteredHistory"
          :key="item.id"
          :novel="item.novel"
          :show-read-time="true"
          :show-last-read="true"
          :show-delete-history="true"
          @click="goToNovelReading(item.novel.id, item.chapter_id, item.read_position)"
          @delete-history="confirmDeleteHistory(item)"
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

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除确认"
      width="30%"
      :close-on-click-modal="false"
    >
      <span>确定要删除《{{ historyToDelete?.novel?.title }}》的阅读历史吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="deleteHistory">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 清空确认对话框 -->
    <el-dialog
      v-model="clearAllDialogVisible"
      title="清空确认"
      width="30%"
      :close-on-click-modal="false"
    >
      <span>确定要清空所有阅读历史吗？此操作不可恢复！</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="clearAllDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="clearAllHistory">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Delete } from '@element-plus/icons-vue'
import { getHistory, deleteHistory as apiDeleteHistory, clearAllHistory as apiClearAllHistory } from '@/api/history'
import NovelCard from '@/components/NovelCard.vue'

const router = useRouter()

// 分页相关
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 排序和搜索
const sortBy = ref('read_at')
const searchQuery = ref('')

// 历史数据
const historyList = ref([])
const loading = ref(false)

// 删除相关
const deleteDialogVisible = ref(false)
const historyToDelete = ref(null)
const clearAllDialogVisible = ref(false)

// 过滤后的历史列表
const filteredHistory = computed(() => {
  if (!searchQuery.value) {
    return historyList.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return historyList.value.filter(item => {
    const novel = item.novel
    return novel.title.toLowerCase().includes(query) || 
           (novel.author && novel.author.toLowerCase().includes(query))
  })
})

// 获取历史数据
const fetchHistory = async () => {
  loading.value = true
  try {
    const response = await getHistory(currentPage.value, pageSize.value, sortBy.value)
    historyList.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('获取历史数据失败:', error)
    ElMessage.error('获取历史数据失败，请稍后重试')
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
  fetchHistory()
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  fetchHistory()
}

// 处理分页页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchHistory()
}

// 跳转到小说阅读页
const goToNovelReading = (novelId: number, chapterId: number, readPosition: number) => {
  router.push({
    path: `/novel/${novelId}/chapter/${chapterId}`,
    query: { position: readPosition.toString() }
  })
}

// 确认删除历史
const confirmDeleteHistory = (history) => {
  historyToDelete.value = history
  deleteDialogVisible.value = true
}

// 删除历史
const deleteHistory = async () => {
  if (!historyToDelete.value) return
  
  try {
    await apiDeleteHistory(historyToDelete.value.id)
    ElMessage.success(`已删除《${historyToDelete.value.novel.title}》的阅读历史`)
    deleteDialogVisible.value = false
    fetchHistory()
  } catch (error) {
    console.error('删除历史失败:', error)
    ElMessage.error('删除历史失败，请稍后重试')
  }
}

// 确认清空所有历史
const confirmClearAllHistory = () => {
  clearAllDialogVisible.value = true
}

// 清空所有历史
const clearAllHistory = async () => {
  try {
    await apiClearAllHistory()
    ElMessage.success('已清空所有阅读历史')
    clearAllDialogVisible.value = false
    fetchHistory()
  } catch (error) {
    console.error('清空历史失败:', error)
    ElMessage.error('清空历史失败，请稍后重试')
  }
}

// 监听搜索查询变化
watch(searchQuery, (newVal) => {
  if (!newVal) {
    // 如果搜索框被清空，重新获取所有数据
    fetchHistory()
  }
})

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped lang="scss">
.history-container {
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