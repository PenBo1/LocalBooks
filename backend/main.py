import os
import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 导入自定义日志系统
from utils.logger_manager import app_logger, api_logger, error_logger

# 导入路由模块
from api.novel import router as novel_router
from api.novel_download import router as novel_download_router
from api.bookshelf import router as bookshelf_router
from api.history import router as history_router
from api.rule import router as rule_router
from api.cache import router as cache_router
from api.search_history import router as search_history_router
# 移除settings_router导入，改为使用localStorage

# 导入数据库初始化
from database.init_db import init_db

# 加载环境变量
load_dotenv()

# 配置日志
log_level = os.getenv("LOG_LEVEL", "INFO").lower()

# 创建FastAPI应用
app = FastAPI(
    title="LocalBooks API",
    description="本地小说软件API接口",
    version="1.0.0"
)

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # 记录请求开始
    request_id = f"{id(request)}"
    client_host = request.client.host if request.client else "unknown"
    api_logger.set_context(request_id=request_id, client_ip=client_host)
    
    # 记录请求信息
    api_logger.info(
        f"开始处理请求: {request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        query_params=str(request.query_params),
        client_ip=client_host
    )
    
    # 处理请求
    try:
        response = await call_next(request)
        
        # 记录响应信息
        api_logger.info(
            f"请求处理完成: {request.method} {request.url.path}",
            status_code=response.status_code,
            method=request.method,
            path=request.url.path
        )
        
        return response
    except Exception as e:
        # 记录异常信息
        error_logger.exception(
            f"请求处理异常: {request.method} {request.url.path}",
            exc_info=e,
            method=request.method,
            path=request.url.path
        )
        raise
    finally:
        # 清除上下文
        api_logger.clear_context()

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
app.include_router(novel_download_router, prefix="/api/novel", tags=["小说"])
app.include_router(bookshelf_router, prefix="/api/bookshelf", tags=["书架"])
app.include_router(history_router, prefix="/api/history", tags=["历史"])
app.include_router(rule_router, prefix="/api/rule", tags=["规则"])
app.include_router(cache_router, prefix="/api/cache", tags=["缓存管理"])
app.include_router(search_history_router, prefix="/api/search_history", tags=["搜索历史"])
# 移除settings_router注册，改为使用localStorage


@app.on_event("startup")
async def startup_event():
    """应用启动时执行的操作"""
    app_logger.info("LocalBooks API 服务启动中...")
    
    # 记录环境信息
    env_info = {
        "环境": os.getenv("ENV", "development"),
        "日志级别": log_level,
        "主机": os.getenv("HOST", "127.0.0.1"),
        "端口": os.getenv("PORT", 8000)
    }
    app_logger.info("应用环境配置", **env_info)
    
    # 初始化数据库
    try:
        await init_db()
        app_logger.info("数据库初始化完成")
    except Exception as e:
        error_logger.exception("数据库初始化失败", exc_info=e)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的操作"""
    app_logger.info("LocalBooks API 服务关闭中...")
    app_logger.info("正在清理资源...")
    # 这里可以添加其他资源清理操作
    app_logger.info("LocalBooks API 服务已安全关闭")


@app.get("/", response_model=dict)
async def root():
    """API根路径"""
    app_logger.info("访问API根路径")
    return {
        "message": "欢迎访问 LocalBooks API",
        "author": {
            "name": "PenBo",
            "github": "https://github.com/PenBo1"
        },
        "resources": {
            "documentation": "/docs",
            "repository": "https://github.com/PenBo1/LocalBooks"
        },
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    app_logger.debug("健康检查请求")
    # 可以在这里添加更多的健康检查逻辑
    return {"status": "ok", "timestamp": app_logger._get_extra()["caller"]["lineno"]}


if __name__ == "__main__":
    # 启动服务
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "development") == "development"
    )