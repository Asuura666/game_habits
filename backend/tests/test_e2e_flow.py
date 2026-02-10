"""End-to-end tests for the complete user flow."""

import pytest
from uuid import uuid4


class TestE2EUserFlow:
    """Test the complete user journey from registration to leveling up."""

    def test_complete_user_journey(self, client, unique_email, unique_username):
        """Test: Register → Create Character → Create Habit → Complete → Gain XP."""
        # Step 1: Register
        response = client.post("/api/auth/register", json={
            "email": unique_email,
            "username": unique_username,
            "password": "TestPass123!"
        })
        assert response.status_code in [200, 201]
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Create character (skip checking if no character - API might return 400)
        character_data = {
            "name": f"E2EHero{uuid4().hex[:4]}",
            "character_class": "warrior",
            "stats": {
                "strength": 15,
                "intelligence": 8,
                "agility": 10,
                "vitality": 14,
                "luck": 8
            }
        }
        response = client.post("/api/characters/", json=character_data, headers=headers)
        assert response.status_code == 201
        character = response.json()
        assert character["level"] == 1
        initial_xp = character["total_xp"]

        # Step 3: Create a habit
        habit_data = {
            "title": "E2E Test Habit",
            "description": "Testing the complete flow",
            "difficulty": "medium",
            "frequency": "daily",
            "positive": True
        }
        response = client.post("/api/habits/", json=habit_data, headers=headers)
        assert response.status_code == 201
        habit = response.json()
        habit_id = habit["id"]

        # Step 4: Complete the habit
        completion_data = {"habit_id": habit_id}
        response = client.post("/api/completions/", json=completion_data, headers=headers)
        assert response.status_code == 201
        completion = response.json()
        assert completion["xp_earned"] > 0

        # Step 5: Verify XP increased
        response = client.get("/api/characters/me", headers=headers)
        assert response.status_code == 200
        updated_character = response.json()
        assert updated_character["total_xp"] > initial_xp

        # Step 6: Check stats reflect the completion
        response = client.get("/api/stats/overview", headers=headers)
        assert response.status_code == 200

    def test_task_creation_and_list(self, client, unique_email, unique_username):
        """Test: Create Task → List Tasks."""
        # Register
        response = client.post("/api/auth/register", json={
            "email": unique_email,
            "username": unique_username,
            "password": "TestPass123!"
        })
        assert response.status_code in [200, 201]
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create character
        response = client.post("/api/characters/", json={
            "name": f"TaskHero{uuid4().hex[:4]}",
            "character_class": "mage",
            "stats": {"strength": 6, "intelligence": 18, "agility": 8, "vitality": 8, "luck": 10}
        }, headers=headers)
        assert response.status_code == 201

        # Create a task
        task_data = {
            "title": "E2E Test Task",
            "description": "Complete this for rewards",
            "difficulty": "hard",
            "priority": "high"
        }
        response = client.post("/api/tasks/", json=task_data, headers=headers)
        assert response.status_code == 201
        task = response.json()
        assert task["title"] == "E2E Test Task"

        # List tasks
        response = client.get("/api/tasks/", headers=headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1


class TestE2EAuthFlow:
    """Test authentication edge cases."""

    def test_register_and_get_me(self, client):
        """Test register and get current user."""
        unique_id = uuid4().hex[:8]
        credentials = {
            "email": f"auth_e2e_{unique_id}@test.com",
            "username": f"AuthE2E{unique_id}",
            "password": "SecurePass123!"
        }

        # Register
        response = client.post("/api/auth/register", json=credentials)
        assert response.status_code in [200, 201]
        register_token = response.json()["access_token"]

        # Verify token works
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {register_token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == credentials["email"]

    def test_duplicate_email_rejected(self, client):
        """Test that duplicate emails are rejected."""
        unique_id = uuid4().hex[:8]
        credentials = {
            "email": f"dupe_{unique_id}@test.com",
            "username": f"Dupe{unique_id}",
            "password": "TestPass123!"
        }

        # First registration should succeed
        response = client.post("/api/auth/register", json=credentials)
        assert response.status_code in [200, 201]

        # Second registration with same email should fail
        credentials["username"] = f"DupeOther{unique_id}"
        response = client.post("/api/auth/register", json=credentials)
        assert response.status_code == 400

    def test_invalid_token_rejected(self, client):
        """Test that invalid tokens are rejected."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401


class TestE2EHabitManagement:
    """Test habit CRUD operations end-to-end."""

    def test_habit_create_read_delete(self, test_user_with_character, client):
        """Test create, read, delete habit flow."""
        headers = test_user_with_character["headers"]

        # Create
        response = client.post("/api/habits/", json={
            "title": "CRUD Test Habit",
            "description": "Will be deleted",
            "difficulty": "easy",
            "frequency": "daily",
            "positive": True
        }, headers=headers)
        assert response.status_code == 201
        habit_id = response.json()["id"]

        # Read
        response = client.get(f"/api/habits/{habit_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["title"] == "CRUD Test Habit"

        # Delete
        response = client.delete(f"/api/habits/{habit_id}", headers=headers)
        assert response.status_code in [200, 204]

        # Verify deleted
        response = client.get(f"/api/habits/{habit_id}", headers=headers)
        assert response.status_code == 404

    def test_multiple_habits(self, test_user_with_character, client):
        """Test creating and listing multiple habits."""
        headers = test_user_with_character["headers"]

        # Create 3 habits
        habits_data = [
            {"title": "Morning Exercise", "difficulty": "medium", "frequency": "daily", "positive": True},
            {"title": "Read 30 min", "difficulty": "easy", "frequency": "daily", "positive": True},
            {"title": "No social media", "difficulty": "hard", "frequency": "daily", "positive": False},
        ]

        for habit in habits_data:
            response = client.post("/api/habits/", json=habit, headers=headers)
            assert response.status_code == 201

        # List all
        response = client.get("/api/habits/", headers=headers)
        assert response.status_code == 200
        habits = response.json()
        assert len(habits) >= 3


class TestE2ECharacterClasses:
    """Test all character classes work correctly."""

    @pytest.mark.parametrize("char_class", ["warrior", "mage", "ranger", "paladin", "assassin"])
    def test_all_classes_create_successfully(self, client, char_class):
        """Test that all character classes can be created."""
        unique_id = uuid4().hex[:8]
        
        # Register
        response = client.post("/api/auth/register", json={
            "email": f"class_{char_class}_{unique_id}@test.com",
            "username": f"Class{char_class[:3]}{unique_id}",
            "password": "TestPass123!"
        })
        assert response.status_code in [200, 201]
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create character with this class
        response = client.post("/api/characters/", json={
            "name": f"Hero{char_class[:3]}{unique_id}",
            "character_class": char_class,
            "stats": {"strength": 10, "intelligence": 10, "agility": 10, "vitality": 10, "luck": 10}
        }, headers=headers)
        
        assert response.status_code == 201
        assert response.json()["character_class"] == char_class


class TestE2EStatsAndProgress:
    """Test stats and progress tracking."""

    def test_stats_overview_structure(self, test_user_with_character, client):
        """Test that stats overview returns expected structure."""
        headers = test_user_with_character["headers"]

        response = client.get("/api/stats/overview", headers=headers)
        assert response.status_code == 200
        stats = response.json()
        
        # Check for expected fields
        assert "total_habits" in stats or "time_range" in stats
        assert "current_streak" in stats

    def test_character_xp_progression(self, test_user_with_character, client):
        """Test that XP increases with completions."""
        headers = test_user_with_character["headers"]

        # Get initial XP
        response = client.get("/api/characters/me", headers=headers)
        initial_xp = response.json()["total_xp"]

        # Create and complete multiple habits
        for i in range(3):
            response = client.post("/api/habits/", json={
                "title": f"XP Test Habit {i}",
                "difficulty": "easy",
                "frequency": "daily",
                "positive": True
            }, headers=headers)
            habit_id = response.json()["id"]
            client.post("/api/completions/", json={"habit_id": habit_id}, headers=headers)

        # Check XP increased
        response = client.get("/api/characters/me", headers=headers)
        final_xp = response.json()["total_xp"]
        assert final_xp > initial_xp


class TestE2ECompletionFlow:
    """Test completion and reward flow."""

    def test_habit_completion_gives_xp(self, test_user_with_character, client):
        """Test that completing a habit gives XP."""
        headers = test_user_with_character["headers"]

        # Create habit
        response = client.post("/api/habits/", json={
            "title": "XP Reward Test",
            "difficulty": "medium",
            "frequency": "daily",
            "positive": True
        }, headers=headers)
        habit_id = response.json()["id"]

        # Complete it
        response = client.post("/api/completions/", json={"habit_id": habit_id}, headers=headers)
        assert response.status_code == 201
        completion = response.json()
        assert completion["xp_earned"] > 0

    def test_double_completion_blocked(self, test_user_with_character, client):
        """Test that completing the same habit twice in one day is blocked."""
        headers = test_user_with_character["headers"]

        # Create habit
        response = client.post("/api/habits/", json={
            "title": "Double Complete Test",
            "difficulty": "easy",
            "frequency": "daily",
            "positive": True
        }, headers=headers)
        habit_id = response.json()["id"]

        # First completion
        response = client.post("/api/completions/", json={"habit_id": habit_id}, headers=headers)
        assert response.status_code == 201

        # Second completion should fail
        response = client.post("/api/completions/", json={"habit_id": habit_id}, headers=headers)
        assert response.status_code == 400
