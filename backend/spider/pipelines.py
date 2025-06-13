from typing import Dict, Any, Optional, List, Union
from scrapy import Spider
from loguru import logger

# 获取爬虫日志记录器
spider_logger = logger.bind(name="spider")


class NovelPipeline:
    """小说数据处理管道"""

    def process_item(self, item: Dict[str, Any], spider: Spider) -> Dict[str, Any]:
        """处理爬取到的项目"""
        # 根据不同的爬虫和任务类型处理数据
        if hasattr(spider, 'task_id') and hasattr(spider, 'callback'):
            # 记录处理的项目
            item_type = item.get('type', 'unknown')
            spider_logger.debug(f"处理项目: {item_type}, 爬虫: {spider.name}")

            # 清理数据
            self._clean_item(item)

            # 调用回调函数
            if spider.callback and callable(spider.callback):
                spider.callback(spider.task_id, item)

        return item

    def _clean_item(self, item: Dict[str, Any]) -> None:
        """清理项目数据"""
        # 移除空字符串和None值
        for key, value in list(item.items()):
            if isinstance(value, str):
                # 清理字符串
                item[key] = value.strip()
                # 如果清理后为空，则设为None
                if not item[key]:
                    item[key] = None

        # 处理特定字段
        if 'content' in item and item['content']:
            # 清理章节内容
            content = item['content']
            # 移除多余空行
            content = '\n'.join(line for line in content.split('\n') if line.strip())
            # 规范化段落
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            item['content'] = content
