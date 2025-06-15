<template>
  <div class="title-bar" @mousedown="handleDrag">
    <div class="title-bar-left">
      <img src="@/assets/LocalBooks.png" alt="LocalBooks" class="title-bar-icon" />
      <span class="title-bar-title">LocalBooks - 本地小说阅读应用</span>
    </div>
    <div class="title-bar-right">
      <div class="title-bar-button" @click="minimize">
        <el-icon><Minus /></el-icon>
      </div>
      <div class="title-bar-button" @click="maximize">
        <el-icon v-if="isMaximized"><CopyDocument /></el-icon>
        <el-icon v-else><FullScreen /></el-icon>
      </div>
      <div class="title-bar-button close-button" @click="close">
        <el-icon><Close /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Minus, FullScreen, CopyDocument, Close } from '@element-plus/icons-vue'

// 窗口是否最大化
const isMaximized = ref(false)

// 窗口控制函数
const minimize = () => {
  window.api.window.minimize()
}

const maximize = () => {
  window.api.window.maximize()
  checkMaximizeStatus()
}

const close = () => {
  window.api.window.close()
}

// 检查窗口是否最大化
const checkMaximizeStatus = async () => {
  isMaximized.value = await window.api.window.isMaximized()
}

// 处理拖动
const handleDrag = (event: MouseEvent) => {
  // 如果点击的是按钮，不进行拖动
  if ((event.target as HTMLElement).closest('.title-bar-button')) {
    return
  }
  // 触发自定义事件，通知主进程开始拖动窗口
  window.api.window.startDrag()
}

// 定期检查窗口最大化状态
let checkInterval: number | null = null

onMounted(() => {
  checkMaximizeStatus()
  // 每秒检查一次窗口状态
  checkInterval = window.setInterval(checkMaximizeStatus, 1000) as unknown as number
})

onBeforeUnmount(() => {
  if (checkInterval !== null) {
    window.clearInterval(checkInterval)
  }
})
</script>

<style scoped lang="scss">
.title-bar {
  height: 32px;
  background-color: var(--el-bg-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  -webkit-app-region: drag; /* 使整个标题栏可拖动 */
  user-select: none;
  border-bottom: 1px solid var(--el-border-color-light);
}

.title-bar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-bar-icon {
  width: 16px;
  height: 16px;
}

.title-bar-title {
  font-size: 12px;
  color: var(--el-text-color-primary);
}

.title-bar-right {
  display: flex;
  -webkit-app-region: no-drag; /* 按钮区域不可拖动 */
}

.title-bar-button {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  
  &:hover {
    background-color: var(--el-fill-color-light);
  }
  
  .el-icon {
    font-size: 14px;
    color: var(--el-text-color-regular);
  }
}

.close-button {
  &:hover {
    background-color: #f56c6c;
    
    .el-icon {
      color: white;
    }
  }
}
</style>