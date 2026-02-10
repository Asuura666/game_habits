"""Tests for tasks endpoints."""
import httpx


class TestTasks:
    """Test task CRUD operations."""

    def test_create_task(self, client: httpx.Client, test_user):
        """Test creating a new task."""
        response = client.post(
            "/api/tasks/",
            json={
                "title": "Complete project",
                "description": "Finish the habit tracker",
                "priority": "high",
            },
            headers=test_user["headers"],
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Complete project"
        assert data["status"] == "pending"

    def test_list_tasks(self, client: httpx.Client, test_user):
        """Test listing tasks."""
        client.post(
            "/api/tasks/",
            json={"title": "List Test"},
            headers=test_user["headers"],
        )
        
        response = client.get(
            "/api/tasks/",
            headers=test_user["headers"],
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_complete_task(self, client: httpx.Client, test_user_with_character):
        """Test completing a task."""
        create_response = client.post(
            "/api/tasks/",
            json={"title": "To Complete"},
            headers=test_user_with_character["headers"],
        )
        task_id = create_response.json()["id"]
        
        response = client.post(
            f"/api/tasks/{task_id}/complete",
            headers=test_user_with_character["headers"],
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
