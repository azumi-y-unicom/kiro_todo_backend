"""
ヘルスチェック用エンドポイント

アプリケーションとデータベースの状態を確認するためのエンドポイント。
Docker Composeのヘルスチェックで使用される。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
import logging

from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    アプリケーションのヘルスチェック
    
    データベース接続とアプリケーションの基本的な動作を確認する。
    Docker Composeのヘルスチェックで使用される。
    
    Returns:
        dict: ヘルスチェック結果
    """
    try:
        # データベース接続テスト
        db.execute(text("SELECT 1"))
        
        # 基本的な情報を返す
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "service": "todo-api-backend"
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "database": "disconnected",
                "error": str(e),
                "service": "todo-api-backend"
            }
        )


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    詳細なヘルスチェック
    
    より詳細なシステム情報を提供する。
    監視システムやデバッグ用途で使用。
    
    Returns:
        dict: 詳細なヘルスチェック結果
    """
    try:
        # データベース接続とバージョン確認
        db_version = db.execute(text("SELECT version()")).scalar()
        
        # テーブル存在確認
        tables_exist = db.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'todos'
        """)).scalar()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "todo-api-backend",
            "database": {
                "status": "connected",
                "version": db_version,
                "tables_initialized": tables_exist > 0
            },
            "environment": {
                "python_version": "3.12",
                "fastapi_version": "0.115.6"
            }
        }
    
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "database": {"status": "disconnected"},
                "error": str(e),
                "service": "todo-api-backend"
            }
        )