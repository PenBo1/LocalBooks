import os
import sys
from loguru import logger
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "WARNING": "WARNING",
    "ERROR": "ERROR",
    "CRITICAL": "CRITICAL"
}

# 默认日志级别
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def setup_logger(log_level: Optional[str] = None) -> None:
    """配置日志记录器"""
    # 确定日志级别
    level = log_level or DEFAULT_LOG_LEVEL
    level = LOG_LEVELS.get(level.upper(), "INFO")

    # 移除默认处理器
    logger.remove()

    # 添加控制台处理器
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # 添加文件处理器 - 常规日志
    logger.add(
        os.path.join(LOG_DIR, "app.log"),
        rotation="10 MB",
        retention="7 days",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    # 添加文件处理器 - 错误日志
    logger.add(
        os.path.join(LOG_DIR, "error.log"),
        rotation="10 MB",
        retention="7 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    # 添加文件处理器 - 爬虫日志
    logger.add(
        os.path.join(LOG_DIR, "spider.log"),
        rotation="10 MB",
        retention="7 days",
        level=level,
        filter=lambda record: "spider" in record["name"].lower(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    logger.info(f"日志系统初始化完成，日志级别: {level}")


def get_logger(name: str):
    """获取命名日志记录器"""
    return logger.bind(name=name)


def log_request(request_data: Dict[str, Any]) -> None:
    """记录请求日志"""
    logger.debug(f"请求数据: {request_data}")


def log_response(response_data: Dict[str, Any]) -> None:
    """记录响应日志"""
    logger.debug(f"响应数据: {response_data}")


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """记录错误日志"""
    error_message = f"错误: {str(error)}"
    if context:
        error_message += f", 上下文: {context}"
    logger.error(error_message, exc_info=True)


# 初始化日志系统
setup_logger()
