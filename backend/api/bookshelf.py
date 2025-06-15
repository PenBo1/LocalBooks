from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from loguru import logger

from database import crud
from database.models import Bookshelf, BookshelfCreate, PaginatedResponse

# 创建路由器
router = APIRouter()


@router.post("/add", response_model=int)
async def add_to_bookshelf(bookshelf: BookshelfCreate):
    """添加小说到书架"""
    try:
        # 检查小说是否存在
        novel = await crud.get_novel(bookshelf.novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail=f"小说不存在: {bookshelf.novel_id}")

        # 如果指定了章节ID，检查章节是否存在
        if bookshelf.last_read_chapter_id:
            chapter = await crud.get_chapter(bookshelf.last_read_chapter_id)
            if not chapter:
                raise HTTPException(status_code=404, detail=f"章节不存在: {bookshelf.last_read_chapter_id}")

            # 检查章节是否属于该小说
            if chapter['novel_id'] != bookshelf.novel_id:
                raise HTTPException(status_code=400, detail="章节不属于该小说")

        # 添加到书架
        bookshelf_id = await crud.add_to_bookshelf(bookshelf)

        return bookshelf_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加到书架失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加到书架失败: {str(e)}")


@router.get("/list", response_model=PaginatedResponse)
async def get_bookshelf(
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页数量", ge=1, le=100),
    sort_by: str = Query("updated_at", description="排序字段: updated_at, added_at, title")
):
    """获取书架列表"""
    try:
        # 获取书架列表
        bookshelf_items, total = await crud.get_bookshelf(page, page_size, sort_by)

        # 构建分页响应
        response = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": bookshelf_items
        }

        return response
    except Exception as e:
        logger.error(f"获取书架列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取书架列表失败: {str(e)}")


@router.post("/update/{bookshelf_id}")
async def update_bookshelf(
    bookshelf_id: int = Path(..., description="书架项ID"),
    data: Dict[str, Any] = Body(..., description="更新数据")
):
    """更新书架项"""
    try:
        # 检查书架项是否存在
        bookshelf = await crud.get_bookshelf_by_id(bookshelf_id)
        if not bookshelf:
            raise HTTPException(status_code=404, detail=f"书架项不存在: {bookshelf_id}")

        # 如果更新了章节ID，检查章节是否存在
        if 'last_read_chapter_id' in data:
            chapter_id = data['last_read_chapter_id']
            if chapter_id:
                chapter = await crud.get_chapter(chapter_id)
                if not chapter:
                    raise HTTPException(status_code=404, detail=f"章节不存在: {chapter_id}")

                # 检查章节是否属于该小说
                if chapter['novel_id'] != bookshelf['novel_id']:
                    raise HTTPException(status_code=400, detail="章节不属于该小说")

        # 更新书架项
        success = await crud.update_bookshelf(bookshelf_id, data)

        if not success:
            raise HTTPException(status_code=500, detail="更新书架项失败")

        return {"message": "更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新书架项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新书架项失败: {str(e)}")


@router.post("/remove/{novel_id}")
async def remove_from_bookshelf(novel_id: int = Path(..., description="小说ID")):
    """从书架移除小说"""
    try:
        # 移除小说
        success = await crud.remove_from_bookshelf(novel_id)

        if not success:
            raise HTTPException(status_code=500, detail="从书架移除小说失败")

        return {"message": "移除成功"}
    except Exception as e:
        logger.error(f"从书架移除小说失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"从书架移除小说失败: {str(e)}")
