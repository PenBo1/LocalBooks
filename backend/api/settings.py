from fastapi import APIRouter, HTTPException, Path, Body
from typing import Dict, Any, Optional
from loguru import logger
import json

from database import crud

router = APIRouter()


@router.get("/")
async def get_all_settings():
    """获取所有设置"""
    try:
        settings = await crud.get_all_settings()
        # 尝试将JSON字符串转换为对象
        for key, value in settings.items():
            try:
                settings[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # 如果不是有效的JSON，保持原样
                pass
        return settings
    except Exception as e:
        logger.error(f"获取所有设置失败: {e}")
        raise HTTPException(status_code=500, detail="获取所有设置失败")


@router.get("/{key}")
async def get_setting(key: str = Path(..., description="设置键名")):
    """获取单个设置"""
    try:
        value = await crud.get_setting(key)
        if value is None:
            raise HTTPException(status_code=404, detail=f"设置 {key} 不存在")
        
        # 尝试将JSON字符串转换为对象
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # 如果不是有效的JSON，保持原样
            pass
            
        return {key: value}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取设置失败: {e}")
        raise HTTPException(status_code=500, detail="获取设置失败")


@router.put("/{key}")
async def update_setting(
    value: Any = Body(..., description="设置值"),
    key: str = Path(..., description="设置键名")
):
    """更新设置"""
    try:
        # 如果值是复杂对象，转换为JSON字符串
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        elif not isinstance(value, str):
            value = str(value)
        
        success = await crud.update_setting(key, value)
        return {"message": f"设置 {key} 更新成功"}
    except Exception as e:
        logger.error(f"更新设置失败: {e}")
        raise HTTPException(status_code=500, detail="更新设置失败")


# 预定义设置键名常量
class SettingKeys:
    THEME = "theme"  # 主题：护眼、深色、浅色、浅黄色、粉色
    FONT_SIZE = "font_size"  # 字号大小
    FONT_FAMILY = "font_family"  # 字体
    LINE_HEIGHT = "line_height"  # 行距
    CACHE_ENABLED = "cache_enabled"  # 是否启用缓存
    CACHE_EXPIRATION = "cache_expiration"  # 缓存过期时间（秒）
    LOG_LEVEL = "log_level"  # 日志等级


@router.get("/default/reset")
async def reset_to_default():
    """重置为默认设置"""
    try:
        # 默认设置
        default_settings = {
            SettingKeys.THEME: "light",  # 浅色主题
            SettingKeys.FONT_SIZE: "16",  # 16px
            SettingKeys.FONT_FAMILY: "Microsoft YaHei, sans-serif",  # 微软雅黑
            SettingKeys.LINE_HEIGHT: "1.5",  # 1.5倍行距
            SettingKeys.CACHE_ENABLED: "true",  # 启用缓存
            SettingKeys.CACHE_EXPIRATION: "86400",  # 24小时
            SettingKeys.LOG_LEVEL: "INFO"  # INFO级别
        }
        
        # 更新所有设置
        for key, value in default_settings.items():
            await crud.update_setting(key, value)
        
        return {"message": "已重置为默认设置"}
    except Exception as e:
        logger.error(f"重置默认设置失败: {e}")
        raise HTTPException(status_code=500, detail="重置默认设置失败")