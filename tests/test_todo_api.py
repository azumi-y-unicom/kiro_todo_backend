"""
ToDoアプリケーションAPI統合テスト

全APIエンドポイントの統合テストを実装する。
テストクライアントを使用したエンドツーエンドテストを提供する。
"""
import pytest
from fastapi.testclient import TestClient
import json

from app.main import app


class TestRootEndpoint:
    """ルートエンドポイントのテスト"""
    
    def test_root_endpoint(self, integration_test_client):
        """ルートエンドポイントの正常動作テスト"""
        response = integration_test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        assert data["message"] == "Welcome to Todo API Backend"


class TestHealthEndpoint:
    """ヘルスチェックエンドポイントのテスト"""
    
    def test_health_check_success(self, integration_test_client):
        """正常なヘルスチェックのテスト"""
        response = integration_test_client.get("/health/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "healthy"
        assert "message" in data


class TestTodoEndpoints:
    """ToDoエンドポイントの統合テスト"""
    
    def test_create_todo_success(self, integration_test_client):
        """ToDoアイテム作成の正常ケーステスト"""
        todo_data = {
            "title": "テストタスク",
            "description": "これはテスト用のタスクです",
            "completed": False
        }
        
        response = integration_test_client.post("/todos/", json=todo_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == todo_data["title"]
        assert data["description"] == todo_data["description"]
        assert data["completed"] == todo_data["completed"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_todo_minimal_data(self, integration_test_client):
        """最小限のデータでのToDoアイテム作成テスト"""
        todo_data = {
            "title": "最小限のタスク"
        }
        
        response = integration_test_client.post("/todos/", json=todo_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == todo_data["title"]
        assert data["description"] is None
        assert data["completed"] is False
    
    def test_create_todo_validation_error_empty_title(self, integration_test_client):
        """空のタイトルでのバリデーションエラーテスト"""
        todo_data = {
            "title": "",
            "description": "説明"
        }
        
        response = integration_test_client.post("/todos/", json=todo_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_create_todo_validation_error_title_too_long(self, integration_test_client):
        """長すぎるタイトルでのバリデーションエラーテスト"""
        todo_data = {
            "title": "a" * 201,  # 最大長を超える
            "description": "説明"
        }
        
        response = integration_test_client.post("/todos/", json=todo_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_create_todo_validation_error_description_too_long(self, integration_test_client):
        """長すぎる説明でのバリデーションエラーテスト"""
        todo_data = {
            "title": "タイトル",
            "description": "a" * 1001  # 最大長を超える
        }
        
        response = integration_test_client.post("/todos/", json=todo_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_get_todos_empty(self, integration_test_client):
        """空のToDoリスト取得テスト"""
        response = integration_test_client.get("/todos/")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_get_todos_with_data(self, integration_test_client):
        """データが存在する場合のToDoリスト取得テスト"""
        # テストデータを作成
        todos_data = [
            {"title": "タスク1", "description": "説明1", "completed": False},
            {"title": "タスク2", "description": "説明2", "completed": True},
            {"title": "タスク3", "description": "説明3", "completed": False}
        ]
        
        created_todos = []
        for todo_data in todos_data:
            response = integration_test_client.post("/todos/", json=todo_data)
            assert response.status_code == 201
            created_todos.append(response.json())
        
        # 全ToDoアイテムを取得
        response = integration_test_client.get("/todos/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # 作成日時の降順でソートされていることを確認
        for i in range(len(data) - 1):
            assert data[i]["created_at"] >= data[i + 1]["created_at"]
    
    def test_get_todos_with_pagination(self, integration_test_client):
        """ページネーション付きToDoリスト取得テスト"""
        # テストデータを作成
        for i in range(5):
            todo_data = {"title": f"タスク{i+1}", "completed": False}
            response = integration_test_client.post("/todos/", json=todo_data)
            assert response.status_code == 201
        
        # 最初のページを取得
        response = integration_test_client.get("/todos/?skip=0&limit=2")
        assert response.status_code == 200
        first_page = response.json()
        assert len(first_page) == 2
        
        # 2番目のページを取得
        response = integration_test_client.get("/todos/?skip=2&limit=2")
        assert response.status_code == 200
        second_page = response.json()
        assert len(second_page) == 2
        
        # 3番目のページを取得
        response = integration_test_client.get("/todos/?skip=4&limit=2")
        assert response.status_code == 200
        third_page = response.json()
        assert len(third_page) == 1
        
        # 重複がないことを確認
        all_ids = set()
        for page in [first_page, second_page, third_page]:
            for todo in page:
                assert todo["id"] not in all_ids
                all_ids.add(todo["id"])
    
    def test_get_todos_invalid_pagination_params(self, integration_test_client):
        """無効なページネーションパラメータのテスト"""
        # 負のskip
        response = integration_test_client.get("/todos/?skip=-1&limit=10")
        assert response.status_code == 422
        
        # 0のlimit
        response = integration_test_client.get("/todos/?skip=0&limit=0")
        assert response.status_code == 422
        
        # 大きすぎるlimit
        response = integration_test_client.get("/todos/?skip=0&limit=1001")
        assert response.status_code == 422
    
    def test_get_todo_by_id_success(self, integration_test_client):
        """特定ToDoアイテム取得の正常ケーステスト"""
        # テストデータを作成
        todo_data = {
            "title": "テストタスク",
            "description": "これはテスト用のタスクです",
            "completed": False
        }
        
        create_response = integration_test_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        
        # 作成したToDoアイテムを取得
        response = integration_test_client.get(f"/todos/{created_todo['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_todo["id"]
        assert data["title"] == todo_data["title"]
        assert data["description"] == todo_data["description"]
        assert data["completed"] == todo_data["completed"]
    
    def test_get_todo_by_id_not_found(self, integration_test_client):
        """存在しないToDoアイテム取得のテスト"""
        response = integration_test_client.get("/todos/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_todo_by_id_invalid_id(self, integration_test_client):
        """無効なIDでのToDoアイテム取得テスト"""
        response = integration_test_client.get("/todos/0")
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_update_todo_success(self, integration_test_client):
        """ToDoアイテム更新の正常ケーステスト"""
        # テストデータを作成
        todo_data = {
            "title": "元のタスク",
            "description": "元の説明",
            "completed": False
        }
        
        create_response = integration_test_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        
        # ToDoアイテムを更新
        update_data = {
            "title": "更新されたタスク",
            "description": "更新された説明",
            "completed": True
        }
        
        response = integration_test_client.put(f"/todos/{created_todo['id']}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_todo["id"]
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["completed"] == update_data["completed"]
        assert data["updated_at"] >= created_todo["updated_at"]
    
    def test_update_todo_partial(self, integration_test_client):
        """部分的なToDoアイテム更新テスト"""
        # テストデータを作成
        todo_data = {
            "title": "元のタスク",
            "description": "元の説明",
            "completed": False
        }
        
        create_response = integration_test_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        
        # 完了状態のみを更新
        update_data = {"completed": True}
        
        response = integration_test_client.put(f"/todos/{created_todo['id']}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_todo["id"]
        assert data["title"] == todo_data["title"]  # 変更されていない
        assert data["description"] == todo_data["description"]  # 変更されていない
        assert data["completed"] is True  # 変更されている
    
    def test_update_todo_not_found(self, integration_test_client):
        """存在しないToDoアイテム更新のテスト"""
        update_data = {
            "title": "存在しないタスク",
            "completed": True
        }
        
        response = integration_test_client.put("/todos/999", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_update_todo_validation_error(self, integration_test_client):
        """ToDoアイテム更新時のバリデーションエラーテスト"""
        # テストデータを作成
        todo_data = {"title": "テストタスク", "completed": False}
        
        create_response = integration_test_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        
        # 無効なデータで更新を試行
        update_data = {"title": ""}  # 空のタイトル
        
        response = integration_test_client.put(f"/todos/{created_todo['id']}", json=update_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_delete_todo_success(self, integration_test_client):
        """ToDoアイテム削除の正常ケーステスト"""
        # テストデータを作成
        todo_data = {
            "title": "削除予定のタスク",
            "description": "このタスクは削除されます",
            "completed": False
        }
        
        create_response = integration_test_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        
        # ToDoアイテムを削除
        response = integration_test_client.delete(f"/todos/{created_todo['id']}")
        
        assert response.status_code == 204
        assert response.content == b""
        
        # 削除されたことを確認
        get_response = integration_test_client.get(f"/todos/{created_todo['id']}")
        assert get_response.status_code == 404
    
    def test_delete_todo_not_found(self, integration_test_client):
        """存在しないToDoアイテム削除のテスト"""
        response = integration_test_client.delete("/todos/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_delete_todo_invalid_id(self, integration_test_client):
        """無効なIDでのToDoアイテム削除テスト"""
        response = integration_test_client.delete("/todos/0")
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestTodoEndpointsEndToEnd:
    """ToDoエンドポイントのエンドツーエンドテスト"""
    
    def test_complete_todo_workflow(self, integration_test_client):
        """完全なToDoワークフローのテスト"""
        # 1. ToDoアイテムを作成
        todo_data = {
            "title": "ワークフローテスト",
            "description": "完全なワークフローをテストする",
            "completed": False
        }
        
        create_response = integration_test_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        todo_id = created_todo["id"]
        
        # 2. 作成したToDoアイテムを取得
        get_response = integration_test_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200
        retrieved_todo = get_response.json()
        assert retrieved_todo["title"] == todo_data["title"]
        assert retrieved_todo["completed"] is False
        
        # 3. ToDoアイテムを完了状態に更新
        update_data = {"completed": True}
        update_response = integration_test_client.put(f"/todos/{todo_id}", json=update_data)
        assert update_response.status_code == 200
        updated_todo = update_response.json()
        assert updated_todo["completed"] is True
        
        # 4. 全ToDoリストで確認
        list_response = integration_test_client.get("/todos/")
        assert list_response.status_code == 200
        todos_list = list_response.json()
        assert len(todos_list) == 1
        assert todos_list[0]["id"] == todo_id
        assert todos_list[0]["completed"] is True
        
        # 5. ToDoアイテムを削除
        delete_response = integration_test_client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 204
        
        # 6. 削除されたことを確認
        final_list_response = integration_test_client.get("/todos/")
        assert final_list_response.status_code == 200
        final_todos_list = final_list_response.json()
        assert len(final_todos_list) == 0
    
    def test_multiple_todos_management(self, integration_test_client):
        """複数ToDoアイテムの管理テスト"""
        # 複数のToDoアイテムを作成
        todos_data = [
            {"title": "タスク1", "description": "最初のタスク", "completed": False},
            {"title": "タスク2", "description": "2番目のタスク", "completed": False},
            {"title": "タスク3", "description": "3番目のタスク", "completed": False}
        ]
        
        created_todos = []
        for todo_data in todos_data:
            response = integration_test_client.post("/todos/", json=todo_data)
            assert response.status_code == 201
            created_todos.append(response.json())
        
        # 全ToDoアイテムを取得して確認
        list_response = integration_test_client.get("/todos/")
        assert list_response.status_code == 200
        todos_list = list_response.json()
        assert len(todos_list) == 3
        
        # 2番目のToDoアイテムを完了状態に更新
        second_todo_id = created_todos[1]["id"]
        update_response = integration_test_client.put(
            f"/todos/{second_todo_id}", 
            json={"completed": True}
        )
        assert update_response.status_code == 200
        
        # 1番目のToDoアイテムを削除
        first_todo_id = created_todos[0]["id"]
        delete_response = integration_test_client.delete(f"/todos/{first_todo_id}")
        assert delete_response.status_code == 204
        
        # 最終状態を確認
        final_list_response = integration_test_client.get("/todos/")
        assert final_list_response.status_code == 200
        final_todos_list = final_list_response.json()
        assert len(final_todos_list) == 2
        
        # 残っているToDoアイテムの状態を確認
        remaining_ids = {todo["id"] for todo in final_todos_list}
        assert first_todo_id not in remaining_ids
        assert second_todo_id in remaining_ids
        assert created_todos[2]["id"] in remaining_ids
        
        # 完了状態の確認
        for todo in final_todos_list:
            if todo["id"] == second_todo_id:
                assert todo["completed"] is True
            else:
                assert todo["completed"] is False


class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def test_invalid_json_request(self, integration_test_client):
        """無効なJSONリクエストのテスト"""
        response = integration_test_client.post(
            "/todos/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, integration_test_client):
        """必須フィールドが欠けているリクエストのテスト"""
        response = integration_test_client.post("/todos/", json={})
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_invalid_content_type(self, integration_test_client):
        """無効なContent-Typeのテスト"""
        response = integration_test_client.post(
            "/todos/",
            content="title=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_method_not_allowed(self, integration_test_client):
        """許可されていないHTTPメソッドのテスト"""
        response = integration_test_client.patch("/todos/1")
        
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data


class TestResponseFormat:
    """レスポンス形式のテスト"""
    
    def test_todo_response_format(self, integration_test_client):
        """ToDoレスポンス形式の確認テスト"""
        todo_data = {
            "title": "フォーマットテスト",
            "description": "レスポンス形式をテストする",
            "completed": False
        }
        
        response = integration_test_client.post("/todos/", json=todo_data)
        assert response.status_code == 201
        
        data = response.json()
        
        # 必須フィールドの存在確認
        required_fields = ["id", "title", "description", "completed", "created_at", "updated_at"]
        for field in required_fields:
            assert field in data
        
        # データ型の確認
        assert isinstance(data["id"], int)
        assert isinstance(data["title"], str)
        assert isinstance(data["completed"], bool)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        
        # 値の確認
        assert data["title"] == todo_data["title"]
        assert data["description"] == todo_data["description"]
        assert data["completed"] == todo_data["completed"]
    
    def test_error_response_format(self, integration_test_client):
        """エラーレスポンス形式の確認テスト"""
        response = integration_test_client.get("/todos/999")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
    
    def test_validation_error_response_format(self, integration_test_client):
        """バリデーションエラーレスポンス形式の確認テスト"""
        response = integration_test_client.post("/todos/", json={"title": ""})
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data