"""
ToDoサービス層のテスト

TodoServiceクラスの単体テストを実装する。
モックを使用して依存関係をテストする。
"""
import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from app.services.todo import (
    TodoService,
    TodoNotFoundError,
    TodoValidationError,
    TodoDatabaseError
)
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.models.todo import Todo


class TestTodoService:
    """TodoServiceクラスのテストケース"""
    
    @pytest.fixture
    def mock_db_session(self):
        """モックデータベースセッション"""
        return Mock()
    
    @pytest.fixture
    def mock_repository(self):
        """モックTodoRepository"""
        return Mock()
    
    @pytest.fixture
    def todo_service(self, mock_db_session):
        """TodoServiceインスタンス"""
        return TodoService(mock_db_session)
    
    @pytest.fixture
    def sample_todo_create(self):
        """サンプルTodoCreateデータ"""
        return TodoCreate(
            title="テストタスク",
            description="これはテスト用のタスクです",
            completed=False
        )
    
    @pytest.fixture
    def sample_todo_update(self):
        """サンプルTodoUpdateデータ"""
        return TodoUpdate(
            title="更新されたタスク",
            description="更新された説明",
            completed=True
        )
    
    @pytest.fixture
    def sample_todo_model(self):
        """サンプルTodoモデル"""
        todo = Todo()
        todo.id = 1
        todo.title = "テストタスク"
        todo.description = "これはテスト用のタスクです"
        todo.completed = False
        todo.created_at = datetime.now()
        todo.updated_at = datetime.now()
        return todo


class TestCreateTodo(TestTodoService):
    """create_todoメソッドのテスト"""
    
    def test_create_todo_success(self, todo_service, mock_repository, sample_todo_create, sample_todo_model):
        """正常なToDoアイテム作成のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.create.return_value = sample_todo_model
        
        # テスト実行
        result = todo_service.create_todo(sample_todo_create)
        
        # 検証
        assert isinstance(result, TodoResponse)
        assert result.id == 1
        assert result.title == "テストタスク"
        assert result.description == "これはテスト用のタスクです"
        assert result.completed is False
        mock_repository.create.assert_called_once_with(sample_todo_create)
    
    def test_create_todo_empty_title(self, todo_service):
        """空のタイトルでのToDoアイテム作成エラーのテスト"""
        # Pydanticレベルでバリデーションエラーが発生することを確認
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            TodoCreate(title="", description="説明", completed=False)
        
        assert "String should have at least 1 character" in str(exc_info.value)
    
    def test_create_todo_whitespace_only_title(self, todo_service):
        """空白のみのタイトルでのToDoアイテム作成エラーのテスト"""
        # Pydanticレベルでバリデーションエラーが発生することを確認
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            TodoCreate(title="   ", description="説明", completed=False)
        
        assert "Title cannot be empty" in str(exc_info.value)
    
    def test_create_todo_title_too_long(self, todo_service):
        """長すぎるタイトルでのToDoアイテム作成エラーのテスト"""
        # Pydanticレベルでバリデーションエラーが発生することを確認
        from pydantic import ValidationError
        
        long_title = "a" * 201
        with pytest.raises(ValidationError) as exc_info:
            TodoCreate(title=long_title, description="説明", completed=False)
        
        assert "String should have at most 200 characters" in str(exc_info.value)
    
    def test_create_todo_description_too_long(self, todo_service):
        """長すぎる説明でのToDoアイテム作成エラーのテスト"""
        # Pydanticレベルでバリデーションエラーが発生することを確認
        from pydantic import ValidationError
        
        long_description = "a" * 1001
        with pytest.raises(ValidationError) as exc_info:
            TodoCreate(title="タイトル", description=long_description, completed=False)
        
        assert "String should have at most 1000 characters" in str(exc_info.value)
    
    def test_create_todo_service_level_validation(self, todo_service, mock_repository):
        """サービスレベルでのバリデーションテスト（空白のみのタイトル）"""
        # Pydanticレベルでバリデーションエラーが発生することを確認
        from pydantic import ValidationError
        
        # 空白のみのタイトルでPydanticレベルのバリデーションをテスト
        with pytest.raises(ValidationError) as exc_info:
            TodoCreate(title="   ", description="説明", completed=False)
        
        assert "Title cannot be empty" in str(exc_info.value)
    
    def test_create_todo_database_error(self, todo_service, mock_repository, sample_todo_create):
        """データベースエラーでのToDoアイテム作成エラーのテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.create.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(TodoDatabaseError) as exc_info:
            todo_service.create_todo(sample_todo_create)
        
        assert "Failed to create todo item" in str(exc_info.value)


