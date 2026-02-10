"""Tests for completions endpoints."""
import httpx


class TestCompletions:
    """Test habit completion functionality."""

    def test_complete_habit(self, client: httpx.Client, test_user_with_character):
        """Test completing a habit earns rewards."""
        # Create a habit
        habit_response = client.post(
            "/api/habits/",
            json={"title": "Completion Test", "frequency": "daily"},
            headers=test_user_with_character["headers"],
        )
        habit_id = habit_response.json()["id"]
        
        # Get initial XP
        user_before = client.get(
            "/api/users/me",
            headers=test_user_with_character["headers"],
        ).json()
        
        # Complete the habit
        response = client.post(
            "/api/completions/",
            json={"habit_id": habit_id},
            headers=test_user_with_character["headers"],
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["xp_earned"] > 0
        assert data["coins_earned"] > 0
        
        # Verify XP increased
        user_after = client.get(
            "/api/users/me",
            headers=test_user_with_character["headers"],
        ).json()
        assert user_after["total_xp"] > user_before["total_xp"]

    def test_double_completion_fails(self, client: httpx.Client, test_user_with_character):
        """Test completing same habit twice in a day fails."""
        habit_response = client.post(
            "/api/habits/",
            json={"title": "Double Test", "frequency": "daily"},
            headers=test_user_with_character["headers"],
        )
        habit_id = habit_response.json()["id"]
        
        # First completion
        client.post(
            "/api/completions/",
            json={"habit_id": habit_id},
            headers=test_user_with_character["headers"],
        )
        
        # Second completion should fail
        response = client.post(
            "/api/completions/",
            json={"habit_id": habit_id},
            headers=test_user_with_character["headers"],
        )
        
        assert response.status_code == 400
