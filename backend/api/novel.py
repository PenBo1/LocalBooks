from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from loguru import logger

from database import crud
from database.models import Novel, Chapter, SearchResult, NovelCreate, ChapterCreate, PaginatedResponse
from spider.spider_manager import spider_manager
from utils.cache import cached

# 创建路由器
router = APIRouter()


@router.get("/search", response_model=List[SearchResult])
async def search_novel(
    keyword: str = Query(..., description="搜索关键词"),
    rule_id: int = Query(..., description="规则ID")
):
    """搜索小说"""
    try:
        # 检查规则是否存在
        rule = await crud.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail=f"规则不存在: {rule_id}")

        # 使用爬虫搜索小说
        results = await spider_manager.search_novel(keyword, rule_id)

        # 记录搜索历史
        from database.models import SearchHistoryCreate
        search_history = SearchHistoryCreate(keyword=keyword)
        await crud.add_search_history(search_history)

        return results
    except Exception as e:
        logger.error(f"搜索小说失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索小说失败: {str(e)}")


# 热门小说API接口已删除


@router.post("/add", response_model=int)
async def add_novel(novel_data: Dict[str, Any]):
    """添加小说"""
    try:
        # 检查是否提供了必要信息
        if not novel_data.get('title') or not novel_data.get('source_url'):
            raise HTTPException(status_code=400, detail="缺少必要的小说信息")

        # 检查规则是否存在
        rule_id = novel_data.get('rule_id')
        if rule_id:
            rule = await crud.get_rule(rule_id)
            if not rule:
                raise HTTPException(status_code=404, detail=f"规则不存在: {rule_id}")

        # 创建小说对象
        novel = NovelCreate(
            title=novel_data['title'],
            author=novel_data.get('author'),
            cover=novel_data.get('cover'),
            description=novel_data.get('description'),
            source=novel_data.get('source'),
            source_url=novel_data['source_url']
        )

        # 添加到数据库
        novel_id = await crud.create_novel(novel)

        return novel_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加小说失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加小说失败: {str(e)}")


@router.get("/{novel_id}", response_model=Novel)
async def get_novel_detail(novel_id: int = Path(..., description="小说ID")):
    """获取小说详情"""
    try:
        novel = await crud.get_novel(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail=f"小说不存在: {novel_id}")

        return novel
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取小说详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取小说详情失败: {str(e)}")


@router.get("/fetch_detail")
async def fetch_novel_detail(
    url: str = Query(..., description="小说详情页URL"),
    rule_id: int = Query(..., description="规则ID")
):
    """从网络获取小说详情"""
    try:
        # 检查规则是否存在
        rule = await crud.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail=f"规则不存在: {rule_id}")

        # 使用爬虫获取小说详情
        detail = await spider_manager.get_novel_detail(url, rule_id)
        if not detail:
            raise HTTPException(status_code=404, detail="获取小说详情失败")

        return detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取小说详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取小说详情失败: {str(e)}")


@router.get("/{novel_id}/chapters", response_model=List[Chapter])
@cached(ttl=3600, key_prefix="novel_chapters")
async def get_novel_chapters(novel_id: int = Path(..., description="小说ID")):
    """获取小说章节列表"""
    try:
        # 检查小说是否存在
        novel = await crud.get_novel(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail=f"小说不存在: {novel_id}")

        # 从数据库获取章节列表
        chapters = await crud.get_novel_chapters(novel_id)

        # 如果数据库中没有章节，则从网络获取
        if not chapters and novel['source_url']:
            # 获取规则
            rule_id = novel.get('rule_id')
            if not rule_id:
                # 尝试根据source查找规则
                rules, _ = await crud.get_rules(page=1, page_size=1)
                if rules:
                    rule_id = rules[0]['id']

            if rule_id:
                # 使用爬虫获取章节列表
                chapter_list = await spider_manager.get_chapters(novel_id, novel['source_url'], rule_id)

                # 保存到数据库
                for chapter_data in chapter_list:
                    chapter = ChapterCreate(
                        novel_id=novel_id,
                        title=chapter_data['title'],
                        chapter_index=chapter_data['chapter_index'],
                        source_url=chapter_data['source_url'],
                        content=None,
                        is_downloaded=False
                    )
                    await crud.create_chapter(chapter)

                # 重新获取章节列表
                chapters = await crud.get_novel_chapters(novel_id)

        return chapters
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取小说章节列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取小说章节列表失败: {str(e)}")


