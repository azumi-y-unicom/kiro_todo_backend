"""
ToDoリポジトリ

ToDoアイテムのデータアクセス層を実装する。
CRUD操作とデータベースセッション管理を提供する。
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
import logging

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate, TodoSearchParams

logger = logging.getLogger(__name__)


class TodoRepository:
    """
    ToDoアイテムのデータアクセスを管理するリポジトリクラス
    
    データベースとの直接的なやり取りを担当し、
    CRUD操作を提供する。
    """
    
    def __init__(self, db: Session):
        """
        リポジトリを初期化する
        
        Args:
            db (Session): SQLAlchemyデータベースセッション
        """
        self.db = db
    
    def create(self, todo_data: TodoCreate) -> Todo:
        """
        新しいToDoアイテムを作成する
        
        Args:
            todo_data (TodoCreate): 作成するToDoアイテムのデータ
            
        Returns:
            Todo: 作成されたToDoアイテム
            
        Raises:
            SQLAlchemyError: データベース操作エラー
        """
        try:
            db_todo = Todo(
                title=todo_data.title,
                description=todo_data.description,
                completed=todo_data.completed,
                end_date=todo_data.end_date
            )
            self.db.add(db_todo)
            self.db.commit()
            self.db.refresh(db_todo)
            
            logger.info(f"Created todo item with id: {db_todo.id}")
            return db_todo
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create todo item: {e}")
            self.db.rollback()
            raise
    
    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        """
        IDでToDoアイテムを取得する
        
        Args:
            todo_id (int): 取得するToDoアイテムのID
            
        Returns:
            Optional[Todo]: 見つかったToDoアイテム、存在しない場合はNone
        """
        try:
            todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
            if todo:
                logger.debug(f"Retrieved todo item with id: {todo_id}")
            else:
                logger.debug(f"Todo item with id {todo_id} not found")
            return todo
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get todo item by id {todo_id}: {e}")
            raise
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Todo]:
        """
        すべてのToDoアイテムを取得する
        
        Args:
            skip (int): スキップする件数（ページネーション用）
            limit (int): 取得する最大件数
            
        Returns:
            List[Todo]: ToDoアイテムのリスト
        """
        try:
            todos = (
                self.db.query(Todo)
                .order_by(Todo.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            logger.debug(f"Retrieved {len(todos)} todo items")
            return todos
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get all todo items: {e}")
            raise
    
    def update(self, todo_id: int, todo_data: TodoUpdate) -> Optional[Todo]:
        """
        ToDoアイテムを更新する
        
        Args:
            todo_id (int): 更新するToDoアイテムのID
            todo_data (TodoUpdate): 更新データ
            
        Returns:
            Optional[Todo]: 更新されたToDoアイテム、存在しない場合はNone
            
        Raises:
            SQLAlchemyError: データベース操作エラー
        """
        try:
            db_todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
            if not db_todo:
                logger.debug(f"Todo item with id {todo_id} not found for update")
                return None
            
            # 更新データが提供された場合のみ更新
            update_data = todo_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_todo, field, value)
            
            self.db.commit()
            self.db.refresh(db_todo)
            
            logger.info(f"Updated todo item with id: {todo_id}")
            return db_todo
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to update todo item with id {todo_id}: {e}")
            self.db.rollback()
            raise
    
    def delete(self, todo_id: int) -> bool:
        """
        ToDoアイテムを削除する
        
        Args:
            todo_id (int): 削除するToDoアイテムのID
            
        Returns:
            bool: 削除が成功した場合True、アイテムが存在しない場合False
            
        Raises:
            SQLAlchemyError: データベース操作エラー
        """
        try:
            db_todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
            if not db_todo:
                logger.debug(f"Todo item with id {todo_id} not found for deletion")
                return False
            
            self.db.delete(db_todo)
            self.db.commit()
            
            logger.info(f"Deleted todo item with id: {todo_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete todo item with id {todo_id}: {e}")
            self.db.rollback()
            raise
    
    def get_by_completion_status(self, completed: bool) -> List[Todo]:
        """
        完了状態でToDoアイテムを取得する
        
        Args:
            completed (bool): 完了状態（True: 完了済み、False: 未完了）
            
        Returns:
            List[Todo]: 指定された完了状態のToDoアイテムのリスト
        """
        try:
            todos = (
                self.db.query(Todo)
                .filter(Todo.completed == completed)
                .order_by(Todo.created_at.desc())
                .all()
            )
            logger.debug(f"Retrieved {len(todos)} todo items with completed={completed}")
            return todos
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get todo items by completion status: {e}")
            raise
    
    def count_all(self) -> int:
        """
        すべてのToDoアイテムの数を取得する
        
        Returns:
            int: ToDoアイテムの総数
        """
        try:
            count = self.db.query(Todo).count()
            logger.debug(f"Total todo items count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to count todo items: {e}")
            raise
    
    def count_by_completion_status(self, completed: bool) -> int:
        """
        完了状態別のToDoアイテム数を取得する
        
        Args:
            completed (bool): 完了状態
            
        Returns:
            int: 指定された完了状態のToDoアイテム数
        """
        try:
            count = self.db.query(Todo).filter(Todo.completed == completed).count()
            logger.debug(f"Todo items count with completed={completed}: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to count todo items by completion status: {e}")
            raise
    
    def search_todos(self, search_params: TodoSearchParams) -> List[Todo]:
        """
        条件に基づいてToDoアイテムを検索する
        
        Args:
            search_params (TodoSearchParams): 検索条件パラメータ
            
        Returns:
            List[Todo]: 検索条件に一致するToDoアイテムのリスト
            
        Raises:
            SQLAlchemyError: データベース操作エラー
        """
        try:
            query = self.db.query(Todo)
            
            # 完了状態での絞り込み
            if search_params.completed is not None:
                query = query.filter(Todo.completed == search_params.completed)
            
            # 期限開始日時での絞り込み
            if search_params.end_date_from is not None:
                query = query.filter(Todo.end_date >= search_params.end_date_from)
            
            # 期限終了日時での絞り込み
            if search_params.end_date_to is not None:
                query = query.filter(Todo.end_date <= search_params.end_date_to)
            
            # 結果を作成日時の降順でソートし、ページネーションを適用
            todos = (
                query
                .order_by(Todo.created_at.desc())
                .offset(search_params.skip)
                .limit(search_params.limit)
                .all()
            )
            
            logger.debug(
                f"Search completed: found {len(todos)} todos with params "
                f"completed={search_params.completed}, "
                f"end_date_from={search_params.end_date_from}, "
                f"end_date_to={search_params.end_date_to}, "
                f"skip={search_params.skip}, limit={search_params.limit}"
            )
            
            return todos
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to search todo items: {e}")
            raise