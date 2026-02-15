# 設計書

## 概要

ToDoアプリケーションのバックエンドAPIは、FastAPIフレームワークを使用したRESTful APIとして設計される。システムはレイヤードアーキテクチャを採用し、API層、ビジネスロジック層、データアクセス層に分離される。PostgreSQLデータベースを使用してデータを永続化し、Dockerコンテナ環境で実行される。

## アーキテクチャ

### システム構成

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Swagger UI    │    │     Client      │    │   PlantUML      │
│  (localhost:    │    │  Applications   │    │  Diagrams       │
│   8000/docs)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI       │
                    │   Application   │
                    │  (Port: 8000)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Database      │
                    │  (Port: 5432)   │
                    └─────────────────┘
```

### レイヤードアーキテクチャ

```
┌─────────────────────────────────────────┐
│              API Layer                  │
│  - FastAPI Routes                       │
│  - Request/Response Models              │
│  - HTTP Status Codes                    │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│           Service Layer                 │
│  - Business Logic                       │
│  - Data Validation                      │
│  - Error Handling                       │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         Repository Layer                │
│  - Database Operations                  │
│  - SQL Queries                          │
│  - Connection Management                │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│           Database Layer                │
│  - PostgreSQL                           │
│  - Table Schemas                        │
│  - Indexes                              │
└─────────────────────────────────────────┘
```

## コンポーネントとインターフェース

### 1. APIエンドポイント

#### ToDoアイテム管理エンドポイント

| メソッド | エンドポイント | 説明 | リクエスト | レスポンス |
|---------|---------------|------|-----------|-----------|
| POST | `/todos` | ToDoアイテム作成（期限設定対応） | `TodoCreate` | `TodoResponse` (201) |
| GET | `/todos` | 全ToDoアイテム取得（期限情報含む） | - | `List[TodoResponse]` (200) |
| GET | `/todos/{id}` | 特定ToDoアイテム取得（期限情報含む） | - | `TodoResponse` (200) |
| PUT | `/todos/{id}` | ToDoアイテム更新（期限変更対応） | `TodoUpdate` | `TodoResponse` (200) |
| DELETE | `/todos/{id}` | ToDoアイテム削除 | - | - (204) |
| GET | `/todos/search` | 条件付きToDoアイテム検索 | Query Parameters | `List[TodoResponse]` (200) |

#### 条件付き検索エンドポイント

**エンドポイント**: `GET /todos/search`

**クエリパラメータ**:
- `completed` (optional): boolean - 完了状態での絞り込み
- `end_date_from` (optional): datetime - 期限開始日時（ISO 8601形式）
- `end_date_to` (optional): datetime - 期限終了日時（ISO 8601形式）
- `skip` (optional): int - ページネーション用スキップ数（デフォルト: 0）
- `limit` (optional): int - 取得件数制限（デフォルト: 100、最大: 1000）

**使用例**:
```
# 完了済みタスクのみ取得
GET /todos/search?completed=true

# 期限切れタスク取得（現在時刻より前の期限）
GET /todos/search?end_date_to=2025-01-08T12:00:00Z

# 今日中のタスク取得
GET /todos/search?end_date_from=2025-01-08T00:00:00Z&end_date_to=2025-01-08T23:59:59Z

