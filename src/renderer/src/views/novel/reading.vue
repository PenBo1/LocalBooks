<template>
  <div
    class="reading-container"
    :class="{ 'sidebar-open': showSidebar }"
    :style="readingStyle"
    @click="handleContainerClick"
  >
    <!-- 顶部工具栏 -->
    <div class="reading-toolbar" :class="{ 'show': showToolbar }">
      <div class="toolbar-left">
        <el-button @click="goBack">
          <el-icon><Back /></el-icon>
          返回
        </el-button>
        <h2 class="novel-title" v-if="novel">{{ novel.title }}</h2>
      </div>
      <div class="toolbar-right">
        <el-button @click="toggleSidebar">
          <el-icon><Menu /></el-icon>
          目录
        </el-button>
        <el-button @click="toggleSettings">
          <el-icon><Setting /></el-icon>
          设置
        </el-button>
      </div>
    </div>

    <!-- 阅读内容 -->
    <div class="reading-content" ref="contentRef">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="15" animated />
      </div>
      <template v-else>
        <div class="chapter-header">
          <h1>{{ chapter?.title || '加载中...' }}</h1>
        </div>
        <div class="chapter-content" v-html="formattedContent"></div>
        <div class="chapter-footer">
          <el-button
            v-if="prevChapterId"
            @click="goToChapter(prevChapterId)"
            :disabled="loading"
          >
            <el-icon><ArrowLeft /></el-icon>
            上一章
          </el-button>
          <el-button
            v-if="nextChapterId"
            @click="goToChapter(nextChapterId)"
            :disabled="loading"
          >
            下一章
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
    </div>

    <!-- 侧边栏（章节目录） -->
    <div class="reading-sidebar" :class="{ 'show': showSidebar }">
      <div class="sidebar-header">
        <h3>目录</h3>
        <el-button text @click="toggleSidebar">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
      <div class="sidebar-search">
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
      </div>
      <div class="sidebar-content">
        <el-skeleton v-if="chaptersLoading" :rows="10" animated />
        <template v-else>
          <el-empty v-if="filteredChapters.length === 0" description="暂无章节" />
          <div v-else class="chapter-list">
            <div
              v-for="item in filteredChapters"
              :key="item.id"
              class="chapter-item"
              :class="{ 'active': item.id === chapterId }"
              @click="goToChapter(item.id)"
            >
              {{ item.title }}
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 设置面板 -->
    <el-drawer
      v-model="showSettings"
      title="阅读设置"
      direction="rtl"
      size="300px"
    >
      <div class="settings-panel">
        <h3>主题</h3>
        <div class="theme-options">
          <div
            v-for="option in themeOptions"
            :key="option.value"
            class="theme-option"
            :class="{ 'active': currentTheme === option.value }"
            @click="changeTheme(option.value)"
          >
            <div class="theme-preview" :class="`theme-${option.value}`">
              <el-icon v-if="option.icon">
                <component :is="option.icon" />
              </el-icon>
              <span>{{ option.label }}</span>
            </div>
          </div>
        </div>

        <el-divider />

        <h3>字体大小</h3>
        <div class="font-size-control">
          <el-button @click="decreaseFontSize" :disabled="fontSize <= 12">
            <el-icon><Minus /></el-icon>
          </el-button>
          <span class="font-size-value">{{ fontSize }}px</span>
          <el-button @click="increaseFontSize" :disabled="fontSize >= 28">
            <el-icon><Plus /></el-icon>
          </el-button>
        </div>

        <el-divider />

        <h3>字体</h3>
        <el-select v-model="fontFamily" placeholder="选择字体" style="width: 100%">
          <el-option
            v-for="font in fontOptions"
            :key="font.value"
            :label="font.label"
            :value="font.value"
            :style="{ fontFamily: font.value }"
          />
        </el-select>

        <el-divider />

        <h3>行距</h3>
        <el-slider
          v-model="lineHeight"
          :min="1"
          :max="3"
          :step="0.1"
          show-stops
        />

        <el-divider />

        <h3>段落间距</h3>
        <el-slider
          v-model="paragraphSpacing"
          :min="0.5"
          :max="3"
          :step="0.1"
          show-stops
        />
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Menu, Setting, ArrowLeft, ArrowRight, Close, Search, Minus, Plus } from '@element-plus/icons-vue'
import { getNovelDetail, getNovelChapters, getChapterContent } from '@/api/novel'
import { addHistory } from '@/api/history'
import { updateBookshelfItem } from '@/api/bookshelf'
import { useSettingsStore } from '@/store/settings'

