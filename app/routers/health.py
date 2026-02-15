"""
ヘルスチェックエンドポイント

アプリケーションとデータベースの状態を確認するAPIエンドポイントを提供する。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
import logging

from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["health"]
)


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンススキーマ"""
    status: str
    database: str
    message: str


@router.get("/", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)):
    """
    アプリケーションとデータベースの状態を確認する
    
    Returns:
        HealthResponse: アプリケーションとデータベースの状態
        
    Raises:
        HTTPException: データベース接続エラーの場合
    """
    try:
        # データベース接続状態の確認
        db.execute(text("SELECT 1"))
        db_status = "healthy"
        logger.debug("Database connection check successful")
        
        return HealthResponse(
            status="healthy",
            database=db_status,
            message="Application is running normally"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "unhealthy",
                "message": "Database connection failed",
                "error": str(e)
            }
        )