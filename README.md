# Todo API Backend

Windows11のローカル環境でDockerを使用して動作するToDoアプリケーションのバックエンドAPI。Python 3.13とFastAPIを使用してRESTful APIを構築し、PostgreSQL 17.5でデータを永続化します。

## 🚀 機能

- **CRUD操作**: ToDoアイテムの作成、読み取り、更新、削除
- **データバリデーション**: Pydanticによる厳密なデータ検証
- **データベース統合**: PostgreSQL 17.5による永続化
- **API仕様書**: Swagger UI / ReDoc による自動生成ドキュメント
- **テスト環境**: pytest による包括的なテストスイート
- **Docker対応**: docker-compose による簡単な環境構築
- **ヘルスチェック**: アプリケーション状態監視機能

## 📋 要件

- Docker Desktop for Windows
- Docker Compose
- Git

## 🛠️ セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd todo-api-backend
```

### 2. 環境変数の設定

`.env.example`ファイルを参考に環境変数を設定してください（オプション）：

```bash
cp .env.example .env
```

### 3. Dockerコンテナの起動

```bash
# アプリケーションとデータベースを起動
docker-compose up -d

# ログを確認する場合
docker-compose logs -f
```

### 4. アプリケーションの確認

アプリケーションが正常に起動したら、以下のURLにアクセスできます：

- **API エンドポイント**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs （**推奨**: APIの仕様確認とテストに使用）
- **ReDoc**: http://localhost:8000/redoc
- **ヘルスチェック**: http://localhost:8000/health

#### Swagger UIの使用方法

1. ブラウザで http://localhost:8000/docs にアクセス
2. 各APIエンドポイントの詳細仕様を確認
3. "Try it out"ボタンでAPIを直接テスト
4. リクエスト/レスポンスの例を確認

### 5. データベース管理ツール（オプション）

Adminerを使用してデータベースを管理できます：

```bash
# Adminerを起動
docker-compose --profile admin up -d adminer

# Adminerにアクセス
# http://localhost:8080
# サーバー: db
# ユーザー名: todouser
# パスワード: todopass
# データベース: todoapp
```

## 📚 API仕様

### エンドポイント一覧

| メソッド | エンドポイント | 説明                 | リクエスト   | レスポンス       |
| -------- | -------------- | -------------------- | ------------ | ---------------- |
| GET      | `/health`      | ヘルスチェック       | -            | `200 OK`         |
| POST     | `/todos`       | ToDoアイテム作成     | `TodoCreate` | `201 Created`    |
| GET      | `/todos`       | 全ToDoアイテム取得   | -            | `200 OK`         |
| GET      | `/todos/{id}`  | 特定ToDoアイテム取得 | -            | `200 OK`         |
| PUT      | `/todos/{id}`  | ToDoアイテム更新     | `TodoUpdate` | `200 OK`         |
| DELETE   | `/todos/{id}`  | ToDoアイテム削除     | -            | `204 No Content` |

### データモデル

#### TodoCreate
```json
{
  "title": "string (必須, 最大200文字)",
  "description": "string (任意, 最大1000文字)",
  "completed": "boolean (デフォルト: false)"
}
```

#### TodoUpdate
```json
{
  "title": "string (任意, 最大200文字)",
  "description": "string (任意, 最大1000文字)",
  "completed": "boolean (任意)"
}
```

#### TodoResponse
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 使用例

#### ToDoアイテムの作成
```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "買い物リスト作成",
    "description": "週末の買い物リストを作成する",
    "completed": false
  }'
```

#### 全ToDoアイテムの取得
```bash
curl -X GET "http://localhost:8000/todos"
```

#### 特定ToDoアイテムの取得
```bash
curl -X GET "http://localhost:8000/todos/1"
```

#### ToDoアイテムの更新
```bash
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

#### ToDoアイテムの削除
```bash
curl -X DELETE "http://localhost:8000/todos/1"
```

## 🧪 テスト実行

### 全テストの実行

```bash
# Dockerコンテナ内でテストを実行
docker-compose exec app pytest

# カバレッジレポート付きでテストを実行
docker-compose exec app pytest --cov=app --cov-report=html

# 特定のテストマーカーのみ実行
docker-compose exec app pytest -m "unit"
docker-compose exec app pytest -m "integration"
```

### ローカル環境でのテスト実行

```bash
# 仮想環境の作成と有効化
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 依存関係のインストール
pip install -r requirements.txt

# テストの実行
pytest
```

### テストカバレッジの確認

テスト実行後、`htmlcov/index.html`でカバレッジレポートを確認できます。

## 🏗️ 開発ガイドライン

### プロジェクト構造

