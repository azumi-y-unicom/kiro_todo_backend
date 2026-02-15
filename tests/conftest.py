"""
テスト設定ファイル

pytestのフィクスチャとテスト用データベース設定を提供する。
統合テスト用のテストクライアントとデータベース設定も含む。
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os
from fastapi.testclient import TestClient

# テスト環境用の環境変数を設定
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "true"

from app.database import Base, get_db
from app.models.todo import Todo
from app.repositories.todo import TodoRepository
from app.main import app


# テスト用データベースURL（SQLiteインメモリ）
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """
    テスト用データベースエンジンを作成する
    
    Returns:
        Engine: テスト用SQLAlchemyエンジン
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False  # テスト時はSQLログを無効化
    )
    
    # テーブル作成
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # テスト終了後のクリーンアップ
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_engine) -> Generator[Session, None, None]:
    """
    テスト用データベースセッションを作成する
    
    各テスト関数ごとに新しいセッションを作成し、
    テスト終了後にロールバックする。
    
    Args:
        test_engine: テスト用データベースエンジン
        
    Yields:
        Session: テスト用データベースセッション
    """
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    
    # トランザクションを開始
    connection = test_engine.connect()
    transaction = connection.begin()
    
    # セッションをトランザクションにバインド
    session = TestSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def todo_repository(test_db_session: Session) -> TodoRepository:
    """
    テスト用TodoRepositoryインスタンスを作成する
    
    Args:
        test_db_session: テスト用データベースセッション
        
    Returns:
        TodoRepository: テスト用リポジトリインスタンス
    """
    return TodoRepository(test_db_session)


@pytest.fixture
def sample_todo_data():
    """
    テスト用のサンプルToDoデータを提供する
    
    Returns:
        dict: サンプルToDoデータ
    """
    return {
        "title": "テストタスク",
        "description": "これはテスト用のタスクです",
        "completed": False
    }


@pytest.fixture
def sample_todo_data_list():
    """
    テスト用の複数のサンプルToDoデータを提供する
    
    Returns:
        list: サンプルToDoデータのリスト
    """
    return [
        {
            "title": "タスク1",
            "description": "最初のタスク",
            "completed": False
        },
        {
            "title": "タスク2",
            "description": "2番目のタスク",
            "completed": True
        },
        {
            "title": "タスク3",
            "description": "3番目のタスク",
            "completed": False
        }
    ]


@pytest.fixture
def created_todo(todo_repository: TodoRepository, sample_todo_data) -> Todo:
    """
    テスト用に作成済みのToDoアイテムを提供する
    
    Args:
        todo_repository: TodoRepositoryインスタンス
        sample_todo_data: サンプルToDoデータ
        
    Returns:
        Todo: 作成済みのToDoアイテム
    """
    from app.schemas.todo import TodoCreate
    
    todo_create = TodoCreate(**sample_todo_data)
    return todo_repository.create(todo_create)


@pytest.fixture
def created_todos(todo_repository: TodoRepository, sample_todo_data_list) -> list[Todo]:
    """
    テスト用に作成済みの複数のToDoアイテムを提供する
    
    Args:
        todo_repository: TodoRepositoryインスタンス
        sample_todo_data_list: サンプルToDoデータのリスト
        
    Returns:
        list[Todo]: 作成済みのToDoアイテムのリスト
    """
    from app.schemas.todo import TodoCreate
    
    todos = []
    for todo_data in sample_todo_data_list:
        todo_create = TodoCreate(**todo_data)
        todo = todo_repository.create(todo_create)
        todos.append(todo)
    
    return todos


@pytest.fixture
def todo_service(test_db_session: Session):
    """
    テスト用TodoServiceインスタンスを作成する
    
    Args:
        test_db_session: テスト用データベースセッション
        
    Returns:
        TodoService: テスト用サービスインスタンス
    """
    from app.services.todo import TodoService
    return TodoService(test_db_session)


# 統合テスト用のフィクスチャ

