"""
データベース接続設定

SQLAlchemyを使用したPostgreSQLデータベースへの接続設定を管理する。
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemyエンジンの作成
def create_database_engine():
    """データベースエンジンを作成する"""
    database_url = settings.get_database_url()
    
    if database_url.startswith("sqlite"):
        # SQLite用の設定
        return create_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=settings.debug
        )
    else:
        # PostgreSQL用の設定
        return create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_recycle=settings.database_pool_recycle,
            echo=settings.debug
        )

engine = create_database_engine()

# セッションファクトリーの作成
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ベースクラスの作成
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションを取得する依存関数
    
    FastAPIの依存性注入で使用される。
    セッションの自動クローズを保証する。
    
    Yields:
        Session: SQLAlchemyセッション
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """
    データベーステーブルを作成する
    
    注意: 本番環境ではAlembicマイグレーションを使用することを推奨。
    この関数は開発・テスト環境でのみ使用する。
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        logger.warning("create_tables() is deprecated. Use Alembic migrations instead.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def get_test_db_engine():
    """
    テスト用データベースエンジンを取得する
    
    Returns:
        Engine: テスト用SQLAlchemyエンジン
    """
    test_url = settings.get_test_database_url()
    return create_engine(
        test_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False} if "sqlite" in test_url else {},
        echo=settings.debug
    )