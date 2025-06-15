<template>
  <div class="app-container">
    <!-- 自定义标题栏 -->
    <TitleBar />
    
    <!-- 主内容区域的布局容器 -->
    <div class="content-container">
      <!-- 左侧导航栏 -->
      <div class="sidebar">
        <div class="logo">
          <h1>LocalBooks</h1>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          :router="true"
          :collapse="isCollapse"
        >
          <el-menu-item v-for="route in routes" :key="route.path" :index="route.path">
            <el-icon>
              <component :is="route.meta?.icon" />
            </el-icon>
            <template #title>{{ route.meta?.title }}</template>
          </el-menu-item>
        </el-menu>
        <div class="sidebar-footer">
          <el-tooltip content="折叠/展开" placement="right">
            <el-button
              class="collapse-btn"
              :icon="isCollapse ? 'Expand' : 'Fold'"
              circle
              @click="toggleCollapse"
            />
          </el-tooltip>
        </div>
      </div>

      <!-- 右侧内容区域 -->
      <div class="main-container">
        <!-- 顶部导航栏 -->
        <div class="navbar">
          <div class="navbar-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentRoute?.meta?.title }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="navbar-right">
            <el-dropdown>
              <span class="el-dropdown-link">
                主题
                <el-icon class="el-icon--right">
                  <arrow-down />
                </el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="option in themeOptions"
                    :key="option.value"
                    @click="changeTheme(option.value)"
                  >
                    {{ option.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <!-- 内容区域 -->
        <div class="app-main">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <keep-alive :include="cachedViews">
                <component :is="Component" />
              </keep-alive>
            </transition>
          </router-view>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'
import { useSettingsStore } from '@/store/settings'
import TitleBar from '@/components/TitleBar.vue'

const route = useRoute()
const router = useRouter()
const settingsStore = useSettingsStore()

// 侧边栏折叠状态
const isCollapse = ref(false)

// 缓存的视图
const cachedViews = ref(['Home', 'Bookshelf', 'History', 'Rule', 'About', 'Settings'])

// 获取路由
const routes = computed(() => {
  const mainRoutes = router.options.routes[0].children || []
  return mainRoutes.filter(route => route.meta && route.meta.title)
})

// 当前激活的菜单
const activeMenu = computed(() => {
  return route.path
})

// 当前路由
const currentRoute = computed(() => {
  return route
})

// 主题选项
const themeOptions = computed(() => {
  return settingsStore.themeOptions
})

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 切换主题
const changeTheme = (theme: string) => {
  settingsStore.setTheme(theme)
}

onMounted(() => {
  // 加载设置
  settingsStore.loadSettings()
})
</script>

<style scoped lang="scss">
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* 主内容区域的布局容器 */
.content-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  display: flex;
  flex-direction: column;
  width: v-bind('isCollapse ? "64px" : "200px"');
  height: 100%;
  background-color: var(--el-menu-bg-color);
  transition: width 0.3s;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 10;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 10px;
    overflow: hidden;

    h1 {
      color: var(--el-menu-text-color);
      font-size: 18px;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .sidebar-menu {
    flex: 1;
    border-right: none;
  }

  .sidebar-footer {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-top: 1px solid var(--el-border-color-light);
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.navbar {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid var(--el-border-color-light);
  background-color: var(--el-bg-color);

  .navbar-left {
    display: flex;
    align-items: center;
  }

  .navbar-right {
    display: flex;
    align-items: center;
  }
}

.app-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: var(--el-bg-color-page);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>