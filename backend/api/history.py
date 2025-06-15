from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List
from loguru import logger

from database import crud
from database.models import HistoryCreate, History, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def get_history_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    sort_by: str = Query("read_at", description="排序字段，支持read_at(阅读时间)和title(标题)")
):
    """获取历史记录列表"""
    try:
        history_items, total = await crud.get_history(page, page_size, sort_by)
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": history_items
        }
    except Exception as e:
        logger.error(f"获取历史记录列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取历史记录列表失败")


@router.post("/", status_code=201)
async def add_history(history: HistoryCreate):
    """添加历史记录"""
    try:
        # 验证小说是否存在
        novel = await crud.get_novel(history.novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        # 验证章节是否存在
        chapter = await crud.get_chapter(history.chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        # 添加历史记录
        history_id = await crud.add_history(history)
        return {"id": history_id, "message": "历史记录添加成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加历史记录失败: {e}")
        raise HTTPException(status_code=500, detail="添加历史记录失败")


@router.post("/delete/{history_id}")
async def delete_history(history_id: int = Path(..., description="历史记录ID")):
    """删除历史记录"""
    try:
        success = await crud.delete_history(history_id)
        if not success:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        return {"message": "历史记录删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除历史记录失败: {e}")
        raise HTTPException(status_code=500, detail="删除历史记录失败")


@router.post("/delete/novel/{novel_id}")
async def delete_novel_history(novel_id: int = Path(..., description="小说ID")):
    """删除小说的所有历史记录"""
    try:
        # 验证小说是否存在
        novel = await crud.get_novel(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说不存在")
        
        success = await crud.delete_novel_history(novel_id)
        return {"message": "小说历史记录删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除小说历史记录失败: {e}")
        raise HTTPException(status_code=500, detail="删除小说历史记录失败")


@router.post("/all/clear")
async def clear_all_history():
    """清空所有历史记录"""
    try:
        success = await crud.clear_all_history()
        return {"message": "所有历史记录已清空"}
    except Exception as e:
        logger.error(f"清空历史记录失败: {e}")
        raise HTTPException(status_code=500, detail="清空历史记录失败")