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

onMounted(async () => {
  // 加载应用设置
  await settingsStore.loadSettings()
  settingsStore.applyTheme()
  
  // 设置初始主题类
  const initialTheme = settingsStore.theme
  document.body.classList.add(`theme-${initialTheme}`)
})
</script>

<style lang="scss">
@import './assets/scss/main.scss';

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
</style>
