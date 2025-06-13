<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h2>应用设置</h2>
          <div class="header-actions">
            <el-button type="primary" @click="saveSettings">
              <el-icon><Check /></el-icon>
              保存设置
            </el-button>
            <el-button @click="resetSettings">
              <el-icon><RefreshRight /></el-icon>
              重置默认
            </el-button>
          </div>
        </div>
      </template>

      <el-form label-position="top" :model="form" class="settings-form">
        <!-- 主题设置 -->
        <el-divider content-position="left">
          <el-icon><Brush /></el-icon>
          主题设置
        </el-divider>

        <el-form-item label="主题">
          <el-radio-group v-model="form.theme" class="theme-options">
            <el-radio-button
              v-for="option in themeOptions"
              :key="option.value"
              :label="option.value"
              class="theme-option"
            >
              <div class="theme-preview" :class="`theme-${option.value}`">
                <span>{{ option.label }}</span>
              </div>
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 阅读设置 -->
        <el-divider content-position="left">
          <el-icon><Reading /></el-icon>
          阅读设置
        </el-divider>

        <div class="form-row">
          <el-form-item label="字体大小">
            <div class="slider-with-value">
              <el-slider
                v-model="form.fontSize"
                :min="12"
                :max="28"
                :step="1"
                show-stops
              />
              <div class="slider-value">{{ form.fontSize }}px</div>
            </div>
          </el-form-item>

          <el-form-item label="字体">
            <el-select v-model="form.fontFamily" placeholder="选择字体">
              <el-option
                v-for="font in fontOptions"
                :key="font.value"
                :label="font.label"
                :value="font.value"
                :style="{ fontFamily: font.value }"
              />
            </el-select>
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item label="行距">
            <div class="slider-with-value">
              <el-slider
                v-model="form.lineHeight"
                :min="1"
                :max="3"
                :step="0.1"
                show-stops
              />
              <div class="slider-value">{{ form.lineHeight }}</div>
            </div>
          </el-form-item>

          <el-form-item label="段落间距">
            <div class="slider-with-value">
              <el-slider
                v-model="form.paragraphSpacing"
                :min="0.5"
                :max="3"
                :step="0.1"
                show-stops
              />
              <div class="slider-value">{{ form.paragraphSpacing }}em</div>
            </div>
          </el-form-item>
        </div>

        <!-- 缓存设置 -->
        <el-divider content-position="left">
          <el-icon><Files /></el-icon>
          缓存设置
        </el-divider>

        <div class="form-row">
          <el-form-item label="启用缓存">
            <el-switch v-model="form.enableCache" />
          </el-form-item>

          <el-form-item label="缓存过期时间(天)">
            <el-input-number
              v-model="form.cacheExpiration"
              :min="1"
              :max="30"
              :disabled="!form.enableCache"
            />
          </el-form-item>
        </div>

        <el-form-item label="缓存大小限制(MB)">
          <div class="slider-with-value">
            <el-slider
              v-model="form.cacheSize"
              :min="100"
              :max="1000"
              :step="100"
              show-stops
              :disabled="!form.enableCache"
            />
            <div class="slider-value">{{ form.cacheSize }}MB</div>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="warning" @click="clearCache" :disabled="!form.enableCache">
            <el-icon><Delete /></el-icon>
            清除缓存
          </el-button>
          <span class="cache-info" v-if="cacheInfo">当前缓存大小: {{ cacheInfo }}</span>
        </el-form-item>

        <!-- 日志设置 -->
        <el-divider content-position="left">
          <el-icon><Document /></el-icon>
          日志设置
        </el-divider>

        <el-form-item label="日志等级">
          <el-select v-model="form.logLevel" placeholder="选择日志等级">
            <el-option
              v-for="level in logLevelOptions"
              :key="level.value"
              :label="level.label"
              :value="level.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="日志保留天数">
          <el-input-number v-model="form.logRetention" :min="1" :max="30" />
        </el-form-item>

        <el-form-item>
          <el-button @click="openLogFolder">
            <el-icon><Folder /></el-icon>
            打开日志文件夹
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, RefreshRight, Brush, Reading, Files, Delete, Document, Folder } from '@element-plus/icons-vue'
import { getSettings, updateSetting, resetToDefault } from '@/api/settings'
import { useSettingsStore } from '@/store/settings'

