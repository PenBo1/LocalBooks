# LocalBooks 后端文档

## 目录

- [项目概述](#项目概述)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [运行逻辑](#运行逻辑)
- [API接口文档](#api接口文档)
- [数据库设计](#数据库设计)
- [前后端接口一致性问题](#前后端接口一致性问题)
- [启动指南](#启动指南)

## 项目概述

LocalBooks后端为本地小说阅读应用提供API服务，负责小说数据的爬取、存储、检索和管理。后端使用FastAPI框架构建，提供RESTful API接口，支持小说搜索、书架管理、历史记录、规则配置和系统设置等功能。

## 技术栈

- **FastAPI**: 现代、高性能的Python Web框架
- **Uvicorn**: ASGI服务器
- **SQLite**: 轻量级关系型数据库
- **aiosqlite**: SQLite的异步接口
- **Scrapy**: 强大的网页爬虫框架
- **aioredis** (可选): Redis的异步客户端，用于缓存
- **cachetools**: 内存缓存工具
- **httpx**: 异步HTTP客户端
- **loguru**: 日志管理工具

## 项目结构

```
backend/
├── api/                  # API路由模块
│   ├── bookshelf.py      # 书架相关接口
│   ├── history.py        # 历史记录相关接口
│   ├── novel.py          # 小说相关接口
│   ├── rule.py           # 规则相关接口
│   └── settings.py       # 设置相关接口
├── database/             # 数据库模块
│   ├── crud.py           # 数据库CRUD操作
│   ├── init_db.py        # 数据库初始化
│   └── models.py         # 数据模型定义
├── logs/                 # 日志文件目录
├── spider/               # 爬虫模块
│   ├── middlewares.py    # 爬虫中间件
│   ├── pipelines.py      # 爬虫管道
│   ├── spider_manager.py # 爬虫管理器
│   └── spiders/          # 爬虫实现
│       ├── chapter_spider.py  # 章节内容爬虫
│       └── novel_spider.py    # 小说信息爬虫
├── utils/                # 工具模块
│   ├── cache.py          # 缓存工具
│   └── logger.py         # 日志工具
├── .env                  # 环境变量配置
├── main.py               # 应用入口
└── requirements.txt      # 依赖列表
```

## 运行逻辑

### 应用启动流程

1. 加载环境变量配置
2. 初始化日志系统
3. 创建FastAPI应用实例
4. 注册API路由
5. 初始化数据库
6. 启动Uvicorn服务器

### 请求处理流程

1. 客户端发送HTTP请求
2. Uvicorn接收请求并传递给FastAPI
3. FastAPI根据路由规则分发请求到对应的处理函数
4. 处理函数执行业务逻辑（数据库操作、爬虫调用等）
5. 返回处理结果给客户端

### 爬虫工作流程

1. 接收爬取任务（搜索小说、获取章节等）
2. 根据规则构建请求
3. 发送HTTP请求获取网页内容
4. 使用规则解析网页内容
5. 将解析结果存储到数据库或返回给API

### 缓存机制

1. 使用装饰器`@cached`标记需要缓存的函数
2. 缓存优先从Redis获取（如果配置了Redis）
3. 如果Redis未配置或未命中，则使用内存缓存
4. 缓存项设置TTL（生存时间）

## API接口文档

### 小说相关接口

#### 搜索小说

```
GET /api/novel/search?keyword={keyword}&rule_id={rule_id}
```

- **描述**: 根据关键词搜索小说
- **参数**:
  - `keyword`: 搜索关键词
  - `rule_id`: 规则ID
- **返回**: 小说搜索结果列表

#### 获取热门小说

```
GET /api/novel/hot?limit={limit}
```

- **描述**: 获取热门小说列表
- **参数**:
  - `limit`: 返回数量，默认10
- **返回**: 热门小说列表

#### 添加小说

```
POST /api/novel/add
```

- **描述**: 添加小说到数据库
- **请求体**: 小说信息对象
- **返回**: 新增小说ID

#### 获取小说详情

```
GET /api/novel/detail/{novel_id}
```

- **描述**: 获取小说详细信息
- **参数**:
  - `novel_id`: 小说ID
- **返回**: 小说详情对象

#### 从网络获取小说详情

```
GET /api/novel/fetch_detail?url={url}&rule_id={rule_id}
```

- **描述**: 从网络获取小说详情
- **参数**:
  - `url`: 小说详情页URL
  - `rule_id`: 规则ID
- **返回**: 小说详情对象

#### 获取小说章节列表

```
GET /api/novel/chapters/{novel_id}
```

- **描述**: 获取小说章节列表
- **参数**:
  - `novel_id`: 小说ID
- **返回**: 章节列表

#### 获取章节内容

```
GET /api/novel/chapter/{chapter_id}
```

- **描述**: 获取章节内容
- **参数**:
  - `chapter_id`: 章节ID
- **返回**: 章节内容对象

### 书架相关接口

#### 获取书架列表

```
GET /api/bookshelf/list?page={page}&page_size={page_size}&sort_by={sort_by}
```

- **描述**: 获取书架列表
- **参数**:
  - `page`: 页码，默认1
  - `page_size`: 每页数量，默认10
  - `sort_by`: 排序字段，默认updated_at
- **返回**: 分页的书架列表

#### 添加到书架

```
POST /api/bookshelf/add
```

- **描述**: 添加小说到书架
- **请求体**: 书架项信息
- **返回**: 新增书架项ID

#### 更新书架项

```
PUT /api/bookshelf/update/{bookshelf_id}
```

- **描述**: 更新书架项信息
- **参数**:
  - `bookshelf_id`: 书架项ID
- **请求体**: 更新信息
- **返回**: 成功消息

#### 从书架移除

```
DELETE /api/bookshelf/remove/{novel_id}
```

- **描述**: 从书架移除小说
- **参数**:
  - `novel_id`: 小说ID
- **返回**: 成功消息

### 历史记录相关接口

#### 获取历史记录列表

```
GET /api/history?page={page}&page_size={page_size}&sort_by={sort_by}
```

- **描述**: 获取历史记录列表
- **参数**:
  - `page`: 页码，默认1
  - `page_size`: 每页数量，默认10
  - `sort_by`: 排序字段，默认read_at
- **返回**: 分页的历史记录列表

#### 添加历史记录

```
POST /api/history
```

- **描述**: 添加历史记录
- **请求体**: 历史记录信息
- **返回**: 新增历史记录ID

#### 删除历史记录

```
DELETE /api/history/{history_id}
```

- **描述**: 删除历史记录
- **参数**:
  - `history_id`: 历史记录ID
- **返回**: 成功消息

#### 删除小说的所有历史记录

```
DELETE /api/history/novel/{novel_id}
```

- **描述**: 删除小说的所有历史记录
- **参数**:
  - `novel_id`: 小说ID
- **返回**: 成功消息

#### 清空所有历史记录

```
DELETE /api/history/all/clear
```

- **描述**: 清空所有历史记录
- **返回**: 成功消息

### 规则相关接口

#### 获取规则列表

```
GET /api/rule?page={page}&page_size={page_size}&sort_by={sort_by}
```

- **描述**: 获取规则列表
- **参数**:
  - `page`: 页码，默认1
  - `page_size`: 每页数量，默认10
  - `sort_by`: 排序字段，默认updated_at
- **返回**: 分页的规则列表

#### 获取规则详情

```
GET /api/rule/{rule_id}
```

- **描述**: 获取规则详情
- **参数**:
  - `rule_id`: 规则ID
- **返回**: 规则详情对象

#### 创建规则

```
POST /api/rule
```

- **描述**: 创建规则
- **请求体**: 规则信息
- **返回**: 新增规则ID

#### 更新规则

```
PUT /api/rule/{rule_id}
```

- **描述**: 更新规则
- **参数**:
  - `rule_id`: 规则ID
- **请求体**: 更新信息
- **返回**: 成功消息

#### 删除规则

```
DELETE /api/rule/{rule_id}
```

- **描述**: 删除规则
- **参数**:
  - `rule_id`: 规则ID
- **返回**: 成功消息

### 设置相关接口

#### 获取所有设置

```
GET /api/settings
```

- **描述**: 获取所有设置
- **返回**: 设置键值对

#### 获取单个设置

```
GET /api/settings/{key}
```

- **描述**: 获取单个设置
- **参数**:
  - `key`: 设置键名
- **返回**: 设置值

#### 更新设置

```
PUT /api/settings/{key}
```

- **描述**: 更新设置
- **参数**:
  - `key`: 设置键名
- **请求体**: 设置值
- **返回**: 成功消息

#### 重置为默认设置

```
GET /api/settings/default/reset
```

- **描述**: 重置为默认设置
- **返回**: 成功消息

## 数据库设计

### 小说表 (novels)

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| id | INTEGER | 主键 |
| title | TEXT | 小说标题 |
| author | TEXT | 作者 |
| cover | TEXT | 封面URL |
| description | TEXT | 小说描述 |
| source | TEXT | 来源网站 |
| source_url | TEXT | 来源URL |
| rule_id | INTEGER | 规则ID |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 章节表 (chapters)

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| id | INTEGER | 主键 |
| novel_id | INTEGER | 小说ID |
| title | TEXT | 章节标题 |
| chapter_index | INTEGER | 章节索引 |
| source_url | TEXT | 来源URL |
| content | TEXT | 章节内容 |
| is_downloaded | BOOLEAN | 是否已下载 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 书架表 (bookshelf)

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| id | INTEGER | 主键 |
| novel_id | INTEGER | 小说ID |
| last_read_chapter_id | INTEGER | 最后阅读章节ID |
| last_read_position | INTEGER | 最后阅读位置 |
| added_at | TIMESTAMP | 添加时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 历史记录表 (history)

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| id | INTEGER | 主键 |
| novel_id | INTEGER | 小说ID |
| chapter_id | INTEGER | 章节ID |
| read_position | INTEGER | 阅读位置 |
| read_at | TIMESTAMP | 阅读时间 |

### 规则表 (rules)

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| id | INTEGER | 主键 |
| name | TEXT | 规则名称 |
| source_url | TEXT | 来源网站URL |
| search_url | TEXT | 搜索URL模板 |
| cover_rule | TEXT | 封面解析规则 |
| title_rule | TEXT | 标题解析规则 |
| author_rule | TEXT | 作者解析规则 |
| description_rule | TEXT | 描述解析规则 |
| chapter_list_rule | TEXT | 章节列表解析规则 |
| chapter_content_rule | TEXT | 章节内容解析规则 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 设置表 (settings)

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| key | TEXT | 设置键名 |
| value | TEXT | 设置值 |
| updated_at | TIMESTAMP | 更新时间 |

## 前后端接口一致性问题

在分析前后端代码的过程中，发现了一些接口不一致的问题，现已解决：

### 已解决的问题

1. **请求方法统一**：
   - 所有后端接口已统一使用GET和POST请求方法
   - 原PUT请求已改为POST请求，路径增加了`/update/`前缀
   - 原DELETE请求已改为POST请求，路径增加了`/delete/`或`/remove/`前缀

2. **书架接口**：
   - 前端请求路径已更新为：`/bookshelf` (GET)、`/bookshelf` (POST)、`/bookshelf/update/{id}` (POST)、`/bookshelf/remove/{novel_id}` (POST)
   - 后端接口路径为：`/bookshelf/list` (GET)、`/bookshelf/add` (POST)、`/bookshelf/update/{bookshelf_id}` (POST)、`/bookshelf/remove/{novel_id}` (POST)

3. **小说详情接口**：
   - 前端请求路径：`/novel/{id}` (GET)
   - 后端接口路径已更新为：`/novel/{novel_id}` (GET)

4. **章节内容接口**：
   - 前端请求路径：`/novel/{novelId}/chapter/{chapterId}` (GET)
   - 后端接口路径已更新为：`/novel/{novel_id}/chapter/{chapter_id}` (GET)

5. **网络获取接口**：
   - 已添加从网络获取小说详情、章节列表和章节内容的后端接口实现
   - 路径分别为：`/novel/{novel_id}/detail/network` (GET)、`/novel/{novel_id}/chapters/network` (GET)、`/novel/{novel_id}/chapter/{chapter_id}/network` (GET)

### 接口修改总结

1. **规则接口**：
   - PUT `/rule/{rule_id}` → POST `/rule/update/{rule_id}`
   - DELETE `/rule/{rule_id}` → POST `/rule/delete/{rule_id}`

2. **历史记录接口**：
   - DELETE `/history/{history_id}` → POST `/history/delete/{history_id}`
   - DELETE `/history/novel/{novel_id}` → POST `/history/delete/novel/{novel_id}`
   - DELETE `/history/all/clear` → POST `/history/all/clear`

3. **设置接口**：
   - PUT `/settings/{key}` → POST `/settings/update/{key}`

4. **书架接口**：
   - PUT `/bookshelf/update/{bookshelf_id}` → POST `/bookshelf/update/{bookshelf_id}`
   - DELETE `/bookshelf/remove/{novel_id}` → POST `/bookshelf/remove/{novel_id}`

5. **小说接口**：
   - GET `/novel/detail/{novel_id}` → GET `/novel/{novel_id}`
   - GET `/novel/chapters/{novel_id}` → GET `/novel/{novel_id}/chapters`
   - GET `/novel/chapter/{chapter_id}` → GET `/novel/{novel_id}/chapter/{chapter_id}`
   - 新增 GET `/novel/{novel_id}/detail/network`
   - 新增 GET `/novel/{novel_id}/chapters/network`
   - 新增 GET `/novel/{novel_id}/chapter/{chapter_id}/network`

## 启动指南

### 环境准备

1. 安装Python 3.8+
2. 安装依赖包
   ```bash
   pip install -r requirements.txt
   ```

### 配置

1. 创建`.env`文件，配置环境变量
   ```
   HOST=127.0.0.1
   PORT=8000
   ENV=development
   LOG_LEVEL=INFO
   REDIS_URL=redis://localhost:6379/0  # 可选，不配置则使用内存缓存
   ```

### 启动服务

```bash
python main.py
```

服务将在`http://127.0.0.1:8000`启动，API文档可访问`http://127.0.0.1:8000/docs`。