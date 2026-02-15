# データベース管理ガイド

このプロジェクトでは、Alembicを使用してデータベースマイグレーションを管理しています。

## 🔧 セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、データベース接続情報を設定：

```bash
cp .env.example .env
```

### 3. データベースの初期化

```bash
# マイグレーションの実行
python scripts/db_migrate.py up

# サンプルデータの投入（開発環境のみ）
python scripts/init_db.py
```

## 📊 マイグレーション管理

### 基本コマンド

```bash
# 最新のマイグレーションまで適用
python scripts/db_migrate.py up

# 現在のマイグレーション状態を確認
python scripts/db_migrate.py current

# マイグレーション履歴を表示
python scripts/db_migrate.py history

# 新しいマイグレーションを作成
python scripts/db_migrate.py create "Add new column to users table"

# 1つ前のマイグレーションに戻す
python scripts/db_migrate.py down

# 特定のリビジョンまで戻す
python scripts/db_migrate.py down abc123
```

### Alembicコマンド（直接実行）

```bash
# 現在の状態を確認
alembic current

# 最新まで適用
alembic upgrade head

# 1つ前に戻す
alembic downgrade -1

# 特定のリビジョンまで戻す
alembic downgrade abc123

# 新しいマイグレーションを自動生成
alembic revision --autogenerate -m "Description of changes"

# 空のマイグレーションファイルを作成
alembic revision -m "Manual migration"

# マイグレーション履歴を表示
alembic history --verbose
```

## 🏗️ モデル変更のワークフロー

### 1. モデルの変更

`app/models/`内のSQLAlchemyモデルを変更します。

```python
# app/models/todo.py
class Todo(Base):
    # 新しいカラムを追加
    priority = Column(Integer, default=1, comment="優先度（1-5）")
```

### 2. マイグレーションの生成

```bash
python scripts/db_migrate.py create "Add priority column to todos"
```

### 3. マイグレーションファイルの確認

生成されたファイル（`alembic/versions/xxx_add_priority_column_to_todos.py`）を確認し、必要に応じて調整します。

### 4. マイグレーションの適用

```bash
python scripts/db_migrate.py up
```

## 📁 ディレクトリ構造

```
├── alembic/                    # Alembicマイグレーション
│   ├── versions/              # マイグレーションファイル
│   ├── env.py                 # Alembic環境設定
│   └── script.py.mako         # マイグレーションテンプレート
├── app/
│   ├── models/                # SQLAlchemyモデル
│   └── database.py            # データベース設定
├── scripts/
│   ├── db_migrate.py          # マイグレーション管理スクリプト
│   └── init_db.py             # データベース初期化スクリプト
├── alembic.ini                # Alembic設定ファイル
└── .env                       # 環境変数
```

## 🔄 従来のSQLマイグレーションからの移行

### 旧システム（手動SQL）の問題点

- ✗ 手動でSQLファイルを管理
- ✗ スキーマとモデルの二重管理
- ✗ マイグレーション履歴の追跡が困難
- ✗ ロールバック機能がない
- ✗ 環境間での同期が困難

### 新システム（Alembic）の利点

- ✅ **自動マイグレーション生成**: モデル変更から自動でマイグレーションを生成
- ✅ **バージョン管理**: マイグレーションの履歴を自動追跡
- ✅ **ロールバック機能**: 簡単に前のバージョンに戻せる
- ✅ **環境間同期**: 開発・テスト・本番環境で同じマイグレーションを適用
- ✅ **依存関係管理**: マイグレーション間の依存関係を自動管理
- ✅ **型安全性**: SQLAlchemyモデルとの整合性を保証

## 🚀 本番環境でのデプロイ

### 1. マイグレーションの確認

```bash
# 適用予定のマイグレーションを確認
alembic show head
alembic history --verbose
```

### 2. バックアップの作成

```bash
# PostgreSQLの場合
pg_dump -h localhost -U username -d database_name > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 3. マイグレーションの適用

```bash
# 本番環境でのマイグレーション実行
alembic upgrade head
```

### 4. 動作確認

アプリケーションが正常に動作することを確認します。

## 🔧 トラブルシューティング

### マイグレーションが失敗した場合

```bash
# 現在の状態を確認
alembic current

# 手動でリビジョンをマーク（データベースは変更せず、履歴のみ更新）
alembic stamp head

# 特定のリビジョンにマーク
alembic stamp abc123
```

### マイグレーションファイルの競合

複数の開発者が同時にマイグレーションを作成した場合：

```bash
# マイグレーションをマージ
alembic merge -m "Merge migrations" rev1 rev2
```

### データベースの完全リセット

```bash
# 全てのテーブルを削除してから再作成
alembic downgrade base
alembic upgrade head
```

## 📚 参考資料

- [Alembic公式ドキュメント](https://alembic.sqlalchemy.org/)
- [SQLAlchemy公式ドキュメント](https://docs.sqlalchemy.org/)
- [FastAPI + SQLAlchemy + Alembic チュートリアル](https://fastapi.tiangolo.com/tutorial/sql-databases/)