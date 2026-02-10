"""Tests for character endpoints."""
import httpx


class TestCharacters:
    """Test character creation and management."""

    def test_create_character(self, client: httpx.Client, test_user):
        """Test creating a character."""
        response = client.post(
            "/api/characters/",
            json={
                "name": "TestWarrior",
                "character_class": "warrior",
                "stats": {
                    "strength": 7,
                    "intelligence": 3,
                    "agility": 5,
                    "vitality": 5,
                    "luck": 5,
                },
            },
            headers=test_user["headers"],
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "TestWarrior"
        assert data["character_class"] == "warrior"

    def test_get_my_character(self, client: httpx.Client, test_user_with_character):
        """Test getting own character."""
        response = client.get(
            "/api/characters/me",
            headers=test_user_with_character["headers"],
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "equipped" in data

    def test_duplicate_character_fails(self, client: httpx.Client, test_user_with_character):
        """Test creating second character fails."""
        response = client.post(
            "/api/characters/",
            json={"name": "Second", "character_class": "mage"},
            headers=test_user_with_character["headers"],
        )
        
        assert response.status_code == 400