```
todo-api-backend/
├── app/                    # アプリケーションコード
│   ├── __init__.py
│   ├── main.py            # FastAPIアプリケーション
│   ├── config.py          # 設定管理
│   ├── database.py        # データベース接続
│   ├── exceptions.py      # カスタム例外
│   ├── models/            # SQLAlchemyモデル
│   ├── schemas/           # Pydanticスキーマ
│   ├── repositories/      # データアクセス層
│   ├── services/          # ビジネスロジック層
│   └── routers/           # APIルーター
├── tests/                 # テストコード
├── docs/                  # ドキュメント
│   └── sequence_diagrams/ # PlantUMLシーケンス図
├── config/                # 設定ファイル
├── data/                  # データベースボリューム
├── db/                    # データベース設定
├── logs/                  # ログファイル
├── docker-compose.yml     # Docker Compose設定
├── Dockerfile            # Dockerイメージ設定
├── requirements.txt      # Python依存関係
├── pytest.ini           # pytest設定
└── README.md            # このファイル
```

### アーキテクチャ

このプロジェクトはレイヤードアーキテクチャを採用しています：

1. **API層** (`routers/`): HTTPリクエスト/レスポンスの処理
2. **サービス層** (`services/`): ビジネスロジックの実装
3. **リポジトリ層** (`repositories/`): データアクセスの抽象化
4. **モデル層** (`models/`): データベーススキーマの定義

### コーディング規約

- **PEP 8**: Pythonコーディングスタイルガイドに準拠
- **型ヒント**: 全ての関数とメソッドに型ヒントを追加
- **ドキュメント**: 重要な関数にはdocstringを記述
- **テスト**: 新機能には対応するテストを作成

### 開発フロー

1. **機能開発**
   ```bash
   # 新しいブランチを作成
   git checkout -b feature/new-feature
   
   # 開発とテスト
   docker-compose up -d
   # 開発作業...
   docker-compose exec app pytest
   
   # コミットとプッシュ
   git add .
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```

2. **テスト駆動開発**
   - 新機能の実装前にテストを作成
   - テストが失敗することを確認
   - 機能を実装してテストを通す
   - リファクタリング

## 🔧 トラブルシューティング

### よくある問題

#### 1. Dockerコンテナが起動しない

```bash
# ログを確認
docker-compose logs

# コンテナを再構築
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 2. データベース接続エラー

```bash
# データベースコンテナの状態を確認
docker-compose ps

# データベースログを確認
docker-compose logs db

# データベースに直接接続してテスト
docker-compose exec db psql -U todouser -d todoapp
```

#### 3. ポート競合エラー

```bash
# 使用中のポートを確認
netstat -an | findstr :8000
netstat -an | findstr :5432

# docker-compose.ymlでポート番号を変更
```

#### 4. テストが失敗する

```bash
# テスト用データベースの状態を確認
docker-compose exec app pytest -v --tb=long

# 特定のテストのみ実行
docker-compose exec app pytest tests/test_specific.py -v
```

### ログの確認

```bash
# アプリケーションログ
docker-compose logs app

# データベースログ
docker-compose logs db

# 全サービスのログ
docker-compose logs
```

## 📊 パフォーマンス

### 推奨システム要件

- **RAM**: 最小 4GB、推奨 8GB以上
- **CPU**: 2コア以上
- **ディスク**: 10GB以上の空き容量

### パフォーマンス最適化

- データベース接続プールの設定
- 適切なインデックスの使用
- 非同期処理の活用
- レスポンス圧縮の有効化

## 🔒 セキュリティ

### 実装済みセキュリティ機能

- SQLインジェクション対策（SQLAlchemy ORM使用）
- 入力データバリデーション（Pydantic使用）
- 非rootユーザーでのコンテナ実行
- 環境変数による機密情報管理

### セキュリティベストプラクティス

- 定期的な依存関係の更新
- セキュリティスキャンの実行
- ログの適切な管理
- HTTPS通信の使用（本番環境）

## 📈 監視とログ

### ヘルスチェック

アプリケーションの状態は以下のエンドポイントで確認できます：

```bash
curl http://localhost:8000/health
```

レスポンス例：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "database": "connected",
  "version": "1.0.0"
}
```

### ログレベル

- **DEBUG**: 詳細なデバッグ情報
- **INFO**: 一般的な情報
- **WARNING**: 警告メッセージ
- **ERROR**: エラー情報

## 🚀 本番環境デプロイ

### 本番環境用設定

```bash
# 本番環境用のDocker Composeファイルを使用
docker-compose -f docker-compose.prod.yml up -d
```

### 環境変数の設定

本番環境では以下の環境変数を適切に設定してください：

- `DATABASE_URL`: 本番データベースのURL
- `DEBUG`: `false`に設定
- `LOG_LEVEL`: `INFO`または`WARNING`に設定
- `CORS_ORIGINS`: 許可するオリジンを制限

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は`LICENSE`ファイルを参照してください。

## 📞 サポート

問題や質問がある場合は、以下の方法でお問い合わせください：

- GitHub Issues: バグレポートや機能リクエスト
- GitHub Discussions: 一般的な質問や議論

## 🔗 関連リンク

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [pytest Documentation](https://docs.pytest.org/)

---

**開発チーム**: Todo API Backend Team  
**最終更新**: 2024年1月  
**バージョン**: 1.0.0