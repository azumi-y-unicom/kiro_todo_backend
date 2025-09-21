# Todo API Backend - Docker管理用Makefile

.PHONY: help build up down logs clean reset migration-create migration-up migration-down migration-status prod-up dev-up

# デフォルトターゲット
help:
	@echo "Todo API Backend - Docker管理コマンド"
	@echo ""
	@echo "開発環境:"
	@echo "  make dev-up          開発環境で起動（マイグレーション自動実行）"
	@echo "  make up              基本的な起動"
	@echo "  make down            停止"
	@echo "  make logs            ログ表示"
	@echo "  make logs-app        アプリケーションログのみ表示"
	@echo ""
	@echo "本番環境:"
	@echo "  make prod-up         本番環境で起動"
	@echo "  make prod-down       本番環境停止"
	@echo ""
	@echo "データベース管理:"
	@echo "  make migration-create MSG='message'  新しいマイグレーション作成"
	@echo "  make migration-up    マイグレーション適用"
	@echo "  make migration-down  マイグレーション1つ戻す"
	@echo "  make migration-status マイグレーション状態確認"
	@echo ""
	@echo "メンテナンス:"
	@echo "  make reset           完全リセット（データ削除）"
	@echo "  make clean           未使用リソース削除"
	@echo "  make build           イメージ再ビルド"

# 開発環境
dev-up:
	@echo "🚀 開発環境で起動中（マイグレーション自動実行）..."
	docker-compose up -d
	@echo "✅ 起動完了！"
	@echo "📊 API: http://localhost:8000"
	@echo "📚 Docs: http://localhost:8000/docs"
	@echo "🗄️  Adminer: http://localhost:8080"

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

# 本番環境
prod-up:
	@echo "🚀 本番環境で起動中..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✅ 本番環境起動完了！"

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# マイグレーション管理
migration-create:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ エラー: メッセージが必要です"; \
		echo "使用例: make migration-create MSG='Add new column'"; \
		exit 1; \
	fi
	@echo "📝 新しいマイグレーション '$(MSG)' を作成中..."
	docker-compose exec app alembic revision --autogenerate -m "$(MSG)"

migration-up:
	@echo "⬆️  マイグレーションを適用中..."
	docker-compose exec app alembic upgrade head

migration-down:
	@echo "⬇️  マイグレーションを1つ戻しています..."
	docker-compose exec app alembic downgrade -1

migration-status:
	@echo "📊 現在のマイグレーション状態:"
	docker-compose exec app alembic current
	@echo ""
	@echo "📜 マイグレーション履歴:"
	docker-compose exec app alembic history --verbose

# メンテナンス
reset:
	@echo "⚠️  データベースを完全リセットします..."
	@read -p "続行しますか？ (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v
	docker-compose up -d
	@echo "✅ リセット完了！"

clean:
	@echo "🧹 未使用リソースを削除中..."
	docker system prune -f
	docker volume prune -f

build:
	@echo "🔨 イメージを再ビルド中..."
	docker-compose build --no-cache

# ヘルスチェック
health:
	@echo "🏥 ヘルスチェック実行中..."
	@curl -f http://localhost:8000/health || echo "❌ ヘルスチェック失敗"

# 開発用ユーティリティ
shell:
	docker-compose exec app bash

db-shell:
	docker-compose exec db psql -U todouser -d todoapp

# テスト実行
test:
	docker-compose exec app python -m pytest

# 依存関係更新
update-deps:
	docker-compose exec app pip install -r requirements.txt --upgrade