const route = useRoute()
const router = useRouter()
const settingsStore = useSettingsStore()

// 小说和章节ID
const novelId = computed(() => Number(route.params.novelId))
const chapterId = computed(() => Number(route.params.chapterId))

// 阅读位置
const readPosition = ref(0)
const contentRef = ref(null)

// 小说和章节数据
const novel = ref(null)
const chapter = ref(null)
const chapters = ref([])
const content = ref('')
const loading = ref(true)
const chaptersLoading = ref(true)

// 章节搜索
const chapterSearchQuery = ref('')
const filteredChapters = ref([])

// UI 状态
const showToolbar = ref(false)
const showSidebar = ref(false)
const showSettings = ref(false)
const toolbarTimer = ref(null)

// 阅读设置
const currentTheme = ref(settingsStore.theme)
const fontSize = ref(settingsStore.fontSize)
const fontFamily = ref(settingsStore.fontFamily)
const lineHeight = ref(settingsStore.lineHeight)
const paragraphSpacing = ref(settingsStore.paragraphSpacing)

// 主题选项
const themeOptions = computed(() => {
  return settingsStore.themeOptions
})

// 字体选项
const fontOptions = [
  { label: '微软雅黑', value: 'Microsoft YaHei' },
  { label: '宋体', value: 'SimSun' },
  { label: '黑体', value: 'SimHei' },
  { label: '楷体', value: 'KaiTi' },
  { label: '仿宋', value: 'FangSong' },
  { label: '思源宋体', value: 'Source Han Serif' },
  { label: '思源黑体', value: 'Source Han Sans' }
]

// 阅读样式
const readingStyle = computed(() => {
  return {
    '--reading-font-size': `${fontSize.value}px`,
    '--reading-font-family': fontFamily.value,
    '--reading-line-height': lineHeight.value,
    '--reading-paragraph-spacing': `${paragraphSpacing.value}em`
  }
})

// 格式化内容
const formattedContent = computed(() => {
  if (!content.value) return ''
  
  // 将内容按段落分割，并用p标签包裹
  const paragraphs = content.value.split('\n').filter(p => p.trim())
  return paragraphs.map(p => `<p>${p}</p>`).join('')
})

// 上一章和下一章ID
const prevChapterId = computed(() => {
  if (!chapter.value || chapters.value.length === 0) return null
  const currentIndex = chapters.value.findIndex(c => c.id === chapter.value.id)
  if (currentIndex > 0) {
    return chapters.value[currentIndex - 1].id
  }
  return null
})

const nextChapterId = computed(() => {
  if (!chapter.value || chapters.value.length === 0) return null
  const currentIndex = chapters.value.findIndex(c => c.id === chapter.value.id)
  if (currentIndex < chapters.value.length - 1) {
    return chapters.value[currentIndex + 1].id
  }
  return null
})

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

