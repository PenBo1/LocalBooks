from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from loguru import logger

from database import crud
from database.models import SearchHistory, SearchHistoryCreate

# 创建路由器
router = APIRouter()


@router.post("/add", response_model=int)
async def add_search_history(search_history: SearchHistoryCreate):
    """添加搜索历史"""
    try:
        history_id = await crud.add_search_history(search_history)
        return history_id
    except Exception as e:
        logger.error(f"添加搜索历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加搜索历史失败: {str(e)}")


@router.get("/list", response_model=List[SearchHistory])
async def get_search_history(limit: int = Query(10, description="返回数量")):
    """获取搜索历史列表"""
    try:
        history_list = await crud.get_search_history(limit)
        return history_list
    except Exception as e:
        logger.error(f"获取搜索历史列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取搜索历史列表失败: {str(e)}")


@router.delete("/{history_id}", response_model=bool)
async def delete_search_history(history_id: int = Path(..., description="搜索历史ID")):
    """删除搜索历史"""
    try:
        result = await crud.delete_search_history(history_id)
        return result
    except Exception as e:
        logger.error(f"删除搜索历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除搜索历史失败: {str(e)}")


@router.delete("/keyword/{keyword}", response_model=bool)
async def delete_search_history_by_keyword(keyword: str = Path(..., description="搜索关键词")):
    """根据关键词删除搜索历史"""
    try:
        result = await crud.delete_search_history_by_keyword(keyword)
        return result
    except Exception as e:
        logger.error(f"删除搜索历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除搜索历史失败: {str(e)}")


@router.delete("/clear", response_model=bool)
async def clear_all_search_history():
    """清空所有搜索历史"""
    try:
        result = await crud.clear_all_search_history()
        return result
    except Exception as e:
        logger.error(f"清空搜索历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清空搜索历史失败: {str(e)}")