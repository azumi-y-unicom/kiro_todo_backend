"""
ToDoエンドポイント

ToDoアイテムのCRUD操作を提供するAPIエンドポイントを実装する。
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoSearchParams
from app.services.todo import (
    TodoService, 
    TodoNotFoundError, 
    TodoValidationError, 
    TodoDatabaseError
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    db: Session = Depends(get_db)
):
    """
    新しいToDoアイテムを作成する
    
    Creates a new todo item with optional deadline support.
    
    Args:
        todo_data (TodoCreate): 作成するToDoアイテムのデータ
            - title: タスクのタイトル（必須、最大200文字）
            - description: タスクの説明（任意、最大1000文字）
            - completed: 完了状態（デフォルト: false）
            - end_date: 完了期限（任意、ISO 8601形式）
        db (Session): データベースセッション
        
    Returns:
        TodoResponse: 作成されたToDoアイテム
        
    Raises:
        HTTPException: バリデーションエラーまたはデータベースエラー
    """
    try:
        service = TodoService(db)
        created_todo = service.create_todo(todo_data)
        logger.info(f"Created todo item: {created_todo.id}")
        return created_todo
        
    except TodoValidationError as e:
        logger.warning(f"Validation error creating todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except TodoDatabaseError as e:
        logger.error(f"Database error creating todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create todo item"
        )


@router.get("/", response_model=List[TodoResponse], status_code=status.HTTP_200_OK)
async def get_todos(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    db: Session = Depends(get_db)
):
    """
    すべてのToDoアイテムを取得する
    
    Args:
        skip (int): スキップする件数（ページネーション用）
        limit (int): 取得する最大件数
        db (Session): データベースセッション
        
    Returns:
        List[TodoResponse]: ToDoアイテムのリスト
        
    Raises:
        HTTPException: バリデーションエラーまたはデータベースエラー
    """
    try:
        service = TodoService(db)
        todos = service.get_all_todos(skip, limit)
        logger.debug(f"Retrieved {len(todos)} todo items")
        return todos
        
    except TodoValidationError as e:
        logger.warning(f"Validation error getting todos: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except TodoDatabaseError as e:
        logger.error(f"Database error getting todos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve todo items"
        )


@router.get("/search", response_model=List[TodoResponse], status_code=status.HTTP_200_OK)
async def search_todos(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    end_date_from: Optional[datetime] = Query(None, description="Filter todos with end_date from this datetime (ISO 8601 format)"),
    end_date_to: Optional[datetime] = Query(None, description="Filter todos with end_date until this datetime (ISO 8601 format)"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return (1-1000)"),
    db: Session = Depends(get_db)
):
    """
    条件に基づいてToDoアイテムを検索する
    
    Search for todo items based on various criteria including completion status and deadline ranges.
    
    Args:
        completed (Optional[bool]): Filter by completion status
        end_date_from (Optional[datetime]): Filter todos with end_date from this datetime
        end_date_to (Optional[datetime]): Filter todos with end_date until this datetime
        skip (int): Number of records to skip for pagination
        limit (int): Maximum number of records to return
        db (Session): データベースセッション
        
    Returns:
        List[TodoResponse]: 検索条件に一致するToDoアイテムのリスト
        
    Raises:
        HTTPException: バリデーションエラーまたはデータベースエラー
        
    Examples:
        - Get completed todos: GET /todos/search?completed=true
        - Get overdue todos: GET /todos/search?end_date_to=2025-01-08T12:00:00Z
        - Get today's todos: GET /todos/search?end_date_from=2025-01-08T00:00:00Z&end_date_to=2025-01-08T23:59:59Z
        - Get incomplete overdue todos: GET /todos/search?completed=false&end_date_to=2025-01-08T12:00:00Z
    """
    try:
        # Create search parameters object
        search_params = TodoSearchParams(
            completed=completed,
            end_date_from=end_date_from,
            end_date_to=end_date_to,
            skip=skip,
            limit=limit
        )
        
        service = TodoService(db)
        todos = service.search_todos(search_params)
        
        logger.info(f"Search completed: found {len(todos)} todos matching criteria")
        return todos
        
    except ValueError as e:
        # Handle Pydantic validation errors (e.g., date range validation)
        logger.warning(f"Validation error in search parameters: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except TodoValidationError as e:
        logger.warning(f"Service validation error searching todos: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except TodoDatabaseError as e:
        logger.error(f"Database error searching todos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search todo items"
        )


@router.get("/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
async def get_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """
    特定のToDoアイテムを取得する
    
    Args:
        todo_id (int): 取得するToDoアイテムのID
        db (Session): データベースセッション
        
    Returns:
        TodoResponse: 見つかったToDoアイテム
        
    Raises:
        HTTPException: ToDoアイテムが見つからない場合またはデータベースエラー
    """
    try:
        service = TodoService(db)
        todo = service.get_todo_by_id(todo_id)
        logger.debug(f"Retrieved todo item: {todo_id}")
        return todo
        
    except TodoNotFoundError as e:
        logger.warning(f"Todo not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item with id {todo_id} not found"
        )
    except TodoValidationError as e:
        logger.warning(f"Validation error getting todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except TodoDatabaseError as e:
        logger.error(f"Database error getting todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve todo item"
        )


@router.put("/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db)
):
    """
    ToDoアイテムを更新する
    
    Updates an existing todo item. All fields are optional.
    
    Args:
        todo_id (int): 更新するToDoアイテムのID
        todo_data (TodoUpdate): 更新データ
            - title: タスクのタイトル（任意、最大200文字）
            - description: タスクの説明（任意、最大1000文字）
            - completed: 完了状態（任意）
            - end_date: 完了期限（任意、ISO 8601形式、nullで削除可能）
        db (Session): データベースセッション
        
    Returns:
        TodoResponse: 更新されたToDoアイテム
        
    Raises:
        HTTPException: ToDoアイテムが見つからない場合またはバリデーションエラー
    """
    try:
        service = TodoService(db)
        updated_todo = service.update_todo(todo_id, todo_data)
        logger.info(f"Updated todo item: {todo_id}")
        return updated_todo
        
    except TodoNotFoundError as e:
        logger.warning(f"Todo not found for update: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item with id {todo_id} not found"
        )
    except TodoValidationError as e:
        logger.warning(f"Validation error updating todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except TodoDatabaseError as e:
        logger.error(f"Database error updating todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update todo item"
        )


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """
    ToDoアイテムを削除する
    
    Args:
        todo_id (int): 削除するToDoアイテムのID
        db (Session): データベースセッション
        
    Raises:
        HTTPException: ToDoアイテムが見つからない場合またはデータベースエラー
    """
    try:
        service = TodoService(db)
        service.delete_todo(todo_id)
        logger.info(f"Deleted todo item: {todo_id}")
        
    except TodoNotFoundError as e:
        logger.warning(f"Todo not found for deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item with id {todo_id} not found"
        )
    except TodoValidationError as e:
        logger.warning(f"Validation error deleting todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except TodoDatabaseError as e:
        logger.error(f"Database error deleting todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete todo item"
        )