// 获取章节内容
const fetchChapterContent = async () => {
  loading.value = true
  content.value = ''
  
  try {
    // 获取章节内容
    const response = await getChapterContent(novelId.value, chapterId.value)
    chapter.value = response.data.chapter
    content.value = response.data.content
    
    // 记录阅读历史
    await addHistory({
      novel_id: novelId.value,
      chapter_id: chapterId.value,
      read_position: readPosition.value
    })
    
    // 更新书架阅读进度
    if (novel.value?.in_bookshelf) {
      await updateBookshelfItem(novelId.value, {
        last_read_chapter_id: chapterId.value,
        last_read_position: readPosition.value
      })
    }
    
    // 滚动到顶部或指定位置
    nextTick(() => {
      if (contentRef.value) {
        if (readPosition.value > 0) {
          contentRef.value.scrollTop = readPosition.value
        } else {
          contentRef.value.scrollTop = 0
        }
      }
    })
  } catch (error) {
    console.error('获取章节内容失败:', error)
    ElMessage.error('获取章节内容失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 过滤章节
const filterChapters = () => {
  if (chapterSearchQuery.value) {
    const query = chapterSearchQuery.value.toLowerCase()
    filteredChapters.value = chapters.value.filter(chapter => 
      chapter.title.toLowerCase().includes(query)
    )
  } else {
    filteredChapters.value = [...chapters.value]
  }
}

// 跳转到指定章节
const goToChapter = (id: number) => {
  // 保存当前阅读位置
  if (contentRef.value) {
    readPosition.value = contentRef.value.scrollTop
  }
  
  router.push(`/novel/${novelId.value}/chapter/${id}`)
  showSidebar.value = false
}

// 返回小说详情页
const goBack = () => {
  router.push(`/novel/${novelId.value}`)
}

// 切换侧边栏
const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value
}

// 切换设置面板
const toggleSettings = () => {
  showSettings.value = !showSettings.value
}

// 处理容器点击
const handleContainerClick = (e) => {
  // 如果点击的是内容区域，则切换工具栏显示状态
  if (e.target.closest('.reading-toolbar') || 
      e.target.closest('.reading-sidebar') || 
      e.target.closest('.el-drawer')) {
    return
  }
  
  showToolbar.value = !showToolbar.value
  
  // 自动隐藏工具栏
  if (showToolbar.value) {
    if (toolbarTimer.value) {
      clearTimeout(toolbarTimer.value)
    }
    
    toolbarTimer.value = setTimeout(() => {
      showToolbar.value = false
    }, 3000)
  }
}

// 更改主题
const changeTheme = (theme: string) => {
  currentTheme.value = theme
  settingsStore.setTheme(theme)
}

// 增加字体大小
const increaseFontSize = () => {
  if (fontSize.value < 28) {
    fontSize.value += 1
    settingsStore.setFontSize(fontSize.value)
  }
}

// 减小字体大小
const decreaseFontSize = () => {
  if (fontSize.value > 12) {
    fontSize.value -= 1
    settingsStore.setFontSize(fontSize.value)
  }
}

// 监听字体和行距变化
watch([fontFamily, lineHeight, paragraphSpacing], ([newFont, newLineHeight, newParagraphSpacing]) => {
  settingsStore.setFontFamily(newFont)
  settingsStore.setLineHeight(newLineHeight)
  settingsStore.setParagraphSpacing(newParagraphSpacing)
})

// 监听路由参数变化
watch(
  () => route.params.chapterId,
  () => {
    fetchChapterContent()
  }
)

// 监听滚动位置
const handleScroll = () => {
  if (contentRef.value) {
    readPosition.value = contentRef.value.scrollTop
  }
}

onMounted(() => {
  // 初始化阅读位置
  if (route.query.position) {
    readPosition.value = parseInt(route.query.position as string) || 0
  }
  
  // 获取数据
  fetchNovelDetail()
  fetchNovelChapters()
  fetchChapterContent()
  
  // 添加滚动监听
  if (contentRef.value) {
    contentRef.value.addEventListener('scroll', handleScroll)
  }
  
  // 显示工具栏，并设置自动隐藏
  showToolbar.value = true
  toolbarTimer.value = setTimeout(() => {
    showToolbar.value = false
  }, 3000)
})

onUnmounted(() => {
  // 移除滚动监听
  if (contentRef.value) {
    contentRef.value.removeEventListener('scroll', handleScroll)
  }
  
  // 清除定时器
  if (toolbarTimer.value) {
    clearTimeout(toolbarTimer.value)
  }
})
</script>

<style lang="scss" scoped>
@import '../../assets/scss/variables.scss';
@import '../../assets/scss/mixins.scss';

.reading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--app-reading-bg-color);
  z-index: 100;
  overflow: hidden;
  transition: padding-left 0.3s;
  
  &.sidebar-open {
    padding-left: 300px;
  }
}

.reading-toolbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background-color: var(--app-bg-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  z-index: 10;
  transform: translateY(-100%);
  transition: transform 0.3s ease;
  
  &.show {
    transform: translateY(0);
  }
  
  .toolbar-left,
  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .el-button {
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
      }
    }
  }
  
  .novel-title {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    
    @include mobile {
      max-width: 200px;
      font-size: 16px;
    }
  }
}

.reading-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20px;
  overflow-y: auto;
  
  @include custom-scrollbar;
  
  .loading-container {
    max-width: 800px;
    margin: 60px auto 0;
    padding: 20px;
  }
  
  .chapter-header {
    max-width: 800px;
    margin: 60px auto 30px;
    text-align: center;
    
    h1 {
      font-size: 24px;
      font-weight: 600;
      margin: 0;
    }
  }
  
  .chapter-content {
    max-width: 800px;
    margin: 0 auto;
    font-size: var(--reading-font-size, 16px);
    font-family: var(--reading-font-family, 'Microsoft YaHei');
    line-height: var(--reading-line-height, 1.8);
    color: var(--app-reading-text-color);
    
    :deep(p) {
      margin-bottom: var(--reading-paragraph-spacing, 1.2em);
      text-indent: 2em;
      transition: margin 0.3s ease;
    }
  }
  
  .chapter-footer {
    max-width: 800px;
    margin: 40px auto;
    display: flex;
    justify-content: space-between;
    padding: 20px 0;
    border-top: 1px solid var(--el-border-color-light);
  }
  
  @include mobile {
    padding: 15px;
  }
}

