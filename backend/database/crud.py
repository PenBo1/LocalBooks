from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import aiosqlite
from loguru import logger

from database.init_db import get_db_connection
from database.models import (
    Novel, NovelCreate,
    Chapter, ChapterCreate,
    Bookshelf, BookshelfCreate,
    History, HistoryCreate,
    Rule, RuleCreate,
    Setting, SettingCreate
)


# 小说相关操作
async def create_novel(novel: NovelCreate) -> int:
    """创建小说"""
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            """
            INSERT INTO novels (title, author, cover, description, source, source_url, last_update)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (novel.title, novel.author, novel.cover, novel.description,
             novel.source, novel.source_url, datetime.now())
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def get_novel(novel_id: int) -> Optional[Dict]:
    """获取小说详情"""
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            "SELECT * FROM novels WHERE id = ?", (novel_id,)
        )
        result = await cursor.fetchone()
        return dict(result) if result else None
    finally:
        await conn.close()


async def search_novels(keyword: str, page: int = 1, page_size: int = 10) -> Tuple[List[Dict], int]:
    """搜索小说"""
    conn = await get_db_connection()
    try:
        # 计算总数
        cursor = await conn.execute(
            "SELECT COUNT(*) as count FROM novels WHERE title LIKE ? OR author LIKE ?",
            (f"%{keyword}%", f"%{keyword}%")
        )
        result = await cursor.fetchone()
        total = result['count']

        # 获取分页数据
        cursor = await conn.execute(
            """
            SELECT * FROM novels
            WHERE title LIKE ? OR author LIKE ?
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (f"%{keyword}%", f"%{keyword}%", page_size, (page - 1) * page_size)
        )
        rows = await cursor.fetchall()
        novels = [dict(row) for row in rows]

        return novels, total
    finally:
        await conn.close()


async def get_hot_novels(limit: int = 10) -> List[Dict]:
    """获取热门小说"""
    conn = await get_db_connection()
    try:
        # 基于历史记录和书架数据计算热门小说
        cursor = await conn.execute(
            """
            SELECT n.*,
                   COUNT(DISTINCT h.id) as history_count,
                   COUNT(DISTINCT b.id) as bookshelf_count
            FROM novels n
            LEFT JOIN history h ON n.id = h.novel_id
            LEFT JOIN bookshelf b ON n.id = b.novel_id
            GROUP BY n.id
            ORDER BY (history_count * 0.7 + bookshelf_count * 0.3) DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def update_novel(novel_id: int, novel_data: Dict[str, Any]) -> bool:
    """更新小说信息"""
    conn = await get_db_connection()
    try:
        # 构建更新SQL
        fields = []
        values = []
        for key, value in novel_data.items():
            if key not in ['id', 'created_at']:
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return False

        # 添加更新时间
        fields.append("updated_at = ?")
        values.append(datetime.now())

        # 添加ID条件
        values.append(novel_id)

        # 执行更新
        await conn.execute(
            f"UPDATE novels SET {', '.join(fields)} WHERE id = ?",
            values
        )
        await conn.commit()
        return True
    finally:
        await conn.close()


# 章节相关操作
async def create_chapter(chapter: ChapterCreate) -> int:
    """创建章节"""
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            """
            INSERT INTO chapters
            (novel_id, title, chapter_index, content, source_url, is_downloaded)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (chapter.novel_id, chapter.title, chapter.chapter_index,
             chapter.content, chapter.source_url, chapter.is_downloaded)
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def get_chapter(chapter_id: int) -> Optional[Dict]:
    """获取章节详情"""
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            "SELECT * FROM chapters WHERE id = ?", (chapter_id,)
        )
        result = await cursor.fetchone()
        return dict(result) if result else None
    finally:
        await conn.close()


