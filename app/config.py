"""
アプリケーション設定管理

環境変数を使用してアプリケーションの設定を管理する。
データベースURL、ログレベルなどの設定を含める。
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """アプリケーション設定クラス"""

    # データベース設定
    database_url: str = "postgresql://user:password@localhost:5432/todoapp"
    database_test_url: Optional[str] = "sqlite:///:memory:"
    
    # データベース接続プール設定
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 300

    # アプリケーション設定
    app_name: str = "Todo API Backend"
    app_version: str = "1.0.0"
    app_description: str = """
    A simple Todo application backend API built with FastAPI and PostgreSQL.
    
    ## Features
    - Create, read, update, and delete todo items
    - Set completion status for tasks
    - Add optional end dates for task deadlines
    - Automatic timestamp tracking (created_at, updated_at)
    - Comprehensive validation and error handling
    
    ## Todo Item Fields
    - **title**: Task title (required, max 200 characters)
    - **description**: Task description (optional, max 1000 characters)  
    - **completed**: Completion status (boolean, default: false)
    - **end_date**: Task deadline (optional, ISO 8601 datetime format)
    - **created_at**: Creation timestamp (auto-generated)
    - **updated_at**: Last update timestamp (auto-updated)
    """
    debug: bool = False
    
    # サーバー設定
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # ログ設定
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_date_format: str = "%Y-%m-%d %H:%M:%S"

    # API設定
    api_prefix: str = ""
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # CORS設定
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # セキュリティ設定
    secret_key: str = "your-secret-key-here"  # 本番環境では必ず変更
    
    # ページネーション設定
    default_page_size: int = 100
    max_page_size: int = 1000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def get_database_url(self) -> str:
        """
        データベースURLを取得する
        
        Returns:
            str: データベース接続URL
        """
        return self.database_url
    
    def get_test_database_url(self) -> str:
        """
        テスト用データベースURLを取得する
        
        Returns:
            str: テスト用データベース接続URL
        """
        return self.database_test_url or "sqlite:///:memory:"
    
    def is_development(self) -> bool:
        """
        開発環境かどうかを判定する
        
        Returns:
            bool: 開発環境の場合True
        """
        return self.debug
    
    def is_production(self) -> bool:
        """
        本番環境かどうかを判定する
        
        Returns:
            bool: 本番環境の場合True
        """
        return not self.debug and os.getenv("ENVIRONMENT", "").lower() == "production"


# グローバル設定インスタンス
settings = Settings()
