"""
テスト環境設定

テスト実行時の環境設定と設定値を管理する。
"""
import os
from typing import Dict, Any


class TestConfig:
    """テスト環境設定クラス"""

    # データベース設定
    TEST_DATABASE_URL = "sqlite:///:memory:"
    TEST_DATABASE_ECHO = False

    # API設定
    TEST_API_HOST = "testserver"
    TEST_API_PORT = 8000
    TEST_API_BASE_URL = f"http://{TEST_API_HOST}:{TEST_API_PORT}"

    # ログ設定
    TEST_LOG_LEVEL = "INFO"
    TEST_LOG_FORMAT = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
    TEST_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # テスト実行設定
    TEST_TIMEOUT = 30  # 秒
    TEST_RETRY_COUNT = 3
    TEST_PARALLEL_WORKERS = 1

    # パフォーマンステスト設定
    PERFORMANCE_TEST_DATA_SIZE = 100
    PERFORMANCE_TEST_TIMEOUT = 60  # 秒

    # カバレッジ設定
    COVERAGE_MIN_PERCENTAGE = 80
    COVERAGE_EXCLUDE_PATTERNS = [
        "*/tests/*",
        "*/venv/*",
        "*/__pycache__/*",
        "*/migrations/*"
    ]

    @classmethod
    def get_test_database_url(cls) -> str:
        """
        テスト用データベースURLを取得する

        Returns:
            str: テスト用データベースURL
        """
        return os.getenv("TEST_DATABASE_URL", cls.TEST_DATABASE_URL)

    @classmethod
    def is_integration_test_enabled(cls) -> bool:
        """
        統合テストが有効かどうかを確認する

        Returns:
            bool: 統合テストが有効な場合True
        """
        return os.getenv("ENABLE_INTEGRATION_TESTS", "true").lower() == "true"

    @classmethod
    def is_performance_test_enabled(cls) -> bool:
        """
        パフォーマンステストが有効かどうかを確認する

        Returns:
            bool: パフォーマンステストが有効な場合True
        """
        return os.getenv("ENABLE_PERFORMANCE_TESTS", "false").lower() == "true"

    @classmethod
    def get_test_environment_variables(cls) -> Dict[str, str]:
        """
        テスト環境用の環境変数を取得する

        Returns:
            Dict[str, str]: 環境変数の辞書
        """
        return {
            "TESTING": "true",
            "DATABASE_URL": cls.get_test_database_url(),
            "LOG_LEVEL": cls.TEST_LOG_LEVEL,
            "DEBUG": "false",
            "CORS_ORIGINS": "*",
            "CORS_ALLOW_CREDENTIALS": "true",
            "CORS_ALLOW_METHODS": "*",
            "CORS_ALLOW_HEADERS": "*"
        }

    @classmethod
    def setup_test_environment(cls):
        """テスト環境をセットアップする"""
        env_vars = cls.get_test_environment_variables()
        for key, value in env_vars.items():
            os.environ[key] = value

    @classmethod
    def cleanup_test_environment(cls):
        """テスト環境をクリーンアップする"""
        test_env_vars = [
            "TESTING",
            "TEST_DATABASE_URL",
            "ENABLE_INTEGRATION_TESTS",
            "ENABLE_PERFORMANCE_TESTS"
        ]

        for var in test_env_vars:
            if var in os.environ:
                del os.environ[var]


class TestDataConfig:
    """テストデータ設定クラス"""

    # サンプルデータ
    SAMPLE_TODO_DATA = {
        "title": "サンプルタスク",
        "description": "これはサンプルのタスクです",
        "completed": False
    }

    SAMPLE_TODO_DATA_LIST = [
        {
            "title": "タスク1",
            "description": "最初のタスク",
            "completed": False
        },
        {
            "title": "タスク2",
            "description": "2番目のタスク",
            "completed": True
        },
        {
            "title": "タスク3",
            "description": "3番目のタスク",
            "completed": False
        }
    ]

    # バリデーションエラー用データ
    INVALID_TODO_DATA = {
        "empty_title": {
            "title": "",
            "description": "空のタイトル"
        },
        "title_too_long": {
            "title": "a" * 201,
            "description": "長すぎるタイトル"
        },
        "description_too_long": {
            "title": "正常なタイトル",
            "description": "a" * 1001
        },
        "missing_title": {
            "description": "タイトルが欠けている"
        }
    }

    # パフォーマンステスト用データ生成
    @classmethod
    def generate_performance_test_data(cls, count: int = 100) -> list:
        """
        パフォーマンステスト用データを生成する

        Args:
            count: 生成するデータの数

        Returns:
            list: パフォーマンステスト用データのリスト
        """
        return [
            {
                "title": f"パフォーマンステストタスク{i+1}",
                "description": f"これは{i+1}番目のパフォーマンステスト用タスクです",
                "completed": i % 3 == 0
            }
            for i in range(count)
        ]


class TestAssertionConfig:
    """テストアサーション設定クラス"""

    # レスポンス時間の閾値（ミリ秒）
    API_RESPONSE_TIME_THRESHOLD = 1000

    # データベースクエリ時間の閾値（ミリ秒）
    DB_QUERY_TIME_THRESHOLD = 500

    # メモリ使用量の閾値（MB）
    MEMORY_USAGE_THRESHOLD = 100

    @classmethod
    def assert_response_time(cls, response_time_ms: float):
        """
        レスポンス時間をアサートする

        Args:
            response_time_ms: レスポンス時間（ミリ秒）
        """
        assert response_time_ms <= cls.API_RESPONSE_TIME_THRESHOLD, \
            f"Response time {response_time_ms}ms exceeds threshold {cls.API_RESPONSE_TIME_THRESHOLD}ms"

    @classmethod
    def assert_query_time(cls, query_time_ms: float):
        """
        クエリ時間をアサートする

        Args:
            query_time_ms: クエリ時間（ミリ秒）
        """
        assert query_time_ms <= cls.DB_QUERY_TIME_THRESHOLD, \
            f"Query time {query_time_ms}ms exceeds threshold {cls.DB_QUERY_TIME_THRESHOLD}ms"

    @classmethod
    def assert_memory_usage(cls, memory_usage_mb: float):
        """
        メモリ使用量をアサートする

        Args:
            memory_usage_mb: メモリ使用量（MB）
        """
        assert memory_usage_mb <= cls.MEMORY_USAGE_THRESHOLD, \
            f"Memory usage {memory_usage_mb}MB exceeds threshold {cls.MEMORY_USAGE_THRESHOLD}MB"


# テスト設定の初期化
def initialize_test_config():
    """テスト設定を初期化する"""
    TestConfig.setup_test_environment()


def cleanup_test_config():
    """テスト設定をクリーンアップする"""
    TestConfig.cleanup_test_environment()


# テスト実行時の設定確認
def validate_test_environment():
    """
    テスト環境の設定を検証する

    Raises:
        RuntimeError: 設定に問題がある場合
    """
    required_env_vars = ["TESTING"]
    missing_vars = []

    for var in required_env_vars:
        if var not in os.environ:
            missing_vars.append(var)

    if missing_vars:
        raise RuntimeError(
            f"Missing required environment variables: {missing_vars}")

    # テスト環境であることを確認
    if os.getenv("TESTING") != "true":
        raise RuntimeError(
            "TESTING environment variable must be set to 'true'")


# テスト設定の表示
def print_test_config():
    """現在のテスト設定を表示する"""
    print("=== Test Configuration ===")
    print(f"Database URL: {TestConfig.get_test_database_url()}")
    print(f"Integration Tests: {TestConfig.is_integration_test_enabled()}")
    print(f"Performance Tests: {TestConfig.is_performance_test_enabled()}")
    print(f"Log Level: {TestConfig.TEST_LOG_LEVEL}")
    print(f"Test Timeout: {TestConfig.TEST_TIMEOUT}s")
    print("=" * 30)
