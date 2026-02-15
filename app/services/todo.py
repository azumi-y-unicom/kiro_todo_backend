"""
ToDoサービス

ToDoアイテムのビジネスロジック層を実装する。
データバリデーション、エラーハンドリング、ビジネスルールを管理する。
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoSearchParams
from app.repositories.todo import TodoRepository

logger = logging.getLogger(__name__)


class TodoNotFoundError(Exception):
    """ToDoアイテムが見つからない場合の例外"""
    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        super().__init__(f"Todo item with id {todo_id} not found")


class TodoValidationError(Exception):
    """ToDoアイテムのバリデーションエラー"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class TodoDatabaseError(Exception):
    """データベース操作エラー"""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class TodoService:
    """
    ToDoアイテムのビジネスロジックを管理するサービスクラス
    
    リポジトリ層を使用してデータアクセスを行い、
    ビジネスルールとバリデーションを適用する。
    """
    
    def __init__(self, db: Session):
        """
        サービスを初期化する
        
        Args:
            db (Session): SQLAlchemyデータベースセッション
        """
        self.repository = TodoRepository(db)
    
    def create_todo(self, todo_data: TodoCreate) -> TodoResponse:
        """
        新しいToDoアイテムを作成する
        
        Args:
            todo_data (TodoCreate): 作成するToDoアイテムのデータ
            
        Returns:
            TodoResponse: 作成されたToDoアイテム
            
        Raises:
            TodoValidationError: バリデーションエラー
            TodoDatabaseError: データベース操作エラー
        """
        try:
            # ビジネスルールのバリデーション
            self._validate_todo_create(todo_data)
            
            # リポジトリを使用してデータを作成
            db_todo = self.repository.create(todo_data)
            
            logger.info(f"Successfully created todo item: {db_todo.id}")
            return TodoResponse.model_validate(db_todo)
            
        except TodoValidationError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while creating todo: {e}")
            raise TodoDatabaseError("Failed to create todo item", e)
        except Exception as e:
            logger.error(f"Unexpected error while creating todo: {e}")
            raise TodoDatabaseError("Unexpected error occurred while creating todo item", e)
    
    def get_todo_by_id(self, todo_id: int) -> TodoResponse:
        """
        IDでToDoアイテムを取得する
        
        Args:
            todo_id (int): 取得するToDoアイテムのID
            
        Returns:
            TodoResponse: 見つかったToDoアイテム
            
        Raises:
            TodoNotFoundError: ToDoアイテムが見つからない場合
            TodoDatabaseError: データベース操作エラー
        """
        try:
            # IDのバリデーション
            self._validate_todo_id(todo_id)
            
            db_todo = self.repository.get_by_id(todo_id)
            if not db_todo:
                logger.warning(f"Todo item not found: {todo_id}")
                raise TodoNotFoundError(todo_id)
            
            logger.debug(f"Successfully retrieved todo item: {todo_id}")
            return TodoResponse.model_validate(db_todo)
            
        except (TodoNotFoundError, TodoValidationError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting todo {todo_id}: {e}")
            raise TodoDatabaseError(f"Failed to retrieve todo item {todo_id}", e)
        except Exception as e:
            logger.error(f"Unexpected error while getting todo {todo_id}: {e}")
            raise TodoDatabaseError(f"Unexpected error occurred while retrieving todo item {todo_id}", e)
    
    def get_all_todos(self, skip: int = 0, limit: int = 100) -> List[TodoResponse]:
        """
        すべてのToDoアイテムを取得する
        
        Args:
            skip (int): スキップする件数（ページネーション用）
            limit (int): 取得する最大件数
            
        Returns:
            List[TodoResponse]: ToDoアイテムのリスト
            
        Raises:
            TodoValidationError: パラメータのバリデーションエラー
            TodoDatabaseError: データベース操作エラー
        """
        try:
            # パラメータのバリデーション
            self._validate_pagination_params(skip, limit)
            
            db_todos = self.repository.get_all(skip, limit)
            
            logger.debug(f"Successfully retrieved {len(db_todos)} todo items")
            return [TodoResponse.model_validate(todo) for todo in db_todos]
            
        except TodoValidationError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting all todos: {e}")
            raise TodoDatabaseError("Failed to retrieve todo items", e)
        except Exception as e:
            logger.error(f"Unexpected error while getting all todos: {e}")
            raise TodoDatabaseError("Unexpected error occurred while retrieving todo items", e)
    
    def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> TodoResponse:
        """
        ToDoアイテムを更新する
        
        Args:
            todo_id (int): 更新するToDoアイテムのID
            todo_data (TodoUpdate): 更新データ
            
        Returns:
            TodoResponse: 更新されたToDoアイテム
            
        Raises:
            TodoNotFoundError: ToDoアイテムが見つからない場合
            TodoValidationError: バリデーションエラー
            TodoDatabaseError: データベース操作エラー
        """
        try:
            # IDのバリデーション
            self._validate_todo_id(todo_id)
            
            # 更新データのバリデーション
            self._validate_todo_update(todo_data)
            
            # 更新前にアイテムの存在確認
            existing_todo = self.repository.get_by_id(todo_id)
            if not existing_todo:
                logger.warning(f"Todo item not found for update: {todo_id}")
                raise TodoNotFoundError(todo_id)
            
            # リポジトリを使用してデータを更新
            updated_todo = self.repository.update(todo_id, todo_data)
            
            logger.info(f"Successfully updated todo item: {todo_id}")
            return TodoResponse.model_validate(updated_todo)
            
        except (TodoNotFoundError, TodoValidationError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while updating todo {todo_id}: {e}")
            raise TodoDatabaseError(f"Failed to update todo item {todo_id}", e)
        except Exception as e:
            logger.error(f"Unexpected error while updating todo {todo_id}: {e}")
            raise TodoDatabaseError(f"Unexpected error occurred while updating todo item {todo_id}", e)
    
    def delete_todo(self, todo_id: int) -> bool:
        """
        ToDoアイテムを削除する
        
        Args:
            todo_id (int): 削除するToDoアイテムのID
            
        Returns:
            bool: 削除が成功した場合True
            
        Raises:
            TodoNotFoundError: ToDoアイテムが見つからない場合
            TodoValidationError: バリデーションエラー
            TodoDatabaseError: データベース操作エラー
        """
        try:
            # IDのバリデーション
            self._validate_todo_id(todo_id)
            
            # 削除前にアイテムの存在確認
            existing_todo = self.repository.get_by_id(todo_id)
            if not existing_todo:
                logger.warning(f"Todo item not found for deletion: {todo_id}")
                raise TodoNotFoundError(todo_id)
            
            # リポジトリを使用してデータを削除
            success = self.repository.delete(todo_id)
            
            if success:
                logger.info(f"Successfully deleted todo item: {todo_id}")
            
            return success
            
        except TodoNotFoundError:
            raise
        except TodoValidationError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting todo {todo_id}: {e}")
            raise TodoDatabaseError(f"Failed to delete todo item {todo_id}", e)
        except Exception as e:
            logger.error(f"Unexpected error while deleting todo {todo_id}: {e}")
            raise TodoDatabaseError(f"Unexpected error occurred while deleting todo item {todo_id}", e)
    
    def get_todos_by_status(self, completed: bool) -> List[TodoResponse]:
        """
        完了状態でToDoアイテムを取得する
        
        Args:
            completed (bool): 完了状態（True: 完了済み、False: 未完了）
            
        Returns:
            List[TodoResponse]: 指定された完了状態のToDoアイテムのリスト
            
        Raises:
            TodoDatabaseError: データベース操作エラー
        """
        try:
            db_todos = self.repository.get_by_completion_status(completed)
            
            logger.debug(f"Successfully retrieved {len(db_todos)} todo items with completed={completed}")
            return [TodoResponse.model_validate(todo) for todo in db_todos]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting todos by status: {e}")
            raise TodoDatabaseError("Failed to retrieve todo items by status", e)
        except Exception as e:
            logger.error(f"Unexpected error while getting todos by status: {e}")
            raise TodoDatabaseError("Unexpected error occurred while retrieving todo items by status", e)
    
    def get_todo_statistics(self) -> dict:
        """
        ToDoアイテムの統計情報を取得する
        
        Returns:
            dict: 統計情報（総数、完了数、未完了数）
            
        Raises:
            TodoDatabaseError: データベース操作エラー
        """
        try:
            total_count = self.repository.count_all()
            completed_count = self.repository.count_by_completion_status(True)
            pending_count = self.repository.count_by_completion_status(False)
            
            statistics = {
                "total": total_count,
                "completed": completed_count,
                "pending": pending_count,
                "completion_rate": round((completed_count / total_count * 100), 2) if total_count > 0 else 0.0
            }
            
            logger.debug(f"Retrieved todo statistics: {statistics}")
            return statistics
            
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting todo statistics: {e}")
            raise TodoDatabaseError("Failed to retrieve todo statistics", e)
        except Exception as e:
            logger.error(f"Unexpected error while getting todo statistics: {e}")
            raise TodoDatabaseError("Unexpected error occurred while retrieving todo statistics", e)
    
    def search_todos(self, search_params: TodoSearchParams) -> List[TodoResponse]:
        """
        条件に基づいてToDoアイテムを検索する
        
        Args:
            search_params (TodoSearchParams): 検索条件パラメータ
            
        Returns:
            List[TodoResponse]: 検索条件に一致するToDoアイテムのリスト
            
        Raises:
            TodoValidationError: 検索パラメータのバリデーションエラー
            TodoDatabaseError: データベース操作エラー
        """
        try:
            # 検索パラメータのバリデーション
            self._validate_search_params(search_params)
            
            # リポジトリを使用して検索を実行
            db_todos = self.repository.search_todos(search_params)
            
            logger.info(
                f"Search completed successfully: found {len(db_todos)} todos with "
                f"completed={search_params.completed}, "
                f"end_date_from={search_params.end_date_from}, "
                f"end_date_to={search_params.end_date_to}"
            )
            
            return [TodoResponse.model_validate(todo) for todo in db_todos]
            
        except TodoValidationError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while searching todos: {e}")
            raise TodoDatabaseError("Failed to search todo items", e)
        except Exception as e:
            logger.error(f"Unexpected error while searching todos: {e}")
            raise TodoDatabaseError("Unexpected error occurred while searching todo items", e)
    
    def _validate_todo_create(self, todo_data: TodoCreate) -> None:
        """
        ToDoアイテム作成データのバリデーション
        
        Args:
            todo_data (TodoCreate): 作成データ
            
        Raises:
            TodoValidationError: バリデーションエラー
        """
        if not todo_data.title or not todo_data.title.strip():
            raise TodoValidationError("Title cannot be empty or whitespace only")
        
        if len(todo_data.title.strip()) > 200:
            raise TodoValidationError("Title cannot exceed 200 characters")
        
        if todo_data.description and len(todo_data.description) > 1000:
            raise TodoValidationError("Description cannot exceed 1000 characters")
    
    def _validate_todo_update(self, todo_data: TodoUpdate) -> None:
        """
        ToDoアイテム更新データのバリデーション
        
        Args:
            todo_data (TodoUpdate): 更新データ
            
        Raises:
            TodoValidationError: バリデーションエラー
        """
        # 少なくとも一つのフィールドが更新される必要がある
        update_data = todo_data.model_dump(exclude_unset=True)
        if not update_data:
            raise TodoValidationError("At least one field must be provided for update")
        
        if todo_data.title is not None:
            if not todo_data.title or not todo_data.title.strip():
                raise TodoValidationError("Title cannot be empty or whitespace only")
            
            if len(todo_data.title.strip()) > 200:
                raise TodoValidationError("Title cannot exceed 200 characters")
        
        if todo_data.description is not None and len(todo_data.description) > 1000:
            raise TodoValidationError("Description cannot exceed 1000 characters")
    
    def _validate_todo_id(self, todo_id: int) -> None:
        """
        ToDoアイテムIDのバリデーション
        
        Args:
            todo_id (int): ToDoアイテムID
            
        Raises:
            TodoValidationError: バリデーションエラー
        """
        if not isinstance(todo_id, int) or todo_id <= 0:
            raise TodoValidationError("Todo ID must be a positive integer")
    
    def _validate_pagination_params(self, skip: int, limit: int) -> None:
        """
        ページネーションパラメータのバリデーション
        
        Args:
            skip (int): スキップする件数
            limit (int): 取得する最大件数
            
        Raises:
            TodoValidationError: バリデーションエラー
        """
        if not isinstance(skip, int) or skip < 0:
            raise TodoValidationError("Skip parameter must be a non-negative integer")
        
        if not isinstance(limit, int) or limit <= 0:
            raise TodoValidationError("Limit parameter must be a positive integer")
        
        if limit > 1000:
            raise TodoValidationError("Limit parameter cannot exceed 1000")
    
    def _validate_search_params(self, search_params: TodoSearchParams) -> None:
        """
        検索パラメータのバリデーション
        
        Args:
            search_params (TodoSearchParams): 検索パラメータ
            
        Raises:
            TodoValidationError: バリデーションエラー
        """
        # ページネーションパラメータのバリデーション
        self._validate_pagination_params(search_params.skip, search_params.limit)
        
        # 日時範囲のバリデーション（Pydanticでも行われるが、追加のビジネスロジックチェック）
        if (search_params.end_date_from and search_params.end_date_to and 
            search_params.end_date_from > search_params.end_date_to):
            raise TodoValidationError("end_date_from must be before or equal to end_date_to")
        
        logger.debug(f"Search parameters validated successfully: {search_params}")