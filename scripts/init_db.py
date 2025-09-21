#!/usr/bin/env python3
"""
データベース初期化スクリプト

開発環境でのデータベース初期化とサンプルデータの投入を行う。
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.database import engine, Base, SessionLocal
from app.models.todo import Todo
from sqlalchemy.orm import Session


def create_tables():
    """データベーステーブルを作成する"""
    print("📊 データベーステーブルを作成中...")
    Base.metadata.create_all(bind=engine)
    print("✅ テーブル作成完了")


def create_sample_data():
    """サンプルデータを作成する"""
    print("📝 サンプルデータを作成中...")
    
    db: Session = SessionLocal()
    try:
        # 既存のデータをチェック
        existing_count = db.query(Todo).count()
        if existing_count > 0:
            print(f"⚠️  既に {existing_count} 件のデータが存在します。スキップします。")
            return
        
        # サンプルデータ
        sample_todos = [
            Todo(
                title="プロジェクトの企画書を作成",
                description="新しいWebアプリケーションの企画書を作成する。要件定義、技術選定、スケジュールを含める。",
                completed=False,
                end_date=datetime.now(timezone.utc) + timedelta(days=7)
            ),
            Todo(
                title="データベース設計",
                description="ユーザー管理とタスク管理のためのデータベーススキーマを設計する。",
                completed=True,
                end_date=datetime.now(timezone.utc) - timedelta(days=2)
            ),
            Todo(
                title="API仕様書の作成",
                description="RESTful APIの仕様書をOpenAPI形式で作成する。",
                completed=False,
                end_date=datetime.now(timezone.utc) + timedelta(days=3)
            ),
            Todo(
                title="フロントエンド開発環境構築",
                description="React + TypeScriptの開発環境をセットアップする。",
                completed=False
            ),
            Todo(
                title="ユニットテストの作成",
                description="APIエンドポイントのユニットテストを作成する。カバレッジ80%以上を目標とする。",
                completed=False,
                end_date=datetime.now(timezone.utc) + timedelta(days=10)
            ),
            Todo(
                title="コードレビューの実施",
                description="チームメンバーのコードレビューを実施し、品質向上を図る。",
                completed=True,
                end_date=datetime.now(timezone.utc) - timedelta(days=1)
            ),
            Todo(
                title="デプロイメント自動化",
                description="CI/CDパイプラインを構築し、自動デプロイメントを実現する。",
                completed=False,
                end_date=datetime.now(timezone.utc) + timedelta(days=14)
            ),
            Todo(
                title="パフォーマンステスト",
                description="アプリケーションの負荷テストを実施し、パフォーマンスを測定する。",
                completed=False,
                end_date=datetime.now(timezone.utc) + timedelta(days=21)
            )
        ]
        
        # データベースに追加
        for todo in sample_todos:
            db.add(todo)
        
        db.commit()
        print(f"✅ {len(sample_todos)} 件のサンプルデータを作成しました")
        
        # 作成されたデータの確認
        total_count = db.query(Todo).count()
        completed_count = db.query(Todo).filter(Todo.completed == True).count()
        pending_count = total_count - completed_count
        
        print(f"📊 データベース統計:")
        print(f"   - 総タスク数: {total_count}")
        print(f"   - 完了済み: {completed_count}")
        print(f"   - 未完了: {pending_count}")
        
    except Exception as e:
        print(f"❌ サンプルデータ作成中にエラーが発生しました: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """メイン関数"""
    print("🚀 データベース初期化を開始します...")
    
    try:
        # テーブル作成
        create_tables()
        
        # サンプルデータ作成
        create_sample_data()
        
        print("🎉 データベース初期化が完了しました！")
        
    except Exception as e:
        print(f"❌ 初期化中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()