const settingsStore = useSettingsStore()

// 表单数据
const form = reactive({
  theme: 'light',
  fontSize: 16,
  fontFamily: 'Microsoft YaHei',
  lineHeight: 1.5,
  paragraphSpacing: 1.2,
  enableCache: true,
  cacheExpiration: 7,
  cacheSize: 500,
  logLevel: 'info',
  logRetention: 7
})

// 缓存信息
const cacheInfo = ref('')

// 主题选项
const themeOptions = [
  { label: '浅色', value: 'light' },
  { label: '深色', value: 'dark' },
  { label: '护眼', value: 'eye-protection' },
  { label: '浅黄', value: 'light-yellow' },
  { label: '粉色', value: 'pink' }
]

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

// 日志等级选项
const logLevelOptions = [
  { label: '调试', value: 'debug' },
  { label: '信息', value: 'info' },
  { label: '警告', value: 'warning' },
  { label: '错误', value: 'error' },
  { label: '严重错误', value: 'critical' }
]

// 加载设置
const loadSettings = async () => {
  try {
    const response = await getSettings()
    const settings = response.data

    // 将设置应用到表单
    Object.keys(form).forEach(key => {
      if (key in settings) {
        form[key] = settings[key]
      }
    })

    // 获取缓存信息
    if (settings.cache_info) {
      cacheInfo.value = settings.cache_info
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败，请稍后重试')
  }
}

// 保存设置
const saveSettings = async () => {
  try {
    // 保存每个设置项
    for (const [key, value] of Object.entries(form)) {
      await updateSetting(key, value)
    }

    // 更新全局设置状态
    settingsStore.setSettings(form)

    ElMessage.success('设置保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败，请稍后重试')
  }
}

// 重置设置
const resetSettings = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要将所有设置重置为默认值吗？此操作不可恢复！',
      '重置确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await resetToDefault()
    await loadSettings()
    
    // 更新全局设置状态
    settingsStore.loadSettings()
    
    ElMessage.success('设置已重置为默认值')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重置设置失败:', error)
      ElMessage.error('重置设置失败，请稍后重试')
    }
  }
}

// 清除缓存
const clearCache = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有缓存吗？这将删除所有已缓存的小说内容。',
      '清除缓存',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await updateSetting('clear_cache', true)
    cacheInfo.value = '0 KB'
    ElMessage.success('缓存已清除')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清除缓存失败:', error)
      ElMessage.error('清除缓存失败，请稍后重试')
    }
  }
}

// 打开日志文件夹
const openLogFolder = () => {
  // 使用Electron的shell.openPath打开日志文件夹
  window.electron?.ipcRenderer.send('open-log-folder')
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped lang="scss">
.settings-container {
  padding: 20px;
}

.settings-card {
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
  }

  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.settings-form {
  .el-divider {
    margin: 30px 0 20px;

    :deep(.el-divider__text) {
      display: flex;
      align-items: center;
      font-size: 16px;
      font-weight: 600;

      .el-icon {
        margin-right: 8px;
      }
    }
  }

  .form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
  }

  .slider-with-value {
    display: flex;
    align-items: center;

    .el-slider {
      flex: 1;
      margin-right: 15px;
    }

    .slider-value {
      width: 60px;
      text-align: center;
      color: var(--el-text-color-secondary);
    }
  }

  .theme-options {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;

    .theme-option {
      :deep(.el-radio-button__inner) {
        padding: 0;
        border: none;
        height: auto;
        background: none;
      }

      .theme-preview {
        width: 120px;
        height: 80px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        transition: transform 0.2s;
        border: 2px solid transparent;

        &:hover {
          transform: scale(1.05);
        }
      }

      &.is-active .theme-preview {
        border-color: var(--el-color-primary);
      }

      .theme-light {
        background-color: #ffffff;
        color: #303133;
      }

      .theme-dark {
        background-color: #303133;
        color: #e6e6e6;
      }

      .theme-eye-protection {
        background-color: #c9e6cd;
        color: #333333;
      }

      .theme-light-yellow {
        background-color: #fdf6e3;
        color: #586e75;
      }

      .theme-pink {
        background-color: #fce4ec;
        color: #880e4f;
      }
    }
  }

  .cache-info {
    margin-left: 10px;
    color: var(--el-text-color-secondary);
  }
}
</style>