#!/bin/bash
set -e

# Docker起動時のエントリーポイントスクリプト
# Alembicマイグレーションの自動実行とアプリケーション起動を行う

echo "🚀 Todo API Backend starting..."

# 環境変数の確認
echo "📊 Environment: ${ENVIRONMENT:-development}"
echo "🗄️  Database URL: ${DATABASE_URL}"

# データベース接続の待機
echo "⏳ Waiting for database to be ready..."
python -c "
import time
import sys
import os
sys.path.append('/app')

from app.database import engine
from sqlalchemy import text

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('✅ Database connection successful')
        break
    except Exception as e:
        retry_count += 1
        print(f'⏳ Database not ready (attempt {retry_count}/{max_retries}): {e}')
        if retry_count >= max_retries:
            print('❌ Failed to connect to database after maximum retries')
            sys.exit(1)
        time.sleep(2)
"

# Alembicマイグレーションの実行
echo "🔄 Running database migrations..."
if [ "${SKIP_MIGRATIONS:-false}" = "true" ]; then
    echo "⚠️  Skipping migrations (SKIP_MIGRATIONS=true)"
else
    # 現在のマイグレーション状態を確認
    echo "📊 Current migration status:"
    alembic current || echo "No migrations applied yet"
    
    # マイグレーションを実行
    echo "⬆️  Applying migrations..."
    alembic upgrade head
    
    if [ $? -eq 0 ]; then
        echo "✅ Migrations completed successfully"
    else
        echo "❌ Migration failed"
        exit 1
    fi
fi

# 開発環境でのサンプルデータ作成
if [ "${ENVIRONMENT:-development}" = "development" ] && [ "${CREATE_SAMPLE_DATA:-false}" = "true" ]; then
    echo "📝 Creating sample data for development..."
    python scripts/init_db.py || echo "⚠️  Sample data creation failed or skipped"
fi

# アプリケーションの起動
echo "🎉 Starting application..."
exec "$@"