import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from dotenv import load_dotenv

# 导入路由模块
from api.novel import router as novel_router
from api.bookshelf import router as bookshelf_router
from api.history import router as history_router
from api.rule import router as rule_router
from api.settings import router as settings_router

# 导入数据库初始化
from database.init_db import init_db

# 加载环境变量
load_dotenv()

# 配置日志
log_level = os.getenv("LOG_LEVEL", "INFO")
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level=log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# 创建FastAPI应用
app = FastAPI(
    title="LocalNovel API",
    description="本地小说软件API接口",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(novel_router, prefix="/api/novel", tags=["小说"])
app.include_router(bookshelf_router, prefix="/api/bookshelf", tags=["书架"])
app.include_router(history_router, prefix="/api/history", tags=["历史"])
app.include_router(rule_router, prefix="/api/rule", tags=["规则"])
app.include_router(settings_router, prefix="/api/settings", tags=["设置"])


@app.on_event("startup")
async def startup_event():
    """应用启动时执行的操作"""
    logger.info("LocalNovel API 服务启动中...")
    # 初始化数据库
    await init_db()
    logger.info("数据库初始化完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的操作"""
    logger.info("LocalNovel API 服务关闭中...")


@app.get("/")
async def root():
    """API根路径"""
    return {"message": "欢迎使用 LocalNovel API"}


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}


if __name__ == "__main__":
    # 启动服务
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "development") == "development"
    )