@router.get("/{novel_id}/chapter/{chapter_id}", response_model=Chapter)
@cached(ttl=3600, key_prefix="chapter_content")
async def get_chapter_content(novel_id: int = Path(..., description="小说ID"), chapter_id: int = Path(..., description="章节ID")):
    """获取章节内容"""
    try:
        # 从数据库获取章节
        chapter = await crud.get_chapter(chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail=f"章节不存在: {chapter_id}")
            
        # 验证章节是否属于该小说
        if chapter['novel_id'] != novel_id:
            raise HTTPException(status_code=400, detail="章节不属于该小说")

        # 如果章节内容为空或未下载，则从网络获取
        if not chapter['content'] or not chapter['is_downloaded']:
            # 获取小说信息
            novel = await crud.get_novel(novel_id)
            if not novel:
                raise HTTPException(status_code=404, detail=f"小说不存在: {novel_id}")

            # 获取规则
            rule_id = novel.get('rule_id')
            if not rule_id:
                # 尝试根据source查找规则
                rules, _ = await crud.get_rules(page=1, page_size=1)
                if rules:
                    rule_id = rules[0]['id']

            if rule_id and chapter['source_url']:
                # 使用爬虫获取章节内容
                content = await spider_manager.get_chapter_content(
                    chapter_id, chapter['source_url'], rule_id
                )

                if content:
                    # 更新章节内容
                    await crud.update_chapter_content(chapter_id, content)
                    chapter['content'] = content
                    chapter['is_downloaded'] = True

        return chapter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取章节内容失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取章节内容失败: {str(e)}")


@router.get("/{novel_id}/detail/network", response_model=Novel)
async def get_novel_detail_from_network(novel_id: int = Path(..., description="小说ID")):
    """从网络获取小说详情"""
    try:
        # 检查小说是否存在
        novel = await crud.get_novel(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail=f"小说不存在: {novel_id}")
        
        # 检查规则是否存在
        rule_id = novel.get('rule_id')
        if not rule_id:
            # 尝试根据source查找规则
            rules, _ = await crud.get_rules(page=1, page_size=1)
            if rules:
                rule_id = rules[0]['id']
            else:
                raise HTTPException(status_code=404, detail="未找到可用的规则")
        
        # 使用爬虫获取小说详情
        detail = await spider_manager.get_novel_detail(novel['source_url'], rule_id)
        if not detail:
            raise HTTPException(status_code=404, detail="获取小说详情失败")
        
        # 更新小说信息
        await crud.update_novel(novel_id, detail)
        
        # 获取更新后的小说信息
        updated_novel = await crud.get_novel(novel_id)
        return updated_novel
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"从网络获取小说详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"从网络获取小说详情失败: {str(e)}")


@router.get("/{novel_id}/chapters/network", response_model=List[Chapter])
async def get_novel_chapters_from_network(novel_id: int = Path(..., description="小说ID")):
    """从网络获取小说章节列表"""
    try:
        # 检查小说是否存在
        novel = await crud.get_novel(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail=f"小说不存在: {novel_id}")
        
        # 检查规则是否存在
        rule_id = novel.get('rule_id')
        if not rule_id:
            # 尝试根据source查找规则
            rules, _ = await crud.get_rules(page=1, page_size=1)
            if rules:
                rule_id = rules[0]['id']
            else:
                raise HTTPException(status_code=404, detail="未找到可用的规则")
        
        # 使用爬虫获取章节列表
        chapter_list = await spider_manager.get_chapters(novel_id, novel['source_url'], rule_id)
        
        # 保存到数据库
        for chapter_data in chapter_list:
            # 检查章节是否已存在
            existing_chapter = await crud.get_chapter_by_url(chapter_data['source_url'])
            if not existing_chapter:
                chapter = ChapterCreate(
                    novel_id=novel_id,
                    title=chapter_data['title'],
                    chapter_index=chapter_data['chapter_index'],
                    source_url=chapter_data['source_url'],
                    content=None,
                    is_downloaded=False
                )
                await crud.create_chapter(chapter)
        
        # 获取更新后的章节列表
        chapters = await crud.get_novel_chapters(novel_id)
        return chapters
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"从网络获取小说章节列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"从网络获取小说章节列表失败: {str(e)}")


@router.get("/{novel_id}/chapter/{chapter_id}/network", response_model=Chapter)
async def get_chapter_content_from_network(novel_id: int = Path(..., description="小说ID"), chapter_id: int = Path(..., description="章节ID")):
    """从网络获取章节内容"""
    try:
        # 检查章节是否存在
        chapter = await crud.get_chapter(chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail=f"章节不存在: {chapter_id}")
        
        # 验证章节是否属于该小说
        if chapter['novel_id'] != novel_id:
            raise HTTPException(status_code=400, detail="章节不属于该小说")
        
        # 检查小说是否存在
        novel = await crud.get_novel(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail=f"小说不存在: {novel_id}")
        
        # 检查规则是否存在
        rule_id = novel.get('rule_id')
        if not rule_id:
            # 尝试根据source查找规则
            rules, _ = await crud.get_rules(page=1, page_size=1)
            if rules:
                rule_id = rules[0]['id']
            else:
                raise HTTPException(status_code=404, detail="未找到可用的规则")
        
        # 使用爬虫获取章节内容
        content = await spider_manager.get_chapter_content(chapter_id, chapter['source_url'], rule_id)
        if not content:
            raise HTTPException(status_code=404, detail="获取章节内容失败")
        
        # 更新章节内容
        await crud.update_chapter_content(chapter_id, content)
        
        # 获取更新后的章节信息
        updated_chapter = await crud.get_chapter(chapter_id)
        return updated_chapter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"从网络获取章节内容失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"从网络获取章节内容失败: {str(e)}")
