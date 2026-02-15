# Database Migrations

このディレクトリには、データベーススキーマの変更を管理するマイグレーションファイルが含まれています。

## マイグレーションファイルの命名規則

```
{version}_{description}.sql
```

- `version`: 3桁の連番（例: 001, 002, 003）
- `description`: マイグレーションの内容を表す英語の説明

## マイグレーションの実行方法

### 開発環境での実行

```bash
# PostgreSQLコンテナに接続
docker-compose exec postgres psql -U todouser -d todoapp

# マイグレーションファイルを実行
\i /docker-entrypoint-initdb.d/migrations/001_add_end_date_column.sql
```

### 本番環境での実行

```bash
# データベースに直接接続してマイグレーションを実行
psql -h <host> -U <username> -d <database> -f db/migrations/001_add_end_date_column.sql
```

## マイグレーション履歴

| Version | Description | Date | Status |
|---------|-------------|------|--------|
| 001 | Add end_date column to todos table | 2025-01-08 | ✅ Ready |

## 注意事項

- マイグレーションは本番環境で実行する前に、必ず開発環境でテストしてください
- 大量のデータがある場合は、マイグレーション実行時間を考慮してください
- バックアップを取ってからマイグレーションを実行することを強く推奨します