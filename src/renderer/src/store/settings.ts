import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getSettings, updateSetting } from '@/api/settings'

export const useSettingsStore = defineStore('settings', () => {
  // 主题设置
  const theme = ref('light') // 默认浅色主题
  const themeOptions = [
    { label: '护眼', value: 'eye-protection' },
    { label: '深色', value: 'dark' },
    { label: '浅色', value: 'light' },
    { label: '浅黄色', value: 'light-yellow' },
    { label: '粉色', value: 'pink' }
  ]

  // 字体设置
  const fontSize = ref(16) // 默认16px
  const fontFamily = ref('Microsoft YaHei, sans-serif') // 默认微软雅黑
  const lineHeight = ref(1.5) // 默认1.5倍行距

  // 缓存设置
  const cacheEnabled = ref(true) // 默认启用缓存
  const cacheExpiration = ref(86400) // 默认24小时

  // 日志设置
  const logLevel = ref('INFO') // 默认INFO级别
  const logLevelOptions = [
    { label: '调试', value: 'DEBUG' },
    { label: '信息', value: 'INFO' },
    { label: '警告', value: 'WARNING' },
    { label: '错误', value: 'ERROR' },
    { label: '严重', value: 'CRITICAL' }
  ]

  // 加载设置
  const loadSettings = async () => {
    try {
      const settings = await getSettings()
      if (settings) {
        theme.value = settings.theme || 'light'
        fontSize.value = parseInt(settings.font_size) || 16
        fontFamily.value = settings.font_family || 'Microsoft YaHei, sans-serif'
        lineHeight.value = parseFloat(settings.line_height) || 1.5
        cacheEnabled.value = settings.cache_enabled === 'true'
        cacheExpiration.value = parseInt(settings.cache_expiration) || 86400
        logLevel.value = settings.log_level || 'INFO'
      }
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  }

  // 更新主题
  const setTheme = async (newTheme: string) => {
    theme.value = newTheme
    await updateSetting('theme', newTheme)
    applyTheme(newTheme)
  }

  // 应用主题
  const applyTheme = (themeName: string) => {
    document.body.className = ''
    document.body.classList.add(`theme-${themeName}`)
  }

  // 更新字体大小
  const setFontSize = async (size: number) => {
    fontSize.value = size
    await updateSetting('font_size', size.toString())
  }

  // 更新字体
  const setFontFamily = async (font: string) => {
    fontFamily.value = font
    await updateSetting('font_family', font)
  }

  // 更新行距
  const setLineHeight = async (height: number) => {
    lineHeight.value = height
    await updateSetting('line_height', height.toString())
  }

  // 更新缓存设置
  const setCacheEnabled = async (enabled: boolean) => {
    cacheEnabled.value = enabled
    await updateSetting('cache_enabled', enabled.toString())
  }

  // 更新缓存过期时间
  const setCacheExpiration = async (time: number) => {
    cacheExpiration.value = time
    await updateSetting('cache_expiration', time.toString())
  }

  // 更新日志级别
  const setLogLevel = async (level: string) => {
    logLevel.value = level
    await updateSetting('log_level', level)
  }

  return {
    theme,
    themeOptions,
    fontSize,
    fontFamily,
    lineHeight,
    cacheEnabled,
    cacheExpiration,
    logLevel,
    logLevelOptions,
    loadSettings,
    setTheme,
    applyTheme,
    setFontSize,
    setFontFamily,
    setLineHeight,
    setCacheEnabled,
    setCacheExpiration,
    setLogLevel
  }
})