import re
import json
from typing import Dict, Any, List, Optional, Callable, Iterator, Union
from urllib.parse import urljoin

import scrapy
from scrapy.http import Request, Response
from bs4 import BeautifulSoup
from loguru import logger

from database import crud

# 获取爬虫日志记录器
spider_logger = logger.bind(name="spider")


class NovelSpider(scrapy.Spider):
    """小说爬虫，用于搜索小说和获取小说详情"""
    name = 'novel_spider'

    def __init__(
        self,
        keyword: Optional[str] = None,
        url: Optional[str] = None,
        rule_id: int = 0,
        task_id: str = '',
        callback: Optional[Callable] = None,
        detail_mode: bool = False,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.keyword = keyword
        self.url = url
        self.rule_id = rule_id
        self.task_id = task_id
        self.callback = callback
        self.detail_mode = detail_mode
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
        if not rule:
            return

        if self.detail_mode and self.url:
            # 详情模式：直接请求小说详情页
            yield Request(url=self.url, callback=self.parse_detail)
        elif self.keyword and rule['search_url']:
            # 搜索模式：请求搜索页
            search_url = rule['search_url'].replace('{keyword}', self.keyword)
            yield Request(url=search_url, callback=self.parse_search)

    def parse_search(self, response: Response) -> Iterator[Dict[str, Any]]:
        """解析搜索结果"""
        try:
            rule = self.rule
            if not rule:
                return

            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取搜索结果列表
            results = []

            # 这里需要根据规则解析搜索结果
            # 由于每个网站的结构不同，这里使用一个通用的方法
            # 实际应用中可能需要针对不同网站定制解析逻辑

            # 假设搜索结果是一个列表，每个项目包含标题、作者、链接等信息
            # 这里使用一些常见的选择器尝试提取
            items = soup.select('div.result-item, div.book-item, li.book-list, div.novel-item')

            for item in items:
                # 提取标题和链接
                title_elem = item.select_one('a.book-name, a.title, h3 > a, div.name > a')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem.get('href')
                if not link:
                    continue

                # 处理相对URL
                if not link.startswith('http'):
                    link = urljoin(response.url, link)

                # 提取作者
                author_elem = item.select_one('span.author, div.author, p.author')
                author = author_elem.get_text(strip=True) if author_elem else None

                # 提取封面
                cover_elem = item.select_one('img.cover, div.cover > img, img.book-cover')
                cover = cover_elem.get('src') if cover_elem else None
                if cover and not cover.startswith('http'):
                    cover = urljoin(response.url, cover)

                # 提取描述
                desc_elem = item.select_one('p.desc, div.intro, div.description')
                description = desc_elem.get_text(strip=True) if desc_elem else None

                # 添加到结果列表
                results.append({
                    'type': 'search_result',
                    'title': title,
                    'author': author,
                    'cover': cover,
                    'description': description,
                    'source': rule['name'],
                    'source_url': link
                })

            # 如果没有找到结果，尝试其他常见的选择器
            if not results:
                # 尝试更多的选择器组合
                items = soup.select('div.book, li.result, div.search-result-item')
                for item in items:
                    title_elem = item.select_one('a, h3, div.title')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href')
                    if not link:
                        continue

                    # 处理相对URL
                    if not link.startswith('http'):
                        link = urljoin(response.url, link)

                    # 添加到结果列表
                    results.append({
                        'type': 'search_result',
                        'title': title,
                        'author': None,
                        'cover': None,
                        'description': None,
                        'source': rule['name'],
                        'source_url': link
                    })

            spider_logger.info(f"搜索结果: {len(results)} 条")
            return results

        except Exception as e:
            spider_logger.error(f"解析搜索结果失败: {str(e)}")
            return []

    def parse_detail(self, response: Response) -> Dict[str, Any]:
        """解析小说详情"""
        try:
            rule = self.rule
            if not rule:
                return {}

            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取小说信息
            result = {
                'type': 'novel_detail',
                'source_url': response.url,
                'source': rule['name']
            }

            # 提取标题
            if rule['title_rule']:
                title_elem = soup.select_one(rule['title_rule'])
                if title_elem:
                    result['title'] = title_elem.get_text(strip=True)

            # 提取作者
            if rule['author_rule']:
                author_elem = soup.select_one(rule['author_rule'])
                if author_elem:
                    result['author'] = author_elem.get_text(strip=True)

            # 提取封面
            if rule['cover_rule']:
                cover_elem = soup.select_one(rule['cover_rule'])
                if cover_elem:
                    cover = cover_elem.get('src')
                    if cover and not cover.startswith('http'):
                        cover = urljoin(response.url, cover)
                    result['cover'] = cover

            # 提取描述
            if rule['description_rule']:
                desc_elem = soup.select_one(rule['description_rule'])
                if desc_elem:
                    result['description'] = desc_elem.get_text(strip=True)

            # 提取章节列表URL
            # 通常小说详情页就包含章节列表，或者有一个链接指向章节列表页
            # 这里假设章节列表就在当前页面
            result['chapters_url'] = response.url

            spider_logger.info(f"获取小说详情成功: {result.get('title', '未知标题')}")
            return result

        except Exception as e:
            spider_logger.error(f"解析小说详情失败: {str(e)}")
            return {}
