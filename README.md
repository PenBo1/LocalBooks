# LocalBooks

## 本地小说阅读应用

一个基于Electron和Vue3的本地小说阅读应用，支持多种主题和阅读设置。

### 主题系统

应用支持多种主题：

- 浅色主题（默认）
- 深色主题
- 护眼主题
- 浅黄主题
- 粉色主题

主题系统使用CSS变量实现，可以轻松扩展和自定义。主题变量定义在`src/renderer/src/assets/scss/variables.scss`文件中，包括：

- 背景颜色
- 文本颜色
- 边框颜色
- 填充颜色
- 主题色（主色、成功色、警告色、危险色、信息色）
- 阅读相关颜色

### 阅读设置

应用提供丰富的阅读设置选项：

- 主题选择
- 字体大小调整
- 字体选择
- 行高调整
- 段落间距调整

[English](#english) | [中文](#中文)

<a name="english"></a>
## LocalBooks - A Local Novel Reading Application

### Introduction
LocalBooks is a cross-platform desktop application for novel reading, which allows users to browse, search, download, and read novels locally. It features a clean and customizable reading interface, bookshelf management, reading history tracking, and supports multiple novel sources through customizable rules.

### Technology Stack

#### Frontend
- Vue 3: Progressive JavaScript framework
- Element Plus: Vue 3 based component library
- TypeScript: JavaScript with syntax for types
- PNPM: Fast, disk space efficient package manager
- Electron: Framework for building cross-platform desktop applications

#### Backend
- FastAPI: Modern, fast web framework for building APIs with Python
- Uvicorn: ASGI server for Python
- SQLite: Lightweight disk-based database
- Redis (optional): In-memory data structure store for caching
- Scrapy: Framework for extracting data from websites

### Features

#### Home Page
- Display hot novels and recently updated novels
- Quick access to bookshelf and history
- Search functionality for finding novels across multiple sources

#### Bookshelf
- Add novels to personal bookshelf
- Track reading progress for each novel
- Sort and filter bookshelf items
- Remove novels from bookshelf

#### History
- Automatically record reading history
- Display recently read chapters
- Quick access to continue reading
- Clear history options

#### Management
- Manage novel sources and rules
- Add, edit, and delete custom rules for different websites
- Test rules for compatibility

#### Settings
- Customize reading interface (font, size, theme, etc.)
- Configure application behavior
- Manage cache and storage

#### Reading Interface
- Clean, distraction-free reading experience
- Chapter navigation
- Font and theme customization
- Reading progress tracking
- Auto-scroll option

### Installation

#### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- PNPM

#### Setup
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/LocalBooks.git
   cd LocalBooks
   ```

2. Install frontend dependencies
   ```bash
   cd src
   pnpm install
   ```

3. Install backend dependencies
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. Start the development server
   ```bash
   # In the src directory
   pnpm dev
   
   # In the backend directory (in another terminal)
   python main.py
   ```

### Building for Production
```bash
# In the src directory
pnpm build
```

### License
MIT

---

<a name="中文"></a>
## LocalBooks - 本地小说阅读应用

### 简介
LocalBooks是一个跨平台的桌面小说阅读应用，允许用户浏览、搜索、下载和本地阅读小说。它具有简洁可定制的阅读界面、书架管理、阅读历史跟踪功能，并通过可自定义规则支持多个小说源。

### 技术栈

#### 前端
- Vue 3：渐进式JavaScript框架
- Element Plus：基于Vue 3的组件库
- TypeScript：带有类型语法的JavaScript
- PNPM：快速、节省磁盘空间的包管理器
- Electron：构建跨平台桌面应用程序的框架

#### 后端
- FastAPI：用于构建API的现代、快速的Python Web框架
- Uvicorn：Python的ASGI服务器
- SQLite：轻量级基于磁盘的数据库
- Redis（可选）：用于缓存的内存数据结构存储
- Scrapy：用于从网站提取数据的框架

### 功能特点

#### 首页
- 显示热门小说和最近更新的小说
- 快速访问书架和历史记录
- 搜索功能，可在多个来源中查找小说

#### 书架
- 将小说添加到个人书架
- 跟踪每本小说的阅读进度
- 对书架项目进行排序和筛选
- 从书架中移除小说

#### 历史记录
- 自动记录阅读历史
- 显示最近阅读的章节
- 快速访问继续阅读
- 清除历史记录选项

#### 管理
- 管理小说源和规则
- 添加、编辑和删除不同网站的自定义规则
- 测试规则的兼容性

#### 设置
- 自定义阅读界面（字体、大小、主题等）
- 配置应用程序行为
- 管理缓存和存储

#### 阅读界面
- 干净、无干扰的阅读体验
- 章节导航
- 字体和主题自定义
- 阅读进度跟踪
- 自动滚动选项

### 安装

#### 前提条件
- Node.js (v14+)
- Python (v3.8+)
- PNPM

#### 设置
1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/LocalBooks.git
   cd LocalBooks
   ```

2. 安装前端依赖
   ```bash
   cd src
   pnpm install
   ```

3. 安装后端依赖
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. 启动开发服务器
   ```bash
   # 在src目录中
   pnpm dev
   
   # 在backend目录中（在另一个终端）
   python main.py
   ```

### 构建生产版本
```bash
# 在src目录中
pnpm build
```

### 许可证
MIT
