"""
ToDoアプリケーションのend_date機能テスト

end_dateフィールドに関連する機能のテストを実装する。
"""
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models.todo import Todo


# テスト用データベース設定
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
    echo=False
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """テスト用データベースセッションを提供する"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


# データベース依存関係をオーバーライド
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def test_client():
    """テスト用FastAPIクライアントを作成する"""
    Base.metadata.create_all(bind=test_engine)
    
    with TestClient(app) as client:
        yield client
    
    # テスト後のクリーンアップ
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_database():
    """各テスト前にデータベースをクリーンアップする"""
    # テスト前のクリーンアップ
    with TestSessionLocal() as db:
        db.query(Todo).delete()
        db.commit()
    
    yield
    
    # テスト後のクリーンアップ
    with TestSessionLocal() as db:
        db.query(Todo).delete()
        db.commit()


class TestTodoEndDate:
    """ToDoアイテムのend_date機能テスト"""
    
    def test_create_todo_with_end_date(self, test_client):
        """end_dateを指定してToDoアイテムを作成するテスト"""
        future_date = datetime.now(timezone.utc) + timedelta(days=7)
        
        todo_data = {
            "title": "期限付きタスク",
            "description": "1週間後が期限のタスク",
            "completed": False,
            "end_date": future_date.isoformat()
        }
        
        response = test_client.post("/todos/", json=todo_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "期限付きタスク"
        assert data["end_date"] is not None
        # ISO形式の日時文字列を比較
        assert data["end_date"].startswith(future_date.strftime("%Y-%m-%d"))
    
    def test_create_todo_without_end_date(self, test_client):
        """end_dateを指定せずにToDoアイテムを作成するテスト"""
        todo_data = {
            "title": "期限なしタスク",
            "description": "期限のないタスク",
            "completed": False
        }
        
        response = test_client.post("/todos/", json=todo_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "期限なしタスク"
        assert data["end_date"] is None
    
    def test_update_todo_add_end_date(self, test_client):
        """既存のToDoアイテムにend_dateを追加するテスト"""
        # まずToDoアイテムを作成
        todo_data = {
            "title": "後で期限を追加するタスク",
            "description": "最初は期限なし",
            "completed": False
        }
        
        create_response = test_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        todo_id = create_response.json()["id"]
        
        # end_dateを追加
        future_date = datetime.now(timezone.utc) + timedelta(days=3)
        update_data = {
            "end_date": future_date.isoformat()
        }
        
        update_response = test_client.put(f"/todos/{todo_id}", json=update_data)
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["end_date"] is not None
        assert data["end_date"].startswith(future_date.strftime("%Y-%m-%d"))
    
    def test_update_todo_remove_end_date(self, test_client):
        """ToDoアイテムからend_dateを削除するテスト"""
        # end_date付きのToDoアイテムを作成
        future_date = datetime.now(timezone.utc) + timedelta(days=5)
        todo_data = {
            "title": "期限を削除するタスク",
            "description": "後で期限を削除する",
            "completed": False,
            "end_date": future_date.isoformat()
        }
        
        create_response = test_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        todo_id = create_response.json()["id"]
        
        # end_dateを削除（nullに設定）
        update_data = {
            "end_date": None
        }
        
        update_response = test_client.put(f"/todos/{todo_id}", json=update_data)
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["end_date"] is None
    
    def test_get_todo_with_end_date(self, test_client):
        """end_date付きのToDoアイテムを取得するテスト"""
        future_date = datetime.now(timezone.utc) + timedelta(days=2)
        todo_data = {
            "title": "取得テスト用タスク",
            "description": "end_date付きの取得テスト",
            "completed": False,
            "end_date": future_date.isoformat()
        }
        
        create_response = test_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        todo_id = create_response.json()["id"]
        
        # ToDoアイテムを取得
        get_response = test_client.get(f"/todos/{todo_id}")
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["title"] == "取得テスト用タスク"
        assert data["end_date"] is not None
        assert data["end_date"].startswith(future_date.strftime("%Y-%m-%d"))


class TestTodoEndDateValidation:
    """ToDoアイテムのend_dateバリデーションテスト"""
    
    def test_create_todo_with_past_end_date(self, test_client):
        """過去の日付をend_dateに設定してToDoアイテムを作成するテスト"""
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        
        todo_data = {
            "title": "過去の期限のタスク",
            "description": "過去の日付が期限",
            "completed": False,
            "end_date": past_date.isoformat()
        }
        
        # 過去の日付でも作成は可能（ビジネスロジックで制御）
        response = test_client.post("/todos/", json=todo_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["end_date"] is not None
    
    def test_create_todo_with_invalid_end_date_format(self, test_client):
        """無効な日付形式でToDoアイテムを作成するテスト"""
        todo_data = {
            "title": "無効な日付形式のタスク",
            "description": "無効な日付形式",
            "completed": False,
            "end_date": "invalid-date-format"
        }
        
        response = test_client.post("/todos/", json=todo_data)
        
        # バリデーションエラーが発生することを確認
        assert response.status_code == 422


class TestTodoEndDateIntegration:
    """ToDoアイテムのend_date統合テスト"""
    
    def test_todo_workflow_with_end_date(self, test_client):
        """end_dateを含むToDoアイテムの完全なワークフローテスト"""
        # 1. end_date付きのToDoアイテムを作成
        future_date = datetime.now(timezone.utc) + timedelta(days=10)
        todo_data = {
            "title": "統合テスト用タスク",
            "description": "完全なワークフローのテスト",
            "completed": False,
            "end_date": future_date.isoformat()
        }
        
        create_response = test_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        todo_id = create_response.json()["id"]
        
        # 2. ToDoアイテムを取得して確認
        get_response = test_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["completed"] is False
        assert data["end_date"] is not None
        
        # 3. ToDoアイテムを完了状態に更新
        update_data = {
            "completed": True
        }
        
        update_response = test_client.put(f"/todos/{todo_id}", json=update_data)
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["completed"] is True
        assert updated_data["end_date"] is not None  # end_dateは保持される
        
        # 4. 全ToDoアイテムリストで確認
        list_response = test_client.get("/todos/")
        assert list_response.status_code == 200
        todos = list_response.json()
        assert len(todos) == 1
        assert todos[0]["id"] == todo_id
        assert todos[0]["completed"] is True
        assert todos[0]["end_date"] is not None
        
        # 5. ToDoアイテムを削除
        delete_response = test_client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 204
        
        # 6. 削除確認
        get_deleted_response = test_client.get(f"/todos/{todo_id}")
        assert get_deleted_response.status_code == 404