import random
from typing import Optional, Union, Type
from scrapy import signals
from scrapy.http import Request, Response
from scrapy.spiders import Spider
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from loguru import logger

from .settings import USER_AGENT_LIST

# 获取爬虫日志记录器
spider_logger = logger.bind(name="spider")


class RandomUserAgentMiddleware:
    """随机用户代理中间件"""

    def process_request(self, request: Request, spider: Spider) -> None:
        """处理请求，设置随机用户代理"""
        user_agent = random.choice(USER_AGENT_LIST)
        request.headers['User-Agent'] = user_agent
        spider_logger.debug(f"使用User-Agent: {user_agent}")


class CustomRetryMiddleware(RetryMiddleware):
    """自定义重试中间件"""

    def __init__(self, settings):
        super().__init__(settings)
        self.max_retry_times = settings.getint('RETRY_TIMES', 3)
        self.retry_http_codes = set(settings.getlist('RETRY_HTTP_CODES', []))

    def process_response(
        self, request: Request, response: Response, spider: Spider
    ) -> Union[Response, Request]:
        """处理响应，根据状态码决定是否重试"""
        if request.meta.get('dont_retry', False):
            return response

        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        # 检查响应内容是否为空或过小
        if len(response.body) < 100:  # 响应内容过小，可能是错误页面
            reason = f"响应内容过小: {len(response.body)} bytes"
            return self._retry(request, reason, spider) or response

        return response

    def process_exception(
        self, request: Request, exception: Exception, spider: Spider
    ) -> Optional[Request]:
        """处理异常，记录日志并重试"""
        spider_logger.error(f"请求异常: {request.url}, 异常: {exception}")
        return super().process_exception(request, exception, spider)

    def _retry(
        self, request: Request, reason: str, spider: Spider
    ) -> Optional[Request]:
        """重试请求"""
        retries = request.meta.get('retry_times', 0) + 1

        if retries <= self.max_retry_times:
            spider_logger.warning(f"重试请求 ({retries}/{self.max_retry_times}): {request.url}, 原因: {reason}")
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            return retryreq
        else:
            spider_logger.error(f"达到最大重试次数，放弃请求: {request.url}")
            return None


class SpiderMiddleware:
    """爬虫中间件"""

    @classmethod
    def from_crawler(cls, crawler):
        """从爬虫创建中间件"""
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_spider_input(self, response: Response, spider: Spider) -> None:
        """处理爬虫输入"""
        return None

    def process_spider_output(self, response: Response, result, spider: Spider):
        """处理爬虫输出"""
        for i in result:
            yield i

    def process_spider_exception(self, response: Response, exception: Exception, spider: Spider):
        """处理爬虫异常"""
        spider_logger.error(f"爬虫异常: {exception}, URL: {response.url}")

    def process_start_requests(self, start_requests, spider: Spider):
        """处理起始请求"""
        for r in start_requests:
            yield r

    def spider_opened(self, spider: Spider) -> None:
        """爬虫开启时的处理"""
        spider_logger.info(f"爬虫 {spider.name} 已启动")

    def spider_closed(self, spider: Spider) -> None:
        """爬虫关闭时的处理"""
        spider_logger.info(f"爬虫 {spider.name} 已关闭")
