<template>
  <div class="about-container">
    <div class="about-card">
      <div class="logo-container">
        <img src="@/assets/logo.svg" alt="LocalNovel Logo" class="logo" />
        <h1>LocalNovel</h1>
        <div class="version">v{{ version }}</div>
      </div>

      <el-divider>
        <el-icon><InfoFilled /></el-icon>
      </el-divider>

      <div class="description">
        <p>LocalNovel 是一款功能强大的本地小说阅读软件，专为小说爱好者设计。它提供了丰富的功能，让您可以轻松搜索、阅读和管理您喜爱的小说。</p>
      </div>

      <el-divider>
        <el-icon><Collection /></el-icon>
        主要功能
      </el-divider>

      <div class="features">
        <div class="feature-item">
          <el-icon><Search /></el-icon>
          <div class="feature-content">
            <h3>小说搜索</h3>
            <p>强大的搜索功能，支持多来源搜索小说，快速找到您想要的内容。</p>
          </div>
        </div>

        <div class="feature-item">
          <el-icon><Reading /></el-icon>
          <div class="feature-content">
            <h3>舒适阅读</h3>
            <p>提供多种阅读主题、字体大小和行距设置，打造个性化的阅读体验。</p>
          </div>
        </div>

        <div class="feature-item">
          <el-icon><Collection /></el-icon>
          <div class="feature-content">
            <h3>书架管理</h3>
            <p>便捷的书架功能，轻松管理您收藏的小说，随时继续阅读。</p>
          </div>
        </div>

        <div class="feature-item">
          <el-icon><Timer /></el-icon>
          <div class="feature-content">
            <h3>阅读历史</h3>
            <p>自动记录阅读历史，方便您随时回顾和继续阅读。</p>
          </div>
        </div>

        <div class="feature-item">
          <el-icon><Setting /></el-icon>
          <div class="feature-content">
            <h3>规则管理</h3>
            <p>自定义网站解析规则，支持添加新的小说来源。</p>
          </div>
        </div>

        <div class="feature-item">
          <el-icon><Download /></el-icon>
          <div class="feature-content">
            <h3>本地缓存</h3>
            <p>支持小说内容本地缓存，离线也能阅读。</p>
          </div>
        </div>
      </div>

      <el-divider>
        <el-icon><Monitor /></el-icon>
        技术栈
      </el-divider>

      <div class="tech-stack">
        <div class="tech-section">
          <h3>前端</h3>
          <ul>
            <li>Vue 3 - 渐进式 JavaScript 框架</li>
            <li>Element Plus - 基于 Vue 3 的组件库</li>
            <li>TypeScript - 类型安全的 JavaScript 超集</li>
            <li>Electron - 跨平台桌面应用开发框架</li>
            <li>PNPM - 高效的包管理器</li>
          </ul>
        </div>

        <div class="tech-section">
          <h3>后端</h3>
          <ul>
            <li>FastAPI - 高性能 Python Web 框架</li>
            <li>Uvicorn - ASGI 服务器</li>
            <li>SQLite - 轻量级数据库</li>
            <li>Scrapy - 网络爬虫框架</li>
            <li>缓存系统 - aioredis 和 cachetools</li>
          </ul>
        </div>
      </div>

      <el-divider>
        <el-icon><User /></el-icon>
        关于作者
      </el-divider>

      <div class="author">
        <p>LocalNovel 是一个开源项目，由热爱阅读和编程的开发者创建。</p>
        <p>欢迎提出建议和反馈，帮助我们不断改进这款软件。</p>
      </div>

      <div class="copyright">
        <p>© {{ new Date().getFullYear() }} LocalNovel. All Rights Reserved.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { InfoFilled, Collection, Search, Reading, Timer, Setting, Download, Monitor, User } from '@element-plus/icons-vue'

// 版本号
const version = ref('1.0.0')
</script>

<style scoped lang="scss">
.about-container {
  padding: 20px;
  display: flex;
  justify-content: center;
}

.about-card {
  max-width: 800px;
  width: 100%;
  background-color: var(--el-bg-color);
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
  padding: 30px;
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;

  .logo {
    width: 100px;
    height: 100px;
    margin-bottom: 10px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    margin: 0;
  }

  .version {
    color: var(--el-text-color-secondary);
    margin-top: 5px;
  }
}

.description {
  text-align: center;
  margin-bottom: 20px;
  font-size: 16px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;

  .feature-item {
    display: flex;
    align-items: flex-start;
    padding: 15px;
    border-radius: 8px;
    background-color: var(--el-fill-color-light);
    transition: transform 0.3s, box-shadow 0.3s;

    &:hover {
      transform: translateY(-5px);
      box-shadow: var(--el-box-shadow);
    }

    .el-icon {
      font-size: 24px;
      color: var(--el-color-primary);
      margin-right: 15px;
      margin-top: 3px;
    }

    .feature-content {
      flex: 1;

      h3 {
        margin: 0 0 8px;
        font-size: 18px;
        font-weight: 600;
      }

      p {
        margin: 0;
        color: var(--el-text-color-secondary);
        font-size: 14px;
        line-height: 1.5;
      }
    }
  }
}

.tech-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 30px;

  .tech-section {
    h3 {
      font-size: 18px;
      font-weight: 600;
      margin-top: 0;
      margin-bottom: 15px;
      color: var(--el-color-primary);
    }

    ul {
      padding-left: 20px;
      margin: 0;

      li {
        margin-bottom: 8px;
        color: var(--el-text-color-regular);
      }
    }
  }
}

.author {
  text-align: center;
  margin-bottom: 30px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.copyright {
  text-align: center;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.el-divider {
  margin: 30px 0;

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
</style>