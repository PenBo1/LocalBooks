from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class NovelBase(BaseModel):
    """小说基本信息模型"""
    title: str
    author: Optional[str] = None
    cover: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class NovelCreate(NovelBase):
    """创建小说的请求模型"""
    pass


class Novel(NovelBase):
    """小说完整信息模型"""
    id: int
    last_update: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChapterBase(BaseModel):
    """章节基本信息模型"""
    title: str
    chapter_index: int
    source_url: Optional[str] = None


class ChapterCreate(ChapterBase):
    """创建章节的请求模型"""
    novel_id: int
    content: Optional[str] = None
    is_downloaded: bool = False


class Chapter(ChapterBase):
    """章节完整信息模型"""
    id: int
    novel_id: int
    content: Optional[str] = None
    is_downloaded: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookshelfBase(BaseModel):
    """书架基本信息模型"""
    novel_id: int
    last_read_chapter_id: Optional[int] = None
    last_read_position: int = 0


class BookshelfCreate(BookshelfBase):
    """创建书架项的请求模型"""
    pass


class Bookshelf(BookshelfBase):
    """书架完整信息模型"""
    id: int
    added_at: datetime
    updated_at: datetime
    novel: Optional[Novel] = None

    class Config:
        from_attributes = True


class HistoryBase(BaseModel):
    """历史记录基本信息模型"""
    novel_id: int
    chapter_id: int
    read_position: int = 0


class HistoryCreate(HistoryBase):
    """创建历史记录的请求模型"""
    pass


class History(HistoryBase):
    """历史记录完整信息模型"""
    id: int
    read_at: datetime
    novel: Optional[Novel] = None
    chapter: Optional[Chapter] = None

    class Config:
        from_attributes = True


class RuleBase(BaseModel):
    """规则基本信息模型"""
    name: str
    source_url: str
    search_url: str
    cover_rule: Optional[str] = None
    title_rule: str
    author_rule: Optional[str] = None
    description_rule: Optional[str] = None
    chapter_list_rule: str
    chapter_content_rule: str


class RuleCreate(RuleBase):
    """创建规则的请求模型"""
    pass


class Rule(RuleBase):
    """规则完整信息模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SettingBase(BaseModel):
    """设置基本信息模型"""
    key: str
    value: str


class SettingCreate(SettingBase):
    """创建设置的请求模型"""
    pass


class Setting(SettingBase):
    """设置完整信息模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    """搜索结果模型"""
    title: str
    author: Optional[str] = None
    cover: Optional[str] = None
    description: Optional[str] = None
    source: str
    source_url: str


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    total: int
    page: int
    page_size: int
    data: List
