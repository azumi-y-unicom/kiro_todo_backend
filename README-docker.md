# Docker Compose 使用ガイド

## 🚀 新機能: Alembic統合

Docker起動時に自動的にAlembicマイグレーションが実行されます！

### 自動実行される処理
1. **データベース接続待機**: PostgreSQLが起動するまで待機
2. **マイグレーション実行**: `alembic upgrade head` を自動実行
3. **サンプルデータ作成**: 開発環境では自動的にサンプルデータを投入
4. **アプリケーション起動**: FastAPIサーバーを起動

## ファイル構成

### `docker-compose.yml` (メインファイル)
- **用途**: 基本的な開発・テスト用設定
- **コマンド**: `docker-compose up -d`
- **特徴**: Alembicマイグレーション自動実行、サンプルデータ作成

### `docker-compose.override.yml` (開発用オーバーライド)
- **用途**: 開発時の追加設定（自動的に適用される）
- **特徴**: ホットリロード、デバッグモード、ボリュームマウント

### `docker-compose.prod.yml` (本番用)
- **用途**: 本番環境用の最適化された設定
- **コマンド**: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`
- **特徴**: セキュリティ強化、リソース制限、サンプルデータ無効化

## 基本的な使用方法

### 1. 開発環境での起動
```bash
# 基本的な起動（推奨）- マイグレーション自動実行
docker-compose up -d

# 起動ログを確認（マイグレーション実行状況を確認）
docker-compose logs -f app

# 全サービスのログを確認
docker-compose logs -f

# 停止
docker-compose down
```

### 2. 本番環境での起動
```bash
# 本番用設定で起動（マイグレーション自動実行、サンプルデータなし）
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# マイグレーション実行状況を確認
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs app
```

### 3. マイグレーション制御オプション

```bash
# マイグレーションをスキップして起動
SKIP_MIGRATIONS=true docker-compose up -d

# サンプルデータ作成を無効化
CREATE_SAMPLE_DATA=false docker-compose up -d

# 環境変数を設定ファイルで管理
echo "SKIP_MIGRATIONS=false" >> .env
echo "CREATE_SAMPLE_DATA=true" >> .env
docker-compose up -d
=======
# 本番用設定で起動
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# または完全版で起動
docker-compose -f docker-compose.full.yml up -d

### 3. データベース管理
- **Adminer**: http://localhost:8080
- **PostgreSQL**: localhost:5432
  - ユーザー: `todouser`
  - パスワード: `todopass`
  - データベース: `todoapp`

### 4. API エンドポイント
- **API**: http://localhost:8000
- **ドキュメント**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **ヘルスチェック**: http://localhost:8000/health

## トラブルシューティング

### ポートが使用中の場合
```bash
# 使用中のポートを確認
netstat -an | findstr :8000
netstat -an | findstr :5432

# プロセスを停止してから再起動
docker-compose down
docker-compose up -d
```

### データベースの初期化
```bash
# ボリュームを削除して完全にリセット（マイグレーションも自動実行）
docker-compose down -v
docker-compose up -d

# マイグレーションのみ手動実行
docker-compose exec app alembic upgrade head

# マイグレーション状態を確認
docker-compose exec app alembic current

# サンプルデータを手動作成
docker-compose exec app python scripts/init_db.py
=======
# ボリュームを削除して完全にリセット
docker-compose down -v
docker-compose up -d

### ログの確認
```bash
# 全サービスのログ
docker-compose logs

# 特定のサービスのログ
docker-compose logs app
docker-compose logs db

# リアルタイムでログを追跡
docker-compose logs -f app
```

## 開発時のヒント

1. **ホットリロード**: `docker-compose.override.yml`により、コード変更時に自動的にアプリケーションが再起動されます
2. **データベース接続**: 開発時はPostgreSQLポートが公開されているため、外部ツールから直接接続可能です
3. **Adminer**: データベースの管理にはAdminerを使用できます（http://localhost:8080）
#
# 🔧 Alembicマイグレーション管理

### Docker環境でのマイグレーション操作

```bash
# 新しいマイグレーションを作成
docker-compose exec app alembic revision --autogenerate -m "Add new feature"

# マイグレーション状態を確認
docker-compose exec app alembic current

# マイグレーション履歴を表示
docker-compose exec app alembic history --verbose

# 特定のリビジョンまで戻す
docker-compose exec app alembic downgrade abc123

# 最新まで適用
docker-compose exec app alembic upgrade head
```

### 起動時の環境変数

| 変数名 | デフォルト | 説明 |
|--------|------------|------|
| `SKIP_MIGRATIONS` | `false` | `true`でマイグレーションをスキップ |
| `CREATE_SAMPLE_DATA` | `true` (dev) / `false` (prod) | サンプルデータの作成 |
| `ENVIRONMENT` | `development` | 環境設定（development/production） |
| `DATABASE_URL` | PostgreSQL接続文字列 | データベース接続URL |

### 起動シーケンス

1. **データベース待機**: PostgreSQLの起動を待機（最大60秒）
2. **マイグレーション確認**: 現在のマイグレーション状態を表示
3. **マイグレーション実行**: `alembic upgrade head` を実行
4. **サンプルデータ**: 開発環境でサンプルデータを作成
5. **アプリケーション起動**: FastAPIサーバーを起動

### トラブルシューティング

#### マイグレーションエラーが発生した場合

```bash
# コンテナ内でマイグレーション状態を確認
docker-compose exec app alembic current

# 手動でマイグレーションを実行
docker-compose exec app alembic upgrade head

# マイグレーションをスキップして起動
SKIP_MIGRATIONS=true docker-compose up -d
```

#### データベースリセットが必要な場合

```bash
# 完全リセット（データとマイグレーション履歴を削除）
docker-compose down -v
docker-compose up -d

# マイグレーション履歴のみリセット
docker-compose exec app alembic stamp base
docker-compose exec app alembic upgrade head
```
