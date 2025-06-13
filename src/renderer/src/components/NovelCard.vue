<template>
  <div class="novel-card" @click="$emit('click')">
    <div class="novel-cover">
      <el-image
        :src="novel.cover || defaultCover"
        fit="cover"
        :lazy="true"
        loading="lazy"
        :alt="novel.title"
      >
        <template #error>
          <div class="image-error">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>
      <div v-if="showBookshelfBadge" class="bookshelf-badge">
        <el-icon><Collection /></el-icon>
      </div>
    </div>
    <div class="novel-info">
      <h3 class="novel-title" :title="novel.title">{{ novel.title }}</h3>
      <p v-if="novel.author" class="novel-author" :title="novel.author">
        <el-icon><User /></el-icon>
        {{ novel.author }}
      </p>
      <p v-if="showLastRead && novel.last_read_chapter" class="novel-last-read" :title="novel.last_read_chapter.title">
        <el-icon><Reading /></el-icon>
        {{ novel.last_read_chapter.title }}
      </p>
      <p v-if="showReadTime && novel.read_at" class="novel-read-time">
        <el-icon><Timer /></el-icon>
        {{ formatTime(novel.read_at) }}
      </p>
    </div>
    <div class="novel-actions">
      <slot name="actions">
        <el-button v-if="showAddToBookshelf" circle size="small" @click.stop="$emit('add-to-bookshelf')">
          <el-icon><Plus /></el-icon>
        </el-button>
        <el-button v-if="showRemoveFromBookshelf" circle size="small" type="danger" @click.stop="$emit('remove-from-bookshelf')">
          <el-icon><Delete /></el-icon>
        </el-button>
        <el-button v-if="showDeleteHistory" circle size="small" type="danger" @click.stop="$emit('delete-history')">
          <el-icon><Delete /></el-icon>
        </el-button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Picture, Collection, User, Reading, Timer, Plus, Delete } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const defaultCover = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgMzAwIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2YyZjJmMiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMzYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIGZpbGw9IiM5OTkiPuaXoOWbvueJhzwvdGV4dD48L3N2Zz4='

interface Novel {
  id: number
  title: string
  cover?: string
  author?: string
  description?: string
  source_url?: string
  in_bookshelf?: boolean
  last_read_chapter?: {
    id: number
    title: string
  }
  read_at?: string
}

interface Props {
  novel: Novel
  showBookshelfBadge?: boolean
  showLastRead?: boolean
  showReadTime?: boolean
  showAddToBookshelf?: boolean
  showRemoveFromBookshelf?: boolean
  showDeleteHistory?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showBookshelfBadge: false,
  showLastRead: false,
  showReadTime: false,
  showAddToBookshelf: false,
  showRemoveFromBookshelf: false,
  showDeleteHistory: false
})

const emit = defineEmits<{
  (e: 'click'): void
  (e: 'add-to-bookshelf'): void
  (e: 'remove-from-bookshelf'): void
  (e: 'delete-history'): void
}>()

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).fromNow()
}
</script>

<style scoped lang="scss">
.novel-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background-color: var(--el-bg-color);
  box-shadow: var(--el-box-shadow-light);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;

  &:hover {
    transform: translateY(-5px);
    box-shadow: var(--el-box-shadow);

    .novel-actions {
      opacity: 1;
    }
  }
}

.novel-cover {
  position: relative;
  width: 100%;
  padding-top: 140%;
  overflow: hidden;

  .el-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .image-error {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    background-color: var(--el-fill-color-light);
    color: var(--el-text-color-secondary);
    font-size: 24px;
  }

  .bookshelf-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: var(--el-color-primary);
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 12px;
  }
}

.novel-info {
  padding: 12px;
  flex: 1;

  .novel-title {
    margin: 0 0 8px;
    font-size: 16px;
    font-weight: 600;
    line-height: 1.2;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .novel-author,
  .novel-last-read,
  .novel-read-time {
    display: flex;
    align-items: center;
    margin: 4px 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;

    .el-icon {
      margin-right: 4px;
      font-size: 14px;
    }
  }
}

.novel-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 1;
}
</style>