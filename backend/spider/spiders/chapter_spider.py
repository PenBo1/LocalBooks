import re
from typing import Dict, Any, List, Optional, Callable, Iterator, Union
from urllib.parse import urljoin

import scrapy
from scrapy.http import Request, Response
from bs4 import BeautifulSoup
from loguru import logger

from database import crud

# 获取爬虫日志记录器
spider_logger = logger.bind(name="spider")


class ChapterSpider(scrapy.Spider):
    """章节爬虫，用于获取小说章节列表和章节内容"""
    name = 'chapter_spider'

    def __init__(
        self,
        novel_id: Optional[int] = None,
        chapter_id: Optional[int] = None,
        url: str = '',
        rule_id: int = 0,
        task_id: str = '',
        callback: Optional[Callable] = None,
        mode: str = 'list',  # 'list' 或 'content'
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.novel_id = novel_id
        self.chapter_id = chapter_id
        self.url = url
        self.rule_id = rule_id
        self.task_id = task_id
        self.callback = callback
        self.mode = mode
        self.rule = None

    async def _get_rule(self) -> Optional[Dict[str, Any]]:
        """获取规则"""
        if not self.rule:
            self.rule = await crud.get_rule(self.rule_id)
            if not self.rule:
                spider_logger.error(f"规则不存在: {self.rule_id}")
        return self.rule

    async def start_requests(self) -> Iterator[Request]:
        """开始请求"""
        rule = await self._get_rule()
        if not rule or not self.url:
            return

        if self.mode == 'list' and self.novel_id:
            # 章节列表模式
            yield Request(url=self.url, callback=self.parse_chapter_list)
        elif self.mode == 'content' and self.chapter_id:
            # 章节内容模式
            yield Request(url=self.url, callback=self.parse_chapter_content)

    def parse_chapter_list(self, response: Response) -> List[Dict[str, Any]]:
        """解析章节列表"""
        try:
            rule = self.rule
            if not rule or not rule['chapter_list_rule']:
                return []

            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取章节列表
            chapters = []
            chapter_elems = soup.select(rule['chapter_list_rule'])

            for index, elem in enumerate(chapter_elems):
                # 提取章节标题和链接
                title = elem.get_text(strip=True)
                link = elem.get('href')

                if not title or not link:
                    continue

                # 处理相对URL
                if not link.startswith('http'):
                    link = urljoin(response.url, link)

                # 添加到章节列表
                chapters.append({
                    'novel_id': self.novel_id,
                    'title': title,
                    'chapter_index': index,
                    'source_url': link
                })

            spider_logger.info(f"获取章节列表成功: {len(chapters)} 章")
            return chapters

        except Exception as e:
            spider_logger.error(f"解析章节列表失败: {str(e)}")
            return []

    def parse_chapter_content(self, response: Response) -> str:
        """解析章节内容"""
        try:
            rule = self.rule
            if not rule or not rule['chapter_content_rule']:
                return ""

            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取章节内容
            content_elem = soup.select_one(rule['chapter_content_rule'])
            if not content_elem:
                return ""

            # 获取纯文本内容
            content = content_elem.get_text('\n', strip=True)

            # 清理内容
            # 移除多余空行
            content = '\n\n'.join(line.strip() for line in content.split('\n') if line.strip())

            # 移除常见的广告文本
            ad_patterns = [
                r'\(请在百度搜索.*?\)',
                r'手机用户请访问.*?com',
                r'本章未完.*?下一页',
                r'天才一秒记住.*?com',
                r'https?://\S+',
                r'www\.\S+\.com',
                r'小说更新最快',
                r'无弹窗阅读',
                r'请记住本站',
                r'本站网址',
                r'免费阅读',
                r'最新章节',
                r'请收藏本站',
                r'手机阅读',
                r'章节目录',
                r'加入书签',
                r'TXT下载',
                r'全文阅读',
            ]

            for pattern in ad_patterns:
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)

            spider_logger.info(f"获取章节内容成功: {len(content)} 字符")
            return content

        except Exception as e:
            spider_logger.error(f"解析章节内容失败: {str(e)}")
            return ""
