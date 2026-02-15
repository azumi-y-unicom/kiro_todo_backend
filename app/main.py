"""
FastAPIメインアプリケーション

ToDoアプリケーションのバックエンドAPIのエントリーポイント。
ルーターの登録、ミドルウェア設定、例外ハンドラーの設定を行う。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import create_tables
from app.routers import todo, health
from app.exceptions import register_exception_handlers


# ログ設定
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format,
    datefmt=settings.log_date_format
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクル管理
    
    起動時にデータベーステーブルを作成し、
    終了時にクリーンアップを行う。
    """
    # 起動時の処理
    logger.info("Starting Todo API Backend application")
    try:
        create_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # 終了時の処理
    logger.info("Shutting down Todo API Backend application")


# FastAPIアプリケーションの作成
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# 例外ハンドラーの登録
register_exception_handlers(app)

# ルーターの登録
app.include_router(health.router)
app.include_router(todo.router)

# ルートエンドポイント
@app.get("/", tags=["root"])
async def root():
    """
    ルートエンドポイント
    
    Returns:
        dict: アプリケーション情報
    """
    return {
        "message": "Welcome to Todo API Backend",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on http://{settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload or settings.debug,
        log_level=settings.log_level.lower()
    )