# 未完了かつ期限切れのタスク取得
GET /todos/search?completed=false&end_date_to=2025-01-08T12:00:00Z
```

**バリデーションエラー例**:
```json
{
  "detail": [
    {
      "loc": ["query", "end_date_from"],
      "msg": "Invalid datetime format. Use ISO 8601 format (e.g., '2025-01-08T12:00:00Z')",
      "type": "value_error"
    }
  ]
}
```

#### 期限設定機能の詳細

**リクエスト例（期限付きToDoアイテム作成）:**
```json
{
  "title": "重要なタスク",
  "description": "期限付きのタスク",
  "completed": false,
  "end_date": "2025-01-15T10:30:00Z"
}
```

**レスポンス例:**
```json
{
  "id": 1,
  "title": "重要なタスク",
  "description": "期限付きのタスク",
  "completed": false,
  "end_date": "2025-01-15T10:30:00Z",
  "created_at": "2025-01-08T09:00:00Z",
  "updated_at": "2025-01-08T09:00:00Z"
}
```

#### ヘルスチェックエンドポイント

| メソッド | エンドポイント | 説明 | レスポンス |
|---------|---------------|------|-----------|
| GET | `/health` | アプリケーション状態確認 | `HealthResponse` (200) |

### 2. プロジェクト構造

```
todo-api-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPIアプリケーションエントリーポイント
│   ├── config.py              # 設定管理
│   ├── database.py            # データベース接続設定
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py            # SQLAlchemyモデル
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── todo.py            # Pydanticスキーマ
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── todo.py            # データアクセス層
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo.py            # ビジネスロジック層
│   └── routers/
│       ├── __init__.py
│       ├── todo.py            # ToDoエンドポイント
│       └── health.py          # ヘルスチェックエンドポイント
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # テスト設定
│   ├── test_todo_api.py       # APIテスト
│   ├── test_todo_service.py   # サービステスト
│   └── test_todo_repository.py # リポジトリテスト
├── docs/
│   ├── sequence_diagrams/
│   │   ├── create_todo.puml
│   │   ├── get_todos.puml
│   │   ├── get_todo_by_id.puml
│   │   ├── update_todo.puml
│   │   └── delete_todo.puml
│   └── README.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── README.md
```

## データモデル

### 1. データベーススキーマ

#### todosテーブル

```sql
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- パフォーマンス向上のためのインデックス
CREATE INDEX idx_todos_completed ON todos(completed);
CREATE INDEX idx_todos_created_at ON todos(created_at);
CREATE INDEX idx_todos_end_date ON todos(end_date);

-- 複合インデックス：よくある検索パターンを最適化
CREATE INDEX idx_todos_completed_created ON todos(completed, created_at DESC);
CREATE INDEX idx_todos_incomplete_end_date ON todos(completed, end_date);

-- 部分インデックス：未完了タスクのみ（PostgreSQL特有の最適化）
CREATE INDEX idx_todos_incomplete_only ON todos(created_at DESC) WHERE completed = FALSE;
```

### 2. Pydanticスキーマ

#### TodoBase
```python
class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: bool = False
    end_date: Optional[datetime] = Field(
        None, 
        description="Task deadline in ISO 8601 format (e.g., '2025-01-15T10:30:00Z'). Optional field for setting task completion deadlines."
    )
```

#### TodoCreate
```python
class TodoCreate(TodoBase):
    pass
```

#### TodoUpdate
```python
class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    end_date: Optional[datetime] = Field(
        None, 
        description="Task deadline in ISO 8601 format (e.g., '2025-01-15T10:30:00Z'). Optional field for setting task completion deadlines."
    )
```

#### TodoResponse
```python
class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### TodoSearchParams
```python
class TodoSearchParams(BaseModel):
    """ToDoアイテム検索用パラメータスキーマ"""
    completed: Optional[bool] = Field(None, description="完了状態での絞り込み")
    end_date_from: Optional[datetime] = Field(
        None, 
        description="期限開始日時（ISO 8601形式）"
    )
    end_date_to: Optional[datetime] = Field(
        None, 
        description="期限終了日時（ISO 8601形式）"
    )
    skip: int = Field(0, ge=0, description="ページネーション用スキップ数")
    limit: int = Field(100, ge=1, le=1000, description="取得件数制限")
    
    @field_validator('end_date_from', 'end_date_to')
    @classmethod
    def validate_datetime_format(cls, v: Optional[datetime]) -> Optional[datetime]:
        """日時形式のバリデーション"""
        return v
    
    @model_validator(mode='after')
    def validate_date_range(self) -> 'TodoSearchParams':
        """日時範囲のバリデーション"""
        if (self.end_date_from and self.end_date_to and 
            self.end_date_from > self.end_date_to):
            raise ValueError('end_date_from must be before or equal to end_date_to')
        return self
```

### 3. SQLAlchemyモデル

```python
class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    @property
    def is_overdue(self) -> bool:
        """
        期限切れかどうかを判定する
        
        Returns:
            bool: 期限切れの場合True（完了済みタスクは期限切れとしない）
        """
        from datetime import datetime, timezone
        
        if not self.end_date or self.completed:
            return False
        
        now = datetime.now(timezone.utc)
        return self.end_date < now
```