class TestGetTodoById(TestTodoService):
    """get_todo_by_idメソッドのテスト"""
    
    def test_get_todo_by_id_success(self, todo_service, mock_repository, sample_todo_model):
        """正常なToDoアイテム取得のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_by_id.return_value = sample_todo_model
        
        # テスト実行
        result = todo_service.get_todo_by_id(1)
        
        # 検証
        assert isinstance(result, TodoResponse)
        assert result.id == 1
        assert result.title == "テストタスク"
        mock_repository.get_by_id.assert_called_once_with(1)
    
    def test_get_todo_by_id_not_found(self, todo_service, mock_repository):
        """存在しないToDoアイテム取得のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(TodoNotFoundError) as exc_info:
            todo_service.get_todo_by_id(999)
        
        assert exc_info.value.todo_id == 999
        assert "Todo item with id 999 not found" in str(exc_info.value)
    
    def test_get_todo_by_id_invalid_id(self, todo_service):
        """無効なIDでのToDoアイテム取得エラーのテスト"""
        with pytest.raises(TodoValidationError) as exc_info:
            todo_service.get_todo_by_id(-1)
        
        assert "Todo ID must be a positive integer" in str(exc_info.value)
    
    def test_get_todo_by_id_database_error(self, todo_service, mock_repository):
        """データベースエラーでのToDoアイテム取得エラーのテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_by_id.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(TodoDatabaseError) as exc_info:
            todo_service.get_todo_by_id(1)
        
        assert "Failed to retrieve todo item 1" in str(exc_info.value)


class TestGetAllTodos(TestTodoService):
    """get_all_todosメソッドのテスト"""
    
    def test_get_all_todos_success(self, todo_service, mock_repository, sample_todo_model):
        """正常な全ToDoアイテム取得のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_all.return_value = [sample_todo_model]
        
        # テスト実行
        result = todo_service.get_all_todos()
        
        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TodoResponse)
        assert result[0].id == 1
        mock_repository.get_all.assert_called_once_with(0, 100)
    
    def test_get_all_todos_with_pagination(self, todo_service, mock_repository):
        """ページネーション付き全ToDoアイテム取得のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_all.return_value = []
        
        # テスト実行
        result = todo_service.get_all_todos(skip=10, limit=20)
        
        # 検証
        assert isinstance(result, list)
        assert len(result) == 0
        mock_repository.get_all.assert_called_once_with(10, 20)
    
    def test_get_all_todos_invalid_skip(self, todo_service):
        """無効なskipパラメータでのエラーのテスト"""
        with pytest.raises(TodoValidationError) as exc_info:
            todo_service.get_all_todos(skip=-1)
        
        assert "Skip parameter must be a non-negative integer" in str(exc_info.value)
    
    def test_get_all_todos_invalid_limit(self, todo_service):
        """無効なlimitパラメータでのエラーのテスト"""
        with pytest.raises(TodoValidationError) as exc_info:
            todo_service.get_all_todos(limit=0)
        
        assert "Limit parameter must be a positive integer" in str(exc_info.value)
    
    def test_get_all_todos_limit_too_large(self, todo_service):
        """大きすぎるlimitパラメータでのエラーのテスト"""
        with pytest.raises(TodoValidationError) as exc_info:
            todo_service.get_all_todos(limit=1001)
        
        assert "Limit parameter cannot exceed 1000" in str(exc_info.value)


class TestUpdateTodo(TestTodoService):
    """update_todoメソッドのテスト"""
    
    def test_update_todo_success(self, todo_service, mock_repository, sample_todo_update, sample_todo_model):
        """正常なToDoアイテム更新のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_by_id.return_value = sample_todo_model
        mock_repository.update.return_value = sample_todo_model
        
        # テスト実行
        result = todo_service.update_todo(1, sample_todo_update)
        
        # 検証
        assert isinstance(result, TodoResponse)
        assert result.id == 1
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.update.assert_called_once_with(1, sample_todo_update)
    
    def test_update_todo_not_found(self, todo_service, mock_repository, sample_todo_update):
        """存在しないToDoアイテム更新のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(TodoNotFoundError) as exc_info:
            todo_service.update_todo(999, sample_todo_update)
        
        assert exc_info.value.todo_id == 999
    
    def test_update_todo_empty_update(self, todo_service):
        """空の更新データでのエラーのテスト"""
        empty_update = TodoUpdate()
        
        with pytest.raises(TodoValidationError) as exc_info:
            todo_service.update_todo(1, empty_update)
        
        assert "At least one field must be provided for update" in str(exc_info.value)
    
    def test_update_todo_invalid_title(self, todo_service):
        """無効なタイトルでの更新エラーのテスト"""
        # Pydanticレベルでバリデーションエラーが発生することを確認
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            TodoUpdate(title="")
        
        assert "String should have at least 1 character" in str(exc_info.value)


class TestDeleteTodo(TestTodoService):
    """delete_todoメソッドのテスト"""
    
    def test_delete_todo_success(self, todo_service, mock_repository, sample_todo_model):
        """正常なToDoアイテム削除のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_by_id.return_value = sample_todo_model
        mock_repository.delete.return_value = True
        
        # テスト実行
        result = todo_service.delete_todo(1)
        
        # 検証
        assert result is True
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.delete.assert_called_once_with(1)
    
    def test_delete_todo_not_found(self, todo_service, mock_repository):
        """存在しないToDoアイテム削除のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(TodoNotFoundError) as exc_info:
            todo_service.delete_todo(999)
        
        assert exc_info.value.todo_id == 999


class TestGetTodosByStatus(TestTodoService):
    """get_todos_by_statusメソッドのテスト"""
    
    def test_get_todos_by_status_completed(self, todo_service, mock_repository, sample_todo_model):
        """完了済みToDoアイテム取得のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_by_completion_status.return_value = [sample_todo_model]
        
        # テスト実行
        result = todo_service.get_todos_by_status(True)
        
        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TodoResponse)
        mock_repository.get_by_completion_status.assert_called_once_with(True)
    
    def test_get_todos_by_status_pending(self, todo_service, mock_repository):
        """未完了ToDoアイテム取得のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.get_by_completion_status.return_value = []
        
        # テスト実行
        result = todo_service.get_todos_by_status(False)
        
        # 検証
        assert isinstance(result, list)
        assert len(result) == 0
        mock_repository.get_by_completion_status.assert_called_once_with(False)


class TestGetTodoStatistics(TestTodoService):
    """get_todo_statisticsメソッドのテスト"""
    
    def test_get_todo_statistics_success(self, todo_service, mock_repository):
        """正常な統計情報取得のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.count_all.return_value = 10
        mock_repository.count_by_completion_status.side_effect = [3, 7]  # completed=True, completed=False
        
        # テスト実行
        result = todo_service.get_todo_statistics()
        
        # 検証
        assert isinstance(result, dict)
        assert result["total"] == 10
        assert result["completed"] == 3
        assert result["pending"] == 7
        assert result["completion_rate"] == 30.0
        
        mock_repository.count_all.assert_called_once()
        assert mock_repository.count_by_completion_status.call_count == 2
    
    def test_get_todo_statistics_empty(self, todo_service, mock_repository):
        """空の統計情報取得のテスト"""
        # モックの設定
        todo_service.repository = mock_repository
        mock_repository.count_all.return_value = 0
        mock_repository.count_by_completion_status.side_effect = [0, 0]
        
        # テスト実行
        result = todo_service.get_todo_statistics()
        
        # 検証
        assert isinstance(result, dict)
        assert result["total"] == 0
        assert result["completed"] == 0
        assert result["pending"] == 0
        assert result["completion_rate"] == 0.0


