from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import shutil
import subprocess
import platform
from typing import Dict, Any
from utils.logger import logger
from database import crud

router = APIRouter(prefix="/cache", tags=["缓存管理"])

# 设置键名
CACHE_DIR_KEY = "cache_directory"

# 默认缓存目录路径
DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "LocalBooks")

class CacheDirectoryRequest(BaseModel):
    path: str

class CacheInfoResponse(BaseModel):
    path: str
    size: str
    count: int
    exists: bool

@router.get("/info", response_model=CacheInfoResponse)
async def get_cache_info():
    """获取缓存目录信息"""
    try:
        cache_dir = await get_cache_directory()
        
        if not os.path.exists(cache_dir):
            return CacheInfoResponse(
                path=cache_dir,
                size="0 MB",
                count=0,
                exists=False
            )
        
        # 计算目录大小和文件数量
        total_size = 0
        file_count = 0
        
        for dirpath, dirnames, filenames in os.walk(cache_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                    file_count += 1
                except (OSError, IOError):
                    continue
        
        # 转换为可读的大小格式
        size_str = format_size(total_size)
        
        return CacheInfoResponse(
            path=cache_dir,
            size=size_str,
            count=file_count,
            exists=True
        )
        
    except Exception as e:
        logger.error(f"获取缓存信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取缓存信息失败: {str(e)}")

@router.post("/create")
async def create_cache_directory():
    """创建缓存目录"""
    try:
        cache_dir = await get_cache_directory()
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            
            # 创建子目录
            subdirs = ["novels", "chapters", "images", "logs", "database"]
            for subdir in subdirs:
                subdir_path = os.path.join(cache_dir, subdir)
                os.makedirs(subdir_path, exist_ok=True)
            
            logger.info(f"缓存目录创建成功: {cache_dir}")
            return {"message": "缓存目录创建成功", "path": cache_dir}
        else:
            return {"message": "缓存目录已存在", "path": cache_dir}
            
    except Exception as e:
        logger.error(f"创建缓存目录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建缓存目录失败: {str(e)}")

@router.post("/set-directory")
async def set_cache_directory(request: CacheDirectoryRequest):
    """设置缓存目录路径"""
    try:
        new_path = request.path
        
        # 验证路径
        if not os.path.isabs(new_path):
            raise HTTPException(status_code=400, detail="路径必须是绝对路径")
        
        # 创建目录（如果不存在）
        os.makedirs(new_path, exist_ok=True)
        
        # 保存到数据库
        success = await crud.update_setting(CACHE_DIR_KEY, new_path)
        if not success:
            raise HTTPException(status_code=500, detail="保存缓存目录路径失败")
        
        # 创建基本子目录
        subdirs = ["novels", "chapters", "images", "logs", "database"]
        for subdir in subdirs:
            subdir_path = os.path.join(new_path, subdir)
            os.makedirs(subdir_path, exist_ok=True)
        
        logger.info(f"缓存目录设置成功: {new_path}")
        return {"message": "缓存目录设置成功", "path": new_path}
        
    except Exception as e:
        logger.error(f"设置缓存目录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"设置缓存目录失败: {str(e)}")

@router.post("/open")
async def open_cache_directory():
    """打开缓存目录"""
    try:
        cache_dir = await get_cache_directory()
        
        if not os.path.exists(cache_dir):
            # 如果目录不存在，先创建
            await create_cache_directory()
        
        # 根据操作系统打开文件管理器
        system = platform.system()
        if system == "Windows":
            os.startfile(cache_dir)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", cache_dir])
        elif system == "Linux":
            subprocess.run(["xdg-open", cache_dir])
        else:
            raise HTTPException(status_code=500, detail="不支持的操作系统")
        
        logger.info(f"打开缓存目录: {cache_dir}")
        return {"message": "缓存目录已打开", "path": cache_dir}
        
    except Exception as e:
        logger.error(f"打开缓存目录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"打开缓存目录失败: {str(e)}")

@router.delete("/clear")
async def clear_cache():
    """清空缓存"""
    try:
        cache_dir = await get_cache_directory()
        
        if os.path.exists(cache_dir):
            # 删除缓存目录中的所有文件和子目录，但保留目录本身
            for item in os.listdir(cache_dir):
                item_path = os.path.join(cache_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            
            # 重新创建基本子目录
            subdirs = ["novels", "chapters", "images", "logs", "database"]
            for subdir in subdirs:
                subdir_path = os.path.join(cache_dir, subdir)
                os.makedirs(subdir_path, exist_ok=True)
        
        logger.info(f"缓存清空成功: {cache_dir}")
        return {"message": "缓存清空成功"}
        
    except Exception as e:
        logger.error(f"清空缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")

async def get_cache_directory() -> str:
    """获取缓存目录路径"""
    try:
        # 从数据库中读取缓存目录路径
        cache_dir = await crud.get_setting(CACHE_DIR_KEY)
        
        # 如果数据库中没有设置，则使用默认路径
        if not cache_dir:
            return DEFAULT_CACHE_DIR
            
        return cache_dir
    except Exception as e:
        logger.error(f"获取缓存目录路径失败: {str(e)}")
        # 出错时返回默认路径
        return DEFAULT_CACHE_DIR

def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"