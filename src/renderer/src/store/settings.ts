import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getSettings, updateSetting } from '@/api/settings'

export const useSettingsStore = defineStore('settings', () => {
  // 主题设置
  const theme = ref('light') // 默认浅色主题
  const themeOptions = [
    { label: '护眼', value: 'eye-protection', icon: 'View' },
    { label: '深色', value: 'dark', icon: 'Moon' },
    { label: '浅色', value: 'light', icon: 'Sunny' },
    { label: '浅黄色', value: 'light-yellow', icon: 'Orange' },
    { label: '粉色', value: 'pink', icon: 'Cherry' }
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
  
  // 作者信息
  const authorInfo = ref({
    name: 'LocalBooks开发团队',
    email: 'support@localbooks.com',
    website: 'https://github.com/localbooks/localbooks',
    description: 'LocalBooks是一个开源的本地小说阅读应用'
  })
  
  // 版本信息
  const version = ref('1.0.0')
  
  // 快捷键设置
  const hotkeys = ref({
    toggleSidebar: 'Ctrl+B',
    search: 'Ctrl+F',
    nextChapter: 'ArrowRight',
    prevChapter: 'ArrowLeft',
    toggleTheme: 'Ctrl+T',
    increaseFontSize: 'Ctrl+Plus',
    decreaseFontSize: 'Ctrl+Minus'
  })

  // 从localStorage加载设置
  const loadFromLocalStorage = () => {
    try {
      const localTheme = localStorage.getItem('theme')
      const localFontSize = localStorage.getItem('font_size')
      const localFontFamily = localStorage.getItem('font_family')
      const localLineHeight = localStorage.getItem('line_height')
      const localCacheEnabled = localStorage.getItem('cache_enabled')
      const localCacheExpiration = localStorage.getItem('cache_expiration')
      const localLogLevel = localStorage.getItem('log_level')
      const localAuthorInfo = localStorage.getItem('author_info')
      const localVersion = localStorage.getItem('version')
      const localHotkeys = localStorage.getItem('hotkeys')
      
      if (localTheme) theme.value = localTheme
      if (localFontSize) fontSize.value = parseInt(localFontSize)
      if (localFontFamily) fontFamily.value = localFontFamily
      if (localLineHeight) lineHeight.value = parseFloat(localLineHeight)
      if (localCacheEnabled) cacheEnabled.value = localCacheEnabled === 'true'
      if (localCacheExpiration) cacheExpiration.value = parseInt(localCacheExpiration)
      if (localLogLevel) logLevel.value = localLogLevel
      if (localAuthorInfo) authorInfo.value = JSON.parse(localAuthorInfo)
      if (localVersion) version.value = localVersion
      if (localHotkeys) hotkeys.value = JSON.parse(localHotkeys)
      
      // 应用主题
      applyTheme(theme.value)
      
      return true
    } catch (error) {
      console.error('从localStorage加载设置失败:', error)
      return false
    }
  }
  
  // 加载设置
  const loadSettings = async () => {
    // 从localStorage加载
    loadFromLocalStorage()
    
    // 如果本地没有设置，使用默认值
    if (!localStorage.getItem('theme')) {
      // 设置默认值
      theme.value = 'light'
      fontSize.value = 16
      fontFamily.value = 'Microsoft YaHei, sans-serif'
      lineHeight.value = 1.5
      cacheEnabled.value = true
      cacheExpiration.value = 86400
      logLevel.value = 'INFO'
      
      // 保存到localStorage
      localStorage.setItem('theme', theme.value)
      localStorage.setItem('font_size', fontSize.value.toString())
      localStorage.setItem('font_family', fontFamily.value)
      localStorage.setItem('line_height', lineHeight.value.toString())
      localStorage.setItem('cache_enabled', cacheEnabled.value.toString())
      localStorage.setItem('cache_expiration', cacheExpiration.value.toString())
      localStorage.setItem('log_level', logLevel.value)
    }
    
    // 如果本地没有作者信息，保存默认值
    if (!localStorage.getItem('author_info')) {
      localStorage.setItem('author_info', JSON.stringify(authorInfo.value))
    }
    
    // 如果本地没有版本信息，保存默认值
    if (!localStorage.getItem('version')) {
      localStorage.setItem('version', version.value)
    }
    
    // 如果本地没有快捷键设置，保存默认值
    if (!localStorage.getItem('hotkeys')) {
      localStorage.setItem('hotkeys', JSON.stringify(hotkeys.value))
    }
    
    // 应用主题
    applyTheme(theme.value)
  }

  // 更新主题
  const setTheme = async (newTheme: string) => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    // 移除对后端API的调用
    applyTheme(newTheme)
  }

  // 应用主题
  const applyTheme = (themeName: string = theme.value) => {
    console.log('应用主题:', themeName)
    
    // 移除所有主题类名
    document.body.classList.remove(
      'theme-light',
      'theme-dark',
      'theme-eye-protection',
      'theme-light-yellow',
      'theme-pink'
    )
    // 添加新主题类名
    document.body.classList.add(`theme-${themeName}`)
    
    // 更新meta主题颜色
    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      // 根据主题设置不同的颜色
      let themeColor = '#ffffff' // 默认浅色
      
      switch (themeName) {
        case 'dark':
          themeColor = '#1a1a1a'
          break
        case 'eye-protection':
          themeColor = '#c7edcc'
          break
        case 'light-yellow':
          themeColor = '#fdf6e3'
          break
        case 'pink':
          themeColor = '#fff0f5'
          break
      }
      
      metaThemeColor.setAttribute('content', themeColor)
    }
    
    // 设置CSS变量
    document.documentElement.style.setProperty('--reading-font-size', `${fontSize.value}px`)
    document.documentElement.style.setProperty('--reading-font-family', fontFamily.value)
    document.documentElement.style.setProperty('--reading-line-height', lineHeight.value.toString())
    
    // 强制刷新主题
    document.body.style.display = 'none'
    setTimeout(() => {
      document.body.style.display = ''
    }, 10)
    
    // 强制应用主题相关的CSS变量
    setTimeout(() => {
      // 确保DOM已更新
      document.documentElement.style.setProperty('--theme-applied', 'true')
    }, 0)
  }

  // 更新字体大小
  const setFontSize = async (size: number) => {
    fontSize.value = size
    localStorage.setItem('font_size', size.toString())
    // 移除对后端API的调用
  }

  // 更新字体
  const setFontFamily = async (font: string) => {
    fontFamily.value = font
    localStorage.setItem('font_family', font)
    // 移除对后端API的调用
  }

  // 更新行距
  const setLineHeight = async (height: number) => {
    lineHeight.value = height
    localStorage.setItem('line_height', height.toString())
    // 移除对后端API的调用
  }

  // 更新缓存启用状态
  const setCacheEnabled = async (enabled: boolean) => {
    cacheEnabled.value = enabled
    localStorage.setItem('cache_enabled', enabled.toString())
    // 移除对后端API的调用
  }

  // 更新缓存过期时间
  const setCacheExpiration = async (time: number) => {
    cacheExpiration.value = time
    localStorage.setItem('cache_expiration', time.toString())
    // 移除对后端API的调用
  }

  // 更新日志级别
  const setLogLevel = async (level: string) => {
    logLevel.value = level
    localStorage.setItem('log_level', level)
    // 移除对后端API的调用
  }
  
  // 更新作者信息
  const setAuthorInfo = (info: any) => {
    authorInfo.value = info
    localStorage.setItem('author_info', JSON.stringify(info))
  }
  
  // 获取作者信息
  const getAuthorInfo = () => {
    return authorInfo.value
  }
  
  // 更新版本号
  const setVersion = (ver: string) => {
    version.value = ver
    localStorage.setItem('version', ver)
  }
  
  // 获取版本号
  const getVersion = () => {
    return version.value
  }
  
  // 更新快捷键设置
  const setHotkeys = (keys: any) => {
    hotkeys.value = keys
    localStorage.setItem('hotkeys', JSON.stringify(keys))
  }
  
  // 更新单个快捷键
  const setHotkey = (key: string, value: string) => {
    hotkeys.value[key] = value
    localStorage.setItem('hotkeys', JSON.stringify(hotkeys.value))
  }
  
  // 获取快捷键设置
  const getHotkeys = () => {
    return hotkeys.value
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
    authorInfo,
    version,
    hotkeys,
    loadSettings,
    setTheme,
    applyTheme,
    setFontSize,
    setFontFamily,
    setLineHeight,
    setCacheEnabled,
    setCacheExpiration,
    setLogLevel,
    setAuthorInfo,
    getAuthorInfo,
    setVersion,
    getVersion,
    setHotkeys,
    setHotkey,
    getHotkeys
  }
})