class TestValidationMethods(TestTodoService):
    """バリデーションメソッドのテスト"""
    
    def test_validate_todo_id_valid(self, todo_service):
        """有効なTodoIDのバリデーションテスト"""
        # 例外が発生しないことを確認
        todo_service._validate_todo_id(1)
        todo_service._validate_todo_id(999)
    
    def test_validate_todo_id_invalid(self, todo_service):
        """無効なTodoIDのバリデーションテスト"""
        with pytest.raises(TodoValidationError):
            todo_service._validate_todo_id(0)
        
        with pytest.raises(TodoValidationError):
            todo_service._validate_todo_id(-1)
    
    def test_validate_pagination_params_valid(self, todo_service):
        """有効なページネーションパラメータのバリデーションテスト"""
        # 例外が発生しないことを確認
        todo_service._validate_pagination_params(0, 10)
        todo_service._validate_pagination_params(100, 1000)
    
    def test_validate_pagination_params_invalid(self, todo_service):
        """無効なページネーションパラメータのバリデーションテスト"""
        with pytest.raises(TodoValidationError):
            todo_service._validate_pagination_params(-1, 10)
        
        with pytest.raises(TodoValidationError):
            todo_service._validate_pagination_params(0, 0)
        
        with pytest.raises(TodoValidationError):
            todo_service._validate_pagination_params(0, 1001)