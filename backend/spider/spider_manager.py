import os
import asyncio
import json
from typing import List, Dict, Any, Optional, Callable
from loguru import logger
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from threading import Thread

from .spiders.novel_spider import NovelSpider
from .spiders.chapter_spider import ChapterSpider
from database.models import SearchResult, Novel, Chapter
from utils.cache import cached

# 获取爬虫日志记录器
spider_logger = logger.bind(name="spider")


def _run_reactor():
    """在单独的线程中运行Twisted反应器"""
    if not reactor.running:
        Thread(target=reactor.run, args=(False,), daemon=True).start()


def _stop_reactor():
    """停止Twisted反应器"""
    if reactor.running:
        reactor.stop()


def _to_future(deferred):
    """将Deferred转换为Future"""
    future = asyncio.Future()

    def callback(result):
        if not future.done():
            future.set_result(result)

    def errback(failure):
        if not future.done():
            future.set_exception(failure.value)

    deferred.addCallbacks(callback, errback)
    return future


class SpiderManager:
    """爬虫管理器"""

    def __init__(self):
        """初始化爬虫管理器"""
        self.settings = get_project_settings()
        self.runner = CrawlerRunner(self.settings)
        self.results = {}
        self.callbacks = {}
        _run_reactor()

    async def search_novel(self, keyword: str, rule_id: int) -> List[SearchResult]:
        """搜索小说"""
        spider_logger.info(f"搜索小说: {keyword}, 规则ID: {rule_id}")

        # 生成唯一任务ID
        task_id = f"search_{keyword}_{rule_id}_{id(self)}"

        # 创建结果Future
        future = asyncio.Future()
        self.callbacks[task_id] = future

        # 启动爬虫
        d = self.runner.crawl(
            NovelSpider,
            keyword=keyword,
            rule_id=rule_id,
            task_id=task_id,
            callback=self._spider_callback
        )

        # 等待爬虫完成
        await _to_future(d)

        # 等待结果
        try:
            result = await asyncio.wait_for(future, timeout=60)
            return result
        except asyncio.TimeoutError:
            spider_logger.error(f"搜索小说超时: {keyword}, 规则ID: {rule_id}")
            return []
        finally:
            # 清理回调
            if task_id in self.callbacks:
                del self.callbacks[task_id]

    async def get_novel_detail(self, url: str, rule_id: int) -> Optional[Dict[str, Any]]:
        """获取小说详情"""
        spider_logger.info(f"获取小说详情: {url}, 规则ID: {rule_id}")

        # 生成唯一任务ID
        task_id = f"detail_{url}_{rule_id}_{id(self)}"

        # 创建结果Future
        future = asyncio.Future()
        self.callbacks[task_id] = future

        # 启动爬虫
        d = self.runner.crawl(
            NovelSpider,
            url=url,
            rule_id=rule_id,
            task_id=task_id,
            callback=self._spider_callback,
            detail_mode=True
        )

        # 等待爬虫完成
        await _to_future(d)

        # 等待结果
        try:
            result = await asyncio.wait_for(future, timeout=60)
            return result
        except asyncio.TimeoutError:
            spider_logger.error(f"获取小说详情超时: {url}, 规则ID: {rule_id}")
            return None
        finally:
            # 清理回调
            if task_id in self.callbacks:
                del self.callbacks[task_id]

    async def get_chapters(self, novel_id: int, url: str, rule_id: int) -> List[Dict[str, Any]]:
        """获取小说章节列表"""
        spider_logger.info(f"获取小说章节列表: 小说ID: {novel_id}, URL: {url}, 规则ID: {rule_id}")

        # 生成唯一任务ID
        task_id = f"chapters_{novel_id}_{rule_id}_{id(self)}"

        # 创建结果Future
        future = asyncio.Future()
        self.callbacks[task_id] = future

        # 启动爬虫
        d = self.runner.crawl(
            ChapterSpider,
            novel_id=novel_id,
            url=url,
            rule_id=rule_id,
            task_id=task_id,
            callback=self._spider_callback,
            mode="list"
        )

        # 等待爬虫完成
        await _to_future(d)

        # 等待结果
        try:
            result = await asyncio.wait_for(future, timeout=60)
            return result
        except asyncio.TimeoutError:
            spider_logger.error(f"获取小说章节列表超时: 小说ID: {novel_id}, URL: {url}")
            return []
        finally:
            # 清理回调
            if task_id in self.callbacks:
                del self.callbacks[task_id]

    async def get_chapter_content(self, chapter_id: int, url: str, rule_id: int) -> Optional[str]:
        """获取章节内容"""
        spider_logger.info(f"获取章节内容: 章节ID: {chapter_id}, URL: {url}, 规则ID: {rule_id}")

        # 生成唯一任务ID
        task_id = f"content_{chapter_id}_{rule_id}_{id(self)}"

        # 创建结果Future
        future = asyncio.Future()
        self.callbacks[task_id] = future

        # 启动爬虫
        d = self.runner.crawl(
            ChapterSpider,
            chapter_id=chapter_id,
            url=url,
            rule_id=rule_id,
            task_id=task_id,
            callback=self._spider_callback,
            mode="content"
        )

        # 等待爬虫完成
        await _to_future(d)

        # 等待结果
        try:
            result = await asyncio.wait_for(future, timeout=60)
            return result
        except asyncio.TimeoutError:
            spider_logger.error(f"获取章节内容超时: 章节ID: {chapter_id}, URL: {url}")
            return None
        finally:
            # 清理回调
            if task_id in self.callbacks:
                del self.callbacks[task_id]

    def _spider_callback(self, task_id: str, result: Any) -> None:
        """爬虫回调函数"""
        if task_id in self.callbacks:
            future = self.callbacks[task_id]
            if not future.done():
                future.set_result(result)

    def close(self) -> None:
        """关闭爬虫管理器"""
        _stop_reactor()


# 创建全局爬虫管理器实例
spider_manager = SpiderManager()
