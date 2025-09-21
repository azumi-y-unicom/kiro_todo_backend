"""
ToDoアイテム検索機能のテスト

条件付き検索機能の包括的なテストを実装する。
"""
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.todo import Todo
from app.schemas.todo import TodoSearchParams
from app.services.todo import TodoService


class TestTodoSearch:
    """ToDoアイテム検索機能のテストクラス"""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, integration_test_client: TestClient):
        """テスト用データのセットアップ"""
        self.client = integration_test_client
        
        # テスト用のToDoアイテムを作成
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        # 完了済み、期限なし
        todo1_data = {
            "title": "Completed Task",
            "description": "This is completed",
            "completed": True,
            "end_date": None
        }
        
        # 未完了、期限切れ
        todo2_data = {
            "title": "Overdue Task",
            "description": "This is overdue",
            "completed": False,
            "end_date": yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        # 未完了、期限あり（未来）
        todo3_data = {
            "title": "Future Task",
            "description": "This has future deadline",
            "completed": False,
            "end_date": tomorrow.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        # 完了済み、期限あり（過去）
        todo4_data = {
            "title": "Completed Overdue Task",
            "description": "This was completed even though overdue",
            "completed": True,
            "end_date": yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        # 未完了、期限なし
        todo5_data = {
            "title": "No Deadline Task",
            "description": "This has no deadline",
            "completed": False,
            "end_date": None
        }
        
        # APIを使用してToDoアイテムを作成
        todos_data = [todo1_data, todo2_data, todo3_data, todo4_data, todo5_data]
        self.created_todos = []
        
        for todo_data in todos_data:
            response = self.client.post("/todos/", json=todo_data)
            assert response.status_code == 201
            self.created_todos.append(response.json())
    
    def test_search_by_completed_true(self):
        """完了済みタスクの検索テスト"""
        response = self.client.get("/todos/search?completed=true")
        
        assert response.status_code == 200
        todos = response.json()
        
        # 完了済みタスクのみが返される
        assert len(todos) == 2
        for todo in todos:
            assert todo["completed"] is True
        
        # 特定のタスクが含まれていることを確認
        titles = [todo["title"] for todo in todos]
        assert "Completed Task" in titles
        assert "Completed Overdue Task" in titles
    
    def test_search_by_completed_false(self):
        """未完了タスクの検索テスト"""
        response = self.client.get("/todos/search?completed=false")
        
        assert response.status_code == 200
        todos = response.json()
        
        # 未完了タスクのみが返される
        assert len(todos) == 3
        for todo in todos:
            assert todo["completed"] is False
        
        # 特定のタスクが含まれていることを確認
        titles = [todo["title"] for todo in todos]
        assert "Overdue Task" in titles
        assert "Future Task" in titles
        assert "No Deadline Task" in titles
    
    def test_search_by_end_date_from(self):
        """期限開始日時での検索テスト"""
        # 今日以降の期限を持つタスクを検索
        now = datetime.now(timezone.utc)
        from_date = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        response = self.client.get(f"/todos/search?end_date_from={from_date}")
        
        assert response.status_code == 200
        todos = response.json()
        
        # 今日以降の期限を持つタスクのみが返される
        assert len(todos) == 1
        assert todos[0]["title"] == "Future Task"
        assert todos[0]["end_date"] is not None
    
    def test_search_by_end_date_to(self):
        """期限終了日時での検索テスト"""
        # 今日以前の期限を持つタスクを検索
        now = datetime.now(timezone.utc)
        to_date = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        response = self.client.get(f"/todos/search?end_date_to={to_date}")
        
        assert response.status_code == 200
        todos = response.json()
        
        # 今日以前の期限を持つタスクが返される
        assert len(todos) == 2
        titles = [todo["title"] for todo in todos]
        assert "Overdue Task" in titles
        assert "Completed Overdue Task" in titles
    
    def test_search_by_date_range(self):
        """期限日時範囲での検索テスト"""
        # 昨日から明日までの範囲で検索
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        from_date = yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')
        to_date = tomorrow.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        response = self.client.get(
            f"/todos/search?end_date_from={from_date}&end_date_to={to_date}"
        )
        
        assert response.status_code == 200
        todos = response.json()
        
        # 指定範囲内の期限を持つタスクが返される
        assert len(todos) == 3
        titles = [todo["title"] for todo in todos]
        assert "Overdue Task" in titles
        assert "Future Task" in titles
        assert "Completed Overdue Task" in titles
    
    def test_search_combined_conditions(self):
        """複数条件の組み合わせ検索テスト"""
        # 未完了かつ期限切れのタスクを検索
        now = datetime.now(timezone.utc)
        to_date = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        response = self.client.get(
            f"/todos/search?completed=false&end_date_to={to_date}"
        )
        
        assert response.status_code == 200
        todos = response.json()
        
        # 未完了かつ期限切れのタスクのみが返される
        assert len(todos) == 1
        assert todos[0]["title"] == "Overdue Task"
        assert todos[0]["completed"] is False
        assert todos[0]["end_date"] is not None
    
    def test_search_no_parameters(self):
        """パラメータなしの検索テスト（全件取得）"""
        response = self.client.get("/todos/search")
        
        assert response.status_code == 200
        todos = response.json()
        
        # すべてのタスクが返される
        assert len(todos) == 5
    
    def test_search_with_pagination(self):
        """ページネーション付き検索テスト"""
        # 最初の2件を取得
        response = self.client.get("/todos/search?limit=2")
        
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 2
        
        # 次の2件を取得
        response = self.client.get("/todos/search?skip=2&limit=2")
        
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 2
        
        # 残りの1件を取得
        response = self.client.get("/todos/search?skip=4&limit=2")
        
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1
    
    def test_search_invalid_date_format(self):
        """無効な日時形式でのバリデーションエラーテスト"""
        response = self.client.get("/todos/search?end_date_from=invalid-date")
        
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert "Input should be a valid datetime" in str(error_detail)
    
    def test_search_invalid_boolean_format(self):
        """無効なboolean値でのバリデーションエラーテスト"""
        response = self.client.get("/todos/search?completed=invalid-bool")
        
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert "Input should be a valid boolean" in str(error_detail)
    
    def test_search_invalid_date_range(self):
        """無効な日時範囲でのバリデーションエラーテスト"""
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        
        # end_date_fromがend_date_toより後の場合
        from_date = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        to_date = yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        response = self.client.get(
            f"/todos/search?end_date_from={from_date}&end_date_to={to_date}"
        )
        
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert "end_date_from must be before or equal to end_date_to" in str(error_detail)
    
    def test_search_invalid_pagination_params(self):
        """無効なページネーションパラメータでのバリデーションエラーテスト"""
        # 負のskip値
        response = self.client.get("/todos/search?skip=-1")
        assert response.status_code == 422
        
        # 0のlimit値
        response = self.client.get("/todos/search?limit=0")
        assert response.status_code == 422
        
        # 上限を超えるlimit値
        response = self.client.get("/todos/search?limit=1001")
        assert response.status_code == 422


class TestTodoSearchService:
    """ToDoサービス層の検索機能テスト"""
    
    @pytest.fixture(autouse=True)
    def setup_service(self, test_db_session: Session):
        """サービスのセットアップ"""
        self.db = test_db_session
        self.service = TodoService(test_db_session)
        
        # テスト用データを作成
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        
        self.test_todos = [
            Todo(title="Test 1", completed=True, end_date=None),
            Todo(title="Test 2", completed=False, end_date=yesterday),
            Todo(title="Test 3", completed=False, end_date=None)
        ]
        
        for todo in self.test_todos:
            self.db.add(todo)
        self.db.commit()
    
    def test_service_search_todos(self):
        """サービス層の検索メソッドテスト"""
        search_params = TodoSearchParams(
            completed=False,
            skip=0,
            limit=10
        )
        
        todos = self.service.search_todos(search_params)
        
        assert len(todos) == 2
        for todo in todos:
            assert todo.completed is False
    
    def test_service_search_validation_error(self):
        """サービス層のバリデーションエラーテスト"""
        from app.services.todo import TodoValidationError
        from pydantic import ValidationError
        
        # 無効な日時範囲（Pydanticレベルでキャッチされる）
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        
        with pytest.raises(ValidationError) as exc_info:
            TodoSearchParams(
                end_date_from=now,
                end_date_to=yesterday,
                skip=0,
                limit=10
            )
        
        assert "end_date_from must be before or equal to end_date_to" in str(exc_info.value)


class TestTodoSearchParams:
    """TodoSearchParamsスキーマのテスト"""
    
    def test_valid_search_params(self):
        """有効な検索パラメータのテスト"""
        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(days=1)
        
        params = TodoSearchParams(
            completed=True,
            end_date_from=now,
            end_date_to=tomorrow,
            skip=0,
            limit=50
        )
        
        assert params.completed is True
        assert params.end_date_from == now
        assert params.end_date_to == tomorrow
        assert params.skip == 0
        assert params.limit == 50
    
    def test_default_values(self):
        """デフォルト値のテスト"""
        params = TodoSearchParams()
        
        assert params.completed is None
        assert params.end_date_from is None
        assert params.end_date_to is None
        assert params.skip == 0
        assert params.limit == 100
    
    def test_date_range_validation(self):
        """日時範囲バリデーションのテスト"""
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        
        # 無効な範囲（from > to）
        with pytest.raises(ValueError) as exc_info:
            TodoSearchParams(
                end_date_from=now,
                end_date_to=yesterday
            )
        
        assert "end_date_from must be before or equal to end_date_to" in str(exc_info.value)
    
    def test_pagination_validation(self):
        """ページネーションバリデーションのテスト"""
        # 負のskip値
        with pytest.raises(ValueError):
            TodoSearchParams(skip=-1)
        
        # 0のlimit値
        with pytest.raises(ValueError):
            TodoSearchParams(limit=0)
        
        # 上限を超えるlimit値
        with pytest.raises(ValueError):
            TodoSearchParams(limit=1001)