<template>
  <div class="settings-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Setting /></el-icon>
        应用设置
      </h1>
      <div class="header-actions">
        <el-button type="primary" @click="saveSettings" :loading="saveLoading">
          <el-icon><Check /></el-icon>
          保存设置
        </el-button>
        <el-button @click="resetSettings" :loading="resetLoading">
          <el-icon><RefreshLeft /></el-icon>
          重置默认
        </el-button>
      </div>
    </div>

    <!-- 设置内容 -->
    <div class="settings-content">
      <!-- 主题设置 -->
      <el-card class="setting-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><Brush /></el-icon>
            <span class="card-title">主题设置</span>
          </div>
        </template>
        <div class="theme-section">
          <div class="theme-grid">
            <div 
              v-for="theme in themeOptions" 
              :key="theme.value"
              class="theme-option"
              :class="{ active: form.theme === theme.value }"
              @click="form.theme = theme.value"
            >
              <div class="theme-preview" :style="{ backgroundColor: theme.color }">
                <div class="theme-preview-content">
                  <div class="preview-text">Aa</div>
                  <div class="preview-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
              <div class="theme-name">{{ theme.label }}</div>
              <el-icon v-if="form.theme === theme.value" class="theme-check"><Check /></el-icon>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 阅读设置 -->
      <el-card class="setting-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><Reading /></el-icon>
            <span class="card-title">阅读设置</span>
          </div>
        </template>
        <div class="reading-settings">
          <div class="setting-row">
            <div class="setting-item">
              <label class="setting-label">字体大小</label>
              <div class="slider-container">
                <el-slider 
                  v-model="form.font_size" 
                  :min="12" 
                  :max="24" 
                  :step="1"
                  show-input
                  input-size="small"
                  class="custom-slider"
                />
                <span class="unit">px</span>
              </div>
            </div>
            <div class="setting-item">
              <label class="setting-label">字体</label>
              <el-select v-model="form.font_family" placeholder="选择字体" class="font-select">
                <el-option 
                  v-for="font in fontOptions" 
                  :key="font.value" 
                  :label="font.label" 
                  :value="font.value"
                />
              </el-select>
            </div>
          </div>
          <div class="setting-row">
            <div class="setting-item">
              <label class="setting-label">行距</label>
              <div class="slider-container">
                <el-slider 
                  v-model="form.line_height" 
                  :min="1.0" 
                  :max="3.0" 
                  :step="0.1"
                  show-input
                  input-size="small"
                  class="custom-slider"
                />
              </div>
            </div>
            <div class="setting-item">
              <label class="setting-label">段落间距</label>
              <div class="slider-container">
                <el-slider 
                  v-model="form.paragraph_spacing" 
                  :min="0" 
                  :max="20" 
                  :step="1"
                  show-input
                  input-size="small"
                  class="custom-slider"
                />
                <span class="unit">px</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 缓存设置 -->
      <el-card class="setting-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><FolderOpened /></el-icon>
            <span class="card-title">缓存设置</span>
          </div>
        </template>
        <div class="cache-settings">
          <div class="setting-row">
            <div class="setting-item full-width">
              <div class="switch-item">
                <label class="setting-label">启用缓存</label>
                <el-switch v-model="form.cache_enabled" />
              </div>
            </div>
          </div>
          <div class="setting-row" v-if="form.cache_enabled">
            <div class="setting-item">
              <label class="setting-label">缓存过期时间</label>
              <div class="slider-container">
                <el-slider 
                  v-model="form.cache_expiration" 
                  :min="3600" 
                  :max="604800" 
                  :step="3600"
                  show-input
                  input-size="small"
                  class="custom-slider"
                />
                <span class="unit">秒</span>
              </div>
            </div>
            <div class="setting-item">
              <label class="setting-label">缓存大小限制</label>
              <div class="slider-container">
                <el-slider 
                  v-model="form.cache_size_limit" 
                  :min="100" 
                  :max="2000" 
                  :step="100"
                  show-input
                  input-size="small"
                  class="custom-slider"
                />
                <span class="unit">MB</span>
              </div>
            </div>
          </div>
          <div class="setting-row" v-if="form.cache_enabled">
            <div class="cache-actions">
              <el-button type="warning" @click="clearCache" :loading="clearCacheLoading">
                <el-icon><Delete /></el-icon>
                清除缓存
              </el-button>
              <div class="cache-info">
                <div class="cache-stat">
                  <span class="stat-label">缓存大小:</span>
                  <span class="stat-value">{{ cacheInfo.size }}</span>
                </div>
                <div class="cache-stat">
                  <span class="stat-label">缓存文件数:</span>
                  <span class="stat-value">{{ cacheInfo.count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 日志设置 -->
      <el-card class="setting-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><Document /></el-icon>
            <span class="card-title">日志设置</span>
          </div>
        </template>
        <div class="log-settings">
          <div class="setting-row">
            <div class="setting-item">
              <label class="setting-label">日志等级</label>
              <el-select v-model="form.log_level" placeholder="选择日志等级" class="log-select">
                <el-option 
                  v-for="level in logLevelOptions" 
                  :key="level.value" 
                  :label="level.label" 
                  :value="level.value"
                />
              </el-select>
            </div>
            <div class="setting-item">
              <label class="setting-label">日志保留天数</label>
              <div class="slider-container">
                <el-slider 
                  v-model="form.log_retention_days" 
                  :min="1" 
                  :max="30" 
                  :step="1"
                  show-input
                  input-size="small"
                  class="custom-slider"
                />
                <span class="unit">天</span>
              </div>
            </div>
          </div>
          <div class="setting-row">
            <div class="log-actions">
              <el-button type="info" @click="openLogFolder">
                <el-icon><FolderOpened /></el-icon>
                打开日志文件夹
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Setting, 
  Check, 
  RefreshLeft, 
  Brush, 
  Reading, 
  FolderOpened, 
  Document, 
  Delete 
} from '@element-plus/icons-vue'
import { getSettings, updateSetting, resetToDefault } from '@/api/settings'
import { useSettingsStore } from '@/store/settings'

const settingsStore = useSettingsStore()

// 响应式数据
const saveLoading = ref(false)
const resetLoading = ref(false)
const clearCacheLoading = ref(false)

const form = reactive({
  theme: 'light',
  font_size: 16,
  font_family: 'Microsoft YaHei, sans-serif',
  line_height: 1.5,
  paragraph_spacing: 10,
  cache_enabled: true,
  cache_expiration: 86400,
  cache_size_limit: 500,
  log_level: 'INFO',
  log_retention_days: 7
})

const cacheInfo = reactive({
  size: '0 MB',
  count: 0
})

// 选项数据
const themeOptions = [
  { label: '浅色', value: 'light', color: '#ffffff' },
  { label: '深色', value: 'dark', color: '#1a1a1a' },
  { label: '护眼', value: 'green', color: '#c7edcc' },
  { label: '浅黄', value: 'yellow', color: '#fef7cd' },
  { label: '粉色', value: 'pink', color: '#fce4ec' }
]

const fontOptions = [
  { label: '微软雅黑', value: 'Microsoft YaHei, sans-serif' },
  { label: '宋体', value: 'SimSun, serif' },
  { label: '黑体', value: 'SimHei, sans-serif' },
  { label: '楷体', value: 'KaiTi, serif' },
  { label: '仿宋', value: 'FangSong, serif' }
]

const logLevelOptions = [
  { label: 'DEBUG', value: 'DEBUG' },
  { label: 'INFO', value: 'INFO' },
  { label: 'WARNING', value: 'WARNING' },
  { label: 'ERROR', value: 'ERROR' }
]

// 加载设置
const loadSettings = async () => {
  try {
    const response = await getSettings()
    const settings = response.data
    
    // 更新表单数据
    Object.keys(form).forEach(key => {
      if (settings[key] !== undefined) {
        if (key === 'cache_enabled') {
          form[key] = settings[key] === 'true' || settings[key] === true
        } else if (['font_size', 'line_height', 'paragraph_spacing', 'cache_expiration', 'cache_size_limit', 'log_retention_days'].includes(key)) {
          form[key] = Number(settings[key])
        } else {
          form[key] = settings[key]
        }
      }
    })
    
    // 应用主题到store
    settingsStore.setTheme(form.theme)
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败')
  }
}

// 保存设置
const saveSettings = async () => {
  saveLoading.value = true
  try {
    // 遍历表单项，逐个更新
    for (const [key, value] of Object.entries(form)) {
      await updateSetting(key, value)
    }
    
    // 更新全局状态
    settingsStore.setTheme(form.theme)
    settingsStore.setFontSize(form.font_size)
    settingsStore.setFontFamily(form.font_family)
    settingsStore.setLineHeight(form.line_height)
    
    ElMessage.success('设置保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  } finally {
    saveLoading.value = false
  }
}

// 重置设置
const resetSettings = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置为默认设置吗？这将覆盖所有当前设置。',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    resetLoading.value = true
    await resetToDefault()
    await loadSettings()
    ElMessage.success('已重置为默认设置')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重置设置失败:', error)
      ElMessage.error('重置设置失败')
    }
  } finally {
    resetLoading.value = false
  }
}

