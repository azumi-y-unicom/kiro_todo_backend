# Docker Compose 使用ガイド

## ファイル構成

### `docker-compose.yml` (メインファイル)
- **用途**: 基本的な開発・テスト用設定
- **コマンド**: `docker-compose up -d`
- **特徴**: シンプルで動作確認しやすい設定

### `docker-compose.override.yml` (開発用オーバーライド)
- **用途**: 開発時の追加設定（自動的に適用される）
- **特徴**: ホットリロード、デバッグモード有効

### `docker-compose.prod.yml` (本番用)
- **用途**: 本番環境用の最適化された設定
- **コマンド**: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`
- **特徴**: セキュリティ強化、リソース制限、パフォーマンス最適化

### `docker-compose.full.yml` (フル機能版)
- **用途**: 全機能を含む完全版
- **コマンド**: `docker-compose -f docker-compose.full.yml up -d`
- **特徴**: 全ての設定オプションを含む

## 基本的な使用方法

### 1. 開発環境での起動
```bash
# 基本的な起動（推奨）
docker-compose up -d

# ログを確認
docker-compose logs -f

# 停止
docker-compose down
```

### 2. 本番環境での起動
```bash
# 本番用設定で起動
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# または完全版で起動
docker-compose -f docker-compose.full.yml up -d
```

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
# ボリュームを削除して完全にリセット
docker-compose down -v
docker-compose up -d
```

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