async def get_novel_chapters(novel_id: int) -> List[Dict]:
    """获取小说的所有章节"""
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            "SELECT * FROM chapters WHERE novel_id = ? ORDER BY chapter_index",
            (novel_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def update_chapter_content(chapter_id: int, content: str) -> bool:
    """更新章节内容"""
    conn = await get_db_connection()
    try:
        await conn.execute(
            """
            UPDATE chapters
            SET content = ?, is_downloaded = 1, updated_at = ?
            WHERE id = ?
            """,
            (content, datetime.now(), chapter_id)
        )
        await conn.commit()
        return True
    finally:
        await conn.close()


# 书架相关操作
async def add_to_bookshelf(bookshelf: BookshelfCreate) -> int:
    """添加到书架"""
    conn = await get_db_connection()
    try:
        # 检查是否已存在
        cursor = await conn.execute(
            "SELECT id FROM bookshelf WHERE novel_id = ?",
            (bookshelf.novel_id,)
        )
        existing = await cursor.fetchone()

        if existing:
            # 更新已有记录
            await conn.execute(
                """
                UPDATE bookshelf
                SET last_read_chapter_id = ?, last_read_position = ?, updated_at = ?
                WHERE id = ?
                """,
                (bookshelf.last_read_chapter_id, bookshelf.last_read_position,
                 datetime.now(), existing['id'])
            )
            await conn.commit()
            return existing['id']
        else:
            # 创建新记录
            cursor = await conn.execute(
                """
                INSERT INTO bookshelf
                (novel_id, last_read_chapter_id, last_read_position)
                VALUES (?, ?, ?)
                """,
                (bookshelf.novel_id, bookshelf.last_read_chapter_id, bookshelf.last_read_position)
            )
            await conn.commit()
            return cursor.lastrowid
    finally:
        await conn.close()


async def get_bookshelf(page: int = 1, page_size: int = 10, sort_by: str = "updated_at") -> Tuple[List[Dict], int]:
    """获取书架列表"""
    conn = await get_db_connection()
    try:
        # 验证排序字段
        valid_sort_fields = ["updated_at", "added_at", "title"]
        if sort_by not in valid_sort_fields:
            sort_by = "updated_at"

        # 处理按小说标题排序的特殊情况
        join_clause = "LEFT JOIN novels n ON b.novel_id = n.id"
        order_clause = "ORDER BY b.updated_at DESC"
        if sort_by == "title":
            order_clause = "ORDER BY n.title ASC"
        elif sort_by == "added_at":
            order_clause = "ORDER BY b.added_at DESC"

        # 计算总数
        cursor = await conn.execute("SELECT COUNT(*) as count FROM bookshelf")
        result = await cursor.fetchone()
        total = result['count']

        # 获取分页数据
        cursor = await conn.execute(
            f"""
            SELECT b.*, n.title, n.author, n.cover, n.description, n.source, n.source_url
            FROM bookshelf b
            {join_clause}
            {order_clause}
            LIMIT ? OFFSET ?
            """,
            (page_size, (page - 1) * page_size)
        )
        rows = await cursor.fetchall()

        # 处理结果
        bookshelf_items = []
        for row in rows:
            item = dict(row)
            novel = {
                "id": item["novel_id"],
                "title": item["title"],
                "author": item["author"],
                "cover": item["cover"],
                "description": item["description"],
                "source": item["source"],
                "source_url": item["source_url"]
            }
            item["novel"] = novel
            # 删除重复字段
            for key in list(novel.keys()):
                if key != "id" and key in item:
                    del item[key]
            bookshelf_items.append(item)

        return bookshelf_items, total
    finally:
        await conn.close()


async def remove_from_bookshelf(novel_id: int) -> bool:
    """从书架移除"""
    conn = await get_db_connection()
    try:
        await conn.execute(
            "DELETE FROM bookshelf WHERE novel_id = ?",
            (novel_id,)
        )
        await conn.commit()
        return True
    finally:
        await conn.close()


# 历史记录相关操作
async def add_history(history: HistoryCreate) -> int:
    """添加历史记录"""
    conn = await get_db_connection()
    try:
        # 检查是否已存在该小说的历史记录
        cursor = await conn.execute(
            "SELECT id FROM history WHERE novel_id = ? AND chapter_id = ?",
            (history.novel_id, history.chapter_id)
        )
        existing = await cursor.fetchone()

        if existing:
            # 更新已有记录
            await conn.execute(
                """
                UPDATE history
                SET read_position = ?, read_at = ?
                WHERE id = ?
                """,
                (history.read_position, datetime.now(), existing['id'])
            )
            await conn.commit()
            return existing['id']
        else:
            # 创建新记录
            cursor = await conn.execute(
                """
                INSERT INTO history
                (novel_id, chapter_id, read_position)
                VALUES (?, ?, ?)
                """,
                (history.novel_id, history.chapter_id, history.read_position)
            )
            await conn.commit()
            return cursor.lastrowid
    finally:
        await conn.close()


async def get_history(page: int = 1, page_size: int = 10, sort_by: str = "read_at") -> Tuple[List[Dict], int]:
    """获取历史记录列表"""
    conn = await get_db_connection()
    try:
        # 验证排序字段
        valid_sort_fields = ["read_at", "title"]
        if sort_by not in valid_sort_fields:
            sort_by = "read_at"

        # 处理按小说标题排序的特殊情况
        order_clause = "ORDER BY h.read_at DESC"
        if sort_by == "title":
            order_clause = "ORDER BY n.title ASC"

        # 计算总数
        cursor = await conn.execute(
            """
            SELECT COUNT(DISTINCT h.novel_id) as count
            FROM history h
            """
        )
        result = await cursor.fetchone()
        total = result['count']

        # 获取分页数据 - 每本小说只取最新的一条历史记录
        cursor = await conn.execute(
            f"""
            SELECT h.*, n.title, n.author, n.cover, n.description, n.source, n.source_url,
                   c.title as chapter_title, c.chapter_index
            FROM history h
            JOIN novels n ON h.novel_id = n.id
            JOIN chapters c ON h.chapter_id = c.id
            JOIN (
                SELECT novel_id, MAX(read_at) as latest_read
                FROM history
                GROUP BY novel_id
            ) latest ON h.novel_id = latest.novel_id AND h.read_at = latest.latest_read
            {order_clause}
            LIMIT ? OFFSET ?
            """,
            (page_size, (page - 1) * page_size)
        )
        rows = await cursor.fetchall()

        # 处理结果
        history_items = []
        for row in rows:
            item = dict(row)
            novel = {
                "id": item["novel_id"],
                "title": item["title"],
                "author": item["author"],
                "cover": item["cover"],
                "description": item["description"],
                "source": item["source"],
                "source_url": item["source_url"]
            }
            chapter = {
                "id": item["chapter_id"],
                "title": item["chapter_title"],
                "chapter_index": item["chapter_index"]
            }
            item["novel"] = novel
            item["chapter"] = chapter
            # 删除重复字段
            for key in list(novel.keys()):
                if key != "id" and key in item:
                    del item[key]
            del item["chapter_title"]
            del item["chapter_index"]
            history_items.append(item)

        return history_items, total
    finally:
        await conn.close()


async def delete_history(history_id: int) -> bool:
    """删除历史记录"""
    conn = await get_db_connection()
    try:
        await conn.execute(
            "DELETE FROM history WHERE id = ?",
            (history_id,)
        )
        await conn.commit()
        return True
    finally:
        await conn.close()


async def delete_novel_history(novel_id: int) -> bool:
    """删除小说的所有历史记录"""
    conn = await get_db_connection()
    try:
        await conn.execute(
            "DELETE FROM history WHERE novel_id = ?",
            (novel_id,)
        )
        await conn.commit()
        return True
    finally:
        await conn.close()


async def clear_all_history() -> bool:
    """清空所有历史记录"""
    conn = await get_db_connection()
    try:
        await conn.execute("DELETE FROM history")
        await conn.commit()
        return True
    finally:
        await conn.close()


# 规则相关操作
async def create_rule(rule: RuleCreate) -> int:
    """创建规则"""
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            """
            INSERT INTO rules
            (name, source_url, search_url, cover_rule, title_rule, author_rule,
             description_rule, chapter_list_rule, chapter_content_rule)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (rule.name, rule.source_url, rule.search_url, rule.cover_rule,
             rule.title_rule, rule.author_rule, rule.description_rule,
             rule.chapter_list_rule, rule.chapter_content_rule)
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def get_rule(rule_id: int) -> Optional[Dict]:
    """获取规则详情"""
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            "SELECT * FROM rules WHERE id = ?", (rule_id,)
        )
        result = await cursor.fetchone()
        return dict(result) if result else None
    finally:
        await conn.close()


async def get_rules(page: int = 1, page_size: int = 10, sort_by: str = "updated_at") -> Tuple[List[Dict], int]:
    """获取规则列表"""
    conn = await get_db_connection()
    try:
        # 验证排序字段
        valid_sort_fields = ["updated_at", "created_at", "name"]
        if sort_by not in valid_sort_fields:
            sort_by = "updated_at"

        # 确定排序方向
        direction = "DESC" if sort_by in ["updated_at", "created_at"] else "ASC"

        # 计算总数
        cursor = await conn.execute("SELECT COUNT(*) as count FROM rules")
        result = await cursor.fetchone()
        total = result['count']

        # 获取分页数据
        cursor = await conn.execute(
            f"SELECT * FROM rules ORDER BY {sort_by} {direction} LIMIT ? OFFSET ?",
            (page_size, (page - 1) * page_size)
        )
        rows = await cursor.fetchall()
        rules = [dict(row) for row in rows]

        return rules, total
    finally:
        await conn.close()


async def update_rule(rule_id: int, rule_data: Dict[str, Any]) -> bool:
    """更新规则"""
    conn = await get_db_connection()
    try:
        # 构建更新SQL
        fields = []
        values = []
        for key, value in rule_data.items():
            if key not in ['id', 'created_at', 'updated_at']:
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return False

        # 添加更新时间
        fields.append("updated_at = ?")
        values.append(datetime.now())

        # 添加ID条件
        values.append(rule_id)

        # 执行更新
        await conn.execute(
            f"UPDATE rules SET {', '.join(fields)} WHERE id = ?",
            values
        )
        await conn.commit()
        return True
    finally:
        await conn.close()


async def delete_rule(rule_id: int) -> bool:
    """删除规则"""
    conn = await get_db_connection()
    try:
        await conn.execute(
            "DELETE FROM rules WHERE id = ?",
            (rule_id,)
        )
        await conn.commit()
        return True
    finally:
        await conn.close()


# 设置相关操作
async def get_setting(key: str) -> Optional[str]:
    """获取设置值"""
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,)
        )
        result = await cursor.fetchone()
        return result['value'] if result else None
    finally:
        await conn.close()


async def get_all_settings() -> Dict[str, str]:
    """获取所有设置"""
    conn = await get_db_connection()
    try:
        cursor = await conn.execute("SELECT key, value FROM settings")
        rows = await cursor.fetchall()
        return {row['key']: row['value'] for row in rows}
    finally:
        await conn.close()


async def update_setting(key: str, value: str) -> bool:
    """更新设置"""
    conn = await get_db_connection()
    try:
        # 检查是否存在
        cursor = await conn.execute(
            "SELECT id FROM settings WHERE key = ?",
            (key,)
        )
        existing = await cursor.fetchone()

        if existing:
            # 更新已有设置
            await conn.execute(
                "UPDATE settings SET value = ?, updated_at = ? WHERE key = ?",
                (value, datetime.now(), key)
            )
        else:
            # 创建新设置
            await conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )

        await conn.commit()
        return True
    finally:
        await conn.close()