@pytest.fixture(scope="session")
def integration_test_engine():
    """
    統合テスト用データベースエンジンを作成する
    
    Returns:
        Engine: 統合テスト用SQLAlchemyエンジン
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # テーブル作成
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # テスト終了後のクリーンアップ
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def integration_test_session_factory(integration_test_engine):
    """
    統合テスト用セッションファクトリを作成する
    
    Args:
        integration_test_engine: 統合テスト用データベースエンジン
        
    Returns:
        sessionmaker: セッションファクトリ
    """
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=integration_test_engine
    )


def override_get_db_for_integration_tests(session_factory):
    """
    統合テスト用のデータベース依存関係オーバーライド関数を作成する
    
    Args:
        session_factory: セッションファクトリ
        
    Returns:
        function: データベースセッションを提供する関数
    """
    def _override_get_db():
        try:
            db = session_factory()
            yield db
        finally:
            db.close()
    
    return _override_get_db


@pytest.fixture(scope="session")
def integration_test_client(integration_test_session_factory):
    """
    統合テスト用FastAPIテストクライアントを作成する
    
    Args:
        integration_test_session_factory: セッションファクトリ
        
    Returns:
        TestClient: FastAPIテストクライアント
    """
    # データベース依存関係をオーバーライド
    app.dependency_overrides[get_db] = override_get_db_for_integration_tests(
        integration_test_session_factory
    )
    
    with TestClient(app) as client:
        yield client
    
    # オーバーライドをクリア
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True, scope="function")
def clean_integration_test_database(integration_test_session_factory):
    """
    各統合テスト前後でデータベースをクリーンアップする
    
    Args:
        integration_test_session_factory: セッションファクトリ
    """
    # テスト前: データをクリーンアップ
    with integration_test_session_factory() as db:
        db.query(Todo).delete()
        db.commit()
    
    yield
    
    # テスト後: データをクリーンアップ
    with integration_test_session_factory() as db:
        db.query(Todo).delete()
        db.commit()


@pytest.fixture
def integration_test_todo_data():
    """
    統合テスト用のサンプルToDoデータを提供する
    
    Returns:
        dict: サンプルToDoデータ
    """
    return {
        "title": "統合テストタスク",
        "description": "これは統合テスト用のタスクです",
        "completed": False
    }


@pytest.fixture
def integration_test_multiple_todo_data():
    """
    統合テスト用の複数のサンプルToDoデータを提供する
    
    Returns:
        list: サンプルToDoデータのリスト
    """
    return [
        {
            "title": "統合テストタスク1",
            "description": "最初の統合テストタスク",
            "completed": False
        },
        {
            "title": "統合テストタスク2",
            "description": "2番目の統合テストタスク",
            "completed": True
        },
        {
            "title": "統合テストタスク3",
            "description": "3番目の統合テストタスク",
            "completed": False
        }
    ]


@pytest.fixture
def created_integration_test_todo(integration_test_client, integration_test_todo_data):
    """
    統合テスト用に作成済みのToDoアイテムを提供する
    
    Args:
        integration_test_client: FastAPIテストクライアント
        integration_test_todo_data: サンプルToDoデータ
        
    Returns:
        dict: 作成済みのToDoアイテムのレスポンスデータ
    """
    response = integration_test_client.post("/todos/", json=integration_test_todo_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def created_integration_test_todos(integration_test_client, integration_test_multiple_todo_data):
    """
    統合テスト用に作成済みの複数のToDoアイテムを提供する
    
    Args:
        integration_test_client: FastAPIテストクライアント
        integration_test_multiple_todo_data: 複数のサンプルToDoデータ
        
    Returns:
        list: 作成済みのToDoアイテムのレスポンスデータのリスト
    """
    created_todos = []
    for todo_data in integration_test_multiple_todo_data:
        response = integration_test_client.post("/todos/", json=todo_data)
        assert response.status_code == 201
        created_todos.append(response.json())
    
    return created_todos


# テストデータベース設定用のヘルパー関数

def setup_test_database():
    """
    テスト用データベースをセットアップする
    
    Returns:
        tuple: (engine, session_factory)
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    Base.metadata.create_all(bind=engine)
    
    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    return engine, session_factory


def teardown_test_database(engine):
    """
    テスト用データベースをクリーンアップする
    
    Args:
        engine: データベースエンジン
    """
    Base.metadata.drop_all(bind=engine)


# パフォーマンステスト用のフィクスチャ

@pytest.fixture
def performance_test_data():
    """
    パフォーマンステスト用の大量データを生成する
    
    Returns:
        list: 大量のToDoデータ
    """
    return [
        {
            "title": f"パフォーマンステストタスク{i+1}",
            "description": f"これは{i+1}番目のパフォーマンステスト用タスクです",
            "completed": i % 2 == 0  # 偶数番目は完了済み
        }
        for i in range(100)
    ]


# エラーテスト用のフィクスチャ

@pytest.fixture
def invalid_todo_data_samples():
    """
    バリデーションエラーテスト用の無効なToDoデータサンプルを提供する
    
    Returns:
        dict: 無効なデータのサンプル集
    """
    return {
        "empty_title": {
            "title": "",
            "description": "空のタイトル"
        },
        "title_too_long": {
            "title": "a" * 201,
            "description": "長すぎるタイトル"
        },
        "description_too_long": {
            "title": "正常なタイトル",
            "description": "a" * 1001
        },
        "missing_title": {
            "description": "タイトルが欠けている"
        },
        "invalid_completed_type": {
            "title": "正常なタイトル",
            "completed": "invalid"
        }
    }