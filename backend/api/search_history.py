from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from utils.logger_manager import api_logger, error_logger

from database import crud
from database.models import SearchHistory, SearchHistoryCreate

# 创建路由器
router = APIRouter()


@router.post("/add", response_model=int)
async def add_search_history(search_history: SearchHistoryCreate):
    """添加搜索历史"""
    try:
        history_id = await crud.add_search_history(search_history)
        api_logger.info("添加搜索历史", keyword=search_history.keyword)
        return history_id
    except Exception as e:
        error_logger.exception("添加搜索历史失败", exc_info=e)
        raise HTTPException(status_code=500, detail=f"添加搜索历史失败: {str(e)}")


@router.get("/list", response_model=List[SearchHistory])
async def get_search_history(limit: int = Query(10, description="返回数量")):
    """获取搜索历史列表"""
    try:
        history_list = await crud.get_search_history(limit)
        api_logger.info("获取搜索历史列表", limit=limit)
        return history_list
    except Exception as e:
        error_logger.exception("获取搜索历史列表失败", exc_info=e)
        raise HTTPException(status_code=500, detail=f"获取搜索历史列表失败: {str(e)}")


@router.post("/delete/{history_id}", response_model=bool)
async def delete_search_history(history_id: int = Path(..., description="搜索历史ID")):
    """删除搜索历史"""
    try:
        result = await crud.delete_search_history(history_id)
        api_logger.info("删除搜索历史", history_id=history_id)
        return result
    except Exception as e:
        error_logger.exception("删除搜索历史失败", exc_info=e)
        raise HTTPException(status_code=500, detail=f"删除搜索历史失败: {str(e)}")


@router.post("/delete/keyword/{keyword}", response_model=bool)
async def delete_search_history_by_keyword(keyword: str = Path(..., description="搜索关键词")):
    """根据关键词删除搜索历史"""
    try:
        result = await crud.delete_search_history_by_keyword(keyword)
        api_logger.info("根据关键词删除搜索历史", keyword=keyword)
        return result
    except Exception as e:
        error_logger.exception("根据关键词删除搜索历史失败", exc_info=e)
        raise HTTPException(status_code=500, detail=f"删除搜索历史失败: {str(e)}")


@router.post("/clear", response_model=bool)
async def clear_all_search_history():
    """清空所有搜索历史"""
    try:
        result = await crud.clear_all_search_history()
        api_logger.info("清空所有搜索历史")
        return result
    except Exception as e:
        error_logger.exception("清空搜索历史失败", exc_info=e)
        raise HTTPException(status_code=500, detail=f"清空搜索历史失败: {str(e)}")