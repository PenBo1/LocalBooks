# Scrapy爬虫设置

BOT_NAME = 'LocalBooks'

SPIDER_MODULES = ['spider.spiders']
NEWCOMER_MODULE = 'spider.spiders'

# 爬虫用户代理
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# 遵循robots.txt规则
ROBOTSTXT_OBEY = False

# 配置最大并发请求数
CONCURRENT_REQUESTS = 16

# 下载超时时间
DOWNLOAD_TIMEOUT = 15

# 下载延迟
DOWNLOAD_DELAY = 0.5

# 随机化下载延迟
RANDOMIZE_DOWNLOAD_DELAY = True

# 禁用cookies
COOKIES_ENABLED = False

# 重试次数
RETRY_TIMES = 3

# 重试HTTP代码
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# 启用重定向
REDIRECT_ENABLED = True

# 日志级别
LOG_LEVEL = 'INFO'

# 禁用Scrapy默认日志，使用loguru
LOG_ENABLED = False

# 启用HTTP缓存
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24小时
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 下载器中间件
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 100,
    'spider.middlewares.RandomUserAgentMiddleware': 400,
    'spider.middlewares.CustomRetryMiddleware': 550,
}

# 项目管道
ITEM_PIPELINES = {
    'spider.pipelines.NovelPipeline': 300,
}

# 启用自动限速
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 5.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# 随机用户代理列表
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
]
