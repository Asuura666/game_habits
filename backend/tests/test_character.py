"""Tests for character creation and management."""

import pytest
from httpx import AsyncClient

# Test data
TEST_USER = {
    "email": "character_test@test.com",
    "username": "CharacterTester",
    "password": "TestPass123!"
}

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
    async def auth_token(self, client: AsyncClient):
        """Get auth token for a new user."""
        # Register a new user
        import uuid
        unique_email = f"char_test_{uuid.uuid4().hex[:8]}@test.com"
        response = await client.post("/api/auth/register", json={
            "email": unique_email,
            "username": f"CharTest{uuid.uuid4().hex[:4]}",
            "password": "TestPass123!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]

    async def test_no_character_initially(self, client: AsyncClient, auth_token: str):
        """New users should not have a character."""
        response = await client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
        assert "Character required" in response.json()["detail"]

    async def test_create_character_success(self, client: AsyncClient, auth_token: str):
        """Should create a character successfully."""
        response = await client.post(
            "/api/characters",
            json=CHARACTER_DATA,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == CHARACTER_DATA["name"]
        assert data["character_class"] == CHARACTER_DATA["character_class"]
        assert data["level"] == 1
        assert data["stats"]["strength"] == CHARACTER_DATA["stats"]["strength"]

    async def test_get_character_after_creation(self, client: AsyncClient, auth_token: str):
        """Should be able to get character after creation."""
        # Create character first
        await client.post(
            "/api/characters",
            json=CHARACTER_DATA,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get character
        response = await client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == CHARACTER_DATA["name"]

    async def test_cannot_create_second_character(self, client: AsyncClient, auth_token: str):
        """Users should not be able to create multiple characters."""
        # Create first character
        await client.post(
            "/api/characters",
            json=CHARACTER_DATA,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Try to create second character
        response = await client.post(
            "/api/characters",
            json={**CHARACTER_DATA, "name": "SecondHero"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should fail (either 400 or 409 depending on implementation)
        assert response.status_code in [400, 409]


class TestCharacterValidation:
    """Test character creation validation."""

    @pytest.fixture
    async def auth_token(self, client: AsyncClient):
        """Get auth token for a new user."""
        import uuid
        unique_email = f"char_val_{uuid.uuid4().hex[:8]}@test.com"
        response = await client.post("/api/auth/register", json={
            "email": unique_email,
            "username": f"ValTest{uuid.uuid4().hex[:4]}",
            "password": "TestPass123!"
        })
        return response.json()["access_token"]

    async def test_name_too_short(self, client: AsyncClient, auth_token: str):
        """Character name must be at least 2 characters."""
        response = await client.post(
            "/api/characters",
            json={**CHARACTER_DATA, "name": "A"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422

    async def test_name_too_long(self, client: AsyncClient, auth_token: str):
        """Character name must be at most 30 characters."""
        response = await client.post(
            "/api/characters",
            json={**CHARACTER_DATA, "name": "A" * 31},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422

    async def test_invalid_class(self, client: AsyncClient, auth_token: str):
        """Character class must be valid."""
        response = await client.post(
            "/api/characters",
            json={**CHARACTER_DATA, "character_class": "invalid_class"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422

    async def test_valid_classes(self, client: AsyncClient, auth_token: str):
        """All valid classes should be accepted."""
        valid_classes = ["warrior", "mage", "ranger", "paladin", "assassin"]
        
        for char_class in valid_classes:
            import uuid
            unique_email = f"class_{char_class}_{uuid.uuid4().hex[:4]}@test.com"
            
            # Register new user for each class test
            reg_response = await client.post("/api/auth/register", json={
                "email": unique_email,
                "username": f"Class{char_class[:4]}{uuid.uuid4().hex[:2]}",
                "password": "TestPass123!"
            })
            token = reg_response.json()["access_token"]
            
            # Create character with this class
            response = await client.post(
                "/api/characters",
                json={**CHARACTER_DATA, "name": f"Hero_{char_class}", "character_class": char_class},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200, f"Failed for class: {char_class}"


class TestCharacterStats:
    """Test character stats and progression."""

    @pytest.fixture
    async def character_with_token(self, client: AsyncClient):
        """Create a user with character and return token."""
        import uuid
        unique_email = f"stat_test_{uuid.uuid4().hex[:8]}@test.com"
        
        # Register
        reg_response = await client.post("/api/auth/register", json={
            "email": unique_email,
            "username": f"StatTest{uuid.uuid4().hex[:4]}",
            "password": "TestPass123!"
        })
        token = reg_response.json()["access_token"]
        
        # Create character
        await client.post(
            "/api/characters",
            json=CHARACTER_DATA,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        return token

    async def test_initial_level_is_1(self, client: AsyncClient, character_with_token: str):
        """New characters should start at level 1."""
        response = await client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {character_with_token}"}
        )
        assert response.json()["level"] == 1

    async def test_initial_xp_is_0(self, client: AsyncClient, character_with_token: str):
        """New characters should start with 0 XP."""
        response = await client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {character_with_token}"}
        )
        data = response.json()
        assert data["current_xp"] == 0
        assert data["total_xp"] == 0

    async def test_stats_match_creation(self, client: AsyncClient, character_with_token: str):
        """Character stats should match creation request."""
        response = await client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {character_with_token}"}
        )
        stats = response.json()["stats"]
        assert stats["strength"] == CHARACTER_DATA["stats"]["strength"]
        assert stats["intelligence"] == CHARACTER_DATA["stats"]["intelligence"]
        assert stats["agility"] == CHARACTER_DATA["stats"]["agility"]
        assert stats["vitality"] == CHARACTER_DATA["stats"]["vitality"]
        assert stats["luck"] == CHARACTER_DATA["stats"]["luck"]

    async def test_hp_is_full(self, client: AsyncClient, character_with_token: str):
        """New characters should have full HP."""
        response = await client.get(
            "/api/characters/me",
            headers={"Authorization": f"Bearer {character_with_token}"}
        )
        data = response.json()
        assert data["hp"] == data["max_hp"]
