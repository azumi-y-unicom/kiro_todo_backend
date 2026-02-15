#!/usr/bin/env python3
"""
データベースマイグレーション管理スクリプト

Alembicを使用してデータベースマイグレーションを実行する。
"""
import subprocess
import sys
import os
from pathlib import Path

# プロジェクトルートを取得
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)


def run_command(command: list[str]) -> int:
    """コマンドを実行し、結果を表示する"""
    print(f"実行中: {' '.join(command)}")
    result = subprocess.run(command, capture_output=False)
    return result.returncode


def migrate_up():
    """最新のマイグレーションまで適用する"""
    print("🔄 データベースマイグレーションを実行中...")
    return run_command(["alembic", "upgrade", "head"])


def migrate_down(revision: str = "-1"):
    """指定されたリビジョンまでダウングレードする"""
    print(f"⬇️  データベースを {revision} までダウングレード中...")
    return run_command(["alembic", "downgrade", revision])


def create_migration(message: str):
    """新しいマイグレーションを作成する"""
    print(f"📝 新しいマイグレーション '{message}' を作成中...")
    return run_command(["alembic", "revision", "--autogenerate", "-m", message])


def show_current():
    """現在のマイグレーション状態を表示する"""
    print("📊 現在のマイグレーション状態:")
    return run_command(["alembic", "current"])


def show_history():
    """マイグレーション履歴を表示する"""
    print("📜 マイグレーション履歴:")
    return run_command(["alembic", "history", "--verbose"])


def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python scripts/db_migrate.py up                    # 最新まで適用")
        print("  python scripts/db_migrate.py down [revision]       # ダウングレード")
        print("  python scripts/db_migrate.py create <message>      # 新規作成")
        print("  python scripts/db_migrate.py current               # 現在の状態")
        print("  python scripts/db_migrate.py history               # 履歴表示")
        sys.exit(1)

    command = sys.argv[1]
    
    if command == "up":
        exit_code = migrate_up()
    elif command == "down":
        revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
        exit_code = migrate_down(revision)
    elif command == "create":
        if len(sys.argv) < 3:
            print("エラー: マイグレーションメッセージが必要です")
            sys.exit(1)
        message = " ".join(sys.argv[2:])
        exit_code = create_migration(message)
    elif command == "current":
        exit_code = show_current()
    elif command == "history":
        exit_code = show_history()
    else:
        print(f"エラー: 不明なコマンド '{command}'")
        sys.exit(1)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()