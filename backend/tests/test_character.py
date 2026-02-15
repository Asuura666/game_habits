"""Tests for character creation and management."""

import uuid
import pytest
from httpx import Client

# Test data
CHARACTER_DATA = {
    "name": "TestHero",
    "character_class": "warrior",
    "stats": {
        "strength": 15,
        "intelligence": 8,
        "agility": 10,
        "vitality": 14,
        "luck": 8
    }
}


class TestCharacterCreation:
    """Test character creation flow."""

    @pytest.fixture
    def auth_token(self, client: Client):
        """Get auth token for a new user."""
        unique_email = f"char_test_{uuid.uuid4().hex[:8]}@test.com"
        response = client.post("/api/auth/register", json={
            "email": unique_email,
            "username": f"CharTest{uuid.uuid4().hex[:4]}",
            "password": "TestPass123!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]

    def test_no_character_initially(self, client: Client, auth_token: str):
        """New users should not have a character."""
        response = client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
        assert "Character required" in response.json()["detail"]

    def test_create_character_success(self, client: Client, auth_token: str):
        """Should create a character successfully."""
        response = client.post(
            "/api/characters/",
            json=CHARACTER_DATA,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["name"] == CHARACTER_DATA["name"]
        assert data["character_class"] == CHARACTER_DATA["character_class"]
        assert data["level"] == 1

    def test_get_character_after_creation(self, client: Client, auth_token: str):
        """Should be able to get character after creation."""
        # Create character first
        client.post(
            "/api/characters/",
            json=CHARACTER_DATA,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get character
        response = client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == CHARACTER_DATA["name"]

    def test_cannot_create_second_character(self, client: Client, auth_token: str):
        """Users should not be able to create multiple characters."""
        # Create first character
        client.post(
            "/api/characters/",
            json=CHARACTER_DATA,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Try to create second character
        response = client.post(
            "/api/characters/",
            json={**CHARACTER_DATA, "name": "SecondHero"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should fail (either 400 or 409 depending on implementation)
        assert response.status_code in [400, 409]


class TestCharacterValidation:
    """Test character creation validation."""

    @pytest.fixture
    def auth_token(self, client: Client):
        """Get auth token for a new user."""
        unique_email = f"char_val_{uuid.uuid4().hex[:8]}@test.com"
        response = client.post("/api/auth/register", json={
            "email": unique_email,
            "username": f"ValTest{uuid.uuid4().hex[:4]}",
            "password": "TestPass123!"
        })
        return response.json()["access_token"]

    def test_name_too_short(self, client: Client, auth_token: str):
        """Character name must be at least 2 characters."""
        response = client.post(
            "/api/characters/",
            json={**CHARACTER_DATA, "name": "A"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422

    def test_name_too_long(self, client: Client, auth_token: str):
        """Character name must be at most 30 characters."""
        response = client.post(
            "/api/characters/",
            json={**CHARACTER_DATA, "name": "A" * 31},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422

    def test_invalid_class(self, client: Client, auth_token: str):
        """Character class must be valid."""
        response = client.post(
            "/api/characters/",
            json={**CHARACTER_DATA, "character_class": "invalid_class"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422

    def test_valid_classes(self, client: Client, auth_token: str):
        """All valid classes should be accepted."""
        valid_classes = ["warrior", "mage", "ranger", "paladin", "assassin"]
        
        for char_class in valid_classes:
            unique_email = f"class_{char_class}_{uuid.uuid4().hex[:4]}@test.com"
            
            # Register new user for each class test
            reg_response = client.post("/api/auth/register", json={
                "email": unique_email,
                "username": f"Class{char_class[:4]}{uuid.uuid4().hex[:2]}",
                "password": "TestPass123!"
            })
            token = reg_response.json()["access_token"]
            
            # Create character with this class
            response = client.post(
                "/api/characters/",
                json={**CHARACTER_DATA, "name": f"Hero_{char_class}", "character_class": char_class},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code in [200, 201], f"Failed for class: {char_class}"


class TestCharacterStats:
    """Test character stats and progression."""

    @pytest.fixture
    def character_with_token(self, client: Client):
        """Create a user with character and return token."""
        unique_email = f"stat_test_{uuid.uuid4().hex[:8]}@test.com"
        
        # Register
        reg_response = client.post("/api/auth/register", json={
            "email": unique_email,
            "username": f"StatTest{uuid.uuid4().hex[:4]}",
            "password": "TestPass123!"
        })
        token = reg_response.json()["access_token"]
        
        # Create character
        client.post(
            "/api/characters/",
            json=CHARACTER_DATA,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        return token

    def test_initial_level_is_1(self, client: Client, character_with_token: str):
        """New characters should start at level 1."""
        response = client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {character_with_token}"}
        )
        assert response.json()["level"] == 1

    def test_initial_xp_is_0(self, client: Client, character_with_token: str):
        """New characters should start with 0 XP."""
        response = client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {character_with_token}"}
        )
        data = response.json()
        assert data["current_xp"] == 0
        assert data["total_xp"] == 0

    def test_stats_match_creation(self, client: Client, character_with_token: str):
        """Character stats should match creation request."""
        response = client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {character_with_token}"}
        )
        stats = response.json()["stats"]
        assert stats["strength"] == CHARACTER_DATA["stats"]["strength"]
        assert stats["intelligence"] == CHARACTER_DATA["stats"]["intelligence"]
        assert stats["agility"] == CHARACTER_DATA["stats"]["agility"]
        assert stats["vitality"] == CHARACTER_DATA["stats"]["vitality"]
        assert stats["luck"] == CHARACTER_DATA["stats"]["luck"]

    def test_hp_is_full(self, client: Client, character_with_token: str):
        """New characters should have full HP."""
        response = client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {character_with_token}"}
        )
        data = response.json()
        assert data["hp"] == data["max_hp"]
