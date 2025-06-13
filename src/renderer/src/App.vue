<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { useSettingsStore } from './store/settings'

const settingsStore = useSettingsStore()

onMounted(() => {
  // 加载应用设置
  settingsStore.loadSettings()
  settingsStore.applyTheme()
})
</script>

<style>
/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: var(--el-font-family);
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--el-border-color-darker);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--el-text-color-secondary);
}

/* 主题变量 */
:root {
  --app-sidebar-width: 220px;
  --app-sidebar-collapsed-width: 64px;
  --app-header-height: 60px;
  --app-transition-duration: 0.3s;
}

/* 主题样式 */
.theme-light {
  --el-bg-color: #ffffff;
  --el-text-color-primary: #303133;
}

.theme-dark {
  --el-bg-color: #303133;
  --el-text-color-primary: #e6e6e6;
  --el-border-color-light: #4c4d4f;
}

.theme-eye-protection {
  --el-bg-color: #f0f9eb;
  --el-text-color-primary: #333333;
}

.theme-light-yellow {
  --el-bg-color: #fdf6e3;
  --el-text-color-primary: #586e75;
}

.theme-pink {
  --el-bg-color: #fce4ec;
  --el-text-color-primary: #880e4f;
}
</style>
