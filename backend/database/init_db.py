import os
import aiosqlite
from loguru import logger

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "LocalBooks.db")

# 确保数据目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 数据库表创建SQL语句
CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS novels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        cover TEXT,
        description TEXT,
        source TEXT,
        source_url TEXT,
        last_update TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        novel_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        chapter_index INTEGER NOT NULL,
        content TEXT,
        source_url TEXT,
        is_downloaded BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS bookshelf (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        novel_id INTEGER NOT NULL,
        last_read_chapter_id INTEGER,
        last_read_position INTEGER DEFAULT 0,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
        FOREIGN KEY (last_read_chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        novel_id INTEGER NOT NULL,
        chapter_id INTEGER NOT NULL,
        read_position INTEGER DEFAULT 0,
        read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
        FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT NOT NULL,
        search_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        source_url TEXT NOT NULL,
        search_url TEXT NOT NULL,
        search_result_rule TEXT,
        cover_rule TEXT,
        title_rule TEXT NOT NULL,
        author_rule TEXT,
        description_rule TEXT,
        chapter_list_rule TEXT NOT NULL,
        chapter_content_rule TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL UNIQUE,
        value TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_novels_title ON novels(title)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chapters_novel_id ON chapters(novel_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_bookshelf_novel_id ON bookshelf(novel_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_history_novel_id ON history(novel_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_search_history_keyword ON search_history(keyword)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_rules_name ON rules(name)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key)
    """
]

# 默认设置
DEFAULT_SETTINGS = [
    ("theme", "light"),  # 默认主题：浅色
    ("font_size", "16"),  # 默认字体大小
    ("font_family", "Microsoft YaHei"),  # 默认字体
    ("line_height", "1.5"),  # 默认行高
    ("cache_limit", "500"),  # 默认缓存限制（MB）
    ("log_level", "INFO"),  # 默认日志级别
]


async def get_db_connection():
    """获取数据库连接"""
    conn = await aiosqlite.connect(DB_PATH)
    # 启用外键约束
    await conn.execute("PRAGMA foreign_keys = ON")
    # 设置行工厂为字典
    conn.row_factory = aiosqlite.Row
    return conn


async def init_db():
    """初始化数据库"""
    try:
        # 连接数据库
        conn = await get_db_connection()

        # 创建表
        for create_table_sql in CREATE_TABLES:
            await conn.execute(create_table_sql)

        # 提交事务
        await conn.commit()

        # 检查是否需要插入默认设置
        cursor = await conn.execute("SELECT COUNT(*) as count FROM settings")
        result = await cursor.fetchone()
        if result['count'] == 0:
            # 插入默认设置
            for key, value in DEFAULT_SETTINGS:
                await conn.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?)",
                    (key, value)
                )
            await conn.commit()
            logger.info("已插入默认设置")

        # 关闭连接
        await conn.close()

        logger.info(f"数据库初始化成功: {DB_PATH}")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise
