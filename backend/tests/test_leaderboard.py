"""
Tests for Leaderboard endpoints.
"""

import pytest
from uuid import uuid4


class TestLeaderboardXP:
    """Tests for XP leaderboards."""
    
    def test_weekly_xp_leaderboard_empty(self, client, test_user):
        """Test weekly XP leaderboard with no friends."""
        response = client.get(
            "/api/leaderboard/xp/weekly",
            headers=test_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert data["leaderboard_type"] == "xp"
        assert data["time_range"] == "week"
        # User should still appear (friends include self)
        assert data["total_participants"] >= 1
    
    def test_monthly_xp_leaderboard_empty(self, client, test_user):
        """Test monthly XP leaderboard with no friends."""
        response = client.get(
            "/api/leaderboard/xp/monthly",
            headers=test_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["leaderboard_type"] == "xp"
        assert data["time_range"] == "month"
    
    def test_leaderboard_unauthorized(self, client):
        """Test leaderboard without auth."""
        response = client.get("/api/leaderboard/xp/weekly")
        assert response.status_code in [401, 403]


class TestLeaderboardStreak:
    """Tests for Streak leaderboard."""
    
    def test_streak_leaderboard(self, client, test_user):
        """Test streak leaderboard."""
        response = client.get(
            "/api/leaderboard/streak",
            headers=test_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["leaderboard_type"] == "streak"
        assert data["time_range"] == "all_time"
        # Current user should appear
        assert len(data["entries"]) >= 1
        # First entry should have user info
        if data["entries"]:
            entry = data["entries"][0]
            assert "username" in entry
            assert "rank" in entry
            assert "score" in entry


class TestLeaderboardCompletion:
    """Tests for Completion rate leaderboard."""
    
    def test_completion_leaderboard(self, client, test_user):
        """Test completion rate leaderboard."""
        response = client.get(
            "/api/leaderboard/completion",
            headers=test_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["leaderboard_type"] == "completion"
        assert data["time_range"] == "month"


class TestLeaderboardPvP:
    """Tests for PvP leaderboard."""
    
    def test_pvp_leaderboard(self, client, test_user):
        """Test PvP leaderboard."""
        response = client.get(
            "/api/leaderboard/pvp",
            headers=test_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["leaderboard_type"] == "pvp"
        assert data["time_range"] == "all_time"


class TestLeaderboardWithFriends:
    """Integration tests with actual friend data."""
    
    def test_leaderboard_shows_friends(self, client, test_user):
        """Test that leaderboard shows friends when they exist."""
        # Create a second user
        unique = uuid4().hex[:8]
        second_user_data = {
            "email": f"leader_{unique}@test.com",
            "username": f"Leader_{unique}",
            "password": "LeaderPass123!"
        }
        
        register_response = client.post("/api/auth/register", json=second_user_data)
        assert register_response.status_code in [200, 201]
        second_token = register_response.json()["access_token"]
        second_headers = {"Authorization": f"Bearer {second_token}"}
        
        # Become friends
        code_response = client.get("/api/friends/code", headers=second_headers)
        friend_code = code_response.json()["friend_code"]
        
        # Send and auto-accept (by sending back)
        client.post(f"/api/friends/code/{friend_code}", headers=test_user["headers"])
        
        pending = client.get("/api/friends/pending", headers=second_headers)
        if pending.json()["incoming_count"] > 0:
            friendship_id = pending.json()["incoming"][0]["id"]
            client.post(f"/api/friends/accept/{friendship_id}", headers=second_headers)
        
        # Now check leaderboard includes both
        response = client.get(
            "/api/leaderboard/streak",
            headers=test_user["headers"]
        )
        assert response.status_code == 200
        data = response.json()
        # Should have at least 2 participants (self + friend)
        assert data["total_participants"] >= 2
