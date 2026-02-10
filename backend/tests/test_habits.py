"""Tests for habits endpoints."""
import httpx


class TestHabits:
    """Test habit CRUD operations."""

    def test_create_habit(self, client: httpx.Client, test_user):
        """Test creating a new habit."""
        response = client.post(
            "/api/habits/",
            json={
                "title": "Morning Exercise",
                "description": "30 minutes workout",
                "frequency": "daily",
            },
            headers=test_user["headers"],
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Morning Exercise"
        assert data["frequency"] == "daily"
        assert data["current_streak"] == 0

    def test_list_habits(self, client: httpx.Client, test_user):
        """Test listing user habits."""
        # Create a habit first
        client.post(
            "/api/habits/",
            json={"title": "List Test", "frequency": "daily"},
            headers=test_user["headers"],
        )
        
        response = client.get(
            "/api/habits/",
            headers=test_user["headers"],
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_update_habit(self, client: httpx.Client, test_user):
        """Test updating a habit."""
        # Create a habit
        create_response = client.post(
            "/api/habits/",
            json={"title": "Original", "frequency": "daily"},
            headers=test_user["headers"],
        )
        habit_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/habits/{habit_id}",
            json={"title": "Updated Title"},
            headers=test_user["headers"],
        )
        
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_delete_habit(self, client: httpx.Client, test_user):
        """Test deleting a habit."""
        create_response = client.post(
            "/api/habits/",
            json={"title": "To Delete", "frequency": "daily"},
            headers=test_user["headers"],
        )
        habit_id = create_response.json()["id"]
        
        response = client.delete(
            f"/api/habits/{habit_id}",
            headers=test_user["headers"],
        )
        
        assert response.status_code == 204
