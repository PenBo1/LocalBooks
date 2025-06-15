from typing import Dict, Any
from fastapi import APIRouter, Path, HTTPException, BackgroundTasks
from loguru import logger

from database import crud
from spider.spider_manager import spider_manager

# 创建路由器
router = APIRouter()


async def download_novel_chapters_task(novel_id: int, rule_id: int, source_url: str):
    """后台任务：下载小说所有章节"""
    try:
        # 获取章节列表
        chapters = await crud.get_novel_chapters(novel_id)
        
        # 如果没有章节，先从网络获取章节列表
        if not chapters:
            chapters = await spider_manager.get_chapters(novel_id, source_url, rule_id)
            if not chapters:
                logger.error(f"获取小说章节列表失败: 小说ID {novel_id}")
                return
        
        # 遍历章节，下载未下载的章节内容
        for chapter in chapters:
            # 如果章节未下载，则下载内容
            if not chapter.get('is_downloaded') or not chapter.get('content'):
                content = await spider_manager.get_chapter_content(
                    chapter['id'], 
                    chapter['url'], 
                    rule_id
                )
                
                if content:
                    # 更新章节内容
                    await crud.update_chapter_content(chapter['id'], content)
                    logger.info(f"下载章节成功: 章节ID {chapter['id']}, 标题: {chapter['title']}")
                else:
                    logger.error(f"下载章节内容失败: 章节ID {chapter['id']}, 标题: {chapter['title']}")
        
        logger.info(f"小说章节下载任务完成: 小说ID {novel_id}")
    except Exception as e:
        logger.error(f"下载小说章节失败: {str(e)}")


@router.post("/{novel_id}/download")
async def download_novel_chapters(background_tasks: BackgroundTasks, novel_id: int = Path(..., description="小说ID")):
    """下载小说所有章节"""
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
        
        # 添加后台任务
        background_tasks.add_task(
            download_novel_chapters_task, 
            novel_id, 
            rule_id, 
            novel['source_url']
        )
        
        return {"message": "章节下载任务已开始，请稍后查看"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载小说章节失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载小说章节失败: {str(e)}")