// 清除缓存
const clearCache = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有缓存吗？',
      '确认清除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    clearCacheLoading.value = true
    await updateSetting('clear_cache', true)
    
    // 更新缓存信息
    cacheInfo.size = '0 MB'
    cacheInfo.count = 0
    
    ElMessage.success('缓存清除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清除缓存失败:', error)
      ElMessage.error('清除缓存失败')
    }
  } finally {
    clearCacheLoading.value = false
  }
}

// 打开日志文件夹
const openLogFolder = () => {
  if (window.electronAPI) {
    window.electronAPI.openLogFolder()
  } else {
    ElMessage.warning('此功能仅在桌面应用中可用')
  }
}

// 组件挂载时加载设置
onMounted(() => {
  loadSettings()
})
</script>

<style lang="scss" scoped>
.settings-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-card {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
  
  .card-icon {
    font-size: 18px;
    color: #409eff;
  }
  
  .card-title {
    font-size: 16px;
  }
}

/* 主题设置样式 */
.theme-section {
  padding: 20px 0;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
}

.theme-option {
  position: relative;
  cursor: pointer;
  border-radius: 12px;
  padding: 16px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  background: #fafafa;
  
  &:hover {
    border-color: #409eff;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  }
  
  &.active {
    border-color: #409eff;
    background: #ecf5ff;
  }
  
  .theme-preview {
    width: 100%;
    height: 80px;
    border-radius: 8px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    
    .theme-preview-content {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      
      .preview-text {
        font-size: 18px;
        font-weight: bold;
        color: #333;
        margin-bottom: 8px;
      }
      
      .preview-dots {
        display: flex;
        gap: 4px;
        justify-content: center;
        
        span {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #666;
          opacity: 0.6;
        }
      }
    }
  }
  
  .theme-name {
    text-align: center;
    font-size: 14px;
    font-weight: 500;
    color: #606266;
  }
  
  .theme-check {
    position: absolute;
    top: 8px;
    right: 8px;
    color: #409eff;
    font-size: 16px;
    background: white;
    border-radius: 50%;
    padding: 2px;
  }
}

/* 设置行样式 */
.reading-settings,
.cache-settings,
.log-settings {
  padding: 20px 0;
}

.setting-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  
  &.full-width {
    grid-column: 1 / -1;
  }
  
  .setting-label {
    font-size: 14px;
    font-weight: 500;
    color: #606266;
    margin-bottom: 8px;
  }
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .custom-slider {
    flex: 1;
  }
  
  .unit {
    font-size: 12px;
    color: #909399;
    min-width: 24px;
  }
}

.switch-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.font-select,
.log-select {
  width: 100%;
}

/* 缓存和日志操作样式 */
.cache-actions,
.log-actions {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.cache-info {
  display: flex;
  gap: 20px;
  margin-left: auto;
  
  .cache-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    
    .stat-label {
      font-size: 12px;
      color: #909399;
    }
    
    .stat-value {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
    }
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .setting-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .theme-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
  }
  
  .cache-actions,
  .log-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .cache-info {
    margin-left: 0;
    justify-content: center;
  }
}
</style>