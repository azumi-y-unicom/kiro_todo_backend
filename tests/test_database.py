"""
テストデータベース設定とユーティリティ

テスト用データベースの設定と管理機能を提供する。
"""
import os
import tempfile
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Generator, Optional

from app.database import Base
from app.models.todo import Todo


class TestDatabaseManager:
    """テストデータベース管理クラス"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        テストデータベースマネージャーを初期化する
        
        Args:
            database_url: データベースURL（指定しない場合はインメモリSQLite）
        """
        self.database_url = database_url or "sqlite:///:memory:"
        self.engine = None
        self.session_factory = None
        self._setup_engine()
    
    def _setup_engine(self):
        """データベースエンジンをセットアップする"""
        if self.database_url.startswith("sqlite"):
            # SQLite用の設定
            self.engine = create_engine(
                self.database_url,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
                echo=False
            )
            
            # SQLiteでFOREIGN KEYを有効化
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        else:
            # PostgreSQL用の設定
            self.engine = create_engine(
                self.database_url,
                echo=False
            )
        
        self.session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """テーブルを作成する"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """テーブルを削除する"""
        Base.metadata.drop_all(bind=self.engine)
    
    def recreate_tables(self):
        """テーブルを再作成する"""
        self.drop_tables()
        self.create_tables()
    
    @contextmanager
    def get_session(self) -> Generator:
        """
        データベースセッションを取得する
        
        Yields:
            Session: データベースセッション
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def clear_all_data(self):
        """全てのデータをクリアする"""
        with self.get_session() as session:
            # 外部キー制約を考慮してテーブルの順序で削除
            session.query(Todo).delete()
            session.commit()
    
    def insert_test_data(self, test_data: list):
        """
        テストデータを挿入する
        
        Args:
            test_data: 挿入するテストデータのリスト
        """
        with self.get_session() as session:
            for data in test_data:
                if isinstance(data, dict):
                    # 辞書形式のデータからTodoオブジェクトを作成
                    todo = Todo(**data)
                    session.add(todo)
                else:
                    # 既にモデルオブジェクトの場合
                    session.add(data)
            session.commit()
    
    def get_all_todos(self) -> list:
        """
        全てのToDoアイテムを取得する
        
        Returns:
            list: ToDoアイテムのリスト
        """
        with self.get_session() as session:
            return session.query(Todo).all()
    
    def count_todos(self) -> int:
        """
        ToDoアイテムの総数を取得する
        
        Returns:
            int: ToDoアイテムの総数
        """
        with self.get_session() as session:
            return session.query(Todo).count()
    
    def close(self):
        """データベース接続を閉じる"""
        if self.engine:
            self.engine.dispose()


class TestDataFactory:
    """テストデータファクトリクラス"""
    
    @staticmethod
    def create_todo_data(
        title: str = "テストタスク",
        description: Optional[str] = "テスト用の説明",
        completed: bool = False
    ) -> dict:
        """
        ToDoデータを作成する
        
        Args:
            title: タイトル
            description: 説明
            completed: 完了状態
            
        Returns:
            dict: ToDoデータ
        """
        return {
            "title": title,
            "description": description,
            "completed": completed
        }
    
    @staticmethod
    def create_multiple_todo_data(count: int = 3) -> list:
        """
        複数のToDoデータを作成する
        
        Args:
            count: 作成するデータの数
            
        Returns:
            list: ToDoデータのリスト
        """
        return [
            TestDataFactory.create_todo_data(
                title=f"テストタスク{i+1}",
                description=f"これは{i+1}番目のテストタスクです",
                completed=i % 2 == 0
            )
            for i in range(count)
        ]
    
    @staticmethod
    def create_invalid_todo_data() -> dict:
        """
        バリデーションエラー用の無効なToDoデータを作成する
        
        Returns:
            dict: 無効なToDoデータのサンプル
        """
        return {
            "empty_title": {"title": "", "description": "空のタイトル"},
            "title_too_long": {"title": "a" * 201, "description": "長すぎるタイトル"},
            "description_too_long": {"title": "正常なタイトル", "description": "a" * 1001},
            "missing_title": {"description": "タイトルが欠けている"},
        }
    
    @staticmethod
    def create_performance_test_data(count: int = 100) -> list:
        """
        パフォーマンステスト用の大量データを作成する
        
        Args:
            count: 作成するデータの数
            
        Returns:
            list: 大量のToDoデータ
        """
        return [
            TestDataFactory.create_todo_data(
                title=f"パフォーマンステストタスク{i+1}",
                description=f"これは{i+1}番目のパフォーマンステスト用タスクです",
                completed=i % 3 == 0  # 3つに1つは完了済み
            )
            for i in range(count)
        ]


# テスト用のデータベース設定関数

def get_test_database_url() -> str:
    """
    テスト用データベースURLを取得する
    
    Returns:
        str: テスト用データベースURL
    """
    # 環境変数からテスト用データベースURLを取得
    test_db_url = os.getenv("TEST_DATABASE_URL")
    
    if test_db_url:
        return test_db_url
    
    # デフォルトはインメモリSQLite
    return "sqlite:///:memory:"


def create_temporary_database() -> str:
    """
    一時的なファイルベースのSQLiteデータベースを作成する
    
    Returns:
        str: 一時データベースファイルのパス
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    return f"sqlite:///{temp_file.name}"


@contextmanager
def temporary_test_database():
    """
    一時的なテストデータベースのコンテキストマネージャー
    
    Yields:
        TestDatabaseManager: テストデータベースマネージャー
    """
    temp_db_path = create_temporary_database()
    db_manager = TestDatabaseManager(temp_db_path)
    
    try:
        db_manager.create_tables()
        yield db_manager
    finally:
        db_manager.close()
        # 一時ファイルを削除
        if temp_db_path.startswith("sqlite:///"):
            file_path = temp_db_path.replace("sqlite:///", "")
            if os.path.exists(file_path):
                os.unlink(file_path)


# テスト用のアサーション関数

def assert_todo_data_equal(actual: dict, expected: dict, ignore_fields: Optional[list] = None):
    """
    ToDoデータが期待値と一致することをアサートする
    
    Args:
        actual: 実際のデータ
        expected: 期待されるデータ
        ignore_fields: 比較から除外するフィールドのリスト
    """
    ignore_fields = ignore_fields or ["id", "created_at", "updated_at"]
    
    for key, value in expected.items():
        if key not in ignore_fields:
            assert key in actual, f"Field '{key}' is missing in actual data"
            assert actual[key] == value, f"Field '{key}': expected {value}, got {actual[key]}"


def assert_todo_list_equal(actual: list, expected: list, ignore_fields: Optional[list] = None):
    """
    ToDoリストが期待値と一致することをアサートする
    
    Args:
        actual: 実際のリスト
        expected: 期待されるリスト
        ignore_fields: 比較から除外するフィールドのリスト
    """
    assert len(actual) == len(expected), f"List length mismatch: expected {len(expected)}, got {len(actual)}"
    
    for i, (actual_item, expected_item) in enumerate(zip(actual, expected)):
        try:
            assert_todo_data_equal(actual_item, expected_item, ignore_fields)
        except AssertionError as e:
            raise AssertionError(f"Item at index {i}: {e}")


# テスト用のモック関数

def mock_database_error():
    """データベースエラーをモックする"""
    from sqlalchemy.exc import SQLAlchemyError
    raise SQLAlchemyError("Mocked database error")


def mock_connection_error():
    """接続エラーをモックする"""
    from sqlalchemy.exc import OperationalError
    raise OperationalError("Mocked connection error", None, None)