## エラーハンドリング

### HTTPエラーレスポンス

| ステータスコード | 説明 | レスポンス形式 |
|-----------------|------|---------------|
| 400 | Bad Request | `{"detail": "Invalid request"}` |
| 404 | Not Found | `{"detail": "Todo not found"}` |
| 422 | Validation Error | `{"detail": [{"loc": ["field"], "msg": "error message", "type": "error_type"}]}` |
| 500 | Internal Server Error | `{"detail": "Internal server error"}` |

### エラーハンドリング戦略

1. **バリデーションエラー**: Pydanticによる自動バリデーション
2. **データベースエラー**: SQLAlchemyエラーをHTTPエラーに変換
3. **ビジネスロジックエラー**: カスタム例外クラスを定義
4. **ログ記録**: 構造化ログでエラー追跡

## テスト戦略

### 1. テストレベル

#### 単体テスト
- **Repository層**: データベース操作のテスト
- **Service層**: ビジネスロジックのテスト
- **Schema**: データバリデーションのテスト

#### 統合テスト
- **API層**: エンドポイントの動作テスト
- **データベース統合**: 実際のデータベースとの連携テスト

### 2. テスト環境

- **テストデータベース**: PostgreSQLテスト用コンテナ
- **テストフィクスチャ**: pytest fixturesでテストデータ管理
- **モック**: 外部依存関係のモック化

### 3. テストカバレッジ

- **目標カバレッジ**: 90%以上
- **重要な機能**: CRUD操作、バリデーション、エラーハンドリング、期限設定機能
- **期限設定機能のテスト**:
  - end_date付きToDoアイテムの作成・更新・削除
  - 期限切れ判定ロジック
  - 無効な日時形式のバリデーション
  - 期限の追加・削除操作

## セキュリティ考慮事項

### 1. 入力検証
- Pydanticによる厳密なデータバリデーション
- SQLインジェクション対策（SQLAlchemy ORM使用）
- XSS対策（JSON APIのため基本的に安全）

### 2. データベースセキュリティ
- 環境変数による認証情報管理
- 最小権限の原則
- 接続プールの適切な設定

### 3. API セキュリティ
- CORS設定
- レート制限（将来的な拡張）
- HTTPSの使用（本番環境）

## パフォーマンス考慮事項

### 1. データベース最適化
- 適切なインデックス設定
- 接続プール管理
- クエリ最適化

### 2. API最適化
- 非同期処理（FastAPIの非同期機能活用）
- レスポンス圧縮
- 適切なHTTPキャッシュヘッダー

## デプロイメント設計

### 1. Docker構成

#### アプリケーションコンテナ
- **ベースイメージ**: python:3.13-slim
- **ポート**: 8000
- **環境変数**: データベース接続情報

#### データベースコンテナ
- **イメージ**: postgres:17.5
- **ポート**: 5432
- **永続化**: Dockerボリューム

### 2. 環境設定

#### 開発環境
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/todoapp
    depends_on:
      - db
  
  db:
    image: postgres:17.5
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=todoapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

## 監視とログ

### 1. ログ戦略
- **構造化ログ**: JSON形式
- **ログレベル**: DEBUG, INFO, WARNING, ERROR
- **ログ内容**: リクエスト/レスポンス、エラー、パフォーマンス

### 2. ヘルスチェック
- **エンドポイント**: `/health`
- **チェック項目**: データベース接続、アプリケーション状態

## 拡張性設計

### 1. 実装済み機能
- ToDoアイテムの基本CRUD操作
- データバリデーションとエラーハンドリング
- PostgreSQLデータベース統合
- Docker環境での実行
- Swagger UI による API仕様書
- 包括的なテストスイート
- **期限設定機能（end_date）**
  - ToDoアイテムへの期限設定
  - 期限切れ判定機能
  - ISO 8601形式での日時管理
  - 期限の追加・更新・削除

### 2. 将来的な機能拡張
- ユーザー認証・認可
- ToDoカテゴリ機能
- 添付ファイル機能
- 通知機能（期限切れアラート）

### 2. スケーラビリティ
- 水平スケーリング対応
- データベース読み取り専用レプリカ
- キャッシュ層の追加