.reading-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 300px;
  height: 100vh;
  background-color: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  transform: translateX(-100%);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  z-index: 20;
  display: flex;
  flex-direction: column;
  box-shadow: 5px 0 15px rgba(0, 0, 0, 0.1);
  
  @include mobile {
    width: 280px;
  }
  
  &.show {
    transform: translateX(0);
  }
  
  .sidebar-header {
    padding: 16px;
    border-bottom: 1px solid var(--el-border-color-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }
    
    .el-button {
      transition: all 0.3s ease;
      
      &:hover {
        transform: rotate(90deg);
      }
    }
  }
  
  .sidebar-search {
    padding: 15px;
    border-bottom: 1px solid var(--el-border-color-light);
    
    .el-input {
      .el-input__wrapper {
        box-shadow: 0 0 0 1px var(--el-border-color) inset;
        transition: all 0.3s ease;
        
        &:hover {
          box-shadow: 0 0 0 1px var(--el-color-primary-light-3) inset;
        }
        
        &.is-focus {
          box-shadow: 0 0 0 1px var(--el-color-primary) inset;
        }
      }
    }
  }
  
  .sidebar-content {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
    @include custom-scrollbar;
  }
  
  .chapter-list {
    list-style: none;
    padding: 0;
    margin: 0;
    
    .chapter-item {
      padding: 12px 15px;
      border-radius: 4px;
      cursor: pointer;
      margin-bottom: 5px;
      transition: all 0.2s ease;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      
      &:hover {
        background-color: var(--el-fill-color-light);
        transform: translateX(5px);
      }
      
      &.active {
        background-color: var(--el-color-primary-light-9);
        color: var(--el-color-primary);
        font-weight: 500;
      }
    }
  }
}

.settings-panel {
  padding: 20px;
  
  h3 {
    margin: 0 0 15px;
    font-size: 16px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    
    .el-icon {
      color: var(--el-color-primary);
    }
  }
  
  .theme-options {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 20px;
    
    .theme-option {
      cursor: pointer;
      transition: all 0.3s ease;
      position: relative;
      
      &.active .theme-preview {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        
        &::after {
          content: '';
          position: absolute;
          top: -5px;
          right: -5px;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background-color: var(--el-color-success);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 12px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
      }
      
      .theme-preview {
        width: 80px;
        height: 50px;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: all 0.3s;
        gap: 5px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        
        &:hover {
          transform: translateY(-3px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .el-icon {
          font-size: 18px;
        }
        
        span {
          font-size: 12px;
          font-weight: 500;
        }
        
        &.theme-light {
          background-color: map-get($light-theme, reading-bg-color);
          color: map-get($light-theme, reading-text-color);
        }
        
        &.theme-dark {
          background-color: map-get($dark-theme, reading-bg-color);
          color: map-get($dark-theme, reading-text-color);
        }
        
        &.theme-eye-protection {
          background-color: map-get($eye-protection-theme, reading-bg-color);
          color: map-get($eye-protection-theme, reading-text-color);
        }
        
        &.theme-light-yellow {
          background-color: map-get($light-yellow-theme, reading-bg-color);
          color: map-get($light-yellow-theme, reading-text-color);
        }
        
        &.theme-pink {
          background-color: map-get($pink-theme, reading-bg-color);
          color: map-get($pink-theme, reading-text-color);
        }
      }
    }
  }
  
  .font-size-control {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 10px;
  
  .font-size-value {
    min-width: 60px;
    text-align: center;
    font-weight: 600;
    color: var(--el-color-primary);
    background-color: var(--el-color-primary-light-9);
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 14px;
  }
  
  .el-button {
    transition: all 0.3s ease;
    
    &:hover:not(.is-disabled) {
      transform: scale(1.1);
    }
    
    &.is-disabled {
      opacity: 0.5;
    }
  }
}
  
  .el-divider {
    margin: 25px 0;
  }
}

// 主题样式已移至全局SCSS文件
</style>