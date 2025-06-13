import os
import json
import asyncio
from typing import Any, Optional, Callable, TypeVar, Dict, Union
from datetime import timedelta
from functools import wraps
import aioredis
from cachetools import TTLCache
from loguru import logger
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 类型变量
T = TypeVar('T')

# 内存缓存
mem_cache = TTLCache(
    maxsize=int(os.getenv("MEM_CACHE_SIZE", "1000")),
    ttl=int(os.getenv("MEM_CACHE_TTL", "3600"))  # 默认1小时
)

# Redis连接
redis_url = os.getenv("REDIS_URL")
redis_client = None


async def get_redis():
    """获取Redis客户端连接"""
    global redis_client
    if redis_url and redis_client is None:
        try:
            redis_client = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
    return redis_client


async def close_redis():
    """关闭Redis连接"""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None
        logger.info("Redis连接已关闭")


async def cache_get(key: str, use_redis: bool = True) -> Optional[Any]:
    """从缓存获取数据"""
    # 先从内存缓存获取
    if key in mem_cache:
        logger.debug(f"从内存缓存获取: {key}")
        return mem_cache[key]

    # 如果启用Redis且内存缓存未命中，则从Redis获取
    if use_redis and redis_url:
        redis = await get_redis()
        if redis:
            try:
                data = await redis.get(key)
                if data:
                    logger.debug(f"从Redis缓存获取: {key}")
                    # 反序列化数据
                    value = json.loads(data)
                    # 同时更新内存缓存
                    mem_cache[key] = value
                    return value
            except Exception as e:
                logger.error(f"从Redis获取缓存失败: {str(e)}")

    return None


async def cache_set(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
    use_redis: bool = True
) -> bool:
    """设置缓存数据"""
    # 更新内存缓存
    mem_cache[key] = value

    # 如果启用Redis，同时更新Redis缓存
    if use_redis and redis_url:
        redis = await get_redis()
        if redis:
            try:
                # 序列化数据
                data = json.dumps(value)
                if ttl:
                    await redis.setex(key, ttl, data)
                else:
                    await redis.set(key, data)
                logger.debug(f"设置Redis缓存: {key}")
                return True
            except Exception as e:
                logger.error(f"设置Redis缓存失败: {str(e)}")
                return False

    return True


async def cache_delete(key: str, use_redis: bool = True) -> bool:
    """删除缓存数据"""
    # 删除内存缓存
    if key in mem_cache:
        del mem_cache[key]

    # 如果启用Redis，同时删除Redis缓存
    if use_redis and redis_url:
        redis = await get_redis()
        if redis:
            try:
                await redis.delete(key)
                logger.debug(f"删除Redis缓存: {key}")
                return True
            except Exception as e:
                logger.error(f"删除Redis缓存失败: {str(e)}")
                return False

    return True


async def cache_clear(pattern: str = "*", use_redis: bool = True) -> bool:
    """清空缓存数据"""
    # 清空内存缓存
    mem_cache.clear()

    # 如果启用Redis，同时清空Redis缓存
    if use_redis and redis_url and pattern:
        redis = await get_redis()
        if redis:
            try:
                # 获取匹配的键
                keys = await redis.keys(pattern)
                if keys:
                    await redis.delete(*keys)
                    logger.debug(f"清空Redis缓存: {pattern}, 共{len(keys)}个键")
                return True
            except Exception as e:
                logger.error(f"清空Redis缓存失败: {str(e)}")
                return False

    return True


def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    use_redis: bool = True,
    key_builder: Optional[Callable[..., str]] = None
):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 构建缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # 默认键构建逻辑
                func_name = func.__name__
                args_str = "_".join(str(arg) for arg in args if not callable(arg))
                kwargs_str = "_".join(f"{k}:{v}" for k, v in kwargs.items())
                cache_key = f"{key_prefix}:{func_name}:{args_str}:{kwargs_str}"

            # 尝试从缓存获取
            cached_result = await cache_get(cache_key, use_redis)
            if cached_result is not None:
                return cached_result

            # 缓存未命中，执行原函数
            result = await func(*args, **kwargs)

            # 缓存结果
            await cache_set(cache_key, result, ttl, use_redis)

            return result
        return wrapper
    return decorator
