"""
ToDoアイテムのSQLAlchemyモデル

PostgreSQLデータベースのtodosテーブルに対応するモデルを定義する。
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import validates

from app.database import Base

# Constants for field lengths - should match schema validation
TITLE_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 1000


class Todo(Base):
    """
    ToDoアイテムモデル

    Attributes:
        id (int): 主キー（自動生成）
        title (str): タイトル（必須、最大200文字）
        description (str): 説明（任意、最大1000文字）
        completed (bool): 完了状態（デフォルト: False）
        end_date (date): 完了予定日（任意）
        created_at (datetime): 作成日時（自動設定）
        updated_at (datetime): 更新日時（自動更新）
    """
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True, comment="主キー")
    title = Column(
        String(TITLE_MAX_LENGTH),
        nullable=False,
        comment=f"タイトル（必須、最大{TITLE_MAX_LENGTH}文字）"
    )
    description = Column(
        Text,
        nullable=True,
        comment=f"説明（任意、最大{DESCRIPTION_MAX_LENGTH}文字）"
    )
    completed = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="完了状態（デフォルト: False）"
    )
    end_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="完了予定日"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="作成日時（自動設定）"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新日時（自動更新）"
    )

    def __repr__(self) -> str:
        """モデルの文字列表現"""
        return (
            f"<Todo(id={self.id}, title='{self.title}', "
            f"completed={self.completed})>"
        )

    def mark_completed(self) -> bool:
        """
        タスクを完了状態にする
        
        Returns:
            bool: 状態が変更された場合True
        """
        if not self.completed:
            self.completed = True
            return True
        return False

    def mark_incomplete(self) -> bool:
        """
        タスクを未完了状態にする
        
        Returns:
            bool: 状態が変更された場合True
        """
        if self.completed:
            self.completed = False
            return True
        return False

    def toggle_completion(self) -> bool:
        """
        完了状態を切り替える
        
        Returns:
            bool: 新しい完了状態
        """
        self.completed = not self.completed
        return self.completed

    @property
    def is_overdue(self) -> bool:
        """
        期限切れかどうかを判定する
        
        Returns:
            bool: 期限切れの場合True
        """
        from datetime import datetime, timezone
        
        if not self.end_date or self.completed:
            return False
        
        now = datetime.now(timezone.utc)
        return self.end_date < now

    @validates('title')
    def validate_title(self, key, title):
        """タイトルの妥当性を検証する"""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty or just whitespace")
        
        if len(title) > TITLE_MAX_LENGTH:
            raise ValueError(
                f"Title cannot exceed {TITLE_MAX_LENGTH} characters"
            )
        
        return title.strip()

    @validates('description')
    def validate_description(self, key, description):
        """説明の妥当性を検証する"""
        if description is not None:
            if len(description) > DESCRIPTION_MAX_LENGTH:
                raise ValueError(
                    f"Description cannot exceed {DESCRIPTION_MAX_LENGTH} "
                    "characters"
                )
            description = description.strip()
            return description if description else None
        return description


# インデックスの定義
# パフォーマンス向上のため、よく検索される列にインデックスを作成

# 単一列インデックス
Index("idx_todos_completed", Todo.completed)
Index("idx_todos_created_at", Todo.created_at)
Index("idx_todos_end_date", Todo.end_date)

# 複合インデックス：よくある検索パターンを最適化
# 完了状態と作成日時での検索（リスト表示用）
Index("idx_todos_completed_created", Todo.completed, Todo.created_at.desc())
# 期限切れタスクの検索用
Index("idx_todos_incomplete_end_date", Todo.completed, Todo.end_date)

# 部分インデックス：PostgreSQL特有の最適化
# 未完了タスクのみのインデックス（完了済みタスクは除外）
Index(
    "idx_todos_incomplete_only",
    Todo.created_at.desc(),
    postgresql_where=(Todo.completed.is_(False))
)